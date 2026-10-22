"""A measurement and its uncertainty joined with a ± between them."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms

from mvp_forms.layout import Join

UNITS = [("mW/m²", "mW/m²"), ("W/m²", "W/m²")]


class HeatFlowForm(forms.Form):
    """Send it with a value and no uncertainty: the error is on the uncertainty alone."""

    value = forms.FloatField()
    uncertainty = forms.FloatField(min_value=0)
    unit = forms.ChoiceField(choices=UNITS)

    def __init__(self, *args, **kwargs):
        """Join the three fields with the text between the first two."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Join("value", HTML("±"), "uncertainty", "unit", label="Heat flow"),
        )
        self.helper.add_input(Submit("submit", "Save"))
