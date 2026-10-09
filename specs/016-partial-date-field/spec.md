# Feature Specification: Partial date field

**Feature Branch**: `016-partial-date-field`

**Created**: 2026-10-09

**Status**: Draft

**Serves**: G11 (the package offers its own fields and widgets, each looking native beside the
pack's own inputs) and G4 (the variant, colour and size of any form component can be set from
Python)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #132

**Depends on**: nothing still to be delivered. It builds on the mask widgets and their script
(FS-015), the joined group (FS-011), the drawing of a multi-widget field (FS-004) and the size,
colour and variant choices of FS-007.

**Input**: Research data often records a date to the year or the month only, because that is all
the source says. A developer should be able to put a field on a form that accepts a year, a year
and month, or a full date, and hands back the ISO text for whichever was given: `2021`, `2021-03`
or `2021-03-14`. The developer chooses between three widgets for it. One is a single masked text
input. One is a year, a month and a day side by side, with the year typed. The third is the same
three parts with the year chosen from a list. All of them keep a person from entering a date that
does not exist, or one outside the dates the developer allows, while they are still filling in the
form, and the field checks again on the server.

## Clarifications

### Session 2026-10-09

The maintainer confirmed the reading of the feature before this was written: a field that returns
ISO text, two widgets, precision that only drops from the right, checks in the browser backed by
the same checks on the server, and no dependency on any partial date package. The coverage scan
then found five ambiguities. Each was resolved from that conversation, the goals, the constitution
and the decision records. Longer rationale is in `decisions.md`.

- **Q: FS-015 says the package has no date widget, because IMask's date mask needs JavaScript
  functions that cannot be written in Python. How does a masked date input square with that?**
  A: FS-015's rule is about what a developer can state from Python, and it stands: the four mask
  widgets still take plain data only. This widget takes no mask from the developer at all. Its
  shape is fixed and the knowledge of the calendar lives in the package's own script. So it is a
  fifth widget beside the four, and FS-015's specification is brought up to date where it says no
  date widget exists. Recorded as FR-011, FR-012 and FR-031.

- **Q: Does the field accept `2021-3-4`, or only `2021-03-04`?**
  A: It accepts a month or day written with one digit and hands back the padded form. A person on
  a page without the script is typing into a plain text box, and refusing `2021-3-4` there helps
  nobody. The year is different: it must be four digits, because `21` could mean two different
  years. Whatever is accepted, what the form receives is always padded ISO text. Recorded as
  FR-003 and FR-004.

- **Q: A person types `2021-` into the masked input and moves on. Is that an error?**
  A: No. A hyphen with nothing after it is read as if it were not there, so `2021-` is the year
  2021 and `2021-03-` is March 2021. The hyphen is the mask's own doing as often as the person's.
  A value cut off inside a part, such as `202` or `2021-0`, is an error. Recorded as FR-005.

- **Q: In the three-part widget a person has chosen the 31st and then changes the month to
  February. What happens to the day?**
  A: The day is cleared, and the same happens when the year changes and the 29th of February no
  longer exists. Moving it to the 28th would submit a date the person never chose. Recorded as
  FR-018.

- **Q: Which calendar decides how long February is, and which years are allowed?**
  A: The one Python's own dates use: the Gregorian rules applied to every year from 0001 to 9999.
  Negative years, years beyond four digits and historical calendars are out of scope. Recorded as
  FR-002 and under Out of scope.

### Session 2026-10-10

The maintainer reviewed the prototype and asked for three things, and stated how the Python side
should be shaped.

- **Q: How does a developer ask for the year as a select?**
  A: By naming a third widget. It is the three-part widget with a select for the year, and it
  takes no options of its own. The years it offers come from the earliest and latest dates stated
  on the field. Recorded as FR-039 and FR-040.

- **Q: Can a developer state an earliest and a latest date?**
  A: Yes, on the field. Each is a partial date or a Python date. The field enforces them and every
  widget follows them. This reverses the earlier ruling that left them to a validator. Recorded as
  FR-034 to FR-038.

- **Q: A year alone is submitted to a field whose earliest date is `1998-03-15`. Is `1998`
  accepted?**
  A: Yes. A partial date stands for every day it could be, and it is accepted when at least one of
  those days is allowed. `1998` could be a day after 15 March, so it passes. `1998-02` could not,
  so it fails. Recorded as FR-035.

- **Q: Where does a developer state the options: on the field or on the widget?**
  A: On the field, all of them. There is one field, and a widget is named and nothing more. The
  field tells whichever widget it has the finest precision and the earliest and latest dates, so a
  developer changes from one widget to another by changing one name. Recorded as FR-041.

- **Q: Can a developer leave the day out altogether?**
  A: Yes, and this was already so: a finest precision of month. It is User Story 4.

- **Q: A masked input is drawn again holding a date its mask refuses, such as `2021-02-30` sent
  from a page with no script. What does it show?**
  A: What was sent, in full, beside the field's error. The mask is held off that input until the
  person has changed it to something the mask takes. Cutting the value to what fits would show
  the person a date they did not send. Self-resolved after the question was put to the maintainer
  twice with the prototype and left open. Recorded as FR-042.

- **Q: What is the option for the finest precision called?**
  A: `resolution`. The maintainer named it when he approved the prototype.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer adds a partial date field to a form (Priority: P1)

A developer has a value that is a date known to the year, the month or the day. They add the
partial date field to a form. Whatever a person submits, the form's cleaned data holds padded ISO
text for a date that exists, or the form reports an error on the field.

**Why this priority**: The field is the feature. It owns the rule for what a partial date is, and
both widgets depend on it. With this story alone a developer already has a working field drawn as
a text input.

**Independent Test**: Define a form with one partial date field, submit it with valid and invalid
values, and read the cleaned data and the errors. No script and no other story is needed.

**Acceptance Scenarios**:

1. **Given** a form with a partial date field, **When** it is submitted with a year, a year and
   month, or a full date, **Then** the cleaned data holds that value as padded ISO text.
2. **Given** such a form, **When** it is submitted with a month above 12, a day the month does
   not have, or the 29th of February in a year that is not a leap year, **Then** the field
   reports an error and the form is invalid.
3. **Given** such a form, **When** it is submitted with a month or day written with one digit,
   **Then** the cleaned data holds the padded form.
4. **Given** such a form, **When** it is submitted with a year of fewer than four digits, a month
   with no year, a day with no month, or text that is not a date, **Then** the field reports an
   error.
5. **Given** a partial date field that is not required, **When** it is submitted empty, **Then**
   the cleaned data holds empty text and the form is valid.
6. **Given** a required partial date field, **When** it is submitted empty, **Then** the field
   reports that it is required.
7. **Given** a field whose initial value is a partial date or a Python date, **When** the form is
   drawn, **Then** the input shows it as ISO text.
8. **Given** a partial date field with no widget named, **When** its form is drawn through the
   pack, **Then** it is drawn as the pack draws any text input, taking the size, colour and
   variant stated for the form or the field.

---

### User Story 2 - A person types a partial date into one masked input (Priority: P1)

A person filling in a form meets a single input for a date. They type digits and the hyphens
appear for them. They can stop after the year or after the month. They cannot type a month that
does not exist, or a day the month they typed does not have.

**Why this priority**: The need behind the feature is that a wrong date is stopped in the browser,
before the form is sent. This is the smaller of the two widgets to do that and builds directly on
the mask script the package already has.

**Independent Test**: Give the field the masked widget, load IMask and the form's media on a page,
and type into the input in a browser.

**Acceptance Scenarios**:

1. **Given** a page that loads IMask and the form's media, **When** a person types digits into
   the input, **Then** the separators between year, month and day are placed for them.
2. **Given** such a page, **When** a person types a digit that would make the month greater than
   12 or less than 1, **Then** the digit is not accepted.
3. **Given** a year and month already typed, **When** a person types a digit that would make a
   day the month does not have, **Then** the digit is not accepted. February allows 29 only when
   the year typed is a leap year.
4. **Given** such a page, **When** a person stops after the year or after the month and submits,
   **Then** the form receives the year or the year and month, and it is valid.
5. **Given** a bound form or an initial value holding a partial date, **When** the form is drawn
   on such a page, **Then** the value is shown under the mask at the precision it has.
6. **Given** a page that loads the form's media and not IMask, **When** a person types and
   submits, **Then** the input behaves as a plain text input, no error is raised in the browser,
   and the field validates what was sent.
7. **Given** an input of this widget added to the page after it has loaded, **When** a person
   types into it, **Then** it is masked as the others are.
8. **Given** a full date typed, **When** the person goes back and changes the year or the month
   so that the day no longer exists and submits, **Then** the field reports an error.

---

### User Story 3 - A person enters a partial date as a year, a month and a day (Priority: P2)

A developer gives the field the widget that asks for the three parts separately. A person sees
one labelled group holding a year, a month and a day. They enter a year, and may go on to pick a
month and then a day. The days on offer are the days that month has in that year.

**Why this priority**: It asks nothing of the person about format and makes the optional parts
plain to see. It is second because the field and the masked input already meet the need, and
this one adds a second script and a new drawing.

**Independent Test**: Give the field this widget, load the form's media on a page, and fill in
the three parts in a browser. Submit with one, two and three parts filled.

**Acceptance Scenarios**:

1. **Given** a field using this widget, **When** its form is drawn through the pack, **Then** the
   three parts are drawn as one joined group under the field's one label, with one help text and
   one set of errors, and each part is named for assistive technology as the year, the month or
   the day.
2. **Given** such a form, **When** it is submitted with only the year, the year and month, or all
   three parts, **Then** the cleaned data holds the padded ISO text for what was given.
3. **Given** a page that loads the form's media, **When** a person chooses a month, **Then** the
   days on offer are the days that month has, and February offers 29 only in a leap year.
4. **Given** a day already chosen, **When** the person changes the month or the year so that the
   day no longer exists, **Then** the day is cleared.
5. **Given** such a page, **When** no year is entered, **Then** a month cannot be chosen, and
   when no month is chosen a day cannot be chosen.
6. **Given** a bound form or an initial value holding a partial date, **When** the form is drawn,
   **Then** each part it has is shown in its place and the others are empty.
7. **Given** a form submitted with a day and no month, or a month and no year, as can happen on a
   page without the script, **Then** the field reports an error.
8. **Given** a field using this widget, **When** a size, colour or variant is stated for the form
   or the field, **Then** every part takes it.
9. **Given** a page that does not load the form's media, **When** the form is drawn and
   submitted, **Then** all three parts can be filled in, the month offers twelve months and the
   day offers 1 to 31, and the field validates what was sent.
10. **Given** a form whose submission failed on this field, **When** it is drawn again, **Then**
    each part shows what the person entered.
11. **Given** a field using the widget whose year is a select, **When** its form is drawn,
    **Then** the year is chosen from a list and the month and the day behave as they do beside a
    typed year.
12. **Given** such a field with no earliest or latest date stated, **When** its form is drawn,
    **Then** the years on offer run from this year back a hundred years.

---

### User Story 4 - A developer sets how precise a partial date must be (Priority: P3)

A developer has a field that must be known at least to the month, or one that is never recorded
to the day. They state the coarsest precision the field accepts and the finest. Both widgets
follow what was stated, and the field enforces it.

**Why this priority**: The first three stories cover a date of any precision, which is the common
case. This narrows it for the fields that need it.

**Independent Test**: Define fields with a coarsest precision of month and with a finest
precision of month, submit values at each precision, and draw each field with both widgets.

**Acceptance Scenarios**:

1. **Given** a field whose coarsest precision is month, **When** it is submitted with a year
   alone, **Then** the field reports an error on the missing month.
2. **Given** a field whose finest precision is month, **When** it is submitted with a full date,
   **Then** the field reports an error.
3. **Given** a field whose finest precision is month, **When** it is drawn with the masked
   widget, **Then** the input accepts no day. **When** it is drawn with the three-part widget,
   **Then** no day part is drawn.
4. **Given** a field whose finest precision is year, **When** it is drawn with either widget,
   **Then** only a year can be entered.
5. **Given** a field stated with a finest precision coarser than its coarsest, **When** the form
   class is defined, **Then** an error is raised that names the two options.
6. **Given** a field with nothing stated, **When** it is submitted at any of the three
   precisions, **Then** it is accepted.

---

### User Story 5 - A developer sets the earliest and latest date a field accepts (Priority: P3)

A developer has a field whose dates cannot fall before or after a known day: nothing before the
project began, nothing in the future. They state an earliest date, a latest date or both on the
field. The field enforces them, and whichever widget the field has keeps a person from entering a
date outside them.

**Why this priority**: Without it a developer writes a validator and the person only learns of the
limit after the form is sent. It is last because every other story works without it.

**Independent Test**: Define a field with an earliest and a latest date, submit values at each
precision on both sides of each limit, and draw the field with each widget.

**Acceptance Scenarios**:

1. **Given** a field with an earliest date, **When** it is submitted with a value every day of
   which is earlier, **Then** the field reports an error that names the earliest date.
2. **Given** a field with a latest date, **When** it is submitted with a value every day of which
   is later, **Then** the field reports an error that names the latest date.
3. **Given** a field whose earliest date is `1998-03-15`, **When** it is submitted with `1998` or
   `1998-03`, **Then** it is accepted. **When** it is submitted with `1998-02` or `1998-03-14`,
   **Then** it is refused.
4. **Given** a field whose earliest or latest date is stated as a year, a year and month, a full
   date or a Python date, **When** the form class is defined, **Then** each is taken.
5. **Given** a field whose earliest date is later than its latest, or one that is not a partial
   date, **When** the form class is defined, **Then** an error is raised that names the option.
6. **Given** such a field drawn with the masked widget, **When** a person types a digit from
   which no allowed date could follow, **Then** the digit is not accepted.
7. **Given** such a field drawn with either three-part widget, **When** a year is entered,
   **Then** the months on offer are those with an allowed day in that year, and the days on offer
   are the allowed days of the month chosen.
8. **Given** such a field drawn with the widget whose year is a select, **When** its form is
   drawn, **Then** the years on offer run from the year of the earliest date to the year of the
   latest.
9. **Given** a month or day already chosen, **When** the person changes the year so that it is no
   longer allowed, **Then** it is cleared.
10. **Given** a form submitted with a date outside the limits, as can happen on a page without the
    script, **When** it is drawn again, **Then** every widget shows what was sent beside the
    error.

---

### Edge Cases

- A value ends in a hyphen, such as `2021-` or `2021-03-`. It is read without the hyphen (FR-005).
- A value is cut off inside a part, such as `202` or `2021-0`. It is an error.
- A value has space around it. The space is dropped, as Django drops it for any text field.
- A month or day is `00`. It is an error.
- The year is `0000`, or has five digits. It is an error.
- A developer gives either widget to a field that is not the partial date field. The widget draws
  and submits text as it would, and whether that text is acceptable is that field's to decide.
- A developer sets `attrs` on either widget. They are kept. On the three-part widget they reach
  every part.
- The form is drawn with Django's own form rendering or another template pack. The masked widget
  draws its input and is masked as usual. The three-part widget draws three controls that work,
  without the joined drawing, which is the pack's.
- A page holds the form's media several times, once for each form. Each script acts once.
- A host project's language is not English. Month names and the field's error messages follow the
  active language, where Django has a translation.
- The three-part widget sits in a formset row added after the page loaded, or in a modal. The
  days follow the month there as anywhere.
- A person types the year into the three-part widget and has not yet typed all four digits. No
  month can be chosen until the year is whole.
- The 29th of February is chosen in a leap year and the year is then changed to one that is not.
  The day is cleared (FR-018).

### Out of scope

- A model field, and storage of any kind. The field hands back text and the developer's own model
  holds it.
- Support for a particular partial date package. The text is plain ISO, which is what such a
  package reads.
- Any order of parts but year, month, day, and any separator but a hyphen.
- An earliest or latest date that moves with another field's value, such as an end date no
  earlier than a start date. A developer writes that in the form's own `clean`.
- Years before 0001 or after 9999, historical calendars, seasons, quarters, decades, date ranges
  and approximate or uncertain dates.
- A time of day or a time zone.
- A calendar to pick from.
- A change to the four mask widgets of FS-015, which still take plain data only.

## Requirements *(mandatory)*

### Functional Requirements

#### The field

- **FR-001**: The package MUST provide a partial date field: a Django form field a developer adds
  to a form. It is the package's first field.
- **FR-002**: The field MUST accept a year, a year and month, or a year, month and day, and MUST
  reject any value naming a date that does not exist under the calendar rules Python's own dates
  use, for years 0001 to 9999.
- **FR-003**: The cleaned value MUST be text in ISO form: a four-digit year, then a two-digit
  month and a two-digit day where given, separated by hyphens. An empty submission to a field
  that is not required MUST clean to empty text.
- **FR-004**: The field MUST accept a month or day written with one digit and return it padded.
  It MUST reject a year not written with four digits.
- **FR-005**: The field MUST read a value ending in a hyphen as if the hyphen were absent, and
  MUST reject a value cut off inside a part.
- **FR-006**: The field MUST reject a month with no year and a day with no month.
- **FR-007**: The field MUST accept an initial value that is a partial date as text or a Python
  date, and show it as ISO text.
- **FR-008**: Each error the field reports MUST identify the part that is wrong or missing, MUST
  be translatable, and MUST be replaceable by the developer as Django's field errors are.
- **FR-009**: The field MUST behave as a Django text field does in every other respect:
  `required`, `label`, `help_text`, `validators`, `disabled` and `initial`.
- **FR-010**: With no widget named, the field MUST use a plain text input, so a form that uses
  the field and neither widget needs no script.

#### The masked widget

- **FR-011**: The package MUST provide a widget that draws one text input masked as a partial
  date. A developer states no mask. It MUST be drawn as the pack draws any text input, taking the
  size, colour and variant stated for the form or the field.
- **FR-012**: On a page that loads IMask and the form's media, the input MUST place the
  separators for the person, MUST accept digits only, MUST refuse a digit that makes the month
  less than 1 or more than 12, and MUST refuse a digit that makes a day the typed month does not
  have in the typed year.
- **FR-013**: The input MUST allow a person to stop after the year or after the month, and what
  it submits then MUST be accepted by the field.
- **FR-014**: The widget MUST work as the mask widgets of FS-015 do in every respect that spec
  settles: one script named in the form's media, no inline script, an input added later is
  masked, no input is masked twice, and a page without IMask gets a plain text input and no
  error.

- **FR-042**: A masked input drawn holding a value its mask refuses MUST show that value whole,
  and MUST be masked from the moment the person changes it to a value the mask takes.

#### The three-part widget

- **FR-015**: The package MUST provide a widget that draws a year, a month and a day as separate
  parts and hands the field one value made from them.
- **FR-016**: Through the pack, the parts MUST be drawn as one joined group in one fieldset whose
  legend is the field's label, with one help text and one set of errors. Each part MUST carry a
  name for assistive technology that says which part it is, and MUST take the size, colour and
  variant stated for the form or the field.
- **FR-017**: On a page that loads the form's media, the days on offer MUST be the days the
  chosen month has in the entered year, a month MUST NOT be choosable before a whole year is
  entered, and a day MUST NOT be choosable before a month is chosen.
- **FR-018**: When a change to the year or month leaves the chosen day without a date, the day
  MUST be cleared. It MUST NOT be moved to another day.
- **FR-019**: The month MUST be chosen by name, in the active language.
- **FR-020**: This widget MUST NOT need IMask. Its behaviour in the browser MUST come from a
  script named in the form's media, with no inline script and no inline handler, which acts on
  parts added to the page later and acts once however often the page includes it.
- **FR-021**: On a page without that script, all three parts MUST be usable and submittable, and
  the field MUST validate what is sent.
- **FR-022**: A form drawn again after a failed submission MUST show in each part what the person
  entered, including a combination the field rejected.

#### Precision

- **FR-023**: The field MUST let a developer state the coarsest precision it accepts and the
  finest, each one of year, month and day. With nothing stated it accepts all three.
- **FR-024**: The field MUST reject a value coarser than the coarsest or finer than the finest,
  with an error that identifies the part that is needed or not allowed.
- **FR-025**: Every widget MUST follow the finest precision stated on the field: the masked input
  accepts nothing beyond it, and a three-part widget draws no part beyond it.
- **FR-026**: A finest precision coarser than the coarsest MUST raise an error when the form
  class is defined, naming both options.

#### The earliest and latest date

- **FR-034**: The field MUST let a developer state an earliest date, a latest date or both. Each
  is a partial date as text or a Python date. With neither stated every date from 0001 to 9999 is
  accepted.
- **FR-035**: The field MUST accept a value when at least one day it could stand for lies on or
  between the two dates, and MUST reject it otherwise with an error that names the date it
  crossed. An earliest date given to the year or month counts from its first day, and a latest
  date from its last.
- **FR-036**: An earliest date later than the latest, or either one that is not a partial date,
  MUST raise an error when the form class is defined, naming the option.
- **FR-037**: On a page that loads IMask and the form's media, the masked input MUST refuse a
  digit from which no accepted date could follow.
- **FR-038**: On a page that loads the form's media, both three-part widgets MUST offer only the
  months that hold an accepted day in the year entered and only the accepted days of the month
  chosen, MUST NOT let a month be chosen under a year that holds no accepted day, and MUST clear a
  month or day that a change of year leaves outside the limits.

#### The three-part widget with a select for the year

- **FR-039**: The package MUST provide a third widget: the three-part widget with the year chosen
  from a select. Everything FR-015 to FR-022 require of the three-part widget MUST hold for it.
- **FR-040**: The years it offers MUST run from the year of the field's earliest date to the year
  of its latest, latest first. Where the latest is not stated the list MUST end at this year, and
  where the earliest is not stated it MUST reach a hundred years back. A year the form was sent
  that is not on the list MUST still be shown when the form is drawn again.

#### One field, any widget

- **FR-041**: Every option MUST be stated on the field: the precisions and the earliest and
  latest dates. A widget MUST take none of them from the developer. The field MUST tell whichever
  widget it is given what was stated, so that changing a field from one widget to another is a
  change of the widget's name and nothing else.

#### Constraints the package keeps

- **FR-027**: The pack's own templates MUST still need no script. A page that loads daisyUI and
  nothing else MUST draw every form that uses neither widget exactly as before.
- **FR-028**: The feature MUST add no model, model field, view, URL or migration, and no runtime
  dependency.
- **FR-029**: The checks in the browser MUST never be the only check. Every rule a widget
  enforces in the browser MUST also be enforced by the field.

#### Shipping it

- **FR-030**: The README MUST gain a section on the field and both widgets: the values accepted
  and returned, the precision options, what each widget needs the page to load, what each does on
  a page without its script, and how the text is handed to a model. The field and both widgets
  MUST appear in the README's public surface, and any template the feature adds MUST appear in
  the template list.
- **FR-031**: The specification of FS-015 and the README's section on mask widgets MUST be
  brought up to date where they say the package has no date widget.
- **FR-032**: The demo MUST gain a page showing the field with each widget at each precision,
  with an earliest and a latest date, with initial values, in an invalid state, in a formset whose rows can be added, and in a modal.
- **FR-033**: `CONTEXT.md` MUST gain the terms under Key Entities.

### Requirement coverage

| Story | Requirements |
|---|---|
| US1: A developer adds a partial date field to a form | FR-001 to FR-010, FR-028 to FR-030, FR-033 |
| US2: A person types a partial date into one masked input | FR-011 to FR-014, FR-027, FR-031, FR-032, FR-042 |
| US3: A person enters a partial date as a year, a month and a day | FR-015 to FR-022, FR-032, FR-039, FR-040 |
| US4: A developer sets how precise a partial date must be | FR-023 to FR-026, FR-041 |
| US5: A developer sets the earliest and latest date a field accepts | FR-034 to FR-038 |

### Key Entities

- **Partial date**: a date known to the year, to the month or to the day, written as ISO text:
  `2021`, `2021-03` or `2021-03-14`. A part is only ever left out from the right.
- **Precision**: how much of a partial date is given. One of year, month and day, from coarsest
  to finest.
- **Part**: the year, the month or the day of a partial date. In the three-part widget each is
  one widget of a multi-widget field, which is what the glossary already calls a part.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every year, month and day combination a person can submit, the field accepts it
  exactly when that date exists, and every accepted value comes back as padded ISO text.
- **SC-002**: On a page with its script loaded, a person cannot bring either widget to offer or
  accept a month outside 1 to 12, or a day beyond the length of the month and year already
  entered.
- **SC-003**: A person can enter a date known only to the year, or only to the month, in either
  widget without entering a placeholder for the missing parts.
- **SC-004**: With every script blocked, a form using either widget can still be filled in and
  submitted, and an impossible date is reported as an error on the field.
- **SC-005**: A form that uses neither widget loads no script from this package, as before.
- **SC-006**: A developer adds a partial date to a form with one field and, at most, one widget
  named, and reads one text value from the cleaned data. Changing the widget changes no other
  line.
- **SC-008**: On a page with its script loaded, a person cannot bring any widget to offer or
  accept a date outside the earliest and latest dates stated on the field.
- **SC-007**: The three-part widget is announced by assistive technology as one named group
  holding three named parts.

## Assumptions

- A host project that wants the masked widget loads IMask itself, as it does for the mask widgets
  of FS-015.
- The text returned is what a model's own partial date field or a plain text column takes. How a
  project stores it is the project's.
- The Gregorian rules for every year from 0001 are acceptable for the research data this is for,
  where early dates are rare and are recorded in the modern calendar.
- The drawing of the three-part widget is settled by eye on a prototype before it is planned.
