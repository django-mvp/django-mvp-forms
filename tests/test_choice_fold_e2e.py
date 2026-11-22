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


def tap(page, field, value):
    """Tap a choice, opening the field's fold first when the choice is in it."""
    target = option(page, field, value)
    fold = page.locator(f"#id_{field} details")
    if not target.is_visible() and fold.count():
        fold.locator("summary").click()
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

        page.locator("#id_chips summary").click()
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

    def test_the_fold_is_opened_and_closed_from_the_keyboard(self, choice_page):
        page = choice_page()
        fold = page.locator("#id_chips details")

        tab_to(page, "#id_chips summary")
        page.keyboard.press("Enter")

        expect(fold).to_have_attribute("open", "")

        page.keyboard.press("Enter")

        expect(fold).not_to_have_attribute("open", "")


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
            page.locator(f"#id_{field}").get_by_role("radio", name="One", exact=True)
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


def fold_of(page, field):
    """Return the fold of a field."""
    return page.locator(f"#id_{field} details[data-choice-fold]")


def values_on_show(page, field):
    """Return the values of the choices on show, in the order they are drawn."""
    return page.locator(f"#id_{field} > [data-choice-shown] input").evaluate_all(
        "(nodes) => nodes.map((node) => node.value)"
    )


def values_folded(page, field):
    """Return the values of the choices in the fold, in the order they are drawn."""
    return page.locator(f"#id_{field} details input").evaluate_all(
        "(nodes) => nodes.map((node) => node.value)"
    )


def settle(page):
    """Wait until the toggle event of a fold just closed has been heard."""
    page.evaluate(
        "() => new Promise((done) => requestAnimationFrame("
        "() => requestAnimationFrame(done)))"
    )


def fold_and_tap(page, field, *values):
    """Open a field's fold, choose the given choices in it and close it again."""
    fold = fold_of(page, field)
    summary = fold.locator("summary")
    summary.click()
    expect(fold).to_have_attribute("open", "")
    for value in values:
        option(page, field, value).click()
    summary.click()
    settle(page)


class TestFoldScript:
    @pytest.mark.parametrize("field", ["chips", "cards", "chip", "card"])
    def test_a_choice_chosen_in_the_fold_is_on_show_when_the_fold_closes(
        self, choice_page, field
    ):
        page = choice_page()
        folded = values_folded(page, field)

        fold_and_tap(page, field, folded[1])

        assert folded[1] in values_on_show(page, field)
        assert folded[1] not in values_folded(page, field)
        assert checked(page, field) == [folded[1]]

    @pytest.mark.parametrize("field", ["chips", "cards"])
    def test_choices_are_on_show_in_the_fields_order(self, choice_page, field):
        page = choice_page()

        fold_and_tap(page, field, "4", "2")

        assert values_on_show(page, field) == ["1", "2", "4"]

    def test_the_count_is_the_number_of_choices_still_folded(self, choice_page):
        page = choice_page()

        fold_and_tap(page, "chips", "3")

        assert fold_of(page, "chips").locator("[data-choice-count]").inner_text() == "2"

    @pytest.mark.parametrize("field", ["chip", "card"])
    def test_the_package_words_are_rewritten_with_the_count(self, choice_page, field):
        page = choice_page()
        summary = fold_of(page, field).locator("summary")
        one = summary.get_attribute("data-choice-one")
        other = summary.get_attribute("data-choice-other")
        folded = values_folded(page, field)

        fold_and_tap(page, field, folded[0])

        left = len(folded) - 1
        words = one if left == 1 else other
        count = fold_of(page, field).locator("[data-choice-count]")
        assert count.inner_text() == words.replace("{n}", str(left))

    def test_the_package_words_use_the_form_for_one(self, choice_page):
        page = choice_page()
        summary = fold_of(page, "card").locator("summary")
        one = summary.get_attribute("data-choice-one")

        fold_and_tap(page, "card", "3")

        count = fold_of(page, "card").locator("[data-choice-count]")
        assert count.inner_text() == one.replace("{n}", "1")

    @pytest.mark.parametrize("field", ["chips", "cards"])
    def test_the_fold_is_removed_when_no_choice_is_left_in_it(self, choice_page, field):
        page = choice_page()

        fold_and_tap(page, field, "2", "3", "4")

        expect(fold_of(page, field)).to_have_count(0)
        assert values_on_show(page, field) == ["1", "2", "3", "4"]

    def test_a_fold_closed_with_nothing_chosen_keeps_its_choices(self, choice_page):
        page = choice_page()

        fold_and_tap(page, "chips")

        assert values_folded(page, "chips") == ["2", "3", "4"]
        assert fold_of(page, "chips").locator("[data-choice-count]").inner_text() == "3"

    def test_the_clearing_choice_stays_outside_the_fold_and_the_script(
        self, choice_page
    ):
        page = choice_page()

        fold_and_tap(page, "chip", "2")
        clearing = option(page, "chip", "")

        assert clearing.evaluate("(node) => node.closest('details') === null")
        assert clearing.evaluate(
            "(node) => node.closest('[data-choice-shown]') === null"
        )
        assert not clearing.evaluate("(node) => node.hasAttribute('data-choice-index')")
        expect(option(page, "chip", "2")).to_be_checked()

    def test_the_clearing_choice_of_a_card_field_is_left_alone(self, choice_page):
        page = choice_page()

        fold_and_tap(page, "card", "3")

        assert page.locator("#id_card [data-choice-index]").count() == 4
        assert (
            not option(page, "card", "")
            .locator("xpath=..")
            .evaluate("(node) => node.hasAttribute('data-choice-index')")
        )

    def test_a_chosen_choice_can_still_be_changed_once_on_show(self, choice_page):
        page = choice_page()

        fold_and_tap(page, "chip", "3")
        option(page, "chip", "").click()

        assert checked(page, "chip") == [""]

    def test_the_script_raises_no_error_while_folding(self, choice_page, page_errors):
        page = choice_page()

        fold_and_tap(page, "chips", "2")

        assert page_errors == []

    def test_what_was_chosen_in_the_fold_is_received_by_the_form(self, choice_page):
        page = choice_page()

        fold_and_tap(page, "chips", "3", "4")
        answer = send(page)

        assert answer["entries"]["chips"] == ["3", "4"]


class TestWithoutTheScript:
    def test_the_fold_opens_and_a_folded_choice_is_submitted(self, choice_page):
        page = choice_page("choice-widgets-bare")

        fold_of(page, "chips").locator("summary").click()
        option(page, "chips", "3").click()
        answer = send(page)

        assert answer["entries"]["chips"] == ["3"]

    def test_a_folded_choice_stays_folded_when_the_fold_closes(self, choice_page):
        page = choice_page("choice-widgets-bare")

        fold_and_tap(page, "chips", "3")

        assert values_folded(page, "chips") == ["2", "3", "4"]

    def test_a_folded_card_is_submitted(self, choice_page):
        page = choice_page("choice-widgets-bare")

        fold_of(page, "cards").locator("summary").click()
        option(page, "cards", "4").click()
        answer = send(page)

        assert answer["entries"]["cards"] == ["1", "4"]


class TestDrawnAgain:
    def test_a_form_drawn_again_after_a_failed_submission_shows_every_choice_chosen(
        self, choice_page
    ):
        page = choice_page("choice-widgets-bare")

        fold_and_tap(page, "chips", "3")
        fold_of(page, "card").locator("summary").click()
        option(page, "card", "4").click()
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert "3" in values_on_show(page, "chips")
        assert "4" in values_on_show(page, "card")
        assert checked(page, "chips") == ["3"]
        assert checked(page, "card") == ["4"]
        assert "3" not in values_folded(page, "chips")

    def test_a_chosen_choice_is_on_show_when_the_page_is_drawn_with_the_script(
        self, choice_page
    ):
        page = choice_page(bound="1", chips="4", cards="3")

        assert "4" in values_on_show(page, "chips")
        assert "3" in values_on_show(page, "cards")
        assert fold_of(page, "chips").locator("[data-choice-count]").inner_text() == "2"


def folded_count(fold):
    """Return the number a fold's summary says is still folded."""
    text = fold.locator("[data-choice-count]").inner_text()
    return int(re.search(r"\d+", text).group())


def tap_first_folded(fold):
    """Open a fold, choose the first choice in it and close it again."""
    fold.locator("summary").click()
    fold.locator("input").first.click()
    fold.locator("summary").click()
    settle(fold.page)


class TestAddedLater:
    def test_a_fold_in_a_row_added_by_a_script_behaves_as_on_load(self, choice_page):
        page = choice_page()
        page.evaluate(INSERT_LINE)
        row = page.locator("#lines")

        tap_first_folded(row.locator("details").first)

        assert row.locator("[data-choice-shown] input:checked").count() == 1
        assert folded_count(row.locator("details").first) == 2

    def test_a_row_added_by_a_script_is_independent_of_the_first(self, choice_page):
        page = choice_page()
        page.evaluate(INSERT_LINE)
        page.evaluate(INSERT_LINE)
        rows = page.locator("#lines details[data-choice-fold]")
        assert rows.count() == 4

        tap_first_folded(rows.first)

        assert rows.count() == 4
        assert folded_count(rows.first) == 2
        assert folded_count(rows.nth(1)) == 3

    def test_a_fold_in_a_form_swapped_in_by_htmx_behaves_as_on_load(self, choice_page):
        page = choice_page("choice-widgets-htmx")

        page.click("#swap")
        page.wait_for_selector("#lines details")
        fold = page.locator("#lines details").first
        tap_first_folded(fold)

        assert page.locator("#lines [data-choice-shown] input:checked").count() == 1
        assert folded_count(fold) == 2

    def test_the_script_included_twice_acts_once(self, page, choice_page):
        page.add_init_script(
            """
            window.listeners = [];
            const add = EventTarget.prototype.addEventListener;
            EventTarget.prototype.addEventListener = function (type, ...rest) {
              if (type === "toggle") window.listeners.push(type);
              return add.call(this, type, ...rest);
            };
            """
        )
        choice_page("choice-widgets-copies")

        fold_and_tap(page, "chips", "3")

        assert page.evaluate("window.listeners.length") == 1
        assert values_on_show(page, "chips") == ["1", "3"]


class TestDisabledFold:
    def test_the_fold_of_a_disabled_field_opens_and_holds_no_choice_to_choose(
        self, choice_page
    ):
        page = choice_page()
        fold = fold_of(page, "locked_chips")

        fold.locator("summary").click()

        expect(fold).to_have_attribute("open", "")
        inputs = fold.locator("input")
        for position in range(inputs.count()):
            expect(inputs.nth(position)).to_be_disabled()
        assert checked(page, "locked_chips") == []
