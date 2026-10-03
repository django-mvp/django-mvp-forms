# Implementation Plan: replace one template without forking the pack

**Branch**: `009-replace-one-template` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

A host project replaces one of the pack's templates by putting a file at the same path where
Django finds it first. That already works (research R1), so the pack's templates do not change.
The feature is three things around it:

1. tests that hold the behaviour in place for every distributed template, on both routes;
2. the list in the README, and a check that fails when the list and the package disagree;
3. a way for a later release to honour a replacement at a path the pack has moved away from,
   with a deprecation warning, so the promise can be kept the first time it is needed.

```django
{# templates/daisyui/required_marker.html, in the host project #}
{% load i18n %}{% if field.field.required %} <abbr title="{% translate "required" %}">*</abbr>{% endif %}
```

Every required field in the project now carries that marker, and every other template is still
the pack's.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; no leading-underscore names; line length
88; no compatibility aliases; no setting, registry or Python hook for replacing a template (D4);
nothing under `.github/` changes.

**Scale/Scope**: no pack template changes. One module and one template tag are added. One
README section, one test helper module, three test modules.

## Constitution Check

- **I, test-first**: every test is written before what it proves, or, where the behaviour is
  already there, proved by breaking it (see *Tests that pass on arrival*).
- **II and III, simplicity**: no setting and no registry of replacements. The deprecation module
  is one dictionary and one function, required by FR-013 and the specification's assumption that
  the behaviour exists before the first release that needs it.
- **VI, documentation**: the README section and the CHANGELOG entries land in the story that
  introduces what they describe.
- **VII, dependencies**: none added.
- **VIII, internationalisation**: the feature adds no text a person using a host project sees.
  A deprecation warning is read by a developer and is not translated, as Django's are not.
- **XI, compatibility**: this feature is the statement of what Article XI covers for templates.
- **XIII, independence**: nothing imports django-mvp or cotton.

## How a replacement is found

Research R1. Two routes, both Django's own:

| Route | Templates | A replacement is found in |
|---|---|---|
| `TEMPLATES` | everything outside `daisyui/widgets/` | a `DIRS` directory, or the `templates` directory of an app listed before `mvp_forms` |
| `FORM_RENDERER` | `daisyui/widgets/*` | with the default renderer, the `templates` directory of an app listed before `mvp_forms`; in a `DIRS` directory only when the renderer is `TemplatesSetting` |

The pack adds nothing to either.

## The test fixtures

In `tests/conftest.py`:

- `replace`: a fixture returning a context manager, `replace({path: source, …})`. It writes each
  source under a temporary directory, puts that directory first in `TEMPLATES[0]["DIRS"]`, sets
  `FORM_RENDERER` to `django.forms.renderers.TemplatesSetting` and adds `django.forms` to
  `INSTALLED_APPS`, through `override_settings`, and clears django-crispy-forms' template caches
  on the way in and on the way out (`clear_crispy_template_caches`, already there). Leaving the
  block takes the replacements away.
- `pack_source`: returns the source of a distributed template by its path.

`tests/host_app/` is a small app that exists only for the tests: an `__init__.py` and one
replacement, `templates/daisyui/widgets/select_date.html`. It is how the default renderer's
route is tested, by listing it before or after `mvp_forms` in `INSTALLED_APPS`. It is not in the
default `INSTALLED_APPS` of the suite.

## The first story's tests

`tests/test_pack/test_replacements.py`. The suite's states are `STATES` from
`tests/test_pack/test_independence.py`, imported and not copied.

- **Every template, a copy with a marker** (FR-001, FR-003, FR-005, FR-006; SC-001, SC-002).
  Parametrised over every template the package distributes, found on disk. With the template
  replaced by a marker followed by its own source, every state is drawn; with the marker taken
  out, each is the same string as with nothing replaced; and the marker was drawn in at least
  one state. Random ids are normalised before comparing (research R6). `layout/tab-link.html` is
  left out of the "was drawn" half and has a test of its own.
- **A state that reaches every template.** Where the first test shows a template no state
  reaches, a state is added to `STATES`.
- **One test per acceptance scenario** not already covered by the parametrised test: the frame
  (1), one layout object among others (2), a widget template through the renderer with the frame
  still the pack's (3), a template several pack templates include (4), the filter, the tag and a
  formset in both layouts (5), taken away again (7), and a form's own `template=`,
  `field_template` and helper `template` still winning (9).
- **Placement** (edge cases): an app listed after the pack is not used; a widget replacement in
  `DIRS` under the default renderer is not used; the same one in an app listed before the pack
  is; two replacements, one including the other, are both used; `tab-link.html` beside a
  `tab.html` that draws `links`; a template of the host project's own at a path the pack does
  not ship is drawn by a layout object that names it and changes nothing else; a widget subclass
  naming its own template is not drawn by a replacement of the pack's widget template; a
  replacement that leaves out the errors draws none and raises nothing.

Elements are found by an attribute the replacement writes, such as `data-replaced`, never by
wording.

**Nothing replaced draws as before** (FR-017, SC-007). No pack template changes, and the tag
library gains a tag nothing calls. It is verified once, at the end, by drawing every state at
the base commit and at the tip and comparing. Reported, not committed.

## The list

A section of the README's public surface, `### Replacing one template`. It holds, in order:

1. what a replacement is and that it needs nothing but the file;
2. where to put it, for each route, and the note on the five templates django-crispy-forms keeps
   in memory (research R4);
3. the worked example, a fenced `django` block under a `#### ` heading of its own;
4. the list: one markdown table, a row per template;
5. what happens when the pack changes a listed template (third story).

The table's columns are `Template`, `Draws`, `Handed` and `Found by`:

- `Template` is the path in backticks.
- `Draws` is a sentence.
- `Handed` is the names in backticks, separated by commas. A part of `drawn` or `table` is
  written with its dot, `drawn.is_group`. A template handed nothing has an empty cell.
- `Found by` is `` `TEMPLATES` `` or `` `FORM_RENDERER` ``.

Rows are grouped in the order a reader looks for them: the form, the field, layout objects,
formsets, widgets.

## The check

`tests/template_surface.py` is a helper module for the tests, holding what the check needs and
nothing that asserts:

- `distributed()`: the paths of every template under the package's `templates` directory.
- `names_read(source)`: the names a template reads from outside itself, as research R5 describes,
  by compiling it with the `django` engine and walking its nodes. Parts of `drawn` and `table`
  come back with their dot.
- `renderer_route()`: the paths on the form renderer route, as research R2 describes.
- `listed(readme)`: the table's rows, each with its path, its handed names and its route.
- `withdrawn_listed(readme)`: the rows of the table of paths on their way out, added in the
  third story.
- `disagreements(listed, distributed, reads, renderer_route, …)`: every way the list and the
  package differ, as a list of short tuples naming the kind and the path: a distributed
  template not listed, a listed path not distributed, a name read and not listed, a route
  listed wrongly.

`tests/test_pack/test_template_list.py`:

- the real list and the real package have no disagreements (US2 scenarios 1, 3, 6; SC-003);
- every row has something in `Draws` (scenario 2), asserted as non-empty and never by its words;
- given made-up inputs, each kind of disagreement is reported: a template added, one removed,
  one renamed, a name read that the row leaves out, the wrong route (scenario 5).

`names_read` has tests of its own in the same module, one per rule in research R5, on small
templates written in the test.

The check lives in the tests and not in the package: nothing in the issue needs the list at run
time (D6).

## The worked example

The README's example replaces `daisyui/required_marker.html`. A test in
`tests/test_pack/test_documented_examples.py` reads the fenced block from under its heading, as
`readme_example` already does for the others, puts it in place with `replace`, and draws a form
with a required field and an optional one. The required field's label holds the element the
example writes, the optional one's does not, and the pack's own marker element is not drawn.

## Changing a listed template later

Research R7. `mvp_forms/deprecation.py`:

```python
WITHDRAWN: dict[str, str | None] = {}


def host_template(path: str, get_template: Callable[[str], object]) -> str:
    """Return ``path`` when the host project has a template there, or ``""``."""
```

- `WITHDRAWN` maps a path the pack has moved away from to the path that replaces it, or to None
  when nothing does. It is empty in this release.
- `host_template` looks `path` up in `WITHDRAWN` (a path that is not there is a mistake in the
  pack and raises `KeyError`), then asks `get_template` for it. Found: it raises a
  `DeprecationWarning` naming the path and what replaces it, or saying that nothing does, and
  returns the path. `TemplateDoesNotExist`: it returns `""` and warns of nothing.
- `get_template` is the engine's or the renderer's own, so the question is asked of whichever
  would draw the template.

In `mvp_forms/templatetags/daisyui.py`, one tag:

```django
{% daisyui_host_template "daisyui/old.html" as old %}{% include old|default:"daisyui/new.html" %}
```

`daisyui_host_template` takes the context and calls `host_template` with
`context.template.engine.get_template`. A template the pack has stopped using is the same tag
with `{% if old %}{% include old %}{% endif %}`. `FieldInput` would call `host_template` with
`self.field.form.renderer.get_template`, at the release that moves a widget template.

No draw site uses the tag in this release, because nothing is withdrawn. A release that moves a
template adds its row to `WITHDRAWN`, changes the draw site, lists the old path in the README's
table of paths on their way out, and says what replaces it in the CHANGELOG. The decision record
written at convergence states that procedure.

Tests:

- `tests/test_deprecation.py`, mirroring the module: with a row put into `WITHDRAWN` for the
  test, a template at the old path is returned and warned about, with both paths in the
  warning; none there returns `""` and warns of nothing, with warnings turned into errors; a row
  whose value is None warns without naming a replacement path; a path that is not withdrawn
  raises `KeyError`.
- `tests/test_templatetags/test_daisyui.py`, a `TestHostTemplate` class: a template that draws
  through the tag draws the host project's template at the old path and warns (US3 scenario 2),
  draws the new one with no warning when the host project has none (6), and draws nothing for a
  path with no replacement when the host project has none (3). One of them through the form
  renderer, in a widget template, so the engine asked is the renderer's.
- `tests/test_pack/test_template_list.py`: a path in `WITHDRAWN` must be in the README's table of
  paths on their way out with the same replacement, a path in that table must be in `WITHDRAWN`,
  and a withdrawn path does not count as "listed but not distributed". With made-up inputs.

FR-014, a renamed name, has no mechanism (research R7) and so no test. FR-012, FR-015 and FR-016
are rules for later releases; the decision record and the README state them.

## Tests that pass on arrival

The first story's tests pass as soon as they are written, because Django already does this. Each
is proved by breaking what it guards and seeing it fail: for the parametrised test, by a
replacement that leaves a name out or a draw site that names a template some other way. The
probes are reported, not committed.

## The README, the CHANGELOG and the glossary

- README: the section described under *The list*. The existing sentence in *Template pack
  `daisyui`* about the form renderer points at it.
- CHANGELOG, under Added: a host project can replace one template, the list, and that the paths
  and the names are public from this release (FR-019). Under the same entry, what happens when
  one changes.
- `CONTEXT.md`: **Replacement** and **Template list**, from the specification's key entities.

## Decision records

Written at convergence, numbered from `origin/main` at that moment. One is expected: the
template surface, covering D2, D3 and D5, and naming the two routes (D4).

## Story order

**US1 → US2 → US3, sequential, in the feature worktree.** US2's check is extended by US3, and
all three touch `tests/conftest.py` or the README.

## What stays out

Research R8.
