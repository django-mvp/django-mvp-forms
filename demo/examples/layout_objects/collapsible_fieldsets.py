"""A form of collapsible fieldsets: one open, one closed, and one closed until it holds an error."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from mvp_forms.layout import Fieldset


class BookingForm(forms.Form):
    """Send it empty: the closed address fieldset opens to show its errors."""

    name = forms.CharField()
    email = forms.EmailField()
    street = forms.CharField()
    town = forms.CharField()
    postcode = forms.CharField()
    gift_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    gift_wrap = forms.BooleanField(required=False)

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
                collapsible=True,
                open=True,
                description="We use these only to send your booking confirmation.",
            ),
            Fieldset(
                "Billing address",
                "street",
                Row(Column("town"), Column("postcode")),
                collapsible=True,
                description="The address your card is registered to, which may "
                "not be where you are staying.",
            ),
            Fieldset(
                "Gift options",
                "gift_wrap",
                "gift_message",
                collapsible=True,
                open=False,
            ),
        )
        self.helper.add_input(Submit("submit", "Book"))
