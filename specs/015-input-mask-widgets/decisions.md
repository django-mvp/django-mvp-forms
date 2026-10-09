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
checks. The browser tests of D12 run against one copy of IMask, 7.6.1, and that is what the
README names.

**ADR:** no.

## D9. The script acts once, however often a page includes it

**Chosen:** the script sets a flag the first time it runs and returns at once on every later run.

**Why:** django-crispy-forms writes a form's media inside every form drawn with `{% crispy %}`.
The prototype's page held the script eight times and gave every input eight masks, which a field
with a display character cannot survive. The specification's edge case said Django's media loads
the script once. That holds only where the page template renders the media, and the edge case,
FR-025 and SC-002 were edited to say what happens. The maintainer was told when the fault was
found and approved the prototype afterwards.

**ADR:** docs/adr/0045-mask-widgets-bring-one-script-that-acts-once.md

## D10. A placeholder character for each definition

**Chosen:** `placeholder_char` takes one character for the whole pattern, or a mapping from a
definition's character to the character shown for it.

**Why:** the maintainer ruled at the prototype that a placeholder has to say what each position
takes, and a row of dots or underscores does not. IMask allows it on a definition, so it costs no
blocks. FR-006 and a scenario of US-1 were edited.

**ADR:** none. It is one option of one widget, described in the README.

## D11. A display character's field submits what was typed

**Chosen:** the script sets the field's entry in the form's data to the mask's value.

**Why:** IMask writes the display characters into the input, so without this a PIN field submits
dots. The option was kept in scope with this fix, since the specification already promised it and
the fix is a few lines on a standard browser event. FR-017 and a scenario of US-1 were edited.

**ADR:** docs/adr/0045-mask-widgets-bring-one-script-that-acts-once.md

## D12. The script is tested in Chrome

**Chosen:** browser tests with the Playwright already among the development tools, launching the
installed Chrome, skipped where it is absent and failing in CI.

**Why:** the fault of D9 passed a simulated DOM and was found by a person typing. django-mvp
already tests its scripts this way. Chrome is launched by channel because this repository's test
workflow does not download Playwright's own browsers and the workflow is outside this feature.

**ADR:** docs/adr/0046-the-mask-script-is-tested-in-a-browser.md

## D13. Blocks are small classes, and the widgets keep their names

**Chosen:** `RangeBlock`, `EnumBlock` and `PatternBlock`. `PatternMaskInput`, `RegexMaskInput`,
`NumberMaskInput` and `DynamicMaskInput`. Options are IMask's names in Python spelling, with
`min_value` and `max_value` for the number bounds.

**Why:** a block has options that should be named and checked as a widget's are, and `from`
cannot be a Python argument. The widget names follow Django's `...Input`.

**ADR:** none. The README is the record of the names.

## D14. An initial number is written in the widget's own format

**Chosen:** `format_value` writes the decimal mark the widget states and no thousands separator.

**Why:** written in plain form, `1234.5` in a field whose thousands separator is a full stop is
read back as `12345` on a page without IMask. Written as `1234,5` it round-trips with or without
IMask, and the script needs no special case for numbers.

**ADR:** none. Local to the number widget.

## D15. What the design review changed

One reviewer read the plan before any of it was built. Everything it found was taken:

- A thousands separator equal to the decimal mark in force is refused, including a comma stated
  with no `radix`, where IMask's default mark is also a comma. An initial 1234.5 would otherwise
  be saved as 12345.
- The form's data is corrected for every masked input and not only where a display character is
  seen, because a pattern inside `DynamicMaskInput` hides its display character from the outer
  mask.
- IMask's built-in definitions are read from `IMask.MaskedPattern.InputDefinition`.
- The first task also moves the demo's forms, so the suite is green at its end.
- One test module, `tests/test_widgets.py`, as the testing standard asks for one source module.
- A page under a policy that forbids inline script is one of the browser tests.
- The number bounds take an `int`, a `float` or a `Decimal`.
- The demo and the README load an exact version of IMask with an integrity value.

**ADR:** none. Each is a correction to the plan and is recorded where it applies.

## D16. A definition is written as text, or as an object when it carries a placeholder character

**Decision:** in `data-imask`, `definitions` maps a character to its expression as text. Where a
placeholder character is stated for the definition, it maps to an object holding `mask` and
`placeholderChar`. A built-in definition (`0`, `a`, `*`) with a placeholder character maps to an
object holding `placeholderChar` alone, and the script reads its expression from IMask.

**Why:** the plain case stays what the approved prototype wrote, so the script that is on the
branch keeps working between the first task and the second. Nothing is written that was not
stated.

**Revisit if:** the script ever needs one shape for every definition. Then every definition is an
object.

## D17. Every refused option is a `ValueError`, including a value of the wrong type

**Decision:** a `blocks` that is not a mapping, a block that is not one of the three classes and
a definition whose expression is not text raise `ValueError` naming the option, through one
helper that carries the one `noqa: TRY004` for it.

**Why:** the specification asks for one error that names the option for every refusal, and a
caller catching it should not need two.

**Revisit if:** the maintainer prefers Python's `TypeError` for a wrong type, which is a change
in that helper alone.

## D18. The script keeps only the pattern kind, the observer and the event until their own tasks

**Decision:** the rewritten script has no branch for a regular expression, a number or a list of
masks, and nothing that reads a number's plain value. It keeps the observer of added nodes and
the event, which the pattern tests do not exercise on their own.

**Why:** the three kinds are rebuilt test-first by the stories that bring their widgets, and a
branch with no widget and no test would be untested code on the branch. The observer and the
event are the script's own shape, and their stories take the red step by removing them.

**Revisit if:** a story needs the script to carry a kind before its widget exists.

## D19. The browser tests count masks through the event

**Decision:** the test that a page holding the script three times gives each input one mask
counts the `mvp-forms:imask` events the script sends, and compares them with the inputs that
carry `data-imask`.

**Why:** IMask keeps no handle on the input, so the event is the one place a count can be read
from. Every mask the script applies sends one.

**Revisit if:** the event is dropped or sent more than once for an input by design.

## D20. The demo's sentence about the price stays until the number story restores the field

**Decision:** the formset section's sentence on the Input masks page still names the price field
and its number widget, although the field is out of the form until the number story. Only the
article half of that sentence changed, to state the pattern `aa-0000`.

**Why:** the page's markup and wording are what the maintainer approved, and the number story puts
the field back as it was, so the sentence is true again when it does. Taking the sentence out
now would leave that story a template edit it does not list.

**Revisit if:** the number story is dropped or delivered separately from this one. Then the sentence
goes with the field.

## D21. The demo loads IMask at an exact version with the integrity value of the published file

**Decision:** both demo pages and the README's example load
`https://cdn.jsdelivr.net/npm/imask@7.6.1/dist/imask.min.js` with an `integrity` of
`sha384-UO8YwPv//GjwHj93ZlwXcDNjv3BSxdBFUB2jtiOuL3d/a0kS9E8sYvHjTBkQI8u8` and `crossorigin`.

**Why:** the hash is that of the copy of 7.6.1 kept under `tests/data/`, which is the file the
npm package ships. No request was made to the CDN while building, so the hash is not read from
what the CDN serves.

**Revisit if:** a browser refuses the file on either page. Then the CDN's copy differs and the hash
is read from it.

## D22. A regular expression's flags are checked against the eight JavaScript has, and no further

**Decision:** `RegexMaskInput` refuses `flags` that is not text and any character outside `dgimsuvy`,
naming `flags`. It does not refuse a repeated flag or `u` and `v` together, which JavaScript's own
`RegExp` refuses in the browser. The expression is never compiled in Python.

**Why:** the plan lists "a character JavaScript does not have" as what is refused. Telling the
combinations apart is JavaScript's rule to keep, and a copy of it in Python would drift.

**Revisit if:** a repeated flag reaches a page often enough to matter. A bad combination makes the
script throw while building that input's options.

## D23. The regular expression's section of the demo restores its form with the view

**Decision:** `RegexMaskForm` is restored in `demo/forms.py` exactly as at the approved prototype,
with its three fields, labels and help text, and the view's list of widgets gains its entry again.

**Why:** the section's markup comes from the view's list, so the entry alone would have no form
to draw. `demo/forms.py` is not among the files `tasks.md` names for this task, and the brief
names the restoration of the form as part of it.

**Revisit if:** none.
