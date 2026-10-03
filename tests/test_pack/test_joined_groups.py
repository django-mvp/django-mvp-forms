"""Fields drawn as one daisyUI join under one label, through crispy-forms."""

import pytest
from crispy_forms.bootstrap import PrependedText
from crispy_forms.layout import Div, Field

from mvp_forms.choices import Choice
from mvp_forms.layout import InvalidMember, Join
from tests.forms import (
    JoinedEdgesForm,
    JoinedForm,
    LineFormSet,
    formset_helper,
)

TAG = "{% crispy form %}"
FORMSET = "{% crispy formset helper %}"
TABLE = "daisyui/table_inline_formset.html"
GROUP_LABEL = "Phone"
VISIBLE = ["country_code", "number", "extension"]
UNJOINED = ["notes", "country_code", "number", "extension", "token"]


def joined(*members, **options):
    options.setdefault("label", GROUP_LABEL)
    return JoinedForm(layout=["notes", Join(*members, **options)])


def join_of(soup):
    return soup.find("div", class_="join")


def children_of(group):
    return group.find_all(True, recursive=False)


def names_in(group):
    return [tag["name"] for tag in children_of(group)]


def refused(draw, form):
    with pytest.raises(InvalidMember) as caught:
        draw(TAG, form=form)
    return caught.value


class TestJoinedGroups:
    def test_the_inputs_are_the_direct_children_of_one_join_in_the_layouts_order(
        self, draw
    ):
        soup = draw(TAG, form=JoinedForm())

        group = join_of(soup)
        assert len(soup.find_all(class_="join")) == 1
        assert names_in(group) == VISIBLE
        assert all("join-item" in tag["class"] for tag in children_of(group))

    def test_the_order_is_the_layouts_not_the_forms(self, draw):
        form = joined("extension", "number", "country_code")

        soup = draw(TAG, form=form)

        assert names_in(join_of(soup)) == ["extension", "number", "country_code"]

    def test_the_group_is_one_fieldset_with_one_legend_and_no_label_for_a_member(
        self, draw
    ):
        soup = draw(TAG, form=JoinedForm())

        fieldset = join_of(soup).find_parent("fieldset")
        assert len(soup.find_all("fieldset")) == 1
        assert len(fieldset.find_all("legend")) == 1
        assert GROUP_LABEL in fieldset.find("legend").get_text()
        for name in VISIBLE:
            assert soup.find_all("label", attrs={"for": f"id_{name}"}) == []

    def test_each_input_is_named_by_its_own_fields_label(self, draw):
        form = JoinedForm()

        soup = draw(TAG, form=form)

        for tag in children_of(join_of(soup)):
            assert tag["aria-label"] == form[tag["name"]].label

    def test_an_aria_label_the_developer_wrote_is_kept(self, draw):
        form = joined("country_code", Field("number", aria_label="Mine"))

        soup = draw(TAG, form=form)

        assert soup.find(id="id_number")["aria-label"] == "Mine"
        assert soup.find(id="id_country_code")["aria-label"] == "Country code"

    def test_a_members_help_text_is_drawn_once_inside_the_fieldset_and_tied_to_it(
        self, draw
    ):
        soup = draw(TAG, form=JoinedForm())

        helps = soup.find_all(id="id_number_helptext")
        assert len(helps) == 1
        assert helps[0].find_parent("fieldset") is join_of(soup).find_parent("fieldset")
        for tag in children_of(join_of(soup)):
            described = tag.get("aria-describedby", "").split()
            assert ("id_number_helptext" in described) is (tag["name"] == "number")

    def test_only_the_failing_member_is_invalid_and_its_error_is_drawn_once(self, draw):
        form = JoinedForm({"country_code": "+49", "number": ""})

        soup = draw(TAG, form=form)

        invalid = [tag["name"] for tag in soup.find_all(attrs={"aria-invalid": "true"})]
        assert invalid == ["number"]
        errors = soup.find_all(id="id_number_error")
        assert len(errors) == 1
        assert errors[0].find_parent("fieldset") is join_of(soup).find_parent(
            "fieldset"
        )
        assert (
            "id_number_error" in soup.find(id="id_number")["aria-describedby"].split()
        )
        for name in ("country_code", "extension"):
            assert soup.find(id=f"id_{name}_error") is None

    def test_a_required_member_puts_the_marker_in_the_legend_and_requires_the_input(
        self, draw
    ):
        soup = draw(TAG, form=JoinedForm())

        legend = join_of(soup).find_parent("fieldset").find("legend")
        assert legend.find(attrs={"aria-hidden": "true"}) is not None
        assert soup.find(id="id_number").has_attr("required")

    def test_a_group_of_optional_members_has_no_marker(self, draw):
        soup = draw(TAG, form=joined("extension"))

        legend = join_of(soup).find_parent("fieldset").find("legend")
        assert legend.find(attrs={"aria-hidden": "true"}) is None

    @pytest.mark.parametrize("bound", [False, True], ids=["valid", "invalid"])
    def test_a_form_posted_from_its_drawn_inputs_cleans_to_the_same_data(
        self, draw, posted, bound
    ):
        results = []
        for layout in (None, UNJOINED):
            soup = draw(TAG, form=JoinedForm(layout=layout))
            data = posted(soup)
            data["number"] = "" if bound else "5551234"
            form = JoinedForm(data, layout=layout)
            results.append(
                (sorted(data), form.is_valid(), form.errors, form.cleaned_data)
            )

        assert results[0] == results[1]
        assert results[0][1] is not bound

    def test_a_disabled_member_is_disabled_in_its_place(self, draw):
        form = JoinedEdgesForm(layout=[Join("country_code", "locked", "fixed")])

        soup = draw(TAG, form=form)

        group = join_of(soup)
        assert names_in(group) == ["country_code", "locked", "fixed"]
        assert group.find(attrs={"name": "locked"}).has_attr("disabled")
        assert not group.find(attrs={"name": "country_code"}).has_attr("disabled")

    def test_a_read_only_member_keeps_its_attribute(self, draw):
        form = JoinedEdgesForm(layout=[Join("country_code", "fixed")])

        soup = draw(TAG, form=form)

        fixed = join_of(soup).find(attrs={"name": "fixed"})
        assert fixed.has_attr("readonly")
        assert fixed["value"] == "Ada"

    def test_a_hidden_member_is_a_hidden_input_outside_the_join(self, draw):
        form = JoinedEdgesForm(layout=[Join("country_code", "token", "fixed")])

        soup = draw(TAG, form=form)

        group = join_of(soup)
        token = soup.find(attrs={"name": "token"})
        assert token["type"] == "hidden"
        assert token.find_parent(class_="join") is None
        assert token.find_parent("fieldset") is group.find_parent("fieldset")
        assert names_in(group) == ["country_code", "fixed"]

    @pytest.mark.parametrize("name", ["agree", "bio"])
    def test_a_field_that_cannot_be_joined_raises_naming_it(self, draw, name):
        form = JoinedEdgesForm(layout=[Join("country_code", name)])

        assert refused(draw, form).member == name

    def test_the_developers_id_class_and_attribute_are_on_the_join(self, draw):
        form = joined(
            *VISIBLE,
            css_id="phone",
            css_class="mine btn-inverse",
            data_role="phone",
        )

        soup = draw(TAG, form=form)

        group = soup.find(id="phone")
        assert group is join_of(soup)
        assert "mine" in group["class"]
        assert "btn-inverse" not in group["class"]
        assert group["data-role"] == "phone"

    def test_every_form_of_a_stacked_formset_draws_the_group(self, draw):
        helper = formset_helper(Join("name", "quantity", "ref", label="Line"))

        soup = draw(FORMSET, formset=LineFormSet(), helper=helper)

        groups = soup.find_all("div", class_="join")
        assert len(groups) == 3
        for row, group in enumerate(groups):
            assert names_in(group) == [f"form-{row}-name", f"form-{row}-quantity"]


class TestJoinedGroupEdges:
    def test_a_group_with_no_label_draws_no_legend_and_each_input_is_named(self, draw):
        form = joined(*VISIBLE, label=None)

        soup = draw(TAG, form=form)

        group = join_of(soup)
        assert group.find_parent("fieldset").find("legend") is None
        for tag in children_of(group):
            assert tag["aria-label"] == form[tag["name"]].label

    def test_a_group_of_one_is_drawn(self, draw):
        soup = draw(TAG, form=joined("number"))

        assert names_in(join_of(soup)) == ["number"]

    def test_with_the_helpers_labels_off_the_fieldset_is_named_and_has_no_legend(
        self, draw
    ):
        form = JoinedForm(show_labels=False)

        soup = draw(TAG, form=form)

        fieldset = join_of(soup).find_parent("fieldset")
        assert fieldset.find("legend") is None
        assert fieldset["aria-label"] == GROUP_LABEL
        for tag in children_of(join_of(soup)):
            assert tag["aria-label"] == form[tag["name"]].label

    def test_a_field_passes_its_attribute_and_its_class_to_its_members_input(
        self, draw
    ):
        form = joined("country_code", Field("number", css_class="mine", maxlength="9"))

        soup = draw(TAG, form=form)

        number = soup.find(id="id_number")
        assert "mine" in number["class"]
        assert number["maxlength"] == "9"
        assert "mine" not in soup.find(id="id_country_code")["class"]

    def test_a_choice_around_a_member_reaches_that_member(self, draw):
        form = joined(Choice("country_code", size="lg"), "number")

        soup = draw(TAG, form=form)

        assert "select-lg" in soup.find(id="id_country_code")["class"]
        assert "input-lg" not in soup.find(id="id_number")["class"]

    def test_a_choice_around_the_group_reaches_every_member(self, draw):
        form = JoinedForm(layout=[Choice(Join("country_code", "number"), size="lg")])

        soup = draw(TAG, form=form)

        assert "select-lg" in soup.find(id="id_country_code")["class"]
        assert "input-lg" in soup.find(id="id_number")["class"]

    @pytest.mark.parametrize("held", [Div("number"), PrependedText("number", "$")])
    def test_any_other_layout_object_raises_when_the_form_is_drawn(self, draw, held):
        form = joined("country_code", held)

        assert refused(draw, form).member == type(held).__name__

    def test_a_formset_drawn_as_a_table_draws_no_join_and_raises_nothing(self, draw):
        helper = formset_helper(Join("name", "quantity", label="Line"), template=TABLE)

        soup = draw(FORMSET, formset=LineFormSet(), helper=helper)

        assert soup.find(class_="join") is None
        assert soup.find(id="id_form-0-name") is not None

    def test_a_label_holding_markup_is_escaped(self, draw):
        form = joined(*VISIBLE, label="<b>Phone</b>")

        soup = draw(TAG, form=form)

        legend = join_of(soup).find_parent("fieldset").find("legend")
        assert legend.find("b") is None
        assert "<b>Phone</b>" in legend.get_text()
