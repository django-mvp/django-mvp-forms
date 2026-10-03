"""Tests for the choices a form states: the table, its rules and the statement."""

import pytest
from crispy_forms.helper import FormHelper
from django import forms
from django.template import Context

from mvp_forms.choices import (
    INHERIT,
    Choice,
    FormChoices,
    InvalidChoice,
    Modifiers,
)

INPUT_COMPONENTS = ["input", "textarea", "select", "file-input", "checkbox", "radio"]
SIZES = ("xs", "sm", "md", "lg", "xl")
COLORS = (
    "neutral",
    "primary",
    "secondary",
    "accent",
    "info",
    "success",
    "warning",
    "error",
)
INPUT_VARIANTS = ("ghost",)
BUTTON_VARIANTS = ("outline", "dash", "soft", "ghost", "link")


class HelpedForm(forms.Form):
    def __init__(self, statement):
        super().__init__()
        self.helper = FormHelper(self)
        self.helper.daisyui = statement


class TestModifiersTables:
    @pytest.mark.parametrize("component", [*INPUT_COMPONENTS, "btn"])
    def test_every_component_has_the_same_sizes_and_colours(self, component):
        assert tuple(Modifiers.sizes[component]) == SIZES
        assert tuple(Modifiers.colors[component]) == COLORS

    @pytest.mark.parametrize("component", ["checkbox", "radio"])
    def test_a_checkbox_and_a_radio_have_no_variant(self, component):
        assert component not in Modifiers.variants

    @pytest.mark.parametrize("component", ["input", "textarea", "select", "file-input"])
    def test_a_text_like_input_has_the_ghost_variant(self, component):
        assert tuple(Modifiers.variants[component]) == INPUT_VARIANTS

    def test_a_button_has_five_variants(self):
        assert tuple(Modifiers.variants["btn"]) == BUTTON_VARIANTS


class TestModifiersResolve:
    @pytest.mark.parametrize(
        ("kind", "component", "name", "expected"),
        [
            ("size", "input", "sm", "input-sm"),
            ("size", "file-input", "lg", "file-input-lg"),
            ("size", "radio", "xs", "radio-xs"),
            ("size", "btn", "xl", "btn-xl"),
            ("color", "textarea", "primary", "textarea-primary"),
            ("color", "checkbox", "error", "checkbox-error"),
            ("color", "btn", "neutral", "btn-neutral"),
            ("variant", "select", "ghost", "select-ghost"),
            ("variant", "btn", "outline", "btn-outline"),
            ("variant", "btn", "link", "btn-link"),
        ],
    )
    def test_a_name_resolves_to_the_components_class(
        self, kind, component, name, expected
    ):
        assert Modifiers.resolve(kind, component, form=name) == expected

    def test_md_is_a_name_with_a_class_of_its_own(self):
        assert Modifiers.resolve("size", "input", form="md") == "input-md"

    def test_nothing_stated_resolves_to_no_class(self):
        assert Modifiers.resolve("size", "input") is None

    def test_the_forms_statement_is_used_when_the_field_states_nothing(self):
        assert Modifiers.resolve("size", "input", own=INHERIT, form="sm") == "input-sm"

    def test_the_fields_own_statement_wins_over_the_forms(self):
        assert Modifiers.resolve("size", "input", own="lg", form="sm") == "input-lg"

    def test_none_is_the_ordinary_drawing_and_undoes_the_forms_statement(self):
        assert Modifiers.resolve("size", "input", own=None, form="sm") is None

    def test_each_kind_is_resolved_on_its_own(self):
        assert Modifiers.resolve("color", "input", own=INHERIT, form="info") == (
            "input-info"
        )
        assert Modifiers.resolve("variant", "input", own="ghost") == "input-ghost"

    @pytest.mark.parametrize(
        ("kind", "component", "allowed"),
        [
            ("size", "input", SIZES),
            ("size", "btn", SIZES),
            ("color", "textarea", COLORS),
            ("color", "btn", COLORS),
            ("variant", "select", INPUT_VARIANTS),
            ("variant", "btn", BUTTON_VARIANTS),
        ],
    )
    def test_an_unknown_name_from_the_form_raises_with_the_names_allowed(
        self, kind, component, allowed
    ):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve(kind, component, form="nonesuch")

        assert caught.value.kind == kind
        assert caught.value.value == "nonesuch"
        assert caught.value.allowed == allowed
        assert caught.value.target is None

    def test_an_unknown_name_from_a_field_raises_and_names_the_field(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve(
                "color", "input", own="purple", form="info", target="name"
            )

        assert caught.value.kind == "color"
        assert caught.value.value == "purple"
        assert caught.value.allowed == COLORS
        assert caught.value.target == "name"

    def test_an_invalid_choice_is_a_value_error(self):
        assert issubclass(InvalidChoice, ValueError)

    def test_the_message_holds_the_names_allowed(self):
        error = InvalidChoice("size", "huge", SIZES, "name")

        assert all(name in str(error) for name in SIZES)

    def test_a_name_belonging_to_buttons_alone_is_unknown_to_an_input(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("variant", "input", form="outline")

        assert caught.value.allowed == INPUT_VARIANTS

    def test_a_form_name_the_field_overrides_is_not_checked_for_that_field(self):
        assert Modifiers.resolve("size", "input", own="lg", form="huge") == "input-lg"

    @pytest.mark.parametrize("component", ["checkbox", "radio"])
    def test_a_variant_the_form_states_is_passed_over_for_a_kind_without_it(
        self, component
    ):
        assert Modifiers.resolve("variant", component, form="ghost") is None

    @pytest.mark.parametrize("component", ["checkbox", "radio"])
    def test_a_variant_a_field_states_for_a_kind_without_it_raises(self, component):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("variant", component, own="ghost", target="agree")

        assert caught.value.kind == "variant"
        assert caught.value.value == "ghost"
        assert caught.value.allowed == ()
        assert caught.value.target == "agree"

    def test_a_choice_for_a_widget_with_no_component_is_passed_over_for_the_form(
        self,
    ):
        assert Modifiers.resolve("size", None, form="sm") is None

    def test_a_choice_for_a_widget_with_no_component_raises_for_the_field(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("size", None, own="sm", target="moment")

        assert caught.value.allowed == ()
        assert caught.value.target == "moment"

    def test_an_unknown_name_is_reported_for_a_widget_with_no_component(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("size", None, form="huge")

        assert caught.value.allowed == SIZES

    def test_a_field_in_error_drops_the_colour(self):
        assert Modifiers.resolve("color", "input", form="info", in_error=True) is None
        assert Modifiers.resolve("color", "btn", own="info", in_error=True) is None

    def test_a_field_in_error_keeps_its_size_and_variant(self):
        assert Modifiers.resolve("size", "input", form="sm", in_error=True) == (
            "input-sm"
        )
        assert Modifiers.resolve("variant", "input", form="ghost", in_error=True) == (
            "input-ghost"
        )

    def test_a_misspelt_colour_is_reported_on_a_field_in_error(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("color", "input", form="purple", in_error=True)

        assert caught.value.value == "purple"

    @pytest.mark.parametrize("value", [["sm"], {"sm": 1}, 3])
    def test_a_value_that_is_not_a_name_raises_and_does_not_crash(self, value):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("size", "input", form=value)

        assert caught.value.value == value


class TestChoice:
    def test_every_argument_is_inherited_by_default(self):
        choice = Choice()

        assert choice.size is INHERIT
        assert choice.color is INHERIT
        assert choice.variant is INHERIT

    def test_the_arguments_are_kept(self):
        choice = Choice(size="lg", color=None, variant="ghost")

        assert choice.size == "lg"
        assert choice.color is None
        assert choice.variant == "ghost"

    def test_the_fields_it_holds_are_kept_in_order(self):
        assert list(Choice("one", "two", size="lg").fields) == ["one", "two"]

    def test_it_holds_no_fields_by_default(self):
        assert list(Choice(size="lg").fields) == []

    def test_over_takes_each_kind_from_the_inner_choice_when_stated(self):
        inner = Choice(size="sm", color=None)
        outer = Choice(size="lg", color="info", variant="ghost")

        merged = inner.over(outer)

        assert merged.size == "sm"
        assert merged.color is None
        assert merged.variant == "ghost"

    def test_over_inherits_what_neither_choice_states(self):
        merged = Choice(size="sm").over(Choice(color="info"))

        assert merged.size == "sm"
        assert merged.color == "info"
        assert merged.variant is INHERIT

    def test_over_changes_neither_choice(self):
        inner = Choice(size="sm")
        outer = Choice(size="lg", color="info")

        inner.over(outer)

        assert (inner.size, inner.color) == ("sm", INHERIT)
        assert (outer.size, outer.color) == ("lg", "info")


class TestFormChoices:
    def test_nothing_is_stated_by_default(self):
        statement = FormChoices()

        assert statement.size is None
        assert statement.color is None
        assert statement.variant is None
        assert statement.button_color is None
        assert statement.button_variant is None
        assert statement.fields == {}

    def test_the_statements_are_kept(self):
        search = Choice(size="lg")

        statement = FormChoices(
            size="sm",
            color="primary",
            variant="ghost",
            button_color="neutral",
            button_variant="outline",
            fields={"search": search},
        )

        assert statement.size == "sm"
        assert statement.color == "primary"
        assert statement.variant == "ghost"
        assert statement.button_color == "neutral"
        assert statement.button_variant == "outline"
        assert statement.fields == {"search": search}

    def test_a_keyword_it_does_not_know_is_refused(self):
        with pytest.raises(TypeError):
            FormChoices(colour="primary")

    def test_the_attribute_and_context_name_is_daisyui(self):
        assert FormChoices.attribute == "daisyui"

    def test_the_contexts_statement_is_found(self):
        statement = FormChoices(size="sm")

        found = FormChoices.lookup(Context({"daisyui": statement}))

        assert found is statement

    def test_the_helpers_statement_is_found_for_a_form(self):
        statement = FormChoices(size="sm")

        found = FormChoices.lookup(Context(), HelpedForm(statement))

        assert found is statement

    def test_the_contexts_statement_wins_over_the_helpers(self):
        from_context = FormChoices(size="sm")
        from_helper = FormChoices(size="lg")

        found = FormChoices.lookup(
            Context({"daisyui": from_context}), HelpedForm(from_helper)
        )

        assert found is from_context

    def test_neither_context_nor_helper_finds_nothing(self):
        assert FormChoices.lookup(Context()) is None
        assert FormChoices.lookup(Context(), forms.Form()) is None

    def test_a_form_whose_helper_states_nothing_finds_nothing(self):
        form = forms.Form()
        form.helper = FormHelper(form)

        assert FormChoices.lookup(Context(), form) is None

    def test_a_context_value_that_is_not_a_statement_is_treated_as_absent(self):
        assert FormChoices.lookup(Context({"daisyui": "the page's own"})) is None

    def test_a_context_value_that_is_not_a_statement_leaves_the_helpers(self):
        statement = FormChoices(size="sm")

        found = FormChoices.lookup(
            Context({"daisyui": {"the": "page"}}), HelpedForm(statement)
        )

        assert found is statement

    @pytest.mark.parametrize("value", ["sm", {"size": "sm"}, None, Choice()])
    def test_a_helper_attribute_that_is_not_a_statement_raises(self, value):
        with pytest.raises(TypeError):
            FormChoices.lookup(Context(), HelpedForm(value))
