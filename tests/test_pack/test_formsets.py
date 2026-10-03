"""A formset drawn by the pack: stacked, one form after another."""

import pytest
from crispy_forms.layout import Submit

from tests.forms import (
    LineForm,
    MediaFormSet,
    formset_helper,
)

SOURCES = ["{% crispy formset %}", "{{ formset|crispy }}"]
MANAGEMENT = ["TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS", "MAX_NUM_FORMS"]
KINDS = ["plain_formset", "model_formset", "inline_formset"]


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
