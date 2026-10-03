# ADR 0022 — A layout object decorates a field through options on the tag, and the frame stays one

**Status:** accepted. Amends [ADR 0006](0006-the-field-frame.md): the frame is `daisyui/frame.html`

## Decision

The field frame lives in `daisyui/frame.html`. `daisyui/field.html` calls `daisyui_field` and
includes it.

A layout object that changes how one field is presented has a template of two lines. It calls
the same tag with a keyword option naming the decoration, then includes the same frame:

```django
{% load daisyui %}
{% daisyui_field field prepended=crispy_prepended_text appended=crispy_appended_text as drawn %}{% include "daisyui/frame.html" %}
```

The options are keyword-only arguments of `FieldInput`: `prepended`, `appended`, `inline`,
`join`, `disabled` and `unlabelled`. `FieldInput` and `daisyui/field_body.html` draw what each
one means. A later layout object that decorates a field adds an option the same way.

The frame reads `drawn`, which the including template sets on the line before, so it is never a
page's variable. It asks `drawn.show_labels` whether to draw a label, which lets one field go
without a label while its neighbours keep theirs.

A host project that overrode `daisyui/field.html` to change the frame overrides
`daisyui/frame.html`.

## Why

django-crispy-forms asks for a separate template for each of these layout objects. Six templates
each holding a copy of the label, required marker, help text and errors would drift apart, which
is what ADR 0006 exists to prevent.

Template inheritance, with a block for the input, does not work here: a value a tag sets inside
a block is gone when the block ends, so a child template could not say how the input is drawn.

`FieldInput` already decides the input's class and attributes for one render, so it is where a
decoration that changes them belongs.

## Revisit if

A decoration needs markup outside the frame, or the options grow until `FieldInput` is doing
several unrelated jobs.
