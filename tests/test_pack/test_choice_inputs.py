"""Fields with choices, drawn through django-crispy-forms."""

import copy

import pytest
from crispy_forms.helper import FormHelper

from tests.forms import DateSelectsForm, SelectEdgesForm, SelectsForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
SELECTS = ["choice", "many", "maybe", "grouped"]


def option_values(select):
    return [option["value"] for option in select.find_all("option")]


def selected_values(select):
    return [option["value"] for option in select.find_all("option", selected=True)]


class TestSelect:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", SELECTS)
    def test_each_is_a_select_with_the_component_class(self, draw, source, name):
        soup = draw(source, form=SelectsForm())

        drawn = soup.find(id=f"id_{name}")

        assert drawn.name == "select"
        assert "select" in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_every_choice_is_offered(self, draw, source):
        soup = draw(source, form=SelectsForm())

        assert option_values(soup.find(id="id_choice")) == ["a", "b"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", SELECTS)
    def test_the_label_is_tied_to_the_select(self, draw, source, name):
        soup = draw(source, form=SelectsForm())

        assert soup.find("label", attrs={"for": f"id_{name}"}) is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_initial_choice_is_selected(self, draw, source):
        form = SelectsForm(initial={"choice": "b"})

        soup = draw(source, form=form)

        assert selected_values(soup.find(id="id_choice")) == ["b"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_held_choice_stays_selected_after_a_failed_submission(self, draw, source):
        form = SelectsForm({"choice": "b", "many": ["a"], "grouped": "nowhere"})

        soup = draw(source, form=form)

        assert form.errors
        assert selected_values(soup.find(id="id_choice")) == ["b"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_multiple_select_holds_every_value(self, draw, source):
        form = SelectsForm({"many": ["a", "b"]})

        drawn = draw(source, form=form).find(id="id_many")

        assert drawn.has_attr("multiple")
        assert selected_values(drawn) == ["a", "b"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_named_groups_are_optgroups_holding_their_choices(self, draw, source):
        drawn = draw(source, form=SelectsForm()).find(id="id_grouped")

        groups = {
            group["label"]: option_values(group) for group in drawn.find_all("optgroup")
        }

        assert groups == {"Fruit": ["a", "b"], "Vegetable": ["c"]}
        assert "d" in option_values(drawn)

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_invalid_select_is_marked_and_described_by_its_error(self, draw, source):
        soup = draw(source, form=SelectsForm({"choice": "nowhere"}))

        drawn = soup.find(id="id_choice")

        assert "select-error" in drawn["class"]
        assert drawn["aria-invalid"] == "true"
        described = drawn["aria-describedby"].split()
        assert "id_choice_error" in described
        assert all(soup.find(id=name) is not None for name in described)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_valid_select_carries_no_error_modifier(self, draw, source):
        drawn = draw(source, form=SelectsForm({"choice": "a"})).find(id="id_choice")

        assert "select-error" not in drawn["class"]
        assert not drawn.has_attr("aria-invalid")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_null_boolean_select_offers_three_options(self, draw, source):
        drawn = draw(source, form=SelectsForm()).find(id="id_maybe")

        assert len(drawn.find_all("option")) == 3

    @pytest.mark.parametrize("source", SOURCES)
    def test_no_choices_draws_an_empty_select(self, draw, source):
        drawn = draw(source, form=SelectEdgesForm()).find(id="id_empty")

        assert drawn.name == "select"
        assert drawn.find_all("option") == []

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_value_no_longer_among_the_choices_selects_nothing(self, draw, source):
        form = SelectEdgesForm({"marked": "gone", "styled": "a"})

        drawn = draw(source, form=form).find(id="id_marked")

        assert selected_values(drawn) == []

    @pytest.mark.parametrize("source", SOURCES)
    def test_markup_in_a_choice_and_a_group_name_is_escaped(self, draw, source):
        soup = draw(source, form=SelectEdgesForm())

        marked = soup.find(id="id_marked")
        grouped = soup.find(id="id_marked_groups")

        assert marked.find("b") is None
        assert grouped.find("i") is None
        assert grouped.find("optgroup")["label"] == "<i>Group</i>"
        assert option_values(marked) == ["<b>", "x"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_class_and_data_attribute_are_kept(self, draw, source):
        drawn = draw(source, form=SelectEdgesForm()).find(id="id_styled")

        assert {"mine", "select"} <= set(drawn["class"])
        assert drawn["data-role"] == "picker"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_draw_leaves_the_widgets_attrs_unchanged(self, draw, source):
        form = SelectEdgesForm({"styled": "gone"})
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        draw(source, form=form)

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before


class TestSelectDate:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_three_selects_each_have_the_component_and_a_name_of_their_own(
        self, draw, source
    ):
        soup = draw(source, form=DateSelectsForm())

        selects = soup.find(id="div_id_born").find_all("select")

        assert {select["name"] for select in selects} == {
            "born_month",
            "born_day",
            "born_year",
        }
        assert all("select" in select["class"] for select in selects)
        names = [select["aria-label"] for select in selects]
        assert all(names)
        assert len(set(names)) == 3

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_field_has_one_legend_one_help_text_and_one_error_element(
        self, draw, source
    ):
        soup = draw(source, form=DateSelectsForm({}))

        frame = soup.find(id="div_id_born")

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend")) == 1
        assert frame.find("label") is None
        assert len(frame.find_all(id="id_born_helptext")) == 1
        assert len(frame.find_all(id="id_born_error")) == 1

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_fieldset_is_described_by_ids_that_exist(self, draw, source):
        soup = draw(source, form=DateSelectsForm({}))

        frame = soup.find(id="div_id_born")
        described = frame["aria-describedby"].split()

        assert described == ["id_born_helptext", "id_born_error"]
        assert all(soup.find(id=name) is not None for name in described)
        assert not any(
            select.has_attr("aria-describedby") for select in frame.find_all("select")
        )

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_with_neither_help_nor_errors_is_not_described(self, draw, source):
        soup = draw(source, form=DateSelectsForm())

        assert not soup.find(id="div_id_plain").has_attr("aria-describedby")

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_invalid_date_marks_every_select(self, draw, source):
        soup = draw(source, form=DateSelectsForm({}))

        selects = soup.find(id="div_id_born").find_all("select")

        assert all(select["aria-invalid"] == "true" for select in selects)
        assert all("select-error" in select["class"] for select in selects)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_held_date_selects_its_three_parts(self, draw, source):
        form = DateSelectsForm(
            {"born_year": "2021", "born_month": "3", "born_day": "9"}
        )

        soup = draw(source, form=form)

        assert selected_values(soup.find(id="id_born_year")) == ["2021"]
        assert selected_values(soup.find(id="id_born_month")) == ["3"]
        assert selected_values(soup.find(id="id_born_day")) == ["9"]

    def test_with_labels_off_the_fieldset_is_named_by_aria_label(self, draw):
        form = DateSelectsForm()
        form.helper = FormHelper()
        form.helper.form_show_labels = False

        soup = draw("{% crispy form %}", form=form)

        frame = soup.find(id="div_id_born")
        assert frame["aria-label"] == form["born"].label
        assert frame.find("legend") is None

    def test_a_subclass_naming_its_own_template_is_drawn_by_it(self, draw):
        soup = draw("{{ form|crispy }}", form=DateSelectsForm())

        own = soup.find(id="div_id_own").find_all("select")
        pack = soup.find(id="div_id_plain").find_all("select")

        assert len(own) == 3
        assert all("select" in select["class"] for select in own)
        assert not any(select.has_attr("aria-label") for select in own)
        assert all(select.has_attr("aria-label") for select in pack)
