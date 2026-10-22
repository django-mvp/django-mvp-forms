# ADR 0064 — A joined group holds text, drawn as an item of the join

**Status:** accepted. Amends [ADR 0059](0059-a-joined-group-holds-buttons-drawn-as-items-of-the-join.md): a `Join` holds text as well as fields and buttons

## Decision

A `Join` holds django-crispy-forms' own `HTML` anywhere among its fields, alone or inside a
`Choice`. A subclass of `HTML` still raises `InvalidMember`.

`Join.contents()` returns a `GroupText` in the place of each `HTML`, carrying the `HTML` and the
`Choice` around it in the group. `Join.members()` returns the members alone, as before.

The text is rendered by its `HTML` with the form's context and drawn inside
`<span class="input join-item w-auto">`, in its place among the inputs. It takes the size, colour
and variant of an input: the form's, then a `Choice` around the group or around the text. A
`Choice` around the text that states a label or a drawing raises `InvalidChoice`.

Text is not a member. A group whose only visible entries are text draws no join, and its hidden
members are drawn alone.

## Why

A measurement and its uncertainty are written with a `±` between them, and a group could not draw
that (#221). The nearest drawing was a disabled button, which reads as a control.

`HTML` is the layout object django-crispy-forms already has for text in a layout (ADR 0008), so a
developer writes what they would write anywhere else, and the pack adds no layout object of its
own. The text belongs between two fields rather than to one of them, so it is an entry of the
group and not text attached to a member.

daisyUI's `input` frames the text with the border, height and padding of the inputs beside it, so
the group reads as one piece at every size. Drawing it with an input's size, colour and variant
keeps it matched to the members when the form or a `Choice` changes them. `w-auto` keeps it as
wide as its text, where an input takes the room left over.

Text alone has nothing to stand between, so it does not make a group worth drawing, where a
button does (ADR 0059).

## Revisit if

A member is asked to carry text attached to it, as `PrependedText` attaches it to a lone field.
A group is asked to hold a layout object that is neither a field, a button nor `HTML`.
