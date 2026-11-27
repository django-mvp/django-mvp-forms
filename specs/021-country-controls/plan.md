# Plan: Country controls with a flag in each option

**Branch**: `021-country-controls` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

One new module, `mvp_forms/countries.py`, holds everything that touches django-countries: the two
widgets, the grouping of the countries first, and, where django-tomselect is installed, the
autocomplete view and `country_config`. One small addition to the pack's Tom Select script lets a
select state an option template and an item template. Nothing else in the package changes, no
stylesheet is added, and the stock select of a django-countries field is drawn as it is today.

The look comes from the approved prototype and is ported, never redrawn: the flag row, the demo
forms, the routes and the documentation page keep the prototype's markup, labels and wording. The
behaviour is rebuilt test-first.

## The script (`mvp_forms/static/mvp_forms/tomselect.js`)

`settings()` reads `render.option` and `render.item` from `data-tom-select` when they are present.
Each is turned into a Tom Select render function that replaces every `${data.name}` with that value
of the option's data, escaped with the `escape` Tom Select passes in, and an absent value with the
empty string. A select that states no `render` gets the settings it gets today. The prototype's
function is the model, with tests behind it. The setting stays internal to the country widgets
(research: no public `TomSelect` argument is needed, and adding one is a surface nobody asked for).

## Python (`mvp_forms/countries.py`, new)

- `FLAGGED`: the flag row string of the prototype, one `%s` for the field that holds the name
  (`text` for a widget, `label` for the fetched control). The widgets and `country_config` share
  it.
- `grouped_at_break(choices)`: the prototype's function. Choices with a break (an entry after
  at least one country whose value is empty) come back as the countries first, then one group headed
  by the break's text, each country that `first_repeat` listed again left out. No break: unchanged.
- `FlaggedOptions`: a mixin for the two widgets.
  - `optgroups()` regroups the choices as `TimeZoneSelect` does (copy the widget, set `choices`).
    For a single widget, where no choice of empty value is left outside the groups, it puts
    `*BLANK_CHOICE_DASH` first (django's constant, as django-countries uses it), so a field with a
    break, or a required field with no blank choice, starts empty (D6). A multiple widget needs
    none. A single widget that draws the empty choice answers `use_required_attribute` as the
    stock `Select` would for a select whose first option is empty, so a required field carries
    `required`.
  - `create_option()` writes `data-flag` with `Country(code=...).flag` on every option that has a
    value.
  - `control_settings()` adds `render` with `FLAGGED % "text"` for `option` and `item`.
- `CountrySelect(FlaggedOptions, TomSelect)` and `CountrySelectMultiple(FlaggedOptions,
  TomSelectMultiple)`: nothing else, so every setting and error is inherited (FR-002).
- Where `django_tomselect` imports: `CountryAutocomplete(AutocompleteIterablesView)` with
  `countries = django_countries.countries`, `page_size = 20`, `iterable = ()` (the parent's
  `get()` answers nothing while it is `None`, and a line says so), `get_iterable()` answering from
  `grouped_at_break(self.countries)`, each result `value`, `label`, `flag`, and `optgroup` for those
  after the break. Each flag is `Country(code=..., custom_countries=self.countries).flag`, so a
  `Countries` subclass's own flag addresses are honoured. A search matches name or code through the parent's `search()`.
  `country_config(url, **kwargs)` returns a `TomSelectConfig` with `value_field="value"`,
  `label_field="label"`, `minimum_query_length` defaulting to 0, and the two templates given
  already as JSON strings in `attrs["data_template_option"]` and `["data_template_item"]`, with a
  comment naming django-tomselect 2026.6.2 (D8).
- The `try/except ImportError` of the prototype stays: the module imports with django-countries
  alone. It is the one module that imports django-countries (FR-008).
- `pyproject.toml` gains two extras, `countries = ["django-countries>=9.1.0"]` and
  `tomselect = ["django-tomselect>=2026.6.2"]`, each with a comment naming what imports it, because
  deptry reports a module that imports a package declared only in the development group
  (Article VII). `uv.lock` is regenerated.

## Constitution and record

Article XII is amended in this pull request to read that the package ships no views of its own
except an autocomplete view for a supported package, which the host project routes, still no
URLs. The footer's version goes from 2.4.1 to 2.5.0 and its date to the day of the amendment. ADR
0073 (next free number on origin/main, re-read at the push) records the amendment and why (D5).
The constitution asks that an amendment be made in its own pull request. FR-014 puts it in this
one, on the maintainer's approved specification, and the report at the merge gate says so
(D11).

## Documentation and the demo

- `demo/examples/third_party/countries.py`, `demo/examples/urls.py`, `demo/urls.py`,
  `demo/docs/third-party-support/django-countries.md`: the prototype's files, ported. The docs page
  keeps its prototype wording and gains the sentence on `first_repeat`.
- README: the django-countries section describes the widgets, the view, `country_config`, the
  countries first and `first_repeat`, and the recipe that put the flag beside the select is
  replaced (D3). `CONTEXT.md` names the new terms. CHANGELOG `Unreleased` gets an Added entry.
- Each documentation change lands in the story that introduces the name.

## The tests

- `tests/test_countries.py` (new, widget level): options carry `data-flag`; the empty choice
  carries none; settings pass through and refuse as `TomSelect` does; the `render` setting is
  written; countries first with and without a break, `first_repeat`, the settings route (the
  suite clears django-countries' cache with `del countries.countries` around each such test); a
  single field with a break starts on its empty option and a required one carries `required`; the module imports with django-tomselect absent;
  `CountryAutocomplete` pages, searches by name and code, orders, groups; `country_config` carries
  the quoted templates.
- `tests/test_pack/test_countries.py` keeps the stock-select tests and gains the two widgets in
  its field list, so they draw with the classes, colour, size, variant, error and disabled
  attributes of any Tom Select select. `tests/forms.py` `CountriesForm` gains the fields.
- `tests/test_countries_e2e.py` (new, Chrome): the script reads a stated template, escapes values,
  draws flag before name in options and items, a single control with no value starts empty,
  counted and remove buttons, and the fetched control against `CountryAutocomplete` under
  django-tomselect 2026.6.2 with no page error.
- A canary beside `country_config`'s tests (D8, D11): the script django-tomselect 2026.6.2 draws
  for a control given `country_config` holds `var template = ` followed by exactly the flag row.
  It goes red on the django-tomselect release that quotes the template itself, and the workaround
  is removed in the pull request that moves to that release.
- `tests/test_pack/test_independence.py` allows `mvp_forms/countries.py` alone to import
  django-countries and django-tomselect.
- Mutations are run before the review (S5).

## Constraints kept

No leading-underscore names. Line length 88. No compatibility aliases. No test of text content,
layout or widths. Plain templates, no Cotton. `.github/` untouched. No stylesheet. Documents read
as current state.
