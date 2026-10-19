"""A row of filters above a list, drawn with no labels above the fields."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django_countries import countries

from demo.examples.custom_widgets.range_input import PairField
from mvp_forms.widgets import RangeInput, TomSelect, TomSelectMultiple

CATEGORIES = [
    ("boreholes", "Boreholes"),
    ("marine", "Marine probes"),
    ("mines", "Mines"),
    ("tunnels", "Tunnels"),
    ("wells", "Wells"),
]
STATUSES = [
    ("", "Any"),
    ("draft", "Draft"),
    ("review", "In review"),
    ("published", "Published"),
]


class SiteFiltersForm(forms.Form):
    """The filters of a list of sites, each named inside its own frame."""

    search = forms.CharField(
        required=False, widget=forms.TextInput({"placeholder": "Search sites"})
    )
    category = forms.MultipleChoiceField(
        choices=CATEGORIES,
        required=False,
        widget=TomSelectMultiple(counted=True, placeholder="Search", clear_button=True),
    )
    country = forms.ChoiceField(
        choices=[("", ""), *countries],
        required=False,
        widget=TomSelect(placeholder="Any", clear_button=True),
    )
    status = forms.ChoiceField(choices=STATUSES, required=False)
    depth = PairField(
        forms.DecimalField, RangeInput(), label="Depth (m)", required=False
    )

    def __init__(self, *args, **kwargs):
        """Draw the fields in one row that wraps, with no labels above them."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "get"
        self.helper.form_show_labels = False
        self.helper.form_class = "grid gap-x-2 sm:grid-cols-2 lg:grid-cols-3"
        self.helper.layout = Layout(
            *self.fields,
            Submit("submit", "Filter", css_class="mt-1 w-fit"),
        )


class ChosenSiteFiltersForm(SiteFiltersForm):
    """The same filters with values already chosen in each."""

    def __init__(self, *args, **kwargs):
        """Start with a choice in every filter."""
        super().__init__(*args, **kwargs)
        chosen = {
            "search": "Rhine",
            "category": ["boreholes", "wells"],
            "country": "DE",
            "status": "published",
            "depth": slice(100, None),
        }
        for name, value in chosen.items():
            self.fields[name].initial = value
