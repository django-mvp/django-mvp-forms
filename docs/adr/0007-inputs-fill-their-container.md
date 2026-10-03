# ADR 0007 — Inputs fill their container

**Status:** accepted

## Decision

Every text-like input and textarea the pack draws carries Tailwind's `w-full`, so it is as wide as
the field frame that holds it. The frame is a one-column grid and needs no class of its own for
the input to stretch.

A width the developer sets wins. When the widget's own `class` holds an unprefixed width utility,
such as `w-40` or `w-1/2`, the pack leaves `w-full` out and that class is the only width on the
input. A width for one breakpoint, such as `md:w-40`, sits beside `w-full`, which stays as the
width below that breakpoint.

`w-full` is named in the class test's list of allowed layout utilities. No test asserts how wide
an input is.

## Why

daisyUI gives `input` and `textarea` a fixed width of 20rem and has no modifier for a full-width
one. Left alone, a form on a wide page is a narrow strip, and an input in a row of columns would
not fill its column.

This is the case ADR 0003 allows a Tailwind utility for: layout, where daisyUI has no component or
modifier for the job. It works on a page using daisyUI's documented CDN install, which loads
Tailwind's browser build beside the stylesheet. On a page with no Tailwind at all the class does
nothing and the input keeps daisyUI's width.

The developer's width has to replace the pack's and not sit beside it. Two width utilities on one
element are settled by their order in the stylesheet, which neither the developer nor the pack
controls.

## Revisit if

daisyUI gains a modifier for a full-width input, at which point the pack uses it and drops the
utility.
