"""The examples in django-crispy-forms' own docstrings, drawn as written."""

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
    "Tab": (
        lambda: Tab("tab_name", "form_field_1", "form_field_2", "form_field_3"),
        [*BOTH, "form_field_3"],
        ("input", {"type": "radio", "aria-label": "tab_name"}),
    ),
    "TabHolder": (
        lambda: TabHolder(Tab("form_field_1", "form_field_2"), Tab("form_field_3")),
        ["form_field_2"],
        ("div", {"class": "tabs"}),
    ),
    "AccordionGroup": (
        lambda: AccordionGroup("group name", "form_field_1", "form_field_2"),
        BOTH,
        ("details", {"class": "collapse"}),
    ),
    "Accordion": (
        lambda: Accordion(
            AccordionGroup("group name", "form_field_1", "form_field_2"),
            AccordionGroup("another group name", "form_field"),
        ),
        [*BOTH, "form_field"],
        ("details", {"open": True}),
    ),
    "Modal": (
        lambda: Modal(
            "form_field_1",
            Div("form_field_2"),
            css_id="modal-id-ex",
            css_class="modal-class-ex",
            title="This is my modal",
        ),
        BOTH,
        ("dialog", {"id": "modal-id-ex"}),
    ),
    "Alert": (
        lambda: Alert(
            content=(
                "<strong>Warning!</strong> Best check yo self, "
                "you're not looking too good."
            )
        ),
        [],
        ("div", {"role": "alert"}),
    ),
    "StrictButton with a context-aware content": (
        lambda: StrictButton("Button for {{ user.username }}"),
        [],
        ("button", {"type": "button"}),
    ),
    "PrependedAppendedText": (
        lambda: PrependedAppendedText("form_field", "$", ".00"),
        ["form_field"],
        ("label", {"class": "input"}),
    ),
    "AppendedText": (
        lambda: AppendedText("form_field", ".00"),
        ["form_field"],
        ("label", {"class": "input"}),
    ),
    "PrependedText": (
        lambda: PrependedText("form_field", "$"),
        ["form_field"],
        ("label", {"class": "input"}),
    ),
    "FieldWithButtons": (
        lambda: FieldWithButtons(
            Field("form_field", css_class="span4"),
            StrictButton("Go!", css_id="go-button"),
            input_size="input-group-sm",
        ),
        ["form_field"],
        ("div", {"class": "join"}),
    ),
    "UneditableField": (
        lambda: UneditableField("form_field", css_class="input-xlarge"),
        ["form_field"],
        ("input", {"disabled": True}),
    ),
    "InlineField": (
        lambda: InlineField("form_field"),
        ["form_field"],
        ("input", {"aria-label": "Form field"}),
    ),
    "InlineCheckboxes": (
        lambda: InlineCheckboxes("form_field"),
        ["form_field"],
        ("div", {"id": "div_id_form_field"}),
    ),
    "InlineRadios": (
        lambda: InlineRadios("form_field"),
        ["form_field"],
        ("div", {"id": "div_id_form_field"}),
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


class TestReadmeButtonChoices:
    def test_the_example_stating_choices_for_buttons_draws(self, draw):
        form = readme_example("Buttons")["ConfirmForm"]()

        soup = draw("{% crispy form %}", form=form)

        for name in ("save", "clear"):
            assert {"btn-sm", "btn-neutral", "btn-outline"} <= set(
                soup.find("input", attrs={"name": name})["class"]
            )
        delete = set(soup.find("button")["class"])
        assert {"btn-sm", "btn-error", "btn-outline"} <= delete
        assert "btn-neutral" not in delete
        assert "input-sm" in set(soup.find(id="id_name")["class"])


class TestReadmeInlineChoices:
    def test_the_example_drawing_choices_in_a_line_draws_both_groups(self, draw):
        form = readme_example("Choices in a line")["SurveyForm"]()

        soup = draw("{% crispy form %}", form=form)

        sizes = soup.find(id="div_id_size").find_all("input", type="radio")
        extras = soup.find(id="div_id_extras").find_all("input", type="checkbox")
        assert [option["value"] for option in sizes] == ["s", "m", "l"]
        assert [option["value"] for option in extras] == ["a", "b"]


class TestReadmeFieldWithButtons:
    def test_the_example_drawing_a_field_with_buttons_joins_them_to_the_input(
        self, draw
    ):
        form = readme_example("A field with buttons")["SearchForm"]()

        soup = draw("{% crispy form %}", form=form)

        parts = (
            soup.find(id="div_id_query")
            .find(class_="join")
            .find_all(True, recursive=False)
        )
        assert [part["name"] for part in parts] == [
            "query",
            "go",
            "clear",
        ]


class TestReadmeUneditableField:
    def test_the_example_draws_the_uneditable_fields_disabled_and_the_other_editable(
        self, draw
    ):
        form = readme_example("An uneditable field")["ProfileForm"]()

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id="id_account")["value"] == "AC-1001"
        assert soup.find(id="id_account").has_attr("disabled")
        assert soup.find(id="id_reference").has_attr("disabled")
        assert not soup.find(id="id_nickname").has_attr("disabled")


class TestReadmeInlineField:
    def test_the_example_draws_the_inline_fields_without_labels_and_the_other_with(
        self, draw
    ):
        form = readme_example("An inline field")["SearchForm"]()

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id="div_id_query").find("label") is None
        assert soup.find(id="id_query")["aria-label"] == "Search"
        assert soup.find(id="id_query")["placeholder"] == "Search"
        assert soup.find("label", attrs={"for": "id_remember"}) is not None
        assert soup.find(id="id_note").has_attr("placeholder") is False
        assert soup.find("label", attrs={"for": "id_note"}) is not None
