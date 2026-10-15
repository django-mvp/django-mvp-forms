"""The coordinate kind of the mask script, run in Chrome with IMask 7.6.1."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from django import forms

from mvp_forms.fields import LatitudeField, LongitudeField
from tests.urls import IMASK_URL

pytestmark = pytest.mark.e2e

IMASK = Path(__file__).parent / "data" / "imask-7.6.1.min.js"
PAGE = "/coordinates-test/"
ENTRIES = "Object.fromEntries(new FormData(document.getElementById('place')))"
# Counts each mask the script reports applying, by the id of its input.
COUNT_MASKS = """
window.masked = [];
document.addEventListener("mvp-forms:imask", (event) =>
  window.masked.push(event.target.id));
"""
MASKS_OF = "(id) => window.masked.filter((each) => each === id).length"
INSERT_INPUT = """
(options) => {
  const input = document.createElement("input");
  input.id = "id_later";
  input.name = "later";
  input.dataset.imask = JSON.stringify(options);
  document.getElementById("place").append(input);
}
"""


class PlaceForm(forms.Form):
    latitude = LatitudeField(required=False)
    longitude = LongitudeField(required=False)


class NarrowForm(forms.Form):
    north = LatitudeField(min_value=40, max_value=60, required=False)
    south = LatitudeField(min_value=-60, max_value=-40, required=False)
    rounded = LongitudeField(decimal_places=2, required=False)


def cleaned(entries, form_class=PlaceForm):
    """Return the form a post of these entries gives, validated."""
    form = form_class(entries)
    form.is_valid()
    return form


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def place_page(page, page_errors, live_server):
    """Open a page holding the form, with IMask answered from tests/data."""
    page.route(
        IMASK_URL,
        lambda route: route.fulfill(path=IMASK, content_type="text/javascript"),
    )
    page.add_init_script(COUNT_MASKS)

    def open_page(imask=True, form_class=PlaceForm, **initial):
        form = form_class(initial=initial)
        script = f'<script src="{IMASK_URL}"></script>' if imask else ""
        html = (
            "<!doctype html><html><head><meta charset=utf-8></head><body>"
            f'<form id="place" method="post">{form.as_div()}</form>'
            f"{form.media}{script}</body></html>"
        )
        page.route(
            f"{live_server.url}{PAGE}",
            lambda route: route.fulfill(body=html, content_type="text/html"),
        )
        page.goto(f"{live_server.url}{PAGE}")
        page.wait_for_load_state("load")
        return page

    return open_page


def type_into(page, name, text):
    field = page.locator(f"#id_{name}")
    field.click()
    field.press_sequentially(text)
    return field.input_value()


def entries_of(page):
    """Return what the form would post, with the script's say on each value."""
    return page.evaluate(ENTRIES)


class TestCoordinateMask:
    @pytest.mark.parametrize(
        ("name", "typed", "shown"),
        [
            ("latitude", "90", "90"),
            ("latitude", "91", "9"),
            ("latitude", "-91", "-9"),
            ("latitude", "90.5", "90."),
            ("longitude", "180", "180"),
            ("longitude", "181", "18"),
            ("longitude", "-181", "-18"),
        ],
    )
    def test_typing_past_the_bounds_is_refused(self, place_page, name, typed, shown):
        page = place_page()

        assert type_into(page, name, typed) == shown

    def test_a_seventh_decimal_place_is_refused(self, place_page):
        page = place_page()

        assert type_into(page, "latitude", "51.12345678") == "51.123456"

    def test_a_minus_sign_is_taken_only_at_the_start(self, place_page):
        page = place_page()

        assert type_into(page, "latitude", "5-1") == "51"
        assert type_into(page, "longitude", "-5-1") == "-51"

    def test_a_second_full_stop_is_refused(self, place_page):
        page = place_page()
        type_into(page, "latitude", "1.2")

        page.locator("#id_latitude").press(".")

        assert page.locator("#id_latitude").input_value() == "1.2"

    def test_letters_are_refused(self, place_page):
        page = place_page()

        assert type_into(page, "latitude", "ab") == ""

    def test_a_posted_value_reaches_the_form_as_the_decimal_typed(self, place_page):
        page = place_page()
        type_into(page, "latitude", "51.5074")
        type_into(page, "longitude", "-0.1278")

        form = cleaned(entries_of(page))

        assert form.cleaned_data["latitude"] == Decimal("51.5074")
        assert form.cleaned_data["longitude"] == Decimal("-0.1278")

    def test_a_lone_minus_posts_what_imask_commits(self, place_page):
        page = place_page()
        type_into(page, "latitude", "-")
        page.locator("#id_longitude").click()

        posted = entries_of(page)["latitude"]

        assert posted == "-0"
        assert str(cleaned(entries_of(page)).cleaned_data["latitude"]) == "0"

    def test_without_imask_the_input_is_plain_and_the_field_refuses_the_value(
        self, place_page, page_errors
    ):
        page = place_page(imask=False)

        assert type_into(page, "latitude", "95") == "95"
        assert page_errors == []
        form = cleaned(entries_of(page))
        assert form.has_error("latitude", code="max_value")

    def test_an_input_added_after_the_page_loaded_is_masked_once(self, place_page):
        page = place_page()
        options = json.loads(page.locator("#id_latitude").get_attribute("data-imask"))

        page.evaluate(INSERT_INPUT, options)
        page.wait_for_function("window.masked.includes('id_later')")

        assert page.evaluate(MASKS_OF, "id_later") == 1
        assert type_into(page, "later", "95") == "9"

    def test_an_input_drawn_holding_more_places_than_the_mask_keeps_posts_it(
        self, place_page
    ):
        page = place_page(latitude="51.50740123")

        assert page.locator("#id_latitude").input_value() == "51.50740123"
        assert page.evaluate(MASKS_OF, "id_latitude") == 0
        posted = entries_of(page)
        assert posted["latitude"] == "51.50740123"
        assert cleaned(posted).has_error("latitude", code="max_decimal_places")

    def test_such_an_input_is_masked_once_the_person_edits_it(self, place_page):
        page = place_page(latitude="51.50740123")
        field = page.locator("#id_latitude")
        field.click()
        field.press("End")

        field.press("Backspace")
        field.press("Backspace")

        assert field.input_value() == "51.507401"
        assert page.evaluate(MASKS_OF, "id_latitude") == 1
        field.press("9")
        assert field.input_value() == "51.507401"

    def test_an_input_drawn_holding_a_value_the_mask_takes_is_masked(self, place_page):
        page = place_page(latitude="51.5")

        assert page.evaluate(MASKS_OF, "id_latitude") == 1
        assert page.locator("#id_latitude").input_value() == "51.5"


class TestNarrowedCoordinateMask:
    @pytest.mark.parametrize(
        ("name", "typed", "shown"),
        [
            ("north", "3", ""),
            ("north", "4", "4"),
            ("north", "45", "45"),
            ("north", "45.5", "45.5"),
            ("north", "61", "6"),
            ("north", "9", ""),
            ("south", "-3", "-"),
            ("south", "-4", "-4"),
            ("south", "-45", "-45"),
            ("south", "-45.5", "-45.5"),
            ("south", "-61", "-6"),
            ("rounded", "1.234", "1.23"),
            ("rounded", "-12.5", "-12.5"),
        ],
    )
    def test_typing_past_the_narrowed_bounds_is_refused(
        self, place_page, name, typed, shown
    ):
        page = place_page(form_class=NarrowForm)

        assert type_into(page, name, typed) == shown

    def test_a_value_left_as_typed_is_posted_and_the_field_refuses_it(self, place_page):
        page = place_page(form_class=NarrowForm)
        type_into(page, "north", "4")
        page.locator("#id_south").click()

        posted = entries_of(page)

        assert posted["north"] == "4"
        form = cleaned(posted, NarrowForm)
        assert form.has_error("north", code="min_value")
        assert form.errors.as_data()["north"][0].params["limit_value"] == 40

    def test_an_input_drawn_holding_a_value_below_the_bound_posts_it(self, place_page):
        page = place_page(form_class=NarrowForm, north="35", south="-35")

        assert page.locator("#id_north").input_value() == "35"
        posted = entries_of(page)
        assert posted["north"] == "35"
        assert posted["south"] == "-35"
        form = cleaned(posted, NarrowForm)
        assert form.has_error("north", code="min_value")
        assert form.has_error("south", code="max_value")

    def test_an_input_drawn_holding_a_value_inside_the_bounds_is_masked(
        self, place_page
    ):
        page = place_page(form_class=NarrowForm, north="45.5")

        assert page.evaluate(MASKS_OF, "id_north") == 1
        assert page.locator("#id_north").input_value() == "45.5"

    def test_a_value_typed_inside_the_narrowed_bounds_is_accepted_by_the_field(
        self, place_page
    ):
        page = place_page(form_class=NarrowForm)
        type_into(page, "north", "45.5")
        type_into(page, "south", "-45.5")
        type_into(page, "rounded", "1.23")

        form = cleaned(entries_of(page), NarrowForm)

        assert form.cleaned_data["north"] == Decimal("45.5")
        assert form.cleaned_data["south"] == Decimal("-45.5")
        assert form.cleaned_data["rounded"] == Decimal("1.23")
