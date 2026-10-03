"""One field with buttons joined to it, drawn by FieldWithButtons."""

import pytest
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.layout import Button, Field, Submit

from mvp_forms.choices import Choice, FormChoices
from tests.forms import DecoratedFieldsForm

BUTTONS = [
    pytest.param(lambda **kw: StrictButton("Go", css_id="act", **kw), id="strict"),
    pytest.param(lambda **kw: Submit("act", "Go", css_id="act", **kw), id="submit"),
    pytest.param(lambda **kw: Button("act", "Go", css_id="act", **kw), id="button"),
]


def draw_form(draw, *layout, bound=False, choices=None, **context):
    form = DecoratedFieldsForm({} if bound else None, layout=layout)
    if choices is not None:
        form.helper.daisyui = choices
    return draw("{% crispy form %}", form=form, **context)


def frame_of(soup, name="amount"):
    return soup.find(id=f"div_id_{name}")


def join_of(soup, name="amount"):
    return frame_of(soup, name).find(class_="join")


def parts_of(join):
    return join.find_all(True, recursive=False)


class TestFieldWithButtonsDrawn:
    @pytest.mark.parametrize("make", BUTTONS)
    def test_one_join_holds_the_input_first_and_then_the_button(self, draw, make):
        soup = draw_form(draw, FieldWithButtons("amount", make()))

        frame = frame_of(soup)
        parts = parts_of(join_of(soup))

        assert len(frame.find_all(class_="join")) == 1
        assert [part.get("id") for part in parts] == ["id_amount", "act"]
        assert "join-item" in parts[0]["class"]

    def test_every_button_follows_the_input_in_the_order_given(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons(
                "amount",
                StrictButton("One", css_id="one"),
                Submit("two", "Two", css_id="two"),
                Button("three", "Three", css_id="three"),
            ),
        )

        parts = parts_of(join_of(soup))

        assert [part.get("id") for part in parts] == [
            "id_amount",
            "one",
            "two",
            "three",
        ]

    def test_the_frame_holds_one_label_one_help_text_and_no_error_when_valid(
        self, draw
    ):
        soup = draw_form(draw, FieldWithButtons("amount", StrictButton("Go")))

        frame = frame_of(soup)

        assert len(frame.find_all("label", attrs={"for": "id_amount"})) == 1
        assert len(frame.find_all(id="id_amount_helptext")) == 1
        assert frame.find(id="id_amount_error") is None

    def test_a_field_as_the_first_item_passes_its_class_and_attributes_on(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons(
                Field("amount", css_class="mine", data_role="money"), StrictButton("Go")
            ),
        )

        field = soup.find(id="id_amount")

        assert "mine" in field["class"]
        assert "join-item" in field["class"]
        assert field["data-role"] == "money"
        assert field.parent is join_of(soup)

    def test_a_button_takes_a_class_of_the_developers_for_the_doubled_border(
        self, draw
    ):
        soup = draw_form(
            draw,
            FieldWithButtons(
                "amount", StrictButton("Go", css_id="act", css_class="join-item")
            ),
        )

        assert "join-item" in soup.find(id="act")["class"]


class TestFieldWithButtonsFailing:
    def test_the_input_has_the_error_modifier_and_is_invalid_and_described(self, draw):
        soup = draw_form(
            draw, FieldWithButtons("amount", StrictButton("Go")), bound=True
        )

        frame = frame_of(soup)
        field = frame.find(id="id_amount")

        assert "input-error" in field["class"]
        assert field["aria-invalid"] == "true"
        assert len(frame.find_all(id="id_amount_error")) == 1
        assert "id_amount_error" in field["aria-describedby"].split()

    def test_the_join_does_not_carry_the_error_modifier(self, draw):
        soup = draw_form(
            draw, FieldWithButtons("amount", StrictButton("Go")), bound=True
        )

        assert "input-error" not in join_of(soup)["class"]

    def test_a_valid_bound_field_has_no_error_modifier_and_no_error_element(self, draw):
        form = DecoratedFieldsForm(
            {"amount": "5"}, layout=[FieldWithButtons("amount", StrictButton("Go"))]
        )

        frame = frame_of(draw("{% crispy form %}", form=form))

        assert "input-error" not in frame.find(id="id_amount")["class"]
        assert frame.find(id="id_amount_error") is None


class TestFieldWithButtonsKeepsTheButtons:
    def test_a_submit_in_the_group_keeps_its_name_and_value(self, draw):
        outside = draw_form(draw, "amount", Submit("go", "Go now", css_id="act"))
        inside = draw_form(
            draw, FieldWithButtons("amount", Submit("go", "Go now", css_id="act"))
        )

        assert inside.find(id="act")["name"] == outside.find(id="act")["name"] == "go"
        assert (
            inside.find(id="act")["value"]
            == outside.find(id="act")["value"]
            == "Go now"
        )

    def test_a_button_whose_content_holds_a_template_tag_is_drawn_once_unevaluated(
        self, draw
    ):
        soup = draw_form(
            draw,
            FieldWithButtons("amount", StrictButton("{{ payload }}", css_id="act")),
            payload="{{ 7|add:1 }}",
        )

        buttons = soup.find_all(id="act")

        assert len(buttons) == 1
        assert buttons[0].get_text() == "{{ 7|add:1 }}"

    def test_a_button_is_drawn_once_even_when_the_field_fails(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons("amount", StrictButton("Go", css_id="act")),
            bound=True,
        )

        assert len(soup.find_all(id="act")) == 1


class TestFieldWithButtonsNothingToJoin:
    def test_with_no_buttons_the_group_holds_the_input_alone(self, draw):
        soup = draw_form(draw, FieldWithButtons("amount"))

        parts = parts_of(join_of(soup))

        assert [part.get("id") for part in parts] == ["id_amount"]


class TestFieldWithButtonsOptions:
    def test_a_css_id_a_css_class_and_an_attribute_are_on_the_join(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons(
                "amount",
                StrictButton("Go"),
                css_id="search-join",
                css_class="mine",
                data_role="search",
            ),
        )

        join = join_of(soup)

        assert join["id"] == "search-join"
        assert "mine" in join["class"]
        assert join["data-role"] == "search"
        assert "mine" not in soup.find(id="id_amount")["class"]

    def test_a_class_written_for_another_pack_is_dropped_from_the_join(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons(
                "amount", StrictButton("Go"), css_class="mine ctrlHolder active"
            ),
        )

        join = join_of(soup)

        assert "mine" in join["class"]
        assert "ctrlHolder" not in join["class"]
        assert "active" not in join["class"]

    def test_input_size_raises_nothing_and_draws_no_class(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons("amount", StrictButton("Go"), input_size="input-group-sm"),
        )

        written = {name for tag in soup.find_all(class_=True) for name in tag["class"]}

        assert join_of(soup) is not None
        assert "input-group-sm" not in written

    def test_a_template_of_the_developers_draws_the_field(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons(
                "amount", StrictButton("Go"), template="tests/own_container.html"
            ),
        )

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None

    def test_a_group_without_the_layout_object_has_no_join(self, draw):
        soup = draw_form(draw, "amount")

        assert soup.find(class_="join") is None
        assert "join-item" not in soup.find(id="id_amount")["class"]


class TestFieldWithButtonsOnOtherWidgets:
    def test_a_select_is_joined_to_the_buttons(self, draw):
        soup = draw_form(
            draw, FieldWithButtons("country", StrictButton("Go", css_id="act"))
        )

        parts = parts_of(join_of(soup, "country"))

        assert [part.get("id") for part in parts] == ["id_country", "act"]
        assert parts[0].name == "select"
        assert "join-item" in parts[0]["class"]

    def test_a_checkbox_and_its_buttons_are_both_drawn(self, draw):
        soup = draw_form(
            draw, FieldWithButtons("agree", StrictButton("Go", css_id="act"))
        )

        frame = frame_of(soup, "agree")

        assert len(frame.find_all("input", id="id_agree")) == 1
        assert len(frame.find_all(id="act")) == 1

    def test_a_radio_group_and_its_buttons_are_both_drawn_and_no_option_is_joined(
        self, draw
    ):
        soup = draw_form(
            draw, FieldWithButtons("pick", StrictButton("Go", css_id="act"))
        )

        frame = frame_of(soup, "pick")
        options = frame.find_all("input", attrs={"name": "pick"})

        assert len(options) > 1
        assert len(frame.find_all(id="act")) == 1
        assert all("join-item" not in option.get("class", []) for option in options)

    def test_a_hidden_field_is_a_hidden_input_alone(self, draw):
        soup = draw_form(
            draw, FieldWithButtons("token", StrictButton("Go", css_id="act"))
        )

        assert soup.find(id="id_token")["type"] == "hidden"
        assert frame_of(soup, "token") is None
        assert soup.find(class_="join") is None
        assert soup.find(id="act") is None


class TestFieldWithButtonsSize:
    @staticmethod
    def buttons():
        return [
            StrictButton("One", css_id="one"),
            Submit("two", "Two", css_id="two"),
            Button("three", "Three", css_id="three"),
        ]

    def test_the_form_s_size_is_on_the_joined_input_and_every_button(self, draw):
        soup = draw_form(
            draw,
            FieldWithButtons("amount", *self.buttons()),
            choices=FormChoices(size="lg"),
        )

        parts = parts_of(join_of(soup))

        assert "input-lg" in parts[0]["class"]
        assert all("btn-lg" in part["class"] for part in parts[1:])

    def test_a_choice_around_the_layout_object_sets_the_size_of_both(self, draw):
        soup = draw_form(
            draw, Choice(FieldWithButtons("amount", *self.buttons()), size="sm")
        )

        parts = parts_of(join_of(soup))

        assert "input-sm" in parts[0]["class"]
        assert all("btn-sm" in part["class"] for part in parts[1:])

    def test_a_choice_around_the_layout_object_wins_over_the_form(self, draw):
        soup = draw_form(
            draw,
            Choice(FieldWithButtons("amount", *self.buttons()), size="sm"),
            choices=FormChoices(size="lg"),
        )

        parts = parts_of(join_of(soup))

        assert "input-sm" in parts[0]["class"]
        assert "input-lg" not in parts[0]["class"]
        assert all("btn-sm" in part["class"] for part in parts[1:])
