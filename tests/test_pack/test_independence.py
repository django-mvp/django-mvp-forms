"""What the pack depends on and what it writes: daisyUI only, nothing of django-mvp."""

import ast
import re
from pathlib import Path

import pytest
from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    FormActions,
    StrictButton,
    Tab,
    TabHolder,
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
    Reset,
    Row,
    Submit,
)
from django.apps import apps

import mvp_forms
from tests.forms import (
    ButtonedForm,
    CheckboxForm,
    CheckboxGroupsForm,
    DateSelectsForm,
    DeveloperAttrsForm,
    FieldAndFormWideErrorsForm,
    FilesForm,
    FormWideErrorsForm,
    HelpedForm,
    RadioGroupsForm,
    SelectsForm,
    StructureForm,
    TextInputsForm,
    UncoveredWidgetsForm,
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
}


def helped(form, **settings):
    form.helper = FormHelper()
    for name, value in settings.items():
        setattr(form.helper, name, value)
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


def helper_buttons():
    return ButtonedForm(
        buttons=(
            Submit("save", "Save"),
            Reset("clear", "Clear"),
            Button("help", "Help"),
        )
    )


NOTHING = frozenset()
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
    pytest.param("{% crispy form %}", buttoned, NOTHING, id="buttons in a layout"),
    pytest.param(
        "{% crispy form %}",
        lambda: buttoned({}),
        NOTHING,
        id="buttons in a layout, invalid",
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
