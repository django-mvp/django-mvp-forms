"""A form of two fieldsets one after the other, one holding another, and one with no legend."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from mvp_forms.layout import Fieldset


class OrderForm(forms.Form):
    """Send it empty: every error is drawn inside the fieldset that holds it."""

    name = forms.CharField()
    email = forms.EmailField(help_text="We send the receipt here.")
    street = forms.CharField()
    town = forms.CharField()
    postcode = forms.CharField()
    leave_with_neighbour = forms.BooleanField(required=False)
    instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    newsletter = forms.BooleanField(required=False, label="Send me the newsletter")

    def __init__(self, *args, **kwargs):
        """Put the fields in their fieldsets."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Fieldset(
                "Contact",
                "name",
                "email",
                description="We use these only to send your receipt.",
            ),
            Fieldset(
                "Delivery address",
                "street",
                Row(Column("town"), Column("postcode")),
                Fieldset(
                    "If nobody is in",
                    "leave_with_neighbour",
                    "instructions",
                ),
            ),
            Fieldset("", "newsletter"),
        )
        self.helper.add_input(Submit("submit", "Place order"))
