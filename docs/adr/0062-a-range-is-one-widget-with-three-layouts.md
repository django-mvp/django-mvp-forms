# ADR 0062 — A range is one widget with three layouts, and no field

**Status:** accepted

## Decision

`RangeInput`, `DateRangeInput` and `DateTimeRangeInput` are `MultiWidget`s of two inputs, drawn
by `mvp_forms/widgets/range.html`. One widget per kind of input carries every layout as a
setting: two frames side by side by default, `joined=True` for one daisyUI `join` in one row, and
`compact=True` for both inputs in one frame with `separator` between them.

The widgets read a pair or a `slice`, so django-filter's `RangeFilter` and
`DateFromToRangeFilter` take them as their `widget`. The package ships no range field, and the
pack does not restyle django-filter's own range widgets.

The pack's template tag tells the widget's template whether a label is drawn. With labels off the
field's label is shown in the first frame, and each end's name becomes its input's placeholder.

The text inside a frame is drawn in the theme's full text colour, as attached text is, because
daisyUI's 60% label colour falls below 4.5:1 in some themes. Sizes the pack cannot express as a
class, the share of the row each frame takes and the divider around the separator, are written in
`style` attributes, as the image input writes its size.

## Why

The three layouts draw the same two inputs and send the same two values. Three widget classes per
kind would be nine classes for one job.

A field would duplicate what django-filter already ships for the list pages ranges are wanted
on, and a plain form builds one in a few lines as a `MultiValueField`. Restyling django-filter's
own widgets would tie the pack to their template and their suffixes, for what passing a widget
already gives.

The point input already draws two ends in two frames that show their names, so the default
layout is that one.

## Revisit if

A project needs a range field in a plain form often enough to share one, or django-filter's range
widgets become what most projects draw.
