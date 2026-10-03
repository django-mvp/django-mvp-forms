# Tasks — 006 Formsets drawn stacked or as a table

**Branch**: `006-formsets` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a name lands in the task that
introduces it.

No test asserts wording, width, spacing, alignment or which utility is used. Elements are found
by id, by name, by role and by element type. A class is asserted only where it is a daisyUI
component a host project depends on (`table`, `checkbox`, `input`), which the testing standard
counts as behaviour for a published pack ("Markup that consumers depend on").

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, fixtures); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell pages only.
Every `ValidationError` is raised with a `code`. Nothing under `.github/` is touched.

## Order

**US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A formset draws stacked with no per-form work (P1)

Issue: #31. Delivers FR-001, FR-002, FR-004, FR-005, FR-006, FR-009, FR-016, FR-017, FR-018;
SC-001, SC-003, SC-008. Also carries FR-021, which the specification lists under US5, because
the glossary changes in the story that first uses the word.

### T001 — The stacked layout

**Files**: `mvp_forms/templates/daisyui/whole_uni_formset.html`,
`mvp_forms/templates/daisyui/uni_formset.html`, `tests/forms.py`, `tests/conftest.py`,
`tests/test_pack/test_formsets.py`, `tests/test_pack/test_independence.py`

Plan, *The templates*, *Tests*; research R1, R3, R4, R8.

- The two templates as the plan's table has them, without the formset-wide errors include, which
  US3 adds.
- `tests/forms.py` gains a small line form (a required text field with help text, an optional
  number field, a hidden field), plain formsets of it, a model formset and an inline formset built
  from `django.contrib.auth` and `django.contrib.contenttypes` models (research R4), and a helper
  for a formset. `tests/conftest.py` gains a fixture that reads every named input out of drawn
  markup as post data, so a drawn formset can be bound again.
- Tests, `TestStackedFormset`, as the plan lists them (US1.1 – US1.7, the layout half of FR-006,
  media once, a helper button once).
- `test_independence.py`: a stacked formset state, unbound.

### T002 — The glossary, the README and the CHANGELOG for formsets

**Files**: `CONTEXT.md`, `README.md`, `CHANGELOG.md`

- `CONTEXT.md`: define **formset**, **stacked layout** and **table layout** as this package uses
  them; take formset out of "Terms deliberately not used", leaving form view there; keep the line
  between drawing a formset, which is this package's, and handling one (the view, saving, adding
  and removing rows in the browser), which is django-mvp's (FR-021).
- README: a "Formsets" part of the public surface: `{% crispy formset %}` and
  `{{ formset|crispy }}` draw a formset stacked; the helper is the formset's; what is drawn (the
  management form once, each form in a container of its own, hidden fields, one form element for
  the whole formset); a helper layout is applied to each form and draws only the fields it names,
  so `DELETE` and `ORDER` are named in it when wanted; the template paths
  `daisyui/whole_uni_formset.html` and `daisyui/uni_formset.html`; what the pack does not do (no
  empty form, no script, no view).
- CHANGELOG: one line under Unreleased, Added.

---

## US2 — The same formset draws as a table (P1)

Issue: #32. Delivers FR-002, FR-003, FR-004, FR-005, FR-007, FR-008, FR-009, FR-016, FR-017;
SC-001, SC-002, SC-003.

### T003 — `FormsetTable` and its tag

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/test_templatetags/test_daisyui.py`

Plan, *`FormsetTable` and the `daisyui_formset_table` tag*; research R6.

- The class and the tag as the plan has them, including `None` for a column whose field a form
  does not have.
- Tests, `TestFormsetTable`: columns are the first form's visible fields in order, with hidden
  fields left out; one row per form in order; each cell is that form's own bound field; a form
  missing a column's field has `None` in that cell and as many cells as there are columns; no
  forms gives no columns and no rows; a form with only hidden fields gives each row one empty
  cell.

### T004 — The table layout

**Files**: `mvp_forms/templates/daisyui/table_inline_formset.html`,
`tests/test_pack/test_formsets.py`, `tests/forms.py`, `tests/test_pack/test_independence.py`,
`README.md`, `CHANGELOG.md`

Plan, *The templates*, *Tests*; research R2, R5, R6.

- The template as the plan has it, without the formset-wide and row errors, which US3 adds.
- Tests, `TestTableFormset`, as the plan lists them (US2.1 – US2.6, FR-016, and the hidden
  fields and round trip on a plain, a model and an inline formset).
- `test_independence.py`: a table formset state, unbound. `LAYOUT_UTILITIES` gains
  `overflow-x-auto`.
- README: the table is chosen with `helper.template = "daisyui/table_inline_formset.html"`; what
  is drawn (daisyUI's `table`, a heading per visible field, each input named by an `aria-label`
  and described by its help text, hidden fields in the row's first cell, no table for a formset
  with no forms); a helper layout is not applied; every form is assumed to have the same fields;
  the table sits in an element with Tailwind's `overflow-x-auto`. CHANGELOG: one line.

---

## US3 — Every error appears beside what it belongs to (P2)

Issue: #33. Delivers FR-010 – FR-013; SC-004.

### T005 — Formset-wide errors, and a row's form-wide errors

**Files**: `mvp_forms/templates/daisyui/errors_formset.html`,
`mvp_forms/templates/daisyui/uni_formset.html`,
`mvp_forms/templates/daisyui/table_inline_formset.html`, `tests/forms.py`,
`tests/test_pack/test_formsets.py`, `tests/test_pack/test_independence.py`, `README.md`,
`CHANGELOG.md`

Plan, *The templates*, *Tests*; research R7.

- `errors_formset.html`, included in both layouts unless errors are off. In the table, the row's
  form-wide errors in its first cell with the id `<form.prefix>_errors`, and `aria-describedby`
  on the row naming it.
- `tests/forms.py` gains a form with a form-wide rule and a formset with a formset-wide rule,
  each raised with a `code`.
- Tests, `TestFormsetErrors`, as the plan lists them (US3.1 – US3.6). In the stacked layout a
  field's error and a form-wide error are already drawn after T001, so those cases pass on their
  first run. The red step is the formset-wide error and the table row's.
- `test_independence.py`: each layout's state with all three kinds of error.
- README: where each kind of error is drawn in each layout, `formset_error_title`, and
  `{{ formset|as_crispy_errors }}` with the path `daisyui/errors_formset.html`. CHANGELOG: one
  line.

---

## US4 — Delete and ordering inputs match the rest of the pack (P3)

Issue: #34. Delivers FR-014, FR-015; SC-006.

### T006 — Delete and order inputs, and rows that line up

**Files**: `mvp_forms/templates/daisyui/table_inline_formset.html`,
`tests/test_pack/test_formsets.py`, `tests/forms.py`, `README.md`, `CHANGELOG.md`

Plan, *`FormsetTable`*, *Tests*; research R6, R9.

- The table template draws an empty cell where a row's cell is `None`.
- Tests, `TestDeleteAndOrder`, as the plan lists them (US4.1 – US4.5 and the edge case of a
  deleted form drawn again).
- README: the delete and order inputs are drawn as the pack's checkbox and number input, each
  with a column of its own in the table, and a form with no delete field leaves that cell empty.
  CHANGELOG: one line.

---

## US5 — Both layouts can be seen in the demo project and found in the README (P3)

Issue: #35. Delivers FR-019, FR-020; SC-005, SC-007.

### T007 — The formset pages, their standalone twins, README and CHANGELOG

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`
(icon names), `demo/templates/demo/formset_stacked.html`,
`demo/templates/demo/formset_stacked_standalone.html`,
`demo/templates/demo/formset_table.html`,
`demo/templates/demo/formset_table_standalone.html`, `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

Plan, *The demo project*, *Tests*; research R11.

- The two page pairs, their four routes, two menu entries and the forms the plan describes. Each
  page draws the formset to submit and the same formset already failing, under different
  prefixes, so no id repeats.
- Tests in `test_demo.py`, as the plan lists them (US5.1 – US5.3, SC-005).
- README: the contributing section names the four pages. Read the public surface's formsets part
  through once against the finished pack and correct anything it no longer says truly
  (US5.4, FR-020). CHANGELOG: one line for the demo pages.
