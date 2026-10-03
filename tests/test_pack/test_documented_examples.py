"""The examples in django-crispy-forms' own docstrings, drawn as written."""

import re
from pathlib import Path

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
        None,
    ),
    "Fieldset with a context-aware legend": (
        lambda: Fieldset(
            "Data for {{ user.username }}", "form_field_1", "form_field_2"
        ),
        BOTH,
        None,
    ),
    "Div": (
        lambda: Div(
            "form_field_1", "form_field_2", css_id="div-example", css_class="divs"
        ),
        BOTH,
        None,
    ),
    "Div, nested": (
        lambda: Div(
            Div(Field("form_field", css_class="field-class"), css_class="div-class"),
            Div("form_field_2", css_class="div-class"),
        ),
        NESTED,
        None,
    ),
    "Row": (
        lambda: Row("form_field_1", "form_field_2", css_id="row-example"),
        BOTH,
        ("div", {"id": "row-example"}),
    ),
    "Row, nested": (
        lambda: Row(
            Div(Field("form_field", css_class="field-class"), css_class="div-class"),
            Div("form_field_2", css_class="div-class"),
        ),
        NESTED,
        None,
    ),
    "Column": (
        lambda: Column("form_field_1", "form_field_2", css_id="col-example"),
        BOTH,
        None,
    ),
    "Column, nested": (
        lambda: Div(
            Column(Field("form_field", css_class="field-class"), css_class="col-sm"),
            Column("form_field_2", css_class="col-sm"),
        ),
        NESTED,
        None,
    ),
    "HTML, a hidden input": (
        lambda: HTML(
            '<input type="hidden" name="{{ step_field }}" value="{{ step0 }}" />'
        ),
        [],
        ("input", {"type": "hidden", "name": "step", "value": "first"}),
    ),
    "Submit": (
        lambda: Submit("Search the Site", "search this site"),
        [],
        ("input", {"name": "search-the-site", "type": "submit"}),
    ),
    "Submit, with attributes": (
        lambda: Submit("Search the Site", "search this site", **CUSTOM_BUTTON),
        [],
        ("input", {"id": "custom-id", "type": "submit", "data": "my-data"}),
    ),
    "Reset": (
        lambda: Reset("Reset This Form", "Revert Me!"),
        [],
        ("input", {"name": "reset-this-form", "type": "reset"}),
    ),
    "Reset, with attributes": (
        lambda: Reset("Reset This Form", "Revert Me!", **CUSTOM_BUTTON),
        [],
        ("input", {"id": "custom-id", "type": "reset", "data": "my-data"}),
    ),
    "Button": (
        lambda: Button("Button 1", "Press Me!"),
        [],
        ("input", {"name": "button-1", "type": "button"}),
    ),
    "Button, with attributes": (
        lambda: Button("Button 1", "Press Me!", **CUSTOM_BUTTON),
        [],
        ("input", {"id": "custom-id", "type": "button", "data": "my-data"}),
    ),
    "Hidden": (
        lambda: Hidden("hidden", "hide-me"),
        [],
        ("input", {"name": "hidden", "type": "hidden", "value": "hide-me"}),
    ),
    "ButtonHolder": (
        lambda: ButtonHolder(
            HTML('<span style="display: hidden;">Information Saved</span>'),
            Submit("Save", "Save"),
        ),
        [],
        ("input", {"name": "Save", "type": "submit"}),
    ),
    "FormActions": (
        lambda: FormActions(
            HTML('<span style="display: hidden;">Information Saved</span>'),
            Submit("Save", "Save", css_class="btn-primary"),
        ),
        [],
        ("input", {"name": "Save", "type": "submit"}),
    ),
    "StrictButton": (
        lambda: StrictButton("button content", css_class="extra"),
        [],
        ("button", {"type": "button"}),
    ),
    "StrictButton with a context-aware content": (
        lambda: StrictButton("Button for {{ user.username }}"),
        [],
        ("button", {"type": "button"}),
    ),
}


CONTEXT = {"step_field": "step", "step0": "first"}
SAVED_TEXT = "Data saved"
SAVED_EXAMPLE = "{% if saved %}" + SAVED_TEXT + "{% endif %}"


class TestDocumentedExamples:
    @pytest.mark.parametrize("bound", [False, True], ids=["unbound", "invalid"])
    @pytest.mark.parametrize(
        ("build", "named", "drawn"), EXAMPLES.values(), ids=EXAMPLES
    )
    def test_it_draws_what_it_names_once(self, draw, build, named, drawn, bound):
        form = DocumentedExamplesForm({} if bound else None, layout=[build()])

        soup = draw("{% crispy form %}", form=form, **CONTEXT)

        for name in named:
            assert len(soup.find_all(id=f"id_{name}")) == 1
        if drawn:
            element, attrs = drawn
            assert len(soup.find_all(element, attrs=attrs)) == 1

    @pytest.mark.parametrize("saved", [True, False])
    def test_the_html_example_draws_its_text_only_when_its_condition_holds(
        self, draw, saved
    ):
        form = DocumentedExamplesForm(layout=[HTML(SAVED_EXAMPLE)])

        soup = draw("{% crispy form %}", form=form, saved=saved)

        assert (SAVED_TEXT in soup.get_text()) == saved


README = Path(__file__).parents[2] / "README.md"


def readme_example(heading):
    section = README.read_text().split(f"### {heading}\n", 1)[1]
    code = re.search(r"```python\n(.*?)```", section, re.DOTALL).group(1)
    namespace = {}
    exec(code, namespace)  # noqa: S102
    return namespace


class TestReadmeFormWideChoices:
    @pytest.mark.parametrize("source", ["{{ form|crispy }}", "{% crispy form %}"])
    def test_the_form_stating_its_choices_is_drawn_with_them(self, draw, source):
        form = readme_example("Size, colour and variant")["SettingsForm"]()

        soup = draw(source, form=form)

        assert {"input-sm", "input-primary", "input-ghost"} <= set(
            soup.find(id="id_name")["class"]
        )
        notes = set(soup.find(id="id_notes")["class"])
        assert {"textarea-sm", "textarea-ghost"} <= notes
        assert "textarea-primary" not in notes
        newsletter = set(soup.find(id="id_newsletter")["class"])
        assert {"checkbox-sm", "checkbox-primary"} <= newsletter
        assert "checkbox-ghost" not in newsletter


class TestReadmeFieldChoices:
    def test_the_example_stating_a_choice_in_a_layout_draws(self, draw):
        form = readme_example("One field's own choice")["SearchForm"]()

        soup = draw("{% crispy form %}", form=form)

        search = set(soup.find(id="id_search")["class"])
        assert {"input-lg", "input-primary"} <= search
        assert "input-sm" not in search
        for name in ("name", "city"):
            tag = set(soup.find(id=f"id_{name}")["class"])
            assert "input-sm" in tag
            assert "input-primary" not in tag
        notes = set(soup.find(id="id_notes")["class"])
        assert {"textarea-sm", "textarea-primary"} <= notes
