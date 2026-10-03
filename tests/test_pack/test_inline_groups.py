"""Choices in a line, drawn by InlineRadios and InlineCheckboxes."""

from typing import NamedTuple

import pytest
from crispy_forms.bootstrap import InlineCheckboxes, InlineRadios
from crispy_forms.layout import Field

from mvp_forms.templatetags.daisyui import FieldInput
from tests.forms import InlineCheckboxesForm, InlineRadiosForm

INLINE = "daisyui/widgets/inline_group.html"
STACKED = "daisyui/widgets/group.html"
NAMES = ["choice", "grouped", "empty", "marked", "marked_groups", "locked", "text"]


class Kind(NamedTuple):
    form: type
    layout_object: type
    input_type: str
    held: dict
    invalid: dict
    initial: dict


KINDS = [
    pytest.param(
        Kind(
            InlineRadiosForm,
            InlineRadios,
            "radio",
            {"choice": "b"},
            {"choice": "nowhere"},
            {"choice": "a"},
        ),
        id="radios",
    ),
    pytest.param(
        Kind(
            InlineCheckboxesForm,
            InlineCheckboxes,
            "checkbox",
            {"choice": ["a", "b"]},
            {"choice": ["nowhere"]},
            {"choice": ["a"]},
        ),
        id="checkboxes",
    ),
]


def checked_values(kind):
    return ["b"] if kind.input_type == "radio" else ["a", "b"]


def inline_layout(kind, *names, **options):
    return [kind.layout_object(name, **options) for name in names or NAMES]


def draw_inline(draw, kind, data=None, *names, initial=None, **options):
    form = kind.form(
        data, initial=initial, layout=inline_layout(kind, *names, **options)
    )
    return draw("{% crispy form %}", form=form)


def frame_of(soup, name="choice"):
    return soup.find(id=f"div_id_{name}")


def inputs_in(soup, name="choice"):
    return frame_of(soup, name).find_all("input")


@pytest.fixture
def field_inputs(monkeypatch):
    built = []
    original = FieldInput.__init__

    def record(self, *args, **kwargs):
        original(self, *args, **kwargs)
        built.append(self)

    monkeypatch.setattr(FieldInput, "__init__", record)
    return built


def templates_of(field_inputs, name):
    return [item.template_name for item in field_inputs if item.field.name == name]


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesDrawn:
    def test_every_choice_is_an_input_of_the_type_sharing_one_name(self, draw, kind):
        soup = draw_inline(draw, kind)

        options = inputs_in(soup)

        assert [option["value"] for option in options] == ["a", "b"]
        assert {option["type"] for option in options} == {kind.input_type}
        assert {option["name"] for option in options} == {"choice"}
        assert all(kind.input_type in option["class"] for option in options)

    def test_every_choice_has_a_label_of_its_own_tied_to_it(self, draw, kind):
        soup = draw_inline(draw, kind)

        options = inputs_in(soup)

        assert len({option["id"] for option in options}) == 2
        for option in options:
            labels = soup.find_all("label", attrs={"for": option["id"]})
            assert len(labels) == 1
            assert option.find_parent("label") is labels[0]
            assert labels[0].text.strip()

    def test_the_group_is_drawn_by_the_inline_template(self, draw, kind, field_inputs):
        draw_inline(draw, kind)

        assert templates_of(field_inputs, "choice") == [INLINE]

    def test_the_same_field_without_the_layout_object_is_drawn_by_the_stacked_one(
        self, draw, kind, field_inputs
    ):
        form = kind.form(layout=[Field("choice")])

        draw("{% crispy form %}", form=form)

        assert templates_of(field_inputs, "choice") == [STACKED]

    def test_a_choice_is_never_widened(self, draw, kind):
        soup = draw_inline(draw, kind)

        assert not any("w-full" in option["class"] for option in inputs_in(soup))


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesFrame:
    def test_the_frame_is_a_fieldset_with_one_legend(self, draw, kind):
        soup = draw_inline(draw, kind)

        frame = frame_of(soup)

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend", recursive=False)) == 1

    def test_a_required_field_has_the_required_marker_and_an_optional_one_has_none(
        self, draw, kind
    ):
        soup = draw_inline(draw, kind)

        required = frame_of(soup).find("legend")
        optional = frame_of(soup, "grouped").find("legend")

        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    def test_the_help_text_is_drawn_once_and_describes_the_fieldset(self, draw, kind):
        soup = draw_inline(draw, kind)

        frame = frame_of(soup)

        assert len(frame.find_all(id="id_choice_helptext")) == 1
        assert frame["aria-describedby"].split() == ["id_choice_helptext"]

    def test_an_invalid_group_has_one_error_element_describing_the_fieldset(
        self, draw, kind
    ):
        soup = draw_inline(draw, kind, kind.invalid)

        frame = frame_of(soup)
        described = frame["aria-describedby"].split()

        assert len(frame.find_all(id="id_choice_error")) == 1
        assert described == ["id_choice_helptext", "id_choice_error"]
        assert all(soup.find(id=name) is not None for name in described)
        options = inputs_in(soup)
        assert all(option["aria-invalid"] == "true" for option in options)
        assert all(f"{kind.input_type}-error" in o["class"] for o in options)

    def test_a_valid_group_carries_no_error_modifier_and_no_error_element(
        self, draw, kind
    ):
        soup = draw_inline(draw, kind, kind.held)

        options = inputs_in(soup)

        assert frame_of(soup).find(id="id_choice_error") is None
        assert not any(f"{kind.input_type}-error" in o["class"] for o in options)
        assert not any(option.has_attr("aria-invalid") for option in options)

    def test_no_id_is_repeated(self, draw, kind):
        soup = draw_inline(draw, kind, kind.invalid)

        ids = [element["id"] for element in soup.find_all(id=True)]

        assert len(ids) == len(set(ids))


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesKeepTheData:
    def test_exactly_the_held_options_are_checked(self, draw, kind):
        soup = draw_inline(draw, kind, kind.held)

        checked = [o["value"] for o in inputs_in(soup) if o.has_attr("checked")]

        assert checked == checked_values(kind)

    def test_the_initial_option_is_checked(self, draw, kind):
        soup = draw_inline(draw, kind, initial=kind.initial)

        checked = [o["value"] for o in inputs_in(soup) if o.has_attr("checked")]

        assert checked == ["a"]

    def test_nothing_is_checked_when_nothing_is_held(self, draw, kind):
        soup = draw_inline(draw, kind)

        assert not any(o.has_attr("checked") for o in inputs_in(soup))

    def test_cleaned_data_is_the_same_as_the_stacked_groups(self, draw, kind):
        data = {**kind.held, "text": "t"}
        stacked = kind.form(data, layout=[Field(name) for name in NAMES])
        inline = kind.form(data, layout=inline_layout(kind))
        draw("{% crispy form %}", form=stacked)
        draw("{% crispy form %}", form=inline)

        assert stacked.is_valid()
        assert inline.is_valid()

        assert inline.cleaned_data == stacked.cleaned_data
        assert inline.cleaned_data["choice"] == kind.held["choice"]


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesOptions:
    def test_an_option_a_widget_disables_is_drawn_disabled(self, draw, kind):
        soup = draw_inline(draw, kind)

        first, second = inputs_in(soup, "locked")

        assert second.has_attr("disabled")
        assert not first.has_attr("disabled")

    def test_a_disabled_field_draws_every_option_disabled(self, draw, kind):
        soup = draw_inline(draw, kind, None, "fixed")

        options = inputs_in(soup, "fixed")

        assert len(options) == 2
        assert all(option.has_attr("disabled") for option in options)

    def test_named_groups_each_sit_under_their_name(self, draw, kind):
        soup = draw_inline(draw, kind)

        frame = frame_of(soup, "grouped")
        named = {
            nested.find("legend").text.strip(): [
                option["value"] for option in nested.find_all("input")
            ]
            for nested in frame.find_all("fieldset")
        }

        assert named == {"Fruit": ["a", "b"], "Vegetable": ["c"]}
        assert [o["value"] for o in frame.find_all("input")] == ["a", "b", "c", "d"]

    def test_markup_in_an_option_label_and_a_group_name_is_escaped(self, draw, kind):
        soup = draw_inline(draw, kind)

        marked = frame_of(soup, "marked")
        groups = frame_of(soup, "marked_groups")

        assert marked.find("b") is None
        assert "<b>Bold</b>" in marked.text
        assert groups.find("i") is None
        assert groups.find("fieldset").find("legend").text.strip() == "<i>Group</i>"

    def test_a_widget_naming_its_own_template_is_drawn_by_it(
        self, draw, kind, field_inputs
    ):
        soup = draw_inline(draw, kind, None, "own", "choice")

        own = frame_of(soup, "own")

        assert templates_of(field_inputs, "own") == [None]
        assert own.find("label", class_="label") is None
        assert len(own.find_all("input")) == 2
        assert frame_of(soup).find("label", class_="label") is not None

    def test_a_widget_naming_its_own_option_template_is_drawn_by_it(
        self, draw, kind, field_inputs
    ):
        soup = draw_inline(draw, kind, None, "own_option")

        own = frame_of(soup, "own_option")

        assert templates_of(field_inputs, "own_option") == [None]
        assert own.find("label", class_="label") is None
        assert len(own.find_all("input")) == 2


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesNothingToLineUp:
    def test_a_field_with_no_choices_is_still_drawn_with_its_frame(self, draw, kind):
        soup = draw_inline(draw, kind, {})

        frame = frame_of(soup, "empty")

        assert frame.name == "fieldset"
        assert frame.find("legend") is not None
        assert inputs_in(soup, "empty") == []

    def test_a_text_field_is_drawn_as_the_undecorated_field_is(self, draw, kind):
        plain = draw("{% crispy form %}", form=kind.form({}, layout=[Field("text")]))

        soup = draw_inline(draw, kind, {}, "text")

        assert str(frame_of(soup, "text")) == str(frame_of(plain, "text"))
        assert soup.find(id="id_text")["type"] == "text"


@pytest.mark.parametrize("kind", KINDS)
class TestInlineChoicesLayoutOptions:
    def test_a_css_class_reaches_every_option(self, draw, kind):
        soup = draw_inline(draw, kind, None, "choice", css_class="mine")

        assert all("mine" in option["class"] for option in inputs_in(soup))

    def test_an_attribute_reaches_every_option(self, draw, kind):
        soup = draw_inline(draw, kind, None, "choice", data_role="pick")

        assert all(option["data-role"] == "pick" for option in inputs_in(soup))

    def test_a_wrapper_class_reaches_the_frames_outer_element(self, draw, kind):
        soup = draw_inline(draw, kind, None, "choice", wrapper_class="mine")

        assert "mine" in frame_of(soup)["class"]

    def test_a_template_of_the_developers_draws_the_field(self, draw, kind):
        soup = draw_inline(
            draw, kind, None, "choice", template="tests/own_container.html"
        )

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None

    def test_a_wrapper_class_does_not_carry_over_to_the_next_field(self, draw, kind):
        form = kind.form(
            layout=[
                kind.layout_object("choice", wrapper_class="mine"),
                kind.layout_object("grouped"),
            ]
        )

        soup = draw("{% crispy form %}", form=form)

        assert frame_of(soup, "grouped")["class"] == ["fieldset"]
