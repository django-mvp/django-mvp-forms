"""Number inputs that format as you type and hand the field a plain number."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import NumberMaskInput


class InvoiceForm(forms.Form):
    """An amount with separators, and a quantity kept inside its limits."""

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=NumberMaskInput(scale=2, thousands_separator=" ", radix=","),
        help_text="Type 1234567,5 and it reads 1 234 567,5.",
        required=False,
    )
    quantity = forms.IntegerField(
        widget=NumberMaskInput(scale=0, min_value=0, max_value=100, autofix=True),
        help_text="Whole numbers from 0 to 100. Anything larger becomes 100.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))
