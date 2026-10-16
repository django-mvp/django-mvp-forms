"""Text inputs that accept a character only while the value still fits."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import RegexMaskInput


class AccountForm(forms.Form):
    """A customer number of digits only and a hexadecimal colour."""

    customer_number = forms.CharField(
        widget=RegexMaskInput(r"^\d{0,8}$"),
        help_text=r"^\d{0,8}$ takes up to eight digits and no letter.",
        required=False,
    )
    colour = forms.CharField(
        widget=RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i"),
        help_text='flags="i" ignores case: a # and up to six hexadecimal digits.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))
