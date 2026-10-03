# Goals

These are the standing directions `django-mvp-forms` works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the package incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | Any Django form or formset draws as correct daisyUI markup with no per-form work | Essential | | |
| G2 | Every layout object django-crispy-forms ships can be used, including tabs, accordion, modal, alert and prepended or appended text | Essential | | |
| G3 | Labels, help text and errors are tied to their inputs the way current Django expects, so forms work with assistive technology | Essential | | |
| G4 | The variant, colour and size of any form component can be set from Python, per form and per field, including toggles and switches | Essential | | |
| G5 | Forms follow whichever daisyUI theme the host project uses, with no per-theme work | Expected | | |
| G6 | The pack works in any daisyUI project, with or without django-mvp | Expected | | |
| G7 | The package keeps pace with current Django, django-crispy-forms and daisyUI releases | Expected | | |
| G8 | A host project can replace one template without forking the pack | Expected | | |
| G9 | daisyUI's other form components, such as rating, range, floating label and joined inputs, are reachable from a layout | Expected | | |
| G10 | A project moving from another crispy pack keeps its layout code, within reason | Expected | | |
| G11 | Shared fields and widgets look native beside the pack's own inputs | Aspirational | | |
| G12 | Fields and widgets from popular third-party Django packages draw well in the pack, where the maintainers judge the package worth supporting | Aspirational | | |

_Written 2026-10-03. Revise as the goals change._
