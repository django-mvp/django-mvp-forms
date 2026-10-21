"""The markup the pack writes on a django-pint quantity field."""

import pytest
from quantityfield.units import ureg

from mvp_forms.choices import FormChoices
from tests.forms import QuantityForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
POSTED = {"weight_0": "2.5", "weight_1": "pound"}


def parts_of(soup):
    return soup.find(id="id_weight_0"), soup.find(id="id_weight_1")


@pytest.mark.parametrize("source", SOURCES)
class TestTheQuantityField:
    def test_the_number_and_the_unit_are_drawn_as_one_join(self, draw, source):
        soup = draw(source, form=QuantityForm())

        number, unit = parts_of(soup)
        join = soup.select_one("div.join.w-full")

        assert (number.name, number["type"]) == ("input", "number")
        assert unit.name == "select"
        assert number.find_parent("div", class_="join") is join
        assert unit.find_parent("div", class_="join") is join
        assert {"join-item", "flex-1"} <= set(number["class"])
        assert {"join-item", "w-auto"} <= set(unit["class"])

    def test_the_size_stated_for_the_form_reaches_both_parts(self, draw, source):
        form = QuantityForm()
        form.helper.daisyui = FormChoices(size="lg")

        soup = draw(source, form=form)

        number, unit = parts_of(soup)
        assert "input-lg" in number["class"]
        assert "select-lg" in unit["class"]

    def test_a_field_in_error_is_drawn_in_error_on_both_parts(self, draw, source):
        soup = draw(source, form=QuantityForm({}))

        number, unit = parts_of(soup)
        assert "input-error" in number["class"]
        assert "select-error" in unit["class"]

    def test_a_posted_form_keeps_its_values(self, draw, source):
        soup = draw(source, form=QuantityForm(POSTED))

        number, unit = parts_of(soup)
        assert number["value"] == "2.5"
        assert unit.find("option", selected=True)["value"] == "pound"


class TestTheCleanedQuantity:
    def test_the_form_cleans_to_the_same_quantity_as_it_does_with_no_pack(self, draw):
        plain = QuantityForm(POSTED)
        drawn = QuantityForm(POSTED)

        draw("{% crispy form %}", form=drawn)

        assert plain.is_valid()
        assert drawn.is_valid()
        assert drawn.cleaned_data == plain.cleaned_data
        assert drawn.cleaned_data["weight"] == ureg.Quantity(2.5, "pound")
