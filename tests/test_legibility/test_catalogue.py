import pytest

from mvp_forms.choices import Modifiers
from mvp_forms.templatetags.daisyui import FieldInput
from tests.legibility.catalogue import Catalogue
from tests.test_pack.test_independence import STATES


def written(states):
    return {
        name
        for state in states
        for tag in state.soup.find_all(class_=True)
        for name in tag["class"]
    }


def tags(states, selector):
    return [tag for state in states for tag in state.soup.select(selector)]


class TestCatalogue:
    def test_every_id_in_states_is_a_state(self):
        names = {state.name for state in Catalogue.states()}

        assert {param.id for param in STATES} <= names

    def test_state_names_are_unique(self):
        names = [state.name for state in Catalogue.states()]

        assert len(set(names)) == len(names)

    def test_a_state_keeps_the_classes_its_form_supplied(self):
        by_name = {state.name: state for state in Catalogue.states()}

        assert by_name["developer class"].supplied == {"wide"}

    def test_every_class_in_the_modifier_tables_is_written_by_a_state(self):
        classes = written(Catalogue.states())
        named = {
            name
            for table in Modifiers.tables.values()
            for modifiers in table.values()
            for name in modifiers.values()
        }

        assert named
        assert named <= classes, named - classes

    def test_every_component_and_error_modifier_is_written_by_a_state(self):
        classes = written(Catalogue.states())
        named = set(FieldInput.components.values()) | set(
            FieldInput.error_modifiers.values()
        )

        assert named <= classes, named - classes

    def test_every_button_colour_is_drawn_with_every_button_variant(self):
        drawn = {
            (colour, variant)
            for tag in tags(Catalogue.states(), "[class~=btn]")
            for colour in Modifiers.colors["btn"].values()
            for variant in Modifiers.variants["btn"].values()
            if {colour, variant} <= set(tag["class"])
        }

        assert drawn == {
            (colour, variant)
            for colour in Modifiers.colors["btn"].values()
            for variant in Modifiers.variants["btn"].values()
        }

    @pytest.mark.parametrize(
        "kind", ["input", "textarea", "select", "file-input", "checkbox", "radio"]
    )
    def test_a_disabled_control_of_each_kind_is_drawn(self, kind):
        assert tags(Catalogue.states(), f"[class~={kind}][disabled]")

    def test_a_disabled_toggle_is_drawn(self):
        assert tags(Catalogue.states(), "[class~=toggle][disabled]")

    def test_a_disabled_toggle_is_drawn_as_a_switch_too(self):
        assert tags(Catalogue.states(), "[class~=toggle][role=switch][disabled]")

    def test_a_rating_is_drawn_plain_in_error_and_disabled(self):
        states = Catalogue.states()

        assert tags(states, ".rating input[class='mask mask-star-2']")
        assert tags(states, ".rating input.bg-error")
        assert tags(states, ".rating input.mask[disabled]")

    def test_a_range_is_drawn_plain_in_error_and_disabled(self):
        states = Catalogue.states()

        assert tags(states, "input[type=range][class='range w-full']")
        assert tags(states, "input[type=range].range-error")
        assert tags(states, "input[type=range].range[disabled]")

    def test_a_read_only_input_is_drawn(self):
        assert tags(Catalogue.states(), "[class~=input][readonly]")

    def test_an_alert_in_each_colour_is_drawn_with_its_dismiss_button(self):
        for colour in Modifiers.colors["btn"]:
            alerts = tags(Catalogue.states(), f"[role=alert].alert-{colour}")

            assert any(alert.select("button.btn") for alert in alerts), colour

    def test_reading_every_state_raises_nothing(self):
        assert Catalogue.measurements()

    def test_every_measurement_names_its_state(self):
        names = {state.name for state in Catalogue.states()}

        assert {m.form_state for m in Catalogue.measurements()} <= names

    def test_the_measurements_are_read_once(self):
        assert Catalogue.measurements() is Catalogue.measurements()
