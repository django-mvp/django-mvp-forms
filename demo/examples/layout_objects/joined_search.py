"""A select, a text input and a button joined into one search bar."""

from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from mvp_forms.choices import FormChoices
from mvp_forms.layout import Join

SCOPES = [("all", "Everything"), ("people", "People"), ("places", "Places")]


class JoinedSearchForm(forms.Form):
    """Send it with no words: the error is on the text input alone."""

    scope = forms.ChoiceField(choices=SCOPES)
    query = forms.CharField(help_text="Names and numbers")

    def __init__(self, *args, **kwargs):
        """Join the two fields and the button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.daisyui = FormChoices(button_color="primary")
        self.helper.layout = Layout(
            Join(
                "scope",
                "query",
                StrictButton("Search", type="submit"),
                label="Search",
            ),
        )
