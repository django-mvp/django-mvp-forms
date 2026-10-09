"""A masked input, drawn as the pack draws a text input and through each renderer."""

import json

import pytest

from mvp_forms.choices import FormChoices
from tests.forms import MaskedForm, MaskedLineFormSet

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.phone|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]
PHONE = {"kind": "pattern", "mask": "+{49} 000 0000000"}


def options_of(soup, name):
    return json.loads(soup.find(id=f"id_{name}")["data-imask"])


def options_of_first(soup):
    return json.loads(soup.find("input", attrs={"data-imask": True})["data-imask"])


class TestMaskedInputs:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_options_are_drawn_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=MaskedForm())

        assert options_of(soup, "phone") == PHONE

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_each_field_carries_its_own_options(self, draw, source):
        soup = draw(source, form=MaskedForm())

        assert options_of(soup, "postcode") == {
            "kind": "pattern",
            "mask": "00000",
            "lazy": False,
            "placeholderChar": "#",
        }

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_is_drawn_as_a_daisyui_text_input(self, draw, source):
        soup = draw(source, form=MaskedForm())

        drawn = soup.find(id="id_phone")

        assert drawn.name == "input"
        assert drawn["type"] == "text"
        assert "input" in drawn["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "input-lg"),
            ("color", "primary", "input-primary"),
            ("variant", "ghost", "input-ghost"),
        ],
    )
    def test_it_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = MaskedForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_phone")["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_attrs_are_kept(self, draw, source):
        soup = draw(source, form=MaskedForm())

        assert soup.find(id="id_phone")["placeholder"] == "Phone"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_carries_the_same_options(self, draw, source):
        formset = MaskedLineFormSet()

        row = draw(source, form=formset.forms[0])
        template = draw(source, form=formset.empty_form)

        assert options_of_first(template) == options_of_first(row)
