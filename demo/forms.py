"""The forms the demo project draws."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Layout, Row
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TextInputsForm(forms.Form):
    """One field of each text input kind the pack draws.

    Every field is optional and carries no help text until the constructor says
    otherwise, so the same form can stand for each state a field can be in. Its
    ``clean`` always fails, so a bound form shows both a field's errors and one
    that belongs to the form as a whole.
    """

    text = forms.CharField(label=_("Text"))
    email = forms.EmailField(label=_("Email"))
    url = forms.URLField(label=_("URL"))
    number = forms.IntegerField(label=_("Number"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    date = forms.DateField(label=_("Date"))
    time = forms.TimeField(label=_("Time"))
    date_time = forms.DateTimeField(label=_("Date and time"))
    textarea = forms.CharField(label=_("Textarea"), widget=forms.Textarea)

    help_texts = {
        "text": _("A line of free text."),
        "email": _("An address such as name@example.com."),
        "url": _("An address that starts with http:// or https://."),
        "number": _("A whole number."),
        "password": _("Kept out of the page when the form is drawn again."),
        "date": _("A date such as 2026-10-03."),
        "time": _("A time such as 14:30."),
        "date_time": _("A date and a time such as 2026-10-03 14:30."),
        "textarea": _("Several lines of free text."),
    }

    def __init__(self, *args, required=False, with_help=False, **kwargs):
        """Switch every field's required flag and help text at once.

        Args:
            *args: Passed to ``forms.Form``.
            required: Whether every field is required.
            with_help: Whether every field carries its help text.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.required = required
            field.help_text = self.help_texts[name] if with_help else ""

    def clean(self):
        """Fail every time, so the form always has an error of its own.

        Raises:
            ValidationError: Always.
        """
        raise ValidationError(
            _("The form as a whole was refused, whatever its fields hold."),
            code="demo_refusal",
        )


class LayoutObjectsForm(forms.Form):
    """A form whose layout uses every layout object the pack draws so far.

    Its layout is built for each instance, and every id in it carries the
    form's prefix, so two of these forms on one page repeat no id. The form
    must be given a prefix.
    """

    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    email = forms.EmailField(label=_("Email"))
    note = forms.CharField(label=_("Note"))

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "Details for {{ owner }}",
                Row(
                    Column("first_name", css_id=f"{prefix}-first"),
                    Column("last_name", css_id=f"{prefix}-last"),
                    css_id=f"{prefix}-row",
                ),
                Div("email", "note", css_id=f"{prefix}-more"),
                css_id=f"{prefix}-details",
            )
        )
