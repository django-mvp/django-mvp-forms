"""A host project replaces one pack template and every other stays the pack's."""

import re

import pytest
from crispy_forms.templatetags import crispy_forms_filters, crispy_forms_tags
from crispy_forms.utils import default_field_template
from django.conf import settings
from django.template import Context, Template

from tests.conftest import FORM_RENDERER_THAT_READS_TEMPLATES, PACK_TEMPLATES
from tests.forms import LineFormSet, TextInputsForm
from tests.test_pack.test_independence import STATES

MARKER = "@@replaced@@"
TEMPLATE_PATHS = sorted(
    path.relative_to(PACK_TEMPLATES).as_posix()
    for path in PACK_TEMPLATES.rglob("*.html")
)
NEVER_DRAWN = {"daisyui/layout/tab-link.html"}
CRISPY_TEMPLATES_KEPT_IN_MEMORY = (
    default_field_template,
    crispy_forms_filters.uni_form_template,
    crispy_forms_filters.uni_formset_template,
    crispy_forms_tags.whole_uni_form_template,
    crispy_forms_tags.whole_uni_formset_template,
)
RANDOM_IDS = re.compile(r"(tabs|accordion)-[0-9a-f]+")
WHITESPACE = re.compile(r"\s+")


def draw_state(source, build):
    template = Template("{% load crispy_forms_tags %}" + source)
    html = template.render(Context({"csrf_token": "token", "form": build()}))
    return RANDOM_IDS.sub(r"\1-id", html)


def without_marker(html):
    # The form renderer strips what a widget template draws, so the whitespace
    # beside a marker at its start is not the pack's.
    return WHITESPACE.sub(" ", html.replace(MARKER, ""))


def draw_every_state():
    return [draw_state(*param.values[:2]) for param in STATES]


@pytest.fixture(scope="class")
def untouched():
    return [without_marker(html) for html in draw_every_state()]


class TestEveryTemplate:
    def test_the_package_has_templates_to_replace(self):
        assert TEMPLATE_PATHS

    @pytest.mark.parametrize("path", TEMPLATE_PATHS)
    def test_a_copy_with_a_marker_draws_what_the_pack_draws_plus_the_marker(
        self, replace, pack_source, untouched, path
    ):
        with replace({path: MARKER + pack_source(path)}):
            replaced = draw_every_state()

        assert [without_marker(html) for html in replaced] == untouched
        if path not in NEVER_DRAWN:
            assert any(MARKER in html for html in replaced)


class TestTheReplaceFixture:
    def test_leaving_the_block_restores_the_settings(self, replace):
        templates = settings.TEMPLATES[0]["DIRS"]
        renderer = settings.FORM_RENDERER
        apps = list(settings.INSTALLED_APPS)

        with replace({"daisyui/required_marker.html": MARKER}):
            assert len(settings.TEMPLATES[0]["DIRS"]) == len(templates) + 1
            assert settings.FORM_RENDERER == FORM_RENDERER_THAT_READS_TEMPLATES
            assert "django.forms" in settings.INSTALLED_APPS

        assert settings.TEMPLATES[0]["DIRS"] == templates
        assert renderer == settings.FORM_RENDERER
        assert apps == settings.INSTALLED_APPS

    def test_leaving_the_block_clears_the_five_templates_crispy_keeps(
        self, replace, draw, draw_layout
    ):
        with replace({"daisyui/whole_uni_formset.html": MARKER}):
            draw_layout("first")
            draw("{% crispy form %}", form=LineFormSet())
            draw("{{ form|crispy }}", form=LineFormSet())
            draw("{{ form|crispy }}", form=TextInputsForm())
            draw("{% crispy form %}", form=TextInputsForm())
            assert all(
                template.cache_info().currsize
                for template in CRISPY_TEMPLATES_KEPT_IN_MEMORY
            )

        assert not any(
            template.cache_info().currsize
            for template in CRISPY_TEMPLATES_KEPT_IN_MEMORY
        )

    def test_a_replacement_of_a_template_crispy_keeps_is_gone_afterwards(
        self, replace, draw
    ):
        with replace({"daisyui/whole_uni_formset.html": MARKER}):
            inside = draw("{% crispy form %}", form=LineFormSet())

        outside = draw("{% crispy form %}", form=LineFormSet())

        assert MARKER in inside.get_text()
        assert MARKER not in outside.get_text()
