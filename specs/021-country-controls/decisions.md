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

**Self-resolved.** **ADR:** none.

## D2. No story for the person filling in the form

**Chosen:** what a person sees and does (typing to search, the flag in each option) is stated as
outcomes under each developer story.

**Why:** the person gains no new way to do anything. Searching a Tom Select control and choosing
from it is what the pack's controls already offer. What is new is a widget a developer names, and
the flag it draws. A story of the person's own would repeat the developer stories' scenarios.

**Self-resolved.** **ADR:** none.

## D3. The stock select and django-countries' flag widget are untouched

**Chosen:** a django-countries field given no widget, or `CountrySelectWidget`, is drawn exactly
as today. The demo stops showing the flag beside the select, and the README's recipe for placing
it there is replaced by the country widgets. The pack still draws `CountrySelectWidget`'s select.

**Why:** the maintainer decided "the stock select stays as django-countries draws it". Removing
the demo field is the prototype's decision. Dropping the pack's drawing of a widget a host project
may use would break that project for no gain, so only the demo and the recipe go.

**Self-resolved.** **ADR:** none.

## D4. The country widgets live in a module of their own

**Chosen:** the widgets, the view and `country_config` sit in a module that imports
django-countries, and no other module of the package does. The view and `country_config` exist
only where django-tomselect is installed.

**Why:** the README promises that django-countries is not a dependency and that a project without
it is drawn as before. A module the host project imports only when it wants the country controls
keeps that promise. django-tomselect is optional too, so a project with django-countries alone
must still have the widgets.

**Self-resolved.** **ADR:** none. The module's name is the plan's call.

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

**Self-resolved, and the item most worth his veto.** **ADR:** yes, with the amendment.

## D6. A single control with no value starts empty

**Chosen:** a single country control whose field holds no value holds no country when it starts,
with or without a break.

**Why:** django-countries uses the break as the empty choice of a field with `first_break`, with
no separate blank choice (checked, `research.md`). The prototype turns the break into a heading,
which leaves the select with no option of empty value, so the browser selects the first country
and the control starts holding it. A person who never touched the field would then submit
Germany. The stock select starts on the empty choice, and the control must do the same.

**Self-resolved.** **ADR:** none.

## D7. `first_repeat` has no effect on the country controls

**Chosen:** each country is listed once, among the countries first where it is one of them.

**Why:** a Tom Select control holds one option per value, so a country cannot be listed twice
(prototype, "Faked or skipped"). The documentation says so, so a developer who sets it knows why
it does nothing.

**Self-resolved.** **ADR:** none.

## D8. The django-tomselect quoting defect is worked round, not waited on

**Chosen:** `country_config` gives django-tomselect its option and item templates already quoted,
as the attributes its template reads, with a comment naming django-tomselect 2026.6.2.

**Why:** 2026.6.2 copies a `render` setting into the attributes as given, and its template writes
that value into the page script unquoted, which is a syntax error (checked, `research.md`). It is
the latest release on 2026-11-27, so no fixed release exists to use. The workaround must keep
working if a later release quotes the template itself, which the build checks.

**Self-resolved.** **ADR:** none.

## D9. The demo's labels name the field and the widget

**Chosen:** every demo field on the country screens is labelled with the field and widget it uses,
and its help text names the settings it shows.

**Why:** the maintainer's decision of 2026-11-27. The demo exists to show a developer what each
widget does, not to imitate a form.

**Self-resolved.** **ADR:** none.

## D10. The demo project's other changes are not this feature

**Chosen:** the demo's documentation theme, its user model and the dependency upgrade the
prototype made are left to the separate work that carries them
([#274](https://github.com/django-mvp/django-mvp-forms/issues/274)). No success criterion is
measured on them, and the side-by-side check covers the three example screens.

**Why:** the prototype needed the upgrade to show its docs page in the new theme, but nothing in
the country controls depends on it.

**Self-resolved.** **ADR:** none.
