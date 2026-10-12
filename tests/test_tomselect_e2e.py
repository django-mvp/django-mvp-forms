"""The script that starts Tom Select, run in Chrome against pages of the test project."""

import re
from pathlib import Path

import django_tomselect
import pytest
from django.urls import reverse
from playwright.sync_api import expect

from tests.urls import DJANGO_TOMSELECT_URL, TOM_SELECT_URL

pytestmark = pytest.mark.e2e

TOM_SELECT = Path(__file__).parent / "data" / "tom-select-2.5.2.complete.min.js"
DJANGO_TOMSELECT = (
    Path(django_tomselect.__file__).parent
    / "static"
    / "django_tomselect"
    / "js"
    / "django-tomselect.min.js"
)
README = Path(__file__).parents[1] / "README.md"
STARTED = "(id) => document.getElementById(id).tomselect !== undefined"
WRAPPERS = "document.querySelectorAll('.ts-wrapper').length"
SELECTS = "document.querySelectorAll('select[data-tom-select]').length"
ENTRIES = "Object.fromEntries(new FormData(document.getElementById('page')))"
OPTIONS_OF = "(id) => Object.keys(document.getElementById(id).tomselect.options)"
# A select a widget would draw, added on its own and then inside another element.
INSERT_SELECT = """
(id) => {
  const select = document.createElement("select");
  select.id = id;
  select.name = id;
  select.multiple = true;
  select.dataset.tomSelect = JSON.stringify({ placeholder: "Pick later" });
  select.add(new Option("Apple", "a"));
  select.add(new Option("Banana", "b"));
  return select;
}
"""
ADD_SELECT = INSERT_SELECT.replace(
    "return select;", 'document.getElementById("page").append(select);'
)
# The same select, its attribute holding a setting the script does not read.
ADD_CREATING_SELECT = ADD_SELECT.replace(
    '{ placeholder: "Pick later" }', '{ create: true, placeholder: "Pick later" }'
)
ADD_WRAPPED_SELECT = INSERT_SELECT.replace(
    "return select;",
    """const holder = document.createElement("div");
  holder.append(select);
  document.getElementById("page").append(holder);""",
)
# What the script of django-mvp does with a formset's empty form: replace the
# prefix in the markup of the template and insert the result.
ADD_ROW = """
(number) => {
  const markup = document.getElementById("line").innerHTML;
  document
    .getElementById("page")
    .insertAdjacentHTML("beforeend", markup.replaceAll("__prefix__", number));
}
"""
MOVE_FRUIT = """
window.held = document.getElementById("id_fruit").tomselect;
const holder = document.createElement("div");
document.getElementById("page").append(holder);
holder.append(document.getElementById("id_fruit"));
"""
# Records each event the script sends, and whether it carries the instance the
# select holds by then.
LISTEN = """
window.heard = [];
document.addEventListener("mvp-forms:tomselect", (event) =>
  window.heard.push({
    id: event.target.id,
    instance: event.detail.tomselect === event.target.tomselect,
    class: event.detail.tomselect instanceof window.TomSelect,
  }));
"""
# A listener that changes one control through a method of its instance.
ADD_AN_OPTION = """
document.addEventListener("mvp-forms:tomselect", (event) => {
  if (event.target.id === "id_fruit") {
    event.detail.tomselect.addOption({ value: "z", text: "Zed" });
  }
});
"""
HEARD_IDS = "window.heard.map((entry) => entry.id)"
SELECT_IDS = (
    "[...document.querySelectorAll('select[data-tom-select]')]"
    ".map((select) => select.id).sort()"
)
IN_TEMPLATE = "(selector) => document.getElementById('line').content.querySelectorAll(selector).length"


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def script_errors(page):
    """The errors the package's script reports to the console, as they arrive."""
    errors = []

    def record(message):
        if message.type == "error" and message.location["url"].endswith("tomselect.js"):
            errors.append(message.text)

    page.on("console", record)
    return errors


@pytest.fixture
def requests_made(page):
    """The requests the page makes for data, as they leave."""
    requests = []

    def record(request):
        if request.resource_type in {"fetch", "xhr"}:
            requests.append(request)

    page.on("request", record)
    return requests


@pytest.fixture
def choices_page(page, page_errors, live_server):
    """Open a page of the test project, with Tom Select answered from files."""
    page.route(
        TOM_SELECT_URL,
        lambda route: route.fulfill(path=TOM_SELECT, content_type="text/javascript"),
    )
    page.route(
        f"**{DJANGO_TOMSELECT_URL}",
        lambda route: route.fulfill(
            path=DJANGO_TOMSELECT, content_type="text/javascript"
        ),
    )

    def open_page(name="choices-page", **initial):
        query = "&".join(f"{key}={value}" for key, value in initial.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def choose(page, name, value):
    """Open the control of a single field and click the option with the value."""
    page.locator(f"#id_{name} + .ts-wrapper .ts-control").click()
    page.locator(f'#id_{name}-ts-dropdown .option[data-value="{value}"]').click()


class TestAControlForEachSelect:
    def test_each_select_a_widget_drew_has_a_control(self, choices_page):
        page = choices_page()

        names = ["id_fruit", "id_cities", "id_marked", "id_off"]

        assert [page.evaluate(STARTED, name) for name in names] == [True] * 4
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)

    def test_no_request_is_made_for_options(self, choices_page, requests_made):
        page = choices_page()
        choose(page, "fruit", "a")

        assert requests_made == []

    def test_a_select_a_widget_did_not_draw_gets_no_control(self, choices_page):
        page = choices_page()

        assert page.evaluate(STARTED, "id_plain") is False
        assert page.locator("#id_plain").is_visible()

    def test_a_select_django_tomselect_drew_is_left_alone(self, choices_page):
        page = choices_page("choices-page-foreign")

        assert page.evaluate(STARTED, "id_country") is False
        assert page.evaluate(STARTED, "id_fruit") is True

    def test_a_page_that_loads_django_tomselects_script_alone_starts_the_control(
        self, choices_page
    ):
        page = choices_page("choices-page-django-tomselect")

        assert page.evaluate(STARTED, "id_fruit") is True

    def test_a_page_with_a_strict_policy_starts_the_control(
        self, choices_page, page_errors
    ):
        page = choices_page("choices-page-strict")

        assert page.evaluate(STARTED, "id_fruit") is True
        assert page_errors == []


class TestWhatTheControlHolds:
    def test_every_option_of_a_long_list_is_reachable_by_typing(self, choices_page):
        page = choices_page()
        field = page.locator("#id_cities-ts-control")

        field.click()
        field.press_sequentially("city")

        expect(page.locator("#id_cities-ts-dropdown .option")).to_have_count(120)

    def test_initial_values_are_held_when_the_control_starts(self, choices_page):
        page = choices_page(fruit="b")

        held = page.evaluate("document.getElementById('id_fruit').tomselect.items")

        assert held == ["b"]

    def test_a_label_holding_markup_is_shown_as_text(self, choices_page):
        page = choices_page()
        field = page.locator("#id_marked-ts-control")
        field.click()

        listed = page.locator("#id_marked-ts-dropdown .option")

        assert listed.inner_text() == "<b>Bold</b> & Tom"
        assert listed.locator("b").count() == 0
        listed.click()
        shown = page.locator("#id_marked + .ts-wrapper .item")
        assert shown.inner_text() == "<b>Bold</b> & Tom"
        assert shown.locator("b").count() == 0


class TestTheFormsFields:
    def test_two_chosen_values_are_sent_under_the_fields_name(self, choices_page):
        page = choices_page()
        choose(page, "fruit", "a")
        page.keyboard.press("Escape")
        choose(page, "fruit", "b")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"fruit": ["a", "b"]' in page.inner_text("body")

    def test_a_disabled_field_has_a_disabled_control(self, choices_page):
        page = choices_page()

        assert page.locator("#id_off-ts-control").is_disabled()

    def test_activating_the_label_moves_focus_into_the_control(self, choices_page):
        page = choices_page()

        page.click("label[for=id_fruit-ts-control]")

        assert page.evaluate("document.activeElement.id") == "id_fruit-ts-control"

    def test_the_element_that_takes_focus_names_the_help_text(self, choices_page):
        page = choices_page()

        described = page.locator("#id_fruit-ts-control").get_attribute(
            "aria-describedby"
        )

        assert "id_fruit_helptext" in described.split()


class TestTheSingleWidget:
    def test_each_select_the_widget_drew_has_a_control(self, choices_page):
        page = choices_page()

        assert page.evaluate(STARTED, "id_single") is True
        assert page.evaluate(STARTED, "id_optional") is True

    def test_picking_an_option_sends_that_one_value(self, choices_page):
        page = choices_page()
        choose(page, "single", "b")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"single": ["b"]' in page.inner_text("body")

    def test_picking_another_option_replaces_the_first(self, choices_page):
        page = choices_page()
        choose(page, "single", "b")
        choose(page, "single", "c")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"single": ["c"]' in page.inner_text("body")

    def test_an_optional_field_is_returned_to_no_value_from_the_keyboard(
        self, choices_page
    ):
        page = choices_page(optional="a")
        assert page.evaluate(STARTED, "id_optional") is True
        assert page.evaluate("document.getElementById('id_optional').value") == "a"

        page.locator("#id_optional-ts-control").focus()
        page.keyboard.press("Backspace")
        page.keyboard.press("Escape")

        with page.expect_navigation():
            page.click("button[type=submit]")
        assert '"optional": [""]' in page.inner_text("body")


class TestAPageWithoutTomSelect:
    def test_nothing_is_started_and_the_form_submits_the_stock_values(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page("choices-page-bare")
        page.select_option("#id_fruit", ["a", "b"])

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"fruit": ["a", "b"]' in page.inner_text("body")
        assert page_errors == []
        assert script_errors == []


class TestOneControlForEachSelect:
    def test_every_select_has_one_control_when_the_script_is_on_the_page_three_times(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page("choices-page-copies")

        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)
        assert page_errors == []
        assert script_errors == []


class TestASelectTomSelectRefuses:
    def test_it_is_left_as_it_is_and_the_next_is_still_started(
        self, choices_page, page_errors
    ):
        page = choices_page("choices-page-refused")

        assert page.locator("#id_refused + .ts-wrapper").count() == 0
        assert page.locator("#id_refused").is_visible()
        assert page.evaluate(STARTED, "id_fruit") is True
        assert page_errors == []


class TestTheSettings:
    def test_the_placeholder_is_the_controls_placeholder_while_it_is_empty(
        self, choices_page
    ):
        page = choices_page()

        multiple = page.locator("#id_placeheld-ts-control").get_attribute("placeholder")
        single = page.locator("#id_placeheld_single-ts-control").get_attribute(
            "placeholder"
        )

        assert multiple == "Pick fruit"
        assert single == "Pick one fruit"

    def test_the_clear_button_empties_a_control_holding_values(self, choices_page):
        page = choices_page(clearable="a")
        items = "document.getElementById('id_clearable').tomselect.items"
        assert page.evaluate(items) == ["a"]

        page.locator("#id_clearable + .ts-wrapper .clear-button").click()

        assert page.evaluate(items) == []

    def test_the_clear_button_empties_a_single_control(self, choices_page):
        page = choices_page(clearable_single="b")
        items = "document.getElementById('id_clearable_single').tomselect.items"
        assert page.evaluate(items) == ["b"]

        page.locator("#id_clearable_single + .ts-wrapper .clear-button").click()

        assert page.evaluate(items) == []

    def test_a_remove_button_removes_its_own_value_alone(self, choices_page):
        page = choices_page()
        choose(page, "removable", "a")
        page.keyboard.press("Escape")
        choose(page, "removable", "b")
        items = "document.getElementById('id_removable').tomselect.items"
        assert page.evaluate(items) == ["a", "b"]

        page.locator(
            '#id_removable + .ts-wrapper .item[data-value="a"] .remove'
        ).click()

        assert page.evaluate(items) == ["b"]

    def test_no_more_than_the_largest_number_of_values_can_be_chosen(
        self, choices_page
    ):
        page = choices_page()
        items = "document.getElementById('id_limited').tomselect.items"
        option = '#id_limited-ts-dropdown .option[data-value="{}"]'
        page.locator("#id_limited + .ts-wrapper .ts-control").click()
        page.locator(option.format("a")).click()
        page.locator(option.format("b")).click()

        assert page.evaluate(items) == ["a", "b"]
        assert not page.locator(option.format("c")).is_visible()

        page.keyboard.press("Backspace")
        page.locator("#id_limited-ts-control").click()
        page.locator(option.format("c")).click()

        assert page.evaluate(items) == ["a", "c"]


class TestGroupsAndUnavailableOptions:
    def test_an_option_is_listed_under_the_heading_of_its_group(self, choices_page):
        page = choices_page()
        page.locator("#id_grouped + .ts-wrapper .ts-control").click()

        listed = page.locator("#id_grouped-ts-dropdown .optgroup").evaluate_all(
            """(groups) => groups.map((group) => [
                group.querySelector('.optgroup-header').textContent,
                [...group.querySelectorAll('.option')].map((o) => o.textContent),
            ])"""
        )

        assert listed == [["Fruit", ["Apple", "Banana"]], ["Vegetable", ["Carrot"]]]

    def test_an_option_drawn_disabled_is_listed_and_cannot_be_chosen(
        self, choices_page
    ):
        page = choices_page()
        items = "document.getElementById('id_unavailable').tomselect.items"
        page.locator("#id_unavailable + .ts-wrapper .ts-control").click()
        dropdown = page.locator("#id_unavailable-ts-dropdown")

        assert dropdown.locator('.option[data-value="b"]').inner_text() == "Banana"
        dropdown.locator('.option[data-value="b"]').click(force=True)

        assert page.evaluate(items) == []
        dropdown.locator('.option[data-value="a"]').click()
        assert page.evaluate(items) == ["a"]


class TestSelectsAddedAfterThePageLoads:
    def test_a_select_added_on_its_own_gets_one_control(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page()
        before = page.evaluate(WRAPPERS)

        page.evaluate(ADD_SELECT, "id_later")

        assert page.evaluate(STARTED, "id_later") is True
        assert page.evaluate(WRAPPERS) == before + 1
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)
        assert page_errors == []
        assert script_errors == []

    def test_a_select_added_inside_another_element_gets_one_control(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page()
        before = page.evaluate(WRAPPERS)

        page.evaluate(ADD_WRAPPED_SELECT, "id_later")

        assert page.evaluate(STARTED, "id_later") is True
        assert page.evaluate(WRAPPERS) == before + 1
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)
        assert page_errors == []
        assert script_errors == []

    def test_a_late_control_has_the_selects_settings_and_submits_its_value(
        self, choices_page
    ):
        page = choices_page()
        page.evaluate(ADD_SELECT, "id_later")

        placeholder = page.locator("#id_later-ts-control").get_attribute("placeholder")
        choose(page, "later", "b")
        page.keyboard.press("Escape")
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert placeholder == "Pick later"
        assert '"id_later": ["b"]' in page.inner_text("body")

    def test_a_setting_the_script_does_not_read_is_left_off(self, choices_page):
        page = choices_page()
        page.evaluate(ADD_CREATING_SELECT, "id_later")

        settings = page.evaluate(
            "document.getElementById('id_later').tomselect.settings"
        )

        assert not settings["create"]
        assert settings["placeholder"] == "Pick later"

    def test_a_late_control_is_tied_to_the_help_text_of_its_select(self, choices_page):
        page = choices_page()
        page.evaluate(ADD_ROW, "2")

        described = page.locator("#id_form-2-fruit-ts-control").get_attribute(
            "aria-describedby"
        )

        assert "id_form-2-fruit_helptext" in described.split()


class TestAFormsetRow:
    def test_a_row_made_from_the_empty_form_holds_one_working_control(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page()
        before = page.evaluate(WRAPPERS)

        page.evaluate(ADD_ROW, "2")

        assert page.evaluate(STARTED, "id_form-2-fruit") is True
        assert page.evaluate(WRAPPERS) == before + 1
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)
        assert page.evaluate(OPTIONS_OF, "id_form-2-fruit") == ["a", "b"]
        placeholder = page.locator("#id_form-2-fruit-ts-control").get_attribute(
            "placeholder"
        )
        assert placeholder == "Pick fruit"
        assert page_errors == []
        assert script_errors == []

    def test_a_value_chosen_in_the_row_is_sent_under_the_name_of_the_row(
        self, choices_page
    ):
        page = choices_page()
        page.evaluate(ADD_ROW, "2")
        choose(page, "form-2-fruit", "a")
        page.keyboard.press("Escape")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"form-2-fruit": ["a"]' in page.inner_text("body")

    def test_the_select_inside_the_template_is_never_started(self, choices_page):
        page = choices_page()
        page.evaluate(ADD_ROW, "2")

        assert page.evaluate(IN_TEMPLATE, "select[data-tom-select]") == 1
        assert page.evaluate(IN_TEMPLATE, ".ts-wrapper") == 0
        started = (
            "document.getElementById('line').content.querySelector('select').tomselect"
        )
        assert page.evaluate(started) is None

    def test_a_row_has_one_control_when_the_script_is_on_the_page_three_times(
        self, choices_page, page_errors, script_errors
    ):
        page = choices_page("choices-page-copies")

        page.evaluate(ADD_ROW, "2")

        assert page.evaluate(STARTED, "id_form-2-fruit") is True
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)
        assert page_errors == []
        assert script_errors == []


class TestAMovedSelect:
    def test_it_keeps_its_one_control(self, choices_page, page_errors, script_errors):
        page = choices_page()
        before = page.evaluate(WRAPPERS)

        page.evaluate(MOVE_FRUIT)

        assert page.evaluate(
            "document.getElementById('id_fruit').tomselect === window.held"
        )
        assert page.evaluate(WRAPPERS) == before
        assert page_errors == []
        assert script_errors == []


class TestAControlInAModal:
    def test_it_is_started_while_the_modal_is_closed(self, choices_page):
        page = choices_page()

        assert page.evaluate(STARTED, "id_nearby") is True

    def test_it_works_when_the_modal_is_opened(self, choices_page):
        page = choices_page()
        page.evaluate("document.getElementById('nearby-dialog').showModal()")

        choose(page, "nearby", "b")

        items = "document.getElementById('id_nearby').tomselect.items"
        assert page.evaluate(items) == ["b"]


class TestTheEvent:
    def test_each_select_sends_it_once_with_the_instance_it_holds(
        self, page, choices_page
    ):
        page.add_init_script(LISTEN)
        page = choices_page()

        heard = page.evaluate("window.heard")

        assert sorted(entry["id"] for entry in heard) == page.evaluate(SELECT_IDS)
        assert all(entry["instance"] and entry["class"] for entry in heard)

    def test_it_is_sent_once_when_the_script_is_on_the_page_three_times(
        self, page, choices_page
    ):
        page.add_init_script(LISTEN)
        page = choices_page("choices-page-copies")

        heard = page.evaluate("window.heard")

        assert sorted(entry["id"] for entry in heard) == page.evaluate(SELECT_IDS)

    def test_it_is_sent_from_a_select_added_later(self, page, choices_page):
        page.add_init_script(LISTEN)
        page = choices_page()
        before = page.evaluate("window.heard.length")

        page.evaluate(ADD_SELECT, "id_later")

        heard = page.evaluate("window.heard")
        assert [entry["id"] for entry in heard[before:]] == ["id_later"]
        assert heard[-1]["instance"] and heard[-1]["class"]

    def test_it_is_sent_from_the_select_of_a_row_added_later(self, page, choices_page):
        page.add_init_script(LISTEN)
        page = choices_page()
        before = page.evaluate("window.heard.length")

        page.evaluate(ADD_ROW, "2")

        heard = page.evaluate("window.heard")
        assert [entry["id"] for entry in heard[before:]] == ["id_form-2-fruit"]

    def test_it_is_not_sent_again_for_a_select_that_is_moved(self, page, choices_page):
        page.add_init_script(LISTEN)
        page = choices_page()
        before = page.evaluate("window.heard.length")

        page.evaluate(MOVE_FRUIT)

        assert page.evaluate("window.heard.length") == before

    def test_it_is_not_sent_for_a_select_tom_select_refused(self, page, choices_page):
        page.add_init_script(LISTEN)
        page = choices_page("choices-page-refused")

        heard = page.evaluate(HEARD_IDS)

        assert "id_refused" not in heard
        assert "id_fruit" in heard

    def test_a_listener_that_calls_a_method_of_the_instance_changes_the_control(
        self, page, choices_page
    ):
        page.add_init_script(ADD_AN_OPTION)
        page = choices_page()

        assert page.evaluate(OPTIONS_OF, "id_fruit") == ["a", "b", "z"]
        choose(page, "fruit", "z")
        items = "document.getElementById('id_fruit').tomselect.items"
        assert page.evaluate(items) == ["z"]

    def test_the_readmes_listener_changes_the_control_it_names(
        self, page, choices_page
    ):
        widgets = re.search(
            r"^### Tom Select widgets$(.*?)^### ", README.read_text(), re.M | re.S
        ).group(1)
        section = re.search(r"^#### The event$(.*?)^#", widgets, re.M | re.S).group(1)
        source = re.search(r"```js\n(.*?)```", section, re.S).group(1)
        source = source.replace("id_topics", "id_fruit").replace("geology", "a")
        page.add_init_script(source)
        page = choices_page()

        items = "document.getElementById('id_fruit').tomselect.items"
        assert page.evaluate(items) == ["a"]
