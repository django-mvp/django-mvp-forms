# ADR 0004 — Inputs are drawn by the pack's own tag, without writing to the widget

**Status:** accepted, amended by [ADR 0009](0009-widget-templates-through-a-copy-of-the-widget.md): the tag is now `{% daisyui_field %}`, and three widgets are drawn from templates of the pack's own

## Decision

The pack draws every widget through its own template tag, `{% daisyui_input field %}`, backed by
the class `FieldInput` in `mvp_forms/templatetags/daisyui.py`. `FieldInput` works out the
attributes the pack adds and passes them to `BoundField.as_widget(attrs=...)`, which merges them
over the widget's own for that one render. Nothing is written to `widget.attrs`.

A later feature that covers a new widget adds it to `FieldInput.components`. It does not use
django-crispy-forms' `{% crispy_field %}` tag.

## Why

`{% crispy_field %}` does two things this pack cannot accept. It appends the widget's class name
in lower case, such as `textinput`, which no daisyUI build defines. And it writes the classes into
`widget.attrs`, so the change stays on the form instance after the render.

Passing attributes for one render keeps every attribute the developer set, adds the pack's class
beside the developer's own, and leaves the form as it was found.

One case cannot go through `as_widget`. When a helper turns errors off and an invalid field has
no help text, the input's description has to be removed, and `as_widget` adds Django's own back
whenever none is given. `FieldInput.render` builds the attributes with
`BoundField.build_widget_attrs` and renders the widget itself in that case only. See ADR 0005.

## Revisit if

django-crispy-forms offers a way to add a class for one render without adding the widget's class
name, or Django lets a caller suppress the description it adds.
