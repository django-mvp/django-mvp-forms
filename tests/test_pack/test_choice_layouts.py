"""The scale and pill widgets drawn through Django's own renderer."""

import pytest
from bs4 import BeautifulSoup
from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    InlineCheckboxes,
    InlineRadios,
    Modal,
    Tab,
    TabHolder,
)
from crispy_forms.layout import Column, Fieldset, Row
from django import forms
from django.contrib.auth.models import Group
from django.contrib.staticfiles import finders
from django.http import QueryDict
from django.utils.safestring import mark_safe

from mvp_forms.choices import Choice, FormChoices, InvalidChoice, Modifiers
from mvp_forms.widgets import (
    CardSelect,
    CardSelectMultiple,
    ChipSelect,
    ChipSelectMultiple,
    PillSelect,
    PillSelectMultiple,
    ScaleSelect,
)
from tests.forms import (
    ChoiceWidgetLineFormSet,
    ChoiceWidgetsForm,
    formset_helper,
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

    def test_the_end_words_are_drawn_when_given(self, drawn):
        soup = drawn(ScaleSelect(low="Never", high="Always"))

        assert len(soup.select("[aria-hidden]")) == 1

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
CHIPS = [ChipSelect, ChipSelectMultiple]
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

    @pytest.mark.parametrize("widget_class", CHIPS)
    def test_each_chip_is_named_by_its_label_alone(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=NUMBERS)

        assert [i["aria-label"] for i in soup.find_all("input")] == LABELS

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_each_card_is_named_by_the_label_that_holds_it(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=NUMBERS)

        inputs = soup.find_all("input")
        assert all(i.get("aria-label") is None for i in inputs)
        assert [i.find_parent("label").get_text().strip() for i in inputs] == LABELS

    @pytest.mark.parametrize("widget_class", CHIPS)
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

    @pytest.mark.parametrize("widget_class", CHIPS)
    def test_a_chips_label_is_escaped(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", "<b>R&D</b>")])

        assert soup.find("input")["aria-label"] == "<b>R&D</b>"
        assert soup.find("b") is None

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_cards_label_is_escaped(self, drawn, widget_class):
        soup = drawn(widget_class(), choices=[("a", "<b>R&D</b>")])

        assert "<b>R&D</b>" in soup.find("label").get_text()
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

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_extras_keyed_by_text_are_found_for_a_value_that_is_not_text(
        self, drawn, widget_class
    ):
        soup = drawn(
            widget_class(descriptions={"1": "One's note"}),
            choices=[(1, "One"), (2, "Two")],
        )

        assert "One's note" in self.label_of(soup, "1").get_text()
        assert "One's note" not in self.label_of(soup, "2").get_text()

    @staticmethod
    def order_in(label):
        """The kinds of children of a card label, in the order they are drawn."""
        kinds = []
        for child in label.find_all(["input", "div"], recursive=False):
            if child.name == "input":
                kinds.append("mark")
            elif child.find("svg"):
                kinds.append("icon")
            else:
                kinds.append("text")
        return kinds

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_the_mark_is_drawn_after_the_icon_and_the_text_by_default(
        self, drawn, widget_class
    ):
        widget = widget_class(icons={"a": mark_safe("<svg></svg>")})

        soup = drawn(widget, choices=self.CHOICES)

        assert self.order_in(self.label_of(soup, "a")) == ["icon", "text", "mark"]

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_a_mark_at_the_start_is_drawn_before_the_icon_and_the_text(
        self, drawn, widget_class
    ):
        widget = widget_class(mark="start", icons={"a": mark_safe("<svg></svg>")})

        soup = drawn(widget, choices=self.CHOICES)

        assert self.order_in(self.label_of(soup, "a")) == ["mark", "icon", "text"]
        assert self.order_in(self.label_of(soup, "b")) == ["mark", "text"]

    @pytest.mark.parametrize("columns", [1, 2, 3])
    @pytest.mark.parametrize("widget_class", CARDS)
    def test_the_columns_select_the_matching_wide_screen_grid(
        self, drawn, widget_class, columns
    ):
        soup = drawn(widget_class(columns=columns, show={"1"}), choices=NUMBERS)

        grids = [
            tag
            for tag in soup.find_all(["div"])
            if any(c.startswith("sm:grid-cols-") for c in tag.get("class", []))
        ]
        assert len(grids) == 1
        assert f"sm:grid-cols-{columns}" in grids[0]["class"]

    @pytest.mark.parametrize("widget_class", CARDS)
    def test_two_columns_are_drawn_when_none_is_given(self, drawn, widget_class):
        soup = drawn(widget_class())

        assert "sm:grid-cols-2" in soup.find(attrs={"data-choice-row": True})["class"]


class TestFold:
    LETTERS = [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]

    def row_of(self, soup):
        return soup.find(attrs={"data-choice-row": True})

    def folded_in(self, soup):
        """The values of the inputs marked as folded, in the order drawn."""
        return [
            i["value"]
            for i in soup.find_all("input")
            if i.has_attr("data-choice-folded")
            or i.find_parent("label", attrs={"data-choice-folded": True})
        ]

    def values_in(self, tag):
        return [i["value"] for i in tag.find_all("input")]

    def more_of(self, soup):
        return soup.find("button", attrs={"data-choice-more": True})

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_every_choice_is_in_one_row_in_the_fields_order_and_the_unnamed_are_marked(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a", "c"}), choices=self.LETTERS)

        assert self.values_in(self.row_of(soup)) == ["a", "b", "c", "d"]
        assert self.folded_in(soup) == ["b", "d"]
        assert soup.find("details") is None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_button_is_drawn_after_the_choices_in_the_row_and_is_hidden(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS)

        button = self.more_of(soup)

        assert button["type"] == "button"
        assert button.has_attr("hidden")
        assert button.parent is self.row_of(soup)
        assert button.find_previous("input")["value"] == "d"

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_button_is_the_only_button_of_the_field(self, drawn, widget_class):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS)

        assert len(soup.find_all("button")) == 1

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_nothing_is_marked_and_no_button_is_drawn_when_every_choice_is_on_show(
        self, drawn, widget_class
    ):
        everything = drawn(widget_class(), choices=self.LETTERS)
        all_named = drawn(widget_class(show=set("abcd")), choices=self.LETTERS)
        unknown_only = drawn(
            widget_class(show={"zzz"}), choices=[("a", "A")], data="field=a"
        )

        for soup in (everything, all_named, unknown_only):
            assert self.more_of(soup) is None
            assert self.folded_in(soup) == []

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_nothing_is_folded_when_no_choice_would_stay_on_show(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show=set()), choices=self.LETTERS)

        assert self.more_of(soup) is None
        assert self.folded_in(soup) == []

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_SINGLES)
    def test_a_chosen_choice_is_never_folded_whether_or_not_it_was_named(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS, data="field=c")

        assert self.folded_in(soup) == ["b", "d"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARD_MULTIPLES)
    def test_every_chosen_choice_of_a_multiple_widget_is_never_folded(
        self, drawn, widget_class
    ):
        soup = drawn(
            widget_class(show={"a"}), choices=self.LETTERS, data="field=b&field=d"
        )

        assert self.folded_in(soup) == ["c"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_no_button_is_drawn_when_every_folded_choice_is_chosen(
        self, drawn, widget_class
    ):
        soup = drawn(
            widget_class(show={"a"}),
            choices=[("a", "A"), ("b", "B")],
            data="field=b",
        )

        assert self.more_of(soup) is None

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_clearing_choice_is_never_folded_and_stays_outside_the_row(
        self, drawn, widget_class
    ):
        choices = [*self.LETTERS, ("", "None")]
        if widget_class in CHIP_AND_CARD_MULTIPLES:
            choices = self.LETTERS
        soup = drawn(widget_class(show={"a"}), choices=choices, initial="a")

        assert "" not in self.folded_in(soup)
        assert "" not in self.values_in(self.row_of(soup))

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_folded_choices_hold_checked_state_for_bound_values(
        self, drawn, widget_class
    ):
        soup = drawn(widget_class(show={"a"}), choices=self.LETTERS, data="field=b")

        checked = [i["value"] for i in soup.find_all("input", checked=True)]

        assert checked == ["b"]

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_developers_words_are_drawn_in_the_button(self, drawn, widget_class):
        soup = drawn(
            widget_class(show={"a"}, fold_label="Others"), choices=self.LETTERS
        )

        assert "Others" in self.more_of(soup).get_text()

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

        assert self.folded_in(narrowed) == ["b", "c", "d"]
        assert self.folded_in(plain) == []
        assert self.folded_in(again) == ["a", "d"]

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

        assert self.folded_in(soup) == [str(groups[0].pk), str(groups[2].pk)]


SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
TAG = "{% crispy form %}"
TABLE = "daisyui/table_inline_formset.html"
SIZES = ("xs", "sm", "md", "lg", "xl")
COLORS = (
    "neutral",
    "primary",
    "secondary",
    "accent",
    "info",
    "success",
    "warning",
    "error",
)
BUTTON_FIELDS = ["scale", "pill", "pills", "chip", "chips", "locked"]
CARD_MARKS = {"card": "radio", "cards": "checkbox"}
EVERY_FIELD = [*BUTTON_FIELDS, *CARD_MARKS]


def inputs_of(soup, name):
    return soup.find(id=f"id_{name}").find_all("input")


def classes_of(tag):
    return set(tag["class"])


def signature(tags):
    return [
        (
            tag["type"],
            tag["value"],
            tag.has_attr("checked"),
            tag.has_attr("disabled"),
            tag.get("aria-label"),
            tuple(tag["class"]),
        )
        for tag in tags
    ]


def refused(draw, source, form):
    with pytest.raises(InvalidChoice) as caught:
        draw(source, form=form)
    return caught.value


def label_of(tag):
    return tag.find_parent("label")


class TestPackSizeAndColour:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("size", SIZES)
    def test_every_size_reaches_every_input_of_every_widget(self, draw, source, size):
        soup = draw(source, form=ChoiceWidgetsForm(choices=FormChoices(size=size)))

        for name in BUTTON_FIELDS:
            assert all(f"btn-{size}" in classes_of(i) for i in inputs_of(soup, name))
        for name, mark in CARD_MARKS.items():
            assert all(f"{mark}-{size}" in classes_of(i) for i in inputs_of(soup, name))

    @pytest.mark.parametrize("color", COLORS)
    def test_every_colour_reaches_every_input_and_the_label_of_a_card(
        self, draw, color
    ):
        soup = draw(TAG, form=ChoiceWidgetsForm(choices=FormChoices(color=color)))

        chosen = set(Modifiers.colors["choice-button"][color].split())
        edge = set(Modifiers.colors["choice-card"][color].split())
        for name in BUTTON_FIELDS:
            assert all(chosen <= classes_of(i) for i in inputs_of(soup, name))
        for name, mark in CARD_MARKS.items():
            for tag in inputs_of(soup, name):
                assert f"{mark}-{color}" in classes_of(tag)
                assert edge <= classes_of(label_of(tag))

    def test_a_size_and_a_colour_stated_for_the_field_win_over_the_forms(self, draw):
        choices = FormChoices(
            size="xl",
            color="primary",
            fields={"scale": Choice(size="xs", color="error")},
        )

        soup = draw(TAG, form=ChoiceWidgetsForm(choices=choices))

        stated = set(Modifiers.colors["choice-button"]["error"].split())
        for tag in inputs_of(soup, "scale"):
            assert {"btn-xs"} | stated <= classes_of(tag)
            assert "btn-xl" not in classes_of(tag)
        assert all("btn-xl" in classes_of(i) for i in inputs_of(soup, "pill"))

    def test_a_card_takes_its_size_on_the_mark_only(self, draw):
        choices = FormChoices(fields={"card": Choice(size="lg")})

        soup = draw(TAG, form=ChoiceWidgetsForm(choices=choices))

        for tag in inputs_of(soup, "card"):
            assert "radio-lg" in classes_of(tag)
            assert not any(name.startswith("btn-") for name in classes_of(tag))

    def test_nothing_stated_writes_no_size_and_no_colour(self, draw):
        soup = draw(TAG, form=ChoiceWidgetsForm())

        for name in BUTTON_FIELDS:
            written = {n for i in inputs_of(soup, name) for n in classes_of(i)}
            assert not written & {f"btn-{size}" for size in SIZES}
            assert not any(n.startswith("checked:bg-") for n in written)
        for name, mark in CARD_MARKS.items():
            written = {n for i in inputs_of(soup, name) for n in classes_of(i)}
            assert not any(n.startswith(f"{mark}-") for n in written)

    def test_no_input_drawn_as_a_button_is_also_a_radio_or_a_checkbox(self, draw):
        soup = draw(TAG, form=ChoiceWidgetsForm(choices=FormChoices(size="sm")))

        for name in BUTTON_FIELDS:
            assert all(
                not {"radio", "checkbox"} & classes_of(i) for i in inputs_of(soup, name)
            )

    def test_the_clearing_choice_takes_the_size_and_the_colour(self, draw):
        soup = draw(
            TAG,
            form=ChoiceWidgetsForm(choices=FormChoices(size="sm", color="accent")),
        )

        clearing = [i for i in inputs_of(soup, "pill") if i["value"] == ""]

        assert len(clearing) == 1
        assert "btn-sm" in classes_of(clearing[0])

    def test_the_developers_own_class_stays_before_the_packs(self, draw):
        class OwnClassForm(ChoiceWidgetsForm):
            pill = forms.ChoiceField(
                choices=NUMBERS,
                widget=PillSelect(attrs={"class": "mine"}),
                required=False,
            )

        soup = draw(TAG, form=OwnClassForm(choices=FormChoices(size="sm")))

        for tag in inputs_of(soup, "pill"):
            assert {"mine", "btn-sm"} <= classes_of(tag)
            assert tag["class"].index("mine") < tag["class"].index("btn-sm")


class TestPackErrorState:
    BOUND = {"pill": "2"}

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_in_error_takes_the_error_colour_and_never_the_forms(
        self, draw, source
    ):
        choices = FormChoices(color="primary")

        soup = draw(source, form=ChoiceWidgetsForm(self.BOUND, choices=choices))

        error = set(Modifiers.colors["choice-button"]["error"].split())
        stated = set(Modifiers.colors["choice-button"]["primary"].split())
        for tag in inputs_of(soup, "scale"):
            assert error <= classes_of(tag)
            assert not stated & classes_of(tag)
        for tag in inputs_of(soup, "pill"):
            assert stated <= classes_of(tag)
            assert not error & classes_of(tag)

    def test_a_card_in_error_takes_the_error_colour_on_its_label_and_mark(self, draw):
        soup = draw(
            TAG,
            form=ChoiceWidgetsForm(self.BOUND, choices=FormChoices(color="primary")),
        )

        error = set(Modifiers.colors["choice-card"]["error"].split())
        stated = set(Modifiers.colors["choice-card"]["primary"].split())
        for name, mark in CARD_MARKS.items():
            for tag in inputs_of(soup, name):
                assert f"{mark}-error" in classes_of(tag)
                assert f"{mark}-primary" not in classes_of(tag)
                assert error <= classes_of(label_of(tag))
                assert not stated & classes_of(label_of(tag))

    def test_a_field_in_error_keeps_its_size(self, draw):
        soup = draw(
            TAG,
            form=ChoiceWidgetsForm(self.BOUND, choices=FormChoices(size="sm")),
        )

        assert all("btn-sm" in classes_of(i) for i in inputs_of(soup, "scale"))

    @pytest.mark.parametrize("source", SOURCES)
    def test_every_input_of_a_field_in_error_is_invalid_and_no_other_is(
        self, draw, source
    ):
        soup = draw(source, form=ChoiceWidgetsForm(self.BOUND))

        for name in ("scale", "card", "cards"):
            assert all(
                tag.get("aria-invalid") == "true" for tag in inputs_of(soup, name)
            )
        for name in ("pill", "pills", "chip", "chips"):
            assert not any(
                tag.has_attr("aria-invalid") for tag in inputs_of(soup, name)
            )


class TestPackFramesTheGroup:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", EVERY_FIELD)
    def test_the_choices_are_one_group_with_a_legend(self, draw, source, name):
        form = ChoiceWidgetsForm()

        soup = draw(source, form=form)

        group = soup.find("fieldset", id=f"div_id_{name}")
        assert form[name].label in group.find("legend").get_text()
        assert group.find(id=f"id_{name}") is not None

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["scale", "card"])
    def test_the_help_text_and_the_errors_describe_the_group(self, draw, source, name):
        soup = draw(source, form=ChoiceWidgetsForm({}))

        group = soup.find("fieldset", id=f"div_id_{name}")
        described = group["aria-describedby"].split()

        assert f"id_{name}_helptext" in described
        assert f"id_{name}_error" in described
        assert all(soup.find(id=ident) is not None for ident in described)

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_legend_of_a_required_field_holds_the_marker(self, draw, source):
        soup = draw(source, form=ChoiceWidgetsForm())

        required = soup.find("fieldset", id="div_id_scale").find("legend")
        optional = soup.find("fieldset", id="div_id_pill").find("legend")

        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_every_input_of_a_disabled_field_is_disabled(self, draw, source):
        soup = draw(source, form=ChoiceWidgetsForm())

        locked = inputs_of(soup, "locked")

        assert len(locked) == len(NUMBERS)
        assert all(tag.has_attr("disabled") for tag in locked)
        assert not any(tag.has_attr("disabled") for tag in inputs_of(soup, "pill"))

    def test_with_labels_off_the_group_is_named_by_an_aria_label(self, draw):
        form = ChoiceWidgetsForm(show_labels=False)

        soup = draw(TAG, form=form)

        group = soup.find("fieldset", id="div_id_scale")
        assert group["aria-label"] == form["scale"].label
        assert group.find("legend") is None


class TestPackDrawsTheWidgetAsItIs:
    @pytest.mark.parametrize("name", EVERY_FIELD)
    def test_the_widget_is_the_same_drawing_as_the_widget_alone(self, draw, name):
        form = ChoiceWidgetsForm()
        alone = BeautifulSoup(str(form[name]), "html.parser")

        soup = draw(TAG, form=form)

        assert str(soup.find(id=f"id_{name}")) == str(alone.find(id=f"id_{name}"))

    def test_the_fields_own_widget_is_not_changed_by_drawing(self, draw):
        form = ChoiceWidgetsForm(choices=FormChoices(size="sm", color="error"))
        before = str(BeautifulSoup(str(form["pill"]), "html.parser"))

        draw(TAG, form=form)

        assert str(BeautifulSoup(str(form["pill"]), "html.parser")) == before

    def test_a_form_using_none_of_the_widgets_draws_no_choice_classes(self, draw):
        class PlainForm(forms.Form):
            pick = forms.ChoiceField(choices=NUMBERS, widget=forms.RadioSelect)

        soup = draw(TAG, form=PlainForm())

        radios = soup.find_all("input", type="radio")
        assert radios
        assert all("radio" in classes_of(i) for i in radios)
        assert not soup.find_all(class_="join")

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_same_inputs_are_drawn_through_the_filter_and_the_tag(
        self, draw, source
    ):
        choices = FormChoices(size="sm", color="info")
        reference = draw(TAG, form=ChoiceWidgetsForm(choices=choices))

        soup = draw(source, form=ChoiceWidgetsForm(choices=choices))

        for name in EVERY_FIELD:
            assert signature(inputs_of(soup, name)) == signature(
                inputs_of(reference, name)
            )

    def test_one_field_through_as_crispy_field_is_the_same_drawing(self, draw):
        form = ChoiceWidgetsForm(choices=FormChoices(size="sm", color="info"))
        reference = draw(TAG, form=form)

        soup = draw("{{ form.pill|as_crispy_field }}", form=form)

        assert signature(soup.find_all("input")) == signature(
            inputs_of(reference, "pill")
        )

    @pytest.mark.parametrize("template", [None, TABLE], ids=["stacked", "table"])
    def test_every_form_of_a_formset_draws_the_widgets_with_the_size(
        self, draw, template
    ):
        settings = {} if template is None else {"template": template}
        helper = formset_helper(**settings)
        helper.daisyui = FormChoices(size="sm")

        soup = draw(
            "{% crispy formset helper %}",
            formset=ChoiceWidgetLineFormSet(),
            helper=helper,
        )

        names = []
        for row in range(2):
            pills = soup.find(id=f"id_form-{row}-pill").find_all("input")
            chips = soup.find(id=f"id_form-{row}-chips").find_all("input")
            assert len(pills) == len(chips) == len(NUMBERS)
            assert all("btn-sm" in classes_of(i) for i in [*pills, *chips])
            names.extend({tag["name"] for tag in [*pills, *chips]})
        assert len(names) == len(set(names)) == 4

    @pytest.mark.parametrize(
        "wrap",
        [
            lambda name: Row(Column(name)),
            lambda name: Fieldset("Pick", name),
            lambda name: TabHolder(Tab("Pick", name)),
            lambda name: Accordion(AccordionGroup("Pick", name)),
            lambda name: Modal(name, css_id="box", title="Pick"),
        ],
        ids=["row", "fieldset", "tab", "accordion group", "modal"],
    )
    @pytest.mark.parametrize("name", ["scale", "chips", "card"])
    def test_inside_another_layout_object_it_is_drawn_as_it_is_outside_one(
        self, draw, wrap, name
    ):
        choices = FormChoices(size="sm", color="info")
        alone = draw(TAG, form=ChoiceWidgetsForm(layout=[name], choices=choices))

        inside = draw(TAG, form=ChoiceWidgetsForm(layout=[wrap(name)], choices=choices))

        assert signature(inputs_of(inside, name)) == signature(inputs_of(alone, name))

    @pytest.mark.parametrize(
        ("wrap", "name"),
        [(InlineRadios, "pill"), (InlineCheckboxes, "pills")],
        ids=["radios", "checkboxes"],
    )
    def test_a_layout_object_that_draws_choices_along_a_line_draws_the_widget(
        self, draw, wrap, name
    ):
        choices = FormChoices(size="sm")
        alone = draw(TAG, form=ChoiceWidgetsForm(layout=[name], choices=choices))

        inline = draw(TAG, form=ChoiceWidgetsForm(layout=[wrap(name)], choices=choices))

        assert signature(inputs_of(inline, name)) == signature(inputs_of(alone, name))
        assert all("btn-sm" in classes_of(i) for i in inputs_of(inline, name))

    def test_a_host_projects_replacement_template_is_used(self, replace, draw):
        marker = '<i data-replaced="pills"></i>'

        with replace({"mvp_forms/widgets/pills.html": marker}):
            soup = draw(SOURCES[0], form=ChoiceWidgetsForm())

        assert len(soup.find_all(attrs={"data-replaced": "pills"})) == 3
        assert inputs_of(soup, "scale")


class TestPackMistakes:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("variant", ["ghost"])
    def test_a_variant_stated_for_the_form_is_passed_over(self, draw, source, variant):
        soup = draw(
            source, form=ChoiceWidgetsForm(choices=FormChoices(variant=variant))
        )

        for name in EVERY_FIELD:
            written = {n for i in inputs_of(soup, name) for n in classes_of(i)}
            assert not any(n.endswith(f"-{variant}") for n in written)

    @pytest.mark.parametrize("name", ["scale", "chips", "card", "cards"])
    def test_a_variant_stated_on_the_field_raises_naming_it(self, draw, name):
        form = ChoiceWidgetsForm(layout=[Choice(name, variant="ghost")])

        error = refused(draw, TAG, form)

        assert (error.kind, error.value, error.allowed) == ("variant", "ghost", ())
        assert error.target == name

    @pytest.mark.parametrize("name", ["scale", "pill", "pills", "chip", "card"])
    @pytest.mark.parametrize("drawing", ["rating", "toggle"])
    def test_a_drawing_stated_for_the_field_raises_naming_it(self, draw, name, drawing):
        form = ChoiceWidgetsForm(layout=[Choice(name, drawing=drawing)])

        error = refused(draw, TAG, form)

        assert (error.kind, error.value, error.allowed) == ("drawing", drawing, ())
        assert error.target == name


class TestScript:
    SCRIPT = "mvp_forms/choice-fold.js"

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_chip_and_card_widgets_name_the_script_and_no_other(self, widget_class):
        scripts = widget_class().media.render_js()

        assert len(scripts) == 1
        assert self.SCRIPT in scripts[0]

    @pytest.mark.parametrize(
        "widget_class", [ScaleSelect, PillSelect, PillSelectMultiple]
    )
    def test_the_scale_and_the_pills_name_no_script(self, widget_class):
        assert widget_class().media.render_js() == []

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_script_is_named_once_for_a_form_of_several_widgets(self, widget_class):
        class Both(forms.Form):
            one = forms.ChoiceField(choices=NUMBERS, widget=widget_class)
            two = forms.ChoiceField(choices=NUMBERS, widget=widget_class)

        assert len(Both().media.render_js()) == 1

    @pytest.mark.parametrize("widget_class", CHIP_AND_CARDS)
    def test_the_script_is_a_file_of_the_package(self, widget_class):
        assert finders.find(self.SCRIPT)
