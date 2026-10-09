# Sketch: Partial date field

A prototype of the field and both widgets on a demo page, built so the maintainer can judge the
two inputs by eye before anything is planned. It has no tests. The screen is what was reviewed.
The code behind it is the plan's to keep, change or rebuild.

## What exists

- **Mask widgets (FS-015).** `MaskInput` writes its options on the input as JSON and names
  `mvp_forms/imask.js` in its media. The script turns that data into IMask options. It passes
  plain data only, so it has no place today for a rule that depends on what was typed earlier.
- **Multi-widget fields (FS-004).** The pack draws any `forms.MultiWidget` inside one fieldset
  with one legend, one help text and one set of errors. It classes each part as an input or a
  select, with the size, colour and error modifier that apply, on a copy of the widget. A part
  keeps any class and `aria-label` it already has.
- **Joined groups (FS-011).** `Join` is a layout object for several fields. A multi-widget is one
  field, so it cannot be a `Join`. The join here is daisyUI's `join` class on an element around
  the parts.
- **The demo.** Each feature has a page with a section per case, then states, sizes, a formset
  with a row added in the browser, and a modal. The input mask page is the closest model.
- **No field exists yet.** The package has shipped widgets and layout objects only.

## What the screens need from the code

- A field that cleans a year, a year and month, or a full date to padded ISO text, and reports a
  separate error for each way a value can be wrong: a bad year, a bad month, a day the month does
  not have, a month with no year, a day with no month, too coarse, too fine.
- The field passes its finest precision and its earliest and latest dates to whichever widget it
  is given. A widget takes none of them from the developer, so a field changes widget by changing
  one name.
- An earliest and a latest date on the field, each a partial date or a Python date. A value is
  accepted when a day it could stand for lies on or between them, so `1998` passes an earliest
  date of `1998-03-15` and `1998-02` does not. The error names the date that was crossed.
- A third widget: the three parts with a select for the year. Its years run from the earliest
  date's year to the latest's. Where one is not stated they end at this year and reach a hundred
  years back. A year that was sent and is not on the list is still shown.
- The masked input refuses a digit from which no allowed date could follow. With a latest date of
  `2004-09`, typing `2004-1` keeps `2004-`.
- In the three-part widgets a year outside the limits leaves the month closed, the months on
  offer are those with an allowed day in the year, and the days on offer are the allowed days.
  A month or day that a change of year puts outside the limits is cleared.
- The element around the parts carries the earliest and latest dates for the script.
- The masked input pads a single-digit month or day that can only be the whole part: typing `4`
  as a month gives `04`. A digit that could still start a valid part is left alone.
- The masked input refuses a digit, and never corrects one. `13` as a month keeps the `1`.
- The masked input asks a touch device for a numeric keypad.
- The three-part widget draws the year as a text input holding four digits, and the month and the
  day as selects whose first option is empty and names the part.
- The three-part widget leaves only the year required in the browser, so a year alone can be
  submitted from a required field.
- Each part carries its own name for assistive technology: Year, Month, Day.
- A form drawn again after a failed submission shows what was sent, including a day the month
  does not have and a day with no month. The script leaves a part that holds a value alone until
  the person changes something.
- A widget template that wraps the parts in the join. It is a new template of the package's.
- The script for the three parts acts on parts added to the page later.

## What the sketch faked

- The masked input pads by overriding a method of IMask's range block that IMask does not
  document. Research R1 tried IMask's published options and found none that keeps a change in
  the middle of a date whole, so the override stays and browser tests pin it.
- When a masked input is drawn again holding a value the mask would refuse, such as `2021-02-30`,
  IMask shows as much as fits (`2021-02-0`) beside the field's error. The specification now says
  it shows what was sent (FR-042).
- The field tells the widget what was stated by setting three attributes on it, the way Django's
  own fields set `is_required`. A widget swapped in after the form is built has to be told again,
  which the demo does by hand.
- The three-part widget with a typed year does nothing to a year outside the limits but keep the
  month closed. The person learns why only from the field's error after sending.
- The select widget's hundred years are counted from the server's date when the form is drawn.
- Error wording is a first draft and has no translations.
- The page has no version outside the django-mvp shell, which every other demo page has.
- Nothing is in the README, the template list, the glossary or the decision records. Two tests
  fail on this branch because of it: the one that compares the template list with the package,
  and the one that says the package's static directory holds one stylesheet and one script.
- Nothing new has a test.

## What was ruled by eye

Decisions of taste made for the first round. The maintainer's rulings are added below as he gives
them.

- The three parts sit at their natural width and do not stretch across the form: a year wide
  enough for four digits, then the two selects.
- The empty option of each select names its part, so the group reads Year, Month, Day when empty.
- A month or day that cannot be chosen yet is shown disabled. It is not hidden.
- At a finest precision of month the day is not drawn at all, and at year only the year is drawn.
- Days beyond the month's length are removed from the list. They are not shown greyed out.
- Months and days outside the earliest and latest dates are removed in the same way.
- The year select lists the latest year first.
- The year select's empty option reads Year, as the other two name their parts.

Rulings from the maintainer:

- 2026-10-10: the first round "all looks pretty good". He asked for a select for the year, an
  earliest and latest date followed by the field and the widgets, and confirmed that a field may
  leave the day out altogether.
- 2026-10-10: approved. The option that states the finest precision is named `resolution`.
