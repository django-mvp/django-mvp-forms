"""The layout objects that group fields behind tabs: a tab holder and its tabs."""

import pytest
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.layout import HTML, Div, Fieldset, Row
from django.utils.translation import gettext_lazy

from mvp_forms.templatetags.daisyui import TAB_GROUP_PLACEHOLDER
from tests.forms import (
    StructureForm,
    StructureHiddenForm,
    StructureWideErrorForm,
)

DEVELOPER_CLASSES = ["mine", "other"]
DEVELOPER_ATTRS = {"data-role": "group", "title": "Group"}
FIELDS = {"first": "a", "second": "b", "third": "c", "fourth": "d"}
FORM_CONTROLS = {*FIELDS, "csrfmiddlewaretoken"}


def three_tabs():
    return TabHolder(
        Tab("One", "first", css_id="one"),
        Tab("Two", "second", css_id="two"),
        Tab("Three", "third", "fourth", css_id="three"),
        css_id="holder",
    )


def data_without(*names):
    return {name: value for name, value in FIELDS.items() if name not in names}


def radios(soup):
    return soup.find_all("input", class_="tab")


def checked(soup):
    return [radio for radio in radios(soup) if radio.has_attr("checked")]


def labels_of(radios_):
    return [radio["aria-label"] for radio in radios_]


def content_of(radio):
    return radio.find_next_sibling()


class TestTabHolder:
    def test_it_draws_one_tabs_element_holding_every_radio(self, draw_layout):
        soup = draw_layout(three_tabs())

        holder = soup.find("div", id="holder")
        assert "tabs" in holder["class"]
        assert radios(holder) == radios(soup)
        assert labels_of(radios(holder)) == ["One", "Two", "Three"]

    def test_each_radio_is_followed_by_its_own_content_element(self, draw_layout):
        soup = draw_layout(three_tabs())

        for radio, tab_id in zip(radios(soup), ["one", "two", "three"], strict=True):
            content = content_of(radio)
            assert content.name == "div"
            assert "tab-content" in content["class"]
            assert content["id"] == tab_id

    def test_each_content_element_holds_its_own_fields(self, draw_layout):
        soup = draw_layout(three_tabs())

        fields = [
            [tag["id"] for tag in content_of(radio).find_all("input")]
            for radio in radios(soup)
        ]
        assert fields == [["id_first"], ["id_second"], ["id_third", "id_fourth"]]

    def test_the_holder_and_each_tab_carry_what_they_were_given(self, draw_layout):
        soup = draw_layout(
            TabHolder(
                Tab(
                    "One",
                    "first",
                    css_id="one",
                    css_class=" ".join(DEVELOPER_CLASSES),
                    **DEVELOPER_ATTRS,
                ),
                css_id="holder",
                css_class="mine",
                **DEVELOPER_ATTRS,
            )
        )

        holder = soup.find("div", id="holder")
        pane = soup.find("div", id="one")
        assert "mine" in holder["class"]
        assert set(DEVELOPER_CLASSES) <= set(pane["class"])
        for element in (holder, pane):
            assert element["data-role"] == DEVELOPER_ATTRS["data-role"]
            assert element["title"] == DEVELOPER_ATTRS["title"]

    @pytest.mark.parametrize("bound", [False, True], ids=["unbound", "invalid"])
    def test_neither_tab_pane_nor_active_is_drawn(self, draw_layout, bound):
        soup = draw_layout(three_tabs(), bound=bound)

        written = {name for tag in soup.find_all(class_=True) for name in tag["class"]}
        assert not written & {"tab-pane", "active"}

    def test_a_single_tab_is_drawn_and_checked(self, draw_layout):
        soup = draw_layout(TabHolder(Tab("Only", "first")))

        assert labels_of(checked(soup)) == ["Only"]

    def test_a_name_holding_markup_is_escaped_in_the_radios_name(self, draw_layout):
        soup = draw_layout(TabHolder(Tab("<b>Bold</b> & more", "first")))

        assert radios(soup)[0]["aria-label"] == "<b>Bold</b> & more"
        assert soup.find("b") is None

    def test_a_lazily_translated_name_is_drawn(self, draw_layout):
        name = gettext_lazy("Details")

        soup = draw_layout(TabHolder(Tab(name, "first")))

        assert radios(soup)[0]["aria-label"] == str(name)

    def test_a_div_inside_a_tab_is_drawn_as_a_div(self, draw_layout):
        soup = draw_layout(TabHolder(Tab("One", Div("first", css_id="box"))))

        box = soup.find("div", id="box")
        assert box.find("input", id="id_first") is not None
        assert box.find_previous_sibling("input", class_="tab") is None
        assert len(radios(soup)) == 1


class TestTabHolderOpenTab:
    def test_unbound_only_the_first_is_checked(self, draw_layout):
        soup = draw_layout(three_tabs())

        assert labels_of(checked(soup)) == ["One"]

    @pytest.mark.parametrize("active", [True, False])
    def test_giving_the_first_tab_active_still_checks_only_the_first(
        self, draw_layout, active
    ):
        soup = draw_layout(
            TabHolder(
                Tab("One", "first", active=active),
                Tab("Two", "second"),
            )
        )

        assert labels_of(checked(soup)) == ["One"]

    def test_the_first_tab_with_an_error_is_checked(self, draw):
        form = StructureForm(data_without("second"), layout=[three_tabs()])

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["Two"]
        assert content_of(checked(soup)[0]).find(id="id_second_error") is not None

    def test_with_errors_in_two_tabs_the_earlier_is_checked(self, draw):
        form = StructureForm(data_without("second", "third"), layout=[three_tabs()])

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["Two"]

    @pytest.mark.parametrize("container", [Row, Fieldset])
    def test_an_error_on_a_field_nested_in_the_tab_checks_that_tab(
        self, draw, container
    ):
        nested = container("second") if container is Row else container("L", "second")
        form = StructureForm(
            data_without("second"),
            layout=[TabHolder(Tab("One", "first"), Tab("Two", nested))],
        )

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["Two"]
        assert content_of(checked(soup)[0]).find(id="id_second_error") is not None

    def test_a_form_wide_error_alone_leaves_the_first_checked(self, draw):
        form = StructureWideErrorForm(FIELDS, layout=[three_tabs()])

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["One"]

    def test_an_error_on_a_hidden_field_checks_the_tab_that_holds_it(self, draw):
        form = StructureHiddenForm(
            FIELDS,
            layout=[TabHolder(Tab("One", "first"), Tab("Two", "second", "token"))],
        )

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["Two"]

    def test_a_tab_holding_only_html_is_not_checked_for_an_error_elsewhere(self, draw):
        form = StructureForm(
            data_without("first"),
            layout=[TabHolder(Tab("Notes", HTML("<p>Notes</p>")), Tab("One", "first"))],
        )

        soup = draw("{% crispy form %}", form=form)

        assert labels_of(checked(soup)) == ["One"]
        assert labels_of(radios(soup)) == ["Notes", "One"]

    def test_one_is_checked_per_group_with_a_holder_nested_in_a_tab(self, draw):
        inner = TabHolder(Tab("Inner one", "first"), Tab("Inner two", "second"))
        outer = TabHolder(Tab("Outer one", "third", inner), Tab("Outer two", "fourth"))
        form = StructureForm(layout=[outer])

        soup = draw("{% crispy form %}", form=form)

        by_group = {}
        for radio in radios(soup):
            by_group.setdefault(radio["name"], []).append(radio)
        assert len(by_group) == 2
        for group in by_group.values():
            assert len([radio for radio in group if radio.has_attr("checked")]) == 1

    def test_a_nested_holders_check_does_not_stand_in_for_the_outer_first(self, draw):
        inner = TabHolder(Tab("Inner one", "first"))
        outer = TabHolder(
            Tab("Outer one", inner, active=False), Tab("Outer two", "second")
        )
        form = StructureForm(layout=[outer])

        soup = draw("{% crispy form %}", form=form)

        assert "Outer one" in labels_of(checked(soup))


class TestTabHolderGroupNames:
    def test_the_radios_of_one_holder_share_a_name(self, draw_layout):
        soup = draw_layout(three_tabs())

        assert len({radio["name"] for radio in radios(soup)}) == 1

    def test_two_holders_in_one_form_have_different_names(self, draw_layout):
        soup = draw_layout(
            TabHolder(Tab("One", "first"), Tab("Two", "second")),
            TabHolder(Tab("Three", "third"), Tab("Four", "fourth")),
        )

        names = [radio["name"] for radio in radios(soup)]
        assert names[0] == names[1]
        assert names[2] == names[3]
        assert names[0] != names[2]

    def test_a_holder_in_each_of_two_forms_have_different_names(self, draw):
        first = StructureForm(layout=[TabHolder(Tab("One", "first"))])
        second = StructureForm(layout=[TabHolder(Tab("Two", "second"))])

        soup = draw("{% crispy first %}{% crispy second %}", first=first, second=second)

        one, two = radios(soup)
        assert one["name"] != two["name"]

    def test_a_holder_nested_in_a_tab_has_a_name_of_its_own(self, draw_layout):
        soup = draw_layout(
            TabHolder(
                Tab("Outer", TabHolder(Tab("Inner", "first")), "second"),
                Tab("Outer too", "third"),
            )
        )

        names = {radio["aria-label"]: radio["name"] for radio in radios(soup)}
        assert names["Inner"] != names["Outer"]
        assert names["Outer"] == names["Outer too"]

    @pytest.mark.parametrize("bound", [False, True], ids=["unbound", "invalid"])
    def test_no_radio_keeps_the_placeholder_name(self, draw_layout, bound):
        soup = draw_layout(three_tabs(), bound=bound)

        placeholder = TAB_GROUP_PLACEHOLDER.split('"')[1]
        assert placeholder not in {radio["name"] for radio in radios(soup)}


class TestTabHolderSubmission:
    def test_every_radio_belongs_to_no_form(self, draw_layout):
        soup = draw_layout(three_tabs())

        assert radios(soup)
        for radio in radios(soup):
            assert radio["form"] == ""

    def test_the_named_controls_without_it_are_the_forms_own_controls(
        self, draw_layout
    ):
        soup = draw_layout(three_tabs())

        controls = soup.find_all(["input", "select", "textarea", "button"])
        submitted = {
            control["name"]
            for control in controls
            if control.has_attr("name") and not control.has_attr("form")
        }
        assert submitted == FORM_CONTROLS
