"""Latitude and longitude fields, drawn as the pack draws a masked text input."""

import json

import pytest
from crispy_forms.helper import FormHelper
from django import forms

from mvp_forms.choices import FormChoices
from mvp_forms.fields import LatitudeField, LongitudeField, PointField

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


class PointForm(forms.Form):
    place = PointField(label="Place", help_text="Where it was found", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class TestPointField:
    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_is_one_fieldset_whose_legend_is_the_label(self, draw, source):
        soup = draw(source, form=PointForm())

        frame = soup.find(id="div_id_place")

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend")) == 1

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_has_one_help_text_and_one_set_of_errors(self, draw, source):
        soup = draw(source, form=PointForm({"place_0": "", "place_1": "5"}))

        frame = soup.find(id="div_id_place")

        assert len(frame.find_all(id="id_place_helptext")) == 1
        assert len(frame.find_all(id="id_place_error")) == 1

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_draws_two_text_inputs_each_named_and_each_with_its_mask(
        self, draw, source
    ):
        soup = draw(source, form=PointForm())

        latitude = soup.find(attrs={"name": "place_0"})
        longitude = soup.find(attrs={"name": "place_1"})

        for part in (latitude, longitude):
            assert part["type"] == "text"
            assert part["aria-label"]
            assert json.loads(part["data-imask"])["kind"] == "coordinate"
            for attribute in ("step", "min", "max"):
                assert not part.has_attr(attribute)
        assert latitude["aria-label"] != longitude["aria-label"]
        assert json.loads(latitude["data-imask"])["max"] == 90
        assert json.loads(longitude["data-imask"])["max"] == 180

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "input-lg"),
            ("color", "primary", "input-primary"),
            ("variant", "ghost", "input-ghost"),
        ],
    )
    def test_both_parts_take_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = PointForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        for name in ("place_0", "place_1"):
            frame = soup.find(attrs={"name": name}).find_parent("label")
            assert added in frame["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_each_part_sits_in_its_own_input_frame_with_a_visible_name(
        self, draw, source
    ):
        soup = draw(source, form=PointForm())

        names = []
        for name in ("place_0", "place_1"):
            part = soup.find(attrs={"name": name})
            frame = part.find_parent("label")
            assert "input" in frame["class"]
            assert "input" not in part.get("class", [])
            names.append(frame.find("span", class_="label").get_text(strip=True))
        assert names == [
            soup.find(attrs={"name": "place_0"})["aria-label"],
            soup.find(attrs={"name": "place_1"})["aria-label"],
        ]
        assert soup.find(attrs={"name": "place_0"}).find_parent("label") is not (
            soup.find(attrs={"name": "place_1"}).find_parent("label")
        )

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_both_parts_are_marked_invalid_when_the_field_is_in_error(
        self, draw, source
    ):
        soup = draw(source, form=PointForm({"place_0": "", "place_1": "5"}))

        for name in ("place_0", "place_1"):
            assert soup.find(attrs={"name": name})["aria-invalid"] == "true"

    def test_the_form_names_the_script_that_applies_the_mask(self):
        assert "mvp_forms/imask.js" in str(PointForm().media)
