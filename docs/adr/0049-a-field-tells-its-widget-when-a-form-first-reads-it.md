# ADR 0049 — A field tells its widget what was stated when a form first reads it

**Status:** accepted

## Decision

`PartialDateField` overrides `get_bound_field`, sets `resolution`, `min_value` and `max_value` as
plain attributes on its widget, and returns what Django returns. Nothing is set in the field's
`__init__`. Each widget carries class defaults for the three attributes, so a widget used on
another field draws to the day with no limits.

A widget is swapped before the form is first drawn or validated.

## Why

A developer often names a widget in a form's `__init__`, after the field was built. Telling the
widget in the field's `__init__` would leave that widget knowing nothing, and it would draw a day
part the field refuses.

`get_bound_field` is the hook Django documents for a field to take part in how it is drawn. A
form calls it once for each field and keeps the result, and each form holds its own copy of the
field and the widget, so one form cannot change another.

`widget_attrs` was not enough. It runs once, in `__init__`, and can only add HTML attributes,
which cannot take a part out of a multi-widget.

Setting plain attributes on a widget is what Django's own fields do with `is_required`.

## Revisit if

A project needs to swap a widget on a form that has already been validated, or Django changes
when a form calls `get_bound_field`.
