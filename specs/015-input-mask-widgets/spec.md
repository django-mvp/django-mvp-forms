# Feature Specification: Input mask widgets for IMask

**Feature Branch**: `015-input-mask-widgets`

**Created**: 2026-10-09

**Status**: Draft

**Serves**: G11 (the package offers its own fields and widgets, each looking native beside the
pack's own inputs) and G4 (the variant, colour and size of any form component can be set from
Python)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #150

**Depends on**: nothing still to be delivered. It builds on the text input the pack already draws
(FS-001) and the size, colour and variant choices of FS-007.

**Input**: A developer should be able to put an input mask on a text field from Python by choosing
a widget, so a person filling in the form gets a formatted phone number, a postcode, a number with
separators or a restricted set of characters as they type. The masking is done in the browser by
[IMask](https://imask.js.org/). This package provides the widgets and the script that connects
them to IMask, and the host project loads IMask itself.

## Clarifications

### Session 2026-10-09

The maintainer confirmed the reading of the feature and what it covers before this was written:
one widget for each kind of mask, the kinds and options listed under Requirements, and the kinds
left out. The coverage scan then found five ambiguities. Each was resolved from that conversation,
the goals, the constitution and the decision records. Longer rationale is in `decisions.md`.

- **Q: One widget that takes IMask's options, or one widget for each kind of mask?**
  A: One for each kind: pattern, regular expression, number, and a choice between several masks.
  Each kind has options that mean nothing on the others, so each widget takes only its own, by
  name, and refuses a value that cannot be right when the form is defined. This is how Django
  itself separates `TextInput`, `NumberInput` and `EmailInput`. Recorded as FR-001 to FR-004.

- **Q: Which of IMask's options are supported?**
  A: Every option that can be written as plain data: text, numbers, true or false, lists, and
  regular expressions written as text. An option that is a JavaScript function cannot be written
  in Python and is not supported: function masks, `prepare`, `prepareChar`, `commit`, `validate`,
  `dispatch`, `format` and `parse`. IMask's date mask needs two of those functions for any format
  but its default, so the four widgets take no JavaScript function, and a date is masked with a
  pattern whose day, month and year are number ranges. A partial date has a widget of its own,
  described under [Partial dates](https://github.com/django-mvp/django-mvp-forms#partial-dates).
  Recorded as FR-005 to FR-016 and under Out of scope.

- **Q: What does the form receive when a masked input is submitted?**
  A: A pattern or regular expression widget submits what the person sees, fixed characters
  included, and the developer's field cleans it as it would any text. A number widget is the
  exception, because a number shown with separators is not one a Django number field accepts. It
  hands the field the number in plain form, so `1 234,56` on the page reaches a `DecimalField` as
  `1234.56`. Recorded as FR-017 to FR-020.

- **Q: The package has never shipped a script, and ADR 0041 says the pack ships none. How does
  this feature square with that?**
  A: The promise is about the template pack: a page that loads daisyUI and nothing else draws
  every form the pack can draw, and that stays true. The script belongs to these widgets. It is
  named in the form's media, so a page gets it only when a form on it uses one of them, and a
  project that uses none never sees it. The script is a file, and the widgets write no inline
  script and no inline handler, so a strict Content Security Policy needs no exception for them.
  Recorded as FR-021 to FR-025.

- **Q: What happens on a page that does not load IMask?**
  A: The input is an ordinary text input that works. Nothing is masked, no error is raised in the
  browser, and the form submits. A mask is a help to the person typing and never the thing that
  makes the data valid, so the widgets add no validation on the server and the developer's field
  validates exactly as it did. Recorded as FR-026 to FR-028.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer masks a text field with a pattern (Priority: P1)

A developer has a field with a fixed shape: a phone number, a postcode, a card number, a product
code. They give the field the pattern widget and write the shape as IMask's pattern text. A person
filling in the form sees the fixed characters appear as they type, cannot type a letter where a
digit belongs, and can be shown the whole shape as a placeholder before typing anything.

**Why this priority**: The pattern is the mask people mean when they say "input mask", and every
other story builds on what this one sets up: the script, the way options reach it, and the input
drawn as one of the pack's own.

**Independent Test**: Define a form with one field using the pattern widget, load IMask and the
form's media on the page, and type into the field. The form can be drawn, filled in and submitted
with no other story delivered.

**Acceptance Scenarios**:

1. **Given** a field using the pattern widget with a pattern, **When** its form is drawn, **Then**
   the input is a text input drawn as the pack draws any text input, and it carries the pattern
   and every option the developer stated in a form the script can read.
2. **Given** a page that loads IMask and the form's media, **When** a person types into the field,
   **Then** IMask applies the pattern with the options the developer stated.
3. **Given** a pattern widget told to show its placeholder always, with a placeholder character,
   **When** the field is empty on such a page, **Then** the whole shape is shown with that
   character in each open position.
4. **Given** a pattern widget with a definition of the developer's own for one character,
   **When** a person types at a position holding that character, **Then** only what the
   definition allows is accepted.
5. **Given** a pattern that names blocks, each a number range, a list of allowed values, a nested
   pattern or a repeated pattern, **When** a person types into a block, **Then** the block
   accepts only what its kind allows.
6. **Given** a bound form whose field holds a value, **When** the form is drawn again on such a
   page, **Then** the value is shown under the mask.
7. **Given** a field using the pattern widget, **When** a size, colour or variant is stated for
   the form or the field, **Then** the input takes it as any text input does.
8. **Given** a pattern widget given an option it does not have, or a block of a kind that does
   not exist, **When** the form class is defined, **Then** an error is raised that names the
   option.
9. **Given** a form using the pattern widget, **When** it is submitted, **Then** the field
   receives the text as the person saw it, fixed characters included.
10. **Given** a pattern widget with a placeholder character stated for a definition, **When** the
    placeholder is shown, **Then** each position of that definition shows that character.
11. **Given** a pattern widget with a display character, **When** the form is submitted, **Then**
    the field receives what the person typed and not the display character.

---

### User Story 2 - A developer restricts what can be typed with a regular expression (Priority: P2)

A developer has a field with no fixed shape but a limited alphabet: digits only, letters and
hyphens, a hexadecimal colour. They give the field the regular expression widget and write the
expression. A person filling in the form finds that a character the expression rejects is not
accepted.

**Why this priority**: It is the simplest mask and a common need, and it reuses everything the
first story sets up.

**Independent Test**: Define a form with one field using the regular expression widget, and type
allowed and disallowed characters into it on a page that loads IMask.

**Acceptance Scenarios**:

1. **Given** a field using the regular expression widget with an expression, **When** its form is
   drawn, **Then** the input carries the expression and its flags in a form the script can read.
2. **Given** a page that loads IMask and the form's media, **When** a person types a character
   that makes the value stop matching the expression, **Then** the character is not accepted.
3. **Given** an expression stated as case-insensitive, **When** a person types in either case,
   **Then** both are accepted where the expression allows the letter.
4. **Given** a regular expression widget created with no expression, **When** the form class is
   defined, **Then** an error is raised.

---

### User Story 3 - A developer formats a number as it is typed (Priority: P2)

A developer has an amount, a quantity or a measurement. They give the field the number widget and
state how many decimal places it has, the thousands separator, the character that marks the
decimal point, and optionally the smallest and largest value. A person filling in the form sees
the separators appear as they type, and the developer's number field receives a number it can
read.

**Why this priority**: Numbers with separators are the second most common mask, and this is the
one kind where the value shown and the value a Django field accepts differ, so the widget has work
of its own to do.

**Independent Test**: Define a form with a `DecimalField` using the number widget with a thousands
separator and a comma as the decimal mark, submit `1 234,56`, and read `cleaned_data`.

**Acceptance Scenarios**:

1. **Given** a field using the number widget, **When** its form is drawn, **Then** the input is a
   text input, asks a touch device for a numeric keypad, and carries every option the developer
   stated in a form the script can read.
2. **Given** a page that loads IMask and the form's media, **When** a person types a number,
   **Then** it is shown with the separators and decimal places the developer stated.
3. **Given** a number widget with a smallest and a largest value, **When** a person types a
   number outside them, **Then** IMask refuses it, or corrects it to the nearest bound when the
   developer asked for that.
4. **Given** a number widget with a thousands separator and a decimal mark that is not a full
   stop, **When** the form is submitted with a number written that way, **Then** the field
   receives the same number with no thousands separator and a full stop as its decimal mark.
5. **Given** a form whose number field holds an initial or submitted value, **When** the form is
   drawn on such a page, **Then** the value is shown with the separators the developer stated.
6. **Given** a number widget whose thousands separator and decimal mark are the same character,
   or whose smallest value is larger than its largest, **When** the form class is defined,
   **Then** an error is raised.
7. **Given** a number field left empty, **When** the form is submitted, **Then** the field
   receives an empty value, as it would from any text input.

---

### User Story 4 - A developer uses a masked field in a formset, a modal and content loaded later (Priority: P2)

A developer puts a masked field in a formset whose rows are added in the browser, in a `Modal`,
and in a form that htmx swaps into the page. In each, the mask is applied without the developer
writing any script.

**Why this priority**: The projects this package serves add formset rows in the browser and load
forms with htmx as a matter of course. A mask that works only on inputs present when the page
loads would fail in most of the places it is used.

**Independent Test**: Draw a formset with a masked field, add a row in the browser, and type into
the new row's field.

**Acceptance Scenarios**:

1. **Given** a page that loads IMask and the form's media, **When** an input of one of these
   widgets is added to the page after it has loaded, by any script, **Then** the mask is applied
   to it.
2. **Given** a formset with a masked field, **When** its empty form is drawn, **Then** the
   template row carries the same options as every other row.
3. **Given** an input whose mask has been applied, **When** the script meets it again, **Then**
   it is not masked a second time.
4. **Given** a masked field in a `Modal`, a `Tab` or an `AccordionGroup`, **When** the container
   is opened, **Then** the mask is in place.
5. **Given** a masked field that is disabled or read-only, **When** the form is drawn on such a
   page, **Then** its value is shown under the mask and it stays disabled or read-only.

---

### User Story 5 - A developer offers several masks and lets the best fit apply (Priority: P3)

A developer has a field that takes values of more than one shape: a phone number of two lengths,
a colour written as a hexadecimal code or as three numbers. They give the field the widget that
chooses between masks and list the masks. As a person types, IMask applies whichever mask fits
what has been typed so far.

**Why this priority**: It is needed less often than a single mask, and it is built from the masks
of the first three stories.

**Independent Test**: Define a form with one field offering two patterns of different lengths,
and type a value of each length on a page that loads IMask.

**Acceptance Scenarios**:

1. **Given** a field using this widget with a list of masks, each a pattern, a regular expression
   or a number mask with its own options, **When** its form is drawn, **Then** the input carries
   every mask in the list, in order, with its options.
2. **Given** a page that loads IMask and the form's media, **When** a person types, **Then**
   IMask applies the mask from the list that fits the most of what was typed, and the earlier one
   when two fit equally.
3. **Given** this widget created with an empty list, **When** the form class is defined, **Then**
   an error is raised.
4. **Given** a form using this widget, **When** it is submitted, **Then** the field receives the
   text as the person saw it.

---

### User Story 6 - A developer adds an option that needs JavaScript (Priority: P3)

A developer needs one of the options this package does not carry, such as choosing a phone mask
from the country code or turning every letter to upper case. They listen for the event the script
sends from each input once its mask is in place, take the IMask instance from it, and set the
option in a few lines of their own script.

**Why this priority**: It serves the few cases outside what plain data can describe. Without it
those cases have no route but to stop using the widget.

**Independent Test**: On a page with a masked field, listen for the event on the document, and
change an option on the instance it carries.

**Acceptance Scenarios**:

1. **Given** a page that loads IMask and the form's media, **When** a mask is applied to an
   input, **Then** an event is sent from that input, reaches a listener on the document, and
   carries the IMask instance.
2. **Given** an input added to the page after it has loaded, **When** its mask is applied,
   **Then** the same event is sent from it.
3. **Given** a developer's listener that updates the options of the instance, **When** a person
   types, **Then** the updated options apply.

---

### Edge Cases

- The page loads the form's media and never loads IMask. Every input is a plain text input, no
  error is raised in the browser, and the form submits (FR-026).
- A number widget's value is typed on a page with no IMask. The server reads it by the same rule
  as always: the thousands separator is dropped and the decimal mark becomes a full stop. A person
  who types `1234.56` where the decimal mark is a comma and the thousands separator a full stop
  therefore submits a different number. The README says so, and the developer's field still
  validates what it receives (FR-020).
- A regular expression that only matches a finished value, such as one requiring exactly five
  digits, accepts no first character. IMask tests the value after every keystroke. The README
  says the expression has to accept every partial value on the way to a whole one (FR-031).
- A regular expression is written in JavaScript's dialect and is never run by Python. A
  difference between the two dialects is the developer's to mind (FR-008).
- A pattern is submitted half filled in. The field receives what was typed, and whether that is
  acceptable is the field's validation to decide.
- A value the developer supplies as initial data does not fit the mask. IMask shows as much of it
  as fits. What is shown is IMask's to decide.
- A developer sets `attrs` on the widget, such as a `placeholder` or a class. They are kept, as
  they are on any widget.
- A developer subclasses one of the widgets. The subclass is drawn and masked as its parent is.
- A page holds several forms drawn with `{% crispy %}`. django-crispy-forms writes a form's media
  inside each form, so the page holds the script once for each of them. The script acts once and
  each input gets one mask (FR-025).
- A host project bundles IMask into its own script and exposes it under the name IMask publishes.
  The widgets work as they do with the copy from a CDN.
- A form is drawn with `|crispy`, `{% crispy form %}` or `|as_crispy_field`, or with Django's own
  form rendering and no crispy-forms at all. The widget draws its options in each.

### Out of scope

- IMask itself. The package does not distribute it, load it or name a CDN outside the demo and
  the README's example.
- Every option that is a JavaScript function, as the clarifications record. A partial date has a
  widget of its own, described under
  [Partial dates](https://github.com/django-mvp/django-mvp-forms#partial-dates).
- IMask's pipes, which format a value without an input.
- Widgets for one particular format, such as a phone number or an IBAN. Formats differ by country
  and each is one line with the pattern widget.
- Validation on the server. A developer who needs the submitted text to match a shape adds a
  validator to the field.
- An option to submit a pattern's value without its fixed characters.
- Fields. This feature adds widgets only.

## Requirements *(mandatory)*

### Functional Requirements

#### The widgets

- **FR-001**: The package MUST provide a pattern mask widget, a regular expression mask widget, a
  number mask widget and a widget that chooses between several masks. Each is a Django form
  widget a developer names on a field.
- **FR-002**: Each widget MUST take its options as named arguments and MUST accept only the
  options of its own kind.
- **FR-003**: Each widget MUST raise an error when the form class is defined if it is given an
  option it does not have, is missing the one it cannot work without, or is given values that
  contradict each other. The error MUST name the option.
- **FR-004**: Each widget MUST draw a text input, and the pack MUST draw it as it draws any text
  input, taking the size, colour and variant stated for the form or the field.

#### Pattern

- **FR-005**: The pattern widget MUST take the pattern as IMask's pattern text, unchanged.
- **FR-006**: The pattern widget MUST support definitions of the developer's own, each a single
  character and the regular expression it stands for, and these options: showing the placeholder
  always, the placeholder character for the whole pattern or for each definition, overwriting in
  place of inserting, filling in fixed characters ahead of the cursor, and the character shown in
  place of what was typed.
- **FR-007**: The pattern widget MUST support named blocks of four kinds: a number range with its
  bounds, its length and whether a value outside them is corrected; a list of allowed values; a
  nested pattern; and a pattern repeated a stated number of times.

#### Regular expression

- **FR-008**: The regular expression widget MUST take the expression as text in JavaScript's
  dialect, with its flags, and MUST pass both to IMask without running the expression in Python.

#### Number

- **FR-009**: The number widget MUST support the number of decimal places, the thousands
  separator, the decimal mark, the other characters to be read as the decimal mark, padding the
  decimal places with zeros, trimming needless zeros, the smallest value, the largest value, and
  correcting a value outside them.
- **FR-010**: The number widget's input MUST ask a touch device for a numeric keypad, and MUST
  stay a text input, since IMask masks no other type.

#### A choice between masks

- **FR-011**: The widget that chooses between masks MUST take an ordered list of masks, each a
  pattern, a regular expression or a number mask with that kind's options.
- **FR-012**: Which mask applies as a person types MUST be IMask's own choice. The package adds
  no rule of its own.

#### What reaches the script

- **FR-013**: Every option a developer states MUST be written on the input as data the script
  reads, and an option the developer did not state MUST NOT be written, so IMask's own default
  applies.
- **FR-014**: The data MUST be escaped as any attribute value is, so a pattern, an expression or
  an allowed value holding a quote or an angle bracket cannot break out of the attribute.
- **FR-015**: A developer's own `attrs` on the widget MUST be kept.
- **FR-016**: The widgets MUST draw the same options whether the form is drawn through the pack,
  through another template pack, or through Django's own form rendering.

#### What the form receives

- **FR-017**: The pattern widget, the regular expression widget and the widget that chooses
  between masks MUST hand the field the submitted text unchanged. Where a pattern has a display
  character, the text submitted MUST be what the person typed. Where a pattern shows its
  placeholder always and nothing was typed into it, the text submitted MUST be empty.
- **FR-018**: The number widget MUST hand the field the submitted number with the thousands
  separator removed and the decimal mark as a full stop.
- **FR-019**: The number widget MUST show an initial or submitted value so that IMask reads it as
  the same number, whatever separators the developer stated.
- **FR-020**: The number widget MUST read a submitted value by the one rule of FR-018 whether or
  not IMask was on the page.

#### The script

- **FR-021**: The package MUST ship one script that applies IMask to every input these widgets
  draw, using the options written on the input.
- **FR-022**: Each widget MUST name the script in its media, so a page that renders the form's
  media loads it and a page with none of these widgets does not.
- **FR-023**: The widgets and the script MUST use no inline script and no inline event handler.
- **FR-024**: The pack's own templates MUST still need no script. A page that loads daisyUI and
  nothing else MUST draw every form that uses none of these widgets exactly as before.
- **FR-025**: The script MUST apply the mask to an input added to the page after it has loaded,
  whichever script added it, and MUST NOT mask one input twice, however many times the page
  includes the script.
- **FR-026**: On a page where IMask is not present, the script MUST do nothing and MUST raise no
  error.
- **FR-027**: The script MUST send an event from each input once its mask is applied. The event
  MUST reach a listener on the document and MUST carry the IMask instance.

#### Constraints the package keeps

- **FR-028**: The widgets MUST add no validation on the server and MUST NOT change the
  validation of the field they are named on.
- **FR-029**: IMask MUST NOT become a dependency of the package and MUST NOT be distributed with
  it.
- **FR-030**: The feature MUST add no field, model, view or URL.

#### Shipping it

- **FR-031**: The README MUST gain a section on the widgets: each widget and its options, how the
  host project loads IMask and the form's media and in which order, the major version of IMask
  the widgets are written for, what the form receives from each widget, the event and what it
  carries, what a page without IMask does, the options that are not supported, and the two
  cautions under Edge cases. Each widget MUST appear in the README's public surface.
- **FR-032**: The demo MUST gain a page that shows each widget with its common options, a masked
  field in a formset whose rows can be added, and one in a modal.
- **FR-033**: The decision records MUST state that the package ships a script for these widgets
  and that the pack's own templates still need none, and ADR 0041 MUST read true beside it.
- **FR-034**: `CONTEXT.md` MUST gain the terms under Key Entities.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1 | FR-001 to FR-007, FR-013 to FR-017, FR-021 to FR-024, FR-026, FR-028 to FR-034 |
| US-2 | FR-001 to FR-004, FR-008, FR-013 to FR-017 |
| US-3 | FR-001 to FR-004, FR-009, FR-010, FR-013 to FR-016, FR-018 to FR-020 |
| US-4 | FR-025, FR-032 |
| US-5 | FR-001 to FR-004, FR-011 to FR-017 |
| US-6 | FR-027, FR-031 |

### Key Entities

- **Mask**: A rule IMask applies to a text input as a person types, which decides what can be
  typed and how it is shown.
- **Kind of mask**: One of the four this package has a widget for: pattern, regular expression,
  number, and a choice between several.
- **Pattern**: A mask written as text in which some characters stand for what may be typed at
  that position and the rest are fixed.
- **Definition**: The meaning of one character in a pattern, such as `0` for any digit.
- **Block**: A named part of a pattern with a rule of its own.
- **Fixed character**: A character of a pattern that IMask writes and the person does not type.
- **Form's media**: The scripts and stylesheets Django collects from a form's widgets, which the
  host project's template renders.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer masks a field by naming one widget and its options in Python, and
  writes no JavaScript, for every mask the four widgets cover.
- **SC-002**: A host project needs at most two additions to a page to make every masked field on
  it work: IMask, and the form's media where the form is not drawn with `{% crispy %}`, which
  writes it.
- **SC-003**: A `DecimalField` using the number widget accepts a number submitted with any
  thousands separator and decimal mark the widget was given, with no cleaning code written by the
  developer.
- **SC-004**: Every option a widget accepts is found on the drawn input, and every option it does
  not accept is refused before any form is drawn.
- **SC-005**: A page that loads none of IMask draws and submits every form that uses these
  widgets, with no error in the browser.
- **SC-006**: Every form in the suite and the demo that uses none of these widgets is drawn with
  the same markup as before the feature, and the package still installs with no new dependency.
- **SC-007**: A masked field works in a formset row added in the browser, in a modal and in
  content swapped in after the page loads, with no script written by the developer.
- **SC-008**: A page with a Content Security Policy that allows scripts from the site's own
  origin and the origin serving IMask, and forbids inline script, masks every field.

## Assumptions

- The widgets are written for IMask 7, the current major version. The README names it. IMask is
  not added to the package's stated support window, because nothing the package installs depends
  on it.
- A form drawn with `{% crispy %}` brings its media with it. For any other form the host project
  renders the form's media in its page template, or loads the script by its static path, which
  the README gives.
- The script's behaviour is tested in a browser, against a copy of IMask kept with the tests.
- The names of the widget classes and of the event are public surface under Article XI from the
  release that ships them.
