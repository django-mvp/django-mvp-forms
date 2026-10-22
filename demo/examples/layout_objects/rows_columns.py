"""A form laid out with a row of columns, a note and a div."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Layout, Row, Submit
from django import forms


class DetailsForm(forms.Form):
    """Send it empty: every error is drawn inside the container that holds it."""

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    note = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Put the fields in their containers."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Row(Column("first_name"), Column("last_name")),
            HTML("<p>We only use this to reply to you.</p>"),
            "email",
            Div("note", css_class="max-w-md"),
        )
        self.helper.add_input(Submit("submit", "Save"))
