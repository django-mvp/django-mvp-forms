"""The layout objects that draw buttons: inputs, buttons, holders and helper buttons."""

import pytest
from crispy_forms.layout import Button, Reset, Submit

DEVELOPER_CLASSES = ["mine", "other"]
DEVELOPER_ATTRS = {"data-role": "action", "title": "Act"}
BASE_INPUTS = [
    pytest.param(Submit, "submit", id="submit"),
    pytest.param(Reset, "reset", id="reset"),
    pytest.param(Button, "button", id="button"),
]


class TestBaseInputs:
    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_an_input_of_its_own_type_with_its_name_and_value(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go"))

        control = soup.find("input", attrs={"name": "act"})
        assert control["type"] == input_type
        assert control["value"] == "Go"

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_a_daisyui_button(self, draw_layout, kind, input_type):
        soup = draw_layout(kind("act", "Go"))

        assert "btn" in soup.find("input", attrs={"name": "act"})["class"]

    def test_a_reset_carries_no_class_written_for_another_pack(self, draw_layout):
        soup = draw_layout(Reset("act", "Clear"))

        assert "btn-inverse" not in soup.find("input", attrs={"name": "act"})["class"]

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(
            kind(
                "act",
                "Go",
                css_id="go",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        )

        control = soup.find("input", id="go")
        assert set(DEVELOPER_CLASSES) <= set(control["class"])
        assert "btn" in control["class"]
        assert control["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert control["title"] == DEVELOPER_ATTRS["title"]

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_drawn_disabled_when_given_disabled(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go", disabled=True))

        assert soup.find("input", attrs={"name": "act"}).has_attr("disabled")

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_not_disabled_unless_asked(self, draw_layout, kind, input_type):
        soup = draw_layout(kind("act", "Go"))

        assert not soup.find("input", attrs={"name": "act"}).has_attr("disabled")

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_a_value_reading_the_context_is_filled_in(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go, {{ who }}"), who="Ada")

        assert soup.find("input", attrs={"name": "act"})["value"] == "Go, Ada"
