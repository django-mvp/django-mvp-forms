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

import copy
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


def grouped_at_break(choices):
    """Return country choices with the countries after the break in a group.

    django-countries lists the countries its ``first`` option names ahead of
    the rest, and when ``first_break`` is set writes that text between them as
    a choice with no value. The countries first stay outside every group, at
    the top, and the rest go under a heading of the break's text. A Tom Select
    control holds one option for each value, so a country ``first_repeat``
    lists again among the rest is left out there. Choices with no break come
    back as they are.
    """
    choices = list(choices)
    for index, (value, label) in enumerate(choices):
        if index and not value and any(code for code, _name in choices[:index]):
            first = {code for code, _name in choices[:index]}
            rest = [choice for choice in choices[index + 1 :] if choice[0] not in first]
            return [*choices[:index], (str(label), rest)]
    return choices


class FlaggedOptions:
    """Write each country's flag on its option, and draw options with it.

    Countries after django-countries' ``first_break`` are grouped under it.
    """

    def optgroups(self, name, value, attrs=None):
        """Return the option groups, the countries after the break in one."""
        grouped = copy.copy(self)
        grouped.choices = grouped_at_break(self.choices)
        return super(FlaggedOptions, grouped).optgroups(name, value, attrs)

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
        or the code. ``countries`` is the list to answer from, django-countries'
        own by default: give it a ``Countries`` subclass to put some countries
        first. The countries after its ``first_break`` carry the break's text in
        ``optgroup``, so they are listed under that heading.
        """

        iterable = True
        page_size = 20
        countries = countries

        def get_iterable(self):
            """Return every country as a result."""
            results = []
            for entry in grouped_at_break(self.countries):
                code, name = entry
                if isinstance(name, list):
                    results.extend(
                        {
                            "value": c,
                            "label": n,
                            "flag": Country(code=c).flag,
                            "optgroup": code,
                        }
                        for c, n in name
                    )
                elif code:
                    results.append(
                        {"value": code, "label": name, "flag": Country(code=code).flag}
                    )
            return results

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
