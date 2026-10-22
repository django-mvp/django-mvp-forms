"""A form that arrives with errors in two of its tabs and two of its groups."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import Accordion, AccordionGroup, Tab, TabHolder


class ApplicationForm(forms.Form):
    """Every tab and every group holding an error is marked, open or closed."""

    name = forms.CharField(required=False)
    street = forms.CharField()
    note = forms.CharField()
    email = forms.EmailField(required=False)
    account = forms.CharField()
    reference = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Put three fields behind tabs and three in groups."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            TabHolder(
                Tab("Profile", "name"),
                Tab("Address", "street"),
                Tab("Notes", "note"),
            ),
            Accordion(
                AccordionGroup("Contact", "email"),
                AccordionGroup("Billing", "account"),
                AccordionGroup("Reference", "reference"),
            ),
        )
        self.helper.add_input(Submit("submit", "Save"))
