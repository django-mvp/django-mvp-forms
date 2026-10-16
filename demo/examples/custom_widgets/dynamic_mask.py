"""A text input that applies whichever of several masks fits best."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import DynamicMaskInput, PatternMaskInput

LOCAL = PatternMaskInput("000-0000")
WITH_AREA = PatternMaskInput("(000) 000-0000")


class PhoneForm(forms.Form):
    """A phone number of seven digits or of ten."""

    phone = forms.CharField(
        widget=DynamicMaskInput([LOCAL, WITH_AREA]),
        help_text="Seven digits are masked as 000-0000, ten as (000) 000-0000.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))
