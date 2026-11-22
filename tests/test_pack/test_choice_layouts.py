"""The scale and pill widgets drawn through Django's own renderer."""

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.http import QueryDict

from mvp_forms.widgets import (
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
