# Planning notes: Floating labels and joined inputs

Notes for whoever plans and builds this feature. They say things about how, which the
specification does not. The plan answers each one by name.

## From the maintainer

These are standing rulings for this repository. They are paraphrased, not quoted.

Class policy, as ADR 0003 has it: daisyUI component classes and modifiers for every input, button
and component, and plain Tailwind layout utilities only where daisyUI has no component for the
job. The package ships no stylesheet and defines no classes. A host page on daisyUI's documented
CDN install needs no build step.

Pack templates are plain Django templates. They never use django-cotton or daisy-cotton, which
are for the demo project's own pages only. `{% include %}` is fine inside the pack.

The package never depends on django-mvp at runtime and never imports from it.

Size, colour and variant are stated through `FormChoices` on `helper.daisyui` and through the
`Choice` layout object (ADRs 0019 to 0022). A new kind of input takes them by adding its rows to
`Modifiers`.

There is no support for migrating layouts from other packs. Fields and widgets beyond the roadmap
arrive as needed, and not through this feature.

Each feature adds its own demo page or pages where it changes what a person sees, and its own
entry in the README's public surface.

Nothing under `.github/` is changed by this work.

## From writing the specification

daisyUI 5's floating label was read from its CDN stylesheet. The wrapper is a `<label
class="floating-label">` holding a `<span>` and the input. The span is transparent while an
`input` or `textarea` inside shows its placeholder, and is shown at the edge on focus or once
there is a value. With no placeholder attribute the span is at the edge at all times. With a
disabled input the span is transparent in every state. Check each of these against the daisyUI
version the pack pins before building on them, because FR-006 and FR-007 rest on them.

`floating-label` and `join`, `join-item`, `join-vertical` and `join-horizontal` are already in
`tests/data/daisyui-classes.txt`.

The frame draws the ordinary label from `drawn.show_labels`, and `InlineField` already offers the
label as a placeholder and keeps one the widget sets. FR-005 and FR-006 probably reuse both.

In daisyUI 5 a `join` sets its corner variables on its direct children. A member's input has to
be a direct child of the join for the corners to square off, so a member cannot be drawn inside
a frame of its own within the join. ADR 0026 records the same for a field with buttons.

The existing join in `daisyui/field_body.html` carries `w-full`, and ADR 0007 puts `w-full` on
every text-like input. A select for a country code beside a text input for the number should not
each take half the width. If sharing the width needs a layout utility that is not yet in the class
test, ADR 0003 has it added there by name. #16 and #18 are open on which utilities are allowed.

ADR 0005 keeps Django's ids for help text and errors, and Django writes `aria-describedby` on
each input itself. FR-016 should need no new id, only each member's help text and error element
drawn under the join with the ids they already have.

A formset drawn as a table applies no layout and names each input by `aria-label`, so neither
part of this feature should reach it. Confirm that a form-wide floating label leaves the table
unchanged.

Decision records are expected for the floating label as a new kind of choice, including the
fallback for a disabled field, and for the joined group as a second layout object the package
defines. `decisions.md` D2, D4, D6 and D7 hold the reasoning.
