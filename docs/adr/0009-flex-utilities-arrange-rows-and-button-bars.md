# ADR 0009 — Tailwind flex utilities arrange rows and button bars

**Status:** accepted

## Decision

A `Row` is drawn with `flex flex-col gap-4 md:flex-row`, and a `Column` with `flex-1 min-w-0`. The
columns stack on a narrow page and sit side by side, in equal shares, from Tailwind's `md`
breakpoint. `ButtonHolder`, `FormActions` and the buttons added to a form helper are drawn with
`flex flex-wrap gap-2 mt-4`.

The developer's classes are written after the pack's on the same element. Each utility is named
in `LAYOUT_UTILITIES` in `tests/test_pack/test_independence.py`. No test asserts how a row is
arranged. That is judged on the demo pages.

## Why

daisyUI has no grid or column component, and none for a line of buttons outside a card or a
modal. ADR 0003 allows a Tailwind utility for layout in exactly that case.

Three ways to arrange a row were weighed:

- A grid with automatic columns gives equal columns for any number of them. django-mvp's packaged
  stylesheet does not contain those utilities, so the columns would have stacked on a django-mvp
  page, which is the first host project this pack has.
- A grid with a fixed column count needs the number of columns, which a template cannot know
  without counting them in Python.
- Flex gives equal shares for any number of columns, and every utility it needs is in both
  Tailwind's browser build and django-mvp's packaged stylesheet.

`min-w-0` lets a column shrink below the width of what it holds, so a long input does not push
its neighbours off the row. A `Column` outside a `Row` carries two utilities that do nothing
there. A field placed straight in a `Row`, with no `Column`, is still drawn, at the width of its
content.

This is the working answer to
[issue #18](https://github.com/django-mvp/django-mvp-forms/issues/18), which stays open for the
maintainer to confirm.

## Revisit if

The maintainer picks another option on issue #18, daisyUI gains a layout component, or django-mvp's
stylesheet stops shipping one of these utilities.
