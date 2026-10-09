"""The markup the pack writes on a django-tomselect select, drawn as crispy-forms draws it."""

import copy

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template import Context, Template
from django_tomselect.middleware import TomSelectMiddleware

from mvp_forms.choices import FormChoices, Modifiers
from tests.forms import TomSelectForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
FIELDS = ["group", "groups", "country", "countries"]
SIZES = Modifiers.names("size", "select")
COLOURS = Modifiers.names("color", "select")
VARIANTS = Modifiers.names("variant", "select")
STYLESHEET = "mvp_forms/tomselect.css"

pytestmark = pytest.mark.django_db


@pytest.fixture
def draw_with_request(rf, parse):
    # django-tomselect draws a model-backed widget in full only while its middleware
    # holds a request.
    def drawing(source, form):
        request = rf.get("/")
        request.user = AnonymousUser()
        template = Template("{% load crispy_forms_tags %}" + source)
        drawn = []

        def respond(request):
            drawn.append(
                template.render(Context({"csrf_token": "token", "form": form}))
            )
            return HttpResponse()

        TomSelectMiddleware(respond)(request)
        return parse(drawn[0])

    return drawing


def stated(**statement):
    form = TomSelectForm()
    form.helper.daisyui = FormChoices(**statement)
    return form


def in_error():
    form = TomSelectForm({})
    form.helper.daisyui = FormChoices(color="primary")
    return form


def classes(soup, name):
    return set(soup.find(id=f"id_{name}")["class"])


@pytest.mark.parametrize("source", SOURCES)
class TestTheSelect:
    def test_each_widget_is_drawn_as_a_select_with_the_packs_class(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, TomSelectForm())

        for name in FIELDS:
            assert soup.find(id=f"id_{name}").name == "select"
            assert {"select", "w-full"} <= classes(soup, name)

    @pytest.mark.parametrize("size", SIZES)
    def test_the_size_stated_for_the_form_is_written_on_each_select(
        self, draw_with_request, source, size
    ):
        soup = draw_with_request(source, stated(size=size))

        for name in FIELDS:
            assert f"select-{size}" in classes(soup, name)

    @pytest.mark.parametrize("colour", COLOURS)
    def test_the_colour_stated_for_the_form_is_written_on_each_select(
        self, draw_with_request, source, colour
    ):
        soup = draw_with_request(source, stated(color=colour))

        for name in FIELDS:
            assert f"select-{colour}" in classes(soup, name)

    @pytest.mark.parametrize("variant", VARIANTS)
    def test_the_variant_stated_for_the_form_is_written_on_each_select(
        self, draw_with_request, source, variant
    ):
        soup = draw_with_request(source, stated(variant=variant))

        for name in FIELDS:
            assert f"select-{variant}" in classes(soup, name)

    def test_a_field_in_error_is_drawn_in_error_with_no_colour(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, in_error())

        for name in FIELDS:
            assert "select-error" in classes(soup, name)
            assert "select-primary" not in classes(soup, name)

    def test_a_field_that_is_not_in_error_is_not_drawn_in_error(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, stated(color="primary"))

        for name in FIELDS:
            assert "select-error" not in classes(soup, name)

    def test_a_disabled_field_carries_the_disabled_attribute_and_no_other(
        self, draw_with_request, source
    ):
        form = TomSelectForm()
        form.fields["groups"].disabled = True
        form.fields["country"].disabled = True

        soup = draw_with_request(source, form)

        disabled = [
            name for name in FIELDS if soup.find(id=f"id_{name}").has_attr("disabled")
        ]
        assert disabled == ["groups", "country"]

    def test_each_label_is_tied_to_its_select(self, draw_with_request, source):
        soup = draw_with_request(source, TomSelectForm())

        for name in FIELDS:
            assert soup.find("label", attrs={"for": f"id_{name}"}) is not None

    def test_a_field_with_help_text_names_it_in_aria_describedby(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, TomSelectForm())

        for name in FIELDS:
            described = soup.find(id=f"id_{name}")["aria-describedby"].split()
            assert f"id_{name}_helptext" in described
            assert soup.find(id=f"id_{name}_helptext") is not None

    def test_a_field_in_error_names_its_errors_in_aria_describedby(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, in_error())

        for name in FIELDS:
            described = soup.find(id=f"id_{name}")["aria-describedby"].split()
            assert f"id_{name}_error" in described
            assert soup.find(id=f"id_{name}_error") is not None

    def test_a_second_draw_is_the_same_and_leaves_the_widgets_attrs_alone(
        self, draw_with_request, source
    ):
        form = stated(size="lg", color="primary", variant="ghost")
        before = {name: copy.deepcopy(form[name].field.widget.attrs) for name in FIELDS}

        first = draw_with_request(source, form)
        second = draw_with_request(source, form)

        assert str(first) == str(second)
        assert before == {name: form[name].field.widget.attrs for name in FIELDS}

    def test_the_stylesheet_is_not_named_in_what_is_drawn(
        self, draw_with_request, source
    ):
        soup = draw_with_request(source, in_error())

        assert STYLESHEET not in str(soup)


class TestTheRequest:
    @pytest.mark.parametrize("name", FIELDS)
    def test_each_select_is_drawn_whole_with_the_address_it_fetches_from(
        self, draw_with_request, name
    ):
        soup = draw_with_request("{{ form|crispy }}", TomSelectForm())

        assert soup.find(id=f"id_{name}").has_attr("data-autocomplete-url")
