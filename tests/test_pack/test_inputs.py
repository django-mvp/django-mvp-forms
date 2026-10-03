"""The text-like fields, drawn through django-crispy-forms."""

import copy

import pytest

from tests.forms import DeveloperAttrsForm, TextInputsForm

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
        assert name["class"] == ["wide", "input"]
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
