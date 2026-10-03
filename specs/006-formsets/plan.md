# Implementation Plan: formsets drawn stacked or as a table

**Branch**: `006-formsets` · **Date**: 2026-10-03 · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

django-crispy-forms asks a template pack for three templates when it is handed a formset, and the
pack has none of them. This feature adds those three and a fourth for the table, which a developer
selects with `helper.template`. The stacked layout draws each form through the template that
already draws a single form, so every input, label, help text and error comes out as FS-001 and
FS-002 defined it. The table draws one row per form and one column per visible field, with each
cell drawing the field through the same field frame with its label turned off. One small class in
the pack's tag module works out the table's columns and rows, because a Django template cannot
look a field up by name. The package gains no setting, no dependency, no script and no stylesheet.

## Technical Context

**Language/Version**: Python 3.12 and 3.13
**Primary Dependencies**: Django 5.2, 6.0 and 6.1; django-crispy-forms 2.7 or later. No new dependency.
**Storage**: none
**Testing**: pytest with pytest-django, BeautifulSoup for reading drawn markup (`tests/conftest.py`, the `draw` fixture)
**Target Platform**: any Django project that loads daisyUI 5 as its CDN install documents
**Project Type**: a published Django package with an undistributed demo project
**Constraints**: plain Django templates only; daisyUI classes for every component; a Tailwind utility only for layout and named in the class test; no import from django-mvp
**Scale/Scope**: four templates, one class and one tag, two demo page pairs

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I, testing | Every task is test-first. No test asserts wording, spacing, alignment or which utility is used. A class is asserted only where it is a daisyUI component a host project depends on (`table`). |
| II, simplicity | Four templates and one class. The stacked layout reuses `display_form.html` and the table reuses the field frame. |
| III, anti-abstraction | No base template shared by the two layouts and no helper subclass. The layout is chosen with the setting django-crispy-forms already has. |
| IV, integration-first | Tests draw real formsets, including a model formset and an inline formset, through `{% crispy %}` and `\|crispy`, post what was drawn, and bind it again. |
| V, security | Every error and label goes through the template layer and is escaped there. The row-error id is built from the form's prefix, which the developer sets. |
| VI, documentation | README public surface, CHANGELOG and the glossary change in the task that introduces each name. |
| VII, dependencies | None added. |
| VIII, i18n | The pack adds no text. |
| X, cohesion | The one class sits beside `FieldInput` in the tag module, which already holds the pack's drawing logic. |
| XI, compatibility | The template paths become public surface and are named in the README. Three are the names django-crispy-forms defines, the fourth is the name its own packs use. |
| XII, scope | No view, URL, script or empty form. The demo's views are the demo's. |
| XIII, plain templates | No Cotton in `mvp_forms/`. The existing test over every distributed template covers the new files. |
| XIV, stock daisyUI | `table`, `divider`, `alert` and `text-error` are daisyUI's. One Tailwind layout utility, `overflow-x-auto`, where daisyUI has no component (research R10). |

No violation to justify.

## Project Structure

```text
mvp_forms/
├── templatetags/daisyui.py              # gains FormsetTable and the daisyui_formset_table tag
└── templates/daisyui/
    ├── whole_uni_formset.html           # new: {% crispy formset %}, stacked
    ├── uni_formset.html                 # new: the stacked forms, also {{ formset|crispy }}
    ├── errors_formset.html              # new: formset-wide errors
    └── table_inline_formset.html        # new: the table, chosen with helper.template

demo/
├── forms.py                             # gains the order line form and its formset
├── views.py, urls.py, menus.py          # gain the two formset page pairs
├── settings.py                          # icon names for the two menu entries
└── templates/demo/
    ├── formset_stacked.html
    ├── formset_stacked_standalone.html
    ├── formset_table.html
    └── formset_table_standalone.html

tests/
├── forms.py                             # gains the forms and formsets the tests draw
├── conftest.py                          # gains a fixture that reads drawn inputs as post data
├── test_templatetags/test_daisyui.py    # gains TestFormsetTable
├── test_pack/test_formsets.py           # new: both layouts, errors, delete and order
├── test_pack/test_independence.py       # gains formset states and one layout utility
└── test_demo.py                         # gains the formset pages

CONTEXT.md, README.md, CHANGELOG.md      # glossary, public surface, change record
```

## The pack

### The templates

| Template | Reached by | Draws |
|---|---|---|
| `whole_uni_formset.html` | `{% crispy formset %}` with no `helper.template` | The form element when `formset_tag` is on, with `flat_attrs`, `formset_method` and `multipart` when the formset needs it; the CSRF token for a post form unless `disable_csrf`; `uni_formset.html`; then `inputs.html`, once, for buttons added to the helper. |
| `uni_formset.html` | the include above, and `{{ formset\|crispy }}` | `formset.media` once when `include_media` is on; the management form; `errors_formset.html` unless errors are off; then each form in its own `<div>`, drawn by `display_form.html` with `include_media` off. A daisyUI `divider` sits at the head of every form's container but the first. |
| `errors_formset.html` | the two layouts, and `{{ formset\|as_crispy_errors }}` | `formset.non_form_errors`, once, in the same `role="alert"` element `errors.html` uses, with `formset_error_title` when set. Nothing when there are none. |
| `table_inline_formset.html` | `helper.template = "daisyui/table_inline_formset.html"` | The same form element, token, media, management form and formset-wide errors, then the table, then `inputs.html`. |

The form wrapper is written out in both `whole_uni_formset.html` and `table_inline_formset.html`.
It is four lines and the two templates are otherwise unrelated, so it is not split out.

**The stacked form.** `display_form.html` is the template `whole_uni_form.html` already uses. It
draws `form.form_html` when django-crispy-forms rendered a helper layout for that form and the
plain field loop otherwise, and in both cases the form's own alert for its form-wide and
hidden-field errors. Nothing in it changes.

**The table.**

```text
<div class="overflow-x-auto">
  <table class="table">
    <thead><tr> one <th scope="col"> per column: the label and the required marker </tr></thead>
    <tbody>
      one <tr> per form
        one <td> per column
          first cell only: the form's hidden fields, then its form-wide errors
          the form's field for that column, drawn by the helper's field template
          with form_show_labels=False; nothing when the form has no such field
    </tbody>
  </table>
</div>
```

- A row's form-wide errors are `form.get_context.errors`, the list `errors.html` reads, drawn in
  `<div id="<form.prefix>_errors" role="alert" class="text-error">` with one `<p>` per error, and
  only when there are any and errors are on. The `<tr>` then carries
  `aria-describedby="<form.prefix>_errors"`.
- A formset with no forms draws no table.
- The table never reads `form.form_html`, so a helper layout is not applied.

### `FormsetTable` and the `daisyui_formset_table` tag

In `mvp_forms/templatetags/daisyui.py`, beside `FieldInput`:

```python
class FormsetTable:
    """Lay a formset's forms out as the rows and columns of one table."""

    def __init__(self, formset: BaseFormSet) -> None: ...

    @property
    def columns(self) -> list[BoundField]:
        """The first form's visible fields, in its own order. Empty with no forms."""

    @property
    def rows(self) -> list[dict[str, Any]]:
        """One entry per form, in the formset's order: the form and its cells."""
```

Each row is `{"form": form, "cells": [...]}`. A cell is the form's bound field with the column's
name, or `None` when the form has no field of that name. When there are no columns, each row has
one `None` cell, so the row's hidden fields and errors have a cell to sit in. Every row therefore
has the same number of cells.

```python
@register.simple_tag
def daisyui_formset_table(formset: BaseFormSet) -> FormsetTable: ...
```

Used as `{% daisyui_formset_table formset as table %}`. The names carry no leading underscore and
the class has no private helpers.

### What the pack leaves to Django and django-crispy-forms

- Which forms a formset has, their order, and their delete and order fields.
- Which fields a helper layout draws. A layout that does not name `DELETE` or `ORDER` draws
  neither, as django-crispy-forms documents.
- Every formset-wide rule, such as a minimum or maximum number of forms. Django reports those as
  formset-wide errors and the pack draws them as such.

## The demo project

Two page pairs, `formset-stacked` and `formset-table`, each with a standalone twin at
`<name>-standalone`, following the layout objects pages: the shell page extends `page_view.html`
and uses Cotton components around the forms, and the standalone page loads daisyUI's CDN build
and nothing else. Both pairs are reached from the sidebar.

`demo/forms.py` gains one form, an order line with an item, a quantity with help text, a unit
price and a hidden reference, and one formset of it with deletion and ordering on:

- the form refuses a quantity below one (a field error) and a line whose total passes a limit (a
  form-wide error, raised with a `code`);
- the formset refuses the same item on two lines (a formset-wide error, raised with a `code`).

A helper class for each layout sets `template` for the table and adds one submit button. Each
page draws the formset twice under different prefixes: once to submit, and once already bound to
data that fails all three ways, drawn without a form element. A post binds the submitted formset
and draws the page again. Nothing is saved.

Every string a person reads in the demo's Python is wrapped for translation.

## Tests

All in `tests/test_pack/test_formsets.py` unless named otherwise. Elements are found by id, name,
role and element type. A posted round trip reads every named input back out of the drawn markup
and binds a new formset from it, so "Django can read it back" is tested on what was drawn.

- **`TestStackedFormset`** (US1): three forms drawn in order, each in a container that holds its
  fields and no other form's; the management form's inputs each present once; a drawn formset of
  three and of none binds to the same count and is valid; a model formset's and an inline
  formset's hidden fields are in the output inside their form's container; a field is drawn as
  the same field in a single form is, compared element by element after the prefix is accounted
  for; one form element with `formset_tag` on and none with it off, never one per form; no helper
  draws stacked; `{{ formset|crispy }}` draws the forms and the management form; a helper layout
  is applied to each form; a helper button is drawn once; media is drawn once.
- **`TestTableFormset`** (US2): one `table` with one body row per form in order and one heading
  per visible field; each heading holds its field's label and a required field's heading holds
  the marker element; every input in a row has an `aria-label` equal to its label's text and an
  `aria-describedby` naming an element in the same cell when the field has help text, and none
  when it has not; a group keeps its `<fieldset>` and that is what is named; hidden fields are in
  their row and add no heading and no cell; the management form once; the round trip; switching
  `helper.template` is the only change between the two layouts; no forms draws no table and still
  round-trips; a helper layout is not applied.
- **`TestFormsetErrors`** (US3), parametrised over the two layouts: a field error in the second
  form is inside that form's unit, the input's `aria-describedby` names it, and no other unit
  holds it; a form-wide error in the third form is inside that unit, and in the table the row's
  `aria-describedby` names its element; a formset-wide error appears once, outside every unit; a
  formset holding all three draws each message exactly once; an unbound and a valid formset draw
  no `role="alert"` element and no row `aria-describedby`; a message holding markup is escaped;
  errors off draws none; `formset_error_title` is drawn when set; a hidden field's error is with
  its form; `{{ formset|as_crispy_errors }}` draws the formset-wide errors alone.
- **`TestDeleteAndOrder`** (US4), parametrised over the two layouts: the delete input is a
  checkbox with the pack's `checkbox` class and the order input a number input with `input`,
  each the same element the pack draws for a boolean and an integer field in a single form; in
  the table each has a heading and an `aria-label`; ticking one form's delete input in the drawn
  markup and posting it reports that form and no other in `deleted_forms`; order values are read
  back in `ordered_forms`; a formset with `can_delete_extra=False` draws no delete input for
  extra forms and every table row has as many cells as there are headings; a form marked for
  deletion and drawn again after a failed post keeps its delete input ticked.
- **`TestFormsetTable`** in `tests/test_templatetags/test_daisyui.py`: columns are the first
  form's visible fields in order; one row per form in order; a cell is that form's own bound
  field; a form missing a column's field has `None` there; no forms gives no columns and no rows;
  a form with only hidden fields gives one empty cell per row.
- **`test_independence.py`**: the parametrised states gain a formset in each layout, unbound and
  with all three kinds of error. `LAYOUT_UTILITIES` gains `overflow-x-auto`.
- **`test_demo.py`**: a contract class per layout run against the shell page and its standalone
  twin. Each page responds; holds a formset with delete and order inputs; shows the three kinds of
  error on the formset that already fails; comes back from an invalid post with all three on the
  submitted one; every visible input has a label that names it or an `aria-label`, every
  `aria-describedby` on the page names an element that exists, and no id repeats (SC-005); the
  sidebar links both shell pages and each page links its twin.

How the table behaves on a narrow screen, the space between stacked forms and where help text
sits are judged on the demo pages. No test pins them.

## Story order

**US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree.** They share
`test_formsets.py`, `tests/forms.py`, the class test and the README section, so they do not run
side by side. US3 and US4 are small and are built in one dispatch.

There is no foundational phase. FS-001 to FS-003 delivered the field frame, the form wrapper, the
buttons include and the test fixtures everything here stands on.

Documentation lands with the story that introduces the name: the glossary and the README's
formsets section with US1, the table's template path with US2, the error placement with US3, the
delete and order behaviour with US4, the demo pages with US5.

## Decisions to record

Graduate to `docs/adr/` when the build converges, numbered from the next number free on
`origin/main` at that point:

- A formset's layout is chosen with `helper.template`, and the pack's template names are the ones
  django-crispy-forms and its packs already use (D2, research R1 and R2).
- In the table every form is exactly one row: hidden fields and form-wide errors sit in the row's
  first cell, and a missing field leaves an empty cell (research R6 and R7).

Recorded in `decisions.md` only: media is drawn once for the formset (R8); a formset with no forms
draws no table (R6); the stacked form's container is a bare `<div>` with a divider (D6, #13).
