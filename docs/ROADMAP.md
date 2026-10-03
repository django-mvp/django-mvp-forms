# Roadmap — django-mvp-forms

**Date:** 2026-10-03

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor release: some take several, and one release can move
two. Once `1.0` ships, a breaking change never goes out as `1.x` — it waits for
the next major.

Aspirational goals may be developed against v2 or v1 as required.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — Plain forms draw as daisyUI

*delivered in [#5](https://github.com/django-mvp/django-mvp-forms/issues/5), [#6](https://github.com/django-mvp/django-mvp-forms/issues/6), [#26](https://github.com/django-mvp/django-mvp-forms/issues/26) · advances G1, G3, G6*

A host project that selects the template pack gets every form drawn as daisyUI markup, whether it uses the crispy filter or the crispy tag, and without writing a layout. This comes first because every later item draws its fields through it.

**Deliverables:**

- Every widget Django ships draws as the matching daisyUI input: text and its variants, textarea, select and multiple select, checkbox, radio and checkbox groups, file, date and time, and hidden inputs
- Labels, required markers and help text for each field
- Field errors and form-wide errors, each tied to the input or form it belongs to so assistive technology announces them
- Disabled and read-only states
- The result works on a page that loads daisyUI's full CDN build, with no build step in the host project
- A demo page showing each widget in each state, and the README's installation and quickstart sections

Serves G1, G3 and G6. Layout objects, formsets and per-field styling choices are later items. A host project with its own Tailwind build works out that configuration itself.

### R2 — Core layout objects

*delivered in [#7](https://github.com/django-mvp/django-mvp-forms/issues/7), [#8](https://github.com/django-mvp/django-mvp-forms/issues/8) · advances G2, G3*

A form with a layout can arrange its fields using the layout objects django-crispy-forms provides for structure and buttons. Depends on R1 for the fields inside them.

**Deliverables:**

- Fieldsets, divs, rows and columns
- Submit, reset, plain and hidden buttons, button holders and form actions
- Inline checkboxes and inline radios
- Fields with buttons, and prepended and appended text
- Uneditable fields, inline fields and multi-widget fields
- Raw HTML placed in a layout
- A demo page for each, and the README's public surface listing them

Serves G2 and G3. Tabs, accordion, modal and alert are R3.

### R3 — Container layout objects

*delivered in [#9](https://github.com/django-mvp/django-mvp-forms/issues/9) · advances G2*

The layout objects that group parts of a form behind an interaction or a notice, drawn with daisyUI's own components. Depends on R1, and is separate from R2 because each of these carries behaviour as well as markup.

**Deliverables:**

- Tabs, including opening on the tab that holds the first error
- Accordion and its groups, with the same handling of errors
- Modal
- Alert, dismissible or not
- A demo page for each

Serves G2. With R2 this covers every layout object django-crispy-forms ships.

### R4 — Formsets

*delivered in [#10](https://github.com/django-mvp/django-mvp-forms/issues/10) · advances G1*

A formset handed to the pack draws as a set of forms, either stacked or as a table with one form per row. Depends on R1.

**Deliverables:**

- Stacked and table layouts for a formset
- The management form, and formset-wide errors
- Per-form errors shown beside the row they belong to
- Delete and ordering inputs drawn consistently with the rest of the pack
- A demo page for each layout

Serves G1. Adding and removing rows in the browser, and the views around a formset, belong to django-mvp and are out of scope.

### R5 — Variants, colours and sizes from Python

*delivered in [#11](https://github.com/django-mvp/django-mvp-forms/issues/11), [#12](https://github.com/django-mvp/django-mvp-forms/issues/12) · advances G4*

A developer chooses how a form's inputs look from Python, once for a whole form and again for any single field. It comes last among the Essential items so it can cover every input and layout object the earlier items introduce.

**Deliverables:**

- A size, colour and variant for all inputs in a form, set in one place
- The same three choices for a single field, overriding the form's
- A boolean field drawn as a checkbox, a toggle or a switch, chosen per field
- The same choices for buttons
- A demo page showing the combinations

Serves G4. daisyUI's other form components, such as rating and range, are R7.

## Expected goals: v1.0.0

Everything a complete, dependable release is expected to have.

### R6 — Replacing one template

*resolve · advances G8*

A host project can replace any single template in the pack and keep the rest. The template paths become a documented, stable part of the public surface.

### R7 — daisyUI's other form components

*feature · advances G9*

Rating, range, floating labels and joined inputs can be placed from a layout, with the same size, colour and variant choices R5 provides.

### R8 — Every daisyUI theme

*feature · advances G5*

Each form state stays legible under every theme daisyUI ships, light and dark, with nothing for the host project to adjust per theme.

### R9 — A stated support window

*resolve · advances G7*

The package states which versions of Django, django-crispy-forms and daisyUI it supports, tests against all of them, and says how soon a new release of each is picked up.

## Aspirational goals

Fields, widgets and support for third-party packages' widgets are added when a project needs one. They carry no roadmap items, so G11 and G12 have none here.
