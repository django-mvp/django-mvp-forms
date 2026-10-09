# Tasks — 014 django-tomselect support

**Branch**: `014-django-tomselect-support` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. The stylesheet, the grouping
template and the demo pages are already on the branch from the approved sketch, so for a rule
that exists the test is written, seen to fail with the rule taken out, and seen to pass with it
back. A task is done when its tests pass, the tree is green and the work is committed.
Documentation lands in the task that introduces what it describes.

`tomselect.css` and the grouping template appear under a task's files for the red step only.
What the maintainer approved on screen is not changed: no value in `tomselect.css`, no markup and
no wording on the demo pages. A test that cannot pass without changing one is reported, not made
to pass.

No test asserts a measurement, a colour value or wording. A stylesheet test asserts that a rule
exists and where it applies. A markup test asserts classes, attributes and ids.

Code standards for every task: no leading-underscore names; line length 88; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. Nothing under `mvp_forms/` imports django-tomselect.
`CONSTITUTION.md` and everything under `.github/` do not change. A document reads as current
state. README links are absolute.

## Decision records

Written at convergence, after the last story, with numbers read from `origin/main` at that
moment. No task writes one.

## Order

**US1 → US2 → US3 → US4, sequential, in the feature worktree.**

---

## US1 — A developer draws a django-tomselect field in a daisyUI form (P1)

Issue: #140. Delivers FR-001 to FR-015, FR-028 to FR-032; SC-001 to SC-004.

### T001 — The stylesheet is distributed, scoped and names no colour, and the suite is green again

**Files**: `tests/test_pack/test_tomselect_stylesheet.py` (new),
`tests/test_pack/test_independence.py`, `tests/test_pack/test_replacements.py`,
`tests/test_pack/test_template_list.py`, `tests/template_surface.py`, `README.md` (the templates
tables only), `mvp_forms/static/mvp_forms/tomselect.css`

Plan, *The stylesheet* (scope, no colour), *Grouping* (the checks narrowed); research R2 to R4.

The branch starts with four failing tests, each a check the sketch's two new files run into:
the package has no static directory, every template a template names is the pack's own, the
README's list matches the package, and every template can be replaced. This task narrows each
as the plan says, so the suite is green at its end and stays green.

- The three checks that name every distributed template read the pack's own directory,
  `daisyui/`. A second test holds that a template under `django_tomselect/` names only
  django-tomselect's template of the same path. The README gains the second table with the
  grouping template's row, and `tests/template_surface.py` reads it. The two tables together
  are compared with every `*.html` under `mvp_forms/templates/`, so a template outside
  `daisyui/` and other than `django_tomselect/tomselect.html` fails: adding an empty
  `mvp_forms/templates/other/x.html` must turn the suite red. The marker-copy test draws
  `daisyui/` templates. What the grouping template does is tested in T006.

- One class in one module directly under `tests/`, beside `template_surface.py`, that reads the
  stylesheet into rules: selectors and declarations, with comments and `@keyframes` handled. T003
  adds a method to it. There is no second helper.
- Scope: every selector is inside a control or is one of the three named exceptions.
- No colour of its own, in any declaration.
- The package's static directory holds `mvp_forms/tomselect.css` and nothing else, in place of
  the test that it has none.
- django-tomselect joins the modules no package module may import.

### T002 — The pack's markup on the four widgets

**Files**: `tests/test_pack/test_tomselect.py` (new), `tests/forms.py`, `tests/urls.py`

Plan, *The pack's markup*; research R1.

- Single and multiple, model-backed and plain choices, each through the filter and the tag.
- Class, each size, each colour, the variant, error with no colour, disabled, label, and the
  same markup on a second draw with the widget's `attrs` the same before and after.
  `aria-describedby` is asserted only on a field that has help text or errors. No drawn form
  names `tomselect.css`.
- Model-backed widgets are drawn with a current request, through the client: django-tomselect
  draws a different template without one. The model is `django.contrib.auth`'s `Group`.
- A page drawn with no django-tomselect field is byte for byte what it was (the existing suite
  already holds this: confirm and name the tests in the report, add none).
- No production change is expected. If one is needed, stop and report why.

### T003 — Legibility under light and dark

**Files**: `tests/test_pack/test_tomselect_stylesheet.py`, the stylesheet reader under `tests/`

Plan, *The stylesheet* (legibility, no table of states); spec FR-014.

- A named table of ink and surface for what the first story draws: an option, the active option,
  a chosen option, the lines that cannot be chosen, the clear button and the loading ring. Each
  is read from the file and held to FS-012's standard under `light` and `dark`.
- The placeholder is asserted to be daisyUI's own pairing and is not held. The disabled wrapper
  and the disabled option are measured and not held.
- No test that a state has a rule.

### T004 — The demo page, and the documentation of the first story

**Files**: `tests/test_demo.py`, `demo/` as sketched, `README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *The demo*, *Documentation*; spec FR-029 to FR-031.

- The page inside the shell and standalone, the sidebar group, each section, a post that cleans
  and a post in error.
- README: the "django-tomselect" section as far as the first story goes (install, load, order,
  the look, sizes, colours, variant, states, the two plugins, what is not supported, the release
  tested, and that on Django 6.1 the `tomselect_media` tag writes no links, so the files are
  loaded through form media or by path, and that without `tomselect.css` daisyUI cuts the
  dropdown off), the sentences about shipping no stylesheet, the demo's pages. CHANGELOG.
  CONTEXT: "Supported package".

---

## US2 — A developer offers tagging (P2)

Issue: #141. Delivers FR-016 to FR-019; FR-028, FR-030, FR-031.

### T005 — Tags and the offer to add a value

**Files**: `tests/test_pack/test_tomselect_stylesheet.py`, `tests/test_demo.py`, `README.md`,
`CONTEXT.md`

- The legibility table gains a tag, its remove button, the tag the keyboard is on and its remove
  button. The disabled tag is measured and not held.
- Demo: the tagging control posts a value that was not an option and the page shows it.
- README: tagging, that saving a new value is the developer's, and that the field must accept a
  value that is not among its choices, which django-tomselect's stock field does not. The demo's
  `TagsField` is shown as the example. CONTEXT: "Tagging".

---

## US3 — A developer groups the options in a dropdown (P2)

Issue: #142. Delivers FR-020 to FR-023; FR-030, FR-031; SC-005.

### T006 — The grouping template and the checks that name it

**Files**: `tests/test_pack/test_tomselect_grouping.py` (new),
`tests/test_pack/test_tomselect_stylesheet.py`, `tests/test_demo.py`,
`mvp_forms/templates/django_tomselect/tomselect.html`, `README.md`, `CONTEXT.md`

Plan, *Grouping*; research R4.

- The drawn widget's script names `optgroupField` and `optionGroupRegister`. With `mvp_forms`
  after `django_tomselect` it does not, and the widget draws.
- A project template at the same path that extends it still groups.
- The group heading joins the legibility table.
- At least one draw is made with a current request.
- Demo: the rocks endpoint answers with `optgroup` on grouped rocks and without on the two that
  have none.
- Check in the running demo whether a chosen option is listed under its group when
  `hide_selected=False`, and report what happens. Do not work around it.
- README: grouping, the `optgroup` key on both kinds of view, `INSTALLED_APPS` order. CONTEXT:
  "Option group".

---

## US4 — A developer puts the control in a modal, a table and a page htmx loads (P3)

Issue: #143. Delivers FR-024 to FR-027; FR-030, FR-031; SC-006.

### T007 — Modal, table and htmx

**Files**: `tests/test_demo.py`, `README.md`

- Demo: the modal form and the table formset are drawn with their controls, the fetched form
  responds and carries a prefix of its own, the second page responds, and the demo's settings
  set `use_htmx` by default.
- README: modal and table, htmx and the `use_htmx` default.

---

## Review fixes

### T008 — The stylesheet wins whichever stylesheet is loaded first (US1)

Review finding: three rules matched Tom Select's class for class and lost when its stylesheet
arrived after ours, as it does with a form's media. Every selector now starts `html:root`.

### T009 — The offer to add a value is set apart (US2)

Review finding: Tom Select lists the offer first, so the rule that drew a line above it could
never match. The line is now drawn beneath it.

### T010 — The README says what the stylesheet really does (US4)

Review findings: the classes are copied to the wrapper only; either load order works; a scrolled
modal or table loses its position while a dropdown in it is open.
