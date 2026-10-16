"""A colour for the form's inputs, and another for its buttons."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from demo.examples.modifiers.base import AccountForm
from mvp_forms.choices import Choice, FormChoices


class ColouredForm(AccountForm):
    """Primary inputs, a secondary button, and notes with no colour at all."""

    def __init__(self, *args, **kwargs):
        """State the colours, and take the colour off one field."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            color="primary",
            button_color="secondary",
            # None undoes the form's choice for this field.
            fields={"notes": Choice(color=None)},
        )
        self.helper.add_input(Submit("submit", "Save"))
