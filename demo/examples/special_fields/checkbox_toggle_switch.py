"""One boolean field drawn three ways."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.choices import Choice, FormChoices


class NotificationsForm(forms.Form):
    """Three boolean fields: a checkbox, a toggle and a switch."""

    remember = forms.BooleanField(label="Remember me", required=False)
    notify = forms.BooleanField(
        label="Email me about replies",
        help_text="Sent once a day at most.",
        required=False,
    )
    publish = forms.BooleanField(label="Publish this record", required=False)

    def __init__(self, *args, **kwargs):
        """State a drawing for two of the fields, each in a different place."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # By name, for the whole form.
        self.helper.daisyui = FormChoices(fields={"notify": Choice(drawing="toggle")})
        self.helper.layout = Layout(
            "remember",
            "notify",
            # Or in the layout, around the field.
            Choice("publish", drawing="switch"),
        )
        self.helper.add_input(Submit("submit", "Save"))
