"""Text inputs that accept only what fits a pattern."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import PatternMaskInput


class ContactForm(forms.Form):
    """A phone number, a postcode and a licence key."""

    phone = forms.CharField(
        widget=PatternMaskInput("+{49} 000 0000000"),
        help_text="Each 0 is a digit. The braces keep 49 in the value.",
        required=False,
    )
    postcode = forms.CharField(
        widget=PatternMaskInput("00000", lazy=False, placeholder_char="#"),
        help_text="lazy=False shows the whole pattern before anything is typed.",
        required=False,
    )
    licence = forms.CharField(
        label="Licence key",
        widget=PatternMaskInput(
            "XXXX-XXXX-XXXX", definitions={"X": "[A-Za-z0-9]"}, eager=True
        ),
        help_text="X is defined here. eager=True fills each hyphen in ahead.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))
