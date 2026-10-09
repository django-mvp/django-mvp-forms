# Research: Input mask widgets for IMask

Written after the prototype was approved, against the main of 2026-10-09, which carries FS-014.
There is no `planning-notes.md` for this feature. Each line of `sketch.md` under "What the screens
need from the code" and "What the sketch faked" is answered below by number.

## R1. What the pack already does for a text input subclass

`FieldInput.components` maps `forms.TextInput` to `input`, and the lookup is by `isinstance`, so a
widget that subclasses `TextInput` is drawn as a daisyUI `input` with the size, colour and variant
choices applied and with `w-full`. Nothing in the pack changes. The prototype confirmed it: a
masked input stated `primary` and `ghost` is drawn `input input-primary input-ghost w-full`.

The widgets write their options through `build_attrs`, which every rendering path calls: the
pack, another crispy pack, and Django's own form rendering. FR-016 needs nothing more.

## R2. How options reach the script

One attribute, `data-imask`, holding JSON. Django escapes attribute values, so a pattern holding
a quote or an angle bracket cannot leave the attribute (FR-014). The JSON uses IMask's own option
names, so the script passes most of it through, and adds a `kind` so the script knows which of
IMask's constructors to use. Three things cannot be JSON and are rebuilt by the script:

- a regular expression, sent as its source and flags and rebuilt with `new RegExp`
- `Number`, `IMask.MaskedRange` and `IMask.MaskedEnum`, named by `kind`
- a definition, sent as its source and optional placeholder character

An option the developer did not state is left out of the JSON, so IMask's default applies
(FR-013).

## R3. The Python interface

Answers "the widgets take their options under provisional names" and "a pattern's blocks are
written as plain dictionaries".

- The widgets keep their prototype names: `PatternMaskInput`, `RegexMaskInput`, `NumberMaskInput`
  and `DynamicMaskInput`, in a new module `mvp_forms.widgets`. Django names its own text inputs
  `...Input`.
- Options are keyword-only arguments under the Python spelling of IMask's names: `lazy`,
  `placeholder_char`, `overwrite`, `eager`, `display_char`, `scale`, `thousands_separator`,
  `radix`, `map_to_radix`, `pad_fractional_zeros`, `normalize_zeros`, `autofix`. The number
  bounds are `min_value` and `max_value`, as on Django's number fields, because `min` and `max`
  are builtins. `attrs` stays where Django puts it.
- An option the widget does not have is a `TypeError` from Python itself, which names it. A value
  that cannot be right is a `ValueError` whose message names the option (FR-003).
- A block is an instance of one of three small classes: `RangeBlock(minimum, maximum)`,
  `EnumBlock(values)` and `PatternBlock(mask)`. `from` is a Python keyword, which rules out
  IMask's own names for a range's bounds. A block of another type is refused. `PatternBlock`
  takes `repeat`. Classes were chosen over dictionaries so a block's options are named arguments
  that are checked, the same as a widget's.
- `DynamicMaskInput` takes a list of the other three widgets. A developer who knows how to write
  one mask writes the list with no second vocabulary.

## R4. A placeholder that says what each position takes

Answers "a placeholder that says what each position takes".

IMask has one `placeholderChar` for a pattern, but a definition may be written as an object with
a `placeholderChar` of its own, and that overrides the pattern's. Checked against IMask 7.6.1:
`aa-0000` with the digit definition given `#` and the letter definition given `a` shows
`aa-####`. `placeholder_char` therefore accepts either one character for the whole pattern or a
mapping from a definition's character to its placeholder character:
`placeholder_char={"0": "#", "a": "a"}`. For one of IMask's three built-in definitions the script
reads the expression from `IMask.PatternInputDefinition.DEFAULT_DEFINITIONS`, so the package never
copies IMask's own expressions. No blocks are needed. A block keeps a `placeholder_char` of its
own, which the date example uses.

## R5. The number round trip

Answers "a number widget whose submitted value reaches a field as a plain number, and whose
initial value is shown with the stated separators".

`value_from_datadict` removes the thousands separator and writes the decimal mark as a full stop
(FR-018, FR-020). The defaults it assumes when an option is not stated are IMask's: no thousands
separator and a comma.

The prototype drew an initial value in plain form and had the script hand it to IMask as an
unmasked value. That fails without IMask: `1234.5` in a field whose thousands separator is a full
stop is read back as `12345`. `format_value` instead writes the value with the widget's decimal
mark and no thousands separator, `1234,5`. IMask reads that as typed text and adds the
separators, and without IMask the same text round-trips through `value_from_datadict` unchanged.
The script needs no special case for numbers. `format_value` does not localise, because the
widget's own options say how the number is written.

## R6. The script is on the page once for each form

Answers "the script acts once however many times a page includes it".

`FormHelper.include_media` is true by default, and `{% crispy %}` then writes the form's media
inside the form. A page with eight forms holds the script tag eight times. `|crispy` and Django's
own rendering write no media, and the page template renders it. The script therefore sets a flag
on `window` the first time it runs and returns at once on every later run.

Two consequences for the documentation. A page whose forms are drawn with `{% crispy %}` needs
IMask and nothing else. The script tag sits inside the form, usually before the tag that loads
IMask, so the script waits for the document to finish loading before it looks for IMask.

## R7. A display character and what the form receives

Answers "a field with a display character submits what was typed".

IMask writes the display characters into the input, so the browser would submit them. The script
listens for the form's `formdata` event and sets the field's entry to the mask's value. The event
fires for a native submit and for any script that builds a `FormData` from the form, which is how
htmx reads a form. A disabled input is left out, as the browser leaves it out.

## R8. Inputs added later

`MutationObserver` on the document, watching added nodes. It covers a formset row added by any
script, an htmx swap and a modal built in the browser, with no dependency on any of them
(FR-025). A `WeakMap` from input to mask stops a second mask on the same input and lets a removed
input be collected.

A formset's `empty_form` is drawn through the same widget, so it carries the same attribute.

## R9. Testing the script

Answers the specification's open assumption.

`pytest-playwright` is already installed through the shared test extras, and django-mvp has the
convention: tests marked `e2e` in files named `*_e2e.py`, skipped where no browser is found and
failing in CI. This repository's test workflow does not ask for Playwright's browsers and the
workflow is not this feature's to change. The tests launch the installed Chrome
(`channel="chrome"`), which GitHub's Ubuntu runners carry and which is present locally.

The tests open pages of the test project through pytest-django's `live_server`. IMask is served
to them from a copy under `tests/data/`, by intercepting the request for it, so no test needs the
network. The copy is test data: the wheel and the sdist hold `mvp_forms`, the README and the
licence, so IMask is not distributed (FR-029). IMask is MIT licensed.

What the browser tests assert is this package's script: that a mask is applied with the options
written on the input, once, to inputs present and added later, that nothing happens without
IMask, that the event is sent, and that a display character's field submits what was typed. They
do not test IMask's own masking rules beyond one keystroke that shows the options arrived.

## R10. What changes in the existing suite

One test fails on the branch: the package's static directory holds only `tomselect.css`. It is
widened to name the script too. No other test fails with the prototype in place: 5128 pass.

## R11. The constitution and the decision records

- Article XII lists widgets as in scope, and Article XV asks for the class, its template, its
  tests and its README entry in one pull request. These widgets use Django's own input template.
- Article XIV is about stylesheets and classes and is untouched.
- Article XIII: the module imports Django only.
- ADR 0014 and ADR 0041 say the pack ships no script file. ADR 0041 is edited so that it reads
  true, and a new record states the decision (FR-033).
- `CONSTITUTION.md` and everything under `.github/` do not change.

## R12. What the specification now says differently

Found while the prototype was built and reviewed, and edited into `spec.md` and `decisions.md`:

- The script is included once for each form drawn with `{% crispy %}` and acts once.
- A placeholder character may be stated for each definition.
- A field with a display character hands the form what was typed.
- The script's behaviour is tested in a browser.
