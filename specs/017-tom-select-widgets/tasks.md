# Tasks — 017 Tom Select widgets for choice fields

**Branch**: `017-tom-select-widgets` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I: the tests are written, seen to
fail, and seen to pass. A task is done when its tests pass, the tree is green and the work is
committed. Documentation lands in the task that introduces what it describes.

No test asserts wording, a colour, a size in pixels or a class used only for looks. A widget test
asserts the attribute's JSON, the media and what the field receives. A browser test asserts what
this package's script does and never Tom Select's own behaviour beyond what shows the settings
arrived. Where a task's behaviour already holds once an earlier task is built, its tests are
proved by breaking the code they depend on and seeing them fail, and the report says how.

Code standards for every task: no leading-underscore names; line length 88; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. `mvp_forms/widgets.py` imports Django and the standard
library only, and no module of the package imports django-tomselect. Nothing under `.github/`
changes. A document reads as current state. README links are absolute. Every `ValueError` names
the argument at fault.

## Decision records

Written at convergence, after the last story, with numbers read from `origin/main` at that
moment. No task writes one. `CONSTITUTION.md` does not change on this branch.

## Order

**US1 → US2 → US3 → US4 → US5 → US6, sequential, in the feature worktree.**

---

## US1 — A developer gives a multiple choice field a Tom Select control (P1)

Issue: #172. Delivers FR-001 to FR-005, FR-012 to FR-018, FR-020, FR-021, FR-023 to FR-033 for
the multiple widget; SC-001, SC-003, SC-005, SC-006, SC-008.

### T001 — The multiple widget

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_tom_select_widgets.py` (new),
`tests/forms.py`, `mvp_forms/widgets.py`

Plan, *The widgets*; research R1.

- `TomSelectMultiple` is a `SelectMultiple` that draws every choice of its field as an option
  and carries `data-tom-select` holding `{}`.
- Its media names `mvp_forms/tomselect.js` and no stylesheet.
- A developer's `attrs` are kept, and a subclass is drawn as its parent is.
- It takes no settings yet. Those are T005's.
- Drawn through `|crispy`, `{% crispy %}`, `|as_crispy_field` and Django's own rendering, the
  attribute is the same. Through the pack the select carries `select` and `w-full`, a stated
  size, colour and variant, `select-error` on a field in error and `disabled` on a disabled
  field, and its label, help text and errors are tied to it as for a stock select.
- A `MultipleChoiceField`, a `TypedMultipleChoiceField` and a `ModelMultipleChoiceField` using
  it clean submitted values to what they clean from `SelectMultiple`, show initial and submitted
  values as selected options, and reject a value not among the choices.
- A form that uses none of these widgets is drawn with the markup it had, and its media names no
  script.

### T002 — The script, tested in Chrome

**Files**: `tests/test_tomselect_e2e.py` (new), `tests/urls.py`, `tests/templates/tests/`,
`tests/data/tom-select-2.5.2.complete.min.js` (new; the complete build of Tom Select 2.5.2 as npm publishes it),
`mvp_forms/static/mvp_forms/tomselect.js` (new), the test that lists the package's static files

Plan, *The script*; research R3, R4, R6. ADR 0046 for how the tests are built.

- On a page that loads Tom Select and the form's media, each select the widget drew has a
  control once the document has loaded, and no request was made for options.
- A field with more than 50 choices offers every one of them when a person types a letter they
  all share.
- Picking two options and submitting sends both values under the field's name.
- Initial values are held by the control when it starts.
- The control of a disabled field is disabled.
- Activating the field's label moves focus into the control.
- On a field with help text, the element that takes focus names the help text's id in
  `aria-describedby`.
- An option whose label holds markup is shown as text, in the dropdown and once chosen.
- A stock select on the page, and a select drawn by a django-tomselect widget, get nothing from
  this script.
- On a page that loads django-tomselect's script and no other copy of Tom Select, the control
  starts.
- On a page with no Tom Select, nothing is started, no error is raised and the form submits the
  values chosen in the stock select.
- Under a policy of `script-src 'self'` and the origin serving Tom Select, the control starts.
- The script tag present several times starts one control for each select.
- A select Tom Select refuses is left as it is and the next one is still started.
- The observer is T007's and the event is T008's.

### T003 — The documents and the demo page

**Files**: `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `mvp_forms/static/mvp_forms/tomselect.css` (its opening comment only), `mvp_forms/widgets.py` (its module docstring only), `demo/` (forms, views,
urls, menus, two templates), `tests/test_demo.py`, the README's example and surface tests

Plan, *The demo* and *Documents*; research R7.

- README gains "Tom Select widgets": what the widgets are for, what the host project loads and
  in which order with and without django-tomselect, the major version of Tom Select and the
  release tested, the attribute, which holds `placeholder`, `maxItems` and `plugins`, and the script as public
  surface, that the two button settings need Tom Select's complete build or django-tomselect's
  script, what a page without Tom Select
  or without `mvp_forms/tomselect.css` does, which lists the widgets suit and when to use
  django-tomselect, that a formset row is added from an empty form kept in a `<template>` element, since an empty
  form drawn into the page is itself started, and never by copying a started row, and what is not supported. `TomSelectMultiple` joins the public surface.
- The django-tomselect section describes `mvp_forms/tomselect.css` as drawing Tom Select
  controls, from django-tomselect or from this package's widgets.
- The comment at the head of `mvp_forms/tomselect.css` and the module docstring of
  `mvp_forms/widgets.py` read true beside the new widgets. No rule of the stylesheet changes.
- CONTEXT.md gains "Tom Select control", "Options that come with the form", "Chosen value" and
  "Form's media",
  and "Option group" covers a group written as Django's grouped choices.
- CHANGELOG, under Unreleased, Added.
- The demo page exists in both forms with the multiple widget: a form that submits and shows
  what it cleaned to, the control at each size, in a colour, in error and disabled, and, on the
  shell page, beside a django-tomselect control and a stock multiple select. Both pages answer
  200 and hold the widget's select.

---

## US2 — A developer gives a single choice field the same control (P1)

Issue: #173. Delivers FR-001 to FR-005, FR-015, FR-023, FR-024 for the single widget.

### T004 — The single widget

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_tom_select_widgets.py`,
`tests/test_tomselect_e2e.py`, `tests/forms.py`, `tests/urls.py`, `mvp_forms/widgets.py`,
`README.md`, `CHANGELOG.md`, `demo/`

- `TomSelect` is a `Select` with the same attribute and media, drawn through the pack as T001
  says of the multiple widget.
- A `ChoiceField`, a `TypedChoiceField` and a `ModelChoiceField` using it clean to what they
  clean from `Select`.
- In Chrome: picking an option submits that one value, picking another replaces it, and an
  optional field with an empty choice can be returned to no value from the keyboard and then
  submits empty.
- What the two widgets share lives in one place in `mvp_forms/widgets.py`.
- README names `TomSelect` in the section and the public surface. The demo page shows it beside
  the multiple one in each section T003 built.

---

## US3 — A developer sets the control's options from Python (P2)

Issue: #174. Delivers FR-006 to FR-010, FR-028.

### T005 — The four settings

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_tom_select_widgets.py`,
`tests/test_tomselect_e2e.py`, `mvp_forms/widgets.py`, `README.md`, `CHANGELOG.md`, `demo/`

Plan, *The widgets*.

- `placeholder` and `clear_button` on both widgets, `remove_button` and `max_items` on the
  multiple one, keyword-only, written under Tom Select's names as the plan says. A setting not
  stated is not written.
- A lazy translation as a placeholder is accepted and is written in the language active when
  the widget is drawn: the test draws it under `translation.override`.
- Refused with a `ValueError` naming the argument: a placeholder that is not text or is empty, a
  button setting that is not `True` or `False`, a `max_items` that is a boolean, not a whole
  number, or below one. The README says that `max_items=1` makes Tom Select draw the control as
  a single one while the form still receives a list. `TomSelect` given `remove_button` or `max_items` raises `TypeError`.
- The settings are the same in every way of drawing the form, and in a formset's empty form.
- In Chrome: the placeholder is the control's placeholder while it is empty, the clear button
  empties a control holding values, a remove button removes its own value alone, and with
  `max_items=2` a third option cannot be chosen until one is removed.
- README documents each setting with an example. The demo page gains a section for them.

---

## US4 — A developer groups options and marks some unavailable (P2)

Issue: #175. Delivers FR-011, FR-014.

### T006 — Groups and unavailable options

**Files**: `tests/test_tomselect_e2e.py`, `tests/forms.py`, `tests/urls.py`, `README.md`, `demo/`

Research R3. Expected to need no change to the package's code. The tests are proved as the
header says, and the report states what was broken to see each fail.

- In Chrome, two tests, each of which fails if the select stops reaching Tom Select intact: a
  field with grouped choices lists an option under its group's heading, and an option drawn
  with `disabled` by a subclass cannot be chosen. Groups, search and escaping are Tom Select's
  own and get no further test.
- README says how groups are written and how a subclass marks an option unavailable. The demo
  page gains a section with both.

---

## US5 — A developer uses the control in a formset, a modal and content loaded later (P2)

Issue: #176. Delivers FR-019, FR-031.

### T007 — Controls on selects added later

**Files**: `tests/test_tomselect_e2e.py`, `tests/urls.py`, `tests/templates/tests/`,
`mvp_forms/static/mvp_forms/tomselect.js`, `README.md`, `demo/`

Plan, *The script*; research R5.

- In Chrome: a select of one of the widgets inserted after the page has loaded gets a control,
  whether it is inserted on its own or inside another element.
- A row made from a formset's empty form kept in a `<template>`, with `__prefix__` replaced,
  holds one working control with the field's options and settings, and a value chosen in it is
  submitted under the new row's name.
- A select moved to another place in the page keeps its one control.
- With the script tag on the page several times, a row added later still has one control.
- A control inside a `Modal` is started while the modal is closed and works when it is opened.
- The select inside a `<template>` is not started.
- The demo page gains a formset whose rows are added from its empty form, and a modal holding a
  control.

---

## US6 — A developer changes something that needs JavaScript (P3)

Issue: #177. Delivers FR-022, FR-030.

### T008 — The event

**Files**: `tests/test_tomselect_e2e.py`, `mvp_forms/static/mvp_forms/tomselect.js`, `README.md`,
`CHANGELOG.md`

- In Chrome: `mvp-forms:tomselect` is sent from each select once its control has started,
  reaches a listener on the document, and `event.detail.tomselect` is the Tom Select instance of
  that select.
- It is sent once for each select, and from a select added later.
- A listener that calls a method of the instance changes the control.
- README documents the event with an example, and it joins the public surface.

---

## After the code review

The review approved the branch with one medium and five low findings. These tasks close the ones
worth closing before the merge.

### T009 — A test that the script passes only the three settings (US5, finding COR-001)

**Files**: `tests/test_tomselect_e2e.py`

- In Chrome: a select added with `data-tom-select` holding `{"create": true, "placeholder":
  "Pick later"}` gets a control whose settings do not have `create` on, and whose placeholder
  arrived. The test fails when the script copies every key of the attribute into the settings.

### T010 — One way to choose an option in the browser tests (US1, findings COR-002 and COR-004)

**Files**: `tests/test_tomselect_e2e.py`, `tests/test_demo.py`

- The helper `pick`, which presses Enter before Tom Select has filtered its list, is removed. Its
  three users call `choose`, which clicks the option by its value.
- The demo test that accepts any integrity value starting `sha384-` for the stylesheet no longer
  asserts on the value. The value on the page was checked by hand against the file the CDN serves.

### T011 — A tab and an accordion group on the demo page, and three small corrections (US5, finding COR-003)

**Files**: `demo/`, `tests/test_demo.py`, `mvp_forms/static/mvp_forms/tomselect.js` (one comment),
`specs/017-tom-select-widgets/plan.md`, `specs/017-tom-select-widgets/spec.md`

- The demo's "In a modal" section becomes "In a modal, a tab and an accordion", with one control
  in a `TabHolder` and one in an `Accordion` beside the modal, on both pages.
- The comment about every option being offered sits on the `maxOptions` line.
- `plan.md` shows `TomSelectMultiple(TomSelect, forms.SelectMultiple)`, as built. `spec.md` reads
  `Status: Approved`.
