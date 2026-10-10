# ADR 0050 — The partial date mask is a fifth mask widget, with a rule of its own in the script

**Status:** accepted

## Decision

`PartialDateMaskInput` stands beside the four mask widgets of
[ADR 0047](0047-one-mask-widget-for-each-kind-of-mask.md). A developer states no mask and no
function. The shape is fixed, and the calendar and the limits are checked by the package's
script through IMask's `validate` option.

The month and day blocks subclass `IMask.MaskedRange` and override `_appendCharRaw`, so that a
single digit that can only be the whole part is given its leading zero. IMask's `prepare` option
pads only a pasted date.

An input drawn holding a value the mask would cut is left unmasked, showing the value whole,
until the person has changed it to one the mask takes.

## Why

ADR 0047 left out a date widget because IMask's date mask needs functions a developer cannot
write in Python. Here the developer writes none, so that reason does not apply, and the four
widgets still take plain data only.

IMask's published options for changing what was typed, `prepare` and `prepareChar`, were both
tried for the padding. Each loses part of the value when a person changes the middle of a date:
with `2021-12-14` typed, replacing the month with `4` gave `2021-1`. Sent unnoticed, that is a
date the person did not enter. The subclass keeps the rest of the value and refuses a change that
would leave the day without a date.

`_appendCharRaw` is not in IMask's guide. The browser tests pin each behaviour that rests on it,
and the README names the IMask version they run against.

A value the field refused is shown beside its error. Cutting it to what the mask takes would
show the person a date they did not send.

## Revisit if

IMask gains a published way to pad a range block, or a new IMask version fails the browser
tests.
