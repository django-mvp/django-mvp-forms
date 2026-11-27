# Research: Country controls with a flag in each option

Written at specification time with the assumptions the specification makes about code that
already exists. The full investigation, and the planning notes answered by name, are added when
the feature is planned.

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
