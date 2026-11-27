"""django-countries' fields, as a stock select and as Tom Select controls with flags."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries.fields import CountryField
from django_tomselect.app_settings import PluginClearButton, PluginRemoveButton
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField

from mvp_forms.countries import CountrySelect, CountrySelectMultiple, country_config


class AddressForm(forms.Form):
    """Countries that come with the form: one, one searched, several, counted."""

    stock_country = CountryField().formfield(
        label="CountryField, stock widget",
        help_text="django-countries' form field with its own select, unchanged.",
    )
    country_select = CountryField().formfield(
        label="CountryField with CountrySelect",
        widget=CountrySelect(placeholder="Search for a country", clear_button=True),
        help_text="One country. Type to search, and clear it with the button.",
        required=False,
    )
    country_select_multiple = CountryField(multiple=True).formfield(
        label="CountryField(multiple=True) with CountrySelectMultiple",
        widget=CountrySelectMultiple(placeholder="Add a country", remove_button=True),
        help_text="Several countries, with remove_button=True.",
        required=False,
    )
    country_select_counted = CountryField(multiple=True).formfield(
        label="CountryField(multiple=True) with CountrySelectMultiple, counted",
        widget=CountrySelectMultiple(counted=True),
        help_text="Several countries, with counted=True: a count in place of the "
        "countries, and a tick on each one chosen.",
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

    autocomplete_country = TomSelectChoiceField(
        label="TomSelectChoiceField with country_config",
        config=country_config(
            "ac-flagged-countries",
            placeholder="Search for a country",
            plugin_clear_button=PluginClearButton(),
        ),
        help_text="One country, fetched from CountryAutocomplete as you type. "
        "The page holds none of the list.",
    )
    autocomplete_countries = TomSelectMultipleChoiceField(
        label="TomSelectMultipleChoiceField with country_config",
        config=country_config(
            "ac-flagged-countries",
            placeholder="Add a country",
            plugin_remove_button=PluginRemoveButton(),
        ),
        help_text="Several countries, fetched from CountryAutocomplete as you type.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Save"))
