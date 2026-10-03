"""Tests for the pack's field tag and the input it draws."""

import copy

import pytest
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Hidden, Reset, Submit
from django import forms
from django.forms import formset_factory
from django.template import Context, Template
from django.utils.safestring import SafeString, mark_safe

from mvp_forms.choices import INHERIT, Choice, FormChoices, InvalidChoice
from mvp_forms.templatetags.daisyui import (
    TAB_GROUP_PLACEHOLDER,
    DrawnButton,
    FieldInput,
    FormsetTable,
    daisyui_button,
    daisyui_classes,
    daisyui_field,
    daisyui_formset_table,
    daisyui_shown,
    daisyui_tab_group,
)
from tests.forms import (
    CheckboxForm,
    DateSelectsForm,
    DeveloperAttrsForm,
    FilesForm,
    HelpedForm,
    LineFormSet,
    NoLinesFormSet,
    OwnTemplateDateWidget,
    SelectsForm,
    TextInputsForm,
    UncoveredInput,
)

KINDS = [
    ("text", "input"),
    ("email", "input"),
    ("url", "input"),
    ("number", "input"),
    ("password", "input"),
    ("date", "input"),
    ("time", "input"),
    ("date_time", "input"),
    ("message", "textarea"),
]


class ShortTextInput(forms.TextInput):
    pass


class HostSelect(forms.Select):
    pass


class OwnCheckboxInput(forms.CheckboxInput):
    pass


class SubclassedDateWidget(forms.SelectDateWidget):
    pass


class HostSelectForm(forms.Form):
    choice = forms.ChoiceField(choices=[("a", "A")], widget=HostSelect)
    born = forms.DateField(widget=forms.SelectDateWidget)


class OptionalRequiredAttributeForm(forms.Form):
    use_required_attribute = False

    name = forms.CharField()
    nickname = forms.CharField(required=False)
    choice = forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect)


class UncoveredForm(forms.Form):
    choice = forms.ChoiceField(choices=[("a", "A")], widget=UncoveredInput)
    short = forms.CharField(widget=ShortTextInput)
    styled = forms.ChoiceField(
        choices=[("a", "A")], widget=UncoveredInput(attrs={"class": "mine"})
    )


class OwnAriaForm(forms.Form):
    labelled = forms.CharField(
        widget=forms.TextInput(attrs={"aria-label": "Mine"}),
    )
    described = forms.CharField(
        widget=forms.TextInput(attrs={"aria-describedby": "mine"}),
        help_text="Some help",
    )


class GroupedHelpedForm(forms.Form):
    use_required_attribute = False

    choice = forms.ChoiceField(
        choices=[("a", "A")], widget=forms.RadioSelect, help_text="Some help"
    )


class MarkedUpLabelForm(forms.Form):
    tagged = forms.CharField(label=mark_safe('<a href="/x" title="y">Name</a>'))
    quoted = forms.CharField(label=mark_safe('He said "hi"'))
    unlabelled = forms.CharField(label="")


class OnlyHiddenForm(forms.Form):
    first = forms.CharField(widget=forms.HiddenInput)
    second = forms.CharField(widget=forms.HiddenInput)


OnlyHiddenFormSet = formset_factory(OnlyHiddenForm, extra=2)


class TestFieldInput:
    @pytest.mark.parametrize(("name", "component"), KINDS)
    def test_each_covered_kind_has_its_component(self, name, component):
        assert FieldInput(TextInputsForm()[name]).component == component

    def test_a_subclass_of_a_covered_widget_is_covered(self):
        assert FieldInput(UncoveredForm()["short"]).component == "input"

    @pytest.mark.parametrize("name", ["choice", "many", "maybe", "grouped"])
    def test_each_kind_of_select_has_the_select_component(self, name):
        assert FieldInput(SelectsForm()[name]).component == "select"

    def test_a_date_drawn_as_three_selects_has_the_select_component(self):
        assert FieldInput(HostSelectForm()["born"]).component == "select"

    def test_a_host_subclass_of_select_is_covered(self):
        assert FieldInput(HostSelectForm()["choice"]).component == "select"

    def test_a_boolean_field_has_the_checkbox_component(self):
        assert FieldInput(CheckboxForm()["agree"]).component == "checkbox"

    def test_a_checkbox_is_not_a_group_and_is_drawn_in_its_label(self):
        field_input = FieldInput(CheckboxForm()["agree"])

        assert not field_input.is_group
        assert field_input.is_single_checkbox

    def test_a_select_is_not_a_single_checkbox(self):
        assert not FieldInput(SelectsForm()["choice"]).is_single_checkbox

    def test_a_checkbox_is_given_no_width_and_gets_its_error_modifier(self):
        field_input = FieldInput(CheckboxForm({})["agree"])

        assert set(field_input.css_class.split()) == {"checkbox", "checkbox-error"}

    def test_an_invalid_select_gets_its_error_modifier(self):
        field_input = FieldInput(SelectsForm({"choice": "nowhere"})["choice"])

        assert "select-error" in field_input.css_class.split()

    def test_an_uncovered_widget_gets_no_pack_class(self):
        field_input = FieldInput(UncoveredForm()["choice"])

        assert field_input.component is None
        assert "class" not in field_input.attrs

    def test_an_uncovered_widget_keeps_its_own_class(self, parse):
        html = FieldInput(UncoveredForm()["styled"]).render()

        assert parse(html).find("input")["class"] == ["mine"]

    def test_the_developers_class_is_kept_beside_the_component(self):
        field_input = FieldInput(DeveloperAttrsForm()["name"])

        assert {"wide", "input"} <= set(field_input.css_class.split())

    def test_a_class_the_developer_already_wrote_is_not_repeated(self):
        class Form(forms.Form):
            name = forms.CharField(widget=forms.TextInput(attrs={"class": "input a"}))

        assert FieldInput(Form()["name"]).css_class.split().count("input") == 1

    def test_the_render_draws_the_widget_with_the_class(self, parse):
        html = FieldInput(TextInputsForm()["text"]).render()

        assert "input" in parse(html).find("input")["class"]

    def test_a_render_leaves_the_widgets_attrs_unchanged(self):
        form = DeveloperAttrsForm()
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        for name in form.fields:
            FieldInput(form[name]).render()

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before

    def test_a_required_field_gets_aria_required_when_the_form_drops_required(self):
        field_input = FieldInput(OptionalRequiredAttributeForm()["name"])

        assert field_input.attrs["aria-required"] == "true"

    def test_a_form_that_keeps_required_needs_no_aria_required(self):
        assert "aria-required" not in FieldInput(TextInputsForm()["text"]).attrs

    def test_an_optional_field_gets_no_aria_required(self):
        field_input = FieldInput(OptionalRequiredAttributeForm()["nickname"])

        assert "aria-required" not in field_input.attrs

    def test_a_grouped_widget_gets_no_aria_attribute(self):
        field_input = FieldInput(OptionalRequiredAttributeForm()["choice"])

        assert "aria-required" not in field_input.attrs

    @pytest.mark.parametrize(("name", "component"), KINDS)
    def test_an_invalid_field_gets_its_components_error_modifier(self, name, component):
        field_input = FieldInput(TextInputsForm({})[name])

        assert f"{component}-error" in field_input.css_class.split()

    @pytest.mark.parametrize(("name", "component"), KINDS)
    def test_a_valid_field_gets_no_error_modifier(self, name, component):
        field_input = FieldInput(TextInputsForm()[name])

        assert f"{component}-error" not in field_input.css_class.split()

    def test_an_invalid_field_with_an_uncovered_widget_gets_no_class(self):
        field_input = FieldInput(UncoveredForm({})["choice"])

        assert "class" not in field_input.attrs


class TestFieldInputTemplate:
    def test_the_stock_date_widget_has_the_packs_template(self):
        field_input = FieldInput(DateSelectsForm()["born"])

        assert field_input.template_name == "daisyui/widgets/select_date.html"

    def test_a_subclass_naming_its_own_template_has_none(self):
        assert FieldInput(DateSelectsForm()["own"]).template_name is None

    def test_a_widget_with_no_packs_template_has_none(self):
        assert FieldInput(TextInputsForm()["text"]).template_name is None

    def test_a_subclass_keeping_its_parents_template_has_the_packs(self):
        class Form(forms.Form):
            born = forms.DateField(widget=SubclassedDateWidget)

        assert FieldInput(Form()["born"]).template_name == (
            "daisyui/widgets/select_date.html"
        )

    def test_the_fields_widget_keeps_its_own_template_after_a_draw(self):
        form = DateSelectsForm()
        widget = form.fields["born"].widget
        before = widget.template_name

        FieldInput(form["born"]).render()

        assert form.fields["born"].widget is widget
        assert widget.template_name == before

    def test_a_widget_with_its_own_template_is_never_copied(self):
        form = DateSelectsForm()

        FieldInput(form["own"]).render()

        assert form.fields["own"].widget.template_name == (
            OwnTemplateDateWidget.template_name
        )

    def test_a_date_is_a_group(self):
        assert FieldInput(DateSelectsForm()["born"]).is_group

    def test_a_single_input_is_not_a_group(self):
        assert not FieldInput(TextInputsForm()["text"]).is_group


class TestFieldInputFiles:
    @pytest.mark.parametrize("name", ["plain", "empty", "several"])
    def test_each_kind_of_file_input_has_the_file_input_component(self, name):
        assert FieldInput(FilesForm()[name]).component == "file-input"

    def test_an_invalid_file_input_fills_its_field_and_gets_its_error_modifier(self):
        class Form(forms.Form):
            upload = forms.FileField()

        field_input = FieldInput(Form({})["upload"])

        assert set(field_input.css_class.split()) == {
            "file-input",
            "w-full",
            "file-input-error",
        }

    def test_a_clearable_file_input_has_the_packs_template(self):
        assert FieldInput(FilesForm()["empty"]).template_name == (
            "daisyui/widgets/clearable_file_input.html"
        )

    def test_a_plain_file_input_has_no_template_of_its_own(self):
        assert FieldInput(FilesForm()["plain"]).template_name is None

    def test_a_subclass_naming_its_own_template_has_none(self):
        assert FieldInput(FilesForm()["own"]).template_name is None

    def test_a_file_input_is_not_a_group(self):
        assert not FieldInput(FilesForm()["empty"]).is_group


class TestFieldInputGroupDescription:
    def test_help_text_alone_is_named(self):
        field_input = FieldInput(DateSelectsForm()["born"])

        assert field_input.group_description == "id_born_helptext"

    def test_errors_alone_are_named(self):
        form = DateSelectsForm(
            {"plain_year": "2020", "plain_month": "2", "plain_day": "31"}
        )

        assert FieldInput(form["plain"]).group_description == "id_plain_error"

    def test_help_text_and_errors_are_both_named_help_text_first(self):
        field_input = FieldInput(DateSelectsForm({})["born"])

        assert field_input.group_description == "id_born_helptext id_born_error"

    def test_neither_help_text_nor_errors_names_nothing(self):
        assert FieldInput(DateSelectsForm()["plain"]).group_description == ""

    def test_with_errors_off_only_the_help_text_is_named(self):
        field_input = FieldInput(DateSelectsForm({})["born"], show_errors=False)

        assert field_input.group_description == "id_born_helptext"

    def test_a_form_without_ids_names_nothing(self):
        form = DateSelectsForm({}, auto_id=False)

        assert FieldInput(form["born"]).group_description == ""


class TestFieldInputLabelsOff:
    def test_the_input_is_named_by_its_label(self):
        form = TextInputsForm()

        field_input = FieldInput(form["text"], show_labels=False)

        assert field_input.attrs["aria-label"] == form["text"].label

    def test_labels_on_add_no_aria_label(self):
        assert "aria-label" not in FieldInput(TextInputsForm()["text"]).attrs

    def test_a_field_without_a_label_gets_no_aria_label(self):
        field_input = FieldInput(MarkedUpLabelForm()["unlabelled"], show_labels=False)

        assert "aria-label" not in field_input.attrs

    def test_the_developers_own_aria_label_is_never_replaced(self, parse):
        field_input = FieldInput(OwnAriaForm()["labelled"], show_labels=False)

        assert "aria-label" not in field_input.attrs
        assert parse(field_input.render()).find("input")["aria-label"] == "Mine"

    @pytest.mark.parametrize(
        ("name", "expected"), [("tagged", "Name"), ("quoted", 'He said "hi"')]
    )
    def test_a_label_marked_safe_cannot_break_out_of_the_attribute(
        self, parse, name, expected
    ):
        form = MarkedUpLabelForm()

        drawn = parse(FieldInput(form[name], show_labels=False).render()).find("input")

        assert drawn["aria-label"] == expected
        assert not {"href", "title", "hi"} & set(drawn.attrs)

    def test_a_grouped_widget_gets_no_aria_label(self):
        field_input = FieldInput(
            OptionalRequiredAttributeForm()["choice"], show_labels=False
        )

        assert "aria-label" not in field_input.attrs


class TestFieldInputErrorsOff:
    def test_no_error_modifier_is_added(self):
        form = TextInputsForm({})

        field_input = FieldInput(form["text"], show_errors=False)

        assert "input-error" not in field_input.css_class.split()

    def test_the_description_names_the_help_text_only(self, parse):
        form = HelpedForm({})

        drawn = parse(FieldInput(form["helped"], show_errors=False).render())

        assert drawn.find("input")["aria-describedby"] == "id_helped_helptext"

    def test_with_no_help_text_the_input_has_no_description_and_keeps_its_id(
        self, parse
    ):
        form = HelpedForm({"bare": ""})

        drawn = parse(FieldInput(form["bare"], show_errors=False).render()).find(
            "input"
        )

        assert not drawn.has_attr("aria-describedby")
        assert drawn["id"] == "id_bare"
        assert drawn["name"] == "bare"
        assert drawn["aria-invalid"] == "true"
        assert drawn["required"] is not None

    def test_a_valid_field_keeps_its_description(self, parse):
        form = HelpedForm({"helped": "x", "bare": "x"})

        drawn = parse(FieldInput(form["helped"], show_errors=False).render())

        assert drawn.find("input")["aria-describedby"] == "id_helped_helptext"

    def test_errors_on_describe_the_error_element_too(self, parse):
        form = HelpedForm({})

        drawn = parse(FieldInput(form["helped"]).render()).find("input")

        assert drawn["aria-describedby"].split() == [
            "id_helped_helptext",
            "id_helped_error",
        ]

    def test_the_developers_own_description_is_left_alone(self, parse):
        form = OwnAriaForm({})

        field_input = FieldInput(form["described"], show_errors=False)

        assert "aria-describedby" not in field_input.attrs
        assert parse(field_input.render()).find("input")["aria-describedby"] == "mine"

    def test_a_form_without_ids_draws_no_description(self, parse):
        form = HelpedForm({}, auto_id=False)

        drawn = parse(FieldInput(form["helped"], show_errors=False).render()).find(
            "input"
        )

        assert not drawn.has_attr("aria-describedby")
        assert not drawn.has_attr("id")

    def test_a_render_leaves_the_widgets_attrs_unchanged(self):
        form = HelpedForm({})
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        FieldInput(form["bare"], show_errors=False).render()

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before


class TestFieldInputGroupedWidget:
    def test_with_labels_and_errors_off_it_receives_no_aria_attribute(self, parse):
        form = GroupedHelpedForm({})
        field_input = FieldInput(form["choice"], show_labels=False, show_errors=False)

        drawn = parse(field_input.render())

        assert not set(field_input.attrs) & {"aria-label", "aria-required"}
        assert "aria-describedby" not in field_input.attrs
        for tag in drawn.find_all(True):
            assert not set(tag.attrs) & {
                "aria-label",
                "aria-required",
                "aria-describedby",
            }


class EntityLabelForm(forms.Form):
    name = forms.CharField(label=mark_safe("Fish &amp; chips"))


class TestFieldInputEntityLabel:
    def test_an_entity_in_a_safe_label_is_named_as_its_character(self):
        field_input = FieldInput(EntityLabelForm()["name"], show_labels=False)

        assert field_input.attrs["aria-label"] == "Fish & chips"


class TestDaisyuiInputSwitches:
    def test_a_switch_that_is_not_false_is_on_for_the_input_and_the_frame(self, draw):
        form = HelpedForm({"bare": ""})

        page = draw(
            '{% include "daisyui/field.html" %}',
            field=form["bare"],
            form_show_errors=None,
        )

        assert page.find(id="id_bare_error") is not None
        assert "input-error" in page.find(id="id_bare")["class"]


class LiteralLabelForm(forms.Form):
    name = forms.CharField(label="Use <b> & AT&amp;T")


class TestFieldInputLiteralLabel:
    def test_a_label_not_marked_safe_is_named_exactly_as_written(self):
        field_input = FieldInput(LiteralLabelForm()["name"], show_labels=False)

        assert field_input.attrs["aria-label"] == "Use <b> & AT&amp;T"


class TestDaisyuiInputFalsySwitches:
    def test_a_switch_of_zero_hides_the_label_and_names_the_input(self, draw):
        form = HelpedForm()

        page = draw(
            '{% include "daisyui/field.html" %}',
            field=form["bare"],
            form_show_labels=0,
        )

        assert page.find("label") is None
        assert page.find(id="id_bare").has_attr("aria-label")


class OwnWidthForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "w-40"}))
    responsive = forms.CharField(widget=forms.TextInput(attrs={"class": "md:w-40"}))


class TestFieldInputDevelopersWidth:
    def test_a_width_the_developer_set_is_the_only_width_class(self):
        classes = FieldInput(OwnWidthForm()["name"]).css_class.split()

        assert [name for name in classes if name.startswith("w-")] == ["w-40"]

    def test_a_width_for_one_breakpoint_keeps_the_packs_width_beside_it(self):
        classes = FieldInput(OwnWidthForm()["responsive"]).css_class.split()

        assert {"md:w-40", FieldInput.width} <= set(classes)


class TestDaisyuiClasses:
    @pytest.mark.parametrize(
        "name", ["btn-inverse", "ctrlHolder", "blockLabel", "error"]
    )
    def test_a_name_written_for_another_pack_is_dropped(self, name):
        assert daisyui_classes(f"btn {name} mine") == "btn mine"

    @pytest.mark.parametrize("name", ["tab-pane", "active"])
    def test_a_name_written_for_tabs_is_dropped(self, name):
        assert daisyui_classes(f"tab-content {name} mine") == "tab-content mine"

    def test_a_name_written_for_alerts_is_dropped(self):
        assert daisyui_classes("alert alert-block mine") == "alert mine"

    def test_a_repeated_name_is_dropped(self):
        assert daisyui_classes("btn mine btn mine") == "btn mine"

    def test_the_order_is_kept(self):
        assert daisyui_classes("zeta alpha mid") == "zeta alpha mid"

    @pytest.mark.parametrize("value", [None, "", "   ", "btn-inverse error"])
    def test_nothing_left_gives_an_empty_string(self, value):
        assert daisyui_classes(value) == ""


class TestDaisyuiShown:
    def test_a_hidden_input_is_left_out_and_the_order_is_kept(self):
        save, go = Submit("save", "Save"), StrictButton("Go")

        assert daisyui_shown([save, Hidden("step", "two"), go]) == [save, go]

    @pytest.mark.parametrize("value", [None, []])
    def test_nothing_given_is_an_empty_list(self, value):
        assert daisyui_shown(value) == []


class TestFieldInputChoices:
    def test_the_forms_statement_adds_the_modifier_of_each_choice(self):
        choices = FormChoices(size="sm", color="primary", variant="ghost")

        field_input = FieldInput(TextInputsForm()["text"], choices=choices)

        assert set(field_input.css_class.split()) == {
            "input",
            "input-sm",
            "input-primary",
            "input-ghost",
            "w-full",
        }

    def test_an_empty_statement_leaves_the_class_string_as_it_was(self):
        field = TextInputsForm()["text"]

        assert (
            FieldInput(field, choices=FormChoices()).css_class
            == FieldInput(field).css_class
        )

    def test_a_field_in_error_keeps_its_error_modifier_and_drops_the_colour(self):
        choices = FormChoices(size="sm", color="primary", variant="ghost")

        field_input = FieldInput(TextInputsForm({})["text"], choices=choices)

        assert set(field_input.css_class.split()) == {
            "input",
            "input-sm",
            "input-ghost",
            "input-error",
            "w-full",
        }

    def test_the_developers_classes_are_kept_beside_the_modifiers(self):
        field_input = FieldInput(
            DeveloperAttrsForm()["name"], choices=FormChoices(size="sm")
        )

        assert {"wide", "input", "input-sm"} <= set(field_input.css_class.split())

    def test_a_choice_placed_around_the_field_wins_over_the_forms_statement(self):
        field_input = FieldInput(
            TextInputsForm()["text"],
            choices=FormChoices(size="lg", color="primary"),
            placed=Choice(size="xs"),
        )

        classes = set(field_input.css_class.split())
        assert {"input-xs", "input-primary"} <= classes
        assert "input-lg" not in classes

    def test_the_choice_named_for_the_field_wins_over_the_forms_statement(self):
        choices = FormChoices(
            size="lg", color="primary", fields={"text": Choice(color=None)}
        )

        classes = set(
            FieldInput(TextInputsForm()["text"], choices=choices).css_class.split()
        )

        assert "input-lg" in classes
        assert "input-primary" not in classes

    def test_a_placed_choice_is_merged_over_the_one_named_for_the_field(self):
        choices = FormChoices(fields={"text": Choice(size="sm", color="info")})

        field_input = FieldInput(
            TextInputsForm()["text"], choices=choices, placed=Choice(size="xl")
        )

        classes = set(field_input.css_class.split())
        assert {"input-xl", "input-info"} <= classes
        assert "input-sm" not in classes

    def test_a_mistake_in_the_forms_statement_is_raised_when_the_input_is_built(self):
        with pytest.raises(InvalidChoice) as caught:
            FieldInput(TextInputsForm()["text"], choices=FormChoices(size="huge"))

        assert caught.value.value == "huge"
        assert caught.value.target is None

    def test_a_mistake_in_a_fields_own_statement_names_the_field(self):
        with pytest.raises(InvalidChoice) as caught:
            FieldInput(TextInputsForm()["text"], placed=Choice(color="purple"))

        assert caught.value.kind == "color"
        assert caught.value.target == "text"

    def test_a_variant_the_form_states_is_passed_over_for_a_checkbox(self):
        field_input = FieldInput(
            CheckboxForm()["agree"], choices=FormChoices(variant="ghost")
        )

        assert set(field_input.css_class.split()) == {"checkbox"}

    def test_a_variant_a_field_states_for_a_checkbox_raises(self):
        with pytest.raises(InvalidChoice) as caught:
            FieldInput(CheckboxForm()["agree"], placed=Choice(variant="ghost"))

        assert caught.value.target == "agree"

    def test_a_widget_with_no_component_is_passed_over_for_the_form(self):
        field_input = FieldInput(
            UncoveredForm()["choice"], choices=FormChoices(size="sm")
        )

        assert "class" not in field_input.attrs

    def test_a_widget_with_no_component_raises_for_a_choice_of_its_own(self):
        with pytest.raises(InvalidChoice):
            FieldInput(UncoveredForm()["choice"], placed=Choice(size="sm"))

    def test_a_render_leaves_the_widgets_attrs_unchanged(self):
        form = DeveloperAttrsForm()
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        for name in form.fields:
            FieldInput(form[name], choices=FormChoices(size="sm")).render()

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before


class HelpedChoicesForm(forms.Form):
    name = forms.CharField()

    def __init__(self, statement):
        super().__init__()
        self.helper = FormHelper(self)
        self.helper.daisyui = statement


class TestDaisyuiFieldChoices:
    def test_the_statement_in_the_context_is_used(self):
        context = Context({"daisyui": FormChoices(size="sm")})

        drawn = daisyui_field(context, TextInputsForm()["text"])

        assert "input-sm" in drawn.css_class.split()

    def test_the_statement_on_the_fields_forms_helper_is_used(self):
        form = HelpedChoicesForm(FormChoices(size="lg"))

        drawn = daisyui_field(Context(), form["name"])

        assert "input-lg" in drawn.css_class.split()

    def test_the_choice_a_layout_placed_in_the_context_is_used(self):
        context = Context(
            {"daisyui": FormChoices(size="sm"), "daisyui_choice": Choice(size="xl")}
        )

        drawn = daisyui_field(context, TextInputsForm()["text"])

        classes = drawn.css_class.split()
        assert "input-xl" in classes
        assert "input-sm" not in classes

    def test_a_context_value_that_is_not_a_choice_is_the_pages_own(self):
        context = Context({"daisyui_choice": "the page's own"})

        drawn = daisyui_field(context, TextInputsForm()["text"])

        assert set(drawn.css_class.split()) == {"input", "w-full"}

    def test_a_helper_attribute_that_is_not_a_statement_raises(self):
        with pytest.raises(TypeError):
            daisyui_field(Context(), HelpedChoicesForm("sm")["name"])


class HandStyledFileForm(forms.Form):
    doc = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"class": "file-input-sm file-input-primary"}
        ),
    )


class TestFieldInputRemovalModifiers:
    def test_a_file_input_resolves_the_checkboxes_size_and_colour(self):
        choices = FormChoices(size="sm", color="accent", variant="ghost")

        field_input = FieldInput(FilesForm()["optional"], choices=choices)

        assert field_input.removal_modifiers == ["checkbox-sm", "checkbox-accent"]

    def test_nothing_stated_resolves_none(self):
        assert FieldInput(FilesForm()["optional"]).removal_modifiers == []

    def test_classes_written_by_hand_on_the_widget_resolve_none(self):
        field_input = FieldInput(HandStyledFileForm()["doc"])

        assert field_input.removal_modifiers == []

    def test_an_input_that_is_not_a_file_input_resolves_none(self):
        choices = FormChoices(size="sm")

        assert (
            FieldInput(TextInputsForm()["text"], choices=choices).removal_modifiers
            == []
        )

    def test_the_widget_drawn_names_them_in_its_context(self):
        field = FilesForm()["optional"]
        field_input = FieldInput(field, choices=FormChoices(size="lg"))

        context = field_input.widget.get_context("optional", field.value(), {})

        assert context["widget"]["removal_class"] == "checkbox-lg"

    def test_the_forms_own_widget_is_left_as_it_was(self):
        field = FilesForm()["optional"]

        FieldInput(field, choices=FormChoices(size="lg")).render()

        context = field.field.widget.get_context("optional", field.value(), {})
        assert "removal_class" not in context["widget"]


class TestDrawnButton:
    def test_a_submit_recoloured_on_the_instance_keeps_its_colour_and_takes_the_forms(
        self,
    ):
        submit = Submit("save", "Save")
        submit.field_classes = "btn btn-success"

        drawn = DrawnButton(submit, choices=FormChoices(button_color="neutral"))

        assert set(drawn.css_class.split()) == {"btn", "btn-success", "btn-neutral"}

    def test_a_base_input_takes_the_forms_size_colour_and_variant_for_buttons(self):
        choices = FormChoices(
            size="sm",
            color="info",
            variant="ghost",
            button_color="accent",
            button_variant="outline",
        )

        drawn = DrawnButton(Button("act", "Go"), choices=choices)

        assert set(drawn.css_class.split()) == {
            "btn",
            "btn-sm",
            "btn-accent",
            "btn-outline",
        }

    @pytest.mark.parametrize("kind", [Submit, Reset, Button])
    def test_stating_nothing_leaves_the_class_string_as_it_was(self, kind):
        button = kind("act", "Go", css_class="mine")

        assert DrawnButton(button, choices=FormChoices()).css_class == (
            daisyui_classes(button.field_classes)
        )

    def test_a_reset_carries_no_class_written_for_another_pack(self):
        drawn = DrawnButton(Reset("act", "Go"), choices=FormChoices(size="sm"))

        assert "btn-inverse" not in drawn.css_class.split()

    def test_a_submit_with_a_resolved_colour_loses_the_default_colour(self):
        drawn = DrawnButton(
            Submit("act", "Go"), choices=FormChoices(button_color="error")
        )

        assert set(drawn.css_class.split()) == {"btn", "btn-error"}

    def test_a_colour_set_to_none_for_the_button_leaves_the_default_colour(self):
        drawn = DrawnButton(
            Submit("act", "Go"),
            choices=FormChoices(button_color="error"),
            placed=Choice(color=None),
        )

        assert set(drawn.css_class.split()) == {"btn", "btn-primary"}

    def test_a_submit_keeps_a_colour_class_the_developer_gave_it(self):
        drawn = DrawnButton(
            Submit("act", "Go", css_class="btn-primary"),
            choices=FormChoices(button_color="error"),
        )

        assert {"btn-primary", "btn-error"} <= set(drawn.css_class.split())

    def test_a_choice_placed_around_the_button_wins_over_the_forms(self):
        drawn = DrawnButton(
            Button("act", "Go"),
            choices=FormChoices(size="sm", button_color="accent"),
            placed=Choice(size="xl"),
        )

        classes = drawn.css_class.split()
        assert {"btn-xl", "btn-accent"} <= set(classes)
        assert "btn-sm" not in classes

    def test_a_strict_button_gets_the_modifiers_inside_its_class_attribute(self):
        button = StrictButton("Go", css_class="mine", title="Act")

        drawn = DrawnButton(button, choices=FormChoices(size="sm"))

        assert drawn.flat_attrs != button.flat_attrs
        assert drawn.flat_attrs.count(" class=") == 1
        assert 'title="Act"' in drawn.flat_attrs
        attribute = drawn.flat_attrs.split(' class="')[1].split('"')[0]
        assert set(attribute.split()) == {"btn", "mine", "btn-sm"}

    @pytest.mark.parametrize("name", ["data_class", "aria_class"])
    def test_a_strict_button_with_an_attribute_ending_in_class_keeps_it_whole(
        self, name
    ):
        button = StrictButton("Go", **{name: "y"})

        drawn = DrawnButton(button, choices=FormChoices(size="sm"))

        attribute = name.replace("_", "-")
        assert f' {attribute}="y"' in drawn.flat_attrs
        assert drawn.flat_attrs.count("btn-sm") == 1
        assert f'{attribute}="y btn-sm"' not in drawn.flat_attrs

    def test_a_strict_button_with_nothing_stated_has_its_attributes_unchanged(self):
        button = StrictButton("Go", css_class="mine", data_class="y")

        assert DrawnButton(button, choices=FormChoices()).flat_attrs == (
            button.flat_attrs
        )

    def test_a_hidden_input_takes_no_modifier(self):
        drawn = DrawnButton(
            Hidden("secret", "x"), choices=FormChoices(size="sm", button_color="info")
        )

        assert drawn.modifiers == []

    def test_a_modifier_the_developer_already_wrote_is_written_once(self):
        drawn = DrawnButton(
            Button("act", "Go", css_class="btn-sm"), choices=FormChoices(size="sm")
        )

        assert drawn.css_class.split().count("btn-sm") == 1


class DrawingsForm(forms.Form):
    plain = forms.BooleanField(required=False)
    other = forms.BooleanField(required=False)
    text = forms.CharField(required=False)
    group = forms.MultipleChoiceField(
        choices=[("a", "A")], widget=forms.CheckboxSelectMultiple, required=False
    )
    maybe = forms.NullBooleanField()
    own = forms.BooleanField(required=False, widget=OwnCheckboxInput)
    must = forms.BooleanField()


def drawn(name, form=None, **kwargs):
    return FieldInput((form or DrawingsForm())[name], **kwargs)


class TestFieldInputDrawing:
    @pytest.mark.parametrize(
        ("drawing", "component"),
        [
            ("checkbox", "checkbox"),
            ("toggle", "toggle"),
            ("switch", "toggle"),
            (None, "checkbox"),
        ],
    )
    def test_a_drawing_stated_in_a_layout_gives_the_component(self, drawing, component):
        field_input = drawn("plain", placed=Choice(drawing=drawing))

        assert field_input.component == component

    def test_nothing_stated_gives_the_checkbox(self):
        assert drawn("plain").component == "checkbox"

    @pytest.mark.parametrize(
        ("drawing", "component"), [("toggle", "toggle"), ("switch", "toggle")]
    )
    def test_a_drawing_stated_by_name_gives_the_component(self, drawing, component):
        choices = FormChoices(fields={"plain": Choice(drawing=drawing)})

        assert drawn("plain", choices=choices).component == component

    def test_the_drawing_in_a_layout_wins_over_the_one_stated_by_name(self):
        choices = FormChoices(fields={"plain": Choice(drawing="toggle")})

        field_input = drawn("plain", choices=choices, placed=Choice(drawing="checkbox"))

        assert field_input.component == "checkbox"

    def test_none_in_a_layout_undoes_the_drawing_stated_by_name(self):
        choices = FormChoices(fields={"plain": Choice(drawing="switch")})

        field_input = drawn("plain", choices=choices, placed=Choice(drawing=None))

        assert field_input.component == "checkbox"

    def test_a_drawing_stated_for_another_field_changes_nothing_here(self):
        choices = FormChoices(fields={"other": Choice(drawing="switch")})

        assert drawn("plain", choices=choices).component == "checkbox"

    @pytest.mark.parametrize(
        ("drawing", "role"),
        [("switch", "switch"), ("toggle", None), ("checkbox", None), (None, None)],
    )
    def test_only_a_switch_carries_a_role(self, drawing, role):
        attrs = drawn("plain", placed=Choice(drawing=drawing)).attrs

        assert attrs.get("role") == role

    @pytest.mark.parametrize("drawing", ["checkbox", "toggle", "switch"])
    def test_each_drawing_is_a_single_checkbox_to_the_frame(self, drawing):
        field_input = drawn("plain", placed=Choice(drawing=drawing))

        assert field_input.is_single_checkbox

    @pytest.mark.parametrize("drawing", ["toggle", "switch"])
    def test_a_toggle_is_written_with_the_toggle_class(self, drawing):
        classes = drawn("plain", placed=Choice(drawing=drawing)).css_class.split()

        assert "toggle" in classes
        assert "checkbox" not in classes

    def test_a_field_in_error_drawn_as_a_toggle_carries_the_toggle_error_modifier(
        self,
    ):
        form = DrawingsForm({})

        field_input = drawn("must", form, placed=Choice(drawing="toggle"))

        assert "toggle-error" in field_input.css_class.split()

    def test_a_subclass_of_the_checkbox_widget_takes_a_drawing(self):
        field_input = drawn("own", placed=Choice(drawing="switch"))

        assert field_input.component == "toggle"
        assert field_input.attrs["role"] == "switch"

    def test_an_unknown_name_on_a_boolean_field_raises_with_the_three_names(self):
        with pytest.raises(InvalidChoice) as caught:
            drawn("plain", placed=Choice(drawing="slider"))

        assert caught.value.kind == "drawing"
        assert caught.value.value == "slider"
        assert caught.value.allowed == ("checkbox", "toggle", "switch")
        assert caught.value.target == "plain"

    def test_an_unknown_name_stated_by_name_raises_naming_the_field(self):
        choices = FormChoices(fields={"plain": Choice(drawing="slider")})

        with pytest.raises(InvalidChoice) as caught:
            drawn("plain", choices=choices)

        assert caught.value.kind == "drawing"
        assert caught.value.target == "plain"

    @pytest.mark.parametrize("name", ["text", "group", "maybe"])
    @pytest.mark.parametrize("drawing", ["checkbox", "toggle", "switch"])
    def test_any_drawing_on_a_field_that_is_not_a_boolean_field_raises(
        self, name, drawing
    ):
        with pytest.raises(InvalidChoice) as caught:
            drawn(name, placed=Choice(drawing=drawing))

        assert caught.value.kind == "drawing"
        assert caught.value.value == drawing
        assert caught.value.allowed == ()
        assert caught.value.target == name

    @pytest.mark.parametrize("name", ["text", "group", "maybe"])
    def test_an_unknown_name_on_a_field_that_is_not_a_boolean_field_allows_nothing(
        self, name
    ):
        with pytest.raises(InvalidChoice) as caught:
            drawn(name, placed=Choice(drawing="slider"))

        assert caught.value.allowed == ()

    @pytest.mark.parametrize("name", ["plain", "text", "group", "maybe"])
    def test_a_list_given_as_the_name_raises_invalid_choice(self, name):
        with pytest.raises(InvalidChoice) as caught:
            drawn(name, placed=Choice(drawing=["toggle"]))

        assert caught.value.kind == "drawing"

    @pytest.mark.parametrize("name", ["text", "group", "maybe"])
    @pytest.mark.parametrize("drawing", [None, INHERIT])
    def test_none_and_inherit_state_nothing_for_any_field(self, name, drawing):
        field_input = drawn(name, placed=Choice(drawing=drawing))

        assert field_input.component != "toggle"

    def test_a_drawing_stated_by_name_for_a_text_field_raises(self):
        choices = FormChoices(fields={"text": Choice(drawing="toggle")})

        with pytest.raises(InvalidChoice) as caught:
            drawn("text", choices=choices)

        assert caught.value.target == "text"

    def test_a_render_draws_a_switch_as_a_checkbox_input_with_the_role(self, parse):
        field_input = drawn("plain", placed=Choice(drawing="switch"))

        tag = parse(field_input.render()).find("input")

        assert tag["type"] == "checkbox"
        assert tag["name"] == "plain"
        assert tag["role"] == "switch"
        assert "toggle" in tag["class"]

    def test_a_render_leaves_the_widgets_attrs_unchanged(self):
        form = DrawingsForm()
        before = copy.deepcopy(form.fields["plain"].widget.attrs)

        drawn("plain", form, placed=Choice(drawing="switch")).render()

        assert form.fields["plain"].widget.attrs == before


class TestDrawnButtonDrawing:
    @pytest.mark.parametrize("drawing", ["checkbox", "toggle", "switch", "slider"])
    @pytest.mark.parametrize(
        "button", [Submit("save", "Save"), StrictButton("More", css_id="more")]
    )
    def test_a_drawing_stated_around_a_button_raises(self, button, drawing):
        with pytest.raises(InvalidChoice) as caught:
            DrawnButton(button, placed=Choice(drawing=drawing))

        assert caught.value.kind == "drawing"
        assert caught.value.value == drawing
        assert caught.value.allowed == ()
        assert caught.value.target is not None

    def test_the_button_is_the_target(self):
        with pytest.raises(InvalidChoice) as caught:
            DrawnButton(Submit("save", "Save"), placed=Choice(drawing="toggle"))

        assert caught.value.target == "save"

    @pytest.mark.parametrize("drawing", [None, INHERIT])
    def test_none_and_inherit_state_nothing_for_a_button(self, drawing):
        built = DrawnButton(Submit("save", "Save"), placed=Choice(drawing=drawing))

        assert built.modifiers == []

    def test_a_hidden_input_takes_no_drawing_and_raises_nothing(self):
        built = DrawnButton(Hidden("secret", "x"), placed=Choice(drawing="toggle"))

        assert built.modifiers == []


class TestDaisyuiButton:
    def test_the_statement_in_the_context_is_used(self):
        context = Context({"daisyui": FormChoices(size="lg")})

        drawn = daisyui_button(context, Button("act", "Go"))

        assert "btn-lg" in drawn.css_class.split()

    def test_the_choice_a_layout_placed_in_the_context_is_used(self):
        context = Context(
            {"daisyui": FormChoices(size="sm"), "daisyui_choice": Choice(size="xl")}
        )

        drawn = daisyui_button(context, Button("act", "Go"))

        classes = drawn.css_class.split()
        assert "btn-xl" in classes
        assert "btn-sm" not in classes

    def test_a_context_value_that_is_not_a_statement_is_the_pages_own(self):
        context = Context({"daisyui": "the page's own", "daisyui_choice": 3})

        drawn = daisyui_button(context, Button("act", "Go"))

        assert drawn.css_class == "btn"

    def test_a_context_with_no_statement_draws_the_button_as_it_was(self):
        drawn = daisyui_button(Context(), Submit("act", "Go"))

        assert set(drawn.css_class.split()) == {"btn", "btn-primary"}


def tab_radio(checked=False):
    return (
        f'<input type="radio" {TAB_GROUP_PLACEHOLDER}{" checked" if checked else ""}>'
    )


def radios_in(html, parse):
    return parse(html).find_all("input")


class TestDaisyuiTabGroup:
    def test_every_placeholder_is_replaced_by_one_name(self, parse):
        panes = tab_radio() + "<div></div>" + tab_radio() + "<div></div>"

        names = {radio["name"] for radio in radios_in(daisyui_tab_group(panes), parse)}

        assert len(names) == 1
        assert TAB_GROUP_PLACEHOLDER.split('"')[1] not in names

    def test_two_calls_give_two_names(self, parse):
        panes = tab_radio()

        first = radios_in(daisyui_tab_group(panes), parse)[0]["name"]
        second = radios_in(daisyui_tab_group(panes), parse)[0]["name"]

        assert first != second

    def test_the_first_radio_is_checked_when_none_is(self, parse):
        panes = tab_radio() + tab_radio()

        radios = radios_in(daisyui_tab_group(panes), parse)

        assert [radio.has_attr("checked") for radio in radios] == [True, False]

    def test_a_checked_radio_is_left_alone(self, parse):
        panes = tab_radio() + tab_radio(checked=True)

        radios = radios_in(daisyui_tab_group(panes), parse)

        assert [radio.has_attr("checked") for radio in radios] == [False, True]

    def test_panes_without_a_radio_are_returned_as_they_are(self):
        assert daisyui_tab_group("<div></div>") == "<div></div>"

    def test_safe_input_stays_safe(self):
        template = Template("{% load daisyui %}{{ panes|daisyui_tab_group }}")

        html = template.render(Context({"panes": SafeString(tab_radio())}))

        assert html.startswith("<input")

    def test_unsafe_input_is_escaped(self):
        template = Template("{% load daisyui %}{{ panes|daisyui_tab_group }}")

        html = template.render(Context({"panes": tab_radio()}))

        assert html.startswith("&lt;input")


class TestFormsetTable:
    def test_the_columns_are_the_first_forms_visible_fields_in_order(self):
        formset = LineFormSet()

        table = FormsetTable(formset)

        assert [column.name for column in table.columns] == ["name", "quantity"]
        assert all(column.form is formset.forms[0] for column in table.columns)

    def test_a_hidden_field_is_not_a_column(self):
        table = FormsetTable(LineFormSet())

        assert "ref" not in [column.name for column in table.columns]

    def test_there_is_one_row_per_form_in_the_formsets_order(self):
        formset = LineFormSet()

        table = FormsetTable(formset)

        assert [row["form"] for row in table.rows] == formset.forms

    def test_each_cell_is_that_forms_own_bound_field(self):
        formset = LineFormSet()

        table = FormsetTable(formset)

        for row in table.rows:
            assert [cell.html_name for cell in row["cells"]] == [
                row["form"].add_prefix("name"),
                row["form"].add_prefix("quantity"),
            ]
            assert all(cell.form is row["form"] for cell in row["cells"])

    def test_a_form_without_a_columns_field_has_none_there(self):
        formset = LineFormSet()
        del formset.forms[1].fields["quantity"]

        table = FormsetTable(formset)

        assert [cell is None for cell in table.rows[1]["cells"]] == [False, True]
        assert all(len(row["cells"]) == len(table.columns) for row in table.rows)

    def test_a_field_only_a_later_form_has_is_not_a_column(self):
        formset = LineFormSet()
        formset.forms[1].fields["extra"] = forms.CharField()

        table = FormsetTable(formset)

        assert [column.name for column in table.columns] == ["name", "quantity"]

    def test_no_forms_gives_no_columns_and_no_rows(self):
        table = FormsetTable(NoLinesFormSet())

        assert table.columns == []
        assert table.rows == []

    def test_forms_with_only_hidden_fields_give_each_row_one_empty_cell(self):
        formset = OnlyHiddenFormSet()

        table = FormsetTable(formset)

        assert table.columns == []
        assert [row["cells"] for row in table.rows] == [[None], [None]]
        assert [row["form"] for row in table.rows] == formset.forms

    def test_the_tag_returns_the_table_of_the_formset(self):
        formset = LineFormSet()

        table = daisyui_formset_table(formset)

        assert isinstance(table, FormsetTable)
        assert [row["form"] for row in table.rows] == formset.forms
