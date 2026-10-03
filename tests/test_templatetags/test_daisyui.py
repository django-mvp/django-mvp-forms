"""Tests for the pack's input tag."""

import copy

import pytest
from django import forms
from django.utils.safestring import mark_safe

from mvp_forms.templatetags.daisyui import FieldInput
from tests.forms import DeveloperAttrsForm, HelpedForm, TextInputsForm

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


class OptionalRequiredAttributeForm(forms.Form):
    use_required_attribute = False

    name = forms.CharField()
    nickname = forms.CharField(required=False)
    choice = forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect)


class UncoveredForm(forms.Form):
    choice = forms.ChoiceField(choices=[("a", "A")])
    short = forms.CharField(widget=ShortTextInput)
    styled = forms.ChoiceField(
        choices=[("a", "A")], widget=forms.Select(attrs={"class": "mine"})
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


class TestFieldInput:
    @pytest.mark.parametrize(("name", "component"), KINDS)
    def test_each_covered_kind_has_its_component(self, name, component):
        assert FieldInput(TextInputsForm()[name]).component == component

    def test_a_subclass_of_a_covered_widget_is_covered(self):
        assert FieldInput(UncoveredForm()["short"]).component == "input"

    def test_an_uncovered_widget_gets_no_pack_class(self):
        field_input = FieldInput(UncoveredForm()["choice"])

        assert field_input.component is None
        assert "class" not in field_input.attrs

    def test_an_uncovered_widget_keeps_its_own_class(self, parse):
        html = FieldInput(UncoveredForm()["styled"]).render()

        assert parse(html).find("select")["class"] == ["mine"]

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
