# Prototype: country controls with flags

Branch `prototype-countries`. A reference for the rebuild, never merged.

## The features

1. **A searchable country control with flags, its options written into the page.**
   A developer gives a django-countries form field `CountrySelect` or
   `CountrySelectMultiple` and gets a Tom Select control: a search box, the
   flag beside each country in the list and in each chosen value, and every
   setting of `TomSelect` and `TomSelectMultiple` (placeholder, clear button,
   remove buttons, counted, maximum).
   Screen: `/examples/countries/`. Code: `mvp_forms/countries.py`
   (`FlaggedOptions`, `CountrySelect`, `CountrySelectMultiple`).
2. **A country autocomplete view for django-tomselect.**
   A developer routes `CountryAutocomplete` and builds a django-tomselect field
   with `country_config(url, ...)`. The control fetches countries as a person
   types, each with its flag, and the page holds none of the list.
   Screen: `/examples/countries/fetched/`. Code: `mvp_forms/countries.py`
   (`CountryAutocomplete`, `country_config`).

Feature 1 depends on the shared piece below. Feature 2 depends on nothing new.

## The shared pieces

- **Option and item templates for the pack's Tom Select widgets.**
  `mvp_forms/static/mvp_forms/tomselect.js` reads `render.option` and
  `render.item` from `data-tom-select` and fills each `${data.name}` with that
  value of the option, escaped, the syntax django-tomselect uses for its own
  templates. Tom Select reads each `data-*` attribute of an option into the
  option's data, so `data-flag` on the option is `data.flag` in the template.
  Built by feature 1. Whether `TomSelect` gets a public setting for it, or it
  stays internal to the country widgets, is the rebuild's call.
- **The flag row** `FLAGGED` in `mvp_forms/countries.py`: the flag image at its
  own size (16 × 11) and the name, in a flex row of Tailwind utilities. It sits
  inside an extra element, because the pack's stylesheet sets the display of
  the item in a single control.

## The look

No stylesheet was added or changed. The look is the pack's own Tom Select
control plus the flag row above.

| Screen | Address | Widths |
|---|---|---|
| Stock select, searched single, multiple with remove buttons, counted multiple | `/examples/countries/` | 390, 1280 |
| Fetched single and multiple | `/examples/countries/fetched/` | 390, 1280 |
| Docs page | `/third-party-support/django-countries/` | 1280 |

## What it replaces

- The old demo's third field, django-countries' `CountrySelectWidget` with a
  flag image placed beside the select. Removed.
- The old demo's multiple field, a stock multiple select of 250 countries.
  Replaced by `CountrySelectMultiple`.
- The docs page `demo/docs/third-party-support/django-countries.md`, rewritten.
- The tests in `tests/test_pack/test_countries.py` and `CountriesForm` in
  `tests/forms.py` still describe the old demo and are not updated here.

## Faked or skipped

- **django-tomselect 2026.6.2 writes its `render` templates into the page
  script unquoted**, which stops the control with a syntax error.
  `country_config` gives the templates as `data_template_option` and
  `data_template_item`, already quoted, which the template reads directly. The
  rebuild decides whether to keep that or wait for a fixed release.
- No tests, no changelog, no README template list entry.
- The flag image has an empty `alt`, since the country's name is beside it.
- django-countries' list is used as it is: no `countries_first`, no
  translations checked.

## Sam's decisions

- 2026-11-27: Tom Select versions, one with the options in the page and one
  fetched through a django-tomselect view. Flags inside the options, never
  beside the select. Work within the existing widgets and add no stylesheet.
