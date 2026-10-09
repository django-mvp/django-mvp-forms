"""The partial date field cleans text to a date that exists, or says why not."""

import datetime

import pytest
from django.core.exceptions import ValidationError

from mvp_forms.fields import PartialDateField
from tests.forms import PartialDateForm, partial_date_form

LEAP_YEAR = 2024
COMMON_YEAR = 2023
LAST_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}
LEAP_LAST_DAYS = {**LAST_DAYS, 2: 29}
MONTHS = [(year, month) for year in (LEAP_YEAR, COMMON_YEAR) for month in LAST_DAYS]
EVERY_MONTH = [
    (year, month, (LEAP_LAST_DAYS if year == LEAP_YEAR else LAST_DAYS)[month])
    for year, month in MONTHS
]


def codes(form):
    return [error.code for error in form.errors.as_data().get("born", [])]


def submit(value, **options):
    form = partial_date_form(**options)({"born": value})
    form.full_clean()
    return form


class TestPartialDateField:
    @pytest.mark.parametrize(
        ("typed", "cleaned"),
        [
            ("2021", "2021"),
            ("2021-03", "2021-03"),
            ("2021-3", "2021-03"),
            ("2021-03-04", "2021-03-04"),
            ("2021-3-4", "2021-03-04"),
            ("2021-12-31", "2021-12-31"),
        ],
    )
    def test_a_year_a_year_and_month_or_a_full_date_cleans_to_padded_iso_text(
        self, typed, cleaned
    ):
        form = PartialDateForm({"born": typed})

        assert form.is_valid()
        assert form.cleaned_data["born"] == cleaned

    @pytest.mark.parametrize(
        ("typed", "cleaned"), [("2021-", "2021"), ("2021-3-", "2021-03")]
    )
    def test_one_trailing_hyphen_is_dropped(self, typed, cleaned):
        form = PartialDateForm({"born": typed})

        assert form.is_valid()
        assert form.cleaned_data["born"] == cleaned

    def test_surrounding_space_is_dropped(self):
        form = PartialDateForm({"born": " 2021-03-04 "})

        assert form.is_valid()
        assert form.cleaned_data["born"] == "2021-03-04"

    @pytest.mark.parametrize("data", [{"born": ""}, {"born": "   "}, {}])
    def test_an_empty_optional_value_cleans_to_an_empty_string(self, data):
        form = PartialDateForm(data)

        assert form.is_valid()
        assert form.cleaned_data["born"] == ""

    def test_a_required_field_refuses_an_empty_value(self):
        form = submit("")

        assert codes(form) == ["required"]

    @pytest.mark.parametrize(("year", "month", "last"), EVERY_MONTH)
    def test_the_last_day_of_each_month_exists_and_the_day_after_it_does_not(
        self, year, month, last
    ):
        existing = submit(f"{year}-{month:02}-{last:02}")
        missing = submit(f"{year}-{month:02}-{last + 1:02}")

        assert existing.is_valid()
        assert codes(missing) == ["day"]

    @pytest.mark.parametrize(
        ("typed", "exists"),
        [("1900-02-29", False), ("2000-02-29", True), ("2100-02-29", False)],
    )
    def test_a_century_year_is_a_leap_year_only_when_divisible_by_four_hundred(
        self, typed, exists
    ):
        assert submit(typed).is_valid() is exists

    @pytest.mark.parametrize(
        ("typed", "code"),
        [
            ("abc", "invalid"),
            ("2021/03/04", "invalid"),
            ("2021-03-04-05", "invalid"),
            ("2021 -03", "invalid"),
            ("-", "invalid"),
            ("2021-1a", "invalid"),
            ("\uff12\uff10\uff12\uff11", "invalid"),
            ("\u0662\u0660\u0662\u0661", "invalid"),
            ("2021-\u06603", "invalid"),
            ("2021--", "invalid"),
            ("2021---", "invalid"),
            ("2021-03--", "invalid"),
            ("202", "year"),
            ("20211", "year"),
            ("21-03", "year"),
            ("0000", "year"),
            ("0000-01-01", "year"),
            ("2021-13", "month"),
            ("2021-00", "month"),
            ("2021-0", "month"),
            ("2021-001", "month"),
            ("2021-13-01", "month"),
            ("2021-02-30", "day"),
            ("2021-04-31", "day"),
            ("2021-01-00", "day"),
            ("2021-01-0", "day"),
            ("2021-01-32", "day"),
            ("2021-01-001", "day"),
            ("2023-02-29", "day"),
            ("-03", "no_year"),
            ("-03-04", "no_year"),
            ("--14", "no_year"),
            ("2021--14", "no_month"),
        ],
    )
    def test_each_way_a_value_can_be_wrong_raises_its_own_code(self, typed, code):
        form = submit(typed)

        assert codes(form) == [code]

    def test_a_python_date_is_shown_as_iso_text(self):
        field = PartialDateField()

        assert field.prepare_value(datetime.date(2021, 3, 4)) == "2021-03-04"

    def test_a_bound_field_with_an_initial_date_shows_it_as_iso_text(self):
        form = PartialDateForm(initial={"born": datetime.date(2021, 3, 4)})

        assert form["born"].value() == "2021-03-04"

    def test_a_disabled_field_keeps_its_initial_value(self):
        form = partial_date_form(disabled=True)(
            {"born": "1999"}, initial={"born": datetime.date(2021, 3, 4)}
        )

        assert form.is_valid()
        assert form.cleaned_data["born"] == "2021-03-04"

    def test_a_validator_runs_on_the_cleaned_text(self):
        def refuse_the_first_of_january(value):
            if value.endswith("-01-01"):
                raise ValidationError("No.", code="first_of_january")

        form = submit("2021-1-1", validators=[refuse_the_first_of_january])

        assert codes(form) == ["first_of_january"]

    def test_a_developers_own_error_message_replaces_the_default(self):
        form = submit("2021-13", error_messages={"month": "Pick a real month."})

        assert form.errors["born"] == ["Pick a real month."]
