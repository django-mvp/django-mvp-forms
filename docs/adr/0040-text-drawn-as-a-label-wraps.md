# ADR 0040 — Text drawn with daisyUI's label class wraps, by one Tailwind utility

**Status:** accepted

## Decision

Help text, the label of a single checkbox, the label of each option in a radio or checkbox group
and the label of a file input's removal checkbox carry Tailwind's `text-wrap` utility beside
daisyUI's `label` class. They wrap onto as many lines as they need.

Text attached before or after an input also carries `label`, and does not carry `text-wrap`. It
stays on one line.

A checkbox or radio beside a label of several lines stays centred against them, as daisyUI aligns
it. The pack writes no alignment utility there.

`text-wrap` is named in `LAYOUT_UTILITIES` in `tests/test_pack/test_independence.py`, as ADR 0003
asks. `tests/test_pack/test_wrapping.py` reads every form state the pack draws and fails when an
element carrying `label` outside an input's wrapper has no `text-wrap`.

## Why

daisyUI's `label` sets `white-space: nowrap`. That suits a caption beside an input. It does not
suit a sentence under one: a help text of about 120 characters made its form 768 pixels wide on a
390 pixel page, and a long option label did the same
([issue #133](https://github.com/django-mvp/django-mvp-forms/issues/133)).

`<p class="label">` under an input is daisyUI's documented markup for help text in a fieldset, and
a `<label class="label">` around a checkbox is its markup for one, so the class stays (ADR 0003,
ADR 0011). The pack ships no stylesheet, so the repair has to be a class on the element. daisyUI
has no class that lets a label wrap, which is the case ADR 0003 allows a Tailwind utility for.

Two utilities do the job on a page that loads daisyUI's CDN build with Tailwind's browser build:
`whitespace-normal` and `text-wrap`. Both were measured in a browser at 390 pixels against
daisyUI 5.0 and 5.7, and both bring the page back to 390. `text-wrap` is also in the stylesheet
django-mvp already ships, and `whitespace-normal` is not, so with `text-wrap` a django-mvp project
is repaired by upgrading this package alone. ADR 0009 chose its utilities on the same ground.

`text-wrap` needs a browser that knows the CSS property of that name: Chrome 114, Firefox 121 or
Safari 17.4. On an older one the text stays on one line, as it did before.

Top-aligning the input with `items-start` was weighed for labels of several lines. A daisyUI
checkbox is taller than a line of the label's text, so it would sit the text of every one-line
label above the middle of its checkbox, which is the common case. Lining the input up with the
first line alone needs a rule of the pack's own, and the pack ships none.

Attached text sits inside the input's own border, where daisyUI sizes it to the input's height. A
unit or a currency symbol is short, and wrapping one would break the input's shape.

## Revisit if

daisyUI lets `label` text wrap by itself, or gains a class for help text. Or django-mvp's
stylesheet stops shipping `text-wrap`. Or a real form needs attached text long enough to wrap.
