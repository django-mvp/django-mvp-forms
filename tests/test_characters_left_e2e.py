"""The script that draws the characters-left line, run in Chrome."""

import json
from pathlib import Path

import pytest
from django.urls import reverse

from tests.urls import HTMX_URL

pytestmark = pytest.mark.e2e

HTMX = Path(__file__).parent / "data" / "htmx-2.0.10.min.js"
# Records each write to the status region of one field's line.
RECORD_WRITES = """
(id) => {
  window.writes = 0;
  const status = document.querySelector(
    `[data-characters-left-line="${id}"] [role=status]`);
  new MutationObserver((records) => { window.writes += records.length; })
    .observe(status, { childList: true, characterData: true, subtree: true });
}
"""
ADD_FILLED = """
() => {
  const input = document.getElementById("id_title").cloneNode();
  input.id = "id_filled";
  input.name = "filled";
  input.value = "x".repeat(15);
  document.getElementById("rows").append(input);
}
"""
ADD_ROW = """
document.getElementById("rows").append(
  document.getElementById("line").content.cloneNode(true));
"""
MARKED_IDS = """
[...document.querySelectorAll("[data-characters-left-words]")].map((node) => node.id)
"""
SERVED_IDS = """
[...document.querySelectorAll("[data-characters-left-line]")]
  .map((node) => node.dataset.charactersLeftLine)
"""


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def characters_page(page, page_errors, live_server):
    """Open a page of the test project, with htmx answered from tests/data."""
    page.route(
        HTMX_URL, lambda route: route.fulfill(path=HTMX, content_type="text/javascript")
    )

    def open_page(name="characters-left", **initial):
        query = "&".join(f"{key}={value}" for key, value in initial.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def type_into(page, locator, text):
    field = page.locator(locator)
    field.click()
    field.press_sequentially(text)
    return field


def line_of(page, field_id):
    return page.locator(f'[data-characters-left-line="{field_id}"]')


def shown_text(page, field_id):
    """The visible line's text when it is shown, and None when it is hidden."""
    visible = line_of(page, field_id).locator("[aria-hidden]")
    if visible.evaluate("element => element.hidden"):
        return None
    return visible.text_content()


def announced(page, field_id):
    return line_of(page, field_id).locator("[role=status]").text_content()


def words_of(page, field_id):
    node = page.locator(f"#{field_id}")
    return json.loads(node.get_attribute("data-characters-left-words"))


def over_phrase(page, field_id, number):
    """The words for a count with a minus before the number."""
    return words_of(page, field_id)[number].replace(str(number), f"-{number}")


def line_classes(page, field_id):
    return line_of(page, field_id).locator("[aria-hidden]").get_attribute("class")


class TestTheLine:
    def test_it_is_hidden_until_the_number_is_reached(self, characters_page):
        page = characters_page()

        type_into(page, "#id_title", "x" * 11)
        before = shown_text(page, "id_title")
        page.locator("#id_title").press_sequentially("x")

        assert before is None
        assert shown_text(page, "id_title") == words_of(page, "id_title")[8]

    def test_the_number_follows_typing_and_deleting(self, characters_page):
        page = characters_page()

        field = type_into(page, "#id_title", "x" * 15)
        typed = shown_text(page, "id_title")
        field.press("Backspace")
        field.press("Backspace")

        assert typed == words_of(page, "id_title")[5]
        assert shown_text(page, "id_title") == words_of(page, "id_title")[7]

    def test_it_is_hidden_again_when_enough_is_deleted(self, characters_page):
        page = characters_page()
        field = type_into(page, "#id_title", "x" * 15)

        for _ in range(5):
            field.press("Backspace")

        assert shown_text(page, "id_title") is None

    def test_a_full_field_takes_no_more_and_says_none_are_left(self, characters_page):
        page = characters_page()

        field = type_into(page, "#id_title", "x" * 20)
        field.press_sequentially("more")

        assert field.input_value() == "x" * 20
        assert shown_text(page, "id_title") == words_of(page, "id_title")[0]

    def test_a_pasted_overflow_is_not_taken_and_none_are_left(self, characters_page):
        page = characters_page()
        page.locator("#id_title").click()

        page.keyboard.insert_text("x" * 30)

        assert page.locator("#id_title").input_value() == "x" * 20
        assert shown_text(page, "id_title") == words_of(page, "id_title")[0]

    def test_characters_of_two_code_units_count_as_the_browser_counts(
        self, characters_page
    ):
        page = characters_page()

        field = type_into(page, "#id_title", "\U0001f600" * 10)

        assert field.evaluate("(node) => node.value.length") == 20
        assert shown_text(page, "id_title") == words_of(page, "id_title")[0]

    def test_a_value_near_the_limit_shows_it_before_anything_is_typed(
        self, characters_page
    ):
        page = characters_page(title="x" * 15)

        assert shown_text(page, "id_title") == words_of(page, "id_title")[5]

    def test_a_value_over_the_limit_says_by_how_many_and_is_not_cut(
        self, characters_page
    ):
        page = characters_page(title="x" * 25)

        assert shown_text(page, "id_title") == over_phrase(page, "id_title", 5)
        assert shown_text(page, "id_title").startswith("-5")
        assert page.locator("#id_title").input_value() == "x" * 25

    def test_the_line_is_in_the_error_colour_only_while_over_the_limit(
        self, characters_page
    ):
        page = characters_page(title="x" * 22)
        over = line_classes(page, "id_title").split()
        field = page.locator("#id_title")
        field.focus()
        field.press("End")
        for _ in range(3):
            field.press("Backspace")
        within = line_classes(page, "id_title").split()

        assert "text-error" in over and "text-base-content" not in over
        assert "text-base-content" in within and "text-error" not in within

    def test_a_value_over_the_limit_by_more_than_the_limit_keeps_its_number(
        self, characters_page
    ):
        page = characters_page(title="x" * 120)

        assert shown_text(page, "id_title").startswith("-100 ")

    def test_a_field_without_a_number_shows_the_line_from_the_start(
        self, characters_page
    ):
        page = characters_page()

        assert shown_text(page, "id_free") == words_of(page, "id_free")[20]
        type_into(page, "#id_free", "xxx")
        assert shown_text(page, "id_free") == words_of(page, "id_free")[17]

    def test_a_count_above_the_words_written_is_said_with_its_own_number(
        self, characters_page
    ):
        page = characters_page()

        assert len(words_of(page, "id_long")) == 200
        assert shown_text(page, "id_long") == words_of(page, "id_long")[100].replace(
            "100", "500"
        )
        type_into(page, "#id_long", "x" * 3)
        assert shown_text(page, "id_long").startswith("497 ")

    def test_a_field_without_a_value_near_the_limit_shows_nothing(
        self, characters_page
    ):
        page = characters_page()

        assert shown_text(page, "id_title") is None
        assert shown_text(page, "id_note") is None

    def test_a_textarea_filled_with_line_breaks_to_the_limit_is_accepted(
        self, characters_page
    ):
        page = characters_page()
        text = "\n".join(["abcd"] * 4) + "e"

        field = type_into(page, "#id_note", text)
        length = field.evaluate("(node) => node.value.length")
        none_left = shown_text(page, "id_note") == words_of(page, "id_note")[0]
        with page.expect_response(
            lambda each: each.request.method == "POST"
        ) as response:
            page.click("#send")

        assert length == 20
        assert none_left
        assert response.value.json()["errors"] == {}
        assert response.value.json()["note"] == text


class TestTheStatusRegion:
    def test_it_is_written_at_the_first_appearance_and_after_typing_stops(
        self, characters_page
    ):
        page = characters_page()
        page.evaluate(RECORD_WRITES, "id_title")

        type_into(page, "#id_title", "x" * 14)
        assert announced(page, "id_title") == words_of(page, "id_title")[8]
        page.wait_for_function(
            "(text) => document.querySelector("
            "'[data-characters-left-line=id_title] [role=status]')"
            ".textContent === text",
            arg=words_of(page, "id_title")[6],
            timeout=4000,
        )

        assert 1 <= page.evaluate("window.writes") <= 2

    def test_it_is_written_at_once_when_none_are_left(self, characters_page):
        page = characters_page()

        type_into(page, "#id_title", "x" * 20)

        assert announced(page, "id_title") == words_of(page, "id_title")[0]

    def test_it_is_not_written_for_a_value_drawn_near_the_limit(self, characters_page):
        page = characters_page(title="x" * 15)

        assert announced(page, "id_title") == ""

    def test_it_is_cleared_when_the_line_hides(self, characters_page):
        page = characters_page()
        field = type_into(page, "#id_title", "x" * 20)

        for _ in range(15):
            field.press("Backspace")

        assert shown_text(page, "id_title") is None
        assert announced(page, "id_title") == ""

    def test_it_is_written_with_text_and_never_as_markup(self, characters_page):
        page = characters_page(title="x" * 15)
        page.evaluate(
            "document.getElementById('id_title').dataset.charactersLeftWords ="
            " JSON.stringify(Array(9).fill('<b>left</b>'))"
        )

        type_into(page, "#id_title", "x" * 5)

        assert page.locator("[data-characters-left-line] b").count() == 0
        assert shown_text(page, "id_title") == "<b>left</b>"


class TestFieldsAddedLater:
    def test_a_formset_row_added_in_the_browser_has_the_line(self, characters_page):
        page = characters_page()
        page.evaluate(ADD_ROW)

        type_into(page, "#rows input", "x" * 15)

        assert line_of(page, "id_form-__prefix__-code").count() == 1
        assert shown_text(page, "id_form-__prefix__-code") is not None

    def test_a_field_added_near_its_limit_shows_the_line_before_anything_is_typed(
        self, characters_page
    ):
        page = characters_page()

        page.evaluate(ADD_FILLED)

        page.wait_for_selector(
            '[data-characters-left-line="id_filled"]', state="attached"
        )
        assert shown_text(page, "id_filled") == words_of(page, "id_filled")[5]

    def test_a_field_in_a_modal_has_the_line(self, characters_page):
        page = characters_page()
        page.evaluate("document.getElementById('aside-dialog').showModal()")

        type_into(page, "#id_aside", "x" * 15)

        assert shown_text(page, "id_aside") is not None

    def test_a_field_swapped_in_by_htmx_has_the_line(self, characters_page):
        page = characters_page()
        page.click("#load")
        page.wait_for_selector("#swap input")

        type_into(page, "#swap input", "x" * 15)

        assert shown_text(page, "id_code") is not None


class TestOneLineForEachInput:
    def test_the_script_twice_on_a_page_gives_one_line_to_each_input(
        self, characters_page
    ):
        page = characters_page("characters-left-twice")

        type_into(page, "#id_title", "x" * 15)

        assert sorted(page.evaluate(SERVED_IDS)) == sorted(page.evaluate(MARKED_IDS))
        assert shown_text(page, "id_title") == words_of(page, "id_title")[5]

    def test_two_members_of_a_join_keep_their_own_lines(self, characters_page):
        page = characters_page()

        type_into(page, "#id_first", "x" * 5)
        type_into(page, "#id_second", "x" * 9)

        assert shown_text(page, "id_first") == words_of(page, "id_first")[5]
        assert shown_text(page, "id_second") == words_of(page, "id_second")[1]

    def test_a_typing_box_of_a_tom_select_is_left_alone(self, characters_page):
        page = characters_page()
        page.wait_for_selector(".ts-control input")

        type_into(page, ".ts-control input", "x" * 30)

        assert sorted(page.evaluate(SERVED_IDS)) == sorted(page.evaluate(MARKED_IDS))
        assert "id_choice" not in page.evaluate(SERVED_IDS)


class TestWithoutTheScript:
    def test_the_field_still_stops_at_its_limit_and_nothing_is_raised(
        self, characters_page, page_errors
    ):
        page = characters_page("characters-left-bare")

        field = type_into(page, "#id_title", "x" * 30)

        assert field.input_value() == "x" * 20
        assert page.evaluate(SERVED_IDS) == []
        assert page_errors == []
