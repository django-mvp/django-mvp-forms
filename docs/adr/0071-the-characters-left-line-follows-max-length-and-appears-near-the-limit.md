# ADR 0071 — The characters-left line follows `max_length` and is shown from the start

**Status:** accepted

## Decision

`CharactersLeftInput` and `CharactersLeftTextarea` show how many characters are left under a
field. The limit is the field's own `max_length`, which Django writes on the control as
`maxlength`. A `maxlength` stated on the widget raises a `ValueError` when the form class is
defined, and a widget on a field with no `max_length` raises one naming the field when the form is
drawn.

The line is shown from the start and counts down as a person types. A developer can state
`show_from` for one widget, and the line is then hidden until that many characters or fewer are
left. A value that is not a whole number above zero raises a `ValueError` naming `show_from`.

The line says "n characters remaining". A value over the limit uses the same sentence with a
negative number, "-24 characters remaining", in the error colour, and is not cut.

The widget writes one pre-formatted sentence for each count from 0 to the smaller of the limit
and 199 in `data-characters-left-words`, so each is translated with the plural forms of the
language of the page. The script says a count of 200 or more with the sentence for
`100 + count % 100`, its number replaced by the count. Every gettext plural formula chooses the
form from `n % 10`, `n % 100` and exact values below 100, so a count of 100 or more and
`100 + count % 100` always take the same form. A test proves this against the plural formula of
every catalogue Django ships, for counts up to 5000. A count over the limit takes the same path,
and one with no sentence of its own, over a limit smaller than the count, takes the last sentence
written.

The script counts as the browser's `maxlength` counts, in UTF-16 code units, so the field stops
taking characters exactly when the line says none are left.

## Why

A second limit stated on the widget would let the line and the browser promise more or less than
the field accepts, and `maxlength` is already on the control.

A line that appears only near the limit gives a person no sign that a limit exists until they are
close to it, and a field drawn full, near the limit, shifts the page when the line appears. A
line that is there from the start tells a person the room they have before they write, and leaves
the layout still. A developer for whom it is noise on a short field states `show_from`.

Writing one sentence for every count up to a long limit would make the control's attributes
large. A person has to read a number only in the language's own plural form, and the form repeats
every hundred, which is why 200 sentences are enough for any limit.

Counting by code point, as Django's validation does, leaves a person with an emoji in their text
stopped by the browser while the line still says some characters are left. A count in code units
is never smaller than a count by code point, so a text the line says fits is still accepted when
it is submitted.

## Revisit if

A setting that lets a person create an option by typing it is added to the package's Tom Select
widgets, where the limit would be the length of a new option's text.
