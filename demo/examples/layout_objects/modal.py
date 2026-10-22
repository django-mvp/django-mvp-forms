"""A form whose address fields sit in a modal."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import Modal

DIALOG_ID = "address-dialog"


class AddressForm(forms.Form):
    """Send it empty: the modal opens by itself, with the errors inside it."""

    name = forms.CharField(required=False)
    street = forms.CharField()
    city = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Put the address in a modal."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            "name",
            Modal("street", "city", css_id=DIALOG_ID, title="Address"),
        )
        self.helper.add_input(Submit("submit", "Save"))
