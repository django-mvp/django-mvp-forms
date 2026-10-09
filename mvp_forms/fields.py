"""Form fields the package offers for needs Django's own do not meet."""

import calendar
import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

PRECISIONS = ("year", "month", "day")


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
        "too_fine_month": _("Enter the year only."),
        "too_fine_day": _("Enter a year and a month, with no day."),
        "min_value": _("Enter a date no earlier than %(limit)s."),
        "max_value": _("Enter a date no later than %(limit)s."),
    }

    def __init__(
        self,
        *,
        coarsest="year",
        resolution="day",
        min_value=None,
        max_value=None,
        **kwargs,
    ):
        """State the precisions and the dates the field accepts.

        Args:
            coarsest: The least precise value accepted.
            resolution: The most precise value accepted.
            min_value: The earliest date accepted, as a partial date or a
                Python date.
            max_value: The latest date accepted, as a partial date or a Python
                date.
            **kwargs: Everything a ``CharField`` takes.

        Raises:
            ValueError: A precision is not one of year, month and day, the
                resolution is coarser than the coarsest, or the earliest date is
                later than the latest.
        """
        for option, value in (("coarsest", coarsest), ("resolution", resolution)):
            if value not in PRECISIONS:
                raise ValueError(
                    f"{option} must be one of {', '.join(PRECISIONS)}, not {value!r}."
                )
        if PRECISIONS.index(resolution) < PRECISIONS.index(coarsest):
            raise ValueError(
                f"resolution must not be coarser than coarsest, not {resolution!r} "
                f"and {coarsest!r}."
            )
        self.coarsest = coarsest
        self.resolution = resolution
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
        self.limit_widget(self.widget)

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

    def limit_widget(self, widget):
        """Tell a widget the resolution and the dates the field accepts."""
        widget.resolution = self.resolution
        widget.min_value = self.min_value
        widget.max_value = self.max_value

    @staticmethod
    def span(value):
        """Return the first and last day a partial date could be."""
        parts = [int(part) for part in value.split("-")]
        year, month, day = [*parts, 0, 0][:3]
        return (year, month or 1, day or 1), (year, month or 12, day or 31)

    def prepare_value(self, value):
        """Show a Python date as ISO text."""
        if isinstance(value, datetime.date):
            return value.isoformat()
        return value

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
        if given <= PRECISIONS.index(self.coarsest):
            self.fail(f"needs_{self.coarsest}")
        if given - 1 > PRECISIONS.index(self.resolution):
            self.fail(f"too_fine_{PRECISIONS[PRECISIONS.index(self.resolution) + 1]}")
        first, last = self.span(value)
        if self.min_value and last < self.span(self.min_value)[0]:
            self.fail("min_value", limit=self.min_value)
        if self.max_value and first > self.span(self.max_value)[1]:
            self.fail("max_value", limit=self.max_value)
        return value

    def parse(self, value):
        """Return the padded ISO text of a partial date that exists."""
        parts = value.rstrip("-").split("-")
        if len(parts) > 3 or any(not re.fullmatch(r"\d*", part) for part in parts):
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
