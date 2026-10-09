"""Fixtures shared across the test suite."""

import copy
import os
from contextlib import contextmanager
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from crispy_forms.templatetags import crispy_forms_filters, crispy_forms_tags
from crispy_forms.utils import default_field_template
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django.template import Context, Template
from django.test import override_settings
from django.urls import reverse

import mvp_forms
from support_window import ASKED, DECLARATION, Window, class_list, installed_versions
from tests.forms import (
    GroupFormSet,
    LineFormSet,
    NoLinesFormSet,
    PermissionFormSet,
    StructureForm,
)
from tests.template_surface import TemplateSurface


def pytest_report_header():
    """Name the Django and django-crispy-forms this run is on."""
    return [f"{name} {version}" for name, version in installed_versions().items()]


def pytest_sessionstart():
    """Stop a run that is on a version other than the one it was asked for."""
    asked = {name: os.environ[key] for name, key in ASKED.items() if key in os.environ}
    disagreements = Window.read(DECLARATION).installed_disagreements(
        installed_versions(), asked
    )
    unmet = [d for d in disagreements if d.package in asked]
    if unmet:
        found = ", ".join(f"{d.package} {d.version}" for d in unmet)
        raise pytest.UsageError(f"This run was asked for other versions: {found}")


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def open_page(client, db, parse):
    def open_url(name, data=None):
        url = reverse(name)
        response = client.get(url) if data is None else client.post(url, data)
        assert response.status_code == 200
        return parse(response.content.decode())

    return open_url


@pytest.fixture
def parse():
    def parse_fragment(html):
        return BeautifulSoup(html, "html.parser")

    return parse_fragment


@pytest.fixture
def draw(parse):
    def draw_template(source, **context):
        template = Template("{% load crispy_forms_tags %}" + source)
        return parse(template.render(Context({"csrf_token": "token", **context})))

    return draw_template


@pytest.fixture
def draw_layout(draw):
    def draw_layout_objects(*layout, bound=False, **context):
        form = StructureForm({} if bound else None, layout=layout)
        return draw("{% crispy form %}", form=form, **context)

    return draw_layout_objects


@pytest.fixture
def posted():
    def read_inputs(soup):
        data = QueryDict(mutable=True)
        for tag in soup.find_all(["input", "select", "textarea"]):
            name = tag.get("name")
            if not name or tag.has_attr("disabled"):
                continue
            if tag.name == "textarea":
                data.appendlist(name, tag.get_text())
            elif tag.name == "select":
                chosen = tag.find_all("option", selected=True) or tag("option")[:1]
                for option in chosen:
                    data.appendlist(name, option.get("value", option.get_text()))
            elif tag.get("type") in {"checkbox", "radio"}:
                if tag.has_attr("checked"):
                    data.appendlist(name, tag.get("value", "on"))
            elif tag.get("type") not in {"submit", "reset", "button", "image"}:
                data.appendlist(name, tag.get("value", ""))
        return data

    return read_inputs


@pytest.fixture
def plain_formset():
    return lambda data=None: LineFormSet(data)


@pytest.fixture
def no_forms_formset():
    return lambda data=None: NoLinesFormSet(data)


@pytest.fixture
def model_formset(db):
    Group.objects.create(name="Editors")
    Group.objects.create(name="Readers")
    return lambda data=None: GroupFormSet(data, queryset=Group.objects.order_by("pk"))


@pytest.fixture
def inline_formset(db):
    owner = ContentType.objects.get_for_model(Group)
    return lambda data=None: PermissionFormSet(data, instance=owner)


@pytest.fixture(scope="session", params=Window.read(DECLARATION).daisyui, ids=str)
def daisyui_classes(request):
    return class_list(request.param)


def clear_crispy_template_caches():
    crispy_forms_filters.uni_form_template.cache_clear()
    crispy_forms_filters.uni_formset_template.cache_clear()
    crispy_forms_tags.whole_uni_form_template.cache_clear()
    crispy_forms_tags.whole_uni_formset_template.cache_clear()
    default_field_template.cache_clear()


@pytest.fixture
def without_django_mvp(settings):
    templates = copy.deepcopy(settings.TEMPLATES)
    templates[0]["OPTIONS"]["context_processors"] = []
    with override_settings(
        INSTALLED_APPS=["crispy_forms", "mvp_forms"], TEMPLATES=templates
    ):
        clear_crispy_template_caches()
        yield
    clear_crispy_template_caches()


PACK_TEMPLATES = Path(mvp_forms.__file__).parent / "templates"
FORM_RENDERER_THAT_READS_TEMPLATES = "django.forms.renderers.TemplatesSetting"


@pytest.fixture
def pack_source():
    return lambda path: (PACK_TEMPLATES / path).read_text()


@pytest.fixture
def replace(tmp_path_factory, settings):
    @contextmanager
    def replacing(sources):
        root = tmp_path_factory.mktemp("replacements")
        for path, source in sources.items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(source)
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [root, *templates[0]["DIRS"]]
        try:
            with override_settings(
                TEMPLATES=templates,
                FORM_RENDERER=FORM_RENDERER_THAT_READS_TEMPLATES,
                INSTALLED_APPS=[*settings.INSTALLED_APPS, "django.forms"],
            ):
                clear_crispy_template_caches()
                yield
        finally:
            clear_crispy_template_caches()

    return replacing


@pytest.fixture
def names_read():
    return lambda source: TemplateSurface("", PACK_TEMPLATES).names_read(source)


@pytest.fixture
def template_surface(tmp_path):
    def surface_of(readme, templates):
        for path, source in templates.items():
            (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / path).write_text(source)
        return TemplateSurface(readme, tmp_path)

    return surface_of


def chrome_may_be_missing(environ):
    """Say whether a Chrome that cannot be launched skips the test and not fails it.

    Locally a missing Chrome is ordinary. In CI it is a failure, since the runner
    carries one and a skip would read as a pass.
    """
    return environ.get("CI", "").lower() not in {"1", "true"}


@pytest.fixture(scope="session")
def chrome(playwright):
    """The installed Chrome, which the browser tests launch by its channel."""
    try:
        browser = playwright.chromium.launch(channel="chrome")
    except Exception as error:
        message = f"Chrome cannot be launched: {error}"
        if chrome_may_be_missing(os.environ):
            pytest.skip(message)
        pytest.fail(message)
    yield browser
    browser.close()


@pytest.fixture
def page(chrome):
    context = chrome.new_context()
    yield context.new_page()
    context.close()
