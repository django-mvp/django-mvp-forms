# ADR 0031 — A rating's colour is daisyUI's colour class on each star

**Status:** accepted

## Decision

daisyUI's rating has size modifiers and no colour modifier. A rating takes its size as a
modifier of the element that holds the stars, such as `rating-sm`, and its colour as daisyUI's
background colour class on each star, such as `bg-primary`. The input that clears a rating takes
neither.

The colour row for a rating in `Modifiers.colors` holds those eight classes, `bg-neutral` to
`bg-error`, written out in full like every other row. A rating in error is drawn without the
chosen colour and with `bg-error` on each star.

A rating has no variant, as daisyUI gives it none.

## Why

The request was that a rating takes the same size and colour choices as every other input.
Colouring each star with a background class is how daisyUI's own documentation colours a
rating, because a star is a masked element and its background is its colour.

The eight classes are in daisyUI's CDN stylesheet and in `tests/data/daisyui-classes.txt`, they
follow the host project's theme, and they need no build step. So they pass the test
[ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md) sets for what the pack may
write, although they are not modifiers of the rating itself. An arbitrary colour utility would
not pass it.

Leaving a rating with no colour was rejected: a form-wide colour would be passed over and a
field's own would raise, which fails the one thing the request asked for by name.

The error colour is written the same way so that a rating in error is marked as every other
input is, with the error as the only colour it shows
([ADR 0021](0021-size-is-shared-colour-and-variant-are-held-twice.md)).

## Revisit if

daisyUI gives the rating colour modifiers or an error modifier of its own.
