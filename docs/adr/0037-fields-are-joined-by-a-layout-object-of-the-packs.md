# ADR 0037 — Fields are joined by a layout object of the pack's, under one label

**Status:** accepted. Amends [ADR 0019](0019-a-choice-is-stated-on-the-helper-and-by-one-layout-object.md) and [ADR 0008](0008-layouts-use-django-crispy-forms-own-layout-objects.md): the package defines a second layout object, `Join`

## Decision

`Join`, in `mvp_forms/layout.py`, names several fields to be drawn as one daisyUI join. It is
the second layout object the package defines. It subclasses nothing of django-crispy-forms but
`LayoutObject` and shadows no upstream name.

A group holds field names, a `Field` of exactly that class, which passes attributes to its
names, and a `Choice`. `Join.members()` returns them as a list of `Member`. Any other layout
object raises `InvalidMember` with its class name. A member the pack does not draw as one input
or one select raises `InvalidMember` with the field's name. Nothing is passed over.

Each member is drawn by a django-crispy-forms `Field` given the template
`daisyui/layout/join_member.html`, through `render_field`, inside the member's `Choice` when it
has one. That template calls `daisyui_field` with the option `member=True` (ADR 0023) and draws
the input alone.

The group is drawn by `daisyui/layout/join.html`:

- a `<fieldset>` whose `<legend>` is the group's label, as escaped text, with the required
  marker when any visible member is required;
- one element carrying `join`, with the developer's id, class and attributes, whose direct
  children are the visible members' inputs, each carrying `join-item`;
- the hidden members' inputs after that element, never inside it;
- each visible member's help text and errors, drawn by `daisyui/field_messages.html` with the
  ids Django gives them (ADR 0005).

A member draws no label. Its input is named by an `aria-label` holding its own field's label,
unless the developer wrote one. A member never takes a floating label.

In place of `w-full` (ADR 0007), a member drawn as an input carries `flex-1` and one drawn as a
select carries `w-auto`. A width the developer wrote on a member is kept and the pack adds
neither.

Size, colour and variant reach each member as they reach any field. One size is not enforced on
a group.

## Why

Joining is a statement about several fields at once, in an order, with a label of its own. ADR
0019 reserved `Choice` for a statement about one field or one button. No layout object of
django-crispy-forms can mean "these inputs, joined" without changing what it draws today:
`MultiField` and `Div` draw each field in its own frame, and `FieldWithButtons` takes one field.
A `MultiWidget` joins the parts of one field, where these are fields validated and cleaned on
their own.

A join squares the corners of its direct children, counting the first and the last among all of
them. A member inside a frame of its own would not be squared, and a hidden input as the first
or last child would take the rounding from a visible one. So the group draws its members one by
one and decides where each goes.

Drawing a member with django-crispy-forms' own `Field` keeps what `render_field` does: it
records the field as rendered, applies a `Field`'s attributes and deals with a name the form
lacks. Copying that into the pack would drift from it.

One legend with a name on each input is what the pack already does for a group of choices and
for the parts of a multi-widget field (ADR 0011, ADR 0027). Help text and errors keep their own
ids because Django writes each input's description from them, so each stays tied to its input
at no cost.

The label is escaped because ADR 0025 draws a developer's text as markup only where
django-crispy-forms documents it so, and escaped text can also be the fieldset's `aria-label`
when the helper turns labels off.

The developer's class goes on the element carrying `join` because `join-vertical` only works
there, and `FieldWithButtons` already puts it there (ADR 0026).

Two members each carrying `w-full` take equal shares, which is what a `Row` of columns already
gives. A country code beside a number wants the select as wide as its options and the input
filling the rest.

A field that cannot be joined raises, where attached text on such a field is simply left off,
because a group whose member cannot be joined has no sensible drawing left.

## Revisit if

django-crispy-forms ships a layout object for a join. daisyUI changes how a join squares its
children. A group is asked to hold buttons, or to be held to one size, which two open questions
on the tracker ask.
