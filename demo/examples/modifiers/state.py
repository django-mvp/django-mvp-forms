"""Disabled and read-only fields, help text, and the error a required field gives."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class StateForm(forms.Form):
    """A disabled field, a read-only one, one with help text and a required one."""

    reference = forms.CharField(initial="R-7", disabled=True)
    account = forms.CharField(
        initial="AC-1001",
        widget=forms.TextInput(attrs={"readonly": True}),
    )
    nickname = forms.CharField(required=False, help_text="Shown on your profile.")
    email = forms.EmailField(help_text="We never share it.")

    def __init__(self, *args, **kwargs):
        """Add a button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))
