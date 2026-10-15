"""Form fields the package offers for needs Django's own do not meet."""

import calendar
import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from mvp_forms.widgets import Check, CoordinateMaskInput, PointInput

RESOLUTIONS = ("year", "month", "day")


class PartialDateField(forms.CharField):
    """A date known to the year, the month or the day, cleaned to ISO text."""

    default_error_messages = {
        "invalid": _("Enter a date as YYYY, YYYY-MM or YYYY-MM-DD."),
        "year": _("Enter the year with four digits."),
        "month": _("Enter a month from 1 to 12."),
        "day": _("That month has no such day."),
        "no_year": _("A month needs a year."),
        "no_month": _("A day needs a month."),
        "needs_month": _("Enter at least a year and a month."),
        "needs_day": _("Enter a full date."),
        "month_not_allowed": _("Enter the year only."),
        "day_not_allowed": _("Enter a year and a month, with no day."),
        "min_value": _("Enter a date no earlier than %(limit)s."),
        "max_value": _("Enter a date no later than %(limit)s."),
    }

    def __init__(
        self,
        *,
        min_resolution="year",
        max_resolution="day",
        min_value=None,
        max_value=None,
        **kwargs,
    ):
        """State the resolutions and the dates the field accepts.

        Args:
            min_resolution: The lowest resolution accepted.
            max_resolution: The highest resolution accepted.
            min_value: The earliest date accepted, as a partial date or a
                Python date.
            max_value: The latest date accepted, as a partial date or a Python
                date.
            **kwargs: Everything a ``CharField`` takes.

        Raises:
            ValueError: A resolution is not one of year, month and day, the
                max_resolution is lower than min_resolution, or the earliest date
                is later than the latest.
        """
        for option, value in (
            ("min_resolution", min_resolution),
            ("max_resolution", max_resolution),
        ):
            if value not in RESOLUTIONS:
                raise ValueError(
                    f"{option} must be one of {', '.join(RESOLUTIONS)}, not {value!r}."
                )
        if RESOLUTIONS.index(max_resolution) < RESOLUTIONS.index(min_resolution):
            raise ValueError(
                f"max_resolution must not be lower than min_resolution, not "
                f"{max_resolution!r} and {min_resolution!r}."
            )
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        super().__init__(**kwargs)
        self.min_value = self.limit("min_value", min_value)
        self.max_value = self.limit("max_value", max_value)
        if (
            self.min_value
            and self.max_value
            and self.span(self.min_value)[0] > self.span(self.max_value)[1]
        ):
            raise ValueError(
                f"min_value must not be later than max_value, not "
                f"{self.min_value!r} and {self.max_value!r}."
            )

    def limit(self, option, value):
        """Return an earliest or latest date as padded ISO text."""
        if value is None:
            return None
        try:
            return self.parse(str(self.prepare_value(value)))
        except ValidationError:
            raise ValueError(
                f"{option} must be a partial date or a date, not {value!r}."
            ) from None

    def get_bound_field(self, form, field_name):
        """Tell the widget the max_resolution and the dates the field accepts."""
        self.widget.max_resolution = self.max_resolution
        self.widget.min_value = self.min_value
        self.widget.max_value = self.max_value
        return super().get_bound_field(form, field_name)

    @staticmethod
    def span(value):
        """Return the first and last day a partial date could be."""
        parts = [int(part) for part in value.split("-")]
        year, month, day = [*parts, 0, 0][:3]
        return (year, month or 1, day or 1), (year, month or 12, day or 31)

    def prepare_value(self, value):
        """Show a Python date, or the date of a datetime, as ISO text."""
        if isinstance(value, datetime.datetime):
            value = value.date()
        if isinstance(value, datetime.date):
            return value.isoformat()
        return value

    def has_changed(self, initial, data):
        """Compare the initial value as the field shows it with what was sent."""
        return super().has_changed(self.prepare_value(initial), data)

    def fail(self, code, **params):
        """Raise the field's error of this code."""
        raise ValidationError(self.error_messages[code], code=code, params=params)

    def to_python(self, value):
        """Return the padded ISO text of what was entered."""
        value = super().to_python(value)
        if value in self.empty_values:
            return ""
        value = self.parse(value)
        given = value.count("-") + 1
        if given <= RESOLUTIONS.index(self.min_resolution):
            self.fail(f"needs_{self.min_resolution}")
        highest = RESOLUTIONS.index(self.max_resolution)
        if given - 1 > highest:
            self.fail(f"{RESOLUTIONS[highest + 1]}_not_allowed")
        first, last = self.span(value)
        if self.min_value and last < self.span(self.min_value)[0]:
            self.fail("min_value", limit=self.min_value)
        if self.max_value and first > self.span(self.max_value)[1]:
            self.fail("max_value", limit=self.max_value)
        return value

    def parse(self, value):
        """Return the padded ISO text of a partial date that exists."""
        parts = value.removesuffix("-").split("-")
        if (
            len(parts) > 3
            or not parts[-1]
            or any(not re.fullmatch("[0-9]*", part) for part in parts)
        ):
            self.fail("invalid")
        year, month, day = [*parts, "", ""][:3]
        if not year:
            self.fail("no_year" if month or day else "invalid")
        if len(year) != 4 or int(year) == 0:
            self.fail("year")
        if day and not month:
            self.fail("no_month")
        if month and (len(month) > 2 or not 1 <= int(month) <= 12):
            self.fail("month")
        if day and (
            len(day) > 2
            or not 1 <= int(day) <= calendar.monthrange(int(year), int(month))[1]
        ):
            self.fail("day")
        given = [part for part in (year, month, day) if part]
        return "-".join([year, *(part.zfill(2) for part in given[1:])])


class CoordinateField(forms.DecimalField):
    """What a latitude and a longitude share: a decimal degree inside a range.

    Attributes:
        limit: The whole number of degrees the range reaches either side of zero.
    """

    limit = 0
    widget = CoordinateMaskInput
    plain_number = re.compile(r"[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)")

    def __init__(self, *, min_value=None, max_value=None, decimal_places=6, **kwargs):
        """State the range and the number of decimal places the field accepts.

        Args:
            min_value: The lowest degree accepted, at least minus the limit.
            max_value: The highest degree accepted, at most the limit.
            decimal_places: The most decimal places accepted.
            **kwargs: Everything a ``DecimalField`` takes but ``max_digits``.

        Raises:
            ValueError: A bound is not a finite number or lies outside the
                range, min_value is above max_value, or decimal_places is not a
                whole number of at least zero.
        """
        bounds = {
            "min_value": -self.limit if min_value is None else min_value,
            "max_value": self.limit if max_value is None else max_value,
        }
        for option, bound in bounds.items():
            Check.number(option, bound)
            if abs(bound) > self.limit:
                raise ValueError(
                    f"{option} must be between {-self.limit} and {self.limit}, "
                    f"not {bound!r}."
                )
        if bounds["min_value"] > bounds["max_value"]:
            raise ValueError(
                f"min_value must not be above max_value, not "
                f"{bounds['min_value']!r} and {bounds['max_value']!r}."
            )
        Check.whole_number("decimal_places", decimal_places)
        if decimal_places < 0:
            raise ValueError(
                f"decimal_places must be at least zero, not {decimal_places!r}."
            )
        super().__init__(decimal_places=decimal_places, **bounds, **kwargs)

    def get_bound_field(self, form, field_name):
        """Tell a ``CoordinateMaskInput`` the decimal places and the bounds."""
        if isinstance(self.widget, CoordinateMaskInput):
            self.widget.scale = self.decimal_places
            self.widget.min_value = self.min_value
            self.widget.max_value = self.max_value
        return super().get_bound_field(form, field_name)

    def to_python(self, value):
        """Return the number as a ``Decimal``, with no sign on a zero.

        Numbers are read as numbers. Text must be a plain number: no exponent,
        no comma, no ``inf`` or ``nan``.
        """
        if isinstance(value, str):
            value = value.strip()
            if value and not self.plain_number.fullmatch(value):
                raise ValidationError(self.error_messages["invalid"], code="invalid")
        number = super().to_python(value)
        if number is not None and number == 0:
            return abs(number)
        return number


class LatitudeField(CoordinateField):
    """A latitude in decimal degrees, from -90 to 90, cleaned to a ``Decimal``."""

    limit = 90
    default_error_messages = {
        "invalid": _("Enter a latitude in decimal degrees."),
        "min_value": _("Enter a latitude of %(limit_value)s or more."),
        "max_value": _("Enter a latitude of %(limit_value)s or less."),
        "max_decimal_places": _(
            "Enter a latitude with no more than %(max)s decimal places."
        ),
    }


class LongitudeField(CoordinateField):
    """A longitude in decimal degrees, from -180 to 180, cleaned to a ``Decimal``."""

    limit = 180
    default_error_messages = {
        "invalid": _("Enter a longitude in decimal degrees."),
        "min_value": _("Enter a longitude of %(limit_value)s or more."),
        "max_value": _("Enter a longitude of %(limit_value)s or less."),
        "max_decimal_places": _(
            "Enter a longitude with no more than %(max)s decimal places."
        ),
    }


class PointField(forms.MultiValueField):
    """A point from a latitude and a longitude, cleaned to WKT text.

    The text carries the spatial reference, ``SRID=4326;POINT(<longitude>
    <latitude>)``, so it can be assigned to a GeoDjango ``PointField``. An empty
    point cleans to ``None``.
    """

    widget = PointInput
    default_error_messages = {
        "incomplete_latitude": _("Enter the latitude as well as the longitude."),
        "incomplete_longitude": _("Enter the longitude as well as the latitude."),
    }

    def __init__(
        self,
        *,
        min_latitude=None,
        max_latitude=None,
        min_longitude=None,
        max_longitude=None,
        decimal_places=6,
        **kwargs,
    ):
        """State the range of each half and the number of decimal places.

        Args:
            min_latitude: The lowest latitude accepted, at least -90.
            max_latitude: The highest latitude accepted, at most 90.
            min_longitude: The lowest longitude accepted, at least -180.
            max_longitude: The highest longitude accepted, at most 180.
            decimal_places: The most decimal places either half accepts.
            **kwargs: What ``Field`` takes, such as ``required`` and ``label``.

        Raises:
            ValueError: A bound or the decimal places is refused, naming the
                option.
        """
        fields = (
            self.half(
                LatitudeField,
                "latitude",
                min_value=min_latitude,
                max_value=max_latitude,
                decimal_places=decimal_places,
            ),
            self.half(
                LongitudeField,
                "longitude",
                min_value=min_longitude,
                max_value=max_longitude,
                decimal_places=decimal_places,
            ),
        )
        super().__init__(fields, require_all_fields=False, **kwargs)

    @staticmethod
    def half(field_class, name, **options):
        """Build one half, with an error that names the point field's option."""
        try:
            return field_class(required=True, **options)
        except ValueError as error:
            message = str(error)
            for bound in ("min", "max"):
                message = message.replace(f"{bound}_value", f"{bound}_{name}")
            raise ValueError(message) from None

    def get_bound_field(self, form, field_name):
        """Tell each part of a ``PointInput`` its bounds and decimal places."""
        if isinstance(self.widget, PointInput):
            for part, half in zip(self.widget.widgets, self.fields, strict=True):
                part.scale = half.decimal_places
                part.min_value = half.min_value
                part.max_value = half.max_value
        return super().get_bound_field(form, field_name)

    def clean(self, value):
        """Refuse a point with one half empty, naming the half.

        ``MultiValueField`` gives a missing half a message with no code, so the
        point field raises ``incomplete`` itself.
        """
        if self.disabled and not isinstance(value, list):
            value = self.widget.decompress(value)
        if isinstance(value, list | tuple) and len(value) == 2:
            latitude, longitude = (self.blank(half) for half in value)
            if latitude and not longitude:
                self.fail("incomplete_latitude")
            if longitude and not latitude:
                self.fail("incomplete_longitude")
        return super().clean(value)

    def blank(self, value):
        """Return whether the half holds nothing."""
        return value in self.empty_values or (
            isinstance(value, str) and not value.strip()
        )

    def fail(self, code):
        """Raise ``incomplete`` with the message of this half."""
        raise ValidationError(self.error_messages[code], code="incomplete")

    def compress(self, data_list):
        """Return the point as WKT text with its spatial reference, or ``None``."""
        if not data_list:
            return None
        latitude, longitude = data_list
        return f"SRID=4326;POINT({longitude:f} {latitude:f})"
