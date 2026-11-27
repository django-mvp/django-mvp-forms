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
"""

import json

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
    """Write each country's flag on its option, and draw options with it."""

    def create_option(self, name, value, label, selected, index, **kwargs):
        """Add the flag of the option's country in ``data-flag``."""
        option = super().create_option(name, value, label, selected, index, **kwargs)
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
        or the code.
        """

        iterable = True
        page_size = 20

        def get_iterable(self):
            """Return every country as a result."""
            return [
                {"value": code, "label": name, "flag": Country(code=code).flag}
                for code, name in countries
            ]

    def country_config(url, **kwargs):
        """Configure a django-tomselect field to fetch countries from ``url``.

        Args:
            url: The name of the URL that serves ``CountryAutocomplete``.
            **kwargs: Any other setting of ``TomSelectConfig``.
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
