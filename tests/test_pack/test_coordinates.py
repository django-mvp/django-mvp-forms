"""Latitude and longitude fields, drawn as the pack draws a masked text input."""

import json

import pytest
from crispy_forms.helper import FormHelper
from django import forms

from mvp_forms.choices import FormChoices
from mvp_forms.fields import LatitudeField, LongitudeField

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.latitude|as_crispy_field }}{{ form.longitude|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]


class CoordinateForm(forms.Form):
    latitude = LatitudeField(required=False)
    longitude = LongitudeField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class TestCoordinateFields:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["latitude", "longitude"])
    def test_each_is_drawn_as_a_text_input_with_no_step_min_or_max(
        self, draw, source, name
    ):
        soup = draw(source, form=CoordinateForm())

        drawn = soup.find(id=f"id_{name}")

        assert drawn.name == "input"
        assert drawn["type"] == "text"
        for attribute in ("step", "min", "max"):
            assert not drawn.has_attr(attribute)

    @pytest.mark.parametrize("source", SOURCES)
    def test_each_carries_the_options_of_its_own_bounds(self, draw, source):
        soup = draw(source, form=CoordinateForm())

        latitude = json.loads(soup.find(id="id_latitude")["data-imask"])
        longitude = json.loads(soup.find(id="id_longitude")["data-imask"])

        assert (latitude["min"], latitude["max"]) == (-90, 90)
        assert (longitude["min"], longitude["max"]) == (-180, 180)

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_pack_gives_the_text_input_its_class(self, draw, source):
        soup = draw(source, form=CoordinateForm())

        assert "input" in soup.find(id="id_latitude")["class"]

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
        form = CoordinateForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_latitude")["class"]

    def test_the_form_names_the_script_that_applies_the_mask(self):
        assert "mvp_forms/imask.js" in str(CoordinateForm().media)
