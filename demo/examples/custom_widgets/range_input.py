"""A number range, a date range and a date and time range, each drawn as one field."""

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.choices import Choice, FormChoices
from mvp_forms.widgets import DateRangeInput, DateTimeRangeInput, RangeInput


class PairField(forms.MultiValueField):
    """A low and a high end, either of which may be empty, cleaned to a slice."""

    def __init__(self, end, widget, **kwargs):
        """Build the two ends from one field class."""
        super().__init__(
            fields=(end(required=False), end(required=False)),
            widget=widget,
            require_all_fields=False,
            **kwargs,
        )

    def compress(self, data_list):
        """Return the two ends as a slice, or None when both are empty."""
        if not data_list or all(value in (None, "") for value in data_list):
            return None
        low, high = data_list
        if low is not None and high is not None and low > high:
            raise forms.ValidationError("The low end is above the high end.")
        return slice(low, high)


class SearchRangesForm(forms.Form):
    """Every kind of range, held, half held, required and disabled."""

    depth = PairField(
        forms.DecimalField,
        RangeInput(),
        label="Depth (m)",
        initial=slice(100, 2500),
        help_text="Either end may be left empty.",
        required=False,
    )
    heat_flow = PairField(
        forms.IntegerField,
        RangeInput(),
        label="Heat flow (mW/m²)",
        initial=slice(60, None),
        help_text="Only a low end: at least 60.",
        required=False,
    )
    measured = PairField(
        forms.DateField,
        DateRangeInput(),
        label="Measured",
        help_text="Required. Send the form with both ends empty to see the error.",
    )
    logged = PairField(
        forms.DateTimeField,
        DateTimeRangeInput(),
        label="Logged",
        initial=slice(datetime.datetime(2024, 3, 1, 9, 0), None),
        required=False,
    )
    archived = PairField(
        forms.IntegerField,
        RangeInput(),
        label="Archived years",
        initial=slice(1990, 2000),
        disabled=True,
        required=False,
        help_text="A disabled field.",
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Search"))


class SmallRangesForm(SearchRangesForm):
    """The same ranges, small, with the heat flow in the primary colour."""

    def __init__(self, *args, **kwargs):
        """State the form's size and one field's colour."""
        super().__init__(*args, **kwargs)
        self.helper.daisyui = FormChoices(
            size="sm", fields={"heat_flow": Choice(color="primary")}
        )
