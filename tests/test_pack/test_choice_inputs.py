"""Fields with choices, drawn through django-crispy-forms."""

import copy

import pytest

from tests.forms import SelectEdgesForm, SelectsForm

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
