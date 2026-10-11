"""The markup the pack writes on a django-countries field, drawn as crispy-forms draws it."""

import pytest

from mvp_forms.choices import FormChoices, Modifiers
from tests.forms import CountriesForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
FIELDS = ["country", "countries", "flagged"]
SIZES = Modifiers.names("size", "select")
COLOURS = Modifiers.names("color", "select")
VARIANTS = Modifiers.names("variant", "select")
POSTED = {"country": "DE", "countries": ["DE", "FR"], "flagged": "NZ"}


def stated(**statement):
    form = CountriesForm()
    form.helper.daisyui = FormChoices(**statement)
    return form


def in_error():
    form = CountriesForm({})
    form.helper.daisyui = FormChoices(color="primary")
    return form


def classes(soup, name):
    return set(soup.find(id=f"id_{name}")["class"])


@pytest.mark.parametrize("source", SOURCES)
class TestTheSelect:
    def test_each_field_is_drawn_as_a_select_with_the_packs_class(self, draw, source):
        soup = draw(source, form=CountriesForm())

        for name in FIELDS:
            assert soup.find(id=f"id_{name}").name == "select"
            assert {"select", "w-full"} <= classes(soup, name)

    @pytest.mark.parametrize("size", SIZES)
    def test_the_size_stated_for_the_form_is_written_on_each_select(
        self, draw, source, size
    ):
        soup = draw(source, form=stated(size=size))

        for name in FIELDS:
            assert f"select-{size}" in classes(soup, name)

    @pytest.mark.parametrize("colour", COLOURS)
    def test_the_colour_stated_for_the_form_is_written_on_each_select(
        self, draw, source, colour
    ):
        soup = draw(source, form=stated(color=colour))

        for name in FIELDS:
            assert f"select-{colour}" in classes(soup, name)

    @pytest.mark.parametrize("variant", VARIANTS)
    def test_the_variant_stated_for_the_form_is_written_on_each_select(
        self, draw, source, variant
    ):
        soup = draw(source, form=stated(variant=variant))

        for name in FIELDS:
            assert f"select-{variant}" in classes(soup, name)

    def test_a_field_in_error_is_drawn_in_error_with_no_colour(self, draw, source):
        soup = draw(source, form=in_error())

        for name in FIELDS:
            assert "select-error" in classes(soup, name)
            assert "select-primary" not in classes(soup, name)

    def test_a_field_that_is_not_in_error_is_not_drawn_in_error(self, draw, source):
        soup = draw(source, form=stated(color="primary"))

        for name in FIELDS:
            assert "select-error" not in classes(soup, name)

    def test_a_disabled_field_carries_the_disabled_attribute_and_no_other(
        self, draw, source
    ):
        form = CountriesForm()
        form.fields["countries"].disabled = True
        form.fields["flagged"].disabled = True

        soup = draw(source, form=form)

        disabled = [
            name for name in FIELDS if soup.find(id=f"id_{name}").has_attr("disabled")
        ]
        assert disabled == ["countries", "flagged"]

    def test_each_label_is_tied_to_its_select(self, draw, source):
        soup = draw(source, form=CountriesForm())

        for name in FIELDS:
            assert soup.find("label", attrs={"for": f"id_{name}"}) is not None

    def test_a_field_with_help_text_names_it_in_aria_describedby(self, draw, source):
        soup = draw(source, form=CountriesForm())

        for name in FIELDS:
            described = soup.find(id=f"id_{name}")["aria-describedby"].split()
            assert f"id_{name}_helptext" in described
            assert soup.find(id=f"id_{name}_helptext") is not None

    def test_a_field_in_error_names_its_errors_in_aria_describedby(self, draw, source):
        soup = draw(source, form=in_error())

        for name in FIELDS:
            described = soup.find(id=f"id_{name}")["aria-describedby"].split()
            assert f"id_{name}_error" in described
            assert soup.find(id=f"id_{name}_error") is not None

    def test_a_posted_form_is_drawn_with_its_values_and_cleans_to_them(
        self, draw, source
    ):
        form = CountriesForm(POSTED)

        soup = draw(source, form=form)

        chosen = {
            name: {
                option["value"]
                for option in soup.find(id=f"id_{name}").find_all(
                    "option", selected=True
                )
            }
            for name in FIELDS
        }
        assert chosen == {
            "country": {"DE"},
            "countries": {"DE", "FR"},
            "flagged": {"NZ"},
        }
        assert form.is_valid()
        assert form.cleaned_data == POSTED
