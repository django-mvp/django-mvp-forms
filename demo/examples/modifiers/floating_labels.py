"""Labels that sit inside their inputs, for the whole form."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.choices import Choice, FormChoices


class SignInForm(forms.Form):
    """Three floating labels, one ordinary label and a checkbox."""

    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput, help_text="At least eight characters."
    )
    country = forms.ChoiceField(choices=[("de", "Germany"), ("uk", "United Kingdom")])
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
    remember = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        """Float every label, except the one on the notes."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            label="floating", fields={"notes": Choice(label=None)}
        )
        self.helper.add_input(Submit("submit", "Sign in"))
