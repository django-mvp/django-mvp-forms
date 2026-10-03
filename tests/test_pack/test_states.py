"""The disabled and read-only states, drawn through django-crispy-forms."""

import pytest

from tests.forms import (
    DisabledAndReadOnlyForm,
    DisabledInputsForm,
    ReadOnlyInputsForm,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]

DISABLED_KINDS = [
    ("text", "input", "input"),
    ("number", "input", "input"),
    ("date", "input", "input"),
    ("message", "textarea", "textarea"),
    ("choice", "select", "select"),
    ("agree", "input", "checkbox"),
    ("upload", "input", "file-input"),
]

READ_ONLY_KINDS = [
    ("text", "input", "input"),
    ("message", "textarea", "textarea"),
    ("choice", "select", "select"),
    ("agree", "input", "checkbox"),
    ("upload", "input", "file-input"),
]


def options_of(soup, name):
    return [
        option
        for option in soup.find_all("input", attrs={"name": name})
        if option.get("type") != "hidden"
    ]


class TestDisabled:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "element", "component"), DISABLED_KINDS)
    def test_a_disabled_input_has_disabled_and_its_component_class(
        self, draw, source, name, element, component
    ):
        soup = draw(source, form=DisabledInputsForm())

        drawn = soup.find(id=f"id_{name}")

        assert drawn.name == element
        assert drawn.has_attr("disabled")
        assert component in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("name", "value"), [("text", "Ada"), ("number", "42"), ("date", "2026-10-03")]
    )
    def test_a_disabled_text_input_still_holds_its_value(
        self, draw, source, name, value
    ):
        soup = draw(source, form=DisabledInputsForm())

        assert soup.find(id=f"id_{name}")["value"] == value

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_textarea_still_holds_its_value(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        assert soup.find(id="id_message").string.strip() == "Hello there"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_select_still_holds_its_choice(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        chosen = soup.find(id="id_choice").find_all("option", selected=True)

        assert [option["value"] for option in chosen] == ["b"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_checkbox_is_still_ticked(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        assert soup.find(id="id_agree").has_attr("checked")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_file_field_still_links_to_its_file(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        frame = soup.find(id="div_id_upload")

        assert frame.find("a")["href"] == "/media/kept.pdf"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_file_field_disables_its_removal_checkbox(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        removal = soup.find(id="upload-clear_id")

        assert removal["type"] == "checkbox"
        assert removal.has_attr("disabled")
        assert "checkbox" in removal["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("name", "component", "held"),
        [("radios", "radio", ["b"]), ("boxes", "checkbox", ["a", "b"])],
    )
    def test_every_option_of_a_disabled_group_is_disabled(
        self, draw, source, name, component, held
    ):
        soup = draw(source, form=DisabledInputsForm())

        options = options_of(soup, name)

        assert [option["value"] for option in options] == ["a", "b"]
        assert all(option.has_attr("disabled") for option in options)
        assert all(component in option["class"] for option in options)
        assert [o["value"] for o in options if o.has_attr("checked")] == held

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_password_input_has_no_value(self, draw, source):
        soup = draw(source, form=DisabledInputsForm())

        secret = soup.find(id="id_secret")

        assert secret.has_attr("disabled")
        assert not secret.has_attr("value")


class TestReadOnly:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "element", "component"), READ_ONLY_KINDS)
    def test_a_readonly_attribute_is_on_the_input_unchanged(
        self, draw, source, name, element, component
    ):
        soup = draw(source, form=ReadOnlyInputsForm())

        drawn = soup.find(id=f"id_{name}")

        assert drawn.name == element
        assert drawn["readonly"] == ""
        assert component in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "element", "component"), READ_ONLY_KINDS)
    def test_the_pack_adds_no_class_for_readonly(
        self, draw, source, name, element, component
    ):
        readonly = draw(source, form=ReadOnlyInputsForm()).find(id=f"id_{name}")
        plain = ReadOnlyInputsForm()
        plain.fields[name].widget.attrs.pop("readonly")

        unmarked = draw(source, form=plain).find(id=f"id_{name}")

        assert readonly["class"] == unmarked["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_readonly_text_input_has_a_name_its_value_and_no_disabled(
        self, draw, source
    ):
        soup = draw(source, form=ReadOnlyInputsForm())

        drawn = soup.find(id="id_text")

        assert drawn["name"] == "text"
        assert drawn["value"] == "Ada"
        assert not drawn.has_attr("disabled")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_readonly_textarea_has_a_name_its_value_and_no_disabled(
        self, draw, source
    ):
        soup = draw(source, form=ReadOnlyInputsForm())

        drawn = soup.find(id="id_message")

        assert drawn["name"] == "message"
        assert drawn.string.strip() == "Hello there"
        assert not drawn.has_attr("disabled")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_text_input_both_disabled_and_readonly_has_both(self, draw, source):
        soup = draw(source, form=DisabledAndReadOnlyForm())

        drawn = soup.find(id="id_text")

        assert drawn.has_attr("disabled")
        assert drawn.has_attr("readonly")
