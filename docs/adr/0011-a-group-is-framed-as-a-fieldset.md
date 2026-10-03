# ADR 0011 — A field of several inputs is framed as a fieldset, and a checkbox sits in its label

**Status:** accepted

## Decision

The field frame, `daisyui/field.html`, draws one of three shapes. It chooses from the field's
widget and from nothing in the page's context.

- **A group.** When Django marks the widget as a group (`BoundField.use_fieldset`: a radio group,
  a checkbox group, a date drawn as three selects), the frame is a
  `<fieldset class="fieldset">` and the field's label is its
  `<legend class="fieldset-legend">`. The fieldset carries `aria-describedby` naming the help
  text and the error element, whichever are drawn. With labels turned off it carries
  `aria-label` holding the label's text.
- **A single checkbox.** The frame is the `div`, and the checkbox sits inside a
  `<label class="label">` tied to it by `for`, followed by the label's text and the required
  marker.
- **Every other field.** The `div` with a `label` above the input, as ADR 0006 describes.

The ids do not change in any shape: `div_<auto_id>` on the frame, `<auto_id>_helptext` and
`<auto_id>_error` inside it. The frame still reads only the four context names ADR 0006 lists.

This amends ADR 0006, which said the frame's outer element is always a `div`.

## Why

A radio group has no single input for a `label` to point at, and Django gives one no `for`.
Its options have to be announced as one group named by the field's label. A native fieldset and
legend do that with no ARIA, they are what Django's own form templates draw for these widgets,
and they are daisyUI's own markup for the two classes the frame already used.

ADR 0006 fixed the element so that it could never be read from a page variable. That reason
stands. `use_fieldset` is Django's flag on the widget, which the page cannot set.

A single checkbox inside its label is daisyUI's documented markup for one, and it makes the
whole line something a person can click.

Django withholds its own description from a group's inputs, because it copies a group's
attributes onto every option. So the description goes on the fieldset.

## Revisit if

A layout object needs a group drawn without a fieldset, or a supported Django version changes
which widgets set `use_fieldset`.
