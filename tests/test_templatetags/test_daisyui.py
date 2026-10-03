"""Tests for the pack's field tag and the input it draws."""

import copy

import pytest
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Hidden, Submit
from django import forms
from django.template import Context, Template
from django.utils.safestring import SafeString, mark_safe

from mvp_forms.templatetags.daisyui import (
    TAB_GROUP_PLACEHOLDER,
    FieldInput,
    daisyui_classes,
    daisyui_shown,
    daisyui_tab_group,
)
from tests.forms import (
    CheckboxForm,
    DateSelectsForm,
    DeveloperAttrsForm,
    FilesForm,
    HelpedForm,
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
