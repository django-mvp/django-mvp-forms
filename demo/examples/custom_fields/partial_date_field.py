"""A date that may be known only to the year or the month."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.fields import PartialDateField


class SampleForm(forms.Form):
    """Each field accepts a different resolution."""

    collected = PartialDateField(
        help_text="2019, 2019-06 or 2019-06-14. All three are accepted.",
    )
    analysed = PartialDateField(
        min_resolution="month",
        help_text="At least a year and a month: 2019 alone is refused.",
        required=False,
    )
    published = PartialDateField(
        max_resolution="month",
        help_text="A year, or a year and a month. A day is refused.",
        required=False,
    )
    sampled = PartialDateField(
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
