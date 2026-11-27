"""The country controls, run in Chrome against pages of the test project."""

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


@pytest.fixture
def countries_page(page, page_errors, live_server):
    """Open a page of country controls, holding the values the query names."""

    def open_page(**initial):
        query = "&".join(f"{key}={value}" for key, value in initial.items())
        page.goto(f"{live_server.url}{reverse('countries-page')}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def search(page, name, text):
    """Open the control of a field and type part of a country's name."""
    page.locator(CONTROL.format(name)).click()
    page.locator(f"#id_{name}-ts-control").fill(text)


def row_order(option):
    """Return the tags of the flag image and the name in an option, in order."""
    return option.evaluate(
        "(option) => [...option.querySelectorAll('.flex > *')]"
        ".map((node) => node.tagName)"
    )


class TestSearchingCountries:
    def test_typing_part_of_a_name_narrows_the_list_to_the_matches(
        self, countries_page
    ):
        page = countries_page()

        search(page, "country", "zeal")

        options = page.locator("#id_country-ts-dropdown .option")
        expect(options).to_have_count(1)
        expect(options).to_have_text("New Zealand")

    def test_each_option_shows_the_flag_of_its_country_ahead_of_its_name(
        self, countries_page
    ):
        page = countries_page()
        search(page, "country", "zeal")

        option = page.locator('#id_country-ts-dropdown .option[data-value="NZ"]')

        assert row_order(option) == ["IMG", "SPAN"]
        expect(option.locator("img")).to_have_attribute("src", "/static/flags/nz.gif")

    def test_the_country_chosen_is_shown_with_its_flag_ahead_of_its_name(
        self, countries_page
    ):
        page = countries_page()
        search(page, "country", "zeal")
        page.locator('#id_country-ts-dropdown .option[data-value="NZ"]').click()

        item = page.locator("#id_country + .ts-wrapper .item")

        assert row_order(item) == ["IMG", "SPAN"]
        expect(item).to_have_text("New Zealand")
        assert page.evaluate("document.getElementById('id_country').value") == "NZ"

    def test_the_control_of_a_single_field_with_no_value_holds_no_country(
        self, countries_page
    ):
        page = countries_page()

        held = page.evaluate("document.getElementById('id_country').tomselect.items")

        assert held == []

    def test_a_value_already_chosen_is_held_with_its_flag(self, countries_page):
        page = countries_page(country="DE")

        item = page.locator("#id_country + .ts-wrapper .item")

        expect(item.locator("img")).to_have_attribute("src", "/static/flags/de.gif")
        expect(item).to_have_text("Germany")


class TestSeveralCountries:
    def test_each_country_chosen_has_its_flag_and_a_button_to_remove_it(
        self, countries_page
    ):
        page = countries_page()
        for text, code in (("zeal", "NZ"), ("germ", "DE")):
            search(page, "countries", text)
            page.locator(
                f'#id_countries-ts-dropdown .option[data-value="{code}"]'
            ).click()

        items = page.locator("#id_countries + .ts-wrapper .item")

        expect(items).to_have_count(2)
        expect(items.locator("img")).to_have_count(2)
        expect(items.locator(".remove")).to_have_count(2)
        assert page.evaluate(
            "[...document.getElementById('id_countries').selectedOptions]"
            ".map((option) => option.value)"
        ) == ["NZ", "DE"]

    def test_a_counted_control_shows_the_flag_in_each_option_of_its_list(
        self, countries_page
    ):
        page = countries_page()
        page.locator(CONTROL.format("counted")).click()

        options = page.locator('#id_counted-ts-dropdown .option[data-value="NZ"]')

        expect(options.locator("img")).to_have_attribute("src", "/static/flags/nz.gif")

    def test_a_counted_control_ticks_each_country_chosen(self, countries_page):
        page = countries_page(counted="NZ")
        page.locator(CONTROL.format("counted")).click()

        ticked = page.locator('#id_counted-ts-dropdown .option[data-value="NZ"]')

        expect(ticked.locator("input[type=checkbox]")).to_be_checked()


class TestASelectAddedLater:
    def test_a_row_added_to_the_page_starts_its_control_with_flags(
        self, countries_page
    ):
        page = countries_page()
        page.evaluate(
            """() => {
              const markup = document.getElementById("line").innerHTML;
              document.getElementById("page").insertAdjacentHTML(
                "beforeend", markup.replaceAll("__prefix__", "1"));
            }"""
        )

        page.locator(CONTROL.format("form-1-country")).click()

        option = page.locator('#id_form-1-country-ts-dropdown .option[data-value="NZ"]')
        expect(option.locator("img")).to_have_attribute("src", "/static/flags/nz.gif")


class TestThePageRaisesNoError:
    def test_opening_every_control_raises_no_error(self, countries_page, page_errors):
        page = countries_page()
        for name in ("country", "countries", "counted"):
            page.locator(CONTROL.format(name)).click()

        assert page_errors == []


@pytest.fixture
def fetched_page(page, page_errors, live_server):
    """Open the demo page whose country controls fetch from the view."""
    # The demo's stylesheet builder comes from a CDN, which the run has no use for.
    page.route("https://cdn.jsdelivr.net/**", lambda route: route.abort())
    page.route(
        TOM_SELECT_URL,
        lambda route: route.fulfill(
            body=TOM_SELECT.read_bytes(), content_type="text/javascript"
        ),
    )
    page.route(
        f"**{DJANGO_TOMSELECT_URL}",
        lambda route: route.fulfill(
            path=DJANGO_TOMSELECT, content_type="text/javascript"
        ),
    )
    page.goto(f"{live_server.url}/examples/countries/fetched/")
    page.wait_for_load_state("load")
    return page


class TestFetchedCountries:
    def test_opening_the_control_lists_countries_with_no_typing(self, fetched_page):
        fetched_page.locator(CONTROL.format("autocomplete_country")).click()

        options = fetched_page.locator("#id_autocomplete_country-ts-dropdown .option")

        expect(options.first).to_be_visible()
        assert options.count() > 1

    def test_a_search_lists_the_countries_matching_the_name(self, fetched_page):
        search(fetched_page, "autocomplete_country", "zeal")

        option = fetched_page.locator(
            '#id_autocomplete_country-ts-dropdown .option[data-value="NZ"]'
        )

        expect(option).to_be_visible()
        assert row_order(option) == ["IMG", "SPAN"]
        expect(option.locator("img")).to_have_attribute("src", "/static/flags/nz.gif")

    def test_the_country_chosen_is_held_with_its_flag_and_posts_its_code(
        self, fetched_page
    ):
        search(fetched_page, "autocomplete_country", "zeal")
        fetched_page.locator(
            '#id_autocomplete_country-ts-dropdown .option[data-value="NZ"]'
        ).click()

        item = fetched_page.locator("#id_autocomplete_country + .ts-wrapper .item")

        assert row_order(item) == ["IMG", "SPAN"]
        expect(item).to_have_text("New Zealand")
        assert (
            fetched_page.evaluate(
                "document.getElementById('id_autocomplete_country').value"
            )
            == "NZ"
        )

    def test_several_countries_are_chosen_with_a_remove_button_each(self, fetched_page):
        for text, code in (("zeal", "NZ"), ("germ", "DE")):
            search(fetched_page, "autocomplete_countries", text)
            fetched_page.locator(
                f'#id_autocomplete_countries-ts-dropdown .option[data-value="{code}"]'
            ).click()

        items = fetched_page.locator("#id_autocomplete_countries + .ts-wrapper .item")

        expect(items).to_have_count(2)
        expect(items.locator(".remove")).to_have_count(2)
        assert fetched_page.evaluate(
            "[...document.getElementById('id_autocomplete_countries').selectedOptions]"
            ".map((option) => option.value)"
        ) == ["NZ", "DE"]

    def test_the_page_raises_no_error(self, fetched_page, page_errors):
        search(fetched_page, "autocomplete_country", "zeal")
        fetched_page.locator(
            '#id_autocomplete_country-ts-dropdown .option[data-value="NZ"]'
        ).click()

        assert page_errors == []


@pytest.fixture
def first_page(page, page_errors, live_server):
    """Open the demo page whose country controls list three countries first."""
    page.route("https://cdn.jsdelivr.net/**", lambda route: route.abort())
    page.goto(f"{live_server.url}/examples/countries/first/")
    page.wait_for_load_state("load")
    return page


def values_listed(page, name):
    """Return the values of the options a control lists, in order."""
    return page.locator(f"#id_{name}-ts-dropdown .option").evaluate_all(
        "(options) => options.map((option) => option.dataset.value)"
    )


class TestCountriesFirst:
    def test_a_single_control_starts_holding_no_country(self, first_page):
        held = first_page.evaluate(
            "document.getElementById('id_country_select_first').tomselect.items"
        )

        assert held == []

    def test_the_countries_first_are_listed_above_the_heading_and_the_rest(
        self, first_page
    ):
        first_page.locator(CONTROL.format("country_select_first")).click()

        assert values_listed(first_page, "country_select_first")[:3] == [
            "DE",
            "AT",
            "CH",
        ]
        heading = first_page.locator(
            "#id_country_select_first-ts-dropdown .optgroup-header"
        )
        expect(heading).to_have_text("Other")

    def test_the_break_is_a_heading_and_never_an_option_to_choose(self, first_page):
        first_page.locator(CONTROL.format("country_select_first")).click()

        options = first_page.locator("#id_country_select_first-ts-dropdown .option")

        expect(options.filter(has_text="Other")).to_have_count(0)

    def test_a_search_lists_the_matches_among_the_countries_first_above_the_rest(
        self, first_page
    ):
        search(first_page, "country_select_first", "ma")
        dropdown = "#id_country_select_first-ts-dropdown"
        expect(
            first_page.locator(f'{dropdown} .option[data-value="AT"]')
        ).to_have_count(0)

        above_the_heading = first_page.evaluate(
            """(dropdown) => {
              const heading = document.querySelector(dropdown + " .optgroup-header");
              const german = document.querySelector(
                dropdown + ' .option[data-value="DE"]');
              return Boolean(
                german.compareDocumentPosition(heading)
                & Node.DOCUMENT_POSITION_FOLLOWING);
            }""",
            dropdown,
        )

        assert above_the_heading

    def test_the_page_raises_no_error(self, first_page, page_errors):
        dropdown = first_page.locator("#id_country_select_first-ts-dropdown")
        first_page.locator(CONTROL.format("country_select_first")).click()
        expect(dropdown).to_be_visible()
        first_page.keyboard.press("Escape")
        expect(dropdown).to_be_hidden()
        first_page.locator(CONTROL.format("country_select_multiple_first")).click()

        assert page_errors == []


class TestFetchedCountriesFirst:
    def test_the_countries_first_come_first_and_the_rest_under_the_heading(
        self, fetched_page
    ):
        fetched_page.locator(CONTROL.format("autocomplete_country_first")).click()
        dropdown = "#id_autocomplete_country_first-ts-dropdown"

        expect(fetched_page.locator(f"{dropdown} .option").first).to_be_visible()

        assert values_listed(fetched_page, "autocomplete_country_first")[:3] == [
            "DE",
            "AT",
            "CH",
        ]
        expect(fetched_page.locator(f"{dropdown} .optgroup-header")).to_have_text(
            "Other"
        )

    def test_a_search_lists_the_matches_among_the_countries_first_above_the_rest(
        self, fetched_page
    ):
        search(fetched_page, "autocomplete_country_first", "ma")
        dropdown = "#id_autocomplete_country_first-ts-dropdown"
        expect(
            fetched_page.locator(f'{dropdown} .option[data-value="DE"]')
        ).to_be_visible()

        above_the_heading = fetched_page.evaluate(
            """(dropdown) => {
              const heading = document.querySelector(dropdown + " .optgroup-header");
              const german = document.querySelector(
                dropdown + ' .option[data-value="DE"]');
              return Boolean(
                german.compareDocumentPosition(heading)
                & Node.DOCUMENT_POSITION_FOLLOWING);
            }""",
            dropdown,
        )

        assert above_the_heading

    def test_a_country_chosen_posts_its_code(self, fetched_page):
        search(fetched_page, "autocomplete_country_first", "aus")
        fetched_page.locator(
            '#id_autocomplete_country_first-ts-dropdown .option[data-value="AT"]'
        ).click()

        value = fetched_page.evaluate(
            "document.getElementById('id_autocomplete_country_first').value"
        )

        assert value == "AT"
