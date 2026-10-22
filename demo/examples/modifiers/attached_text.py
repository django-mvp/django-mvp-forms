"""Text before, after, or on both sides of an input."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms

from mvp_forms.layout import Join


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
            Join(HTML("$"), "amount"),
            Join("weight", HTML("kg")),
            Join(HTML("$"), "budget", HTML(".00")),
        )
        self.helper.add_input(Submit("submit", "Save"))
