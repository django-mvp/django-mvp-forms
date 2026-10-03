"""The layout objects that draw buttons: inputs, buttons, holders and helper buttons."""

import pytest
from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.layout import Button, ButtonHolder, Hidden, Reset, Submit

from tests.forms import ButtonedForm

DEVELOPER_CLASSES = ["mine", "other"]
DEVELOPER_ATTRS = {"data-role": "action", "title": "Act"}
BASE_INPUTS = [
    pytest.param(Submit, "submit", id="submit"),
    pytest.param(Reset, "reset", id="reset"),
    pytest.param(Button, "button", id="button"),
]


class TestBaseInputs:
    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_an_input_of_its_own_type_with_its_name_and_value(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go"))

        control = soup.find("input", attrs={"name": "act"})
        assert control["type"] == input_type
        assert control["value"] == "Go"

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_a_daisyui_button(self, draw_layout, kind, input_type):
        soup = draw_layout(kind("act", "Go"))

        assert "btn" in soup.find("input", attrs={"name": "act"})["class"]

    def test_a_reset_carries_no_class_written_for_another_pack(self, draw_layout):
        soup = draw_layout(Reset("act", "Clear"))

        assert "btn-inverse" not in soup.find("input", attrs={"name": "act"})["class"]

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(
            kind(
                "act",
                "Go",
                css_id="go",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        )

        control = soup.find("input", id="go")
        assert set(DEVELOPER_CLASSES) <= set(control["class"])
        assert "btn" in control["class"]
        assert control["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert control["title"] == DEVELOPER_ATTRS["title"]

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_drawn_disabled_when_given_disabled(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go", disabled=True))

        assert soup.find("input", attrs={"name": "act"}).has_attr("disabled")

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_not_disabled_unless_asked(self, draw_layout, kind, input_type):
        soup = draw_layout(kind("act", "Go"))

        assert not soup.find("input", attrs={"name": "act"}).has_attr("disabled")

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_a_value_reading_the_context_is_filled_in(
        self, draw_layout, kind, input_type
    ):
        soup = draw_layout(kind("act", "Go, {{ who }}"), who="Ada")

        assert soup.find("input", attrs={"name": "act"})["value"] == "Go, Ada"


class TestStrictButton:
    def test_it_is_a_button_element_holding_the_markup_it_was_given(self, draw_layout):
        soup = draw_layout(StrictButton("<em>Save</em> it", css_id="save"))

        button = soup.find("button", id="save")
        assert button.find("em").get_text() == "Save"

    def test_a_context_value_in_its_content_is_filled_in(self, draw_layout):
        soup = draw_layout(StrictButton("Save {{ who }}", css_id="save"), who="Ada")

        assert soup.find("button", id="save").get_text() == "Save Ada"

    def test_markup_in_a_context_value_is_escaped(self, draw_layout):
        soup = draw_layout(
            StrictButton("Save {{ who }}", css_id="save"), who="<script>x</script>"
        )

        button = soup.find("button", id="save")
        assert button.find("script") is None
        assert "<script>x</script>" in button.get_text()

    def test_its_type_is_button_unless_another_was_chosen(self, draw_layout):
        soup = draw_layout(
            StrictButton("Plain", css_id="plain"),
            StrictButton("Send", css_id="send", type="submit"),
        )

        assert soup.find("button", id="plain")["type"] == "button"
        assert soup.find("button", id="send")["type"] == "submit"

    def test_it_is_a_daisyui_button(self, draw_layout):
        soup = draw_layout(StrictButton("Save", css_id="save"))

        assert "btn" in soup.find("button", id="save")["class"]

    def test_it_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout
    ):
        soup = draw_layout(
            StrictButton(
                "Save",
                css_id="save",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        )

        button = soup.find("button", id="save")
        assert set(DEVELOPER_CLASSES) <= set(button["class"])
        assert "btn" in button["class"]
        assert button["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert button["title"] == DEVELOPER_ATTRS["title"]


HOLDERS = [
    pytest.param(ButtonHolder, id="button holder"),
    pytest.param(FormActions, id="form actions"),
]


class TestHolders:
    @pytest.mark.parametrize("holder", HOLDERS)
    def test_the_buttons_are_inside_one_container_in_the_order_given(
        self, draw_layout, holder
    ):
        soup = draw_layout(
            holder(
                Submit("save", "Save"),
                Reset("clear", "Clear"),
                Button("help", "Help"),
                StrictButton("More", css_id="more"),
                css_id="actions",
            )
        )

        container = soup.find(id="actions")
        controls = container.find_all(["input", "button"])
        assert [control.get("name") or control["id"] for control in controls] == [
            "save",
            "clear",
            "help",
            "more",
        ]

    @pytest.mark.parametrize("holder", HOLDERS)
    def test_it_carries_the_id_and_the_classes_it_was_given(self, draw_layout, holder):
        soup = draw_layout(
            holder(
                Submit("save", "Save"),
                css_id="actions",
                css_class=" ".join(DEVELOPER_CLASSES),
            )
        )

        assert soup.find(id="actions")["class"][-2:] == DEVELOPER_CLASSES

    @pytest.mark.parametrize("holder", HOLDERS)
    def test_it_writes_no_id_when_it_was_given_none(self, draw_layout, holder):
        soup = draw_layout(holder(Submit("save", "Save"), css_class="mine"))

        container = soup.find("input", attrs={"name": "save"}).parent
        assert not container.has_attr("id")

    @pytest.mark.parametrize("holder", HOLDERS)
    def test_an_empty_one_is_drawn(self, draw_layout, holder):
        soup = draw_layout(holder(css_id="actions"))

        container = soup.find(id="actions")
        assert container is not None
        assert container.find(["input", "button"]) is None

    def test_form_actions_carries_the_attributes_it_was_given(self, draw_layout):
        soup = draw_layout(
            FormActions(Submit("save", "Save"), css_id="actions", **DEVELOPER_ATTRS)
        )

        container = soup.find(id="actions")
        assert container["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert container["title"] == DEVELOPER_ATTRS["title"]


class TestHelperButtons:
    @pytest.fixture
    def draw_helper(self, draw):
        def draw_buttons(*buttons, **context):
            form = ButtonedForm(buttons=buttons)
            return draw("{% crispy form %}", form=form, **context)

        return draw_buttons

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_inside_the_form_element_after_the_fields(
        self, draw_helper, kind, input_type
    ):
        form = draw_helper(kind("act", "Go")).find("form")

        controls = form.find_all("input")
        assert controls[-1]["name"] == "act"
        assert [control["name"] for control in controls[-3:-1]] == ["first", "second"]

    @pytest.mark.parametrize(("kind", "input_type"), BASE_INPUTS)
    def test_it_is_the_element_a_layout_draws_for_the_same_button(
        self, draw_helper, draw_layout, kind, input_type
    ):
        button = kind("act", "Go", css_class="mine", **DEVELOPER_ATTRS)

        in_helper = draw_helper(button).find("input", attrs={"name": "act"})
        in_layout = draw_layout(button).find("input", attrs={"name": "act"})

        assert in_helper.attrs == in_layout.attrs
        assert in_helper["type"] == input_type

    def test_the_buttons_are_drawn_in_the_order_they_were_added(self, draw_helper):
        form = draw_helper(Submit("save", "Save"), Reset("clear", "Clear")).find("form")

        assert [control["name"] for control in form.find_all("input")[-2:]] == [
            "save",
            "clear",
        ]

    def test_markup_in_a_value_is_escaped(self, draw_helper):
        soup = draw_helper(Submit("save", '"><script>x</script>'))

        assert soup.find("script") is None
        value = soup.find("input", attrs={"name": "save"})["value"]
        assert value == '"><script>x</script>'

    def test_a_helper_with_no_buttons_draws_no_container(self, draw_helper):
        form = draw_helper().find("form")

        assert len(form.find_all("div", recursive=False)) == len(
            ButtonedForm.base_fields
        )

    def test_a_helper_with_buttons_draws_them_in_one_container(self, draw_helper):
        form = draw_helper(Submit("save", "Save"), Reset("clear", "Clear")).find("form")

        container = form.find("input", attrs={"name": "save"}).parent
        assert container.find("input", attrs={"name": "clear"}) is not None
        assert (
            len(form.find_all("div", recursive=False))
            == len(ButtonedForm.base_fields) + 1
        )

    def test_a_strict_button_is_the_button_a_layout_draws(
        self, draw_helper, draw_layout
    ):
        content = "<em>Go</em> {{ who }}"
        in_helper = draw_helper(
            StrictButton(content, css_id="go", css_class="mine"), who="Ada"
        ).find("button", id="go")
        in_layout = draw_layout(
            StrictButton(content, css_id="go", css_class="mine"), who="Ada"
        ).find("button", id="go")

        assert in_helper.find_parent("form") is not None
        assert in_helper.attrs == in_layout.attrs
        assert str(in_helper) == str(in_layout)

    def test_a_strict_button_shares_the_container_of_the_other_buttons(
        self, draw_helper
    ):
        form = draw_helper(
            Submit("save", "Save"), StrictButton("Go", css_id="go")
        ).find("form")

        assert (
            form.find("button", id="go").parent
            is form.find("input", attrs={"name": "save"}).parent
        )

    def test_a_helper_holding_only_a_hidden_input_draws_no_container(self, draw_helper):
        form = draw_helper(Hidden("step", "two")).find("form")

        assert form.find("input", attrs={"name": "step"}).parent is form
        assert len(form.find_all("div", recursive=False)) == len(
            ButtonedForm.base_fields
        )

    def test_a_hidden_input_is_drawn_outside_the_container_of_the_buttons(
        self, draw_helper
    ):
        form = draw_helper(Submit("save", "Save"), Hidden("step", "two")).find("form")

        assert form.find("input", attrs={"name": "step"}).parent is form
        assert form.find("input", attrs={"name": "save"}).parent is not form

    def test_a_layouts_buttons_are_drawn_with_the_form_element_off(self, draw_layout):
        soup = draw_layout(Submit("save", "Save"))

        assert soup.find("form") is None
        assert soup.find("input", attrs={"name": "save"}) is not None
