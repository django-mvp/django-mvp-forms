# ADR 0032 — Text the pack writes is drawn in the theme's content colour

**Status:** accepted

## Decision

Text the pack colours by its own choice is drawn in `base-content`. Help text, the label of a
single checkbox, the labels in a radio or checkbox group, attached text, table headers, tabs and
the text of the error alert carry `text-base-content`. Field errors, the required marker and a
table row's errors carry no colour class. A radio draws its ring and dot in the text colour around
it, so the class on a group's labels reaches them too. The dismiss button the pack puts in an
alert is a plain button, whose text passes on every alert's fill.

A class is written as a repair only when it brings a pairing up to the standard under every
shipped theme. The pack never repaints a control with a utility, and never writes a colour or a
variant as a repair: those are the developer's to state.

An error is marked by the input's error modifier, by `aria-invalid`, by where the message sits
and by the tinted alert at the top of the form, and not by the colour of its text.

## Why

daisyUI draws `label` text at 60% of the text colour and a tab that is not chosen at 50%. That
falls short of 4.5 to 1 under 15 to 33 of the 35 themes. The theme's error colour as text falls
short under 21. `base-content` passes on `base-100` and on `base-200` under all 35. At 90% it
still passes everywhere and at 80% it does not, so no muted grade is worth keeping.

`border-base-content` on an input would pass, but it paints over daisyUI's own drawing with a
utility, and the pack's inputs would stop looking like the rest of a daisyUI site (ADR 0003).
No colour modifier passes under every theme, and a colour is a choice the developer makes
(ADR 0021).

## Revisit if

daisyUI raises the contrast of `label` text or of its error colour across its themes, so that
the muted and the red text pass on their own.
