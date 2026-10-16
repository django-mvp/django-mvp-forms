"""django-countries' own fields, drawn by this package with nothing added."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

# django-countries places the flag by this argument. This one sits the flag
# beside its select.
FLAG_BESIDE = (
    '<div class="flex items-center gap-2">{widget}'
    '<img class="country-select-flag" id="{flag_id}" src="{country.flag}"></div>'
)


class AddressForm(forms.Form):
    """One country, several countries, and one with its flag."""

    country = CountryField().formfield()
    visited = CountryField(multiple=True).formfield(required=False)
    born_in = CountryField().formfield(
        widget=CountrySelectWidget(layout=FLAG_BESIDE), required=False
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
