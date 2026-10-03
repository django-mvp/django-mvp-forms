"""A formset drawn by the pack: stacked, one form after another."""

import pytest
from crispy_forms.layout import Submit

from tests.forms import (
    ChoiceLineFormSet,
    LineForm,
    MarkupRuledLineFormSet,
    MediaFormSet,
    RuledLineFormSet,
    formset_helper,
    ruled_data,
)

SOURCES = ["{% crispy formset %}", "{{ formset|crispy }}"]
MANAGEMENT = ["TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS", "MAX_NUM_FORMS"]
KINDS = ["plain_formset", "model_formset", "inline_formset"]
TABLE = "daisyui/table_inline_formset.html"
TAG = "{% crispy formset helper %}"


def names_in(tag):
    return {found["name"] for found in tag.find_all(attrs={"name": True})}


def names_of(form):
    return {form.add_prefix(name) for name in form.fields}


def container_of(soup, formset, index):
    others = set().union(
        *(names_of(form) for i, form in enumerate(formset.forms) if i != index)
    )
    own = names_of(formset.forms[index])
    node = soup.find(attrs={"name": min(own)})
    while not names_in(node.parent) & others:
        node = node.parent
    return node


@pytest.mark.django_db
class TestStackedFormset:
    @pytest.mark.parametrize("source", SOURCES)
    def test_each_form_is_drawn_in_order_in_a_container_of_its_own(
        self, draw, plain_formset, source
    ):
        formset = plain_formset()

        soup = draw(source, formset=formset)

        containers = [container_of(soup, formset, i) for i in range(3)]
        assert [names_in(tag) for tag in containers] == [
            names_of(form) for form in formset.forms
        ]
        assert all(tag.name == "div" for tag in containers)
        drawn = [tag["name"] for tag in soup.find_all(attrs={"name": True})]
        assert [n for n in drawn if n.endswith("-name")] == [
            form.add_prefix("name") for form in formset.forms
        ]

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_management_form_is_drawn_once_field_by_field(
        self, draw, plain_formset, source
    ):
        formset = plain_formset()

        soup = draw(source, formset=formset)

        for name in MANAGEMENT:
            inputs = soup.find_all(attrs={"name": formset.add_prefix(name)})
            assert len(inputs) == 1
            assert inputs[0]["type"] == "hidden"

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("kind", [*KINDS, "no_forms_formset"])
    def test_a_drawn_formset_binds_to_the_same_number_of_forms_and_is_valid(
        self, draw, posted, request, source, kind
    ):
        build = request.getfixturevalue(kind)
        unbound = build()

        soup = draw(source, formset=unbound)
        bound = build(posted(soup))

        assert bound.is_valid(), bound.errors
        assert len(bound.forms) == len(unbound.forms)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("kind", ["model_formset", "inline_formset"])
    def test_every_hidden_field_is_inside_its_form_s_container(
        self, draw, request, source, kind
    ):
        formset = request.getfixturevalue(kind)()

        soup = draw(source, formset=formset)

        for index, form in enumerate(formset.forms):
            container = container_of(soup, formset, index)
            hidden = {field.html_name for field in form.hidden_fields()}
            assert hidden
            assert hidden <= names_in(container)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_is_the_same_markup_as_in_a_single_form(
        self, draw, plain_formset, source
    ):
        formset = plain_formset()
        form = LineForm(prefix=formset.forms[0].prefix, use_required_attribute=False)

        in_formset = draw(source, formset=formset)
        alone = draw("{{ form|crispy }}", form=form)

        for name in ("name", "quantity"):
            frame = "div_" + form[name].auto_id
            assert in_formset.find(id=frame) is not None
            assert str(in_formset.find(id=frame)) == str(alone.find(id=frame))

    def test_a_formset_with_no_helper_is_drawn_stacked(self, draw, plain_formset):
        formset = plain_formset()

        soup = draw("{% crispy formset %}", formset=formset)

        assert len(soup.find_all("form")) == 1
        assert [container_of(soup, formset, i).name for i in range(3)] == ["div"] * 3

    def test_one_form_element_wraps_the_whole_formset(self, draw, plain_formset):
        formset = plain_formset()

        soup = draw(
            "{% crispy formset helper %}", formset=formset, helper=formset_helper()
        )

        wrapper = soup.find_all("form")
        assert len(wrapper) == 1
        assert names_in(wrapper[0]) >= set().union(*map(names_of, formset.forms))
        assert wrapper[0].find(attrs={"name": formset.add_prefix("TOTAL_FORMS")})

    def test_no_form_element_is_drawn_when_the_helper_asks_for_none(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        soup = draw(
            "{% crispy formset helper %}",
            formset=formset,
            helper=formset_helper(form_tag=False),
        )

        assert soup.find("form") is None
        assert soup.find(attrs={"name": formset.forms[0].add_prefix("name")})

    def test_the_filter_draws_no_form_element(self, draw, plain_formset):
        soup = draw("{{ formset|crispy }}", formset=plain_formset())

        assert soup.find("form") is None

    def test_a_helper_layout_is_applied_to_each_form(self, draw, plain_formset):
        formset = plain_formset()

        soup = draw(
            "{% crispy formset helper %}",
            formset=formset,
            helper=formset_helper("name", form_tag=False),
        )

        for index, form in enumerate(formset.forms):
            container = container_of(soup, formset, index)
            assert names_in(container) == {
                form.add_prefix("name"),
                form.add_prefix("ref"),
            }

    def test_a_button_added_to_the_helper_is_drawn_once(self, draw, plain_formset):
        soup = draw(
            "{% crispy formset helper %}",
            formset=plain_formset(),
            helper=formset_helper(buttons=[Submit("save", "Save")]),
        )

        assert len(soup.find_all(attrs={"name": "save"})) == 1

    def test_the_formset_s_media_is_drawn_once(self, draw):
        formset = MediaFormSet()

        soup = draw("{% crispy formset %}", formset=formset)

        scripts = soup.find_all("script", src=lambda src: src.endswith("media.js"))
        assert len(scripts) == 1

    def test_the_media_is_left_out_when_the_helper_asks_for_none(self, draw):
        soup = draw(
            "{% crispy formset helper %}",
            formset=MediaFormSet(),
            helper=formset_helper(include_media=False),
        )

        assert soup.find("script") is None


def inputs_in(tag):
    return [
        found
        for found in tag.find_all(["input", "select", "textarea"])
        if found.get("type") != "hidden"
    ]


def table_helper(*layout, **settings):
    return formset_helper(*layout, template=TABLE, **settings)


@pytest.mark.django_db
class TestTableFormset:
    def test_one_table_has_a_row_per_form_in_order(self, draw, plain_formset):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        tables = soup.find_all("table")
        assert len(tables) == 1
        assert "table" in tables[0]["class"]
        rows = tables[0].find("tbody").find_all("tr")
        assert [names_in(row) for row in rows] == [
            names_of(form) for form in formset.forms
        ]
        drawn = [found["name"] for found in tables[0].find_all(attrs={"name": True})]
        assert [name for name in drawn if name.endswith("-name")] == [
            form.add_prefix("name") for form in formset.forms
        ]

    def test_there_is_a_heading_per_visible_field_holding_its_label(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        headings = soup.find("thead").find_all("th")
        visible = formset.forms[0].visible_fields()
        assert len(headings) == len(visible)
        for heading, field in zip(headings, visible, strict=True):
            assert heading["scope"] == "col"
            assert field.label in heading.get_text()

    def test_a_required_field_s_heading_holds_the_marker_and_an_optional_one_not(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        required, optional = soup.find("thead").find_all("th")
        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    def test_every_input_is_named_by_an_aria_label_equal_to_its_label(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        for row, form in zip(
            soup.find("tbody").find_all("tr"), formset.forms, strict=True
        ):
            for field in form.visible_fields():
                (found,) = row.find_all(attrs={"name": field.html_name})
                assert found["aria-label"] == field.label
                assert not row.find_all("label")

    def test_an_input_is_described_by_its_help_text_in_the_same_cell(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        for row, form in zip(
            soup.find("tbody").find_all("tr"), formset.forms, strict=True
        ):
            helped = row.find(attrs={"name": form.add_prefix("name")})
            unhelped = row.find(attrs={"name": form.add_prefix("quantity")})
            cell = helped.find_parent("td")
            assert cell.find(id=helped["aria-describedby"]) is not None
            assert not unhelped.has_attr("aria-describedby")

    def test_a_group_keeps_its_fieldset_and_the_fieldset_carries_the_label(self, draw):
        formset = ChoiceLineFormSet()

        soup = draw(TAG, formset=formset, helper=table_helper())

        for row, form in zip(
            soup.find("tbody").find_all("tr"), formset.forms, strict=True
        ):
            for field in form.visible_fields():
                fieldset = row.find(id="div_" + field.auto_id)
                assert fieldset.name == "fieldset"
                assert fieldset["aria-label"] == field.label
                assert fieldset.find(attrs={"name": field.html_name}) is not None
                assert not any(
                    option.has_attr("aria-label") for option in inputs_in(fieldset)
                )

    @pytest.mark.parametrize("kind", KINDS)
    def test_every_hidden_field_is_in_its_row_and_adds_no_heading_or_cell(
        self, draw, request, kind
    ):
        formset = request.getfixturevalue(kind)()

        soup = draw(TAG, formset=formset, helper=table_helper())

        visible = formset.forms[0].visible_fields()
        assert len(soup.find("thead").find_all("th")) == len(visible)
        rows = soup.find("tbody").find_all("tr")
        for row, form in zip(rows, formset.forms, strict=True):
            hidden = {field.html_name for field in form.hidden_fields()}
            assert hidden
            assert hidden <= names_in(row.find("td"))
            assert len(row.find_all("td")) == len(visible)
            assert all(
                found.find_parent("td") is not None
                for field in form.hidden_fields()
                for found in row.find_all(attrs={"name": field.html_name})
            )

    @pytest.mark.parametrize("kind", [*KINDS, "no_forms_formset"])
    def test_the_management_form_is_drawn_once(self, draw, request, kind):
        formset = request.getfixturevalue(kind)()

        soup = draw(TAG, formset=formset, helper=table_helper())

        for name in MANAGEMENT:
            inputs = soup.find_all(attrs={"name": formset.add_prefix(name)})
            assert len(inputs) == 1
            assert inputs[0]["type"] == "hidden"

    @pytest.mark.parametrize("kind", [*KINDS, "no_forms_formset"])
    def test_a_drawn_formset_binds_to_the_same_number_of_forms_and_is_valid(
        self, draw, posted, request, kind
    ):
        build = request.getfixturevalue(kind)
        unbound = build()

        soup = draw(TAG, formset=unbound, helper=table_helper())
        bound = build(posted(soup))

        assert bound.is_valid(), bound.errors
        assert len(bound.forms) == len(unbound.forms)

    def test_one_form_element_wraps_the_table(self, draw, plain_formset):
        soup = draw(TAG, formset=plain_formset(), helper=table_helper())

        wrapper = soup.find_all("form")
        assert len(wrapper) == 1
        assert wrapper[0].find("table") is not None

    def test_no_form_element_is_drawn_when_the_helper_asks_for_none(
        self, draw, plain_formset
    ):
        soup = draw(TAG, formset=plain_formset(), helper=table_helper(form_tag=False))

        assert soup.find("form") is None
        assert soup.find("table") is not None

    def test_no_forms_draws_no_table(self, draw, no_forms_formset):
        formset = no_forms_formset()

        soup = draw(TAG, formset=formset, helper=table_helper())

        assert soup.find("table") is None
        assert soup.find(attrs={"name": formset.add_prefix("TOTAL_FORMS")})

    def test_the_template_is_the_only_change_between_the_layouts(
        self, draw, plain_formset
    ):
        formset = plain_formset()

        stacked = draw(TAG, formset=formset, helper=formset_helper(form_tag=False))
        tabled = draw(TAG, formset=formset, helper=table_helper(form_tag=False))

        assert stacked.find("table") is None
        assert tabled.find("table") is not None
        assert names_in(stacked) == names_in(tabled)

    def test_a_helper_layout_is_not_applied(self, draw, plain_formset):
        formset = plain_formset()

        soup = draw(TAG, formset=formset, helper=table_helper("name", form_tag=False))

        rows = soup.find("tbody").find_all("tr")
        assert [names_in(row) for row in rows] == [
            names_of(form) for form in formset.forms
        ]
        assert len(soup.find("thead").find_all("th")) == 2

    def test_the_formset_s_media_is_drawn_once(self, draw):
        soup = draw(TAG, formset=MediaFormSet(), helper=table_helper())

        scripts = soup.find_all("script", src=lambda src: src.endswith("media.js"))
        assert len(scripts) == 1

    def test_a_button_added_to_the_helper_is_drawn_once(self, draw, plain_formset):
        soup = draw(
            TAG,
            formset=plain_formset(),
            helper=table_helper(buttons=[Submit("save", "Save")]),
        )

        assert len(soup.find_all(attrs={"name": "save"})) == 1


REQUIRED = "This field is required."
WHOLE = "The line failed as a whole"
TOO_MUCH = "The lines add up to too much"
REFUSED = "The reference is refused"
LAYOUTS = ["stacked", "table"]
SOUND = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
ALL_THREE = [
    {"name": "a", "quantity": "6"},
    {"name": "", "quantity": "6"},
    {"name": "whole"},
]


def layout_helper(layout, **settings):
    if layout == "table":
        return table_helper(form_tag=False, **settings)
    return formset_helper(form_tag=False, **settings)


def units_of(soup, formset, layout):
    if layout == "table":
        return soup.find("tbody").find_all("tr")
    return [container_of(soup, formset, i) for i in range(len(formset.forms))]


def draw_ruled(draw, layout, lines, formset_class=RuledLineFormSet, **settings):
    formset = formset_class(ruled_data(*lines))
    soup = draw(TAG, formset=formset, helper=layout_helper(layout, **settings))
    return soup, formset, units_of(soup, formset, layout)


def occurrences(soup, message):
    return soup.get_text().count(message)


def described_by(tag):
    return tag["aria-describedby"].split()


class TestFormsetErrors:
    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_a_field_error_is_in_its_form_s_unit_and_describes_the_input(
        self, draw, layout
    ):
        lines = [{"name": "a"}, {"name": "", "quantity": "1"}, {"name": "c"}]

        soup, formset, units = draw_ruled(draw, layout, lines)

        field = formset.forms[1]["name"]
        error = units[1].find(id=field.auto_id + "_error")
        assert error is not None
        assert REQUIRED in error.get_text()
        assert error["id"] in described_by(
            units[1].find(attrs={"name": field.html_name})
        )
        assert occurrences(soup, REQUIRED) == 1
        assert not any(REQUIRED in unit.get_text() for unit in (units[0], units[2]))

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_a_form_wide_error_is_in_its_form_s_unit(self, draw, layout):
        lines = [{"name": "a"}, {"name": "b"}, {"name": "whole"}]

        soup, formset, units = draw_ruled(draw, layout, lines)

        assert WHOLE in units[2].get_text()
        assert occurrences(soup, WHOLE) == 1
        assert not any(WHOLE in unit.get_text() for unit in units[:2])

    def test_a_row_s_form_wide_error_is_named_by_the_row(self, draw):
        lines = [{"name": "a"}, {"name": "b"}, {"name": "whole"}]

        soup, formset, units = draw_ruled(draw, "table", lines)

        prefix = formset.forms[2].prefix
        error = units[2].find(id=prefix + "_errors")
        assert error["role"] == "alert"
        assert WHOLE in error.get_text()
        assert error.find_parent("td") is units[2].find("td")
        assert described_by(units[2]) == [prefix + "_errors"]
        assert not units[0].has_attr("aria-describedby")
        assert not units[1].has_attr("aria-describedby")
        assert len(soup.find("tbody").find_all("tr")) == 3

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_a_hidden_field_s_error_is_with_its_form(self, draw, layout):
        lines = [{"name": "a"}, {"name": "b"}, {"name": "c", "ref": "bad"}]

        soup, formset, units = draw_ruled(draw, layout, lines)

        assert REFUSED in units[2].get_text()
        assert occurrences(soup, REFUSED) == 1

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_a_formset_wide_error_is_drawn_once_outside_every_unit(self, draw, layout):
        lines = [{"name": "a", "quantity": "6"}, {"name": "b", "quantity": "6"}, {}]

        soup, formset, units = draw_ruled(draw, layout, lines)

        alerts = soup.find_all(attrs={"role": "alert"})
        assert len(alerts) == 1
        assert TOO_MUCH in alerts[0].get_text()
        assert not any(unit in alerts[0].parents for unit in units)

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_every_message_is_drawn_exactly_once_with_all_three_kinds(
        self, draw, layout
    ):
        lines = [*ALL_THREE[:2], {"name": "whole", "ref": "bad"}]

        soup, formset, units = draw_ruled(draw, layout, lines)

        assert formset.non_form_errors()
        for message in (REQUIRED, WHOLE, TOO_MUCH, REFUSED):
            assert occurrences(soup, message) == 1, message
        assert TOO_MUCH not in "".join(unit.get_text() for unit in units)

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_no_alert_and_no_row_description_without_errors(
        self, draw, plain_formset, layout
    ):
        unbound = plain_formset()
        valid = RuledLineFormSet(ruled_data(*SOUND))

        for formset in (unbound, valid):
            soup = draw(TAG, formset=formset, helper=layout_helper(layout))

            assert formset.is_bound is (formset is valid)
            assert soup.find(attrs={"role": "alert"}) is None
            assert soup.find("tr", attrs={"aria-describedby": True}) is None

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_a_message_holding_markup_is_escaped(self, draw, layout):
        lines = [{"name": "a", "quantity": "6"}, {"name": "b", "quantity": "6"}, {}]

        soup, _, _ = draw_ruled(
            draw, layout, lines, formset_class=MarkupRuledLineFormSet
        )

        assert soup.find("script") is None
        assert "<script>alert(1)</script>" in soup.find(attrs={"role": "alert"}).text

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_no_error_is_drawn_when_the_helper_turns_errors_off(self, draw, layout):
        soup, _, _ = draw_ruled(draw, layout, ALL_THREE, form_show_errors=False)

        assert soup.find(attrs={"role": "alert"}) is None
        for message in (REQUIRED, WHOLE, TOO_MUCH):
            assert occurrences(soup, message) == 0, message
        assert soup.find("tr", attrs={"aria-describedby": True}) is None

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_the_formset_error_title_is_drawn_when_set(self, draw, layout):
        lines = [{"name": "a", "quantity": "6"}, {"name": "b", "quantity": "6"}, {}]

        soup, _, _ = draw_ruled(draw, layout, lines, formset_error_title="Mind this")

        assert "Mind this" in soup.find(attrs={"role": "alert"}).get_text()

    @pytest.mark.parametrize("layout", LAYOUTS)
    def test_no_title_is_drawn_when_none_is_set(self, draw, layout):
        lines = [{"name": "a", "quantity": "6"}, {"name": "b", "quantity": "6"}, {}]

        soup, _, _ = draw_ruled(draw, layout, lines)

        assert len(soup.find(attrs={"role": "alert"}).find_all("p")) == 1

    def test_the_filter_draws_the_formset_wide_errors_once_in_the_stacked_layout(
        self, draw
    ):
        formset = RuledLineFormSet(ruled_data(*ALL_THREE))

        soup = draw("{{ formset|crispy }}", formset=formset)

        assert occurrences(soup, TOO_MUCH) == 1

    def test_the_errors_filter_draws_the_formset_wide_errors_alone(self, draw):
        formset = RuledLineFormSet(ruled_data(*ALL_THREE))

        soup = draw("{{ formset|as_crispy_errors }}", formset=formset)

        assert len(soup.find_all(attrs={"role": "alert"})) == 1
        assert occurrences(soup, TOO_MUCH) == 1
        for message in (REQUIRED, WHOLE):
            assert occurrences(soup, message) == 0
        assert soup.find(attrs={"name": True}) is None
