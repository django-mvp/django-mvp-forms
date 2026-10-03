"""Tests for the pack's input tag."""

import copy

import pytest
from django import forms

from mvp_forms.templatetags.daisyui import FieldInput
from tests.forms import DeveloperAttrsForm, TextInputsForm

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

        assert field_input.css_class.split() == ["wide", "input"]

    def test_a_class_the_developer_already_wrote_is_not_repeated(self):
        class Form(forms.Form):
            name = forms.CharField(widget=forms.TextInput(attrs={"class": "input a"}))

        assert FieldInput(Form()["name"]).css_class.split() == ["input", "a"]

    def test_the_render_draws_the_widget_with_the_class(self, parse):
        html = FieldInput(TextInputsForm()["text"]).render()

        assert parse(html).find("input")["class"] == ["input"]

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
