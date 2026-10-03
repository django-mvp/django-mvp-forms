"""A field with no visible label, drawn by InlineField."""

import pytest
from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Field

from tests.forms import InlineFieldsForm


def draw_form(draw, *layout, bound=False, data=None):
    form = InlineFieldsForm({} if bound else data, layout=layout)
    return draw("{% crispy form %}", form=form)


def frame_of(soup, name="name"):
    return soup.find(id=f"div_id_{name}")


class TestInlineFieldDrawn:
    def test_the_frame_holds_no_label_element(self, draw):
        soup = draw_form(draw, InlineField("name"))

        assert frame_of(soup).find("label") is None
        assert soup.find("label", attrs={"for": "id_name"}) is None

    def test_the_input_is_named_by_an_aria_label_equal_to_the_label(self, draw):
        soup = draw_form(draw, InlineField("name"))

        assert soup.find(id="id_name")["aria-label"] == "Your name"

    def test_the_label_is_offered_as_the_placeholder(self, draw):
        soup = draw_form(draw, InlineField("name"))

        assert soup.find(id="id_name")["placeholder"] == "Your name"

    def test_a_widgets_own_placeholder_is_kept(self, draw):
        soup = draw_form(draw, InlineField("own"))

        assert soup.find(id="id_own")["placeholder"] == "Mine"
        assert soup.find(id="id_own")["aria-label"] == "Own"

    def test_a_widgets_own_aria_label_is_kept(self, draw):
        soup = draw_form(draw, InlineField("named"))

        assert soup.find(id="id_named")["aria-label"] == "Mine"
        assert soup.find(id="id_named")["placeholder"] == "Named"

    def test_a_textarea_gets_a_placeholder_too(self, draw):
        soup = draw_form(draw, InlineField("note"))

        assert soup.find(id="id_note")["placeholder"] == "Note"
        assert soup.find(id="id_note")["aria-label"] == "Note"

    def test_a_field_with_no_label_has_no_aria_label_and_no_placeholder(self, draw):
        soup = draw_form(draw, InlineField("unlabelled"))

        field = soup.find(id="id_unlabelled")

        assert not field.has_attr("aria-label")
        assert not field.has_attr("placeholder")

    def test_the_input_keeps_its_component_class(self, draw):
        soup = draw_form(draw, InlineField("name"))

        assert "input" in soup.find(id="id_name")["class"]


class TestInlineFieldLabelMarkedSafe:
    def test_it_reaches_the_placeholder_and_the_aria_label_as_text(self, draw):
        soup = draw_form(draw, InlineField("marked"))

        field = soup.find(id="id_marked")

        assert field["placeholder"] == "Marked & bold"
        assert field["aria-label"] == "Marked & bold"
        assert frame_of(soup, "marked").find("b") is None


class TestInlineFieldOnOtherWidgets:
    def test_a_single_checkbox_keeps_its_label_with_the_checkbox_inside(self, draw):
        soup = draw_form(draw, InlineField("agree"))

        frame = frame_of(soup, "agree")
        labels = frame.find_all("label")

        assert len(labels) == 1
        assert labels[0].find(id="id_agree") is not None
        assert not frame.find(id="id_agree").has_attr("aria-label")

    def test_a_select_gets_no_placeholder_and_is_named_by_aria_label(self, draw):
        soup = draw_form(draw, InlineField("country"))

        field = soup.find(id="id_country")

        assert frame_of(soup, "country").find("label") is None
        assert not field.has_attr("placeholder")
        assert field["aria-label"] == "Fruit"

    def test_a_radio_group_gets_no_placeholder_and_is_named_by_aria_label(self, draw):
        soup = draw_form(draw, InlineField("pick"))

        frame = frame_of(soup, "pick")
        options = frame.find_all("input", attrs={"type": "radio"})

        assert frame.name == "fieldset"
        assert frame["aria-label"] == "Pick"
        assert frame.find("legend") is None
        assert len(options) == 2
        assert not any(option.has_attr("placeholder") for option in options)

    def test_a_hidden_field_is_a_hidden_input_alone(self, draw):
        soup = draw_form(draw, InlineField("token"))

        assert soup.find(id="id_token")["type"] == "hidden"
        assert frame_of(soup, "token") is None


class TestInlineFieldFailing:
    def test_the_error_element_is_drawn_and_describes_the_input(self, draw):
        soup = draw_form(draw, InlineField("name"), bound=True)

        frame = frame_of(soup)
        field = frame.find(id="id_name")

        assert len(frame.find_all(id="id_name_error")) == 1
        assert "id_name_error" in field["aria-describedby"].split()

    def test_the_input_is_invalid_and_carries_its_error_modifier(self, draw):
        soup = draw_form(draw, InlineField("name"), bound=True)

        field = soup.find(id="id_name")

        assert field["aria-invalid"] == "true"
        assert "input-error" in field["class"]

    def test_there_is_still_no_label_when_the_field_fails(self, draw):
        soup = draw_form(draw, InlineField("name"), bound=True)

        assert frame_of(soup).find("label") is None

    def test_a_valid_bound_field_has_no_error_element(self, draw):
        soup = draw_form(draw, InlineField("name"), data={"name": "Ada"})

        assert frame_of(soup).find(id="id_name_error") is None
        assert not soup.find(id="id_name").has_attr("aria-invalid")


class TestInlineFieldHelpText:
    def test_the_help_text_is_drawn_and_describes_the_input(self, draw):
        soup = draw_form(draw, InlineField("name"))

        frame = frame_of(soup)

        assert len(frame.find_all(id="id_name_helptext")) == 1
        assert (
            "id_name_helptext" in frame.find(id="id_name")["aria-describedby"].split()
        )


class TestInlineFieldBesideOthers:
    def test_a_field_that_is_not_inline_keeps_its_label(self, draw):
        soup = draw_form(draw, InlineField("name"), "plain", Field("own"))

        assert frame_of(soup, "plain").find("label", attrs={"for": "id_plain"})
        assert frame_of(soup, "own").find("label", attrs={"for": "id_own"})
        assert frame_of(soup).find("label") is None
        assert not soup.find(id="id_plain").has_attr("aria-label")
        assert not soup.find(id="id_plain").has_attr("placeholder")

    def test_the_label_is_not_lost_for_the_next_field(self, draw):
        soup = draw_form(draw, InlineField("name"), "plain")

        assert frame_of(soup, "plain").find("label") is not None


class TestInlineFieldOptions:
    def test_a_css_class_and_an_attribute_reach_the_input(self, draw):
        soup = draw_form(draw, InlineField("name", css_class="mine", data_role="x"))

        field = soup.find(id="id_name")

        assert "mine" in field["class"]
        assert field["data-role"] == "x"

    def test_a_wrapper_class_reaches_the_frames_outer_element(self, draw):
        soup = draw_form(draw, InlineField("name", wrapper_class="mine"))

        assert "mine" in frame_of(soup)["class"]

    def test_a_template_of_the_developers_draws_the_field(self, draw):
        soup = draw_form(draw, InlineField("name", template="tests/own_container.html"))

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None


class TestInlineFieldKeepsTheData:
    def test_the_name_and_value_are_those_of_the_undecorated_field(self, draw):
        data = {"name": "Ada"}
        plain = draw_form(draw, Field("name"), data=data)

        soup = draw_form(draw, InlineField("name"), data=data)

        assert soup.find(id="id_name")["name"] == plain.find(id="id_name")["name"]
        assert soup.find(id="id_name")["value"] == plain.find(id="id_name")["value"]

    @pytest.mark.parametrize("name", ["name", "agree", "country", "pick"])
    def test_cleaned_data_is_the_same_with_and_without_the_layout_object(
        self, draw, name
    ):
        data = {
            "name": "Ada",
            "own": "o",
            "named": "n",
            "marked": "m",
            "note": "t",
            "country": "a",
            "agree": "on",
            "pick": "b",
            "plain": "p",
            "token": "k",
        }
        plain = InlineFieldsForm(data, layout=[Field(name)])
        decorated = InlineFieldsForm(data, layout=[InlineField(name)])
        draw("{% crispy form %}", form=plain)
        draw("{% crispy form %}", form=decorated)

        plain.is_valid()
        decorated.is_valid()

        assert decorated.cleaned_data == plain.cleaned_data
        assert decorated.cleaned_data[name]


class TestInlineFieldNeverWritesToTheForm:
    def test_the_widget_keeps_its_attributes(self, draw):
        form = InlineFieldsForm(layout=[InlineField("name")])
        before = dict(form.fields["name"].widget.attrs)

        draw("{% crispy form %}", form=form)

        assert form.fields["name"].widget.attrs == before
