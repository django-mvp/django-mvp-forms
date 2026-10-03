"""Tests for the choices a form states: the table, its rules and the statement."""

import pytest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import LayoutObject
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


class TestChoiceDrawing:
    def test_it_is_inherited_by_default(self):
        assert Choice().drawing is INHERIT

    def test_it_is_kept(self):
        assert Choice(drawing="toggle").drawing == "toggle"

    def test_none_is_kept(self):
        assert Choice(drawing=None).drawing is None

    def test_over_takes_the_inner_drawing_when_stated(self):
        merged = Choice(drawing="toggle").over(Choice(drawing="switch"))

        assert merged.drawing == "toggle"

    def test_over_takes_the_outer_drawing_when_the_inner_one_is_left_out(self):
        merged = Choice(size="sm").over(Choice(drawing="switch"))

        assert merged.drawing == "switch"

    def test_over_states_none_when_the_inner_drawing_is_none(self):
        merged = Choice(drawing=None).over(Choice(drawing="switch"))

        assert merged.drawing is None

    def test_over_inherits_a_drawing_neither_choice_states(self):
        merged = Choice(size="sm").over(Choice(color="info"))

        assert merged.drawing is INHERIT

    def test_over_changes_neither_choice(self):
        inner = Choice(drawing="toggle")
        outer = Choice(drawing="switch")

        inner.over(outer)

        assert (inner.drawing, outer.drawing) == ("toggle", "switch")


class TestModifiersDrawings:
    def test_each_drawing_names_the_component_it_is_drawn_with(self):
        assert Modifiers.drawings == {
            "checkbox": "checkbox",
            "toggle": "toggle",
            "switch": "toggle",
            "rating": "rating",
        }


class TestModifiersToggle:
    def test_a_toggle_has_the_same_sizes_and_colours_as_the_other_inputs(self):
        assert tuple(Modifiers.sizes["toggle"]) == SIZES
        assert tuple(Modifiers.colors["toggle"]) == COLORS

    def test_a_toggle_has_no_variant(self):
        assert "toggle" not in Modifiers.variants

    @pytest.mark.parametrize("name", SIZES)
    def test_each_size_resolves_to_its_toggle_class(self, name):
        assert Modifiers.resolve("size", "toggle", form=name) == f"toggle-{name}"

    @pytest.mark.parametrize("name", COLORS)
    def test_each_colour_resolves_to_its_toggle_class(self, name):
        assert Modifiers.resolve("color", "toggle", own=name) == f"toggle-{name}"

    def test_a_variant_the_form_states_is_passed_over(self):
        assert Modifiers.resolve("variant", "toggle", form="ghost") is None

    def test_a_variant_a_field_states_raises_with_nothing_allowed(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("variant", "toggle", own="ghost", target="notify")

        assert (caught.value.kind, caught.value.value) == ("variant", "ghost")
        assert (caught.value.allowed, caught.value.target) == ((), "notify")

    def test_a_field_in_error_drops_the_colour_and_keeps_the_size(self):
        assert Modifiers.resolve("color", "toggle", form="info", in_error=True) is None
        assert Modifiers.resolve("size", "toggle", form="sm", in_error=True) == (
            "toggle-sm"
        )

    def test_an_unknown_size_raises_with_the_names_allowed(self):
        with pytest.raises(InvalidChoice) as caught:
            Modifiers.resolve("size", "toggle", own="huge", target="notify")

        assert (caught.value.allowed, caught.value.target) == (SIZES, "notify")


class Recorder:
    def __init__(self, leaves_a_layer=False):
        self.leaves_a_layer = leaves_a_layer
        self.seen = []

    def render(self, form, context, template_pack=None, **kwargs):
        self.seen.append(context.get(Choice.context_name))
        if self.leaves_a_layer:
            context.update({"left": "behind"})
        return "<recorded>"


class TestChoiceRender:
    def test_it_is_a_layout_object(self):
        assert isinstance(Choice("name"), LayoutObject)

    def test_what_it_holds_is_drawn_with_itself_placed_in_the_context(self):
        held = Recorder()
        choice = Choice(held, size="lg")

        choice.render(None, Context(), template_pack="daisyui")

        placed = held.seen[0]
        assert isinstance(placed, Choice)
        assert placed.size == "lg"

    def test_everything_it_holds_is_drawn_in_order(self):
        first, second = Recorder(), Recorder()

        html = Choice(first, second, size="lg").render(
            None, Context(), template_pack="daisyui"
        )

        assert html == "<recorded><recorded>"
        assert len(first.seen) == len(second.seen) == 1

    def test_an_inner_choice_is_placed_merged_over_the_outer_one(self):
        held = Recorder()
        inner = Choice(held, color="info")
        outer = Choice(inner, size="lg", color="accent")

        outer.render(None, Context(), template_pack="daisyui")

        placed = held.seen[0]
        assert (placed.size, placed.color) == ("lg", "info")

    def test_the_outer_choice_is_placed_again_after_an_inner_one(self):
        before, after = Recorder(), Recorder()
        outer = Choice(Choice(before, size="sm"), after, size="lg")

        outer.render(None, Context(), template_pack="daisyui")

        assert before.seen[0].size == "sm"
        assert after.seen[0].size == "lg"

    def test_nothing_is_placed_in_the_context_afterwards(self):
        context = Context()

        Choice(Recorder(), size="lg").render(None, context, template_pack="daisyui")

        assert Choice.context_name not in context

    def test_a_choice_placed_before_is_visible_again_afterwards(self):
        outer = Choice(size="xl")
        context = Context({Choice.context_name: outer})

        Choice(Recorder(), size="lg").render(None, context, template_pack="daisyui")

        assert context[Choice.context_name] is outer

    def test_it_removes_its_own_layer_when_what_it_holds_leaves_one_above(self):
        context = Context()
        depth = len(context.dicts)

        Choice(Recorder(leaves_a_layer=True), size="lg").render(
            None, context, template_pack="daisyui"
        )

        assert Choice.context_name not in context
        assert context["left"] == "behind"
        assert len(context.dicts) == depth + 1

    def test_it_removes_its_own_layer_when_drawing_what_it_holds_raises(self):
        class Failing:
            def render(self, form, context, template_pack=None, **kwargs):
                raise RuntimeError

        context = Context()

        with pytest.raises(RuntimeError):
            Choice(Failing(), size="lg").render(None, context, template_pack="daisyui")

        assert Choice.context_name not in context


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


class TestFormChoicesCheck:
    @pytest.mark.parametrize(
        ("keyword", "kind", "allowed"),
        [
            ("size", "size", SIZES),
            ("color", "color", COLORS),
            ("variant", "variant", INPUT_VARIANTS),
            ("button_color", "color", COLORS),
            ("button_variant", "variant", BUTTON_VARIANTS),
        ],
    )
    def test_a_name_daisyui_lacks_raises_for_its_kind_and_family(
        self, keyword, kind, allowed
    ):
        with pytest.raises(InvalidChoice) as caught:
            FormChoices(**{keyword: "nonesuch"}).check()

        error = caught.value
        assert (error.kind, error.value, error.target) == (kind, "nonesuch", None)
        assert error.allowed == allowed

    def test_a_variant_only_buttons_have_is_refused_for_the_inputs(self):
        with pytest.raises(InvalidChoice) as caught:
            FormChoices(variant="outline").check()

        assert "outline" not in caught.value.allowed

    def test_a_variant_inputs_and_buttons_share_is_accepted_for_both(self):
        FormChoices(variant="ghost", button_variant="ghost").check()

    def test_a_statement_of_nothing_is_accepted(self):
        FormChoices().check()

    def test_lookup_checks_the_statement_it_finds_in_the_context(self):
        with pytest.raises(InvalidChoice):
            FormChoices.lookup(Context({"daisyui": FormChoices(button_color="x")}))

    def test_lookup_checks_the_statement_it_finds_on_the_helper(self):
        with pytest.raises(InvalidChoice):
            FormChoices.lookup(
                Context(), HelpedForm(FormChoices(button_variant="glow"))
            )
