"""The layout object that shows part of a form in a modal."""

from crispy_forms.bootstrap import Accordion, AccordionGroup, Modal, Tab, TabHolder
from crispy_forms.layout import HTML, Div

from tests.forms import StructureForm

DEVELOPER_ATTRS = {"data-role": "dialog-box", "lang": "en"}
FIELDS = {"first": "a", "second": "b", "third": "c", "fourth": "d"}
FORM_CONTROLS = {*FIELDS, "csrfmiddlewaretoken"}


def one_modal(**kwargs):
    return Modal("first", "second", css_id="box", title="Details", **kwargs)


def data_without(*names):
    return {name: value for name, value in FIELDS.items() if name not in names}


def dialogs(soup):
    return soup.find_all("dialog")


def opened(soup):
    return [dialog for dialog in dialogs(soup) if dialog.has_attr("open")]


class TestModal:
    def test_it_draws_one_dialog_with_the_id_it_was_given(self, draw_layout):
        soup = draw_layout(one_modal())

        assert [dialog["id"] for dialog in dialogs(soup)] == ["box"]
        assert "modal" in dialogs(soup)[0]["class"]

    def test_the_dialog_holds_its_fields_inside_a_modal_box(self, draw_layout):
        soup = draw_layout(one_modal(), "third")

        box = soup.find("dialog", id="box").find(class_="modal-box")
        assert [tag["id"] for tag in box.find_all("input")] == [
            "id_first",
            "id_second",
        ]
        assert soup.find("input", id="id_third").find_parent("dialog") is None

    def test_unbound_the_dialog_is_closed(self, draw_layout):
        soup = draw_layout(one_modal())

        assert not soup.find("dialog").has_attr("open")

    def test_the_title_names_the_dialog(self, draw_layout):
        soup = draw_layout(one_modal(title_id="heading"))

        dialog = soup.find("dialog")
        title = dialog.find(id=dialog["aria-labelledby"])
        assert title is not None
        assert title.get_text() == "Details"

    def test_a_title_holding_markup_is_escaped(self, draw_layout):
        soup = draw_layout(Modal("first", css_id="box", title="<b>Bold</b> & more"))

        dialog = soup.find("dialog")
        assert dialog.find(id=dialog["aria-labelledby"]).get_text() == (
            "<b>Bold</b> & more"
        )
        assert dialog.find("b") is None

    def test_the_dialog_holds_one_button_and_it_is_not_a_submit(self, draw_layout):
        soup = draw_layout(one_modal())

        dialog = soup.find("dialog")
        buttons = dialog.find_all("button")
        assert [button["type"] for button in buttons] == ["button"]
        assert buttons[0].get_text(strip=True)
        assert dialog.find(attrs={"type": "submit"}) is None

    def test_nothing_outside_the_dialog_refers_to_its_id(self, draw_layout):
        soup = draw_layout("third", one_modal())

        outside = [
            tag
            for tag in soup.find_all(True)
            if tag.find_parent("dialog") is None and tag.name != "dialog"
        ]
        for tag in outside:
            assert "box" not in tag.attrs.values()

    def test_a_modal_given_no_id_is_drawn_with_the_one_crispy_forms_made(
        self, draw_layout
    ):
        modal = Modal("first")

        soup = draw_layout(modal)

        assert soup.find("dialog", id=modal.css_id) is not None

    def test_css_class_title_class_title_id_and_attributes_reach_their_elements(
        self, draw_layout
    ):
        soup = draw_layout(
            Modal(
                "first",
                css_id="box",
                css_class="mine other",
                title="Details",
                title_id="heading",
                title_class="large",
                **DEVELOPER_ATTRS,
            )
        )

        dialog = soup.find("dialog", id="box")
        title = soup.find(id=dialog["aria-labelledby"])
        assert {"mine", "other"} <= set(dialog["class"])
        assert dialog["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert dialog["lang"] == DEVELOPER_ATTRS["lang"]
        assert title["class"] == ["large"]
        assert title["id"] == "heading-label"

    def test_a_div_inside_a_modal_is_drawn_as_a_div(self, draw_layout):
        soup = draw_layout(Modal(Div("first", css_id="inner"), css_id="box"))

        inner = soup.find("div", id="inner")
        assert inner.find("input", id="id_first") is not None
        assert inner.find_parent("dialog", id="box") is not None


class TestModalInsideTheForm:
    def test_the_modals_fields_are_inside_the_form_element(self, draw):
        form = StructureForm(layout=[one_modal(), "third"])
        form.helper.form_tag = True

        soup = draw("{% crispy form %}", form=form)

        form_tag = soup.find("form")
        assert form_tag.find("dialog", id="box") is not None
        assert form_tag.find("input", id="id_first").find_parent("dialog")

    def test_the_controls_in_the_form_are_the_forms_own_controls(self, draw_layout):
        soup = draw_layout(one_modal(), "third", "fourth")

        controls = soup.find_all(["input", "select", "textarea", "button"])
        named = {control["name"] for control in controls if control.has_attr("name")}
        assert named == FORM_CONTROLS


class TestModalOpensForAnError:
    def test_an_error_in_a_field_of_the_modal_opens_it_with_the_error_inside(
        self, draw
    ):
        form = StructureForm(data_without("second"), layout=[one_modal(), "third"])

        soup = draw("{% crispy form %}", form=form)

        assert [dialog["id"] for dialog in opened(soup)] == ["box"]
        assert opened(soup)[0].find(id="id_second_error") is not None

    def test_an_error_only_outside_the_modal_leaves_it_closed(self, draw):
        form = StructureForm(data_without("third"), layout=[one_modal(), "third"])

        soup = draw("{% crispy form %}", form=form)

        assert dialogs(soup)
        assert opened(soup) == []

    def test_a_modal_opened_for_an_error_takes_the_focus(self, draw_layout):
        soup = draw_layout("first", Modal("second", css_id="box"), bound=True)

        assert soup.find("dialog", id="box").has_attr("autofocus")

    def test_a_closed_modal_does_not_take_the_focus(self, draw_layout):
        soup = draw_layout("first", Modal("second", css_id="box"))

        assert not soup.find("dialog", id="box").has_attr("autofocus")

    def test_it_opens_when_the_helper_does_not_show_errors(self, draw):
        form = StructureForm(data_without("second"), layout=[one_modal()])
        form.helper.form_show_errors = False

        soup = draw("{% crispy form %}", form=form)

        assert [dialog["id"] for dialog in opened(soup)] == ["box"]

    def test_a_modal_holding_only_html_never_opens(self, draw):
        form = StructureForm(
            {},
            layout=[Modal(HTML("<p id='note'>Notes</p>"), css_id="box"), "first"],
        )

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("dialog").find("p", id="note") is not None
        assert opened(soup) == []

    def test_a_valid_field_whose_value_is_the_invalid_mark_does_not_open_it(self, draw):
        form = StructureForm(
            {**FIELDS, "first": 'aria-invalid="true"'}, layout=[one_modal()]
        )

        soup = draw("{% crispy form %}", form=form)

        assert dialogs(soup)
        assert opened(soup) == []

    def test_two_modals_are_both_drawn_and_an_error_opens_only_its_own(self, draw):
        form = StructureForm(
            data_without("third"),
            layout=[
                Modal("first", "second", css_id="one"),
                Modal("third", "fourth", css_id="two"),
            ],
        )

        soup = draw("{% crispy form %}", form=form)

        assert [dialog["id"] for dialog in dialogs(soup)] == ["one", "two"]
        assert [dialog["id"] for dialog in opened(soup)] == ["two"]

    def test_an_error_in_a_group_in_a_tab_in_a_modal_opens_all_three(self, draw):
        layout = Modal(
            TabHolder(
                Tab("Plain", "first"),
                Tab(
                    "Nested",
                    Accordion(
                        AccordionGroup("One", "second"),
                        AccordionGroup("Two", "third"),
                    ),
                ),
            ),
            css_id="box",
        )
        form = StructureForm(data_without("third"), layout=[layout])

        soup = draw("{% crispy form %}", form=form)

        dialog = soup.find("dialog", id="box")
        radios = dialog.find_all("input", class_="tab")
        checked = [radio["aria-label"] for radio in radios if radio.has_attr("checked")]
        groups = [
            group for group in dialog.find_all("details") if group.has_attr("open")
        ]
        assert dialog.has_attr("open")
        assert checked == ["Nested"]
        assert [group.find("summary").get_text() for group in groups] == ["Two"]
