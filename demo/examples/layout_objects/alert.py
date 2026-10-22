"""Alerts between the fields of a form."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import Alert


class NoticeForm(forms.Form):
    """Three alerts: one that can be dismissed, one that stays, one in a colour."""

    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Build the layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Alert("A notice the reader can dismiss."),
            Alert("A notice that stays.", dismiss=False),
            Alert("A notice in a colour.", css_class="alert-success"),
            "name",
        )
        self.helper.add_input(Submit("submit", "Save"))
