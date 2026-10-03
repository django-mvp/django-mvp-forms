# ADR 0030 — Each kind of field has its own drawings

**Status:** accepted

## Decision

A drawing is how one field is drawn when it is not drawn the ordinary way, stated with
`Choice(drawing=...)`. Which drawings a field takes is decided by its widget:

| The field's widget | Drawings |
|---|---|
| `CheckboxInput` or a subclass | `checkbox`, `toggle`, `switch` |
| `Select` or `RadioSelect` or a subclass that holds one value | `rating` |
| `NumberInput` or a subclass | `range` |
| anything else | none |

A multiple select, a checkbox group and a null-boolean select hold no single choice and take
none. A select or a radio group that names a template of its own takes none either, because a
rating is drawn through the pack's template.

`FieldInput.drawings_of` in `mvp_forms/templatetags/daisyui.py` is that table.
`Modifiers.drawings` in `mvp_forms/choices.py` still maps each drawing to the daisyUI class it is
drawn with.

A drawing stated for a field that does not take it raises `InvalidChoice` when the form is
drawn. The error names the field and carries the drawings that field takes, which is nothing for
a field that takes none. The pack never falls back to another drawing. A hidden field is drawn
as a hidden input and nothing stated for it is looked at.

A later drawing adds its name to both tables. A form still has no drawing of its own.

## Why

[ADR 0022](0022-a-switch-is-a-toggle-announced-as-a-switch.md) gave a boolean field three
drawings and refused a drawing on anything else. A rating and a range are the same kind of
statement, "draw this one field another way", for two other kinds of field. Stating them the
same way keeps one place to say it, lets one field carry a drawing, a size and a colour
together, and works for a form with no layout.

A widget for each, or a layout object for each, was rejected. A widget would make a developer
change their form's fields to change how they look.
[ADR 0019](0019-a-choice-is-stated-on-the-helper-and-by-one-layout-object.md) says the package
defines one layout object, and a second would not reach a form drawn without a layout.

Deciding from the widget what a field may be drawn as is not the same as deciding how to draw
it. Nothing is drawn differently until the developer states a drawing by name.

The error carries the field's own drawings because a developer who writes `toggle` on a select
is best helped by being told that a select takes `rating`.

## Revisit if

A drawing applies to more than one kind of field, or a project needs a rating from a select
that has its own template.
