# ADR 0068 — A formset's forms are drawn as fieldset panels, and are stated on the helper

**Status:** accepted. Extends [ADR 0066](0066-a-fieldset-is-a-panel-that-can-collapse.md) to formsets, and [ADR 0019](0019-a-choice-is-stated-on-the-helper-and-by-one-layout-object.md) with two more arguments of `FormChoices`

## Decision

Each form of a stacked formset is drawn as the panel a `Fieldset` is, by
`daisyui/layout/fieldset.html` itself, in place of a `<div>` with a divider between one form and
the next. A formset drawn as a table is drawn inside one such panel, and every form stays one row
of it, as [ADR 0018](0018-in-a-table-every-form-is-exactly-one-row.md) requires. The table itself
moves to `daisyui/table_inline_formset_table.html` so the tag can draw it inside the panel.

How the panels are set out is stated on the helper, as two arguments of `FormChoices`:

- `forms=StackedForms(legend=..., collapsible=..., open=...)` for the stacked layout
- `table=TablePanel(legend=..., collapsible=..., open=...)` for the table

A stacked form's legend is a template rendered with `number`, the form's place counting from one,
and `form`. The table's legend is rendered with `formset`. Both take the two checks a `Fieldset`
makes: `open` needs `collapsible`, and `collapsible` needs a legend.

A form, or a table, holding an error of any kind is drawn open with the error mark a collapsible
fieldset carries. Ids start with the form's prefix, or the formset's for the table, followed by
`-panel` or `-table`.

## Why

Once fieldsets became panels that collapse (#226), the forms of a formset were the one grouping
in a form that looked different and could not collapse. Drawing them with the fieldset's own
template keeps the two the same by construction rather than by copying its classes.

One legend template answers the three ways a form could be named: by its place, by a value it
holds, or by a fixed label. A `Fieldset`'s legend is already rendered as a template, so this adds
no mechanism.

The statement sits on the helper because the helper is where every drawing choice of the pack is
stated, under one attribute whose constructor refuses an argument it does not know. The formset
class is Django's, and the pack subclasses nothing of Django's or django-crispy-forms'. The table
gets an object of its own because its legend names the formset, where a stacked form's names one
form.

A form counts as in error for a form-wide error as well as a field error, because a closed panel
hides either.

The table's panel carries `min-w-0`. A fieldset's minimum inline size is its content's, which
would stop the table scrolling sideways inside it on a narrow screen.

## Revisit if

A formset needs a heading of its own before its first form, or the table layout needs each row to
collapse on its own.
