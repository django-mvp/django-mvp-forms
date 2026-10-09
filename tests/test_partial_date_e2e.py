"""The script that keeps a three-part date in step, run in Chrome with no IMask."""

import json

import pytest
from django.urls import reverse
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e

FIELDS = ["typed", "listed"]
# Records each listener for the events the script reacts to, and each observer.
RECORD_REGISTRATIONS = """
window.registered = [];
const add = EventTarget.prototype.addEventListener;
EventTarget.prototype.addEventListener = function (type, ...rest) {
  if (type === "input" || type === "change") window.registered.push(type);
  return add.call(this, type, ...rest);
};
const Observer = window.MutationObserver;
window.MutationObserver = function (...args) {
  window.registered.push("observer");
  return new Observer(...args);
};
"""
INSERT_LINE = """
document.getElementById("dates").append(
  document.getElementById("line").content.cloneNode(true));
"""
VALUES = "(node) => Array.from(node.options, (option) => option.value)"
IS_SELECT = "(node) => node.tagName === 'SELECT'"
# Sets a value and sends one kind of event only, as a script of the host's might.
SET_AND_SEND = """
(node, [value, type]) => {
  node.value = value;
  node.dispatchEvent(new Event(type, { bubbles: true }));
}
"""


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def requests_made(page):
    """The addresses the page asks for, as they are asked."""
    asked = []
    page.on("request", lambda request: asked.append(request.url))
    return asked


@pytest.fixture
def dates_page(page, page_errors, live_server):
    """Open a page of three-part dates of the test project."""

    def open_page(name="dates", **entries):
        query = "&".join(f"{key}={value}" for key, value in entries.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def part(page, field, which, prefix=""):
    """Return one part of a field's group."""
    return page.locator(f'[name="{prefix}{field}_{which}"]')


def enter_year(page, field, year, prefix=""):
    """Type a year into a text input, or choose it in a select."""
    year_part = part(page, field, "year", prefix)
    if year_part.evaluate(IS_SELECT):
        year_part.select_option(year)
    else:
        year_part.fill(year)


def offered(page, field, which, prefix=""):
    """Return the values on offer in a month or a day, without the empty one."""
    return [
        value
        for value in part(page, field, which, prefix).evaluate(VALUES)
        if value != ""
    ]


def submit(page):
    """Send the form and return what the page answered."""
    with page.expect_navigation():
        page.click("button[type=submit]")
    return json.loads(page.inner_text("body"))


class TestPartialDateScript:
    @pytest.mark.parametrize("field", FIELDS)
    def test_no_month_can_be_chosen_until_a_year_is_entered(self, dates_page, field):
        page = dates_page()

        expect(part(page, field, "month")).to_be_disabled()

        enter_year(page, field, "2021")

        expect(part(page, field, "month")).to_be_enabled()

    def test_no_month_can_be_chosen_until_the_year_has_four_digits(self, dates_page):
        page = dates_page()

        enter_year(page, "typed", "202")

        expect(part(page, "typed", "month")).to_be_disabled()

        enter_year(page, "typed", "2021")

        expect(part(page, "typed", "month")).to_be_enabled()

    @pytest.mark.parametrize("kind", ["input", "change"])
    def test_either_an_input_or_a_change_event_is_enough(self, dates_page, kind):
        page = dates_page()

        part(page, "typed", "year").evaluate(SET_AND_SEND, ["2021", kind])

        expect(part(page, "typed", "month")).to_be_enabled()

    @pytest.mark.parametrize("field", FIELDS)
    def test_no_day_can_be_chosen_until_a_month_is_chosen(self, dates_page, field):
        page = dates_page()
        enter_year(page, field, "2021")

        expect(part(page, field, "day")).to_be_disabled()

        part(page, field, "month").select_option("03")

        expect(part(page, field, "day")).to_be_enabled()

    @pytest.mark.parametrize("field", FIELDS)
    def test_clearing_the_year_closes_the_month_and_the_day_and_empties_them(
        self, dates_page, field
    ):
        page = dates_page()
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("03")
        part(page, field, "day").select_option("14")

        enter_year(page, field, "")

        expect(part(page, field, "month")).to_be_disabled()
        expect(part(page, field, "day")).to_be_disabled()
        assert part(page, field, "month").input_value() == ""
        assert part(page, field, "day").input_value() == ""

    @pytest.mark.parametrize("field", FIELDS)
    @pytest.mark.parametrize(
        ("year", "month", "days"),
        [
            ("2021", "01", 31),
            ("2021", "04", 30),
            ("2021", "02", 28),
            ("2020", "02", 29),
            ("2000", "02", 29),
        ],
    )
    def test_the_days_offered_are_the_days_the_month_has_in_that_year(
        self, dates_page, field, year, month, days
    ):
        page = dates_page()
        enter_year(page, field, year)

        part(page, field, "month").select_option(month)

        assert offered(page, field, "day") == [
            f"{day:02}" for day in range(1, days + 1)
        ]

    def test_a_year_divisible_by_100_and_not_by_400_has_no_29th_of_february(
        self, dates_page
    ):
        page = dates_page()
        enter_year(page, "typed", "2100")

        part(page, "typed", "month").select_option("02")

        assert offered(page, "typed", "day")[-1] == "28"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_day_the_month_does_not_have_is_not_in_the_list(self, dates_page, field):
        page = dates_page()
        enter_year(page, field, "2021")

        part(page, field, "month").select_option("02")

        assert "30" not in offered(page, field, "day")
        assert "31" not in offered(page, field, "day")
        assert page.locator(f'[name="{field}_day"] option[hidden]').count() == 0

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_chosen_31st_is_cleared_when_the_month_becomes_february(
        self, dates_page, field
    ):
        page = dates_page()
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("03")
        part(page, field, "day").select_option("31")

        part(page, field, "month").select_option("02")

        assert part(page, field, "day").input_value() == ""
        assert part(page, field, "month").input_value() == "02"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_chosen_29th_of_february_is_cleared_when_the_year_stops_being_leap(
        self, dates_page, field
    ):
        page = dates_page()
        enter_year(page, field, "2020")
        part(page, field, "month").select_option("02")
        part(page, field, "day").select_option("29")

        enter_year(page, field, "2021")

        assert part(page, field, "day").input_value() == ""
        assert part(page, field, "month").input_value() == "02"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_day_the_new_month_still_has_is_kept(self, dates_page, field):
        page = dates_page()
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("03")
        part(page, field, "day").select_option("15")

        part(page, field, "month").select_option("04")

        assert part(page, field, "day").input_value() == "15"

    @pytest.mark.parametrize("field", FIELDS)
    def test_the_days_return_when_the_month_has_them_again(self, dates_page, field):
        page = dates_page()
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("02")

        part(page, field, "month").select_option("03")

        assert offered(page, field, "day")[-1] == "31"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_form_drawn_holding_the_30th_of_february_shows_what_was_sent(
        self, dates_page, field
    ):
        page = dates_page(
            bound=1,
            **{f"{field}_year": "2021", f"{field}_month": "02", f"{field}_day": "30"},
        )

        assert part(page, field, "year").input_value() == "2021"
        assert part(page, field, "month").input_value() == "02"
        assert part(page, field, "day").input_value() == "30"
        expect(part(page, field, "day")).to_be_enabled()

    @pytest.mark.parametrize("field", FIELDS)
    def test_what_was_sent_is_cleared_once_the_person_changes_a_part(
        self, dates_page, field
    ):
        page = dates_page(
            bound=1,
            **{f"{field}_year": "2021", f"{field}_month": "02", f"{field}_day": "30"},
        )

        enter_year(page, field, "2022")

        assert part(page, field, "day").input_value() == ""
        assert part(page, field, "month").input_value() == "02"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_form_drawn_holding_a_day_with_no_month_shows_what_was_sent(
        self, dates_page, field
    ):
        page = dates_page(
            bound=1,
            **{f"{field}_year": "2021", f"{field}_month": "", f"{field}_day": "14"},
        )

        assert part(page, field, "year").input_value() == "2021"
        assert part(page, field, "month").input_value() == ""
        assert part(page, field, "day").input_value() == "14"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_day_with_no_month_is_cleared_once_the_person_changes_the_year(
        self, dates_page, field
    ):
        page = dates_page(
            bound=1,
            **{f"{field}_year": "2021", f"{field}_month": "", f"{field}_day": "14"},
        )

        enter_year(page, field, "2022")

        assert part(page, field, "day").input_value() == ""

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_month_with_no_year_shows_what_was_sent(self, dates_page, field):
        page = dates_page(
            bound=1, **{f"{field}_year": "", f"{field}_month": "03", f"{field}_day": ""}
        )

        assert part(page, field, "month").input_value() == "03"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_value_the_form_was_given_is_shown_in_its_parts(self, dates_page, field):
        page = dates_page(**{field: "2020-02-29"})

        assert part(page, field, "year").input_value() == "2020"
        assert part(page, field, "month").input_value() == "02"
        assert part(page, field, "day").input_value() == "29"
        assert offered(page, field, "day")[-1] == "29"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_group_added_later_behaves_the_same(self, dates_page, field):
        page = dates_page()
        prefix = "form-__prefix__-"

        page.evaluate(INSERT_LINE)

        expect(part(page, field, "month", prefix)).to_be_disabled()
        enter_year(page, field, "2021", prefix)
        expect(part(page, field, "month", prefix)).to_be_enabled()
        part(page, field, "month", prefix).select_option("02")
        assert offered(page, field, "day", prefix)[-1] == "28"

    def test_the_script_included_more_than_once_acts_once(self, dates_page, page):
        page.add_init_script(RECORD_REGISTRATIONS)
        dates_page("dates")
        once = page.evaluate("window.registered")

        dates_page("dates-copies")
        thrice = page.evaluate("window.registered")

        assert once
        assert thrice == once

    @pytest.mark.parametrize("field", FIELDS)
    def test_the_script_included_more_than_once_still_follows_the_calendar(
        self, dates_page, field
    ):
        page = dates_page("dates-copies")
        enter_year(page, field, "2021")

        part(page, field, "month").select_option("02")

        assert offered(page, field, "day")[-1] == "28"

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_page_without_the_script_offers_twelve_months_and_31_days(
        self, dates_page, field
    ):
        page = dates_page("dates-bare")

        assert len(offered(page, field, "month")) == 12
        assert len(offered(page, field, "day")) == 31
        expect(part(page, field, "month")).to_be_enabled()
        expect(part(page, field, "day")).to_be_enabled()

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_page_without_the_script_submits_the_parts(self, dates_page, field):
        page = dates_page("dates-bare")
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("03")
        part(page, field, "day").select_option("14")

        answer = submit(page)

        assert answer["cleaned"][field] == "2021-03-14"
        assert answer["errors"] == {}

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_page_without_the_script_has_the_field_refuse_a_day_with_no_month(
        self, dates_page, field
    ):
        page = dates_page("dates-bare")
        enter_year(page, field, "2021")
        part(page, field, "day").select_option("14")

        answer = submit(page)

        assert answer["errors"] == {field: ["no_month"]}

    @pytest.mark.parametrize("field", FIELDS)
    def test_a_year_and_a_month_are_submitted_as_they_stand(self, dates_page, field):
        page = dates_page()
        enter_year(page, field, "2021")
        part(page, field, "month").select_option("03")

        answer = submit(page)

        assert answer["cleaned"][field] == "2021-03"
        assert answer["errors"] == {}

    def test_the_page_loads_no_imask_and_the_script_works(
        self, dates_page, page_errors, requests_made
    ):
        page = dates_page()

        enter_year(page, "typed", "2021")
        part(page, "typed", "month").select_option("02")

        assert page.evaluate("typeof window.IMask") == "undefined"
        assert not [url for url in requests_made if "imask" in url.lower()]
        assert offered(page, "typed", "day")[-1] == "28"
        assert page_errors == []
