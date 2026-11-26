"""A Tom Select control whose list of options stays open under the search box."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.widgets import TomSelect

ORGANISATIONS = [
    ("", ""),
    ("awi", "Alfred Wegener Institute"),
    ("bgs", "British Geological Survey"),
    ("caltech", "California Institute of Technology"),
    ("eth", "ETH Zurich"),
    ("gfz", "GFZ Helmholtz Centre for Geosciences"),
    ("ifremer", "Ifremer"),
    ("ingv", "National Institute of Geophysics and Volcanology"),
    ("noaa", "National Oceanic and Atmospheric Administration"),
    ("scripps", "Scripps Institution of Oceanography"),
    ("usgs", "United States Geological Survey"),
    ("whoi", "Woods Hole Oceanographic Institution"),
]


class OrganisationForm(forms.Form):
    """A long list people browse as much as they search."""

    organisation = forms.ChoiceField(
        choices=ORGANISATIONS,
        widget=TomSelect(
            placeholder="Search organisations",
            attrs={"data-open-list": True},
        ),
        help_text="The list stays open under the box. Picking an option leaves it there.",
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
