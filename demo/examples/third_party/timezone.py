"""django-timezone-field's form field, drawn as a searchable, grouped control."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from timezone_field import TimeZoneFormField

from mvp_forms.widgets import TimeZoneSelect


class MeetingForm(forms.Form):
    """A required timezone and an optional one offset from GMT."""

    timezone = TimeZoneFormField(initial="Europe/Berlin", widget=TimeZoneSelect)
    home_timezone = TimeZoneFormField(
        choices_display="WITH_GMT_OFFSET",
        required=False,
        help_text="Each name is shown with its offset from GMT today.",
        widget=TimeZoneSelect(placeholder="Pick your home timezone"),
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
