"""A partial date drawn as three selects."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.fields import PartialDateField
from mvp_forms.widgets import PartialDateSelect


class SelectDatesForm(forms.Form):
    """A date known to the year, one to the month and one inside a range."""

    collected = PartialDateField(
        widget=PartialDateSelect,
        help_text="A year, a year and month, or a full date.",
    )
    published = PartialDateField(
        widget=PartialDateSelect,
        max_resolution="month",
        help_text='max_resolution="month": no day can be entered.',
        required=False,
    )
    sampled = PartialDateField(
        widget=PartialDateSelect,
        min_value="1998-03-15",
        max_value="2004-09",
        help_text="Nothing before 15 March 1998 or after September 2004.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
