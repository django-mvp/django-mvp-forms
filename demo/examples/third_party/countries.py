"""django-countries' fields, as a stock select and as Tom Select controls with flags."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries.fields import CountryField
from django_tomselect.app_settings import PluginClearButton, PluginRemoveButton
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField

from mvp_forms.countries import (
    CountrySelect,
    CountrySelectMultiple,
    country_config,
)


class AddressForm(forms.Form):
    """Countries that come with the form: one, one searched, several, counted."""

    country = CountryField().formfield(
        help_text="django-countries' own field, a stock select.",
    )
    born_in = CountryField().formfield(
        widget=CountrySelect(placeholder="Search for a country", clear_button=True),
        help_text="Type to search. Each country shows its flag.",
        required=False,
    )
    visited = CountryField(multiple=True).formfield(
        widget=CountrySelectMultiple(placeholder="Add a country", remove_button=True),
        help_text="Several countries, each with a remove button.",
        required=False,
    )
    lived_in = CountryField(multiple=True).formfield(
        widget=CountrySelectMultiple(counted=True),
        help_text="Several countries, counted, with a tick on each one chosen.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))


class FetchedCountriesForm(forms.Form):
    """Countries fetched as a person types, for one value and for several."""

    born_in = TomSelectChoiceField(
        config=country_config(
            "ac-flagged-countries",
            placeholder="Search for a country",
            plugin_clear_button=PluginClearButton(),
        ),
        help_text="Fetched as you type. The page holds none of the list.",
    )
    visited = TomSelectMultipleChoiceField(
        config=country_config(
            "ac-flagged-countries",
            placeholder="Add a country",
            plugin_remove_button=PluginRemoveButton(),
        ),
        help_text="Several countries, fetched as you type.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Save"))
