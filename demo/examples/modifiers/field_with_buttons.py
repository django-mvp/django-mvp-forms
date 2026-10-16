"""A search box with buttons joined to it."""

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class SearchForm(forms.Form):
    """One field with a button on its edge."""

    query = forms.CharField(label="Search", help_text="Names and numbers.")

    def __init__(self, *args, **kwargs):
        """Join a submit button to the field."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            FieldWithButtons(
                "query",
                StrictButton("Go", type="submit", css_class="btn-primary join-item"),
            ),
        )
