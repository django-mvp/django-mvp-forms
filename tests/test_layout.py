"""Tests for the ``Join`` layout object: what it holds and what it draws."""

import pytest
from crispy_forms.bootstrap import InlineField, PrependedText, StrictButton
from crispy_forms.layout import HTML, Div, Field, MultiWidgetField, Submit
from django.utils.safestring import mark_safe

from mvp_forms.choices import INHERIT, Choice
from mvp_forms.layout import InvalidMember, Join
from tests.forms import StructureForm, StructureHiddenForm


def names_of(group):
    return [member.name for member in group.members()]


def drawn_names(soup):
    return [
        tag["name"]
        for tag in soup.find_all(["input", "select"])
        if tag["name"] != "csrfmiddlewaretoken"
    ]


class TestJoinMembers:
    def test_names_are_members_in_the_order_given(self):
        group = Join("third", "first", "second")

        assert names_of(group) == ["third", "first", "second"]

    def test_a_group_holding_nothing_has_no_members(self):
        assert Join().members() == []

    def test_a_name_has_no_attributes_and_no_choice(self):
        (member,) = Join("first").members()

        assert member.attrs == {}
        assert member.choice is None

    def test_a_field_holding_one_name_gives_the_member_its_attributes(self):
        (member,) = Join(Field("first", css_class="x", autocomplete="tel")).members()

        assert member.name == "first"
        assert member.attrs == {"class": "x", "autocomplete": "tel"}

    def test_a_field_holding_several_names_gives_each_its_attributes(self):
        group = Join(Field("first", "second", data_role="phone"))

        assert [(member.name, member.attrs) for member in group.members()] == [
            ("first", {"data-role": "phone"}),
            ("second", {"data-role": "phone"}),
        ]

    @pytest.mark.parametrize(
        "field",
        [
            Field("first", wrapper_class="wide"),
            Field("first", template="tests/own_field.html"),
        ],
        ids=["wrapper_class", "template"],
    )
    def test_a_field_with_a_wrapper_class_or_a_template_raises(self, field):
        with pytest.raises(InvalidMember) as raised:
            Join(field).members()

        assert raised.value.member == "Field"

    def test_a_choice_gives_each_name_it_holds_its_choice(self):
        group = Join(Choice("first", "second", size="sm"))

        sizes = [member.choice.size for member in group.members()]

        assert names_of(group) == ["first", "second"]
        assert sizes == ["sm", "sm"]

    def test_a_choice_may_hold_a_field_and_the_field_keeps_its_attributes(self):
        group = Join(Choice("first", Field("second", css_class="x"), size="sm"))

        first, second = group.members()

        assert first.attrs == {}
        assert second.attrs == {"class": "x"}
        assert first.choice.size == second.choice.size == "sm"

    def test_a_choice_inside_a_choice_is_merged_over_the_outer_one(self):
        group = Join(
            Choice("first", Choice("second", size="lg"), size="sm", color="primary")
        )

        first, second = group.members()

        assert (first.choice.size, first.choice.color) == ("sm", "primary")
        assert (second.choice.size, second.choice.color) == ("lg", "primary")
        assert second.choice.variant is INHERIT

    def test_a_member_outside_the_choice_has_none(self):
        group = Join("first", Choice("second", size="sm"), "third")

        choices = [member.choice for member in group.members()]

        assert choices[0] is None
        assert choices[1].size == "sm"
        assert choices[2] is None

    def test_the_layouts_order_is_kept_through_fields_and_choices(self):
        group = Join(
            "third", Field("first", css_class="x"), Choice("second", size="sm")
        )

        assert names_of(group) == ["third", "first", "second"]

    @pytest.mark.parametrize(
        "held",
        [
            Div("first"),
            PrependedText("first", "$"),
            InlineField("first"),
            Submit("go", "Go"),
            StrictButton("Go"),
            HTML("<hr>"),
            MultiWidgetField("first", attrs={}),
            Join("first"),
        ],
        ids=lambda held: type(held).__name__,
    )
    def test_any_other_layout_object_raises_naming_its_class(self, held):
        with pytest.raises(InvalidMember) as caught:
            Join(held).members()

        assert caught.value.member == type(held).__name__

    def test_a_layout_object_inside_a_choice_raises_too(self):
        with pytest.raises(InvalidMember) as caught:
            Join(Choice("first", Div("second"))).members()

        assert caught.value.member == "Div"

    def test_the_error_is_a_value_error(self):
        assert issubclass(InvalidMember, ValueError)


class TestJoinRender:
    def test_a_group_holding_nothing_draws_nothing(self, draw):
        form = StructureForm(layout=["first", Join()])

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("fieldset") is None
        assert drawn_names(soup) == ["first"]

    def test_a_group_of_hidden_members_draws_their_inputs_and_no_fieldset(self, draw):
        form = StructureHiddenForm(layout=["first", Join("token")])

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("fieldset") is None
        assert drawn_names(soup) == ["first", "token"]
        assert soup.find(attrs={"name": "token"})["type"] == "hidden"

    def test_each_member_is_recorded_as_rendered(self, draw):
        form = StructureHiddenForm(layout=[Join("first", Field("second"), "token")])

        draw("{% crispy form %}", form=form)

        assert form.rendered_fields == {"first", "second", "token"}

    def test_a_name_the_form_lacks_draws_nothing_and_the_others_are_drawn(self, draw):
        form = StructureForm(layout=[Join("first", "nothing", "second")])

        soup = draw("{% crispy form %}", form=form)

        group = soup.find("div", class_="join")
        assert drawn_names(group) == ["first", "second"]
        assert form.rendered_fields >= {"first", "second"}

    def test_a_group_of_only_a_name_the_form_lacks_draws_no_fieldset(self, draw):
        form = StructureForm(layout=["first", Join("nothing")])

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("fieldset") is None
        assert drawn_names(soup) == ["first"]


class TestJoinLabelText:
    def test_a_plain_label_is_returned_as_written(self):
        assert Join(label="Tel & fax").label_text == "Tel & fax"

    def test_a_label_marked_safe_loses_its_tags_and_reads_its_entities(self):
        label = mark_safe("<b>Tel</b> &amp; fax")

        assert Join(label=label).label_text == "Tel & fax"

    def test_no_label_is_an_empty_string(self):
        assert Join().label_text == ""
