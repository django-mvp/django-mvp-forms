# ADR 0047 — One mask widget for each kind of mask, taking what can be written as data

**Status:** accepted

## Decision

There is a widget for each kind of IMask mask that can be described from Python:
`PatternMaskInput`, `RegexMaskInput`, `NumberMaskInput` and `DynamicMaskInput`. Each takes only
the options of its own kind, as keyword arguments, and refuses a value that cannot be right with
a `ValueError` that names the option, when the form class is defined.

An option is supported when its value is text, a number, true or false, a list, or a regular
expression written as text. An option whose value is a JavaScript function is not supported:
function masks, `prepare`, `prepareChar`, `commit`, `validate`, `dispatch`, `format` and `parse`.
The four widgets take no function, so none of them is a date widget: IMask's date mask needs two
of those functions for any format but its default. A date is a pattern whose day, month and year
are `RangeBlock`s. A partial date has a widget of its own, `PartialDateMaskInput`, described under
[Partial dates](https://github.com/django-mvp/django-mvp-forms#partial-dates).

A developer who needs one of those options listens for the `mvp-forms:imask` event, which carries
the IMask instance.

`PatternMaskInput`, `RegexMaskInput` and `DynamicMaskInput` hand the field the text as typed.
`NumberMaskInput` hands it the number with no thousands separator and a full stop as its decimal
mark, and writes an initial value with its own decimal mark. The widgets add no validation.

## Why

IMask's kinds of mask share almost no options. One widget for all of them would take either a
dictionary of IMask's options, which checks nothing and puts a JavaScript interface into Python,
or a long list of arguments of which most combinations mean nothing. Django separates
`TextInput`, `NumberInput` and `EmailInput` the same way.

Options travel to the browser on the input, as data. A function cannot make that trip unless the
package invents a way to name JavaScript from Python, and a developer who needs one is already
writing JavaScript.

A mask helps the person typing and is never what makes the data valid, so what the form does with
the text is the field's business. Removing a pattern's fixed characters on the server would mean
reading IMask's pattern language in Python. The number is the exception because `1 234,56` is not
text a `DecimalField` accepts, and the rule for it is one sentence that needs none of IMask's
logic. It runs on the server so that it holds when IMask is absent.

## Revisit if

A project needs a function option often enough that the event is a burden, or IMask's date mask
becomes usable with data alone.
