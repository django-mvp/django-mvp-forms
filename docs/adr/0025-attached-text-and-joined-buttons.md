# ADR 0025 — Attached text and joined buttons are daisyUI's own markup, one size, and buttons are drawn once

**Status:** accepted

## Decision

**Attached text** is daisyUI's label inside an input. A wrapping `<label>` carries the component
class (`input` or `select`), the size, colour and variant, the width and the error modifier.
Each text is a `<span class="label">` inside it, and the input inside is drawn with no class of
the pack's. Because the wrapper is a label, the text is part of the input's accessible name.
That holds while the form draws labels. With labels off the input is named by an `aria-label`
holding the field's label, which takes the place of every label, the wrapper included.

**A field with buttons** is daisyUI's `join`: one element carrying `join` around the input,
which carries `join-item`, and the buttons.

**The buttons are drawn once.** django-crispy-forms draws them before the field's template runs
and the pack uses that string as it is. The pack adds no class to them and never renders a
button a second time.

**A joined group takes one size.** The attached text shares the wrapper with the input, so it
always has the input's size. A button takes the size stated for the form and the size of a
`Choice` around the `FieldWithButtons`. A size stated for one field by name reaches the input
and not its buttons.

Only an input and a select have this markup. On any other widget, and on a group, the field is
drawn undecorated.

## Why

Both are the markup daisyUI documents for the job, and the README says stock markup wins.

Tying the text to the input with `aria-describedby` was rejected. Django writes that attribute
itself for help text and errors, and steps aside as soon as anyone else supplies one, so the
pack would have to rebuild the whole list for every state.

In daisyUI 5.7 the `join` container sets the corner variables on its children, and `btn`,
`input` and `select` read them. A button is squared off on its joined side with no class of its
own. `join-item` adds the one-pixel overlap, which a developer can ask for with `css_class`.

Rendering a button again, to add a class, would run already-rendered text through the template
engine: a button's `render` renders its content as a template and stores the result back on the
object. Text a person typed could then be evaluated as template code.

That is also why a size stated for one field by name cannot reach its buttons: they were drawn
before the field, with nothing saying which field they belong to.

## Revisit if

django-crispy-forms draws the buttons after the field, or passes the field to them, or daisyUI
changes how `join` squares its children.
