"""The fields clean text to a date that exists or a coordinate in range, or say why not."""

import datetime
from decimal import Decimal

import pytest
from django import forms
from django.core.exceptions import ValidationError
from django.utils import translation

from mvp_forms.fields import LatitudeField, LongitudeField, PartialDateField
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

    @pytest.mark.parametrize(
        "initial",
        [datetime.date(2021, 3, 4), datetime.datetime(2021, 3, 4, 10, 30)],
    )
    def test_an_initial_date_sent_back_as_the_same_iso_text_is_not_a_change(
        self, initial
    ):
        field = PartialDateField(required=False)

        assert field.has_changed(initial, "2021-03-04") is False

    @pytest.mark.parametrize(
        "initial",
        [datetime.date(2021, 3, 4), datetime.datetime(2021, 3, 4, 10, 30)],
    )
    def test_an_initial_date_sent_back_as_another_value_is_a_change(self, initial):
        field = PartialDateField(required=False)

        assert field.has_changed(initial, "2021-03-05") is True
        assert field.has_changed(initial, "2021-03") is True

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
            ({"min_resolution": "month"}, "2021", "needs_month"),
            ({"min_resolution": "day"}, "2021", "needs_day"),
            ({"min_resolution": "day"}, "2021-03", "needs_day"),
            ({"max_resolution": "month"}, "2021-03-04", "day_not_allowed"),
            ({"max_resolution": "year"}, "2021-03", "month_not_allowed"),
            ({"max_resolution": "year"}, "2021-03-04", "month_not_allowed"),
        ],
    )
    def test_a_value_outside_the_resolutions_stated_is_refused_with_its_own_code(
        self, options, typed, code
    ):
        form = submit(typed, **options)

        assert codes(form) == [code]

    @pytest.mark.parametrize(
        ("options", "typed"),
        [
            ({"min_resolution": "month"}, "2021-03"),
            ({"min_resolution": "month"}, "2021-03-04"),
            ({"min_resolution": "day"}, "2021-03-04"),
            ({"max_resolution": "month"}, "2021"),
            ({"max_resolution": "month"}, "2021-03"),
            ({"max_resolution": "year"}, "2021"),
            ({"min_resolution": "month", "max_resolution": "month"}, "2021-03"),
        ],
    )
    def test_a_value_inside_the_resolutions_stated_is_cleaned(self, options, typed):
        form = submit(typed, **options)

        assert form.is_valid()
        assert form.cleaned_data["born"] == typed

    def test_a_value_that_is_not_a_date_is_refused_before_its_resolution_is_checked(
        self,
    ):
        form = submit("2021-02-30", min_resolution="day", max_resolution="day")

        assert codes(form) == ["day"]

    @pytest.mark.parametrize(
        ("options", "named"),
        [
            ({"min_resolution": "week"}, ["min_resolution"]),
            ({"max_resolution": "hour"}, ["max_resolution"]),
            (
                {"min_resolution": "day", "max_resolution": "month"},
                ["min_resolution", "max_resolution"],
            ),
            (
                {"min_resolution": "month", "max_resolution": "year"},
                ["min_resolution", "max_resolution"],
            ),
        ],
    )
    def test_a_resolution_that_cannot_be_held_raises_when_the_form_is_defined(
        self, options, named
    ):
        with pytest.raises(ValueError) as raised:
            partial_date_form(**options)

        assert all(option in str(raised.value) for option in named)

    @pytest.mark.parametrize(
        "widget", [PartialDateMaskInput, PartialDateInput, PartialDateSelect]
    )
    def test_the_field_tells_each_widget_the_max_resolution(self, widget):
        form = partial_date_form(max_resolution="month", widget=widget())()

        assert form["born"].field.widget.max_resolution == "month"

    def test_a_widget_replaced_in_the_forms_init_is_told_the_max_resolution(self):
        class Form(forms.Form):
            born = PartialDateField(max_resolution="month")

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["born"].widget = PartialDateSelect()

        form = Form()

        assert form["born"].field.widget.max_resolution == "month"

    def test_two_forms_of_one_class_with_different_widgets_do_not_affect_each_other(
        self,
    ):
        class Form(forms.Form):
            born = PartialDateField(
                max_resolution="month", widget=PartialDateMaskInput()
            )

        masked, parts = Form(), Form()
        parts.fields["born"].widget = PartialDateInput()

        assert masked["born"].field.widget.max_resolution == "month"
        assert parts["born"].field.widget.max_resolution == "month"
        assert isinstance(masked.fields["born"].widget, PartialDateMaskInput)
        assert Form.base_fields["born"].widget.max_resolution == "day"

    @pytest.mark.parametrize(
        ("limit", "typed"),
        [
            ("1998-03-15", "1998"),
            ("1998-03-15", "1998-03"),
            ("1998-03-15", "1998-03-15"),
            ("1998-03-15", "2004-09-30"),
            ("1998-03", "1998-03-01"),
            ("1998-03", "1998-03"),
            ("1998", "1998-01-01"),
            ("1998", "1998"),
        ],
    )
    def test_a_value_on_or_after_the_earliest_date_is_cleaned(self, limit, typed):
        form = submit(typed, min_value=limit)

        assert form.is_valid()
        assert form.cleaned_data["born"] == typed

    @pytest.mark.parametrize(
        ("limit", "typed"),
        [
            ("1998-03-15", "1997"),
            ("1998-03-15", "1998-02"),
            ("1998-03-15", "1998-03-14"),
            ("1998-03", "1998-02-28"),
            ("1998-03", "1998-02"),
            ("1998", "1997-12-31"),
            ("1998", "1997"),
        ],
    )
    def test_a_value_before_the_earliest_date_is_refused_with_min_value(
        self, limit, typed
    ):
        form = submit(typed, min_value=limit)

        assert codes(form) == ["min_value"]

    @pytest.mark.parametrize(
        ("limit", "typed"),
        [
            ("1998-03-15", "1998"),
            ("1998-03-15", "1998-03"),
            ("1998-03-15", "1998-03-15"),
            ("1998-03-15", "1997-12-31"),
            ("1998-03", "1998-03-31"),
            ("1998-03", "1998-03"),
            ("1998", "1998-12-31"),
            ("1998", "1998"),
        ],
    )
    def test_a_value_on_or_before_the_latest_date_is_cleaned(self, limit, typed):
        form = submit(typed, max_value=limit)

        assert form.is_valid()
        assert form.cleaned_data["born"] == typed

    @pytest.mark.parametrize(
        ("limit", "typed"),
        [
            ("1998-03-15", "1999"),
            ("1998-03-15", "1998-04"),
            ("1998-03-15", "1998-03-16"),
            ("1998-03", "1998-04-01"),
            ("1998-03", "1998-04"),
            ("1998", "1999-01-01"),
            ("1998", "1999"),
        ],
    )
    def test_a_value_after_the_latest_date_is_refused_with_max_value(
        self, limit, typed
    ):
        form = submit(typed, max_value=limit)

        assert codes(form) == ["max_value"]

    @pytest.mark.parametrize(
        ("typed", "expected"),
        [
            ("1997-12-31", ["min_value"]),
            ("1998-03-14", ["min_value"]),
            ("1998-03-15", []),
            ("2000", []),
            ("2004-09-30", []),
            ("2004-10-01", ["max_value"]),
            ("2004-10", ["max_value"]),
            ("2005", ["max_value"]),
        ],
    )
    def test_a_field_with_both_limits_refuses_a_value_beyond_either(
        self, typed, expected
    ):
        form = submit(typed, min_value="1998-03-15", max_value="2004-09")

        assert codes(form) == expected

    def test_a_python_date_is_taken_as_a_limit_and_given_in_the_error(self):
        form = submit("1998-03-14", min_value=datetime.date(1998, 3, 15))

        error = form.errors.as_data()["born"][0]

        assert error.code == "min_value"
        assert error.params == {"limit": "1998-03-15"}

    @pytest.mark.parametrize(
        ("options", "typed", "code", "limit"),
        [
            ({"min_value": "1998-3"}, "1998-02", "min_value", "1998-03"),
            ({"max_value": "1998-3-5"}, "1998-03-06", "max_value", "1998-03-05"),
        ],
    )
    def test_the_limit_in_the_error_is_padded_iso_text(
        self, options, typed, code, limit
    ):
        form = submit(typed, **options)

        error = form.errors.as_data()["born"][0]

        assert error.code == code
        assert error.params == {"limit": limit}

    @pytest.mark.parametrize("data", [{"born": ""}, {}])
    def test_an_empty_optional_value_is_not_compared_with_the_limits(self, data):
        form = partial_date_form(required=False, min_value="1998", max_value="2004")(
            data
        )

        assert form.is_valid()
        assert form.cleaned_data["born"] == ""

    def test_the_limits_apply_after_the_value_is_known_to_be_a_date(self):
        form = submit("1997-02-30", min_value="1998")

        assert codes(form) == ["day"]

    @pytest.mark.parametrize(
        ("options", "named"),
        [
            ({"min_value": "abc"}, ["min_value"]),
            ({"max_value": "abc"}, ["max_value"]),
            ({"min_value": "1998-13"}, ["min_value"]),
            ({"max_value": "1998-02-30"}, ["max_value"]),
            ({"min_value": "98"}, ["min_value"]),
            ({"max_value": "1998/03/15"}, ["max_value"]),
            ({"min_value": "2004", "max_value": "1998"}, ["min_value", "max_value"]),
            (
                {"min_value": "1998-07", "max_value": "1998-06-30"},
                ["min_value", "max_value"],
            ),
            (
                {
                    "min_value": datetime.date(2004, 9, 1),
                    "max_value": datetime.date(2004, 8, 31),
                },
                ["min_value", "max_value"],
            ),
        ],
    )
    def test_a_limit_that_cannot_be_held_raises_when_the_form_is_defined(
        self, options, named
    ):
        with pytest.raises(ValueError) as raised:
            partial_date_form(**options)

        assert all(option in str(raised.value) for option in named)

    @pytest.mark.parametrize(
        "options",
        [
            {"min_value": "1998-03-15", "max_value": "1998-03-15"},
            {"min_value": "1998", "max_value": "1998-06"},
            {"min_value": "1998-03", "max_value": "1998-03-01"},
        ],
    )
    def test_limits_that_leave_a_day_to_choose_are_held(self, options):
        assert partial_date_form(**options)

    @pytest.mark.parametrize(
        "widget", [PartialDateMaskInput, PartialDateInput, PartialDateSelect]
    )
    def test_the_field_tells_each_widget_the_limits(self, widget):
        form = partial_date_form(
            min_value=datetime.date(1998, 3, 15), max_value="2004-9", widget=widget()
        )()

        told = form["born"].field.widget

        assert (told.min_value, told.max_value) == ("1998-03-15", "2004-09")

    def test_a_widget_replaced_in_the_forms_init_is_told_the_limits(self):
        class Form(forms.Form):
            born = PartialDateField(min_value="1998", max_value="2004")

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["born"].widget = PartialDateSelect()

        told = Form()["born"].field.widget

        assert (told.min_value, told.max_value) == ("1998", "2004")

    def test_a_limit_that_follows_todays_date_is_given_in_the_forms_init(self):
        class Form(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["born"] = PartialDateField(max_value=datetime.date.today())

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        assert Form({"born": today.isoformat()}).is_valid()
        assert Form({"born": tomorrow.isoformat()}).has_error("born", "max_value")


EACH_FIELD = (
    pytest.param(LatitudeField, 90, id="latitude"),
    pytest.param(LongitudeField, 180, id="longitude"),
)


def place_form(field_class, **options):
    class PlaceForm(forms.Form):
        place = field_class(**options)

    return PlaceForm


def place_codes(form):
    return [error.code for error in form.errors.as_data().get("place", [])]


def submit_place(field_class, value, **options):
    form = place_form(field_class, **options)({"place": value})
    form.full_clean()
    return form


class TestCoordinateField:
    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize(
        ("typed", "cleaned"),
        [
            ("51.5", "51.5"),
            ("0", "0"),
            ("-12.345678", "-12.345678"),
            ("-1", "-1"),
            ("+1.5", "1.5"),
            (".5", "0.5"),
            ("-.5", "-0.5"),
            ("5.", "5"),
            (" 5.25 ", "5.25"),
            ("0.000001", "0.000001"),
        ],
    )
    def test_a_number_in_range_cleans_to_the_decimal_typed(
        self, field_class, limit, typed, cleaned
    ):
        form = submit_place(field_class, typed)

        assert form.cleaned_data["place"] == Decimal(cleaned)
        assert isinstance(form.cleaned_data["place"], Decimal)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_both_ends_of_the_range_are_accepted(self, field_class, limit):
        low = submit_place(field_class, f"-{limit}")
        high = submit_place(field_class, f"{limit}.")
        high_full = submit_place(field_class, f"{limit}.000000")

        assert low.cleaned_data["place"] == Decimal(-limit)
        assert high.cleaned_data["place"] == Decimal(limit)
        assert high_full.cleaned_data["place"] == Decimal(limit)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_value_past_the_upper_end_is_refused_with_the_bound(
        self, field_class, limit
    ):
        form = submit_place(field_class, f"{limit}.000001")

        assert place_codes(form) == ["max_value"]
        error = form.errors.as_data()["place"][0]
        assert error.params["limit_value"] == limit
        assert "place" not in form.cleaned_data

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_value_past_the_lower_end_is_refused_with_the_bound(
        self, field_class, limit
    ):
        form = submit_place(field_class, f"-{limit + 1}")

        assert place_codes(form) == ["min_value"]
        error = form.errors.as_data()["place"][0]
        assert error.params["limit_value"] == -limit

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_more_than_six_decimal_places_is_refused_and_not_rounded(
        self, field_class, limit
    ):
        form = submit_place(field_class, "51.5000001")

        assert place_codes(form) == ["max_decimal_places"]
        assert "place" not in form.cleaned_data

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize(
        "typed",
        [
            "abc",
            "51,5",
            "5e1",
            "1E2",
            "inf",
            "-inf",
            "nan",
            "-",
            "+",
            ".",
            "1.2.3",
            "٣",
        ],
    )
    def test_text_that_is_not_a_plain_number_is_invalid(
        self, field_class, limit, typed
    ):
        form = submit_place(field_class, typed)

        assert place_codes(form) == ["invalid"]

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("typed", ["-0", "-0.0", "-0.000000", "+0"])
    def test_minus_zero_cleans_to_zero_without_a_sign(self, field_class, limit, typed):
        cleaned = submit_place(field_class, typed).cleaned_data["place"]

        assert cleaned == 0
        assert not cleaned.is_signed()

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("typed", ["", "   ", None])
    def test_empty_is_none_when_not_required(self, field_class, limit, typed):
        form = submit_place(field_class, typed, required=False)

        assert form.is_valid()
        assert form.cleaned_data["place"] is None

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("typed", ["", "   ", None])
    def test_empty_is_required_when_required(self, field_class, limit, typed):
        form = submit_place(field_class, typed)

        assert place_codes(form) == ["required"]

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize(
        ("given", "cleaned"),
        [
            (0.00005, "0.00005"),
            (-0.00005, "-0.00005"),
            (1.5, "1.5"),
            (3, "3"),
            (Decimal("2.25"), "2.25"),
        ],
    )
    def test_a_number_is_read_as_the_number_it_is(
        self, field_class, limit, given, cleaned
    ):
        field = field_class()

        assert field.clean(given) == Decimal(cleaned)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("given", [float("inf"), float("nan"), Decimal("NaN")])
    def test_a_number_that_is_not_finite_is_invalid(self, field_class, limit, given):
        with pytest.raises(ValidationError) as caught:
            field_class().clean(given)

        assert caught.value.code == "invalid"

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_disabled_field_with_a_float_initial_near_zero_cleans_to_it(
        self, field_class, limit
    ):
        class PlaceForm(forms.Form):
            place = field_class(disabled=True)

        form = PlaceForm(data={}, initial={"place": 0.00005})

        assert form.is_valid()
        assert form.cleaned_data["place"] == Decimal("0.00005")

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("initial", [Decimal("51.5"), 51.5, "51.5"])
    @pytest.mark.parametrize("language", ["en", "de", "fr"])
    def test_the_initial_value_is_shown_with_a_full_stop_in_every_language(
        self, field_class, limit, initial, language
    ):
        form = place_form(field_class)(initial={"place": initial})

        with translation.override(language):
            html = str(form["place"])

        assert 'value="51.5"' in html

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_posted_value_is_not_localised(self, field_class, limit):
        with translation.override("de"):
            form = submit_place(field_class, "51,5")

        assert place_codes(form) == ["invalid"]

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("code", ["invalid", "min_value", "max_value"])
    def test_a_developers_error_message_replaces_the_codes_message(
        self, field_class, limit, code
    ):
        typed = {
            "invalid": "x",
            "min_value": str(-limit - 1),
            "max_value": str(limit + 1),
        }
        form = submit_place(
            field_class, typed[code], error_messages={code: "Mine, %(limit_value)s."}
        )

        assert place_codes(form) == [code]
        assert form.errors["place"][0].startswith("Mine")

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_developers_message_replaces_the_decimal_places_message(
        self, field_class, limit
    ):
        form = submit_place(
            field_class, "1.1234567", error_messages={"max_decimal_places": "Too fine."}
        )

        assert form.errors["place"] == ["Too fine."]

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_developers_validators_run_after_the_field_accepts_the_value(
        self, field_class, limit
    ):
        def not_zero(value):
            if value == 0:
                raise ValidationError("No zero.", code="zero")

        form = submit_place(field_class, "0", validators=[not_zero])

        assert place_codes(form) == ["zero"]

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_disabled_field_keeps_its_initial_value(self, field_class, limit):
        class PlaceForm(forms.Form):
            place = field_class(disabled=True, initial=Decimal("12.5"))

        form = PlaceForm(data={"place": "99"})

        assert form.is_valid()
        assert form.cleaned_data["place"] == Decimal("12.5")

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_the_options_are_stated_on_the_field(self, field_class, limit):
        field = field_class()

        assert field.min_value == -limit
        assert field.max_value == limit
        assert field.decimal_places == 6
        assert field.max_digits is None


class TestCoordinateFieldOptions:
    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_narrower_bounds_are_accepted_and_enforced(self, field_class, limit):
        form = submit_place(field_class, "11", min_value=-10, max_value=10.5)

        assert place_codes(form) == ["max_value"]
        assert form.errors.as_data()["place"][0].params["limit_value"] == 10.5

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize(
        ("bounds", "value", "code", "limit_value"),
        [
            ((40, 60), "35", "min_value", 40),
            ((40, 60), "61", "max_value", 60),
            ((-60, -40), "-35", "max_value", -40),
            ((-60, -40), "-61", "min_value", -60),
        ],
    )
    def test_a_value_outside_a_narrowed_range_names_the_bound_it_broke(
        self, field_class, limit, bounds, value, code, limit_value
    ):
        form = submit_place(
            field_class, value, min_value=bounds[0], max_value=bounds[1]
        )

        assert place_codes(form) == [code]
        assert form.errors.as_data()["place"][0].params["limit_value"] == limit_value

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("value", ["40", "45.5", "60"])
    def test_a_value_inside_a_narrowed_range_is_taken(self, field_class, limit, value):
        form = submit_place(field_class, value, min_value=40, max_value=60)

        assert form.cleaned_data["place"] == Decimal(value)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_the_bounds_of_the_range_itself_are_accepted_as_options(
        self, field_class, limit
    ):
        field = field_class(min_value=-limit, max_value=Decimal(limit))

        assert field.clean(str(limit)) == limit

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_lower_bound_above_zero_is_accepted(self, field_class, limit):
        field = field_class(min_value=5, max_value=10)

        assert field.clean("5") == 5

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_decimal_places_are_stated(self, field_class, limit):
        form = submit_place(field_class, "1.234", decimal_places=2)
        zero = submit_place(field_class, "1.5", decimal_places=0)
        whole = submit_place(field_class, "7", decimal_places=0)

        assert place_codes(form) == ["max_decimal_places"]
        assert place_codes(zero) == ["max_decimal_places"]
        assert whole.cleaned_data["place"] == 7

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("option", ["min_value", "max_value"])
    @pytest.mark.parametrize("bound", ["5", True, float("inf"), float("nan"), [1]])
    def test_a_bound_that_is_not_a_finite_number_names_the_option(
        self, field_class, limit, option, bound
    ):
        with pytest.raises(ValueError, match=option):
            field_class(**{option: bound})

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize(
        ("option", "bound"),
        [("min_value", -1), ("max_value", 1)],
    )
    def test_a_bound_outside_the_range_names_the_option(
        self, field_class, limit, option, bound
    ):
        stated = bound * (limit + 1)

        with pytest.raises(ValueError, match=option):
            field_class(**{option: stated})

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_a_lower_bound_above_the_upper_names_the_option(self, field_class, limit):
        with pytest.raises(ValueError, match="min_value"):
            field_class(min_value=10, max_value=5)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    @pytest.mark.parametrize("places", [-1, 1.5, "2", True, None])
    def test_decimal_places_that_are_not_a_whole_number_name_the_option(
        self, field_class, limit, places
    ):
        with pytest.raises(ValueError, match="decimal_places"):
            field_class(decimal_places=places)

    @pytest.mark.parametrize(("field_class", "limit"), [*EACH_FIELD])
    def test_equal_bounds_are_accepted(self, field_class, limit):
        field = field_class(min_value=3, max_value=3)

        assert field.clean("3") == 3
