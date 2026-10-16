"""A form whose fields sit in three accordion groups."""

from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms


class ProfileForm(forms.Form):
    """Send it empty: the group holding the first error is the one that opens."""

    name = forms.CharField(required=False)
    street = forms.CharField(required=False)
    note = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Put the fields in their groups."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup("Profile", "name"),
                AccordionGroup("Address", "street"),
                AccordionGroup("Notes", "note"),
            ),
        )
        self.helper.add_input(Submit("submit", "Save"))


class ChosenGroupForm(forms.Form):
    """The first group is closed and the second open, whatever the order."""

    name = forms.CharField(required=False)
    street = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Say which group starts open."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup("Closed", "name", active=False),
                AccordionGroup("Open", "street", active=True),
            ),
        )
