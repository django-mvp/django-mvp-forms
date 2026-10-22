# ADR 0065 — A join of one field replaces attached text and FieldWithButtons

**Status:** accepted. Amends [ADR 0064](0064-a-joined-group-holds-text-drawn-as-an-item-of-the-join.md): a `Join` of one field is how text or a button is attached to an input

## Decision

A `Join` whose one visible member is a field is drawn in that field's own frame: a `<div
class="fieldset">` with the id `div_<id>`, a `<label>` for the input, the join, and the field's help
text and errors. The label is the group's `label`, which also becomes the input's `aria-label`
unless the developer wrote one, or else the field's own label. A group of several fields is still a
`<fieldset>` with a `<legend>`.

django-crispy-forms' `PrependedText`, `AppendedText`, `PrependedAppendedText` and `FieldWithButtons`
are deprecated. The pack draws them for one more minor version with a `DeprecationWarning` naming
the `Join` that replaces each, then stops and removes their two templates.

`mvp_forms.layout` passes through, unchanged, the twelve other layout objects of
`crispy_forms.bootstrap` the pack draws, and the documentation imports them from there.

## Why

The four deprecated objects and `Join` all draw a daisyUI `join` around an input, through three
templates and three code paths. Every change to size, colour, error state or Tom Select handling had
to be made in each. `Join` already holds text before, between and after fields and holds buttons, so
it covers everything the four do with one set of rules (#224).

For the switch to cost a project nothing, a group of one field has to read as a field. A fieldset
with a legend is the markup for several controls. For one it is heavier than a label, and with no
`label` given the group had no visible label at all.

`crispy_forms.bootstrap` is named for the framework django-crispy-forms' own templates were written
for. Telling a daisyUI project to import from it reads as if Bootstrap were involved. Passing the
classes through unchanged, rather than subclassing them, keeps them the same objects, so a form that
still imports from `crispy_forms.bootstrap` draws exactly as before.

Attached text never took a floating label, so moving to `Join`, whose members never float, loses
nothing.

## Revisit if

A developer needs text attached inside an input's daisyUI wrapper, where it is part of the input's
accessible name, rather than beside it as an item of the join.
