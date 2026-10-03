"""The forms the suite draws."""

from crispy_forms.helper import FormHelper
from django import forms


class TextInputsForm(forms.Form):
    text = forms.CharField()
    email = forms.EmailField()
    url = forms.URLField()
    number = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput)
    date = forms.DateField()
    time = forms.TimeField()
    date_time = forms.DateTimeField()
    message = forms.CharField(widget=forms.Textarea)


class DeveloperAttrsForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "wide", "placeholder": "Your name"})
    )
    born = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))


class SecretForm(forms.Form):
    hidden = forms.CharField(widget=forms.PasswordInput)
    shown = forms.CharField(widget=forms.PasswordInput(render_value=True))


class TextInputsWithLayoutForm(TextInputsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)


class UncoveredWidgetsForm(forms.Form):
    first = forms.CharField(help_text="First help")
    choice = forms.ChoiceField(choices=[("a", "A")], help_text="Choice help")
    agree = forms.BooleanField(help_text="Agree help")
    upload = forms.FileField(help_text="Upload help")
    last = forms.CharField(help_text="Last help")


class NoFieldsForm(forms.Form):
    pass
