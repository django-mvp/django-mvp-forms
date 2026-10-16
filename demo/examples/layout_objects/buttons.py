"""Forms whose buttons come from the layout: a button holder and form actions."""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Button,
    ButtonHolder,
    Layout,
    Reset,
    Row,
    Submit,
)
from django import forms


class HolderForm(forms.Form):
    """Two fields straight in a row, and a button holder under them."""

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row("first_name", "last_name"),
            ButtonHolder(Submit("submit", "Save"), Reset("reset", "Start again")),
        )


class ActionsForm(forms.Form):
    """A submit, a reset and a plain button, together in form actions."""

    name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            "name",
            FormActions(
                Submit("submit", "Save"),
                Reset("reset", "Start again"),
                Button("help", "Help"),
            ),
        )
