"""The partial date field cleans text to a date that exists, or says why not."""

import datetime

import pytest
from django import forms
from django.core.exceptions import ValidationError

from mvp_forms.fields import PartialDateField
from mvp_forms.widgets import PartialDateInput, PartialDateMaskInput, PartialDateSelect
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

    def test_a_datetime_is_shown_as_its_date_with_no_time(self):
        field = PartialDateField()

        assert (
            field.prepare_value(datetime.datetime(2021, 3, 4, 10, 30)) == "2021-03-04"
        )

    def test_a_bound_field_with_an_initial_datetime_shows_its_date_and_cleans_it(self):
        form = partial_date_form()(initial={"born": datetime.datetime(2021, 3, 4, 10)})

        assert form["born"].value() == "2021-03-04"
        assert form.fields["born"].clean(form["born"].value()) == "2021-03-04"

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

    @pytest.mark.parametrize(
        ("options", "typed", "code"),
        [
            ({"coarsest": "month"}, "2021", "needs_month"),
            ({"coarsest": "day"}, "2021", "needs_day"),
            ({"coarsest": "day"}, "2021-03", "needs_day"),
            ({"resolution": "month"}, "2021-03-04", "too_fine_day"),
            ({"resolution": "year"}, "2021-03", "too_fine_month"),
            ({"resolution": "year"}, "2021-03-04", "too_fine_month"),
        ],
    )
    def test_a_value_outside_the_precisions_stated_is_refused_with_its_own_code(
        self, options, typed, code
    ):
        form = submit(typed, **options)

        assert codes(form) == [code]

    @pytest.mark.parametrize(
        ("options", "typed"),
        [
            ({"coarsest": "month"}, "2021-03"),
            ({"coarsest": "month"}, "2021-03-04"),
            ({"coarsest": "day"}, "2021-03-04"),
            ({"resolution": "month"}, "2021"),
            ({"resolution": "month"}, "2021-03"),
            ({"resolution": "year"}, "2021"),
            ({"coarsest": "month", "resolution": "month"}, "2021-03"),
        ],
    )
    def test_a_value_inside_the_precisions_stated_is_cleaned(self, options, typed):
        form = submit(typed, **options)

        assert form.is_valid()
        assert form.cleaned_data["born"] == typed

    def test_a_value_that_is_not_a_date_is_refused_before_its_precision_is_checked(
        self,
    ):
        form = submit("2021-02-30", coarsest="day", resolution="day")

        assert codes(form) == ["day"]

    @pytest.mark.parametrize(
        ("options", "named"),
        [
            ({"coarsest": "week"}, ["coarsest"]),
            ({"resolution": "hour"}, ["resolution"]),
            ({"coarsest": "day", "resolution": "month"}, ["coarsest", "resolution"]),
            ({"coarsest": "month", "resolution": "year"}, ["coarsest", "resolution"]),
        ],
    )
    def test_a_precision_that_cannot_be_held_raises_when_the_form_is_defined(
        self, options, named
    ):
        with pytest.raises(ValueError) as raised:
            partial_date_form(**options)

        assert all(option in str(raised.value) for option in named)

    @pytest.mark.parametrize(
        "widget", [PartialDateMaskInput, PartialDateInput, PartialDateSelect]
    )
    def test_the_field_tells_each_widget_the_resolution(self, widget):
        form = partial_date_form(resolution="month", widget=widget())()

        assert form["born"].field.widget.resolution == "month"

    def test_a_widget_replaced_in_the_forms_init_is_told_the_resolution(self):
        class Form(forms.Form):
            born = PartialDateField(resolution="month")

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["born"].widget = PartialDateSelect()

        form = Form()

        assert form["born"].field.widget.resolution == "month"

    def test_two_forms_of_one_class_with_different_widgets_do_not_affect_each_other(
        self,
    ):
        class Form(forms.Form):
            born = PartialDateField(resolution="month", widget=PartialDateMaskInput())

        masked, parts = Form(), Form()
        parts.fields["born"].widget = PartialDateInput()

        assert masked["born"].field.widget.resolution == "month"
        assert parts["born"].field.widget.resolution == "month"
        assert isinstance(masked.fields["born"].widget, PartialDateMaskInput)
        assert Form.base_fields["born"].widget.resolution == "day"
