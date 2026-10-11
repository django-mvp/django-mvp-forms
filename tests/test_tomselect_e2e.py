"""The script that starts Tom Select, run in Chrome against pages of the test project."""

from pathlib import Path

import django_tomselect
import pytest
from django.urls import reverse

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
STARTED = "(id) => document.getElementById(id).tomselect !== undefined"
WRAPPERS = "document.querySelectorAll('.ts-wrapper').length"
SELECTS = "document.querySelectorAll('select[data-tom-select]').length"
ENTRIES = "Object.fromEntries(new FormData(document.getElementById('page')))"


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


def pick(page, name, text):
    """Type the text into the control of the field, take the first match, close."""
    field = page.locator(f"#id_{name}-ts-control")
    field.click()
    field.press_sequentially(text)
    page.keyboard.press("Enter")
    page.keyboard.press("Escape")


class TestAControlForEachSelect:
    def test_each_select_a_widget_drew_has_a_control(self, choices_page):
        page = choices_page()

        names = ["id_fruit", "id_cities", "id_marked", "id_off"]

        assert [page.evaluate(STARTED, name) for name in names] == [True] * 4
        assert page.evaluate(WRAPPERS) == page.evaluate(SELECTS)

    def test_no_request_is_made_for_options(self, choices_page, requests_made):
        page = choices_page()
        pick(page, "fruit", "Apple")

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

        assert page.locator("#id_cities-ts-dropdown .option").count() == 120

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
        pick(page, "fruit", "Apple")
        pick(page, "fruit", "Banana")

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


def choose(page, name, value):
    """Open the control of a single field and click the option with the value."""
    page.locator(f"#id_{name} + .ts-wrapper .ts-control").click()
    page.locator(f'#id_{name}-ts-dropdown .option[data-value="{value}"]').click()


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
