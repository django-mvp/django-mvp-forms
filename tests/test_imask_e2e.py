"""The script that applies IMask, run in Chrome against pages of the test project."""

from pathlib import Path

import pytest
from django.urls import reverse

from tests.urls import IMASK_URL

pytestmark = pytest.mark.e2e

IMASK = Path(__file__).parent / "data" / "imask-7.6.1.min.js"
# Counts each mask the script reports applying, by the id of its input.
COUNT_MASKS = """
window.masked = [];
document.addEventListener("mvp-forms:imask", (event) =>
  window.masked.push(event.target.id));
"""
ENTRIES = "Object.fromEntries(new FormData(document.getElementById('masked')))"


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def masked_page(page, page_errors, live_server):
    """Open a page of the test project, with IMask answered from tests/data."""
    page.route(
        IMASK_URL,
        lambda route: route.fulfill(path=IMASK, content_type="text/javascript"),
    )
    page.add_init_script(COUNT_MASKS)

    def open_page(name="masked", **initial):
        query = "&".join(f"{key}={value}" for key, value in initial.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def type_into(page, name, text):
    field = page.locator(f"#id_{name}")
    field.click()
    field.press_sequentially(text)
    return field.input_value()


class TestMaskedInputs:
    def test_a_definition_the_developer_stated_decides_what_is_accepted(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "shelf", "9") == ""
        assert type_into(page, "shelf", "3") == "3"

    def test_a_range_block_refuses_a_number_no_value_in_its_bounds_starts_with(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "day", "4") == ""
        assert type_into(page, "day", "3") == "3"

    def test_an_enum_block_completes_a_value_from_its_list(self, masked_page):
        page = masked_page()

        assert type_into(page, "resolution", "T") == "TV"

    def test_a_repeated_block_stops_after_its_last_repeat(self, masked_page):
        page = masked_page()

        assert type_into(page, "serial", "12345") == "123"

    def test_a_pattern_shown_always_is_shown_with_its_placeholder_character(
        self, masked_page
    ):
        page = masked_page()

        assert page.locator("#id_postcode").input_value() == "#####"

    def test_a_placeholder_character_for_each_definition_is_shown_for_it(
        self, masked_page
    ):
        page = masked_page()

        assert page.locator("#id_reference").input_value() == "aa-####"

    def test_a_built_in_definition_with_a_placeholder_character_keeps_its_rule(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "reference", "1") == "aa-####"

    def test_a_value_the_form_was_drawn_with_is_shown_under_the_mask(self, masked_page):
        page = masked_page(postcode="12")

        assert page.locator("#id_postcode").input_value() == "12###"


class TestRegexMaskedInputs:
    def test_a_character_that_stops_the_value_matching_is_not_accepted(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "customer", "12a3") == "123"

    def test_a_flag_reaches_imask(self, masked_page):
        page = masked_page()

        assert type_into(page, "colour", "#AbC") == "#AbC"


class TestNumberMaskedInputs:
    def test_a_typed_number_gains_its_separators(self, masked_page):
        page = masked_page()

        assert type_into(page, "amount", "1234567,5") == "1 234 567,5"

    def test_an_initial_value_is_shown_with_its_separators(self, masked_page):
        page = masked_page(amount="1234567.5")

        assert page.locator("#id_amount").input_value() == "1 234 567,5"

    def test_a_post_returns_the_plain_number(self, masked_page):
        page = masked_page("masked-cleaned")
        type_into(page, "amount", "1234567,5")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"amount": "1234567.5"' in page.inner_text("body")

    def test_a_page_without_imask_posts_the_plain_number_too(self, masked_page):
        page = masked_page("masked-bare-cleaned", amount="1234567.5")

        assert page.locator("#id_amount").input_value() == "1234567,5"
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"amount": "1234567.5"' in page.inner_text("body")


class TestOneMaskForEachInput:
    def test_every_input_is_masked_once_when_the_script_is_on_the_page_once(
        self, masked_page
    ):
        page = masked_page()

        inputs = page.locator("input[data-imask]").evaluate_all(
            "(nodes) => nodes.map((node) => node.id)"
        )

        assert sorted(page.evaluate("window.masked")) == sorted(inputs)

    def test_every_input_is_masked_once_when_the_script_is_on_the_page_three_times(
        self, masked_page
    ):
        page = masked_page("masked-copies")

        inputs = page.locator("input[data-imask]").evaluate_all(
            "(nodes) => nodes.map((node) => node.id)"
        )

        assert sorted(page.evaluate("window.masked")) == sorted(inputs)


class TestAPageWithoutIMask:
    def test_it_raises_no_error_and_leaves_a_text_input(self, masked_page, page_errors):
        page = masked_page("masked-bare")

        assert page_errors == []
        assert page.locator("#id_postcode").input_value() == ""
        assert page.locator("#id_postcode").get_attribute("type") == "text"

    def test_it_submits_what_was_typed(self, masked_page):
        page = masked_page("masked-bare")
        type_into(page, "phone", "abc")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"phone": ["abc"]' in page.inner_text("body")


class TestWhatTheFormReceives:
    def test_a_display_character_shows_but_the_field_submits_what_was_typed(
        self, masked_page
    ):
        page = masked_page()

        shown = type_into(page, "pin", "1234")
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert shown == "••••"
        assert '"pin": ["1234"]' in page.inner_text("body")

    def test_an_input_removed_from_its_form_adds_no_entry(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate("document.getElementById('id_pin').remove()")

        assert "pin" not in page.evaluate(ENTRIES)

    def test_a_disabled_input_adds_no_entry(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate("document.getElementById('id_pin').disabled = true")

        assert "pin" not in page.evaluate(ENTRIES)

    def test_an_input_with_no_name_adds_no_entry(self, masked_page):
        page = masked_page()

        assert "" not in page.evaluate(ENTRIES)


class TestAStrictContentSecurityPolicy:
    def test_a_page_that_forbids_inline_script_is_still_masked(self, masked_page):
        page = masked_page("masked-strict")

        assert type_into(page, "shelf", "9") == ""
        assert type_into(page, "shelf", "3") == "3"
