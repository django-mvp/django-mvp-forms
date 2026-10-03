# ADR 0030 — Legibility is calculated from the theme's published colours

**Status:** accepted

## Decision

Whether a form can be read under a theme is settled by calculation, in the test suite, against
the minimum contrast WCAG 2.2 sets at level AA: 4.5 to 1 for text, and 3 to 1 for the part of a
control that shows what it is or what state it is in.

The colours come from daisyUI's own `themes.css` for the pinned version, kept verbatim in
`tests/data/daisyui-themes.css` beside the class list and refreshed with it. Every theme in that
file is checked.

`tests/legibility/` draws every form state the pack has, and a reader walks the markup with the
text colour and the surface inherited down the tree. One table, `Reader.paints`, says what each
daisyUI class the pack writes does to them. A class with no row stops the suite. The contrast
maths is written there too, with no dependency. A see-through colour is laid on its surface
before it is clipped to what a screen can show, which is what a browser paints.

The parts of a control held to 3 to 1 are the border of an input, a select, a textarea and a file
input, the border of a checkbox or radio that is off, a toggle that is off, the mark and fill of
each when on, the arrow of a select and of an accordion group, and the bar under the chosen tab.
A button is held by its text. The dimmed content of a disabled control is measured and reported
and is not held. Nothing the pack draws is large text, so every piece of text is held to 4.5.

## Why

A host project is most likely to be held to level AA itself, and it is a calculation, which a
test needs. Level AAA would put most of daisyUI's themes in the list of exceptions. A newer
perceptual measure is not yet a published standard.

Judging pages by eye cannot be repeated when daisyUI changes a theme. A headless browser reading
computed styles would need a browser in continuous integration. Evaluating daisyUI's stylesheet
itself would need a CSS engine. Reading the markup through a table is the smallest thing that
measures what the pack really drew. A hand-written list of pairings would measure the list.

The table is a reading of daisyUI's stylesheet for one version. It was compared with what a
browser paints for that version, and the colours agree to within one step in 255.

A colour library would have been a development dependency pinned in this package alone, where
development tooling comes from the shared bundle. The maths is short and is held by fixed
vectors.

WCAG exempts a disabled control, and daisyUI dims one from the `disabled` attribute (ADR 0013),
so holding it to the figure would list every theme and say nothing.

## Revisit if

The pinned daisyUI version moves: the rows of `Reader.paints` are re-read with it. Or daisyUI
draws text at 24px or more, which brings in the figure for large text. Or the shared bundle
gains a colour library.
