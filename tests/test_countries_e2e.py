"""The country controls, run in Chrome against pages of the test project."""

import pytest
from django.urls import reverse
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e

OPTION = "#id_templated-ts-dropdown .option"
CONTROL = "#id_{} + .ts-wrapper .ts-control"


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def templated_page(page, page_errors, live_server):
    """Open the page whose select states an option and an item template."""
    page.goto(f"{live_server.url}{reverse('templated-page')}")
    page.wait_for_load_state("load")
    return page


class TestAStatedTemplate:
    def test_each_option_is_drawn_from_the_template_with_its_own_data(
        self, templated_page
    ):
        templated_page.locator(CONTROL.format("templated")).click()

        flags = templated_page.locator(f"{OPTION} img").evaluate_all(
            "(images) => images.map((image) => image.getAttribute('src'))"
        )

        assert flags == ["/static/flags/a.gif", "/static/flags/b.gif", ""]

    def test_the_text_of_an_option_follows_its_flag_in_the_row(self, templated_page):
        templated_page.locator(CONTROL.format("templated")).click()

        order = templated_page.locator(OPTION).first.evaluate(
            "(option) => [...option.children].map((child) => child.tagName)"
        )

        assert order == ["IMG", "I"]

    def test_a_chosen_value_is_drawn_from_the_item_template(self, templated_page):
        templated_page.locator(CONTROL.format("templated")).click()
        templated_page.locator(f'{OPTION}[data-value="a"]').click()

        item = templated_page.locator("#id_templated + .ts-wrapper .item")

        expect(item.locator("img")).to_have_attribute("src", "/static/flags/a.gif")
        expect(item.locator("i")).to_have_text("Apple")

    def test_a_value_holding_markup_is_shown_as_text(self, templated_page):
        templated_page.locator(CONTROL.format("templated")).click()

        option = templated_page.locator(f'{OPTION}[data-value="b"]')

        expect(option.locator("b")).to_have_count(0)
        expect(option.locator("i")).to_have_text('<b>Bold</b> & "quoted"')

    def test_a_select_with_no_template_is_drawn_as_it_was(self, templated_page):
        templated_page.locator(CONTROL.format("plain")).click()

        option = templated_page.locator("#id_plain-ts-dropdown .option")

        expect(option).to_have_text("Apple")
        expect(option.locator("img")).to_have_count(0)

    def test_the_script_raises_no_error(self, templated_page, page_errors):
        templated_page.locator(CONTROL.format("templated")).click()

        assert page_errors == []
