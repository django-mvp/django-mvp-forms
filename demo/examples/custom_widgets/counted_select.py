"""Multiple choice fields that show a count in place of the values chosen."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries import countries

from mvp_forms.widgets import TomSelectMultiple

DISCIPLINES = [
    ("geology", "Geology"),
    ("glaciology", "Glaciology"),
    ("petrology", "Petrology"),
    ("seismology", "Seismology"),
    ("tectonics", "Tectonics"),
    ("volcanology", "Volcanology"),
]
DATASETS = [
    ("margins", "Heat flow measurements from the continental margins, 1990 to 2020"),
    ("boreholes", "Borehole temperature logs with the correction each one used"),
    ("conductivity", "Thermal conductivity of sedimentary rocks, from core samples"),
    ("oceans", "Heat flow through the floor of the oceans"),
    ("short", "Short one"),
]


class FieldworkForm(forms.Form):
    """A short list, a long list, long labels and a disabled field."""

    disciplines = forms.MultipleChoiceField(
        choices=DISCIPLINES,
        initial=["geology", "volcanology"],
        widget=TomSelectMultiple(counted=True, placeholder="Search"),
        help_text="Required. Clear every tick and send the form to see the error.",
    )
    countries = forms.MultipleChoiceField(
        choices=list(countries),
        required=False,
        widget=TomSelectMultiple(counted=True, placeholder="Search", clear_button=True),
        help_text="Every country. Type in the list to search.",
    )
    datasets = forms.MultipleChoiceField(
        choices=DATASETS,
        initial=["margins", "boreholes", "conductivity"],
        required=False,
        widget=TomSelectMultiple(counted=True, placeholder="Search"),
        help_text="Options with long labels.",
    )
    archived = forms.MultipleChoiceField(
        choices=DISCIPLINES,
        initial=["petrology", "tectonics"],
        required=False,
        disabled=True,
        widget=TomSelectMultiple(counted=True),
        help_text="A disabled field.",
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
