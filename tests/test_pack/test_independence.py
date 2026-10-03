"""What the pack depends on and what it writes: daisyUI only, nothing of django-mvp."""

import ast
import re
from pathlib import Path

import pytest
from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    Alert,
    AppendedText,
    FieldWithButtons,
    FormActions,
    InlineCheckboxes,
    InlineField,
    InlineRadios,
    Modal,
    PrependedAppendedText,
    PrependedText,
    StrictButton,
    Tab,
    TabHolder,
    UneditableField,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    Button,
    ButtonHolder,
    Column,
    Div,
    Fieldset,
    Hidden,
    MultiField,
    MultiWidgetField,
    Reset,
    Row,
    Submit,
)
from django.apps import apps

import mvp_forms
from mvp_forms.choices import Choice, FormChoices, Modifiers
from tests.forms import (
    ButtonedForm,
    CheckboxForm,
    CheckboxGroupsForm,
    DateSelectsForm,
    DecoratedFieldsForm,
    DeveloperAttrsForm,
    DrawnBooleansForm,
    EveryInputForm,
    FieldAndFormWideErrorsForm,
    FilesForm,
    FloatingForm,
    FormWideErrorsForm,
    HelpedForm,
    InlineCheckboxesForm,
    InlineFieldsForm,
    InlineRadiosForm,
    LineFormSet,
    MediaForm,
    MultiWidgetsForm,
    RadioGroupsForm,
    RequiredDrawnBooleanForm,
    RuledLineFormSet,
    SelectsForm,
    StructureForm,
    TextInputsForm,
    UncoveredWidgetsForm,
    UneditableFieldsForm,
    ruled_data,
)

PACKAGE = Path(mvp_forms.__file__).parent
TEMPLATES = sorted((PACKAGE / "templates").rglob("*.html"))
FORBIDDEN_MODULES = {"mvp", "django_cotton", "daisy_cotton"}
FORBIDDEN_LIBRARIES = {"cotton", "mvp"}

DEVELOPER_CLASS = "wide"
LABEL_CLASS = "supplied-by-label-class"
FIELD_CLASS = "supplied-by-field-class"
FORM_CLASS = "supplied-by-form-class"
HELPER_CLASSES = {LABEL_CLASS, FIELD_CLASS, FORM_CLASS}
MINE = frozenset({"mine"})
# Tailwind utilities the pack writes where daisyUI has no class for the job.
# Each is named here so that adding one is a reviewed change.
LAYOUT_UTILITIES = {
    "w-full",
    "flex",
    "flex-col",
    "gap-4",
    "md:flex-row",
    "flex-1",
    "min-w-0",
    "flex-wrap",
    "gap-2",
    "mt-4",
    "overflow-x-auto",
}


def helped(form, **settings):
    form.helper = FormHelper()
    for name, value in settings.items():
        setattr(form.helper, name, value)
    return form


def stating(form, choices):
    form.helper.daisyui = choices
    return form


def supplying_classes(form):
    return helped(
        form, label_class=LABEL_CLASS, field_class=FIELD_CLASS, form_class=FORM_CLASS
    )


def classes_in(soup):
    return {name for tag in soup.find_all(class_=True) for name in tag["class"]}


def imported_modules(path):
    modules = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            modules.add(node.module.split(".")[0])
    return modules


def structured(data=None):
    return StructureForm(
        data,
        layout=(
            Fieldset(
                "Account",
                Div(Row(Column("first"), Column("second")), css_id="box"),
                HTML("<p>Written for {{ who }}</p>"),
                "third",
            ),
            "fourth",
        ),
    )


def buttoned(data=None):
    return StructureForm(
        data,
        layout=(
            "first",
            Hidden("step", "two"),
            FormActions(
                Submit("save", "Save"),
                Reset("clear", "Clear"),
                Button("help", "Help"),
                StrictButton("More", css_id="more"),
            ),
            ButtonHolder(Submit("again", "Again")),
        ),
    )


def everything(data=None):
    return StructureForm(
        data,
        layout=(
            Fieldset(
                "Account",
                Div(Row(Column("first"), Column("second")), css_id="box"),
                HTML("<p>Written for {{ who }}</p>"),
            ),
            MultiField("Contact", "third", css_id="contact"),
            Hidden("step", "two"),
            FormActions(
                Submit("save", "Save"),
                Reset("clear", "Clear"),
                Button("help", "Help"),
                StrictButton("More", css_id="more"),
            ),
            ButtonHolder(Submit("again", "Again")),
        ),
    )


def tabbed(data=None):
    return StructureForm(
        data,
        layout=(
            TabHolder(
                Tab("One", "first", css_class="mine"),
                Tab("Two", Row("second"), Fieldset("Group", "third")),
                Tab("Three", TabHolder(Tab("Inner", "fourth"))),
                css_class="mine",
            ),
        ),
    )


def accordioned(data=None):
    return StructureForm(
        data,
        layout=(
            Accordion(
                AccordionGroup("One", "first", css_class="mine"),
                AccordionGroup("Two", Row("second"), Fieldset("Group", "third")),
                AccordionGroup("Three", "fourth", active=True),
                css_class="mine",
            ),
        ),
    )


def modalled(data=None):
    return StructureForm(
        data,
        layout=(
            Modal(
                "first",
                Row("second"),
                css_id="box",
                css_class="mine",
                title="Details",
                title_class="mine",
            ),
            "third",
        ),
    )


def alerted(data=None):
    return StructureForm(
        data,
        layout=(
            "first",
            Alert("Mind <b>this</b>", css_id="note", css_class="alert-warning mine"),
            Alert("Stay", dismiss=False, block=True),
            "second",
        ),
    )


def attached(data=None):
    return DecoratedFieldsForm(
        data,
        layout=(
            PrependedText("amount", "$"),
            AppendedText("country", "#"),
            PrependedAppendedText("other", "$", ".00"),
        ),
    )


def with_buttons(data=None):
    return DecoratedFieldsForm(
        data,
        layout=(
            FieldWithButtons("amount", StrictButton("Go")),
            FieldWithButtons(
                "country",
                Submit("search", "Search"),
                Button("clear", "Clear"),
                css_id="joined-country",
            ),
            FieldWithButtons("other"),
        ),
    )


def uneditable(data=None):
    return UneditableFieldsForm(
        data,
        layout=(
            UneditableField("account"),
            UneditableField("country"),
            UneditableField("agree"),
            UneditableField("pick"),
            UneditableField("boxes"),
            UneditableField("notes"),
            UneditableField("empty", css_class="mine"),
        ),
    )


def inlined_fields(data=None):
    return InlineFieldsForm(
        data,
        layout=(
            InlineField("name"),
            InlineField("own"),
            InlineField("named"),
            InlineField("marked"),
            InlineField("note"),
            InlineField("country"),
            InlineField("agree"),
            InlineField("pick"),
            InlineField("plain", css_class="mine"),
        ),
    )


def inlined_radios(data=None):
    return InlineRadiosForm(
        data,
        layout=(
            InlineRadios("choice"),
            InlineRadios("grouped"),
            InlineRadios("locked"),
        ),
    )


def inlined_checkboxes(data=None):
    return InlineCheckboxesForm(
        data,
        layout=(
            InlineCheckboxes("choice"),
            InlineCheckboxes("grouped"),
            InlineCheckboxes("locked"),
        ),
    )


def multi_widget(data=None):
    return MultiWidgetsForm(
        data,
        layout=(
            MultiWidgetField(
                "moment", attrs=({"class": "mine"}, {"placeholder": "12:30"})
            ),
            MultiWidgetField("phone", attrs={"data-part": "phone"}),
            "ends",
            "name",
        ),
    )


def helper_buttons():
    return ButtonedForm(
        buttons=(
            Submit("save", "Save"),
            Reset("clear", "Clear"),
            Button("help", "Help"),
        )
    )


def failing_lines():
    return RuledLineFormSet(
        ruled_data(
            {"name": "a", "quantity": "6"},
            {"name": "", "quantity": "6"},
            {"name": "whole", "ref": "bad"},
        )
    )


NOTHING = frozenset()
TOGGLE_AND_SWITCH = FormChoices(
    fields={"notify": Choice(drawing="toggle"), "publish": Choice(drawing="switch")}
)
TOGGLE_AND_SWITCH_IN_ERROR = FormChoices(
    fields={"agree": Choice(drawing="toggle"), "notify": Choice(drawing="switch")}
)
TOGGLE_AND_SWITCH_SIZED = FormChoices(
    size="sm",
    color="primary",
    fields={
        "notify": Choice(drawing="toggle"),
        "publish": Choice(drawing="switch", size="lg", color="accent"),
    },
)
TOGGLE_AND_SWITCH_SIZED_IN_ERROR = FormChoices(
    size="sm",
    color="primary",
    fields={
        "agree": Choice(drawing="toggle"),
        "notify": Choice(drawing="switch", size="xl", color="success"),
    },
)
EVERY_CHOICE = FormChoices(size="sm", color="primary", variant="ghost")
FLOATING_LABELS = FormChoices(label="floating")
EVERY_BUTTON_CHOICE = FormChoices(
    size="lg", color="accent", button_color="neutral", button_variant="outline"
)
ERRORS_ONLY = "{{ form|as_crispy_errors }}"

STATES = [
    pytest.param("{{ form|crispy }}", TextInputsForm, NOTHING, id="unbound"),
    pytest.param(
        "{{ form|crispy }}", lambda: TextInputsForm({}), NOTHING, id="invalid"
    ),
    pytest.param("{{ form|crispy }}", lambda: HelpedForm({}), NOTHING, id="help text"),
    pytest.param(
        "{{ form|crispy }}",
        lambda: FormWideErrorsForm({}),
        NOTHING,
        id="form-wide errors",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: FieldAndFormWideErrorsForm({}),
        NOTHING,
        id="field and form-wide errors",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: DeveloperAttrsForm({}),
        {DEVELOPER_CLASS},
        id="developer class",
    ),
    pytest.param("{{ form|crispy }}", SelectsForm, NOTHING, id="selects"),
    pytest.param(
        "{{ form|crispy }}", lambda: SelectsForm({}), NOTHING, id="invalid selects"
    ),
    pytest.param("{{ form|crispy }}", DateSelectsForm, NOTHING, id="dates"),
    pytest.param(
        "{{ form|crispy }}", lambda: DateSelectsForm({}), NOTHING, id="invalid dates"
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(DateSelectsForm({}), form_show_labels=False),
        NOTHING,
        id="dates without labels",
    ),
    pytest.param("{{ form|crispy }}", CheckboxForm, MINE, id="checkboxes"),
    pytest.param(
        "{{ form|crispy }}", lambda: CheckboxForm({}), MINE, id="invalid checkboxes"
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(CheckboxForm({}), form_show_labels=False),
        MINE,
        id="checkboxes without labels",
    ),
    pytest.param("{{ form|crispy }}", RadioGroupsForm, NOTHING, id="radio groups"),
    pytest.param(
        "{{ form|crispy }}", lambda: RadioGroupsForm({}), NOTHING, id="invalid radios"
    ),
    pytest.param(
        "{{ form|crispy }}", CheckboxGroupsForm, NOTHING, id="checkbox groups"
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: CheckboxGroupsForm({}),
        NOTHING,
        id="invalid checkbox groups",
    ),
    pytest.param("{{ form|crispy }}", FilesForm, NOTHING, id="files"),
    pytest.param(
        "{{ form|crispy }}", lambda: FilesForm({}), NOTHING, id="invalid files"
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: UncoveredWidgetsForm({}),
        NOTHING,
        id="uncovered widgets",
    ),
    pytest.param(
        ERRORS_ONLY, lambda: FormWideErrorsForm({}), NOTHING, id="errors on their own"
    ),
    pytest.param(
        "{{ form.text|as_crispy_field }}",
        lambda: TextInputsForm({}),
        NOTHING,
        id="one field",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(FieldAndFormWideErrorsForm({})),
        NOTHING,
        id="tag",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: supplying_classes(DeveloperAttrsForm({})),
        {DEVELOPER_CLASS} | HELPER_CLASSES,
        id="tag with the helper's classes",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(FormWideErrorsForm({}), form_error_title="Mind this"),
        NOTHING,
        id="tag with a title",
    ),
    pytest.param(
        "{% crispy form %}", structured, NOTHING, id="structural layout objects"
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: structured({}),
        NOTHING,
        id="structural layout objects, invalid",
    ),
    pytest.param("{% crispy form %}", everything, NOTHING, id="all thirteen objects"),
    pytest.param(
        "{% crispy form %}",
        lambda: everything({}),
        NOTHING,
        id="all thirteen objects, invalid",
    ),
    pytest.param("{% crispy form %}", tabbed, MINE, id="tabs"),
    pytest.param("{% crispy form %}", lambda: tabbed({}), MINE, id="tabs, invalid"),
    pytest.param("{% crispy form %}", accordioned, MINE, id="accordion"),
    pytest.param(
        "{% crispy form %}", lambda: accordioned({}), MINE, id="accordion, invalid"
    ),
    pytest.param("{% crispy form %}", modalled, MINE, id="modal"),
    pytest.param("{% crispy form %}", lambda: modalled({}), MINE, id="modal, invalid"),
    pytest.param("{% crispy form %}", alerted, MINE, id="alert"),
    pytest.param("{% crispy form %}", lambda: alerted({}), MINE, id="alert, invalid"),
    pytest.param("{% crispy form %}", attached, NOTHING, id="attached text"),
    pytest.param(
        "{% crispy form %}",
        lambda: attached({}),
        NOTHING,
        id="attached text, invalid",
    ),
    pytest.param("{% crispy form %}", with_buttons, NOTHING, id="field with buttons"),
    pytest.param(
        "{% crispy form %}",
        lambda: with_buttons({}),
        NOTHING,
        id="field with buttons, invalid",
    ),
    pytest.param("{% crispy form %}", uneditable, MINE, id="uneditable fields"),
    pytest.param(
        "{% crispy form %}",
        lambda: uneditable({}),
        MINE,
        id="uneditable fields, invalid",
    ),
    pytest.param("{% crispy form %}", inlined_fields, MINE, id="inline fields"),
    pytest.param(
        "{% crispy form %}",
        lambda: inlined_fields({}),
        MINE,
        id="inline fields, invalid",
    ),
    pytest.param("{% crispy form %}", multi_widget, MINE, id="multi-widget fields"),
    pytest.param(
        "{% crispy form %}",
        lambda: multi_widget({}),
        MINE,
        id="multi-widget fields, invalid",
    ),
    pytest.param(
        "{{ form|crispy }}", MultiWidgetsForm, NOTHING, id="split date and time"
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: MultiWidgetsForm({}),
        NOTHING,
        id="split date and time, invalid",
    ),
    pytest.param("{% crispy form %}", buttoned, NOTHING, id="buttons in a layout"),
    pytest.param(
        "{% crispy form %}",
        lambda: buttoned({}),
        NOTHING,
        id="buttons in a layout, invalid",
    ),
    pytest.param("{% crispy form %}", inlined_radios, NOTHING, id="inline radios"),
    pytest.param(
        "{% crispy form %}",
        lambda: inlined_radios({}),
        NOTHING,
        id="inline radios, invalid",
    ),
    pytest.param(
        "{% crispy form %}", inlined_checkboxes, NOTHING, id="inline checkboxes"
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: inlined_checkboxes({}),
        NOTHING,
        id="inline checkboxes, invalid",
    ),
    pytest.param(
        "{% crispy form %}", helper_buttons, NOTHING, id="buttons added to the helper"
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(TextInputsForm({}), form_show_labels=False),
        NOTHING,
        id="tag without labels",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(FieldAndFormWideErrorsForm({}), form_show_errors=False),
        NOTHING,
        id="tag without errors",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: stating(EveryInputForm(), EVERY_CHOICE),
        NOTHING,
        id="every choice stated, through the filter",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: stating(EveryInputForm({}), EVERY_CHOICE),
        NOTHING,
        id="every choice stated, invalid, through the tag",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: stating(
            ButtonedForm(
                buttons=(
                    Submit("save", "Save"),
                    Reset("clear", "Clear"),
                    Button("help", "Help"),
                    StrictButton("More"),
                )
            ),
            EVERY_BUTTON_CHOICE,
        ),
        NOTHING,
        id="buttons with every choice stated",
    ),
    pytest.param("{% crispy form %}", LineFormSet, NOTHING, id="stacked formset"),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(LineFormSet(), template="daisyui/table_inline_formset.html"),
        NOTHING,
        id="table formset",
    ),
    pytest.param(
        "{% crispy form %}",
        failing_lines,
        NOTHING,
        id="stacked formset with all three kinds of error",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: helped(failing_lines(), template="daisyui/table_inline_formset.html"),
        NOTHING,
        id="table formset with all three kinds of error",
    ),
    pytest.param(
        "{{ form|as_crispy_errors }}",
        failing_lines,
        NOTHING,
        id="formset-wide errors on their own",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: DrawnBooleansForm(choices=TOGGLE_AND_SWITCH),
        NOTHING,
        id="a toggle and a switch, through the filter",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: DrawnBooleansForm({}, choices=TOGGLE_AND_SWITCH),
        NOTHING,
        id="a toggle and a switch, bound, through the tag",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: RequiredDrawnBooleanForm({}, choices=TOGGLE_AND_SWITCH_IN_ERROR),
        NOTHING,
        id="a toggle and a switch in error, through the filter",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: RequiredDrawnBooleanForm({}, choices=TOGGLE_AND_SWITCH_IN_ERROR),
        NOTHING,
        id="a toggle and a switch in error, through the tag",
    ),
    pytest.param(
        "{{ form|crispy }}",
        lambda: DrawnBooleansForm(choices=TOGGLE_AND_SWITCH_SIZED),
        NOTHING,
        id="a toggle and a switch with a size and a colour, through the filter",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: RequiredDrawnBooleanForm({}, choices=TOGGLE_AND_SWITCH_SIZED_IN_ERROR),
        NOTHING,
        id="a toggle and a switch with a size and a colour in error, through the tag",
    ),
    pytest.param(
        "{{ form|crispy }}", MediaForm, NOTHING, id="media, through the filter"
    ),
    pytest.param("{% crispy form %}", MediaForm, NOTHING, id="media, through the tag"),
    pytest.param(
        "{{ form|crispy }}",
        lambda: FloatingForm(choices=FLOATING_LABELS),
        NOTHING,
        id="floating labels, through the filter",
    ),
    pytest.param(
        "{% crispy form %}",
        lambda: FloatingForm({}, choices=FLOATING_LABELS),
        NOTHING,
        id="floating labels, invalid, through the tag",
    ),
]


class TestEmittedClasses:
    @pytest.mark.parametrize(("source", "build", "supplied"), STATES)
    def test_every_class_the_pack_wrote_is_one_daisyui_defines(
        self, draw, daisyui_classes, source, build, supplied
    ):
        soup = draw(source, form=build())

        written = classes_in(soup) - supplied

        assert written
        assert written <= daisyui_classes | LAYOUT_UTILITIES, written - daisyui_classes

    def test_the_classes_the_forms_supplied_are_drawn(self, draw):
        soup = draw("{% crispy form %}", form=supplying_classes(DeveloperAttrsForm({})))

        assert {DEVELOPER_CLASS} | HELPER_CLASSES <= classes_in(soup)


class TestModifierTables:
    @pytest.mark.parametrize("kind", ["size", "color", "variant"])
    def test_every_class_in_the_table_is_one_daisyui_defines(
        self, daisyui_classes, kind
    ):
        written = {
            name
            for modifiers in Modifiers.tables[kind].values()
            for name in modifiers.values()
        }

        assert written
        assert written <= daisyui_classes, written - daisyui_classes

    def test_every_class_a_label_means_is_one_daisyui_defines(self, daisyui_classes):
        written = set(Modifiers.labels.values())

        assert written
        assert written <= daisyui_classes, written - daisyui_classes


class TestWithoutDjangoMvp:
    def test_the_fixture_leaves_only_the_pack_and_crispy_installed(
        self, without_django_mvp
    ):
        assert {config.name for config in apps.get_app_configs()} == {
            "crispy_forms",
            "mvp_forms",
        }

    @pytest.mark.parametrize("source", ["{{ form|crispy }}", "{% crispy form %}"])
    def test_a_form_is_drawn_with_its_fields_and_its_alert(
        self, draw, without_django_mvp, source
    ):
        soup = draw(source, form=helped(FieldAndFormWideErrorsForm({})))

        assert soup.find(id="id_helped") is not None
        assert soup.find(attrs={"role": "alert"}) is not None

    def test_the_form_wide_errors_are_drawn_on_their_own(
        self, draw, without_django_mvp
    ):
        soup = draw(ERRORS_ONLY, form=FormWideErrorsForm({}))

        assert soup.find(attrs={"role": "alert"}) is not None


class TestDistributedFiles:
    def test_the_package_has_templates_to_check(self):
        assert TEMPLATES

    @pytest.mark.parametrize("path", TEMPLATES, ids=lambda path: path.name)
    def test_no_template_uses_cotton(self, path):
        source = path.read_text()

        loaded = {
            name
            for libraries in re.findall(r"{%\s*load\s+([^%]+?)\s*%}", source)
            for name in libraries.split()
        }

        assert not re.search(r"<c-", source)
        assert not loaded & FORBIDDEN_LIBRARIES

    def test_every_template_named_by_a_template_is_the_packs_own(self):
        named = [
            path
            for template in TEMPLATES
            for path in re.findall(
                r"{%\s*(?:extends|include)\s+[\"']([^\"']+)[\"']", template.read_text()
            )
        ]

        assert named
        assert all(path.startswith("daisyui/") for path in named)

    @pytest.mark.parametrize(
        "path", sorted(PACKAGE.rglob("*.py")), ids=lambda path: path.name
    )
    def test_no_module_imports_django_mvp_or_cotton(self, path):
        assert not imported_modules(path) & FORBIDDEN_MODULES

    def test_the_package_has_no_static_directory(self):
        assert not [path for path in PACKAGE.rglob("static") if path.is_dir()]
