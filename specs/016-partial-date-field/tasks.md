# Tasks — 016 Partial date field

**Branch**: `016-partial-date-field` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. `mvp_forms/fields.py`, the three
partial date widgets in `mvp_forms/widgets.py`, their template, both scripts' partial date code
and the demo page are on the branch from the approved sketch, with no tests. A task rebuilds the
part it names test-first: the tests are written, seen to fail with the prototype's code for that
part removed or broken, and seen to pass once it is written again to the plan. Prototype code a
later task owns is left working until that task, so the demo page answers after every task. A
task is done when its tests pass, the tree is green and the work is committed. Documentation
lands in the task that introduces what it describes.

What the maintainer approved on screen is not changed: the demo page's sections, their order,
its fields and its help text. The planned differences are the three the plan lists under "The
demo". A test that cannot pass without changing anything else on that page is reported, not made
to pass.

No test asserts wording, a colour, a width or a class used only for looks. A field test asserts
the cleaned value or the error's code. A widget test asserts the attribute's JSON, the parts
drawn, the media and what the field receives. A browser test asserts what this package's scripts
do and never IMask's own masking rules beyond what shows the options arrived.

Code standards for every task: no leading-underscore names; line length 88; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. `mvp_forms/fields.py` and `mvp_forms/widgets.py`
import Django and the standard library only. `CONSTITUTION.md` and everything under `.github/`
do not change. A document reads as current state. README links are absolute. Every `ValueError`
names the option at fault, and every `ValidationError` is raised with a `code`.

## Decision records

Written at convergence, after the last story, with numbers read from `origin/main` at that
moment. No task writes one. T003 edits ADR 0047 in place where it says there is no date widget.

## Order

**US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree.**

---

## US1 — A developer adds a partial date field to a form (P1)

Issue: #160. Delivers FR-001 to FR-010, FR-028 to FR-030, FR-033; SC-001, SC-004 to SC-006.

### T001 — The field and its rules

**Files**: `tests/test_fields.py` (new), `tests/test_pack/test_partial_dates.py` (new),
`tests/forms.py`, `mvp_forms/fields.py`, `mvp_forms/locale/en/LC_MESSAGES/django.po`,
`README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *The field*; research R8.

- `PartialDateField` cleans a year, a year and month, or a full date to padded ISO text, and an
  empty value to `""`. One-digit months and days are padded. A trailing hyphen is dropped.
  Surrounding space is dropped.
- Each way a value can be wrong raises its own code: `invalid`, `year`, `month`, `day`,
  `no_year`, `no_month`. The cases: text that is not a date, more than three parts, a year not of
  four digits, the year `0000`, a month or day of `00`, a month above 12, a day the month does
  not have, the 29th of February outside a leap year, a month with no year, a day with no month,
  a value cut off inside a part.
- Every date that exists is accepted and every one that does not is refused: one parametrised
  test walks every month of a leap year and of a year that is not, with the last day and the day
  after it.
- `prepare_value` shows a `datetime.date` as ISO text, and a bound field with an initial partial
  date shows it.
- `required`, `disabled`, `validators` and a developer's own `error_messages` behave as on a
  `CharField`.
- With no widget named the field is drawn through the pack as any text input, taking a stated
  size, colour and variant, and its form's media names no script.
- The options `coarsest`, `resolution`, `min_value` and `max_value` are T006's and T007's. The
  prototype's code for them stays until then and gains no test here.
- README: the section "Partial dates" opens with the field: the values accepted and returned,
  the error codes, and how the text is handed to a model. CHANGELOG entry. `CONTEXT.md` gains
  partial date and precision, and the sense of part. The English catalogue is regenerated.

---

## US2 — A person types a partial date into one masked input (P1)

Issue: #161. Delivers FR-011 to FR-014, FR-027, FR-031, FR-042; SC-002 to SC-004.

### T002 — The masked widget

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_partial_dates.py`, `tests/forms.py`,
`mvp_forms/widgets.py`, `README.md`

Plan, *The widgets*.

- `PartialDateMaskInput` takes `attrs` and nothing else. `data-imask` holds the kind
  `partial-date` and a resolution of `day`. It asks for a numeric keypad unless the developer's
  `attrs` state an `inputmode`, keeps the developer's `attrs`, and names `mvp_forms/imask.js` in
  its media.
- Drawn through the pack it is a daisyUI `input` that takes a stated size, colour and variant,
  and the same attribute is drawn through Django's own rendering.
- On a field that is not a partial date field it draws and submits text.
- README: the masked widget, what the page must load, and what it does without IMask.

### T003 — The partial date mask, tested in Chrome

**Files**: `tests/test_imask_e2e.py`, `tests/urls.py`, `tests/forms.py`, `tests/templates/`,
`mvp_forms/static/mvp_forms/imask.js`, `specs/015-input-mask-widgets/spec.md`,
`docs/adr/0047-one-mask-widget-for-each-kind-of-mask.md`, `README.md`

Plan, *The scripts*; research R1, R2 and R10.

- Typing digits places the hyphens. A digit that would make the month 0 or above 12 is refused.
  A digit that would make a day the typed month does not have is refused, and February takes 29
  only in a leap year.
- A single digit that can only be the whole month or day is padded, through IMask's `prepare`
  option. The subclass of IMask's range block is removed. A pasted `2021-3-4` gives `2021-03-04`.
- Stopping after the year or the month and submitting sends that value, and the form is valid.
- An initial `2021-03` is shown as `2021-03`.
- An input drawn holding `2021-02-30` shows `2021-02-30`, and is masked once the person has
  changed it to a value the mask takes (FR-042).
- An input added to the page later is masked. A page without IMask raises no error and submits.
- A full date whose year is then changed so the day no longer exists submits and the field
  reports the error.
- The limits and the resolution in the mask are T006's and T008's.
- FS-015's specification, ADR 0047 and the README's "Input masks" section stop saying there is
  no date widget, as research R10 words it.

---

## US3 — A person enters a partial date as a year, a month and a day (P2)

Issue: #162. Delivers FR-015 to FR-022, FR-032, FR-039, FR-040; SC-002 to SC-004, SC-007.

### T004 — The three-part widgets and their template

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_partial_dates.py`,
`tests/test_pack/test_template_list.py` (unchanged, must pass), `tests/forms.py`,
`mvp_forms/widgets.py`, `mvp_forms/templates/mvp_forms/widgets/partial_date.html`, `README.md`

Plan, *The widgets*.

- `PartialDateInput` takes `attrs` and nothing else. Its parts submit under names ending
  `_year`, `_month` and `_day`. A year alone, a year and month, and all three clean to the padded
  ISO text. A day with no month and a month with no year reach the field and are refused with
  `no_month` and `no_year`.
- An initial partial date or `datetime.date` fills the parts it has and leaves the rest empty.
- Through the pack: one fieldset whose legend is the label, one help text, one set of errors,
  the parts inside one element carrying `data-partial-date`, each part with its `aria-label` and
  `data-partial-date-part`, and each taking a stated size, colour and variant. Only the year
  carries `required`.
- A form drawn again after a refused submission shows in each part what was sent, including the
  30th of February and a day with no month.
- A developer's `attrs` reach every part. Through Django's own rendering three working controls
  are drawn.
- `PartialDateSelect` draws the year as a select and is otherwise the same. With no limits its
  years run from this year back a hundred, latest first, and a held year not on the list is
  still an option. The years under a `min_value` and `max_value` are T007's.
- The widgets' media names `mvp_forms/partial-date.js`.
- README: both widgets, and the template in the template list.

### T005 — The three parts kept in step, tested in Chrome

**Files**: `tests/test_partial_date_e2e.py` (new), `tests/test_pack/test_independence.py`,
`tests/urls.py`, `tests/forms.py`, `tests/templates/`, `pyproject.toml` (`non-mirror-paths`),
`mvp_forms/static/mvp_forms/partial-date.js`, `README.md`

Plan, *The scripts*; research R4 and R7.

- No month can be chosen before the year has four digits, and no day before a month is chosen.
- The days offered are the days of the chosen month, and February offers 29 only in a leap year.
  Days that cannot be chosen are not in the list.
- A chosen 31st is cleared when the month becomes February, and a chosen 29th of February when
  the year stops being a leap year. Nothing is moved to another day.
- The same holds with the year as a select.
- A group drawn holding the 30th of February, or a day with no month, shows what was sent until
  the person changes a part.
- A group added to the page later behaves the same. The script included twice acts once.
- A page that does not load the script offers twelve months and 31 days, and submits.
- The page loads no IMask, and the script works.
- The static-directory test names the stylesheet and both scripts.
- README: what the script does and what the widgets do without it.

---

## US4 — A developer sets how precise a partial date must be (P3)

Issue: #163. Delivers FR-023 to FR-026, FR-041; SC-006.

### T006 — Coarsest precision and resolution

**Files**: `tests/test_fields.py`, `tests/test_widgets.py`,
`tests/test_pack/test_partial_dates.py`, `tests/test_imask_e2e.py`, `tests/forms.py`,
`mvp_forms/fields.py`, `mvp_forms/widgets.py`, `mvp_forms/static/mvp_forms/imask.js`,
`demo/partial_date_forms.py`, `README.md`

Plan, *The field* and *The widgets*; research R3.

- `coarsest="month"` refuses a year alone with `needs_month`, and `coarsest="day"` refuses
  anything but a full date with `needs_month` or `needs_day`.
- `resolution="month"` refuses a full date with `too_fine_day`, and `resolution="year"` refuses a
  month with `too_fine_month`.
- A precision that is not one of the three, and a `resolution` coarser than `coarsest`, raise
  `ValueError` naming the options when the form class is defined.
- The field tells its widget through `get_bound_field`: a field drawn with each of the three
  widgets, and a field whose widget is replaced in the form's `__init__`, all follow the
  resolution. Two forms of one class with different widgets do not affect each other.
- At a resolution of month the masked input's `data-imask` says so and the input takes no day in
  Chrome. The three-part widgets draw no day part, and at year draw the year alone.
- A widget on a field that is not a partial date field keeps a resolution of day.
- The demo's help text says `resolution=`, and its forms stop telling their widgets by hand.
- README: the two options and what each widget does with the resolution.

---

## US5 — A developer sets the earliest and latest date a field accepts (P3)

Issue: #164. Delivers FR-034 to FR-038; SC-008.

### T007 — The limits on the field and in what the widgets draw

**Files**: `tests/test_fields.py`, `tests/test_widgets.py`,
`tests/test_pack/test_partial_dates.py`, `tests/forms.py`, `mvp_forms/fields.py`,
`mvp_forms/widgets.py`, `mvp_forms/templates/mvp_forms/widgets/partial_date.html`, `README.md`

Plan, *The field* and *The widgets*.

- `min_value` and `max_value` each take a year, a year and month, a full date or a
  `datetime.date`.
- With `min_value="1998-03-15"`: `1998`, `1998-03` and `1998-03-15` are accepted, and `1997`,
  `1998-02` and `1998-03-14` are refused with `min_value`, the limit in the error's `params`. The
  mirror cases hold for `max_value`, and a limit given to the month counts to its last day.
- A limit that is not a partial date, and a `min_value` later than `max_value`, raise
  `ValueError` naming the option when the form class is defined.
- The masked input's `data-imask` carries `min` and `max` where stated and not otherwise. The
  three-part widgets' element carries `data-partial-date-min` and `data-partial-date-max` where
  stated and not otherwise.
- `PartialDateSelect` lists the years from the latest limit's year down to the earliest's, and
  the three cases of a missing limit follow the plan.
- A form drawn again after a date outside the limits was sent shows what was sent in every
  widget.
- README: the two options and how a partial value is compared with a limit.

### T008 — The limits in the browser, and the demo

**Files**: `tests/test_imask_e2e.py`, `tests/test_partial_date_e2e.py`, `tests/test_demo.py`,
`tests/urls.py`, `tests/forms.py`, `mvp_forms/static/mvp_forms/imask.js`,
`mvp_forms/static/mvp_forms/partial-date.js`, `demo/`, `README.md`

Plan, *The scripts* and *The demo*; research R5.

- Masked, with limits of `1998-03-15` and `2004-09`: `1997` keeps `199`, `19980314` keeps
  `1998-03-1`, `19980315` is taken whole, and `200410` keeps `2004-0`.
- Three parts, same limits: 1997 leaves the month closed. 1998 offers March to December, and
  March offers the 15th onward. 2004 offers January to September.
- A chosen month or day that a change of year puts outside the limits is cleared.
- The same holds with the year as a select, whose list holds 1998 to 2004.
- The demo page keeps what was approved, with the plan's three differences, and gains a
  standalone version without django-mvp. `tests/test_demo.py`: both pages answer, each widget's
  section is present, and a post returns what each field received.
- README: what each widget does with the limits, and the note on a typed year (research R5).
