# ADR 0059 — A joined group holds buttons, drawn as items of the join

**Status:** accepted. Amends [ADR 0037](0037-fields-are-joined-by-a-layout-object-of-the-packs.md): a `Join` holds buttons as well as fields

## Decision

A `Join` holds a `StrictButton`, a `Submit`, a `Button` or a `Reset` anywhere among its fields,
alone or inside a `Choice`. A `Hidden` is an input of django-crispy-forms and not a button, so it
still raises `InvalidMember`.

`Join.contents()` returns what the group holds in order, a `Member` for each field name and a
`GroupButton` for each button, carrying the `Choice` around it in the group. `Join.members()`
returns the members alone, as before.

Each button is drawn by `render_field`, as it is drawn anywhere else, with the group placed in
the context as `daisyui_join`. `daisyui_button` reads it and adds `join-item` to the button's
classes after the classes of its choices. The button sits in the join in its place among the
members' inputs.

A button takes the form's `size`, `button_color` and `button_variant`, and a `Choice` around the
group or around the button, as the buttons of a `FieldWithButtons` do. A group with no visible
member but a button draws the join with the button in it.

Members are drawn exactly as ADR 0037 draws them.

## Why

daisyUI's lead example of a join is a select, a text input and a button in one piece, and
`FieldWithButtons` joins buttons to one field only. The maintainer settled under #94 that a group
of fields takes buttons too, and that they follow the form's choices as any other button does.

Drawing the button with django-crispy-forms' own `render_field` keeps a `Submit`'s name and value
and the escaping of a button's content, which copying it into the pack would drift from.

The pack adds `join-item` to a button in a group, where a `FieldWithButtons` leaves it to the
developer, because the group draws every child of the join itself and already writes `join-item`
on each member. A button without it keeps its own corners and border, so the group would not read
as one piece. `FieldWithButtons` draws its buttons through django-crispy-forms before the field,
with nothing in the context to say they are joined.

A group of hidden members and a button still has something to show, so the button is not dropped.

## Revisit if

`FieldWithButtons` starts writing `join-item` on its buttons, when the two should say the same
thing. A group is asked to hold a layout object that is neither a field nor a button.
