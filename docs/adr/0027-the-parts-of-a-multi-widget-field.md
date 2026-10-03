# ADR 0027 — The parts of a multi-widget field are classed and named on a copy

**Status:** accepted. Extends [ADR 0012](0012-widget-templates-through-a-copy-of-the-widget.md)

## Decision

A field whose widget is a `forms.MultiWidget` is drawn from a deep copy of the widget. On the
copy, for one render, each part is given:

- a class: the part's own class names, then the pack's for that part's kind, with the size,
  colour, variant and error modifier that apply to it;
- an `aria-label`, unless it has one or is hidden: `Date` and `Time` for a
  `forms.SplitDateTimeWidget`, translated, and the field's label for any other multi-widget.

The form's own widget and its parts are never written to. The frame is the `<fieldset>` ADR 0011
draws for a group, so the parts share one legend, one help text and one set of errors.

This holds with or without `MultiWidgetField`, which draws through the ordinary field template.

## Why

A class passed to `BoundField.as_widget` replaces every part's own class, including one a
developer gave a part through `MultiWidgetField`. That is the one thing the layout object exists
to set, so the parts have to be classed one by one.

ADR 0004 and ADR 0012 keep the pack from writing to a form's widget. `MultiWidget` copies its
parts when it is deep-copied, so the copy can be changed freely.

A part with no name is announced as an unnamed text box. The pack knows what the two parts of a
split date and time are. For any other multi-widget it does not, and the field's label is the
only name it has.

## Revisit if

Django gives the parts of a multi-widget names of their own.
