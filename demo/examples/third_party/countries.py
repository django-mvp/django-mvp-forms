"""django-countries' fields, as a stock select and as Tom Select controls with flags."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries.fields import CountryField

from mvp_forms.countries import CountrySelect, CountrySelectMultiple


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
