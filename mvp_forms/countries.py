"""Country controls for django-countries, each option drawn with its flag.

Two ways to offer countries, which the host project picks between:

- ``CountrySelect`` and ``CountrySelectMultiple`` write every country into the
  page with the form, as the pack's other Tom Select widgets do. Each option
  carries its flag image in ``data-flag``.
- ``CountryAutocomplete`` is a django-tomselect view that answers as a person
  types, so the page holds none of the list. ``country_config`` configures a
  django-tomselect field to use it with the same flag in every option.

The flag is the image django-countries serves, drawn at its own size beside
the country's name. Nothing here needs a stylesheet.

This is the one module of the package that imports django-countries.
"""

import copy
import json

from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from django_countries import countries
from django_countries.fields import Country

from mvp_forms.widgets import TomSelect, TomSelectMultiple

# The flag before the name, in each option and each chosen value. Tom Select
# reads the text of an option from ``text``, django-tomselect from ``label``.
# The row sits inside the element Tom Select draws, whose own display the
# stylesheet sets for a single control.
FLAGGED = (
    '<div><span class="flex items-center gap-2">'
    '<img src="${data.flag}" alt="" width="16" height="11">'
    "<span>${data.%s}</span></span></div>"
)


class FlaggedOptions:
    """Write each country's flag on its option, and draw options with it.

    A single control starts holding no country. Tom Select offers no option of
    empty value, so one is drawn first when the field's choices have none, and
    the browser has nothing to start on but that.
    """

    def optgroups(self, name, value, attrs=None):
        """Return the option groups, with an empty option first in a single one."""
        choices = list(self.choices)
        if not self.allow_multiple_selected and not any(
            not code and not isinstance(label, (list, tuple)) for code, label in choices
        ):
            choices = [*BLANK_CHOICE_DASH, *choices]
        drawn = copy.copy(self)
        drawn.choices = choices
        return super(FlaggedOptions, drawn).optgroups(name, value, attrs)

    def use_required_attribute(self, initial):
        """Draw a required field required, whatever its first choice is.

        The empty option drawn first is not one of the field's choices, so
        Django's own answer, which reads the first choice, would drop it.

        Args:
            initial: The field's initial value, which Django passes on.

        Returns:
            Whether the select carries the ``required`` attribute.
        """
        return forms.Widget.use_required_attribute(self, initial)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """Add the flag of the option's country in ``data-flag``."""
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        code = "" if value is None else str(value)
        if code:
            option["attrs"]["data-flag"] = Country(code=code).flag
        return option

    def control_settings(self):
        """Draw each option and each chosen value with its flag."""
        settings = super().control_settings()
        settings["render"] = {"option": FLAGGED % "text", "item": FLAGGED % "text"}
        return settings


class CountrySelect(FlaggedOptions, TomSelect):
    """A searchable control for one country, each option with its flag."""


class CountrySelectMultiple(FlaggedOptions, TomSelectMultiple):
    """A searchable control for several countries, each option with its flag."""


try:
    from django_tomselect.app_settings import TomSelectConfig
    from django_tomselect.autocompletes import AutocompleteIterablesView
except ImportError:  # django-tomselect is optional.
    pass
else:

    class CountryAutocomplete(AutocompleteIterablesView):
        """Every country django-countries lists, with its code and its flag.

        Each result holds ``value``, the country's code, ``label``, its name,
        and ``flag``, the address of its flag image. A search matches the name
        or the code. ``countries`` is the list to answer from, django-countries'
        own by default.
        """

        # The parent answers nothing while ``iterable`` is None. The list is
        # read in ``get_iterable``, so any value that is not None will do.
        iterable = ()
        page_size = 20
        countries = countries

        def get_iterable(self):
            """Return every country as a result."""
            return [
                {
                    "value": code,
                    "label": name,
                    "flag": Country(code=code, custom_countries=self.countries).flag,
                }
                for code, name in self.countries
                if code
            ]

    def country_config(url, **kwargs):
        """Configure a django-tomselect field to fetch countries from ``url``.

        Args:
            url: The name of the URL that serves ``CountryAutocomplete``.
            **kwargs: Any other setting of ``TomSelectConfig``.

        Returns:
            The configuration, drawing each option and each chosen value with
            its flag.
        """
        kwargs.setdefault("minimum_query_length", 0)
        # django-tomselect writes these into its script as they are given. Its
        # own "render" setting reaches the script unquoted in 2026.6.2, which
        # stops the control, so the templates are given already quoted.
        attrs = kwargs.pop("attrs", {})
        attrs["data_template_option"] = json.dumps(FLAGGED % "label")
        attrs["data_template_item"] = json.dumps(FLAGGED % "label")
        return TomSelectConfig(
            url=url, value_field="value", label_field="label", attrs=attrs, **kwargs
        )
