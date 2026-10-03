"""The examples in django-crispy-forms' own docstrings, drawn as written."""

import pytest
from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.layout import (
    HTML,
    Button,
    ButtonHolder,
    Column,
    Div,
    Field,
    Fieldset,
    Hidden,
    Reset,
    Row,
    Submit,
)

from tests.forms import DocumentedExamplesForm

BOTH = ["form_field_1", "form_field_2"]
NESTED = ["form_field", "form_field_2"]
CUSTOM_BUTTON = {
    "css_id": "custom-id",
    "css_class": "custom class",
    "my_attr": True,
    "data": "my-data",
}

EXAMPLES = {
    "Fieldset": (
        lambda: Fieldset(
            "Text for the legend",
            "form_field_1",
            "form_field_2",
            css_id="my-fieldset-id",
            css_class="my-fieldset-class",
            data="my-data",
        ),
        BOTH,
    ),
    "Fieldset with a context-aware legend": (
        lambda: Fieldset(
            "Data for {{ user.username }}", "form_field_1", "form_field_2"
        ),
        BOTH,
    ),
    "Div": (
        lambda: Div(
            "form_field_1", "form_field_2", css_id="div-example", css_class="divs"
        ),
        BOTH,
    ),
    "Div, nested": (
        lambda: Div(
            Div(Field("form_field", css_class="field-class"), css_class="div-class"),
            Div("form_field_2", css_class="div-class"),
        ),
        NESTED,
    ),
    "Row": (lambda: Row("form_field_1", "form_field_2", css_id="row-example"), BOTH),
    "Row, nested": (
        lambda: Row(
            Div(Field("form_field", css_class="field-class"), css_class="div-class"),
            Div("form_field_2", css_class="div-class"),
        ),
        NESTED,
    ),
    "Column": (
        lambda: Column("form_field_1", "form_field_2", css_id="col-example"),
        BOTH,
    ),
    "Column, nested": (
        lambda: Div(
            Column(Field("form_field", css_class="field-class"), css_class="col-sm"),
            Column("form_field_2", css_class="col-sm"),
        ),
        NESTED,
    ),
    "HTML": (lambda: HTML("{% if saved %}Data saved{% endif %}"), []),
    "HTML, a hidden input": (
        lambda: HTML(
            '<input type="hidden" name="{{ step_field }}" value="{{ step0 }}" />'
        ),
        [],
    ),
    "Submit": (lambda: Submit("Search the Site", "search this site"), []),
    "Submit, with attributes": (
        lambda: Submit("Search the Site", "search this site", **CUSTOM_BUTTON),
        [],
    ),
    "Reset": (lambda: Reset("Reset This Form", "Revert Me!"), []),
    "Reset, with attributes": (
        lambda: Reset("Reset This Form", "Revert Me!", **CUSTOM_BUTTON),
        [],
    ),
    "Button": (lambda: Button("Button 1", "Press Me!"), []),
    "Button, with attributes": (
        lambda: Button("Button 1", "Press Me!", **CUSTOM_BUTTON),
        [],
    ),
    "Hidden": (lambda: Hidden("hidden", "hide-me"), []),
    "ButtonHolder": (
        lambda: ButtonHolder(
            HTML('<span style="display: hidden;">Information Saved</span>'),
            Submit("Save", "Save"),
        ),
        [],
    ),
    "FormActions": (
        lambda: FormActions(
            HTML('<span style="display: hidden;">Information Saved</span>'),
            Submit("Save", "Save", css_class="btn-primary"),
        ),
        [],
    ),
    "StrictButton": (lambda: StrictButton("button content", css_class="extra"), []),
    "StrictButton with a context-aware content": (
        lambda: StrictButton("Button for {{ user.username }}"),
        [],
    ),
}


class TestDocumentedExamples:
    @pytest.mark.parametrize("bound", [False, True], ids=["unbound", "invalid"])
    @pytest.mark.parametrize(("build", "named"), EXAMPLES.values(), ids=EXAMPLES)
    def test_it_draws_and_holds_each_field_it_names_once(
        self, draw, build, named, bound
    ):
        form = DocumentedExamplesForm({} if bound else None, layout=[build()])

        soup = draw("{% crispy form %}", form=form)

        for name in named:
            assert len(soup.find_all(id=f"id_{name}")) == 1
