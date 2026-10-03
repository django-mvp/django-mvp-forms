"""The parts of a multi-widget field, drawn through MultiWidgetField or alone."""

import copy

from crispy_forms.layout import Field, MultiWidgetField

from mvp_forms.choices import Choice, FormChoices
from tests.forms import MultiWidgetsForm, RefusedMomentForm

DATA = {
    "moment_0": "2026-10-03",
    "moment_1": "12:30",
    "phone_0": "1",
    "phone_1": "2",
    "phone_2": "3",
    "name": "Ada",
}


def draw_form(draw, *layout, bound=False, form=MultiWidgetsForm, data=None):
    built = form({} if bound else data, layout=layout)
    return draw("{% crispy form %}", form=built)


def frame_of(soup, name="moment"):
    return soup.find(id=f"div_id_{name}")


def part_of(soup, name, index):
    return soup.find(attrs={"name": f"{name}_{index}"})


def classes_of(part):
    return part.get("class", [])


class TestMultiWidgetFieldAttributes:
    def test_a_sequence_of_sets_puts_each_on_its_own_part(self, draw):
        soup = draw_form(
            draw,
            MultiWidgetField("moment", attrs=({"data-first": "1"}, {"data-last": "2"})),
        )

        date, time = part_of(soup, "moment", 0), part_of(soup, "moment", 1)

        assert date["data-first"] == "1"
        assert not date.has_attr("data-last")
        assert time["data-last"] == "2"
        assert not time.has_attr("data-first")

    def test_a_single_set_goes_on_every_part(self, draw):
        soup = draw_form(draw, MultiWidgetField("phone", attrs={"data-all": "1"}))

        parts = [part_of(soup, "phone", index) for index in range(3)]

        assert [part["data-all"] for part in parts] == ["1", "1", "1"]

    def test_fewer_sets_than_parts_leaves_the_rest_without_them(self, draw):
        soup = draw_form(
            draw,
            MultiWidgetField("phone", attrs=({"data-one": "1"}, {"data-two": "2"})),
        )

        parts = [part_of(soup, "phone", index) for index in range(3)]

        assert parts[0]["data-one"] == "1"
        assert parts[1]["data-two"] == "2"
        assert not parts[2].has_attr("data-one")
        assert not parts[2].has_attr("data-two")

    def test_a_part_made_hidden_has_neither_a_class_nor_a_name(self, draw):
        soup = draw_form(
            draw, MultiWidgetField("phone", attrs=({}, {"type": "hidden"}, {}))
        )

        hidden = part_of(soup, "phone", 1)

        assert hidden["type"] == "hidden"
        assert not hidden.has_attr("class")
        assert not hidden.has_attr("aria-label")
        assert "input" in classes_of(part_of(soup, "phone", 0))


class TestMultiWidgetFieldClasses:
    def test_each_part_carries_the_input_class(self, draw):
        soup = draw_form(draw, MultiWidgetField("moment", attrs={}))

        assert "input" in classes_of(part_of(soup, "moment", 0))
        assert "input" in classes_of(part_of(soup, "moment", 1))

    def test_a_field_that_fails_has_the_error_modifier_on_each_part(self, draw):
        soup = draw_form(
            draw,
            MultiWidgetField("moment", attrs={}),
            bound=True,
            form=RefusedMomentForm,
        )

        assert "input-error" in classes_of(part_of(soup, "moment", 0))
        assert "input-error" in classes_of(part_of(soup, "moment", 1))

    def test_a_field_that_passes_has_no_error_modifier(self, draw):
        soup = draw_form(draw, MultiWidgetField("moment", attrs={}), data=DATA)

        assert "input-error" not in classes_of(part_of(soup, "moment", 0))

    def test_a_class_given_to_one_part_is_kept_beside_the_packs(self, draw):
        soup = draw_form(
            draw, MultiWidgetField("moment", attrs=({"class": "mine"}, {}))
        )

        date, time = part_of(soup, "moment", 0), part_of(soup, "moment", 1)

        assert {"mine", "input"} <= set(classes_of(date))
        assert "mine" not in classes_of(time)
        assert "input" in classes_of(time)

    def test_the_forms_size_and_colour_reach_every_part(self, draw):
        form = MultiWidgetsForm(None, layout=[MultiWidgetField("moment", attrs={})])
        form.helper.daisyui = FormChoices(size="lg", color="primary")

        soup = draw("{% crispy form %}", form=form)

        for index in (0, 1):
            assert {"input-lg", "input-primary"} <= set(
                classes_of(part_of(soup, "moment", index))
            )

    def test_a_choice_around_the_layout_object_reaches_every_part(self, draw):
        soup = draw_form(draw, Choice(MultiWidgetField("moment", attrs={}), size="sm"))

        for index in (0, 1):
            assert "input-sm" in classes_of(part_of(soup, "moment", index))

    def test_a_choice_around_the_layout_object_wins_over_the_forms(self, draw):
        form = MultiWidgetsForm(
            None, layout=[Choice(MultiWidgetField("moment", attrs={}), size="sm")]
        )
        form.helper.daisyui = FormChoices(size="lg")

        soup = draw("{% crispy form %}", form=form)

        classes = classes_of(part_of(soup, "moment", 0))

        assert "input-sm" in classes
        assert "input-lg" not in classes

    def test_a_failing_field_has_the_error_modifier_and_not_the_colour(self, draw):
        form = RefusedMomentForm({}, layout=[MultiWidgetField("moment", attrs={})])
        form.helper.daisyui = FormChoices(size="lg", color="primary")

        soup = draw("{% crispy form %}", form=form)

        for index in (0, 1):
            classes = classes_of(part_of(soup, "moment", index))
            assert {"input-lg", "input-error"} <= set(classes)
            assert "input-primary" not in classes


class TestMultiWidgetFieldFrame:
    def test_the_frame_is_a_fieldset_with_one_legend(self, draw):
        soup = draw_form(draw, MultiWidgetField("moment", attrs={}))

        frame = frame_of(soup)

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend")) == 1

    def test_the_frame_has_one_help_text_and_one_error_and_is_described_by_them(
        self, draw
    ):
        soup = draw_form(
            draw,
            MultiWidgetField("moment", attrs={}),
            bound=True,
            form=RefusedMomentForm,
        )

        frame = frame_of(soup)

        assert len(frame.find_all(id="id_moment_helptext")) == 1
        assert len(frame.find_all(id="id_moment_error")) == 1
        assert frame["aria-describedby"] == "id_moment_helptext id_moment_error"


class TestMultiWidgetFieldNames:
    def test_the_two_parts_of_a_split_date_and_time_are_named_differently(self, draw):
        soup = draw_form(draw, MultiWidgetField("moment", attrs={}))

        names = [part_of(soup, "moment", index)["aria-label"] for index in (0, 1)]

        assert names[0] != names[1]
        assert all(names)

    def test_a_name_given_through_the_layout_object_is_kept(self, draw):
        soup = draw_form(
            draw,
            MultiWidgetField("moment", attrs=({"aria-label": "Day of the start"}, {})),
        )

        assert part_of(soup, "moment", 0)["aria-label"] == "Day of the start"
        assert part_of(soup, "moment", 1)["aria-label"]

    def test_the_parts_of_any_other_multi_widget_are_named_by_the_fields_label(
        self, draw
    ):
        soup = draw_form(draw, MultiWidgetField("phone", attrs={}))

        names = [part_of(soup, "phone", index)["aria-label"] for index in range(3)]

        assert names == ["Phone", "Phone", "Phone"]


class TestMultiWidgetFieldCleaned:
    def test_cleaned_data_equals_the_undecorated_fields(self):
        plain = MultiWidgetsForm(DATA)
        decorated = MultiWidgetsForm(
            DATA, layout=[MultiWidgetField("moment", "phone", attrs={"class": "x"})]
        )

        assert plain.is_valid()
        assert decorated.is_valid()
        assert decorated.cleaned_data == plain.cleaned_data

    def test_cleaned_data_is_the_same_after_the_form_is_drawn(self, draw):
        form = MultiWidgetsForm(
            DATA, layout=[MultiWidgetField("moment", attrs={"class": "x"})]
        )
        before = MultiWidgetsForm(DATA)
        before.is_valid()

        draw("{% crispy form %}", form=form)

        assert form.is_valid()
        assert form.cleaned_data == before.cleaned_data


class TestMultiWidgetFieldWidgetsLeftAlone:
    def test_the_forms_widget_and_its_parts_carry_nothing_of_the_packs(self, draw):
        form = MultiWidgetsForm(
            {}, layout=[MultiWidgetField("moment", attrs=({"data-a": "1"}, {}))]
        )

        draw("{% crispy form %}", form=form)

        widget = form.fields["moment"].widget
        for part in widget.widgets:
            assert "input" not in str(part.attrs.get("class", "")).split()
            assert "input-error" not in str(part.attrs.get("class", "")).split()
            assert "aria-label" not in part.attrs
        assert "class" not in widget.attrs

    def test_the_widget_the_form_holds_is_the_same_object_after_drawing(self, draw):
        form = MultiWidgetsForm(None, layout=[MultiWidgetField("moment", attrs={})])
        widget = form.fields["moment"].widget
        parts = list(widget.widgets)

        draw("{% crispy form %}", form=form)

        assert form.fields["moment"].widget is widget
        assert widget.widgets == parts

    def test_drawing_twice_gives_the_same_markup(self, draw):
        form = MultiWidgetsForm(
            {}, layout=[MultiWidgetField("moment", attrs=({"class": "mine"}, {}))]
        )

        first = draw("{% crispy form %}", form=form)
        second = draw("{% crispy form %}", form=form)

        assert str(first) == str(second)

    def test_a_deep_copy_of_the_form_draws_the_same_markup(self, draw):
        form = MultiWidgetsForm(None, layout=[Field("moment")])

        first = draw("{% crispy form %}", form=form)
        second = draw("{% crispy form %}", form=copy.deepcopy(form))

        assert str(first) == str(second)


class TestSplitDateTimeWithNoLayoutObject:
    def test_each_part_is_an_input_named_by_its_own_label(self, draw):
        soup = draw_form(draw, Field("moment"))

        date, time = part_of(soup, "moment", 0), part_of(soup, "moment", 1)

        assert "input" in classes_of(date)
        assert "input" in classes_of(time)
        assert date["aria-label"] != time["aria-label"]

    def test_the_fields_that_fail_have_the_error_modifier_on_each_part(self, draw):
        soup = draw_form(draw, bound=True, form=RefusedMomentForm)

        assert "input-error" in classes_of(part_of(soup, "moment", 0))
        assert "input-error" in classes_of(part_of(soup, "moment", 1))

    def test_a_form_drawn_whole_gives_the_parts_the_same_classes(self, draw):
        form = MultiWidgetsForm(None)

        soup = draw("{{ form|crispy }}", form=form)

        assert "input" in classes_of(part_of(soup, "moment", 0))
        assert "input" in classes_of(part_of(soup, "phone", 2))

    def test_the_frame_is_a_fieldset_described_by_its_help_text(self, draw):
        soup = draw_form(draw)

        frame = frame_of(soup)

        assert frame.name == "fieldset"
        assert frame["aria-describedby"] == "id_moment_helptext"

    def test_a_hidden_split_field_is_drawn_as_hidden_inputs_alone(self, draw):
        form = MultiWidgetsForm(None, layout=[Field("moment")])
        form.fields["moment"].widget = form.fields["moment"].hidden_widget()

        soup = draw("{% crispy form %}", form=form)

        inputs = soup.find_all("input", attrs={"name": ["moment_0", "moment_1"]})

        assert [tag["type"] for tag in inputs] == ["hidden", "hidden"]
        assert all(not tag.has_attr("class") for tag in inputs)
        assert soup.find(id="div_id_moment") is None


class TestMultiWidgetFieldOnOneWidget:
    def test_a_field_with_one_widget_is_drawn_with_the_attributes(self, draw):
        soup = draw_form(draw, MultiWidgetField("name", attrs={"data-one": "1"}))

        field = soup.find(id="id_name")

        assert field["data-one"] == "1"
        assert "input" in classes_of(field)
        assert frame_of(soup, "name").name == "div"


class TestMultiWidgetFieldOptions:
    def test_wrapper_class_is_written_on_the_frame(self, draw):
        soup = draw_form(
            draw, MultiWidgetField("moment", attrs={}, wrapper_class="when")
        )

        assert "when" in frame_of(soup)["class"]

    def test_a_template_of_the_developers_draws_the_field(self, draw):
        soup = draw_form(
            draw,
            MultiWidgetField("moment", attrs={}, template="tests/own_container.html"),
        )

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None
