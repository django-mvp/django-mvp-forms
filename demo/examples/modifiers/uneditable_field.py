"""Fields drawn with their value shown and the input disabled."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import UneditableField


class ProfileForm(forms.Form):
    """An account number the browser will not send back, and one Django keeps."""

    account = forms.CharField(initial="AC-1001", help_text="Issued once.")
    reference = forms.CharField(initial="R-7", disabled=True)
    nickname = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Draw two fields uneditable."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            UneditableField("account"),
            UneditableField("reference"),
            "nickname",
        )
        self.helper.add_input(Submit("submit", "Save"))
