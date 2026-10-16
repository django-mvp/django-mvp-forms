"""A floating label on one field of a layout."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.choices import Choice


class NameForm(forms.Form):
    """Two text inputs, the first with a floating label."""

    first_name = forms.CharField()
    last_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Wrap one field in a Choice."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Choice("first_name", label="floating"),
            "last_name",
        )
        self.helper.add_input(Submit("submit", "Save"))
