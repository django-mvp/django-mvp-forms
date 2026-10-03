"""The layout objects that group fields in an accordion: an accordion and its groups."""

from crispy_forms.bootstrap import Accordion, AccordionGroup, Tab, TabHolder
from crispy_forms.layout import HTML, Div
from django.utils.translation import gettext_lazy

from tests.forms import (
    StructureForm,
    StructureHiddenForm,
    StructureWideErrorForm,
)

DEVELOPER_CLASSES = ["mine", "other"]
DEVELOPER_ATTRS = {"data-role": "group", "title": "Group"}
FIELDS = {"first": "a", "second": "b", "third": "c", "fourth": "d"}
FORM_CONTROLS = {*FIELDS, "csrfmiddlewaretoken"}


def three_groups():
    return Accordion(
        AccordionGroup("One", "first", css_id="one"),
        AccordionGroup("Two", "second", css_id="two"),
        AccordionGroup("Three", "third", "fourth", css_id="three"),
        css_id="holder",
    )


def data_without(*names):
    return {name: value for name, value in FIELDS.items() if name not in names}


def groups(soup):
    return soup.find_all("details")


def names_of(details):
    return [group.find("summary").get_text() for group in details]


def opened(soup):
    return [group for group in groups(soup) if group.has_attr("open")]


class TestAccordion:
    def test_it_draws_one_element_holding_every_group_in_order(self, draw_layout):
        soup = draw_layout(three_groups())

        holder = soup.find("div", id="holder")
        assert groups(holder) == groups(soup)
        assert names_of(groups(holder)) == ["One", "Two", "Three"]

    def test_each_group_is_a_collapse_with_a_title_and_content(self, draw_layout):
        soup = draw_layout(three_groups())

        for group in groups(soup):
            assert "collapse" in group["class"]
            assert "collapse-title" in group.find("summary")["class"]
            assert group.find("div", class_="collapse-content") is not None

    def test_each_group_holds_its_own_fields(self, draw_layout):
        soup = draw_layout(three_groups())

        fields = [
            [tag["id"] for tag in group.find_all("input")] for group in groups(soup)
        ]
        assert fields == [["id_first"], ["id_second"], ["id_third", "id_fourth"]]

    def test_the_accordion_and_each_group_carry_what_they_were_given(self, draw_layout):
        soup = draw_layout(
            Accordion(
                AccordionGroup(
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
        group = soup.find("details", id="one")
        assert "mine" in holder["class"]
        assert set(DEVELOPER_CLASSES) <= set(group["class"])
        for element in (holder, group):
            assert element["data-role"] == DEVELOPER_ATTRS["data-role"]
            assert element["title"] == DEVELOPER_ATTRS["title"]

    def test_an_accordion_given_no_id_is_drawn_with_the_one_crispy_forms_made(
        self, draw_layout
    ):
        accordion = Accordion(AccordionGroup("One", "first"))

        soup = draw_layout(accordion)

        holder = soup.find("div", id=accordion.css_id)
        assert groups(holder) == groups(soup)

    def test_a_single_group_is_drawn_open(self, draw_layout):
        soup = draw_layout(Accordion(AccordionGroup("Only", "first")))

        assert names_of(opened(soup)) == ["Only"]

    def test_a_name_holding_markup_is_escaped(self, draw_layout):
        soup = draw_layout(Accordion(AccordionGroup("<b>Bold</b> & more", "first")))

        assert names_of(groups(soup)) == ["<b>Bold</b> & more"]
        assert soup.find("b") is None

    def test_a_lazily_translated_name_is_drawn(self, draw_layout):
        name = gettext_lazy("Details")

        soup = draw_layout(Accordion(AccordionGroup(name, "first")))

        assert names_of(groups(soup)) == [str(name)]

    def test_a_group_holding_only_html_is_drawn(self, draw_layout):
        soup = draw_layout(
            Accordion(AccordionGroup("Notes", HTML("<p id='note'>Notes</p>")))
        )

        assert groups(soup)[0].find("p", id="note") is not None

    def test_a_div_inside_a_group_is_drawn_as_a_div(self, draw_layout):
        soup = draw_layout(Accordion(AccordionGroup("One", Div("first", css_id="box"))))

        box = soup.find("div", id="box")
        assert box.find("input", id="id_first") is not None
        assert box.find_parent("details") is not None
        assert len(groups(soup)) == 1


class TestAccordionOpenGroup:
    def test_unbound_only_the_first_is_open(self, draw_layout):
        soup = draw_layout(three_groups())

        assert names_of(opened(soup)) == ["One"]

    def test_active_on_a_later_group_opens_it_as_well(self, draw_layout):
        soup = draw_layout(
            Accordion(
                AccordionGroup("One", "first"),
                AccordionGroup("Two", "second", active=True),
                AccordionGroup("Three", "third"),
            )
        )

        assert names_of(opened(soup)) == ["One", "Two"]

    def test_active_false_on_the_first_group_keeps_it_closed(self, draw_layout):
        soup = draw_layout(
            Accordion(
                AccordionGroup("One", "first", active=False),
                AccordionGroup("Two", "second"),
            )
        )

        assert opened(soup) == []

    def test_the_first_group_with_an_error_is_open_with_the_error_inside(self, draw):
        form = StructureForm(data_without("second"), layout=[three_groups()])

        soup = draw("{% crispy form %}", form=form)

        assert names_of(opened(soup)) == ["Two"]
        assert opened(soup)[0].find(id="id_second_error") is not None

    def test_with_errors_in_two_groups_the_earlier_is_open(self, draw):
        form = StructureForm(data_without("second", "third"), layout=[three_groups()])

        soup = draw("{% crispy form %}", form=form)

        assert names_of(opened(soup)) == ["Two"]

    def test_a_form_wide_error_alone_leaves_the_first_open(self, draw):
        form = StructureWideErrorForm(FIELDS, layout=[three_groups()])

        soup = draw("{% crispy form %}", form=form)

        assert names_of(opened(soup)) == ["One"]

    def test_an_error_on_a_hidden_field_opens_the_group_that_holds_it(self, draw):
        form = StructureHiddenForm(
            FIELDS,
            layout=[
                Accordion(
                    AccordionGroup("One", "first"),
                    AccordionGroup("Two", "second", "token"),
                )
            ],
        )

        soup = draw("{% crispy form %}", form=form)

        assert names_of(opened(soup)) == ["Two"]

    def test_an_accordion_inside_a_tab_opens_both_for_an_error_in_a_group(self, draw):
        accordion = Accordion(
            AccordionGroup("One", "first"), AccordionGroup("Two", "second")
        )
        form = StructureForm(
            data_without("second"),
            layout=[TabHolder(Tab("Plain", "third"), Tab("Nested", accordion))],
        )

        soup = draw("{% crispy form %}", form=form)

        radios = soup.find_all("input", class_="tab")
        checked = [radio["aria-label"] for radio in radios if radio.has_attr("checked")]
        assert checked == ["Nested"]
        assert names_of(opened(soup)) == ["Two"]


class TestAccordionGroupNames:
    def test_no_group_carries_a_name(self, draw_layout):
        soup = draw_layout(three_groups())

        assert groups(soup)
        for group in groups(soup):
            assert not group.has_attr("name")

    def test_two_accordions_have_different_ids(self, draw_layout):
        soup = draw_layout(
            Accordion(AccordionGroup("One", "first")),
            Accordion(AccordionGroup("Two", "second")),
        )

        ids = [
            holder["id"]
            for holder in soup.find_all("div", id=True)
            if holder.find("details") and not holder.find_parent("details")
        ]
        assert len(ids) == 2
        assert ids[0] != ids[1]


class TestAccordionSubmission:
    def test_the_controls_in_the_form_are_the_forms_own_controls(self, draw_layout):
        soup = draw_layout(three_groups())

        controls = soup.find_all(["input", "select", "textarea", "button"])
        assert {control["name"] for control in controls} == FORM_CONTROLS

    def test_the_accordion_draws_no_control_of_its_own(self, draw_layout):
        soup = draw_layout(three_groups())

        holder = soup.find("div", id="holder")
        for summary in holder.find_all("summary"):
            assert summary.find(["input", "select", "textarea", "button"]) is None
        assert len(holder.find_all("input")) == len(FIELDS)
        assert holder.find(["select", "textarea", "button"]) is None
