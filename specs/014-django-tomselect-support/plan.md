# Implementation Plan: django-tomselect support

**Branch**: `014-django-tomselect-support` · **Spec**: [spec.md](spec.md) · **Research**:
[research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

The screens the maintainer approved are on this branch: the stylesheet, a grouping template and
the demo pages. They arrived with no tests. The build keeps what he approved on screen and puts
the tests, the documentation and the amended checks behind it, story by story. No Python under
`mvp_forms/` changes: the pack already writes the right classes on a django-tomselect select
(research R1).

What the feature distributes:

- `mvp_forms/static/mvp_forms/tomselect.css`
- `mvp_forms/templates/django_tomselect/tomselect.html`

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7, daisyUI 5.
- django-tomselect 2026.6.2 in the `dev` dependency group only. Nothing under `mvp_forms/` imports
  it.
- Tests are pytest under `tests/`, rendered in Python, with no browser (research R7).
- `uv run pre-commit run --all-files` is the lint gate. `uv run pytest -n auto` is the suite.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, testing | Every task writes its tests first. For a rule that already exists in the stylesheet, "first" means the test is seen to fail with the rule taken out, then pass with it back. |
| II and III, simplicity | No Python is added to the package. The stylesheet is one file. Grouping is fifteen lines of template. |
| VI, documentation | Each story documents its own surface in the README in the same task. |
| VII, dependencies | django-tomselect is a development dependency. A test holds that no module imports it. |
| XII, scope | No view, URL, field or widget class in the package. The demo's autocomplete views are the demo's. |
| XIII, plain templates | The grouping template is plain Django. It extends django-tomselect's template, which the checks under this article are narrowed to allow for a supported package's directory and for nothing else. |
| XIV, stock daisyUI | Amended in its own pull request before this merges (research R10). The pack's own templates still define no class. |
| XV, fields and widgets arrive when needed | No roadmap item. The README's public surface gains the section. |

## The stylesheet

Kept as the sketch has it. The tests hold its structure, not its taste:

- **Scope (FR-003).** Every selector, after `:root`, starts at `.ts-wrapper`, `.ts-dropdown` or
  `div.ts-dropdown`, or is one of three named exceptions: the status element, `.modal-box:has(…)`
  and `.overflow-x-auto:has(…)`. The test reads the file, splits it into rules and checks each
  selector. An exception is matched whole, so a new rule outside a control fails.
- **No colour of its own (FR-004).** No hex colour, no `rgb(`, `hsl(`, `oklch(`, `oklab(` and no
  named colour other than `transparent` and `currentColor` in any declaration. Colours appear only
  as `var(--color-…)`, alone or inside `color-mix`. The test covers colour only.
- **Legibility (FR-014).** A named table of ink and surface: for each, the selector, the
  declaration or opacity that makes the ink, and the surface it sits on. The test reads each from
  the file, resolves `var(--color-…)`, `color-mix(in oklab, …)` and opacity with
  `tests/legibility`, and holds the contrast to FS-012's standard under `light` and `dark`. Held:
  a tag, its remove button, the tag the keyboard is on and its remove button, an option, the
  active option, a chosen option, a group heading, the lines that cannot be chosen, the clear
  button and the loading ring. The placeholder is daisyUI's own pairing and counts as the
  exception FS-012 already lists. The disabled wrapper, the disabled tag and the disabled option
  are measured and not held, as FS-012 does for a disabled field.
- **No table of states.** Whether each state the specification lists has a drawing is not held by
  a test: a test that a selector exists could only fail when someone removes the rule on purpose.
  Those states are shown on the demo page and walked by the maintainer. The legibility test fails
  if a rule it reads a colour from disappears.

One class in one module directly under `tests/`, beside `template_surface.py`, reads the
stylesheet into rules and answers for a selector's declarations. The scope, colour and legibility
tests all use it. There is no second helper.

## The pack's markup

No production change. `tests/test_pack/test_tomselect.py` draws forms with each of the four
widgets through `{{ form|crispy }}` and `{% crispy form %}` and holds: the `select` class, each
size, each colour, the variant, `select-error` with no colour on a field in error, the `disabled`
attribute, the label's `for`, `aria-describedby` naming the help text and the errors, and the same
markup on a second draw. Model-backed widgets use an autocomplete view over `django.contrib.auth`'s `Group`, registered in
`tests/urls.py`, and are drawn with a current request, through the client, because
django-tomselect draws a different template without one. `aria-describedby` is asserted only on
a field that has help text or errors. No drawn form names `tomselect.css` (FR-002).

`tests/test_pack/test_independence.py` gains django-tomselect to the modules no package module may
import. The fixture that leaves only the pack and crispy installed already shows the pack draws
without it.

## Grouping

`mvp_forms/templates/django_tomselect/tomselect.html`, as sketched (research R4). Tests draw a
widget and read the script it writes: `optgroupField` and `optionGroupRegister` are present, and
with `mvp_forms` listed after `django_tomselect` they are absent and the widget still draws.

The three checks that name every distributed template are narrowed:

- `test_every_template_named_by_a_template_is_the_packs_own` reads templates under `daisyui/`. A
  second test holds that a template under `django_tomselect/` names only django-tomselect's
  template of the same path. The README's two tables together are still compared with every
  `*.html` under `mvp_forms/templates/`, so a template anywhere else fails.
- The README's template list gains a second, short table for a supported package's templates, and
  `tests/template_surface.py` reads it. The row says what it draws, that it is found through
  application directories, and the order `INSTALLED_APPS` needs.
- `test_replacements.py` draws its marker copies for `daisyui/` templates. The grouping template
  gets one test of its own: a project template at the same path that extends it still groups.
- `test_the_package_has_no_static_directory` becomes a test that the package's static directory
  holds `mvp_forms/tomselect.css` and nothing else.

## The demo

The sketch's pages, forms, views, routes, menu group and settings are kept. `demo/tomselect_forms.py`
and `demo/tomselect_views.py` stay as modules of their own. `tests/test_demo.py` gains a class for
the page: it responds inside the shell and standalone, the sidebar lists it under a group apart
from the standard pages, each section is present, the form posts and shows what it cleaned to, a
post with no country comes back in error, the fetched form responds, and every page of the demo
links `tomselect.css`.

## Documentation

- README, under "Public surface": a section "django-tomselect" covering what to install and load
  and in what order, `INSTALLED_APPS` order, the one look supported, sizes, colours and variant,
  tagging, grouping with the `optgroup` key, htmx and `use_htmx`, modal and table, the two plugins
  covered, what is not supported, the release tested and the Django 6.1 note. The "Scope &
  philosophy" and "Installation" sentences that say the package ships no stylesheet are brought
  into line. The demo section lists the new pages.
- CHANGELOG, under Unreleased. CONTEXT gains "Tagging", "Option group" and "Supported package".
- Decision records at convergence: the optional stylesheet per supported package; legibility under
  `light` and `dark`; grouping through a template that extends django-tomselect's. ADR 0003, 0029
  and 0034 are pointed at the first where it changes what they rest on.

## Story order

US1 → US2 → US3 → US4, sequential, in the feature worktree. US1 carries the amended checks, so the
suite is green again at its end.

## What this plan does not do

- No browser in the suite or in CI.
- No change to django-tomselect's scripts or behaviour (research R9).
- No support for the token widget, the Bootstrap looks, or a plugin beyond the clear and remove
  buttons.
- No amendment to the constitution on this branch (research R10).
