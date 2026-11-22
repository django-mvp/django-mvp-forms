"""Fields that say how many characters are left under them."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory

from mvp_forms.widgets import CharactersLeftInput, CharactersLeftTextarea


class SampleForm(forms.Form):
    """A form with a submit button and no browser validation."""

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))


class TitleForm(SampleForm):
    """A text input with a limit."""

    title = forms.CharField(
        max_length=40,
        widget=CharactersLeftInput,
        help_text="The line appears when 8 characters or fewer are left.",
    )


class SummaryForm(SampleForm):
    """A textarea with a limit, and an input whose line appears sooner."""

    summary = forms.CharField(
        max_length=200,
        widget=CharactersLeftTextarea(attrs={"rows": 4}),
        help_text="A line break counts as one character.",
    )
    note = forms.CharField(
        max_length=30,
        widget=CharactersLeftInput(show_from=20),
        required=False,
        help_text="show_from=20",
    )


class NoteLineForm(forms.Form):
    """One note in a list."""

    note = forms.CharField(max_length=30, widget=CharactersLeftInput)


NoteLineFormSet = formset_factory(NoteLineForm, extra=1)


class NoteLineHelper(FormHelper):
    """Draws each note without a form tag, so the page can add rows between them."""

    def __init__(self, *args, **kwargs):
        """Leave out the form tag and the media, which the page draws once."""
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.include_media = False


class OverTheLimitForm(SampleForm):
    """A saved value that is longer than the field now allows."""

    title = forms.CharField(
        max_length=20,
        widget=CharactersLeftInput,
        help_text="The saved title is longer than 20 characters. It is not cut.",
    )

    initial_values = {"title": "A title written before the limit was lowered"}
