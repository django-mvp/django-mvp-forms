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
    MultiWidgetField,
    Reset,
    Row,
    Submit,
)

from tests.conftest import PACK_TEMPLATES
from tests.forms import DocumentedExamplesForm, HelpedForm
from tests.template_surface import TemplateSurface

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
    "MultiWidgetField": (
        lambda: MultiWidgetField(
            "form_field_split",
            attrs=({"style": "width: 30px;"}, {"class": "second_widget_class"}),
        ),
        ["form_field_split_0", "form_field_split_1"],
        ("input", {"style": "width: 30px;"}),
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


class TestReadmeMultiWidgetField:
    def test_the_example_puts_each_attribute_on_its_own_part(self, draw):
        form = readme_example("A multi-widget field")["EventForm"]()

        soup = draw("{% crispy form %}", form=form)

        date = soup.find(attrs={"name": "starts_0"})
        time = soup.find(attrs={"name": "starts_1"})
        assert date["placeholder"] == "2026-10-03"
        assert not time.has_attr("placeholder")
        assert "mine" in time["class"]
        assert "input" in date["class"]
        assert date["aria-label"] != time["aria-label"]


class TestReadmeDrawings:
    def test_the_example_stating_a_drawing_draws_each_field_as_stated(self, draw):
        form = readme_example("Checkbox, toggle and switch")["SettingsForm"]()

        soup = draw("{% crispy form %}", form=form)

        remember = soup.find(id="id_remember")
        assert "checkbox" in remember["class"]
        assert not remember.has_attr("role")
        notify = soup.find(id="id_notify")
        assert "toggle" in notify["class"]
        assert not notify.has_attr("role")
        publish = soup.find(id="id_publish")
        assert "toggle" in publish["class"]
        assert publish["role"] == "switch"

    def test_the_drawing_stated_by_name_reaches_the_filter_too(self, draw):
        form = readme_example("Checkbox, toggle and switch")["SettingsForm"]()

        soup = draw("{{ form|crispy }}", form=form)

        assert "toggle" in soup.find(id="id_notify")["class"]


class TestReadmeFloatingLabels:
    @pytest.mark.parametrize("source", ["{{ form|crispy }}", "{% crispy form %}"])
    def test_the_example_floats_the_fields_it_states_and_no_other(self, draw, source):
        form = readme_example("Floating labels")["SignInForm"]()

        soup = draw(source, form=form)

        for name in ("email", "password", "country"):
            field = soup.find(id=f"id_{name}")
            label = field.find_parent("label", class_="floating-label")
            assert label["for"] == f"id_{name}"
        notes = soup.find("label", attrs={"for": "id_notes"})
        assert "floating-label" not in notes.get("class", [])
        assert (
            soup.find(id="id_remember").find_parent("label", class_="floating-label")
            is None
        )


class TestReadmeDrawingSizeAndColour:
    def test_the_example_gives_the_toggle_and_the_switch_the_size_and_colour(
        self, draw
    ):
        form = readme_example("Checkbox, toggle and switch")["SettingsForm"]()

        soup = draw("{% crispy form %}", form=form)

        assert "checkbox-sm" in set(soup.find(id="id_remember")["class"])
        assert "toggle-sm" in set(soup.find(id="id_notify")["class"])
        publish = set(soup.find(id="id_publish")["class"])
        assert {"toggle-sm", "toggle-primary"} <= publish


def readme_template(heading):
    section = README.read_text().split(f"#### {heading}\n", 1)[1]
    return re.search(r"```django\n(.*?)```", section, re.DOTALL).group(1)


REPLACEMENT_HEADING = "A required marker of your own"


class TestReadmeReplacement:
    def test_the_example_marks_a_required_field_and_not_an_optional_one(
        self, replace, draw
    ):
        source = readme_template(REPLACEMENT_HEADING)

        with replace({"daisyui/required_marker.html": source}):
            soup = draw("{% crispy form %}", form=HelpedForm())

        required = soup.find("label", attrs={"for": "id_bare"})
        optional = soup.find("label", attrs={"for": "id_optional"})
        assert required.find("abbr") is not None
        assert optional.find("abbr") is None

    def test_the_marker_the_pack_draws_is_not_drawn(self, replace, draw):
        source = readme_template(REPLACEMENT_HEADING)

        with replace({"daisyui/required_marker.html": source}):
            soup = draw("{% crispy form %}", form=HelpedForm())

        assert soup.find(attrs={"aria-hidden": "true"}) is None

    def test_the_example_reads_only_what_the_list_hands_its_template(self):
        surface = TemplateSurface(README.read_text(), PACK_TEMPLATES)
        handed = {row["path"]: row["handed"] for row in surface.listed()}[
            "daisyui/required_marker.html"
        ]

        read = surface.names_read(readme_template(REPLACEMENT_HEADING))

        assert read <= handed
