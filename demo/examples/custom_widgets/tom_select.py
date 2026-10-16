"""Choice fields drawn as searchable Tom Select controls."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import TomSelect, TomSelectMultiple

TOPICS = [
    ("geology", "Geology"),
    ("glaciology", "Glaciology"),
    ("petrology", "Petrology"),
    ("seismology", "Seismology"),
    ("tectonics", "Tectonics"),
    ("volcanology", "Volcanology"),
]
GROUPED = [
    ("Rock", [("geology", "Geology"), ("petrology", "Petrology")]),
    (
        "Movement",
        [("seismology", "Seismology"), ("tectonics", "Tectonics")],
    ),
    ("glaciology", "Glaciology"),
]


class TopicsForm(forms.Form):
    """One value, several values, and a list written in groups."""

    topic = forms.ChoiceField(
        choices=[("", "No topic"), *TOPICS],
        widget=TomSelect(placeholder="Pick a topic", clear_button=True),
        help_text="Backspace on the control returns it to no value.",
        required=False,
    )
    topics = forms.MultipleChoiceField(
        choices=TOPICS,
        widget=TomSelectMultiple(
            placeholder="Pick up to three", remove_button=True, max_items=3
        ),
        help_text="Required. Each value has a button that removes it.",
    )
    grouped = forms.ChoiceField(
        choices=GROUPED,
        widget=TomSelect,
        help_text="Options are listed under the heading they were written in.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
