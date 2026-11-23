"""The choice widgets and their fold script, driven in headless Chrome."""

import json
import re

import pytest
from django.urls import reverse
from playwright.sync_api import expect

from tests.urls import HTMX_URL

pytestmark = pytest.mark.e2e

HTMX = "tests/data/htmx-2.0.10.min.js"
SINGLE = ["scale", "pill", "chip", "card"]
MULTIPLE = ["pills", "chips", "cards"]
ACTIVE = "document.activeElement"
INSERT_LINE = """
document.getElementById("lines").append(
  document.getElementById("line").content.cloneNode(true));
"""


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def choice_page(page, page_errors, live_server):
    """Open a page of the test project that holds every choice widget."""

    def open_page(name="choice-widgets", **entries):
        page.route(
            HTMX_URL,
            lambda route: route.fulfill(path=HTMX, content_type="text/javascript"),
        )
        query = "&".join(f"{key}={value}" for key, value in entries.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def option(page, field, value):
    """Return the input of one choice of a field."""
    return page.locator(f'[name="{field}"][value="{value}"]')


def more_of(page, field):
    """Return the button that shows the folded choices of a field."""
    return page.locator(f"#id_{field} [data-choice-more]")


def tap(page, field, value):
    """Tap a choice, showing the field's folded choices first when it is one."""
    target = option(page, field, value)
    if not target.is_visible() and more_of(page, field).count():
        more_of(page, field).click()
    target.click()


def checked(page, field):
    """Return the values chosen in a field, in the order drawn."""
    return page.locator(f'[name="{field}"]').evaluate_all(
        "(nodes) => nodes.filter((node) => node.checked).map((node) => node.value)"
    )


def tab_to(page, selector, limit=60):
    """Press Tab until the focus is on an input matching the selector."""
    page.evaluate("document.body.focus()")
    for _ in range(limit):
        page.keyboard.press("Tab")
        if page.evaluate(f"{ACTIVE}.matches({json.dumps(selector)})"):
            return
    raise AssertionError(f"Tab never reached {selector}")


def send(page, **chosen):
    """Choose the required choices, send the form and return what it answered."""
    option(page, "scale", chosen.get("scale", "1")).click()
    tap(page, "card", chosen.get("card", "1"))
    tap(page, "cards", chosen.get("cards", "1"))
    with page.expect_navigation():
        page.click("button[type=submit]")
    return json.loads(page.inner_text("body"))


class TestTapping:
    def test_tapping_a_scale_choice_chooses_it_and_replaces_the_last(self, choice_page):
        page = choice_page()

        option(page, "scale", "2").click()
        option(page, "scale", "4").click()

        assert checked(page, "scale") == ["4"]

    @pytest.mark.parametrize("field", ["pill", "chip", "card"])
    def test_tapping_a_single_choice_replaces_the_one_chosen(self, choice_page, field):
        page = choice_page()

        tap(page, field, "1")
        tap(page, field, "2")

        assert checked(page, field) == ["2"]

    @pytest.mark.parametrize("field", ["pill", "chip", "card"])
    def test_the_clearing_choice_empties_a_single_choice_field(
        self, choice_page, field
    ):
        page = choice_page()

        tap(page, field, "1")
        option(page, field, "").click()

        assert checked(page, field) == [""]

    @pytest.mark.parametrize("field", ["pills", "cards"])
    def test_tapping_a_chosen_multiple_choice_unticks_it(self, choice_page, field):
        page = choice_page()

        tap(page, field, "1")
        tap(page, field, "2")
        tap(page, field, "1")

        assert checked(page, field) == ["2"]

    def test_tapping_a_chip_in_the_fold_chooses_it(self, choice_page):
        page = choice_page()

        more_of(page, "chips").click()
        option(page, "chips", "3").click()

        assert checked(page, "chips") == ["3"]

    def test_what_was_tapped_is_what_the_form_receives(self, choice_page):
        page = choice_page()

        option(page, "pills", "2").click()
        option(page, "pills", "3").click()
        option(page, "pill", "4").click()
        answer = send(page, scale="3", card="2", cards="1")

        assert answer["entries"]["scale"] == ["3"]
        assert answer["entries"]["pills"] == ["2", "3"]
        assert answer["entries"]["pill"] == ["4"]
        assert answer["entries"]["card"] == ["2"]

    def test_a_cleared_single_choice_is_received_as_empty(self, choice_page):
        page = choice_page()

        option(page, "pill", "2").click()
        option(page, "pill", "").click()
        answer = send(page)

        assert answer["cleaned"]["pill"] == ""


class TestKeyboard:
    @pytest.mark.parametrize("field", SINGLE)
    def test_arrow_keys_choose_the_next_choice_of_a_single_choice_field(
        self, choice_page, field
    ):
        page = choice_page()

        tab_to(page, f'[name="{field}"]')
        page.keyboard.press("ArrowRight")

        assert len(checked(page, field)) == 1
        assert page.evaluate(f"{ACTIVE}.matches(':focus-visible')")

    @pytest.mark.parametrize("field", MULTIPLE)
    def test_space_ticks_and_unticks_a_choice_of_a_multiple_field(
        self, choice_page, field
    ):
        page = choice_page()

        tab_to(page, f'[name="{field}"]')
        page.keyboard.press("Space")

        assert len(checked(page, field)) == 1

        page.keyboard.press("Space")

        assert checked(page, field) == []

    def test_tab_moves_through_the_choices_of_a_multiple_field(self, choice_page):
        page = choice_page()
        first = page.locator('[name="pills"]').first

        tab_to(page, '[name="pills"]')

        assert first.evaluate("(node) => node === document.activeElement")
        page.keyboard.press("Tab")
        assert page.evaluate(f'{ACTIVE}.name === "pills"')
        assert page.evaluate(f"{ACTIVE}.value") == "2"

    @pytest.mark.parametrize("field", SINGLE + MULTIPLE)
    def test_the_focus_on_a_choice_is_visible(self, choice_page, field):
        page = choice_page()

        tab_to(page, f'[name="{field}"]')

        assert page.evaluate(f"{ACTIVE}.matches(':focus-visible')")

    def test_the_more_button_is_pressed_from_the_keyboard(self, choice_page):
        page = choice_page()

        tab_to(page, "#id_chips [data-choice-more]")
        page.keyboard.press("Enter")

        assert page.evaluate(f'{ACTIVE}.name === "chips" && {ACTIVE}.value === "2"')


class TestNames:
    @pytest.mark.parametrize(
        ("field", "labels"),
        [
            ("pill", ["One", "Two", "Three", "Four", "None"]),
            ("pills", ["One", "Two", "Three", "Four"]),
        ],
    )
    def test_each_input_is_named_by_its_label(self, choice_page, field, labels):
        page = choice_page()

        names = page.locator(f'[name="{field}"]').evaluate_all(
            "(nodes) => nodes.map((node) => node.getAttribute('aria-label'))"
        )

        assert sorted(names) == sorted(labels)

    def test_the_first_and_last_of_a_scale_carry_the_end_words(self, choice_page):
        page = choice_page()
        scale = page.locator("#id_scale")

        expect(scale.get_by_role("radio", name=re.compile("^One.*Low"))).to_have_count(
            1
        )
        expect(
            scale.get_by_role("radio", name=re.compile("^Four.*High"))
        ).to_have_count(1)
        expect(scale.get_by_role("radio", name="Two", exact=True)).to_have_count(1)
        expect(scale.get_by_role("radio", name="Three", exact=True)).to_have_count(1)

    @pytest.mark.parametrize("field", ["chip", "card"])
    def test_a_single_choice_of_chips_or_cards_is_named_by_its_label(
        self, choice_page, field
    ):
        page = choice_page()

        expect(
            page.locator(f"#id_{field}").get_by_role("radio", name=re.compile("One"))
        ).to_have_count(1)


class TestLongLabels:
    def test_a_long_label_wraps_in_a_chip(self, choice_page):
        page = choice_page()
        short = option(page, "chip", "short")
        long = page.locator('#long [value="long"]')

        assert long.bounding_box()["height"] > 1.5 * short.bounding_box()["height"]

    def test_a_long_label_is_the_chips_whole_name(self, choice_page):
        page = choice_page()

        name = page.locator('#long [value="long"]').get_attribute("aria-label")

        assert name.startswith("A label long enough") and name.endswith("several lines")


class TestDisabled:
    def test_no_choice_of_a_disabled_field_can_be_chosen(self, choice_page):
        page = choice_page()

        expect(page.locator('[name="locked"]').first).to_be_disabled()

    def test_the_script_raises_no_error(self, choice_page, page_errors):
        choice_page()

        assert page_errors == []


def visible_values(page, field):
    """Return the values of the choices that can be seen, in the order drawn."""
    return page.locator(f"#id_{field} [data-choice-row] input").evaluate_all(
        "(nodes) => nodes.filter((node) => node.checkVisibility()).map("
        "(node) => node.value)"
    )


def all_values(page, field):
    """Return the values of every choice in the row, in the order drawn."""
    return page.locator(f"#id_{field} [data-choice-row] input").evaluate_all(
        "(nodes) => nodes.map((node) => node.value)"
    )


class TestFoldScript:
    @pytest.mark.parametrize("field", ["chips", "cards", "chip", "card"])
    def test_the_choices_not_on_show_are_hidden_and_the_button_is_shown(
        self, choice_page, field
    ):
        page = choice_page()

        assert len(visible_values(page, field)) < len(all_values(page, field)) - (
            field in ("chip", "card")
        )
        expect(more_of(page, field)).to_be_visible()

    @pytest.mark.parametrize("field", ["chips", "cards", "chip", "card"])
    def test_the_button_shows_the_hidden_choices_in_place_and_goes(
        self, choice_page, field
    ):
        page = choice_page()
        order = all_values(page, field)

        more_of(page, field).click()

        assert visible_values(page, field) == order
        assert all_values(page, field) == order
        expect(more_of(page, field)).to_have_count(0)

    @pytest.mark.parametrize("field", ["chips", "cards"])
    def test_the_focus_goes_to_the_first_choice_shown(self, choice_page, field):
        page = choice_page()
        on_show = visible_values(page, field)
        first = next(v for v in all_values(page, field) if v not in on_show)

        more_of(page, field).click()

        assert page.evaluate(f'{ACTIVE}.name === "{field}" && {ACTIVE}.value') == first

    def test_a_choice_that_is_chosen_is_never_hidden(self, choice_page):
        page = choice_page(bound="1", chips="3", cards="4")

        assert visible_values(page, "chips") == ["1", "3"]
        assert visible_values(page, "cards") == ["1", "4"]

    def test_a_choice_checked_by_the_browser_before_the_script_runs_stays_on_show(
        self, choice_page
    ):
        page = choice_page(bound="1", chips="4")

        assert "4" in visible_values(page, "chips")
        expect(more_of(page, "chips")).to_be_visible()

    def test_no_button_is_left_when_every_folded_choice_is_chosen(self, choice_page):
        page = choice_page(bound="1", chips="2&chips=3&chips=4")

        expect(more_of(page, "chips")).to_have_count(0)
        assert visible_values(page, "chips") == ["1", "2", "3", "4"]

    def test_the_clearing_choice_is_left_alone(self, choice_page):
        page = choice_page()

        clearing = option(page, "chip", "")

        expect(clearing).to_be_visible()
        assert clearing.evaluate("(node) => node.closest('[data-choice-row]') === null")
        assert not clearing.evaluate(
            "(node) => node.hasAttribute('data-choice-folded')"
        )

    def test_a_chosen_choice_can_still_be_changed_once_shown(self, choice_page):
        page = choice_page()

        tap(page, "chip", "3")
        option(page, "chip", "").click()

        assert checked(page, "chip") == [""]

    def test_the_script_raises_no_error_while_folding(self, choice_page, page_errors):
        page = choice_page()

        more_of(page, "chips").click()

        assert page_errors == []

    def test_what_was_chosen_among_the_folded_is_received_by_the_form(
        self, choice_page
    ):
        page = choice_page()

        tap(page, "chips", "3")
        tap(page, "chips", "4")
        answer = send(page)

        assert answer["entries"]["chips"] == ["3", "4"]


class TestWithoutTheScript:
    def test_every_choice_is_shown_and_the_button_stays_hidden(self, choice_page):
        page = choice_page("choice-widgets-bare")

        assert visible_values(page, "chips") == ["1", "2", "3", "4"]
        expect(more_of(page, "chips")).to_be_hidden()

    def test_a_folded_choice_is_submitted(self, choice_page):
        page = choice_page("choice-widgets-bare")

        option(page, "chips", "3").click()
        answer = send(page)

        assert answer["entries"]["chips"] == ["3"]

    def test_a_folded_card_is_submitted(self, choice_page):
        page = choice_page("choice-widgets-bare")

        option(page, "cards", "4").click()
        answer = send(page)

        assert answer["entries"]["cards"] == ["1", "4"]


class TestDrawnAgain:
    def test_a_form_drawn_again_after_a_failed_submission_shows_what_was_chosen(
        self, choice_page
    ):
        page = choice_page("choice-widgets-bare")

        option(page, "chips", "3").click()
        option(page, "card", "4").click()
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert checked(page, "chips") == ["3"]
        assert checked(page, "card") == ["4"]
        assert "3" in visible_values(page, "chips")
        assert "4" in visible_values(page, "card")


class TestAddedLater:
    def test_a_row_added_by_a_script_is_folded_as_on_load(self, choice_page):
        page = choice_page()
        page.evaluate(INSERT_LINE)
        row = page.locator("#lines [data-choice-row]").first

        button = row.locator("[data-choice-more]")

        expect(button).to_be_visible()
        assert row.locator("input:visible").count() == 1
        button.click()
        assert row.locator("input:visible").count() == 4

    def test_a_row_added_by_a_script_is_independent_of_the_first(self, choice_page):
        page = choice_page()
        page.evaluate(INSERT_LINE)
        page.evaluate(INSERT_LINE)
        buttons = page.locator("#lines [data-choice-more]")
        assert buttons.count() == 4

        buttons.first.click()

        assert buttons.count() == 3

    def test_a_form_swapped_in_by_htmx_is_folded_as_on_load(self, choice_page):
        page = choice_page("choice-widgets-htmx")

        page.click("#swap")
        page.wait_for_selector("#lines [data-choice-more]:visible")
        row = page.locator("#lines [data-choice-row]").first

        assert row.locator("input:visible").count() == 1
        row.locator("[data-choice-more]").click()
        assert row.locator("input:visible").count() == 4

    def test_the_script_included_twice_acts_once(self, choice_page, page_errors):
        page = choice_page("choice-widgets-copies")

        more_of(page, "chips").click()

        assert visible_values(page, "chips") == ["1", "2", "3", "4"]
        assert page_errors == []


class TestDisabledFold:
    def test_the_choices_of_a_disabled_field_are_shown_and_all_disabled(
        self, choice_page
    ):
        page = choice_page()

        more_of(page, "locked_chips").click()

        inputs = page.locator('[name="locked_chips"]')
        for position in range(inputs.count()):
            expect(inputs.nth(position)).to_be_disabled()
            expect(inputs.nth(position)).to_be_visible()
        assert checked(page, "locked_chips") == []
