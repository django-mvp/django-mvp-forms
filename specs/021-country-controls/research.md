# Research: Country controls with a flag in each option

Written at specification time with the assumptions the specification makes about code that
already exists. The full investigation, and the planning notes answered by name, are added when
the feature is planned.

## Packages brought up to date

`forge own-deps` on 2026-11-27 lists `django-mvp` 0.34.2 → 0.40.0, `daisy-cotton` 0.2.0 → 0.3.0
(through django-mvp) and `django-mvp-sphinx` 0.6.1 → 0.11.1, all dev-group packages of the demo.
django-mvp 0.40 requires `object_preferences`, `PreferencesMiddleware` and a user model with
`PreferencesMixin` in the demo, and that work, with the sphinx upgrade, is the open resolve run on
the tracker ([#274](https://github.com/django-mvp/django-mvp-forms/issues/274)), which edits
`demo/settings.py`, `demo/migrations/`, `pyproject.toml` and `uv.lock`. The three upgrades are one
chain and ride in that pull request. This branch makes no change to them and picks them up when it
brings itself up to date with `main`.

## Planning notes, answered

- **Option and item templates for the pack's Tom Select widgets**: adopted, internal to the country
  widgets. Nothing in the spec asks for a public `TomSelect` setting, and one would be a surface
  to support and document for no requester.
- **The flag row `FLAGGED`**: adopted as the prototype has it, in `mvp_forms/countries.py`, the
  one string serving the widgets and the fetched control.
- **The quoting defect**: the latest django-tomselect is 2026.6.2, so the workaround is kept, with
  a comment naming the version (D8), and a browser test covers both the current release and a
  release that quotes the template itself.
- **Design rules**: adopted without change.
- **The look is ported**: the plan names the six files and the story that lands each.
- **What it replaces**: `CountriesForm` keeps its stock fields and gains the widgets; the stock
  select's tests stay.
- **The empty choice and Article XII**: D6 and D5.

## What already exists

- Option groups for a Tom Select: `TimeZoneSelect.optgroups()` in `mvp_forms/widgets.py` (this
  repo). `FlaggedOptions.optgroups()` takes the same route.
- Search and paging of an iterable autocomplete: `AutocompleteIterablesView` (installed package).
- The flag address: `django_countries.fields.Country.flag` (installed package).
- Escaping an option's values: Tom Select's `escape` argument to a render function (the browser
  library the pack ships). Only the `${data.name}` filling is new code, the syntax django-tomselect
  already uses.
- Everything else of the widgets' settings: `TomSelect` and `TomSelectMultiple` (this repo).

## Assumptions checked

Each was run or read on the default branch at `f7b5060`, or in the installed release, on
2026-11-27.

- **The pack's Tom Select script reads only three settings.** `tomselect.js` copies
  `placeholder`, `maxItems` and `plugins` from `data-tom-select` and nothing else, so an option
  template written by a widget today is ignored. FR-005 is new work, and a select with no template
  stays as it is.
- **`TomSelect` and `TomSelectMultiple` take what FR-002 lists.** `placeholder`, `clear_button`,
  `remove_button`, `max_items`, `counted`, `none_text` and `count_text`, with their checks and
  errors, in `mvp_forms/widgets.py`. `TimeZoneSelect` already regroups its choices in
  `optgroups()`, the same route the countries first can take.
- **No module of the package imports django-countries.** A search of `mvp_forms/` finds no
  reference to it, as the README states.
- **django-countries' choices with countries first.** With `first = ["DE", "AT", "CH"]` and
  `first_break = "Other"`, a field's choices are the three countries, then `("", "Other")`, then
  the other 246 countries. No `("", "---------")` choice is added, whether the field is required
  or not: the break is the empty choice. Without `first_break` the blank choice comes first and
  then the three countries. Default `first_repeat` already leaves the three out of the rest.
- **The prototype's control on a field with a break has no empty option.** Its page
  `/examples/countries/first/` draws the single control's select starting with
  `<option value="DE">`, so the select starts on Germany (`decisions.md`, D6).
- **The flag address.** `Country(code="NZ").flag` is `/static/flags/nz.gif` under the demo's
  settings, from django-countries' static files.
- **django-tomselect 2026.6.2 is the latest release.** PyPI lists 2026.6.2 as the newest on
  2026-11-27, and it is the release in `uv.lock`.
- **The quoting defect is real in 2026.6.2.** `TomSelectWidgetMixin._process_render_attrs`
  copies `attrs["render"]["option"]` into `data_template_option` as given, with no quoting. The
  template `django_tomselect/render/option.html` writes
  `var template = {{ widget.attrs.data_template_option|safe }};`, so an unquoted string is a
  script syntax error. A value given already as a JSON string is read correctly.
- **`AutocompleteIterablesView` searches label and value.** Its `search()` keeps items whose
  `label` or `value` holds the query, lower-cased, so the autocomplete's search of name and code
  is django-tomselect's own.
- **The pack's django-tomselect template lists option groups.** CONTEXT.md and FS-014: an option
  carrying an `optgroup` key is listed under that heading when `mvp_forms` comes before
  `django_tomselect` in `INSTALLED_APPS`, as the demo has it.
