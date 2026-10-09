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
    }

    def __init__(self, *, coarsest="year", finest="day", **kwargs):
        """State the precisions the field accepts.

        Args:
            coarsest: The least precise value accepted.
            finest: The most precise value accepted.
            **kwargs: Everything a ``CharField`` takes.

        Raises:
            ValueError: A precision is not one of year, month and day, or the
                finest is coarser than the coarsest.
        """
        for option, value in (("coarsest", coarsest), ("finest", finest)):
            if value not in PRECISIONS:
                raise ValueError(
                    f"{option} must be one of {', '.join(PRECISIONS)}, not {value!r}."
                )
        if PRECISIONS.index(finest) < PRECISIONS.index(coarsest):
            raise ValueError(
                f"finest must not be coarser than coarsest, not {finest!r} "
                f"and {coarsest!r}."
            )
        self.coarsest = coarsest
        self.finest = finest
        super().__init__(**kwargs)
        if hasattr(self.widget, "set_finest"):
            self.widget.set_finest(finest)

    def prepare_value(self, value):
        """Show a Python date as ISO text."""
        if isinstance(value, datetime.date):
            return value.isoformat()
        return value

    def fail(self, code):
        """Raise the field's error of this code."""
        raise ValidationError(self.error_messages[code], code=code)

    def to_python(self, value):
        """Return the padded ISO text of what was entered."""
        value = super().to_python(value)
        if value in self.empty_values:
            return ""
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
        if len(given) <= PRECISIONS.index(self.coarsest):
            self.fail(f"needs_{self.coarsest}")
        if len(given) - 1 > PRECISIONS.index(self.finest):
            self.fail(f"too_fine_{PRECISIONS[PRECISIONS.index(self.finest) + 1]}")
        return "-".join([year, *(part.zfill(2) for part in given[1:])])
