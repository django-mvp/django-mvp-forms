# ADR 0002 — The pack never changes an input's type

**Status:** accepted, amended by [ADR 0030](0030-a-stated-drawing-may-set-the-element-drawn.md)

## Decision

A template in the pack draws the widget it is handed, with the input type that widget declares.
It never reads the type to decide how to draw, and never sets one. A `DateField` is therefore a
text input, as Django makes it, unless the developer writes
`DateInput(attrs={"type": "date"})`. Either way it is drawn as a daisyUI `input`.

## Why

The input type decides the format the browser submits, and the field's parsing has to match it.
A pack that turned date fields into date pickers would break every form that sets its own
`input_formats`, and it would change what a form submits because of a setting about appearance.

It would also be work done per field, and the pack's first goal is that an ordinary form is drawn
well with nothing done to it.

## Revisit if

Django changes the default type of its date and time widgets, at which point the pack follows
Django without doing anything.
