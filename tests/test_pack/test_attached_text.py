"""Text attached to an input by PrependedText, AppendedText, PrependedAppendedText."""

import pytest
from crispy_forms.bootstrap import AppendedText, PrependedAppendedText, PrependedText
from crispy_forms.layout import Field

from tests.forms import DecoratedFieldsForm, MarkedUpDecoratedForm

OBJECTS = [
    pytest.param(lambda **kw: PrependedText("amount", "$", **kw), id="prepended"),
    pytest.param(lambda **kw: AppendedText("amount", ".00", **kw), id="appended"),
    pytest.param(
        lambda **kw: PrependedAppendedText("amount", "$", ".00", **kw), id="both"
    ),
]


def draw_form(draw, *layout, bound=False, form=DecoratedFieldsForm, data=None):
    built = form({} if bound else data, layout=layout)
    return draw("{% crispy form %}", form=built)


def frame_of(soup, name="amount"):
    return soup.find(id=f"div_id_{name}")


def wrapper_of(frame, component="input"):
    return frame.find("label", class_=component)


def texts_of(wrapper):
    return [span.get_text() for span in wrapper.find_all("span", class_="label")]


class TestAttachedTextDrawn:
    def test_prepended_text_comes_before_the_input_inside_one_wrapper(self, draw):
        soup = draw_form(draw, PrependedText("amount", "$"))

        wrapper = wrapper_of(frame_of(soup))

        assert wrapper.find("input") is not None
        assert texts_of(wrapper) == ["$"]
        assert wrapper.find("span", class_="label").find_next_sibling("input")
        assert wrapper.find("input").find_next_sibling("span") is None

    def test_appended_text_comes_after_the_input(self, draw):
        soup = draw_form(draw, AppendedText("amount", ".00"))

        wrapper = wrapper_of(frame_of(soup))

        assert texts_of(wrapper) == [".00"]
        assert wrapper.find("input").find_next_sibling("span", class_="label")
        assert wrapper.find("input").find_previous_sibling("span") is None

    def test_both_texts_surround_the_input_in_one_wrapper(self, draw):
        soup = draw_form(draw, PrependedAppendedText("amount", "$", ".00"))

        frame = frame_of(soup)
        wrapper = wrapper_of(frame)

        assert len(frame.find_all("label", class_="input")) == 1
        assert texts_of(wrapper) == ["$", ".00"]
        field = wrapper.find("input")
        assert field.find_previous_sibling("span").get_text() == "$"
        assert field.find_next_sibling("span").get_text() == ".00"

    @pytest.mark.parametrize("build", OBJECTS)
    def test_the_input_inside_the_wrapper_carries_no_component_class(self, draw, build):
        soup = draw_form(draw, build())

        field = soup.find(id="id_amount")

        assert "input" not in field.get("class", [])

    def test_the_frame_holds_one_label_one_help_text_and_no_error_when_valid(
        self, draw
    ):
        soup = draw_form(draw, PrependedAppendedText("amount", "$", ".00"))

        frame = frame_of(soup)

        assert len(frame.find_all("label", attrs={"for": "id_amount"})) == 1
        assert len(frame.find_all(id="id_amount_helptext")) == 1
        assert frame.find(id="id_amount_error") is None

    @pytest.mark.parametrize("build", OBJECTS)
    def test_the_input_is_inside_the_wrapper_label_so_the_text_names_it(
        self, draw, build
    ):
        soup = draw_form(draw, build())

        assert soup.find(id="id_amount").find_parent("label", class_="input")


class TestAttachedTextNothingToAttach:
    @pytest.mark.parametrize("text", ["", None])
    def test_an_empty_or_missing_prepended_text_draws_no_span(self, draw, text):
        soup = draw_form(draw, PrependedAppendedText("amount", text, ".00"))

        assert texts_of(wrapper_of(frame_of(soup))) == [".00"]

    @pytest.mark.parametrize("text", ["", None])
    def test_an_empty_or_missing_appended_text_draws_no_span(self, draw, text):
        soup = draw_form(draw, PrependedAppendedText("amount", "$", text))

        assert texts_of(wrapper_of(frame_of(soup))) == ["$"]

    @pytest.mark.parametrize("text", ["", None])
    def test_with_neither_text_there_is_no_wrapper(self, draw, text):
        soup = draw_form(draw, PrependedAppendedText("amount", text, text))

        frame = frame_of(soup)

        assert wrapper_of(frame) is None
        assert "input" in frame.find(id="id_amount")["class"]

    @pytest.mark.parametrize("text", ["", None])
    def test_an_attached_text_that_is_empty_draws_the_field_as_undecorated(
        self, draw, text
    ):
        plain = draw_form(draw, Field("amount"))

        decorated = draw_form(draw, PrependedText("amount", text))

        assert str(frame_of(decorated)) == str(frame_of(plain))


class TestAttachedTextFailing:
    @pytest.mark.parametrize("build", OBJECTS)
    def test_the_wrapper_carries_the_error_modifier_and_the_input_is_invalid(
        self, draw, build
    ):
        soup = draw_form(draw, build(), bound=True)

        frame = frame_of(soup)
        field = frame.find(id="id_amount")

        assert "input-error" in wrapper_of(frame)["class"]
        assert "input-error" not in field.get("class", [])
        assert field["aria-invalid"] == "true"
        assert len(frame.find_all(id="id_amount_error")) == 1
        assert "id_amount_error" in field["aria-describedby"].split()

    def test_a_valid_bound_field_has_no_error_modifier_and_no_error_element(self, draw):
        soup = draw_form(
            draw,
            PrependedText("amount", "$"),
            form=DecoratedFieldsForm,
            data={"amount": "5"},
        )

        frame = frame_of(soup)

        assert "input-error" not in wrapper_of(frame)["class"]
        assert frame.find(id="id_amount_error") is None
        assert not frame.find(id="id_amount").has_attr("aria-invalid")


class TestAttachedTextOnASelect:
    def test_the_wrapper_carries_select_and_the_select_carries_no_class_of_its_own(
        self, draw
    ):
        soup = draw_form(draw, PrependedText("country", "#"))

        frame = frame_of(soup, "country")
        wrapper = wrapper_of(frame, "select")

        assert wrapper.find("select", id="id_country") is not None
        assert "select" not in wrapper.find("select").get("class", [])
        assert texts_of(wrapper) == ["#"]

    def test_a_failing_select_carries_the_select_error_modifier_on_the_wrapper(
        self, draw
    ):
        soup = draw_form(draw, AppendedText("country", "#"), bound=True)

        frame = frame_of(soup, "country")

        assert "select-error" in wrapper_of(frame, "select")["class"]
        assert frame.find(id="id_country_error") is not None


class TestAttachedTextKeepsTheData:
    def test_the_name_and_value_are_those_of_the_undecorated_field(self, draw):
        data = {"amount": "42"}
        plain = draw_form(draw, Field("amount"), data=data)

        soup = draw_form(draw, PrependedText("amount", "$"), data=data)

        assert soup.find(id="id_amount")["name"] == plain.find(id="id_amount")["name"]
        assert soup.find(id="id_amount")["value"] == plain.find(id="id_amount")["value"]

    @pytest.mark.parametrize("build", OBJECTS)
    def test_cleaned_data_is_the_same_with_and_without_the_layout_object(
        self, draw, build
    ):
        data = {
            "amount": "5",
            "country": "a",
            "agree": "on",
            "pick": "a",
            "born_year": "2000",
            "born_month": "1",
            "born_day": "2",
            "notes": "n",
            "token": "t",
        }
        plain = DecoratedFieldsForm(data, layout=[Field("amount")])
        decorated = DecoratedFieldsForm(data, layout=[build()])
        draw("{% crispy form %}", form=plain)
        draw("{% crispy form %}", form=decorated)

        plain.is_valid()
        decorated.is_valid()

        assert decorated.cleaned_data["amount"] == plain.cleaned_data["amount"] == "5"
        assert decorated.cleaned_data == plain.cleaned_data


class TestAttachedTextEscaping:
    def test_text_holding_markup_is_drawn_as_an_element(self, draw):
        soup = draw_form(
            draw, PrependedAppendedText("amount", "<b>US</b>", "<i>.00</i>")
        )

        wrapper = wrapper_of(frame_of(soup))

        assert wrapper.find("b") is not None
        assert wrapper.find("i") is not None

    def test_a_label_help_text_error_and_value_holding_markup_are_escaped(self, draw):
        form = MarkedUpDecoratedForm(
            {"amount": "<u>typed</u>"},
            layout=[PrependedText("amount", "$")],
        )

        soup = draw("{% crispy form %}", form=form)

        frame = frame_of(soup)
        assert frame.find("label", attrs={"for": "id_amount"}).find("b") is None
        assert frame.find(id="id_amount_helptext").find("i") is None
        assert frame.find(id="id_amount_error").find("script") is None
        assert frame.find("u") is None
        assert frame.find(id="id_amount")["value"] == "<u>typed</u>"


class TestAttachedTextOptions:
    def test_a_css_class_and_an_attribute_reach_the_input(self, draw):
        soup = draw_form(
            draw, PrependedText("amount", "$", css_class="mine", data_role="money")
        )

        field = soup.find(id="id_amount")

        assert "mine" in field["class"]
        assert field["data-role"] == "money"

    def test_a_wrapper_class_reaches_the_frames_outer_element(self, draw):
        soup = draw_form(draw, PrependedText("amount", "$", wrapper_class="mine"))

        assert "mine" in frame_of(soup)["class"]

    def test_a_template_of_the_developers_draws_the_field(self, draw):
        soup = draw_form(
            draw, PrependedText("amount", "$", template="tests/own_container.html")
        )

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None

    def test_input_size_and_active_raise_nothing_and_add_no_class(self, draw):
        soup = draw_form(
            draw, PrependedText("amount", "$", input_size="input-lg", active=True)
        )

        written = {name for tag in soup.find_all(class_=True) for name in tag["class"]}

        assert wrapper_of(frame_of(soup)) is not None
        assert "input-lg" not in written
        assert "active" not in written


class TestAttachedTextOnAWidgetItDoesNotSuit:
    @pytest.mark.parametrize("name", ["agree", "pick", "born", "notes", "upload"])
    def test_the_field_is_drawn_as_it_is_undecorated(self, draw, name):
        plain = draw_form(draw, Field(name), bound=True)

        decorated = draw_form(draw, PrependedAppendedText(name, "$", ".00"), bound=True)

        assert str(frame_of(decorated, name)) == str(frame_of(plain, name))
        assert "$" not in frame_of(decorated, name).get_text()

    @pytest.mark.parametrize("name", ["agree", "pick", "born", "notes", "upload"])
    def test_it_keeps_its_label_and_its_errors(self, draw, name):
        soup = draw_form(draw, PrependedText(name, "$"), bound=True)

        frame = frame_of(soup, name)

        assert frame.find(["label", "legend"]) is not None
        assert frame.find(id=f"id_{name}_error") is not None

    def test_a_hidden_field_is_a_hidden_input_alone(self, draw):
        soup = draw_form(draw, PrependedText("token", "$"), bound=True)

        hidden = soup.find(id="id_token")

        assert hidden["type"] == "hidden"
        assert frame_of(soup, "token") is None
        assert soup.find("label", attrs={"for": "id_token"}) is None
        assert "$" not in soup.get_text()


class TestWrapperClass:
    def test_a_plain_field_with_a_wrapper_class_has_it_on_a_div_frame(self, draw):
        soup = draw_form(draw, Field("amount", wrapper_class="mine"))

        frame = frame_of(soup)

        assert frame.name == "div"
        assert "mine" in frame["class"]

    def test_a_plain_field_with_a_wrapper_class_has_it_on_a_fieldset_frame(self, draw):
        soup = draw_form(draw, Field("pick", wrapper_class="mine"))

        frame = frame_of(soup, "pick")

        assert frame.name == "fieldset"
        assert "mine" in frame["class"]

    def test_a_field_with_none_has_no_class_but_the_frames_own(self, draw):
        soup = draw_form(draw, Field("amount"), Field("pick"))

        assert frame_of(soup)["class"] == ["fieldset"]
        assert frame_of(soup, "pick")["class"] == ["fieldset"]

    def test_a_wrapper_class_does_not_carry_over_to_the_next_field(self, draw):
        soup = draw_form(draw, Field("amount", wrapper_class="mine"), "other")

        assert frame_of(soup, "other")["class"] == ["fieldset"]
