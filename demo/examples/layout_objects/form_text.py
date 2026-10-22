"""An enquiry form with text at each of the three sizes: an introduction, a note between fields and the small print."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.layout import Fieldset, FormText


class EnquiryForm(forms.Form):
    """Send it empty: the text stays where it is, beside the errors."""

    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    guests = forms.IntegerField(
        min_value=1, help_text="A rough number is fine. You can change it later."
    )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Anything else we should know",
    )
    name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        """Put the text between the fields."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            FormText(
                "Tell us about the event you are planning. We reply to every "
                "enquiry within two working days.",
                size="large",
            ),
            Fieldset(
                "Your event",
                "date",
                "guests",
                "details",
                description="The date and the number of guests are all we need "
                "to check the room is free.",
            ),
            Fieldset(
                "About you",
                "name",
                FormText("We only use this to reply to you."),
                "email",
            ),
            FormText(
                'By sending this enquiry you agree to our <a class="link" '
                'href="#">booking terms</a>. Nothing is booked until we have '
                "replied and you have confirmed.",
                size="small",
                variant="muted",
            ),
        )
        self.helper.add_input(Submit("submit", "Send enquiry"))
