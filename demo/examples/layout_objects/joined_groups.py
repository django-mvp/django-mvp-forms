"""A country code and a number joined under one label."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms

from mvp_forms.layout import Join

COUNTRY_CODES = [("+49", "+49"), ("+44", "+44"), ("+1", "+1")]


class PhoneForm(forms.Form):
    """Send it with a code and no number: the error is on the number alone."""

    country_code = forms.ChoiceField(choices=COUNTRY_CODES)
    number = forms.CharField(help_text="Digits only")

    def __init__(self, *args, **kwargs):
        """Join the two fields."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Join(
                "country_code",
                Field("number", autocomplete="tel"),
                label="Phone",
            ),
        )
        self.helper.add_input(Submit("submit", "Save"))
