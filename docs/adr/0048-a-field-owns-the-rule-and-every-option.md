# ADR 0048 — A field owns the rule and every option, and its widgets take none

**Status:** accepted

## Decision

Where the package offers a value with rules of its own, a form field owns those rules and every
option a developer states. `PartialDateField` is the first. It holds what a partial date is, the
coarsest precision and the resolution, and the earliest and latest date, and it validates on the
server whatever drew the input.

The widgets beside it, `PartialDateMaskInput`, `PartialDateInput` and `PartialDateSelect`, take
`attrs` and nothing else. A variation in how the value is entered, such as a select for the
year, is a widget of its own and not an option on another.

With no widget named the field is a plain text input and its form needs no script.

## Why

A widget does not validate. A rule stated on a widget would hold only while that widget's script
ran, and a form sent from a page without the script would be accepted.

With every option on the field, a developer changes how the value is entered by changing one
name. An option on a widget would be a second thing to carry across each time, and two widgets
could be given different limits for the same field.

## Revisit if

A widget needs an option that is about entry alone and has no meaning to the field, such as the
order in which years are listed.
