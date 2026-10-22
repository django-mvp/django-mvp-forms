"""Tests for the layout objects of ``mvp_forms.layout``: what they hold and draw."""

import pytest
from crispy_forms.bootstrap import InlineField, PrependedText, StrictButton
from crispy_forms.layout import (
    HTML,
    Button,
    Div,
    Field,
    Hidden,
    MultiWidgetField,
    Reset,
    Submit,
)
from django.utils.safestring import mark_safe

from mvp_forms.choices import INHERIT, Choice
from mvp_forms.layout import (
    Fieldset,
    FormText,
    GroupButton,
    GroupText,
    InvalidMember,
    Join,
    Member,
)
from tests.forms import StructureForm, StructureHiddenForm

LEGEND = "Account"
DESCRIPTION = "Only the account holder can change these."


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
            Hidden("go", "Go"),
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


class TestJoinContents:
    @pytest.mark.parametrize(
        "button",
        [StrictButton("Go"), Submit("go", "Go"), Button("go", "Go"), Reset("go", "Go")],
        ids=lambda button: type(button).__name__,
    )
    def test_a_button_is_held_in_its_place_and_not_a_member(self, button):
        group = Join("first", button, "second")

        contents = group.contents()

        assert [type(held) for held in contents] == [Member, GroupButton, Member]
        assert contents[1].button is button
        assert contents[1].choice is None
        assert names_of(group) == ["first", "second"]

    def test_a_button_in_a_choice_carries_the_merged_choice(self):
        button = StrictButton("Go")
        group = Join(Choice("first", Choice(button, color="error"), size="sm"))

        member, held = group.contents()

        assert member.choice.size == "sm"
        assert (held.choice.size, held.choice.color) == ("sm", "error")

    def test_text_is_held_in_its_place_and_not_a_member(self):
        text = HTML("±")
        group = Join("first", text, "second")

        contents = group.contents()

        assert [type(held) for held in contents] == [Member, GroupText, Member]
        assert contents[1].text is text
        assert contents[1].choice is None
        assert names_of(group) == ["first", "second"]

    def test_text_in_a_choice_carries_the_merged_choice(self):
        group = Join(Choice("first", Choice(HTML("±"), variant="ghost"), size="sm"))

        member, held = group.contents()

        assert (held.choice.size, held.choice.variant) == ("sm", "ghost")

    def test_a_group_of_fields_holds_its_members_alone(self):
        group = Join("first", Field("second", css_class="x"))

        assert group.contents() == group.members()


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


def drawn_form_text(draw, form_text, **context):
    form = StructureForm(layout=(form_text,))
    return draw("{% crispy form %}", form=form, **context).find("div")


def toggle_of(fieldset):
    return fieldset.find("input", type="checkbox", class_="peer")


def drawn_fieldset(draw, *layout, bound=False, prefix=None):
    form = StructureForm({} if bound else None, layout=layout, prefix=prefix)
    return draw("{% crispy form %}", form=form).find("fieldset")


class TestFieldsetOptions:
    def test_open_on_a_fieldset_that_is_not_collapsible_raises(self):
        with pytest.raises(ValueError, match="collapsible"):
            Fieldset(LEGEND, "first", open=True)

    def test_a_collapsible_fieldset_with_no_legend_raises(self):
        with pytest.raises(ValueError, match="legend"):
            Fieldset("", "first", collapsible=True)

    def test_the_options_are_not_written_as_attributes(self, draw):
        fieldset = drawn_fieldset(
            draw,
            Fieldset(
                LEGEND,
                "first",
                collapsible=True,
                open=True,
                description=DESCRIPTION,
            ),
        )

        assert not {"collapsible", "open", "description"} & set(fieldset.attrs)


class TestFieldsetDescription:
    def test_it_is_drawn_before_the_first_field(self, draw):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", "second", description=DESCRIPTION)
        )

        drawn = fieldset.find_all(id=["account-description", "id_first"])
        assert [tag["id"] for tag in drawn] == [
            "account-description",
            "id_first",
        ]

    def test_it_describes_the_fieldset(self, draw):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", description=DESCRIPTION)
        )

        described_by = fieldset["aria-describedby"]
        assert fieldset.find(id=described_by).get_text(strip=True) == DESCRIPTION

    def test_it_describes_a_collapsible_fieldset_too(self, draw):
        fieldset = drawn_fieldset(
            draw,
            Fieldset(LEGEND, "first", collapsible=True, description=DESCRIPTION),
        )

        described_by = fieldset["aria-describedby"]
        assert fieldset.find(id=described_by).get_text(strip=True) == DESCRIPTION

    def test_markup_in_it_is_escaped(self, draw):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", description="<b>Bold</b>")
        )

        assert fieldset.find("b") is None
        assert "<b>Bold</b>" in fieldset.get_text()

    def test_it_is_drawn_as_form_text_with_no_size(self, draw):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", description=DESCRIPTION)
        )
        form_text = drawn_form_text(draw, FormText(DESCRIPTION))

        description = fieldset.find(id="account-description")
        assert description.name == form_text.name
        assert description["class"] == form_text["class"]

    def test_with_none_nothing_describes_the_fieldset(self, draw):
        fieldset = drawn_fieldset(draw, Fieldset(LEGEND, "first"))

        assert not fieldset.has_attr("aria-describedby")


class TestCollapsibleFieldset:
    def test_a_plain_fieldset_has_no_toggle(self, draw):
        fieldset = drawn_fieldset(draw, Fieldset(LEGEND, "first"))

        assert toggle_of(fieldset) is None

    def test_its_legend_holds_the_label_of_its_toggle(self, draw):
        fieldset = drawn_fieldset(draw, Fieldset(LEGEND, "first", collapsible=True))

        label = fieldset.find("legend").find("label")
        assert label["for"] == toggle_of(fieldset)["id"]
        assert label.get_text(strip=True) == LEGEND

    def test_the_toggle_comes_before_the_legend_and_the_fields(self, draw):
        fieldset = drawn_fieldset(draw, Fieldset(LEGEND, "first", collapsible=True))

        toggle = toggle_of(fieldset)
        assert toggle.find_next_sibling("legend") is not None
        assert toggle.find_next_sibling("div").find("input", id="id_first")

    @pytest.mark.parametrize("open_", [True, False])
    def test_open_says_whether_it_is_drawn_open(self, draw, open_):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", collapsible=True, open=open_)
        )

        assert toggle_of(fieldset).has_attr("checked") is open_

    def test_it_is_drawn_closed_unless_told_otherwise(self, draw):
        fieldset = drawn_fieldset(draw, Fieldset(LEGEND, "first", collapsible=True))

        assert not toggle_of(fieldset).has_attr("checked")

    def test_one_holding_a_field_in_error_is_drawn_open(self, draw):
        fieldset = drawn_fieldset(
            draw,
            Fieldset(LEGEND, "first", collapsible=True),
            bound=True,
        )

        toggle = toggle_of(fieldset)
        assert toggle.has_attr("checked")
        assert fieldset.find(id=toggle["aria-describedby"]) is not None

    def test_one_holding_a_hidden_field_in_error_is_drawn_open(self, draw):
        form = StructureHiddenForm(
            {"first": "a"},
            layout=[Fieldset(LEGEND, "first", "token", collapsible=True)],
        )

        fieldset = draw("{% crispy form %}", form=form).find("fieldset")

        assert toggle_of(fieldset).has_attr("checked")

    def test_one_holding_a_nested_field_in_error_is_drawn_open(self, draw):
        fieldset = drawn_fieldset(
            draw,
            Fieldset(LEGEND, Div("first"), collapsible=True),
            bound=True,
        )

        assert toggle_of(fieldset).has_attr("checked")

    def test_one_holding_no_field_in_error_keeps_its_state(self, draw):
        form = StructureForm(
            {"first": "a"},
            layout=[
                Fieldset(LEGEND, "first", collapsible=True),
                "second",
            ],
        )

        fieldset = draw("{% crispy form %}", form=form).find("fieldset")

        toggle = toggle_of(fieldset)
        assert not toggle.has_attr("checked")
        assert not toggle.has_attr("aria-describedby")

    def test_its_toggle_id_starts_with_its_css_id(self, draw):
        fieldset = drawn_fieldset(
            draw, Fieldset(LEGEND, "first", collapsible=True, css_id="group")
        )

        assert toggle_of(fieldset)["id"] == "group-toggle"

    def test_the_toggle_ids_of_two_forms_in_a_formset_differ(self, draw):
        ids = [
            toggle_of(
                drawn_fieldset(
                    draw, Fieldset(LEGEND, "first", collapsible=True), prefix=prefix
                )
            )["id"]
            for prefix in ["form-0", "form-1"]
        ]

        assert ids[0] != ids[1]


class TestFormText:
    def test_it_is_drawn_at_its_place_in_the_layout(self, draw_layout):
        soup = draw_layout("first", FormText("Between"), "second")

        text = soup.find(string="Between")
        assert text.find_previous("input")["name"] == "first"
        assert text.find_next("input")["name"] == "second"

    def test_it_is_drawn_inside_a_fieldset(self, draw_layout):
        soup = draw_layout(Fieldset(LEGEND, "first", FormText("Inside"), "second"))

        assert soup.find(string="Inside").find_parent("fieldset") is not None

    def test_markup_in_the_text_is_drawn(self, draw):
        form_text = drawn_form_text(draw, FormText("<b>Bold</b> and plain"))

        assert form_text.find("b").get_text() == "Bold"

    def test_a_context_value_in_it_is_filled_in_and_escaped(self, draw_layout):
        soup = draw_layout(FormText("Written for {{ who }}"), who="<i>Ann</i>")

        assert soup.find("i") is None
        assert soup.find(string="Written for <i>Ann</i>") is not None

    @pytest.mark.parametrize(
        ("size", "drawn"),
        [("small", "text-xs"), (None, "text-sm"), ("large", "text-base")],
    )
    def test_each_size_draws_its_text_size(self, draw, size, drawn):
        form_text = drawn_form_text(draw, FormText("Sized", size=size))

        sizes = {"text-xs", "text-sm", "text-base"}
        assert sizes & set(form_text["class"]) == {drawn}

    @pytest.mark.parametrize(
        ("variant", "drawn"),
        [(None, "text-base-content"), ("muted", "text-base-content/90")],
    )
    def test_each_variant_draws_its_text_colour(self, draw, variant, drawn):
        form_text = drawn_form_text(draw, FormText("Shaded", variant=variant))

        colours = {"text-base-content", "text-base-content/90"}
        assert colours & set(form_text["class"]) == {drawn}

    def test_an_unknown_size_raises(self):
        with pytest.raises(ValueError, match="size"):
            FormText("Sized", size="md")

    def test_an_unknown_variant_raises(self):
        with pytest.raises(ValueError, match="variant"):
            FormText("Shaded", variant="soft")

    def test_a_template_of_your_own_draws_it(self, draw_layout):
        soup = draw_layout(FormText("Mine", template="tests/own_form_text.html"))

        assert soup.find(id="mine").get_text() == "Mine"

    def test_its_id_classes_and_attributes_are_kept(self, draw):
        form_text = drawn_form_text(
            draw,
            FormText("Kept", css_id="note", css_class="mine", data_role="note"),
        )

        assert form_text["id"] == "note"
        assert form_text["class"][-1] == "mine"
        assert form_text["data-role"] == "note"
