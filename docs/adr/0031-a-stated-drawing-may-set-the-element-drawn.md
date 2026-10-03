# ADR 0031 — A stated drawing may set the element drawn, and never what is submitted

**Status:** accepted

## Decision

When a developer states a drawing for a field, the pack draws the element that drawing needs,
even where it is not the element the field's widget would draw:

- a `rating` is radio inputs, whether the field's widget is a radio group or a select
- a `range` is an input of type `range`, where the field's widget is a number input

It does so only for a drawing stated by name, and only where the form receives the same value
either way. A select and a radio group submit the same value for the same choice. A number input
and a slider submit the same number. The field's validation and cleaned data do not depend on
the drawing.

The form's own widget is never written to. A radio group is drawn through a shallow copy that
names the pack's rating template. A select is drawn through a `RadioSelect` made for that one
draw from the select's attributes and choices. A number input is drawn through a shallow copy
whose input type is `range`, by Django's own template.

A form that states no drawing is drawn as
[ADR 0002](0002-the-pack-never-changes-an-input-type.md) says: with the input type each widget
declares.

## Why

ADR 0002 exists because the input type decides what the browser submits, and a setting about
appearance must not change that. Both conditions here keep its reason intact: the developer
asked for the element by name, and what is submitted is the same.

Requiring `RadioSelect` for a rating, or `NumberInput(attrs={"type": "range"})` for a range, was
rejected. A Django `ChoiceField` is a select unless told otherwise, so drawing one as a rating
would need two changes in two places, one of them on the field.

A rating is built on Django's `RadioSelect` because it already gives every option the widget's
attributes, an id of its own and `checked`. A `Select` gives its options none of them, and
withholds `required` when its first choice has a value. Passing `type` as an attribute to a
number input would write the attribute twice, which is why the copy's input type is set instead.

Drawing through a copy follows
[ADR 0004](0004-inputs-are-drawn-without-writing-to-the-widget.md) and
[ADR 0012](0012-widget-templates-through-a-copy-of-the-widget.md).

A slider has no empty state. An optional number field drawn as a range always submits a number,
and the README says so.

## Revisit if

A drawing is wanted where the submitted value would differ, or a project needs a select
subclass's own options to reach a rating.
