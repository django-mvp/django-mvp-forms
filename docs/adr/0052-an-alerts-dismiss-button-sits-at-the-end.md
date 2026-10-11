# ADR 0052 — An alert's dismiss button sits at the end, by one Tailwind utility

**Status:** accepted

## Decision

The dismiss button of an `Alert` carries Tailwind's `ms-auto` utility after its `btn` classes. It
sits against the end of the alert: the right under left-to-right text and the left under
right-to-left. The alert's content stays at the start.

`ms-auto` is named in `LAYOUT_UTILITIES` in `tests/test_pack/test_independence.py`, as ADR 0003
asks. No test asserts where the button sits. That is judged on the demo pages.

## Why

daisyUI's alert is a grid. With two children its columns are `auto minmax(auto, 1fr)` and every
child starts at the start of its column. daisyUI's documented alert with buttons has three
children, an icon, the text and the buttons, so the text takes the wide column and the buttons
land at the end. The pack's alert has no icon. Its content took the narrow column and the button
started the wide one, 16 pixels after the last word and, on a 988 pixel alert, 676 pixels from
the end ([issue #166](https://github.com/django-mvp/django-mvp-forms/issues/166)).

daisyUI has no class that moves a child of an alert to the end, which is the case ADR 0003 allows
a Tailwind utility for. Two were weighed:

- `justify-self-end` says what is meant most directly. django-mvp's packaged stylesheet does not
  contain it, so the button would have stayed where it was on a django-mvp page.
- `ms-auto` gives the button an automatic margin on its starting side, which takes up the free
  space of its column. It is in both Tailwind's browser build and django-mvp's packaged
  stylesheet, so a django-mvp project is repaired by upgrading this package alone. ADR 0009 and
  ADR 0040 chose their utilities on the same ground.

Both pages of the demo were measured in Chrome, inside the django-mvp shell and with daisyUI's CDN
build alone, at 1280 and 320 pixels and in both directions. The button ends at the alert's
padding in all of them. At 320 pixels the content wraps beside the button and the page does not
scroll sideways, as before.

Wrapping the button in a `<div>`, as daisyUI's example does for several buttons, was weighed. It
needs the same utility, and the button's `onclick` would have to change, which a host project
that allows the handler by its hash would have to follow (ADR 0041).

Adding daisyUI's `alert-vertical sm:alert-horizontal`, which stacks the content and the button on
a narrow page, was left out. Nothing asked for it and the alert already fits at 320 pixels.

## Revisit if

daisyUI gains a class for an action at the end of an alert, or changes the alert's grid so that a
second child ends its column. Or django-mvp's stylesheet stops shipping `ms-auto`. Or the pack
draws an icon in an alert, which would put the content in the wide column.
