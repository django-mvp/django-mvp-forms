# ADR 0015 — In a table, every form is exactly one row

**Status:** accepted

## Decision

In the table layout each form of a formset is one `<tr>` in the table's body, whatever the form
holds. Nothing else adds a row.

- The form's hidden fields are drawn in the row's first cell.
- The form's own errors, which are its form-wide errors and its hidden fields' errors, are drawn
  in that same cell ahead of the field, in an element whose id is the form's prefix followed by
  `_errors`. The row names that element with `aria-describedby`. A row without such errors has
  neither.
- The columns are the first form's visible fields. A form that has no field for a column gets an
  empty cell, so every row has as many cells as there are headings.
- A formset with no forms draws no table.

The rows and columns are worked out by `FormsetTable` in `mvp_forms/templatetags/daisyui.py`,
because a template cannot look a field up by name.

## Why

A table whose rows are the forms is the one thing a host project, or a script that adds and
removes rows, can rely on when reading the page. An error drawn in a row of its own would make a
form two rows only while it is invalid, which is when the count matters most.

Django gives every form of a formset the same fields with one exception: with
`can_delete_extra=False`, forms beyond the initial ones have no delete field. Initial forms come
first, so the first form always has the delete field when any form does, and its visible fields
are the widest set.

The id cannot collide with a field's: field ids start `id_` and field frames `div_id_`
(ADR 0005).

## Revisit if

A form's own errors prove unreadable in the first cell, or django-mvp's row handling needs a
different hook ([issue #13](https://github.com/django-mvp/django-mvp-forms/issues/13)).
