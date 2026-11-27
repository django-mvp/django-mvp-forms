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
        "(option) => [...option.querySelectorAll('img, span span')]"
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

        expect(options.locator("img")).to_have_attribute(
            "src", "/static/flags/nz.gif"
        )

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
