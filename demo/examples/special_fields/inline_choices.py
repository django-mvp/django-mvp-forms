"""A radio group and a checkbox group drawn along one line."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import InlineCheckboxes, InlineRadios


class SurveyForm(forms.Form):
    """A required radio group and an optional checkbox group."""

    size = forms.ChoiceField(
        choices=[("s", "Small"), ("m", "Medium"), ("l", "Large")],
        widget=forms.RadioSelect,
        help_text="Pick one.",
    )
    extras = forms.MultipleChoiceField(
        choices=[("ketchup", "Ketchup"), ("mustard", "Mustard"), ("mayo", "Mayo")],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Lay both groups out along a line."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(InlineRadios("size"), InlineCheckboxes("extras"))
        self.helper.add_input(Submit("submit", "Order"))
