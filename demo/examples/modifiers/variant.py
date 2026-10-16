"""A variant for the form's inputs, and another for its buttons."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from demo.examples.modifiers.base import AccountForm
from mvp_forms.choices import FormChoices


class GhostForm(AccountForm):
    """Ghost inputs, which show their border only when focused."""

    def __init__(self, *args, **kwargs):
        """State the variant of the inputs and of the buttons."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(variant="ghost", button_variant="outline")
        self.helper.add_input(Submit("submit", "Save"))
