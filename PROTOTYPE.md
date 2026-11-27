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

3. **Some countries first, grouped.** A developer configures django-countries'
   `first` and `first_break` (a `Countries` subclass on the field, or the
   settings), and the country widgets list those countries at the top and the
   rest under a heading of the break's text. `CountryAutocomplete` takes a
   `countries` to answer from and gives the rest an `optgroup` of the break's
   text. Screens: `/examples/countries/first/` and the third field of
   `/examples/countries/fetched/`. Code: `grouped_at_break` in
   `mvp_forms/countries.py`.

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

## The demo project

- django-mvp-sphinx is upgraded from 0.6.1 to 0.11.1, which styles the docs
  pages with sphinx-daisyui. `demo/docs/conf.py` names the `daisyui` theme.
  The demo had no styles of its own for the docs pages to remove.
- The upgrade brings django-mvp 0.40, which needs `object_preferences`, its
  `PreferencesMiddleware` and a user model with `PreferencesMixin`. The demo
  gets `demo.User` and its first migration, so an existing `demo.sqlite3` has to
  be recreated. The sidebar renderer is django-mvp-sphinx's.
- Every field of the country demos is labelled with the field and widget it
  uses, and its help text names the settings it shows.

## Faked or skipped

- A Tom Select control holds one option for each value, so `first_repeat` is
  dropped in the country widgets: a country first is not listed again below.
- django-countries' own stock select, with `first_break` on a field that
  starts empty, shows the break's text as the chosen value, because the blank
  choice and the break both have the empty value. The country widgets don't,
  since the break becomes a heading.

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
- 2026-11-27: The flag stays before the name. Each demo field is labelled with
  what it uses, not a made-up form's wording. Use django-mvp-sphinx's own docs
  styling, upgraded, with no demo overrides.
- 2026-11-27: Offer django-countries' "countries first" as the grouping, with
  demos. No continent or region grouping: django-countries has no such data
  and no other source is added.
