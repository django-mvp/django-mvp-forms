# Research: Partial date field

Written after the prototype was approved, against the main of 2026-10-10, which carries FS-015.
The maintainer's planning notes are answered first, by name. Then each line of `sketch.md` under
"What the screens need from the code" and "What the sketch faked" that needs more than building.

## The maintainer's planning notes

### 1. A regex or pattern IMask widget

**Adopted, as a pattern with a rule of its own.** The masked widget is IMask's pattern mask
`Y-M-D` with three range blocks. A pattern alone cannot know that February is short or that a
date is too early, so the package's script adds IMask's `validate` option, which is given the
whole value on every keystroke and refuses the keystroke by returning false. A regular
expression mask was not adopted: it cannot place the hyphens for the person.

### 2. A multi-widget on a daisyUI join

**Adopted.** `forms.MultiWidget` with a template of the package's that wraps the parts in an
element classed `join`. The pack already draws a multi-widget's parts as the inputs and selects
they are, each with its size and colour (FS-004), so the pack's templates do not change.

### 3. The partial date package

**Adopted as stated: no dependency.** The field returns ISO text, which is what that package's
model field reads.

### 4. One field with a swappable widget

**Adopted.** One class, `PartialDateField`. Every option is a keyword of the field, and the three
widgets take `attrs` and nothing else. R3 below is how the field tells its widget.

### 5. A select for the year

**Adopted, as a third widget.** `PartialDateSelect` subclasses `PartialDateInput` and replaces
one part. An option on `PartialDateInput` was not adopted, because note 4 asks that changing
widget be one name and nothing else, and an option on a widget is a second thing to carry over.

## R1. Padding a single digit

The prototype pads `4` to `04` by overriding `_appendCharRaw` on a subclass of IMask's range
block, a method IMask does not document. IMask documents two options for changing what was typed
before it is masked: `prepareChar`, called for each character, and `prepare`, called for each
insertion. Both were tried in Chrome against IMask 7.6.1, with plain range blocks.

- `prepareChar` returning `04` for `4` fills the month, but the day typed next is then refused.
- `prepare` returning `04` for `4` works for typing in order: `20214` gives `2021-04` and
  `202149` gives `2021-04-09`.
- `prepare` fails for a change in the middle of a value, whether or not it is limited to what
  the person typed (`flags.input` set and `flags.tail` not). IMask puts the text after the cursor
  back one character at a time and gives up the whole insertion when two characters arrive for
  one. With `2021-12-14` typed, selecting the month and typing `4` gives `2021-1`: the month is
  changed and the day is lost. With `2020-02-29` typed, replacing the last digit of the year with
  `1` gives `2020-`. Sent unnoticed, either cleans to a date the person did not enter.
- The prototype's subclass gives `2021-04-14` for the first and leaves `2020-02-29` for the
  second, which is what FR-012 asks: a digit is refused and nothing is corrected.

**Chosen: the subclass of the range block stays.** It is the one way found that pads and keeps a
change in the middle whole. The cost is a dependence on a method of IMask's that is not in its
guide, so the browser tests of T003 pin each behaviour it gives, and the README names the IMask
version the widget is tested against. A pasted partial date with one-digit parts is padded in
`prepare`, which is called once for a paste at the end of the input and has no text after the
cursor to put back: `2021-3-4` pasted into an empty input gives `2021-03-04`.

## R2. A masked input holding a value its mask refuses (FR-042)

IMask sets the input to as much of the value as its mask takes when it is created. To show what
was sent, the script tries the value before it creates the mask: it builds IMask's masked object
from the options with `IMask.createMask`, resolves the input's value through it, and compares.
Where they differ the input is left alone, and a listener on its `input` event tries again each
time the person changes it. The first time the value resolves to itself the mask is created and
the listener is removed. An empty input always resolves to itself.

This applies to the partial date mask only. The four mask widgets of FS-015 are not changed.

## R3. How the field tells its widget what was stated

The prototype set three attributes on the widget in the field's `__init__`. A developer who
swaps the widget afterwards, as `self.fields["collected"].widget = PartialDateSelect()` in a
form's `__init__`, got a widget that knew nothing, and the demo told it again by hand.

Django gives a field one documented hook that runs once for each form, the first time the form reads
the field: `Field.get_bound_field(form, field_name)`. **Chosen:** the field overrides it, sets
`resolution`, `min_value` and `max_value` on `self.widget`, and returns what `super()` returns.
Each form holds its own copy of the field and of the widget, so nothing is shared between forms.
Nothing is set in `__init__`. A form keeps what the hook returned, so a widget is swapped before
the form is first drawn or validated, which is where a form's `__init__` does it. A widget used with no partial date field keeps its class defaults:
a resolution of day and no limits.

Setting plain attributes on the widget is what Django's own fields do with `is_required` and
`is_localized`. `widget_attrs` was not used: it runs once in `__init__`, and it can only add
HTML attributes, which cannot remove the day part from a multi-widget.

## R4. Options that leave a list

The prototype set `hidden` and `disabled` on a month or day that cannot be chosen. Safari ignores
`hidden` on an `option`, so the person would see a greyed day, which the maintainer ruled
against. **Chosen:** the script keeps each select's full list of options the first time it meets
it, in a `WeakMap`, and puts into the select only those that can be chosen, in their order. A
held option that cannot be chosen is kept while the form is first shown (FR-022).

## R5. A typed year outside the limits

A text input has no minimum. With a typed year outside the limits the month stays closed, and
the field's error says which date was crossed when the form is sent. Nothing more is built. A
developer who wants the person stopped earlier names `PartialDateSelect`, whose list holds only
years inside the limits. The README says so.

## R6. The year list's default reach

Counted from `datetime.date.today()` each time the widget is drawn, so a long-running process
does not keep last year's list. This is the behaviour FR-040 asks for and is not a fake.

## R7. Two scripts that know the calendar

`imask.js` and `partial-date.js` each hold the same few lines: the length of a month, and a
partial date read as a number. The three-part widget must work on a page that loads no IMask and
no mask script (FR-020), so neither script can lean on the other. The lines are repeated, under
Article III.

## R8. Translations

`mvp_forms/locale/en/LC_MESSAGES/django.po` exists. The field's error messages and the three
part names are new strings, wrapped with `gettext_lazy`, and the catalogue is regenerated with
`makemessages` in the task that adds each. Month names come from `django.utils.dates.MONTHS`,
which Django translates.

## R9. Testing the scripts

FS-015 settled it (ADR 0046): a script is tested in Chrome through `pytest-playwright`, in a
module marked `e2e` and declared in `non-mirror-paths`. The partial date mask's tests join
`tests/test_imask_e2e.py`. The three-part script gets `tests/test_partial_date_e2e.py`. Pages
for both come from `tests/urls.py` and `tests/forms.py`, as the mask pages do.

## R10. What FS-015 says about a date widget

Three places say there is none: FS-015's `spec.md` (the clarification and Out of scope), ADR
0047, and the README's "Input masks" section. Each is edited to say that the four widgets take
no function and that a partial date has a widget of its own, with a link. ADR 0047's decision
stands, so it is edited in place and not superseded.

## R11. No new dependency

Nothing is added to the package or to its development dependencies. `calendar.monthrange` and
`datetime` are the standard library's.
