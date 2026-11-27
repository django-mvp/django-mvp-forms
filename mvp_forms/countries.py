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
