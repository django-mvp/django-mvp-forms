"""The forms the django-countries page draws."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from demo.forms import ChosenForm
from mvp_forms.choices import FormChoices


def country_field(**kwargs):
    """Build the field django-countries gives a model's country."""
    return CountryField().formfield(label=_("Country"), **kwargs)


def countries_field(**kwargs):
    """Build the field django-countries gives a model that holds several."""
    return CountryField(multiple=True).formfield(label=_("Countries"), **kwargs)


def flagged_field(**kwargs):
    """Build a country field drawn by django-countries' flag widget."""
    return CountryField().formfield(
        label=_("Country, with its flag"), widget=CountrySelectWidget(), **kwargs
    )


class CountriesForm(forms.Form):
    """The three country fields beside a text input, which can be posted."""

    name = forms.CharField(label=_("Name"), required=False)
    country = country_field(help_text=_("One country, from a stock select."))
    countries = countries_field(
        required=False, help_text=_("Several countries, from a multiple select.")
    )
    flagged = flagged_field(
        required=False, help_text=_("The flag follows the country you pick.")
    )

    def __init__(self, *args, **kwargs):
        """Build the helper and a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class CountriesStateForm(ChosenForm):
    """The three country fields in one state.

    Args:
        state: ``"filled"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with nothing posted, so every field fails.
    """

    country = country_field()
    countries = countries_field()
    flagged = flagged_field()

    def __init__(self, *args, state, **kwargs):
        """Put the fields in their state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        if state in ("filled", "disabled"):
            self.initial.update(country="DE", countries=["FR", "JP"], flagged="NZ")
        for field in self.fields.values():
            field.disabled = state == "disabled"


class CountriesSizedForm(ChosenForm):
    """The three country fields at one size.

    Args:
        size: The size the form states.
    """

    country = country_field(required=False)
    countries = countries_field(required=False)
    flagged = flagged_field(required=False)

    def __init__(self, *args, size, **kwargs):
        """State the size for the form."""
        super().__init__(*args, choices=FormChoices(size=size), **kwargs)
        self.initial.update(country="JP", countries=["DE", "NZ"], flagged="FR")
