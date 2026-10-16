"""Text before, after, or on both sides of an input."""

from crispy_forms.bootstrap import AppendedText, PrependedAppendedText, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms


class PriceForm(forms.Form):
    """Three amounts, each with its unit attached."""

    amount = forms.DecimalField(help_text="Before tax.")
    weight = forms.DecimalField()
    budget = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        """Attach a unit to each field in the layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            PrependedText("amount", "$"),
            AppendedText("weight", "kg"),
            PrependedAppendedText("budget", "$", ".00"),
        )
        self.helper.add_input(Submit("submit", "Save"))
