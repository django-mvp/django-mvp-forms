# ADR 0067 — Form text is sized and shaded with Tailwind utilities

**Status:** accepted. Extends [ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md): `text-base` joins the named utilities in the class test

## Decision

`mvp_forms.layout.FormText` draws a passage of text between fields in a `<div>`, rendered as a
template against the page's context, as a `Fieldset` legend is. It takes two options:

- `size`: none, `"small"` or `"large"`, drawn as `text-sm`, `text-xs` and `text-base`
- `variant`: none or `"muted"`, drawn as `text-base-content` and `text-base-content/90`

A `Fieldset`'s description is drawn through the same template with neither option, so a host
project that replaces `daisyui/layout/form_text.html` changes both.

## Why

daisyUI has no text component with sizes or shades. Its `label` class, which help text uses, is
for the text of one field, and fades it to 60%. Form text is about the form or a group of fields
and is meant to be more prominent than help text, so it is drawn at the size of the text in an
input by default, one step down for small print and one step up for an introduction.

The muted shade was chosen against the pack's legibility check. At 70%, the shade first tried, the
text falls below 4.5 to 1 on the page or on a fieldset's panel under 7 of daisyUI's 35 themes, and
at 80% under 2. At 90% it meets 4.5 to 1 under all of them. The README promises that every piece
of text the pack colours by its own choice can be read under every built-in theme, and a muted
shade is the pack's choice. `text-base-content/90` is also a class in daisyUI's published
stylesheet, so only the size `text-base` is a new utility in the class test.

The variant's name is `muted` and not one of daisyUI's colour names, because it is a shade of the
text colour. Colours for form text were left for later.

## Revisit if

daisyUI adds a text component with sizes or shades, or the pack takes colours for form text.
