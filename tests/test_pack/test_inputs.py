"""The text-like fields, drawn through django-crispy-forms."""

import copy
import re

import pytest

from tests.forms import (
    DeveloperAttrsForm,
    NoFieldsForm,
    SecretForm,
    TextInputsForm,
    TextInputsWithLayoutForm,
    UncoveredWidgetsForm,
)

FRAME_ID = re.compile(r"^div_")

KINDS = [
    ("text", "input", "input"),
    ("email", "input", "input"),
    ("url", "input", "input"),
    ("number", "input", "input"),
    ("password", "input", "input"),
    ("date", "input", "input"),
    ("time", "input", "input"),
    ("date_time", "input", "input"),
    ("message", "textarea", "textarea"),
]


class TestCoveredInputs:
    @pytest.mark.parametrize(("name", "element", "component"), KINDS)
    def test_each_kind_is_drawn_as_its_daisyui_component(
        self, draw, name, element, component
    ):
        soup = draw("{{ form|crispy }}", form=TextInputsForm())

        drawn = soup.find(id=f"id_{name}")

        assert drawn.name == element
        assert component in drawn["class"]

    def test_the_developers_attributes_all_arrive(self, draw):
        soup = draw("{{ form|crispy }}", form=DeveloperAttrsForm())

        name, born, notes = (soup.find(id=f"id_{n}") for n in ("name", "born", "notes"))

        assert name["placeholder"] == "Your name"
        assert {"wide", "input"} <= set(name["class"])
        assert born["type"] == "date"
        assert "input" in born["class"]
        assert notes["rows"] == "3"
        assert "textarea" in notes["class"]

    def test_name_id_and_value_are_djangos(self, draw):
        form = TextInputsForm({"text": "hello", "message": "a note"})

        soup = draw("{{ form|crispy }}", form=form)

        text = soup.find(id="id_text")
        assert text["name"] == "text"
        assert text["value"] == "hello"
        assert soup.find(id="id_message").get_text().strip() == "a note"

    def test_the_widgets_attrs_are_unchanged_by_a_draw(self, draw):
        form = DeveloperAttrsForm()
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        draw("{{ form|crispy }}", form=form)

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before


class TestCrispyTag:
    @pytest.mark.parametrize("form_class", [TextInputsForm, TextInputsWithLayoutForm])
    def test_each_field_matches_what_the_filter_drew(self, draw, form_class):
        by_filter = draw("{{ form|crispy }}", form=form_class())

        by_tag = draw("{% crispy form %}", form=form_class())

        for name in TextInputsForm.base_fields:
            assert str(by_tag.find(id=f"div_id_{name}")) == str(
                by_filter.find(id=f"div_id_{name}")
            )

    def test_a_form_with_no_fields_still_has_its_form_element(self, draw):
        soup = draw("{% crispy form %}", form=NoFieldsForm())

        assert soup.find("form") is not None
        assert soup.find_all(id=FRAME_ID) == []


class TestBoundValues:
    def test_each_input_holds_what_was_submitted(self, draw):
        data = {
            "text": "hello",
            "email": "a@example.com",
            "url": "https://example.com",
            "number": "42",
            "date": "2026-01-02",
            "time": "10:30",
            "date_time": "2026-01-02 10:30",
        }

        soup = draw("{{ form|crispy }}", form=TextInputsForm(data))

        for name, value in data.items():
            assert soup.find(id=f"id_{name}")["value"] == value

    def test_a_textarea_holds_what_was_submitted(self, draw):
        soup = draw("{{ form|crispy }}", form=TextInputsForm({"message": "a note"}))

        assert soup.find(id="id_message").get_text().strip() == "a note"

    def test_a_password_is_empty_unless_the_widget_renders_its_value(self, draw):
        form = SecretForm({"hidden": "s3cret", "shown": "s3cret"})

        soup = draw("{{ form|crispy }}", form=form)

        assert not soup.find(id="id_hidden").get("value")
        assert soup.find(id="id_shown")["value"] == "s3cret"


class TestSingleField:
    def test_it_is_drawn_as_it_is_inside_the_whole_form(self, draw):
        form = TextInputsForm({"text": "hello"})

        whole = draw("{{ form|crispy }}", form=form)
        single = draw("{{ form.text|as_crispy_field }}", form=form)

        assert str(single.find(id="div_id_text")) == str(whole.find(id="div_id_text"))


class TestUncoveredWidgets:
    def test_each_field_keeps_its_place_with_label_help_text_and_errors(self, draw):
        form = UncoveredWidgetsForm({"choice": "z"})

        soup = draw("{{ form|crispy }}", form=form)

        frames = [frame["id"] for frame in soup.find_all(id=FRAME_ID)]
        assert frames == [f"div_id_{name}" for name in form.fields]
        for name in form.fields:
            frame = soup.find(id=f"div_id_{name}")
            assert frame.find("label", attrs={"for": f"id_{name}"})
            assert frame.find(id=f"id_{name}_helptext")
            assert frame.find(id=f"id_{name}_error")

    def test_the_form_draws_through_the_tag_too(self, draw):
        soup = draw("{% crispy form %}", form=UncoveredWidgetsForm({"choice": "z"}))

        assert len(soup.find_all(id=FRAME_ID)) == 5


class TestNoFields:
    def test_the_filter_draws_no_field(self, draw):
        soup = draw("{{ form|crispy }}", form=NoFieldsForm())

        assert soup.find_all(id=FRAME_ID) == []
