"""The fields the size, colour and variant examples all draw."""

from django import forms

PLANS = [("free", "Free"), ("team", "Team")]


class AccountForm(forms.Form):
    """A text input, a select, a textarea, a checkbox and a radio group."""

    name = forms.CharField(required=False)
    plan = forms.ChoiceField(choices=PLANS, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)
    newsletter = forms.BooleanField(label="Send me the newsletter", required=False)
    billing = forms.ChoiceField(
        choices=[("month", "Monthly"), ("year", "Yearly")],
        widget=forms.RadioSelect,
        required=False,
    )
