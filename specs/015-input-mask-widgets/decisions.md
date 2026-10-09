# Decisions: Input mask widgets for IMask

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer confirmed the reading of the feature and its coverage on 2026-10-09. Everything below
that he did not rule on directly is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. One widget for each kind of mask

**Chosen:** four widgets: pattern, regular expression, number, and a choice between several masks.

**Why:** IMask's kinds of mask share almost no options. A number mask has a decimal mark and a
scale, a pattern has definitions and blocks, a regular expression has neither. One widget for all
of them would take either a raw dictionary of IMask options, which checks nothing and puts a
JavaScript interface into Python, or a long list of named arguments of which most combinations
are meaningless. A widget for each kind takes only its own options by name and can refuse a wrong
one when the form is defined. Django separates `TextInput`, `NumberInput` and `EmailInput` the
same way.

**Confirmed by the maintainer.**

**ADR:** yes.

## D2. What is supported is what can be written as data

**Chosen:** every IMask option whose value is text, a number, true or false, a list, or a regular
expression written as text. No option whose value is a JavaScript function.

**Why:** options travel from Python to the browser on the input, as data. A function cannot make
that trip without the package inventing a way to name JavaScript from Python, and the developer
who needs one is already writing JavaScript. US-6 gives that developer the IMask instance.

IMask's date mask is left out by the same rule. Any format but its default needs a `format` and a
`parse` function. A pattern whose day, month and year are number-range blocks masks a date with
data alone, and Django's `DateField` reads the result through `input_formats`.

**Confirmed by the maintainer.**

**ADR:** yes, with D1.

## D3. A pattern submits what is shown, and a number submits a number

**Chosen:** pattern, regular expression and choice widgets hand the field the submitted text as it
is. The number widget removes the thousands separator and writes the decimal mark as a full stop.

**Why:** a mask is a help to the person typing. What the form does with the text is the field's
business, and a field that wants a phone number without its brackets already has `clean` for
that. Removing a pattern's fixed characters on the server would mean reading IMask's pattern
language in Python, a second implementation that could disagree with the first.

The number is different in kind. `1 234,56` is not text a `DecimalField` accepts, so without this
the number widget could not be used on the fields it exists for. The rule is simple enough to
state in one sentence and needs none of IMask's logic.

The rule runs on the server and not in the browser on submit, so it holds when IMask is absent
and cannot be skipped by a script that fails. Its cost is the edge case the spec records: on a
page with no IMask, a person must type the number the way the widget would have shown it.

**Stated to the maintainer as the assumption he was most likely to correct. He did not.**

**ADR:** yes.

## D4. The package ships a script, and the pack still needs none

**Chosen:** one script, named in each widget's media. No inline script, no inline handler. ADR
0041 is edited where it says the pack ships no script file so that it reads true: the pack's
templates need none.

**Why:** ADR 0014 and ADR 0041 protect one promise, that a page loading daisyUI and nothing else
draws every form the pack can draw. These widgets are not the pack. A developer names one on a
field on purpose, and Django's media is the ordinary way a widget brings its script. A project
that uses none never loads it.

A file was chosen over inline script so that a strict Content Security Policy needs no exception,
which is the limit ADR 0041 had to accept for the modal and the alert.

**ADR:** yes.

## D5. No server validation

**Chosen:** the widgets add no validator and change none.

**Why:** a widget that validated would have to run the developer's JavaScript regular expression
in Python, or read IMask's pattern language, and either would sometimes disagree with the
browser. A developer who needs the shape enforced writes a validator in the dialect the server
runs.

**ADR:** no. The README states it.

## D6. An event carries the IMask instance

**Chosen:** the script sends an event from each input once its mask is applied.

**Why:** it is the route for everything D2 leaves out, at the cost of one line in the script. It
was put to the maintainer as a suggestion and he neither took nor refused it, so it is included as
the lowest-priority story, where it can be cut without touching the others.

**ADR:** no.

## D7. No widgets for particular formats

**Chosen:** no phone, IBAN or postcode widget.

**Why:** each is one line with the pattern widget, and the right pattern depends on the country.
Recommended to the maintainer, who did not object.

**ADR:** no.

## D8. IMask is not added to the support window

**Chosen:** the README names the major version of IMask the widgets are written for. The support
window of FS-013 is unchanged.

**Why:** the window promises that every version it names is tested. The package installs nothing
of IMask's and the suite has no browser, so a version named there would be a promise nothing
checks. If planning gives the suite a browser, this can be revisited then.

**ADR:** no.
