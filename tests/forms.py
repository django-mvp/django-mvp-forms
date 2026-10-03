"""The forms the suite draws."""

from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets


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


class UncoveredInput(widgets.Input):
    input_type = "text"


class UncoveredWidgetsForm(forms.Form):
    first = forms.CharField(help_text="First help")
    choice = forms.ChoiceField(
        choices=[("a", "A")], widget=UncoveredInput, help_text="Choice help"
    )
    agree = forms.BooleanField(widget=UncoveredInput, help_text="Agree help")
    upload = forms.FileField(widget=UncoveredInput, help_text="Upload help")
    last = forms.CharField(help_text="Last help")


class NoFieldsForm(forms.Form):
    pass


class FormWideErrorsForm(forms.Form):
    name = forms.CharField(required=False)

    def clean(self):
        raise ValidationError(
            [
                ValidationError("The first failure", code="first"),
                ValidationError("The second failure", code="second"),
            ]
        )


class FormWideMarkupForm(forms.Form):
    name = forms.CharField(required=False)

    def clean(self):
        raise ValidationError("<script>alert(1)</script>", code="markup")


class HelpedForm(forms.Form):
    helped = forms.CharField(help_text="Some help")
    bare = forms.CharField()
    optional = forms.CharField(required=False)


class UploadForm(forms.Form):
    upload = forms.FileField(required=False)


class MediaWidget(forms.TextInput):
    class Media:
        js = ["tests/media.js"]


class MediaForm(forms.Form):
    name = forms.CharField(widget=MediaWidget)


class DeveloperLabelledForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"aria-label": "Mine"}))


class FieldAndFormWideErrorsForm(HelpedForm):
    def clean(self):
        raise ValidationError("It failed as a whole", code="whole")


FRUIT = [("a", "Apple"), ("b", "Banana")]
GROUPED = [("Fruit", FRUIT), ("Vegetable", [("c", "Carrot")]), ("d", "Dill")]


class SelectsForm(forms.Form):
    choice = forms.ChoiceField(choices=FRUIT, help_text="Pick one")
    many = forms.MultipleChoiceField(choices=FRUIT)
    maybe = forms.NullBooleanField()
    grouped = forms.ChoiceField(choices=GROUPED)


class SelectEdgesForm(forms.Form):
    empty = forms.ChoiceField(choices=[], required=False)
    marked = forms.ChoiceField(
        choices=[("<b>", "<b>Bold</b>"), ("x", "Tom & Jerry")], required=False
    )
    marked_groups = forms.ChoiceField(
        choices=[("<i>Group</i>", [("y", "Yes")])], required=False
    )
    styled = forms.ChoiceField(
        choices=FRUIT,
        widget=forms.Select(attrs={"class": "mine", "data-role": "picker"}),
    )
