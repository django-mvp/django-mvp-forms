"""A partial date field, drawn as the pack draws a text input and through each renderer."""

import json

import pytest

from mvp_forms.choices import FormChoices
from tests.forms import (
    PartialDateForm,
    PartialDateLineFormSet,
    PartialDateMaskForm,
    PartialDateMaskLineFormSet,
)

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.born|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]


class TestPartialDateField:
    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_daisyui_text_input(self, draw, source):
        soup = draw(source, form=PartialDateForm())

        drawn = soup.find(id="id_born")

        assert drawn.name == "input"
        assert drawn["type"] == "text"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_pack_gives_the_text_input_its_class(self, draw, source):
        soup = draw(source, form=PartialDateForm())

        assert "input" in soup.find(id="id_born")["class"]

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
        form = PartialDateForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_is_drawn_as_a_text_input(self, draw, source):
        soup = draw(source, form=PartialDateLineFormSet().empty_form)

        assert (
            soup.find("input", attrs={"name": "form-__prefix__-born"})["type"] == "text"
        )

    def test_the_form_names_no_script(self):
        assert "<script" not in str(PartialDateForm().media)


class TestPartialDateMaskInput:
    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_text_input_carrying_its_options(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        drawn = soup.find(id="id_born")

        assert drawn.name == "input"
        assert drawn["type"] == "text"
        assert json.loads(drawn["data-imask"]) == {
            "kind": "partial-date",
            "resolution": "day",
        }

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_attrs_and_the_numeric_keypad_are_drawn(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        drawn = soup.find(id="id_born")

        assert drawn["placeholder"] == "Born"
        assert drawn["inputmode"] == "numeric"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_pack_gives_the_text_input_its_class(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        assert "input" in soup.find(id="id_born")["class"]

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
        form = PartialDateMaskForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_carries_the_same_options(self, draw, source):
        formset = PartialDateMaskLineFormSet()

        row = draw(source, form=formset.forms[0])
        template = draw(source, form=formset.empty_form)

        assert (
            template.find("input", attrs={"data-imask": True})["data-imask"]
            == row.find("input", attrs={"data-imask": True})["data-imask"]
        )

    def test_the_forms_media_names_the_script(self):
        assert "mvp_forms/imask.js" in str(PartialDateMaskForm().media)
