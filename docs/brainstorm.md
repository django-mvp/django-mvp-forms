# Brainstorm notes

Working notes from before the package was created. These are not decisions. Anything here that hardens into one gets a record in `docs/adr/`.

## Prior art (surveyed October 2026)

| Package | What it is | State |
|---|---|---|
| [crispy-tailwind](https://github.com/django-crispy-forms/crispy-tailwind) | The official Tailwind pack for django-crispy-forms | Last release 1.0.3 in February 2024, last commit March 2025, 29 open issues and pull requests. Emits Tailwind utility classes, not daisyUI components. django-mvp depends on it today |
| [crispy-daisyui](https://github.com/fabge/crispy-daisyui) | A daisyUI pack, forked from crispy-tailwind | Release 0.13.0 in February 2026 and commits since, no open issues. One maintainer, no test suite, and described by its author as "modified just enough to suit my needs" |
| [crispy-bootstrap5](https://github.com/django-crispy-forms/crispy-bootstrap5) | The official Bootstrap 5 pack | Actively released. The reference for what a complete pack covers |

No other daisyUI pack for django-crispy-forms turned up on PyPI or GitHub.

## Why build another

The overlap with crispy-daisyui is real: both are daisyUI template packs for the same library. The case for a separate one:

- django-mvp's form rendering is part of every page it serves, so the pack under it has to be maintained on django-mvp's schedule and tested against the versions it supports. Neither existing pack offers that. crispy-tailwind is stalled, and crispy-daisyui is one person's working copy with no tests.
- The aim is a complete pack, covering every crispy-forms layout object, where crispy-daisyui covers the common form elements.
- The package also needs a home for form fields and widgets shared across django-mvp projects, which a pack-only package would not give.

## Shape agreed so far

- django-mvp depends on this package, not the other way round. The pack needs only Django and django-crispy-forms.
- Pack templates are plain Django templates with no django-cotton or daisy-cotton dependency.
- Scope is rendering and inputs: the pack, its layout objects, fields and widgets. Form views, formsets and page templates stay in django-mvp.
- Fields and widgets are added as projects need them and carry no roadmap items.
