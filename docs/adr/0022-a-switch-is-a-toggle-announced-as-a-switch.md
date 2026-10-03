# ADR 0022 — A switch is daisyUI's toggle, announced as a switch

**Status:** accepted, amended by [ADR 0030](0030-each-kind-of-field-has-its-own-drawings.md)

## Decision

A boolean field has three drawings, stated with `Choice(drawing=...)`: `checkbox`, `toggle` and
`switch`. `Modifiers.drawings` in `mvp_forms/choices.py` maps each to the daisyUI class it is
drawn with. A toggle and a switch are both daisyUI's toggle, the same checkbox input with the
class `toggle`. The one difference is that a switch carries `role="switch"`.

So a toggle is still a checkbox to assistive technology, checked or not checked, and a switch is
announced as a switch that is on or off. They look the same.

The drawing changes the class and the role handed to the widget for one render, and nothing
else. The input stays `type="checkbox"` with the field's name, so what is submitted and what the
form cleans to do not depend on the drawing. No template in the pack reads the drawing. The frame
draws a toggle the way it draws a single checkbox, which is why it keeps the label, the required
marker, the help text, the errors and the disabled state.

A later drawing for a boolean field adds a name to `Modifiers.drawings`. If it needs a class
daisyUI does not have, it does not belong in this pack.

## Why

The request named a toggle and a switch as two things, and daisyUI has a checkbox, a toggle and
nothing called a switch. A third look would need classes the pack defines itself, which
[ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md) rules out, and it would not work
on a page that loads only daisyUI's CDN build.

Telling them apart by where the label sits was rejected. That is appearance, and it would leave
the two the same to anyone not looking at the page.

What assistive technology says is the one difference that is behaviour, that needs nothing
beyond stock daisyUI, and that matters to someone. A setting that takes effect as a state reads
naturally as a switch, and a field that records agreement reads naturally as a checkbox. The
developer knows which a field is. `role="switch"` on a checkbox input is allowed by the HTML and
ARIA specifications and takes its state from the input's own `checked`, so no script is needed.

Keeping the input a checkbox, and changing only an attribute and a class, follows
[ADR 0002](0002-the-pack-never-changes-an-input-type.md) and
[ADR 0004](0004-inputs-are-drawn-without-writing-to-the-widget.md).

## Revisit if

daisyUI gains a component of its own for a switch, or the maintainer settles that a toggle and a
switch should differ in some other way.
