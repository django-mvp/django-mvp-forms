"""Fields with no visible label, for a form that sits in a line."""

from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms


class FilterForm(forms.Form):
    """A search box and a checkbox without labels, and a note with one."""

    query = forms.CharField(label="Search", help_text="Names and numbers.")
    remember = forms.BooleanField(label="Remember me", required=False)
    note = forms.CharField(label="Note", required=False)

    def __init__(self, *args, **kwargs):
        """Hide the label of two fields."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            InlineField("query"),
            InlineField("remember"),
            "note",
        )
        self.helper.add_input(Submit("submit", "Filter"))
