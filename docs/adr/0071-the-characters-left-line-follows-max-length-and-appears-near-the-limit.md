# ADR 0071 — The characters-left line follows `max_length` and appears near the limit

**Status:** accepted

## Decision

`CharactersLeftInput` and `CharactersLeftTextarea` show how many characters are left under a
field. The limit is the field's own `max_length`, which Django writes on the control as
`maxlength`. A `maxlength` stated on the widget raises a `ValueError` when the form class is
defined, and a widget on a field with no `max_length` raises one naming the field when the form is
drawn.

The line is hidden until `show_from` characters or fewer are left. The package's number is
`CHARACTERS_LEFT_FROM`, 8, and a developer can state another number for one widget. A value that
is not a whole number above zero raises a `ValueError` naming `show_from`.

The script counts as the browser's `maxlength` counts, in UTF-16 code units, so the field stops
taking characters exactly when the line says none are left.

## Why

A second limit stated on the widget would let the line and the browser promise more or less than
the field accepts, and `maxlength` is already on the control. A count that is always shown is
noise on a field that is nowhere near its limit.

Counting by code point, as Django's validation does, leaves a person with an emoji in their text
stopped by the browser while the line still says some characters are left. A count in code units
is never smaller than a count by code point, so a text the line says fits is still accepted when
it is submitted.

## Revisit if

A setting that lets a person create an option by typing it is added to the package's Tom Select
widgets, where the limit would be the length of a new option's text.
