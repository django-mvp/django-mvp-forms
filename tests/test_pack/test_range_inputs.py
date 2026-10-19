"""A range of two inputs, drawn as one field in each of its three layouts."""

import pytest

from mvp_forms.choices import Choice, FormChoices
from tests.forms import RangeInputsForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
FRAMED = ["depth", "measured", "logged", "joined"]


def ends_of(soup, name):
    """Return the low and the high input of a range."""
    return soup.find(id=f"id_{name}_0"), soup.find(id=f"id_{name}_1")


class TestARange:
    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_one_fieldset_whose_legend_is_the_label(self, draw, source):
        soup = draw(source, form=RangeInputsForm())

        frame = soup.find(id="div_id_depth")

        assert frame.name == "fieldset"
        assert frame.find("legend").get_text(strip=True) == "Depth"

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", FRAMED)
    def test_each_end_sits_in_its_own_input_frame_showing_its_name(
        self, draw, source, name
    ):
        soup = draw(source, form=RangeInputsForm())

        low, high = ends_of(soup, name)

        assert low.find_parent("label") is not high.find_parent("label")
        for end in (low, high):
            frame = end.find_parent("label")
            assert "input" in frame["class"]
            assert "input" not in end.get_attribute_list("class")
            shown = frame.find("span", class_="label").get_text(strip=True)
            assert shown == end["aria-label"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_it_draws_the_values_it_holds_and_leaves_an_absent_end_empty(
        self, draw, source
    ):
        form = RangeInputsForm(initial={"depth": slice(100, None)})

        soup = draw(source, form=form)

        low, high = ends_of(soup, "depth")
        assert low["value"] == "100"
        assert not high.has_attr("value")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_joined_range_is_one_join_of_two_frames(self, draw, source):
        soup = draw(source, form=RangeInputsForm())

        low, high = ends_of(soup, "joined")
        join = low.find_parent(class_="join")

        assert join is high.find_parent(class_="join")
        assert "join-item" in low.find_parent("label")["class"]
        assert "join-item" in high.find_parent("label")["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["compact", "worded"])
    def test_a_compact_range_has_both_ends_in_one_frame(self, draw, source, name):
        soup = draw(source, form=RangeInputsForm())

        low, high = ends_of(soup, name)

        assert low.parent is high.parent
        assert "input" in low.parent["class"]
        assert "input" not in low.get_attribute_list("class")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "input-lg"),
            ("color", "primary", "input-primary"),
            ("variant", "ghost", "input-ghost"),
        ],
    )
    @pytest.mark.parametrize("name", ["depth", "joined", "compact"])
    def test_every_frame_takes_the_size_colour_and_variant_stated(
        self, draw, source, kind, value, added, name
    ):
        form = RangeInputsForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        for end in ends_of(soup, name):
            assert added in end.parent["class"]

    def test_a_field_s_own_colour_wins_over_the_form_s(self, draw):
        form = RangeInputsForm()
        form.helper.daisyui = FormChoices(
            color="primary", fields={"depth": Choice(color="accent")}
        )

        soup = draw("{% crispy form %}", form=form)

        for end in ends_of(soup, "depth"):
            assert "input-accent" in end.parent["class"]
            assert "input-primary" not in end.parent["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_range_in_error_marks_every_frame_and_both_ends(self, draw, source):
        soup = draw(source, form=RangeInputsForm({}))

        for end in ends_of(soup, "needed"):
            assert "input-error" in end.parent["class"]
            assert end["aria-invalid"] == "true"
        assert soup.find(id="div_id_needed").find(id="id_needed_error")


class TestARangeWithLabelsOff:
    @pytest.mark.parametrize("name", ["depth", "joined", "compact"])
    def test_the_label_is_shown_in_the_first_frame(self, draw, name):
        form = RangeInputsForm(show_labels=False)

        soup = draw("{% crispy form %}", form=form)

        low, _high = ends_of(soup, name)
        assert low.parent.find("span", class_="label").get_text(strip=True) == (
            form[name].label
        )

    @pytest.mark.parametrize("name", ["depth", "joined"])
    def test_the_second_frame_shows_no_name_and_each_end_its_placeholder(
        self, draw, name
    ):
        soup = draw("{% crispy form %}", form=RangeInputsForm(show_labels=False))

        low, high = ends_of(soup, name)

        assert high.parent.find("span", class_="label") is None
        assert low["placeholder"] == low["aria-label"]
        assert high["placeholder"] == high["aria-label"]

    def test_the_fieldset_is_named_by_the_label_in_place_of_a_legend(self, draw):
        soup = draw("{% crispy form %}", form=RangeInputsForm(show_labels=False))

        frame = soup.find(id="div_id_depth")

        assert frame.find("legend") is None
        assert frame["aria-label"] == "Depth"
