"""A form whose fields sit behind three tabs."""

from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms


class ProfileForm(forms.Form):
    """Send it empty: two tabs hold an error, and the first of them opens."""

    name = forms.CharField(required=False)
    street = forms.CharField()
    city = forms.CharField()
    note = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Put the fields behind their tabs."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            TabHolder(
                Tab("Profile", "name"),
                Tab("Address", "street", "city"),
                Tab("Notes", "note"),
            ),
        )
        self.helper.add_input(Submit("submit", "Save"))
