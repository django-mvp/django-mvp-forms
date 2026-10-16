# ADR 0056 — The coordinate kind checks its bounds in its own validate and never hands them to IMask

**Status:** accepted

## Decision

`CoordinateMaskInput` writes `min` and `max` into `data-imask`, and the script's `coordinate`
kind reads them into its own `validate`. They are never passed to IMask as `min` and `max`. The
`validate` refuses a value when nothing that can still be typed after it lies between the bounds,
so `3` is refused under 40 to 60 while `4`, `45` and `45.5` are taken. An empty value, or a lone
`-` while the lower bound is below zero, is always taken.

An input drawn holding a value the mask would cut, such as `51.50740123` at six decimal places,
waits unmasked and shows the value whole until the person changes it, as the partial date's does
([ADR 0050](0050-the-partial-date-mask-has-a-rule-of-its-own.md)). A value outside the bounds
that the script's `validate` refuses is treated the same way. The field refuses what is posted,
with `min_value`, `max_value` or `max_decimal_places`, and nothing is rounded or clamped.

## Why

IMask's number mask clamps the value to `min` and `max` on every commit: when the mask attaches,
on every blur and when the value is set. A stored `35` under 40 to 60 would be shown and posted
as `40`, and a typed `4` would become `40` on leaving the input. Either posts a place the person
never entered and the field accepts it.

Its `min` and `max` also refuse a digit that is merely on the way to a value: with a lower bound
of 40, the first digit `4` is below it. A check that asks whether any continuation lies inside
the bounds has no such problem and needs the bounds in the script's own function.

Leaving the clamp out means what the person typed is what is posted, and the field, which holds
the rule, says what is wrong with it.

## Revisit if

IMask gains a number option that refuses a value without changing it, or a new IMask version
fails the browser tests that pin this behaviour.
