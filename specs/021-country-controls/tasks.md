# Tasks — 021 Country controls with a flag in each option

**Branch**: `021-country-controls` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I: the tests are written and seen to
fail for the right reason, then the code is written. A task is done when its tests pass, the tree
is green and the work is committed. Documentation lands in the task that introduces what it
describes.

No test asserts wording, a colour, a width or a class used only for looks. A widget test asserts
the attributes written, the error raised for each refused option and the media. A browser test
asserts what the script does to the page and to the field's value.

Code standards for every task: no leading-underscore names, methods, helpers, templates or
constants; line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. The pack's templates are plain Django templates, not
Cotton. Everything under `.github/` does not change. A document reads as current state. README
links are absolute. The look files (the flag row, the demo forms and their labels, the routes and
the documentation page's wording) are ported from `origin/prototype-countries`, never redrawn.

## Order

**US1 → US2 → US3, sequential, in the feature worktree.**

---

## Phase 1: User Story 1 — A developer gives a country field a searchable control with flags (P1)

Issue: #276. Delivers FR-001 to FR-008, FR-021 to FR-023 (the widgets' part); SC-001, SC-003, SC-007.

### Group 1

- [ ] T001 [US1] The script reads an option template and an item template

**Files**: `tests/test_countries_e2e.py` (new), `mvp_forms/static/mvp_forms/tomselect.js`

Plan, *The script*. A select whose `data-tom-select` holds `render.option` and `render.item` draws
each from the template, escaping every value; one with no `render` is drawn as before.

- [ ] T002 [US1] `CountrySelect` and `CountrySelectMultiple`, the flag on each option

**Files**: `tests/test_countries.py` (new), `mvp_forms/countries.py` (new),
`tests/test_pack/test_independence.py`

Plan, *Python*. `FlaggedOptions`, `FLAGGED`, the two widgets. `data-flag` on every option with a
value and none on the empty choice. Settings and refusals inherited. The single widget starts
empty on a field whose choices have a break (D6). The module imports with django-tomselect absent.

### Group 2

- [ ] T003 [US1] Through every renderer, in the browser, in the demo and the documentation

**Files**: `tests/forms.py`, `tests/test_pack/test_countries.py`, `tests/test_countries_e2e.py`,
`demo/examples/third_party/countries.py`, `demo/examples/urls.py`,
`demo/docs/third-party-support/django-countries.md`, `README.md`, `CONTEXT.md`, `CHANGELOG.md`

Plan, *The tests*, *Documentation and the demo*. The widgets drawn by `{{ form|crispy }}` and
`{% crispy form %}` carry the classes and attributes of any Tom Select select. In Chrome: search,
choose, flag before the name in the list and the chosen value, remove buttons, counted, a value
already chosen, a formset row and htmx-added select. Demo `AddressForm` and the first section of
the page, as the prototype has them.

---

## Phase 2: User Story 2 — A developer routes a country autocomplete and builds a fetched country field (P2)

Issue: #277. Delivers FR-009 to FR-014, FR-021 to FR-023 (the view's part); SC-002, SC-005.

- [ ] T004 [US2] `CountryAutocomplete` and `country_config`

**Files**: `tests/test_countries.py`, `mvp_forms/countries.py`

Plan, *Python*. Pages of 20, search by name and code ignoring case, django-countries' order,
results with `value`, `label`, `flag`. `country_config` carries the URL name, `value_field`,
`label_field`, the minimum query length of 0 and the two templates as JSON strings; any
`TomSelectConfig` setting passes. Both are absent without django-tomselect, and the widgets import.

- [ ] T005 [US2] The constitution, the record, the browser, the demo and the documentation

**Files**: `CONSTITUTION.md`, `docs/adr/0073-an-autocomplete-view-for-a-supported-package.md`,
`tests/test_countries_e2e.py`, `demo/examples/third_party/countries.py`,
`demo/examples/urls.py`, `demo/urls.py`,
`demo/docs/third-party-support/django-countries.md`, `README.md`, `CONTEXT.md`, `CHANGELOG.md`

Article XII amended (FR-014) with the ADR. In Chrome, under django-tomselect 2026.6.2: the fetched
control opens, searches, shows flag before name in options and chosen values with no page error,
and posts the codes. Demo `FetchedCountriesForm` (its first two fields), the `ac-flagged-countries`
route and the page section, as the prototype has them.

---

## Phase 3: User Story 3 — A developer lists some countries first (P3)

Issue: #278. Delivers FR-015 to FR-020, FR-021 to FR-023 (the grouping's part); SC-004.

- [ ] T006 [US3] Countries first in the widgets and in the view

**Files**: `tests/test_countries.py`, `mvp_forms/countries.py`

Plan, *Python*. `grouped_at_break` and `optgroups()` for both widgets. Countries first outside any
group and ahead of the rest, the rest under one group headed by the break, no group without a break,
each country once whatever `first_repeat` says, the settings route (`COUNTRIES_FIRST`,
`COUNTRIES_FIRST_BREAK`), the stock select untouched. `CountryAutocomplete.countries` and the
`optgroup` of results after the break.

- [ ] T007 [US3] Countries first in the browser, the demo and the documentation

**Files**: `tests/test_countries_e2e.py`, `demo/examples/third_party/countries.py`,
`demo/examples/urls.py`, `demo/urls.py`, `demo/docs/third-party-support/django-countries.md`,
`README.md`, `CONTEXT.md`, `CHANGELOG.md`

In Chrome: the single control on a field with a break starts empty, the break is a heading no one
can choose, a search lists matches among the countries first above the heading, the fetched control
lists the rest under the heading. Demo `GermanSpeakingFirst`, `CountriesFirstForm`, the third
fetched field and the `ac-flagged-countries-first` route, and the page section with the
`first_repeat` sentence, as the prototype has them.
