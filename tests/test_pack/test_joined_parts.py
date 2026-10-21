"""The parts of a multi-widget on Django's own template, drawn as one daisyUI join."""

import pytest
from crispy_forms.layout import Field
from django import forms

from mvp_forms.choices import FormChoices
from tests.forms import AmountsForm, MultiWidgetsForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]


def classes_of(part):
    return part.get("class", [])


def parts_of(soup, name="amount"):
    return soup.find(attrs={"name": f"{name}_0"}), soup.find(
        attrs={"name": f"{name}_1"}
    )


@pytest.mark.parametrize("source", SOURCES)
class TestAnInputAndASelect:
    def test_the_parts_are_drawn_inside_one_join(self, draw, source):
        soup = draw(source, form=AmountsForm())

        joins = soup.select("div.join.w-full")

        assert len(joins) == 1
        assert all(part.find_parent("div", class_="join") for part in parts_of(soup))

    def test_the_input_fills_the_row_and_the_select_is_as_wide_as_its_options(
        self, draw, source
    ):
        soup = draw(source, form=AmountsForm())

        number, unit = parts_of(soup)

        assert {"join-item", "flex-1"} <= set(classes_of(number))
        assert {"join-item", "w-auto"} <= set(classes_of(unit))
        assert "w-full" not in classes_of(number)
        assert "w-full" not in classes_of(unit)

    def test_the_form_size_reaches_both_parts(self, draw, source):
        form = AmountsForm()
        form.helper.daisyui = FormChoices(size="lg")

        soup = draw(source, form=form)

        assert "input-lg" in classes_of(parts_of(soup)[0])
        assert "select-lg" in classes_of(parts_of(soup)[1])

    def test_the_error_modifier_reaches_both_parts(self, draw, source):
        soup = draw(source, form=AmountsForm({}))

        assert "input-error" in classes_of(parts_of(soup)[0])
        assert "select-error" in classes_of(parts_of(soup)[1])


class TestParts:
    def test_a_hidden_part_is_drawn_after_the_join_and_outside_it(self, draw):
        form = AmountsForm(parts=(forms.NumberInput, forms.HiddenInput))

        soup = draw("{% crispy form %}", form=form)

        number, hidden = parts_of(soup)
        join = soup.select_one("div.join")
        assert number.find_parent("div", class_="join") is join
        assert hidden.find_parent("div", class_="join") is None
        assert hidden["type"] == "hidden"
        assert join.find_next("input", attrs={"name": "amount_1"}) is hidden

    def test_a_widget_with_a_template_of_its_own_is_not_joined(self, draw):
        form = MultiWidgetsForm(None, layout=[Field("moment")])

        soup = draw("{% crispy form %}", form=form)

        assert soup.select("div.join") == []

    def test_a_part_that_is_neither_an_input_nor_a_select_leaves_the_widget_unjoined(
        self, draw
    ):
        soup = draw(
            "{% crispy form %}",
            form=AmountsForm(parts=(forms.NumberInput, forms.CheckboxInput)),
        )

        assert soup.select("div.join") == []
        assert "w-full" in classes_of(parts_of(soup)[0])
