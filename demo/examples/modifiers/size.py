"""A size for the whole form, and a different one for one field."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from demo.examples.modifiers.base import AccountForm
from mvp_forms.choices import Choice, FormChoices


class SmallForm(AccountForm):
    """Every input and button small, except the notes."""

    def __init__(self, *args, **kwargs):
        """State the form's size, and the one field that differs."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm",
            fields={"notes": Choice(size="lg")},
        )
        self.helper.add_input(Submit("submit", "Save"))
