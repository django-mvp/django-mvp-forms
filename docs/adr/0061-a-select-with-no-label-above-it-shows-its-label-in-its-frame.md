# ADR 0061 — A select with no label above it shows its label in its frame

**Status:** accepted

## Decision

When a form draws no labels, through `form_show_labels` or `InlineField`, a select whose field has
a label is drawn in daisyUI's `select` frame with the label as a `<span class="label">` before
it. This holds for a stock select, `TomSelect`, `TomSelectMultiple`, counted or not, and a
django-tomselect control. A select with text attached by a layout, buttons joined to it or a
place in a `Join` keeps those and shows no label of its own.

The frame is a `<label>` around a stock select and a `<div>` around a Tom Select control.
`mvp_forms/tomselect.js` opens a control when the frame outside it is pressed, and
`mvp_forms/tomselect.css` fits the control into the frame, with its dropdown as wide as the
frame.

## Why

With labels off, a text input can carry its name as a placeholder, but a select shows only its
value. A row of filters drawn that way reads "Any", "Any", "2 selected", and a person cannot
tell one from another. daisyUI documents a select with a label inside its frame, which is the
markup the pack already draws for attached text, so the name costs no new component.

It follows from the layout and is not a widget setting. The problem belongs to every select in a
form with labels off, and a setting on one widget would leave the stock select and
django-tomselect's controls without it.

A `<label>` passes every press inside it to the first control it holds. For a Tom Select control
that is the select Tom Select has hidden, so a press on an option left the control and closed its
dropdown. A `<div>` passes nothing on, and the script opens the control instead.

## Revisit if

daisyUI or Tom Select changes how a select inside a frame is drawn, or a host project needs a
select with labels off to show only its value.
