"""Fixtures shared across the test suite."""

import copy
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from crispy_forms.templatetags import crispy_forms_filters, crispy_forms_tags
from crispy_forms.utils import default_field_template
from django.template import Context, Template
from django.test import override_settings
from django.urls import reverse


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


@pytest.fixture(scope="session")
def daisyui_classes():
    path = Path(__file__).parent / "data" / "daisyui-classes.txt"
    lines = path.read_text().splitlines()
    return {line for line in lines if line and not line.startswith("#")}


def clear_crispy_template_caches():
    crispy_forms_filters.uni_form_template.cache_clear()
    crispy_forms_filters.uni_formset_template.cache_clear()
    crispy_forms_tags.whole_uni_form_template.cache_clear()
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
