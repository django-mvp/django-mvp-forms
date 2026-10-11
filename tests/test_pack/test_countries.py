"""The markup the pack writes on a django-countries field, drawn as crispy-forms draws it."""

import copy

import pytest

from mvp_forms.choices import FormChoices, Modifiers
from tests.forms import (
    FLAG_LAYOUT_OF_THE_DEVELOPERS,
    CountriesForm,
    FlagLayoutForm,
    FlagPlacedForm,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
FIELDS = ["country", "countries", "flagged"]
SIZES = Modifiers.names("size", "select")
COLOURS = Modifiers.names("color", "select")
VARIANTS = Modifiers.names("variant", "select")
ROW = {"flex", "items-center", "gap-2"}
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


def flag_of(soup, name):
    return soup.find("img", id=f"flag_id_{name}")


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


@pytest.mark.parametrize("source", SOURCES)
class TestTheFlag:
    def test_the_select_and_its_flag_are_the_two_children_of_one_row(
        self, draw, source
    ):
        soup = draw(source, form=CountriesForm())

        row = soup.find(id="id_flagged").parent
        assert set(row["class"]) == ROW
        assert [child.name for child in row.find_all(recursive=False)] == [
            "select",
            "img",
        ]
        assert flag_of(soup, "flagged").parent is row

    def test_the_row_sits_inside_the_frame_after_the_label(self, draw, source):
        soup = draw(source, form=CountriesForm())

        frame = soup.find(id="div_id_flagged")
        row = soup.find(id="id_flagged").parent
        assert row.parent is frame
        assert row.find_previous_sibling("label")["for"] == "id_flagged"

    def test_a_field_in_error_keeps_its_row(self, draw, source):
        soup = draw(source, form=in_error())

        assert set(soup.find(id="id_flagged").parent["class"]) == ROW

    def test_a_field_with_no_flag_has_no_row(self, draw, source):
        soup = draw(source, form=CountriesForm())

        for name in ("country", "countries"):
            assert soup.find(id=f"id_{name}").parent["id"] == f"div_id_{name}"

    def test_a_layout_of_the_developers_is_drawn_as_written(self, draw, source):
        soup = draw(source, form=FlagLayoutForm())

        mine = soup.find(id="id_flagged").parent
        assert mine["class"] == ["mine"]
        assert mine.parent["id"] == "div_id_flagged"

    def test_a_second_draw_is_the_same_and_leaves_the_widget_alone(self, draw, source):
        form = stated(size="lg", color="primary", variant="ghost")
        widget = form.fields["flagged"].widget
        before = (widget.layout, copy.deepcopy(widget.attrs))

        first = draw(source, form=form)
        second = draw(source, form=form)

        assert str(first) == str(second)
        assert before == (widget.layout, widget.attrs)


class TestTheFlagInAFrameOfThePacks:
    @pytest.mark.parametrize("name", ["joined", "attached", "floating", "member"])
    def test_a_flag_widget_the_layout_decorates_is_given_no_row(self, draw, name):
        soup = draw("{% crispy form %}", form=FlagPlacedForm())

        assert not set(soup.find(id=f"id_{name}").parent["class"]) >= ROW
        assert flag_of(soup, name) is not None


class TestADeveloperLayout:
    def test_the_fixture_differs_from_django_countries_own(self):
        assert FlagLayoutForm().fields["flagged"].widget.layout == (
            FLAG_LAYOUT_OF_THE_DEVELOPERS
        )
        assert CountriesForm().fields["flagged"].widget.layout != (
            FLAG_LAYOUT_OF_THE_DEVELOPERS
        )
