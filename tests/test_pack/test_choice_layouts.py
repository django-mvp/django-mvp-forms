"""The scale and pill widgets drawn through Django's own renderer."""

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.contrib.auth.models import Group
from django.http import QueryDict
from django.utils.safestring import mark_safe

from mvp_forms.widgets import (
    CardSelect,
    CardSelectMultiple,
    ChipSelect,
    ChipSelectMultiple,
    PillSelect,
    PillSelectMultiple,
    ScaleSelect,
)

NUMBERS = [("1", "One"), ("2", "Two"), ("3", "Three"), ("4", "Four")]
VALUES = [choice[0] for choice in NUMBERS]
LABELS = [choice[1] for choice in NUMBERS]
WITH_CLEARING = [*NUMBERS, ("", "None")]
SINGLES = [ScaleSelect, PillSelect]
LAYOUTS = [ScaleSelect, PillSelect, PillSelectMultiple]


@pytest.fixture
def drawn():
    def draw_field(widget, *, choices=NUMBERS, data=None, initial=None, **kwargs):
        multiple = isinstance(widget, forms.CheckboxSelectMultiple)
        field_class = forms.MultipleChoiceField if multiple else forms.ChoiceField
        form_class = type(
            "ChoiceForm",
            (forms.Form,),
            {
                "field": field_class(
                    choices=choices, widget=widget, initial=initial, **kwargs
                )
            },
        )
        form = form_class(QueryDict(data) if data is not None else None)
        return BeautifulSoup(str(form["field"]), "html.parser")

    return draw_field


class TestScaleAndPillInputs:
    @pytest.mark.parametrize("widget_class", SINGLES)
    def test_every_choice_is_one_radio_input_in_the_fields_order(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class())

        inputs = soup.find_all("input")

        assert [(i["type"], i["name"], i["value"]) for i in inputs] == [
            ("radio", "field", value) for value in VALUES
        ]

    def test_every_choice_of_a_multiple_widget_is_one_checkbox_input(self, drawn):
        soup = drawn(PillSelectMultiple())

        inputs = soup.find_all("input")

        assert [(i["type"], i["name"], i["value"]) for i in inputs] == [
            ("checkbox", "field", value) for value in VALUES
        ]

    @pytest.mark.parametrize("widget_class", LAYOUTS)
    def test_each_input_is_named_by_its_label_alone(self, drawn, widget_class):
        soup = drawn(widget_class())

        inputs = soup.find_all("input")

        assert [i["aria-label"] for i in inputs] == LABELS

    @pytest.mark.parametrize("widget_class", SINGLES)
    def test_the_clearing_choice_follows_the_others(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("", "None"), *NUMBERS])

        values = [i["value"] for i in soup.find_all("input")]

        assert values == ["1", "2", "3", "4", ""]

    def test_a_multiple_widget_draws_the_empty_choice_in_its_place(self, drawn):
        soup = drawn(PillSelectMultiple(), choices=[("", "None"), *NUMBERS])

        values = [i["value"] for i in soup.find_all("input")]

        assert values == ["", "1", "2", "3", "4"]

    @pytest.mark.parametrize("widget_class", SINGLES)
    def test_the_bound_value_is_checked(self, drawn, widget_class):
        soup = drawn(widget_class(), data="field=3")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == ["3"]

    @pytest.mark.parametrize("widget_class", SINGLES)
    def test_the_initial_value_is_checked(self, drawn, widget_class):
        soup = drawn(widget_class(), initial="2")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == ["2"]

    def test_every_bound_value_of_a_multiple_widget_is_checked(self, drawn):
        soup = drawn(PillSelectMultiple(), data="field=1&field=4")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == ["1", "4"]

    def test_the_clearing_choice_is_checked_when_the_value_is_empty(self, drawn):
        soup = drawn(PillSelect(), choices=WITH_CLEARING, data="field=")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == [""]

    @pytest.mark.parametrize("widget_class", LAYOUTS)
    def test_a_disabled_field_disables_every_input(self, drawn, widget_class):
        soup = drawn(widget_class(), disabled=True)

        assert all(i.has_attr("disabled") for i in soup.find_all("input"))

    @pytest.mark.parametrize("widget_class", LAYOUTS)
    def test_a_developers_attribute_is_written_on_every_input(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(attrs={"data-probe": "yes"}))

        assert all(i["data-probe"] == "yes" for i in soup.find_all("input"))

    @pytest.mark.parametrize("widget_class", LAYOUTS)
    def test_a_label_is_escaped_in_the_name_of_its_input(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", '<b>"R&D"</b>')])

        assert soup.find("input")["aria-label"] == '<b>"R&D"</b>'
        assert soup.find("b") is None

    @pytest.mark.parametrize("widget_class", LAYOUTS)
    def test_the_widget_names_no_script(self, widget_class):
        assert not widget_class().media._js


class TestScaleEnds:
    def ends_of(self, soup):
        inputs = soup.find_all("input")
        first, last = inputs[0], inputs[-1]
        return (
            first.get("aria-labelledby", "").split(),
            last.get("aria-labelledby", "").split(),
        )

    def test_the_first_and_last_inputs_are_named_with_their_end_words(self, drawn):
        soup = drawn(ScaleSelect(low="Never", high="Always"))

        first, last = self.ends_of(soup)
        inputs = soup.find_all("input")

        assert first[0] == inputs[0]["id"]
        assert soup.find(id=first[1]).get_text(strip=True) == "Never"
        assert last[0] == inputs[-1]["id"]
        assert soup.find(id=last[1]).get_text(strip=True) == "Always"

    def test_the_inputs_between_are_named_by_their_label_alone(self, drawn):
        soup = drawn(ScaleSelect(low="Never", high="Always"))

        middle = soup.find_all("input")[1:-1]

        assert all(not i.has_attr("aria-labelledby") for i in middle)

    def test_the_end_words_are_drawn_only_when_given(self, drawn):
        soup = drawn(ScaleSelect())

        assert soup.select("[aria-hidden]") == []
        assert all(not i.has_attr("aria-labelledby") for i in soup.find_all("input"))

    def test_one_end_alone_is_drawn_alone(self, drawn):
        soup = drawn(ScaleSelect(high="Always"))

        first, last = self.ends_of(soup)

        assert first == []
        assert soup.find(id=last[1]).get_text(strip=True) == "Always"

    def test_the_clearing_choice_is_not_an_end_and_follows_the_others(self, drawn):
        soup = drawn(
            ScaleSelect(low="Never", high="Always"),
            choices=[("", "None"), *NUMBERS],
        )

        inputs = soup.find_all("input")

        assert [i["value"] for i in inputs] == ["1", "2", "3", "4", ""]
        assert not inputs[-1].has_attr("aria-labelledby")
        assert inputs[-2].has_attr("aria-labelledby")

    def test_the_words_are_escaped(self, drawn):
        soup = drawn(ScaleSelect(low="<b>Never</b>"))

        assert soup.find("b") is None


CHIP_AND_CARD_SINGLES = [ChipSelect, CardSelect]
CHIP_AND_CARD_MULTIPLES = [ChipSelectMultiple, CardSelectMultiple]
CHIP_AND_CARDS = [*CHIP_AND_CARD_SINGLES, *CHIP_AND_CARD_MULTIPLES]
CARDS = [CardSelect, CardSelectMultiple]
LONG_LABEL = "A choice whose label runs on, and on, and on, " * 4


class TestChipAndCardInputs:
    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_SINGLES)
    def test_every_choice_is_one_radio_input_in_the_fields_order(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class())

        inputs = soup.find_all("input")

        assert [(i["type"], i["name"], i["value"]) for i in inputs] == [
            ("radio", "field", value) for value in VALUES
        ]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_MULTIPLES)
    def test_every_choice_of_a_multiple_widget_is_one_checkbox_input(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class())

        inputs = soup.find_all("input")

        assert [(i["type"], i["name"], i["value"]) for i in inputs] == [
            ("checkbox", "field", value) for value in VALUES
        ]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_each_input_is_named_by_its_label_alone(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=NUMBERS)

        assert [i["aria-label"] for i in soup.find_all("input")] == LABELS

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_label_of_any_length_is_given_in_full(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", LONG_LABEL)])

        assert soup.find("input")["aria-label"] == LONG_LABEL

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_card_holds_its_label_in_full(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", LONG_LABEL)])

        assert LONG_LABEL in soup.find("label").get_text()

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_SINGLES)
    def test_the_clearing_choice_follows_the_others(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("", "None"), *NUMBERS])

        assert [i["value"] for i in soup.find_all("input")] == ["1", "2", "3", "4", ""]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_MULTIPLES)
    def test_a_multiple_widget_draws_the_empty_choice_in_its_place(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(), choices=[("", "None"), *NUMBERS])

        assert [i["value"] for i in soup.find_all("input")] == ["", "1", "2", "3", "4"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_SINGLES)
    def test_the_bound_and_initial_values_are_checked(self, drawn, widget_class):
        bound = drawn(widget_class(), data="field=3")
        initial = drawn(widget_class(), initial="2")

        assert [i["value"] for i in bound.find_all("input", checked=True)] == ["3"]
        assert [i["value"] for i in initial.find_all("input", checked=True)] == ["2"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_MULTIPLES)
    def test_every_bound_value_of_a_multiple_widget_is_checked(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(), data="field=1&field=4")

        assert [i["value"] for i in soup.find_all("input", checked=True)] == ["1", "4"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_disabled_field_disables_every_input(self, drawn, widget_class):
        soup = drawn(widget_class(), disabled=True)

        assert all(i.has_attr("disabled") for i in soup.find_all("input"))

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_label_is_escaped(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", "<b>R&D</b>")])

        assert soup.find("input")["aria-label"] == "<b>R&D</b>"
        assert soup.find("b") is None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_no_template_draws_a_script_or_a_handler(self, drawn, widget_class):
        soup = drawn(widget_class(show={"1"}))

        assert soup.find("script") is None
        assert not [
            name
            for tag in soup.find_all(True)
            for name in tag.attrs
            if name.startswith("on")
        ]


class TestCardExtras:
    CHOICES = [("a", "Alpha"), ("b", "Beta"), ("c", "Gamma")]

    def label_of(self, soup, value):
        return soup.find("input", value=value).find_parent("label")

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_extras_are_drawn_only_for_the_choices_given_them(
        self, drawn, widget_class
    ):
        widget = widget_class(
            descriptions={"a": "About alpha"},
            meta={"b": "Kind of beta"},
            icons={"c": mark_safe('<svg data-icon="gamma"></svg>')},
        )

        soup = drawn(widget, choices=self.CHOICES)

        first, second, third = (self.label_of(soup, v) for v in "abc")
        assert "About alpha" in first.get_text()
        assert "About alpha" not in second.get_text()
        assert "Kind of beta" in second.get_text()
        assert "Kind of beta" not in first.get_text()
        assert third.find("svg", attrs={"data-icon": "gamma"})
        assert first.find("svg") is None
        assert second.find("svg") is None

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_choice_given_no_extras_is_drawn_with_its_label_alone(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(), choices=self.CHOICES)

        label = self.label_of(soup, "a")

        assert label.get_text().split() == ["Alpha"]
        assert label.find("svg") is None

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_description_with_an_angle_bracket_is_escaped(self, drawn, widget_class):
        soup = drawn(
            widget_class(descriptions={"a": "<b>bold</b> & more"}),
            choices=self.CHOICES,
        )

        label = self.label_of(soup, "a")

        assert label.find("b") is None
        assert "<b>bold</b> & more" in label.get_text()

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_short_line_with_an_angle_bracket_is_escaped(self, drawn, widget_class):
        soup = drawn(widget_class(meta={"a": "<i>x</i>"}), choices=self.CHOICES)

        label = self.label_of(soup, "a")

        assert label.find("i") is None
        assert "<i>x</i>" in label.get_text()

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_an_icon_not_marked_safe_is_escaped(self, drawn, widget_class):
        soup = drawn(
            widget_class(icons={"a": '<svg data-icon="x"></svg>'}),
            choices=self.CHOICES,
        )

        assert soup.find("svg") is None

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_extras_are_found_by_the_value_read_as_text(self, drawn, widget_class):
        soup = drawn(
            widget_class(descriptions={1: "One's note"}),
            choices=[(1, "One"), (2, "Two")],
        )

        assert "One's note" in self.label_of(soup, "1").get_text()

    @pytest.mark.parametrize("columns", [1, 2, 3])
    @pytest.mark.parametrize("widget_class", CARDS)
    def test_the_columns_select_the_matching_wide_screen_grid(
        self, drawn, widget_class, columns
    ):
        soup = drawn(widget_class(columns=columns, show={"1"}), choices=NUMBERS)

        grids = [
            tag
            for tag in soup.find_all(["div"])
            if tag.has_attr("data-choice-shown") or tag.find_parent("details")
        ]
        for grid in grids:
            wide = {c for c in grid.get("class", []) if c.startswith("sm:grid-cols-")}
            assert wide <= {f"sm:grid-cols-{columns}"}
        assert any(f"sm:grid-cols-{columns}" in grid.get("class", []) for grid in grids)

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_two_columns_are_drawn_when_none_is_given(self, drawn, widget_class):
        soup = drawn(widget_class())

        assert "sm:grid-cols-2" in soup.find(attrs={"data-choice-shown": True})["class"]


class TestFold:
    LETTERS = [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]

    def fold_of(self, soup):
        return soup.find("details", attrs={"data-choice-fold": True})

    def values_in(self, tag):
        return [i["value"] for i in tag.find_all("input")]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_choices_not_named_are_in_a_fold_in_the_fields_order(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a", "c"}), choices=self.LETTERS)

        fold = self.fold_of(soup)
        shown = soup.find(attrs={"data-choice-shown": True})

        assert self.values_in(fold) == ["b", "d"]
        assert self.values_in(shown) == ["a", "c"]
        assert not fold.has_attr("open")

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_fold_is_a_disclosure_with_a_summary(self, drawn, widget_class):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS)

        fold = self.fold_of(soup)

        assert fold.find("summary") is not None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_every_choice_is_one_input_whether_shown_or_folded(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS)

        assert sorted(self.values_in(soup)) == ["a", "b", "c", "d"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_each_choice_carries_its_place_in_the_fields_order(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"b", "d"}), choices=self.LETTERS)

        places = {
            i["value"]: (i.find_parent(attrs={"data-choice-index": True}) or i)[
                "data-choice-index"
            ]
            for i in soup.find_all("input")
        }

        assert places == {"a": "0", "b": "1", "c": "2", "d": "3"}

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_no_fold_is_drawn_when_every_choice_is_on_show(self, drawn, widget_class):
        everything = drawn(widget_class(), choices=self.LETTERS)
        all_named = drawn(widget_class(show=set("abcd")), choices=self.LETTERS)
        unknown_only = drawn(
            widget_class(show={"zzz"}), choices=[("a", "A")], data="field=a"
        )

        assert self.fold_of(everything) is None
        assert self.fold_of(all_named) is None
        assert self.fold_of(unknown_only) is None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_fold_holding_every_choice_with_none_chosen_is_open(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show=set()), choices=self.LETTERS)

        fold = self.fold_of(soup)

        assert fold.has_attr("open")
        assert self.values_in(fold) == ["a", "b", "c", "d"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_SINGLES)
    def test_a_chosen_choice_is_on_show_whether_or_not_it_was_named(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS, data="field=c")

        assert self.values_in(self.fold_of(soup)) == ["b", "d"]
        assert "c" in self.values_in(soup.find(attrs={"data-choice-shown": True}))

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_MULTIPLES)
    def test_every_chosen_choice_of_a_multiple_widget_is_on_show(
        self, drawn, widget_class
    ):
        soup = drawn(
            widget_class(show={"a"}), choices=self.LETTERS, data="field=b&field=d"
        )

        assert self.values_in(self.fold_of(soup)) == ["c"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_fold_whose_choices_are_all_chosen_is_not_drawn(
        self, drawn, widget_class
    ):
        soup = drawn(
            widget_class(show={"a"}),
            choices=[("a", "A"), ("b", "B")],
            data="field=b",
        )

        assert self.fold_of(soup) is None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_clearing_choice_is_never_in_the_fold(self, drawn, widget_class):
        choices = [*self.LETTERS, ("", "None")]
        if widget_class in CHIP_AND_CARD_MULTIPLES:
            choices = self.LETTERS
        soup = drawn(widget_class(show={"a"}), choices=choices)

        assert "" not in self.values_in(self.fold_of(soup))

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_fold_holds_checked_state_for_bound_values(self, drawn, widget_class):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS, data="field=b")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == ["b"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_fold_holds_checked_state_for_initial_values(self, drawn, widget_class):
        initial = ["b"] if widget_class in CHIP_AND_CARD_MULTIPLES else "b"
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS, initial=initial)

        assert [i["value"] for i in soup.find_all("input", checked=True)] == ["b"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_package_words_carry_the_count_of_folded_choices(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS)

        assert "3" in self.fold_of(soup).find("summary").get_text()

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_developers_words_are_drawn_with_the_count(self, drawn, widget_class):
        soup = drawn(
            widget_class(show={"a"}, fold_label="Others"), choices=self.LETTERS
        )

        summary = self.fold_of(soup).find("summary")

        assert "Others" in summary.get_text()
        assert summary.find(attrs={"data-choice-count": True}).get_text() == "3"

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_show_set_on_a_form_instance_affects_that_form_alone(self, widget_class):
        class LetterForm(forms.Form):
            field = (
                forms.MultipleChoiceField
                if widget_class in CHIP_AND_CARD_MULTIPLES
                else forms.ChoiceField
            )(choices=TestFold.LETTERS, widget=widget_class())

            def __init__(self, *args, show=None, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["field"].widget.show = show

        narrowed = BeautifulSoup(str(LetterForm(show={"a"})["field"]), "html.parser")
        plain = BeautifulSoup(str(LetterForm()["field"]), "html.parser")
        again = BeautifulSoup(str(LetterForm(show={"b", "c"})["field"]), "html.parser")

        assert self.values_in(self.fold_of(narrowed)) == ["b", "c", "d"]
        assert self.fold_of(plain) is None
        assert self.values_in(self.fold_of(again)) == ["a", "d"]

    @pytest.mark.django_db
    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_a_model_choice_keyed_by_primary_key_folds_the_right_choices(
        self, widget_class
    ):
        groups = [Group.objects.create(name=name) for name in ("One", "Two", "Three")]
        multiple = widget_class in CHIP_AND_CARD_MULTIPLES
        field_class = (
            forms.ModelMultipleChoiceField if multiple else forms.ModelChoiceField
        )

        class GroupForm(forms.Form):
            field = field_class(
                queryset=Group.objects.order_by("pk"),
                widget=widget_class(show={groups[1].pk}),
            )

        soup = BeautifulSoup(str(GroupForm()["field"]), "html.parser")

        assert self.values_in(self.fold_of(soup)) == [
            str(groups[0].pk),
            str(groups[2].pk),
        ]
