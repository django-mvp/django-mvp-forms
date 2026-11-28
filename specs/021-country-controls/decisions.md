# Decisions: Country controls with a flag in each option

Rationale too long to inline in `spec.md`, and every place the issue was silent and a reading was
chosen. The screens of the prototype and the maintainer's recorded decisions on it are taken as
agreed. Everything below was self-resolved from them and is the maintainer's to overturn when he
reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. One feature, three stories

**Chosen:** the searchable widgets, the fetched control and the countries first are one feature
with three developer stories.

**Why:** all three give a django-countries field a control with flags, they share the flag row
and the option template, and the third extends the first two. A developer sets out to do each of
the three on its own, so each is a story. Every setting of the widgets, the empty choice, htmx and
formsets are scenarios under the first story, not stories of their own.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D2. No story for the person filling in the form

**Chosen:** what a person sees and does (typing to search, the flag in each option) is stated as
outcomes under each developer story.

**Why:** the person gains no new way to do anything. Searching a Tom Select control and choosing
from it is what the pack's controls already offer. What is new is a widget a developer names, and
the flag it draws. A story of the person's own would repeat the developer stories' scenarios.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D3. The stock select and django-countries' flag widget are untouched

**Chosen:** a django-countries field given no widget, or `CountrySelectWidget`, is drawn exactly
as today. The demo stops showing the flag beside the select, and the README's recipe for placing
it there is replaced by the country widgets. The pack still draws `CountrySelectWidget`'s select.

**Why:** the maintainer decided "the stock select stays as django-countries draws it". Removing
the demo field is the prototype's decision. Dropping the pack's drawing of a widget a host project
may use would break that project for no gain, so only the demo and the recipe go.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D4. The country widgets live in a module of their own

**Chosen:** the widgets, the view and `country_config` sit in a module that imports
django-countries, and no other module of the package does. The view and `country_config` exist
only where django-tomselect is installed.

**Why:** the README promises that django-countries is not a dependency and that a project without
it is drawn as before. A module the host project imports only when it wants the country controls
keeps that promise. django-tomselect is optional too, so a project with django-countries alone
must still have the widgets.

**Self-resolved.**

**ADR:** none — the module's name is a local choice nothing else inherits.

## D5. The autocomplete view needs Article XII amended

**Chosen:** `CountryAutocomplete` ships, and the build amends CONSTITUTION.md Article XII to allow
an autocomplete view for a supported package that the host project routes itself. The package
still ships no URL.

**Why:** Article XII says the package ships no views. The maintainer asked for "a version that
uses django-tomselect, with a view that answers with countries" (prototype issue,
[#272](https://github.com/django-mvp/django-mvp-forms/issues/272)), and his decision of
2026-11-27 accepted it. The article exists to keep page views, form views and formset handling
out of the package, which belong to django-mvp. An autocomplete view for a supported package is
the data source of a widget, not a page. Leaving the article as it is would make the agreed
feature unconstitutional.

**Self-resolved, and the item most worth his veto.**

**ADR:** docs/adr/0073-an-autocomplete-view-for-a-supported-package.md

## D6. A single control with no value starts empty

**Chosen:** a single country control whose field holds no value holds no country when it starts,
with or without a break.

**Why:** django-countries uses the break as the empty choice of a field with `first_break`, with
no separate blank choice (checked, `research.md`). The prototype turns the break into a heading,
which leaves the select with no option of empty value, so the browser selects the first country
and the control starts holding it. A person who never touched the field would then submit
Germany. The stock select starts on the empty choice, and the control must do the same.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D7. `first_repeat` has no effect on the country controls

**Chosen:** each country is listed once, among the countries first where it is one of them.

**Why:** a Tom Select control holds one option per value, so a country cannot be listed twice
(prototype, "Faked or skipped"). The documentation says so, so a developer who sets it knows why
it does nothing.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D8. The django-tomselect quoting defect is worked round, not waited on

**Chosen:** `country_config` gives django-tomselect its option and item templates already quoted,
as the attributes its template reads, with a comment naming django-tomselect 2026.6.2.

**Why:** 2026.6.2 copies a `render` setting into the attributes as given, and its template writes
that value into the page script unquoted, which is a syntax error (checked, `research.md`). It is
the latest release on 2026-11-27, so no fixed release exists to use. The workaround must keep
working if a later release quotes the template itself, which the build checks.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D9. The demo's labels name the field and the widget

**Chosen:** every demo field on the country screens is labelled with the field and widget it uses,
and its help text names the settings it shows.

**Why:** the maintainer's decision of 2026-11-27. The demo exists to show a developer what each
widget does, not to imitate a form.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D10. The demo project's other changes are not this feature

**Chosen:** the demo's documentation theme, its user model and the dependency upgrade the
prototype made are left to the separate work that carries them
([#274](https://github.com/django-mvp/django-mvp-forms/issues/274)). No success criterion is
measured on them, and the side-by-side check covers the three example screens.

**Why:** the prototype needed the upgrade to show its docs page in the new theme, but nothing in
the country controls depends on it.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D11. Design review of the plan

**Chosen:** the plan takes each finding of the design review that adds no work beyond a stated
requirement, and records the two readings below for the maintainer.

- **deptry and the extras.** Article VII requires deptry to pass, and it reports a module that
  imports a package declared only in the development group. The package gains the extras
  `countries` and `tomselect`, as it has `timezone`. Nothing becomes a required dependency.
- **The canary.** The obvious upstream fix of the quoting defect would quote the template a second
  time, which a workaround that already quotes would show as quote marks in every option. The spec's
  edge case asks for a control that keeps working when the defect is fixed. Reading chosen: a
  canary test fails on the first django-tomselect release that quotes the template, and the
  workaround goes in the pull request that moves to that release. A project that moves to that
  release before the package's next release sees the quote marks until then. Fully tolerating both
  behaviours would need the workaround to read django-tomselect's version, a mechanism the spec does
  not ask for.
- **The amendment's own pull request.** The constitution asks that an amendment be made in its own
  pull request. FR-014 puts it in this one, on the maintainer's approved specification. The
  amendment goes in with its ADR and a new footer (version 2.5.0). The pull request says so.
- **A flag the `Countries` object overrides.** The autocomplete reads each flag through the
  `Countries` it answers from. A widget sees only the choices its field gives it, so it draws
  django-countries' own address for each country, which honours `COUNTRIES_FLAG_URL`. A per-country
  flag address set on a `Countries` subclass shows in the fetched control and not in the widgets.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D12. The three stories are built one after another

**Chosen:** the three stories share one module, one script and one demo page, so they are built
one after another, each test first. Each story ends on a green run of every check before the
next begins, since each build leans on the one before.

**Self-resolved.**

**ADR:** none — local to this feature, nothing downstream inherits it.

## D13. Two tests that existed before this feature are changed

**Chosen:** the tests of the pack's draw of a django-countries field gain the two new widgets'
fields, and the rule that no module imports django-countries is relaxed for the one module that
is meant to.

**Why:** `tests/test_pack/test_countries.py` now draws, posts, disables and cleans two more
fields, and asserts everything it asserted before. Nothing was removed or loosened. The
independence test forbade every module of the package from importing django-countries, and
FR-008 makes `mvp_forms/countries.py` the one module that does, so the rule now allows that file
alone, for django-countries and django-tomselect, and still forbids both everywhere else.

**Self-resolved.**

**ADR:** none — a test follows a requirement of this feature and nothing downstream inherits it.
