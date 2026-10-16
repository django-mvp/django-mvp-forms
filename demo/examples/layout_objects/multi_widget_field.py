"""A split date and time whose two inputs each have a placeholder."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, MultiWidgetField, Submit
from django import forms


class EventForm(forms.Form):
    """Send it empty: the start is required, the end is not."""

    starts = forms.SplitDateTimeField(help_text="Local date and time")
    ends = forms.SplitDateTimeField(required=False)

    def __init__(self, *args, **kwargs):
        """Give each part of the start its own placeholder."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            MultiWidgetField(
                "starts",
                attrs=({"placeholder": "2026-10-03"}, {"placeholder": "12:30"}),
            ),
            "ends",
        )
        self.helper.add_input(Submit("submit", "Save"))
