# Feature Specification: Characters left under a text field

**Feature Branch**: `020-characters-left`

**Created**: 2026-11-22

**Status**: Draft

**Serves**: G11 (the package offers its own fields and widgets, for needs no third-party package
meets, each looking native beside the pack's own inputs) and G3 (labels, help text and errors are
tied to their inputs, so forms work with assistive technology)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #251

**Depends on**: nothing still to be delivered. It builds on the text input and textarea the pack
already draws (FS-001).

**Input**: A field with a maximum length tells the person only when they submit too much. A line
under the field counting down the characters left lets them fit their text as they type. A
developer should be able to turn this on for a text input or textarea, including the typing box of
the package's Tom Select widgets, and have it follow the field's own `max_length`.

## Why

Django writes a field's `max_length` on its input as the browser's own limit, so a person cannot
type past it. Nothing tells them how close they are. Their text stops taking characters without a
word, or, in a textarea holding line breaks, it is refused by the field after they submit,
because the browser and Django count a line break differently. A line under the field that says
how many characters are left, once only a few are, lets a person shorten their text while they
are still writing it.

## Clarifications

### Session 2026-11-22

The reading of the feature was settled before this was written: one setting a developer turns on
for a field, the line it adds, where it works, and what is left out. The coverage scan then found
six ambiguities. Each was resolved from the issue, the goals, the constitution and the decision
records. Longer rationale is in `decisions.md`.

- **Q: Is the line there all the time, or only near the limit?**
  A: Only once a few characters are left. A count that is always on is noise for a field that is
  nowhere near its limit. The package sets how many "a few" is, and a developer can state another
  number for one field. Recorded as FR-004 and FR-005.

- **Q: Where does the limit come from?**
  A: From the field's own `max_length` and nowhere else, so the line can never promise more than
  the field accepts. Recorded as FR-002.

- **Q: Is the line offered on the package's Tom Select widgets, as the issue asks?**
  A: Not by this feature. On a Tom Select control the line matters only where a person can create
  an option by typing it, and its limit would then be the length of a new option's text. The
  package's `TomSelect` and `TomSelectMultiple` let a person choose only among the field's
  choices (FS-017), so their typing box only searches, and the line is not offered on them. It is
  added with the setting that lets a person create an option, if one is ever specified. Recorded
  under Out of scope.

- **Q: What does assistive technology hear?**
  A: The number left, announced politely, when the line first appears, when the person stops
  typing, and when no characters are left. Never once for every key. Recorded as FR-011.

- **Q: A textarea with line breaks: the browser counts each break as one character and the
  submitted text holds two. Which count does the line follow?**
  A: The field's. A text the line says fits must be accepted when it is submitted. Recorded as
  FR-009.

- **Q: What does the line say about a value that is already over the limit, such as initial data
  written before the limit was lowered?**
  A: That it is over, and by how many characters. The box does not cut the value, and the field's
  validation reports it as it does today. Recorded as FR-008.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer shows how many characters are left under a field (Priority: P1)

A developer has a field with a maximum length: a short name, a title, or a summary written in a
textarea. They turn on the characters-left line for the field from Python, on its widget, and
write no script and no template. They may state from how many characters left the line
appears.

**Why this priority**: It is the whole of the developer's side of the feature. Without it there is
no line to see.

**Independent Test**: Define a form with a `CharField` with a `max_length`, drawn as a text input
with the line turned on, render it with its form's media, and read the page.

**Acceptance Scenarios**:

1. **Given** a `CharField` with a `max_length` whose text input has the line turned on, **When**
   its form is drawn, **Then** the input carries the field's `max_length` as its limit and is
   marked so the script finds it.
2. **Given** the same on a field drawn as a textarea, **When** its form is drawn, **Then** the
   textarea is marked in the same way.
3. **Given** a field with the line turned on, **When** the form's media is rendered, **Then** it
   names the package's script for the line, and **Given** a form with no field that turns it on,
   **Then** the form's media does not name it.
4. **Given** a field that states from how many characters left the line appears, **When** its
   form is drawn, **Then** that number is written for it, and **Given** one that states none,
   **Then** the package's number is.
5. **Given** a field with no `max_length` whose widget has the line turned on, **When** the form
   is drawn, **Then** an error is raised that names the field.
6. **Given** a number from which the line appears that is not a whole number above zero, or a
   limit stated on the widget, **When** the form class is defined, **Then** an error is raised
   that names the setting.
7. **Given** a field with the line turned on, **When** it is drawn through the pack, through
   another template pack or through Django's own form rendering, **Then** the same attributes
   are written.

---

### User Story 2 - A person sees how many characters are left as they type (Priority: P1)

A person filling in a form types into a field with a limit. While plenty of room is left, nothing
is shown. Once only a few characters are left, a line under the field says how many, and it
counts down as they type, and up again as they delete. When none are left the field takes no
more. A person using a screen reader hears the number when it matters, not on every key.

**Why this priority**: This is what the feature is for. A developer's setting with no line a
person sees would serve nobody.

**Independent Test**: On a page that loads the form's media, type into a field with the line
turned on until it is full, and read the line and the field's value at each step.

**Acceptance Scenarios**:

1. **Given** a field with the line turned on, **When** it holds fewer characters than the limit
   less the number from which the line appears, **Then** no line is shown.
2. **Given** such a field, **When** a person types until that number of characters or fewer is
   left, **Then** a line under the field says how many are left, and **When** they type or delete
   another, **Then** the number follows.
3. **Given** such a field, **When** a person deletes until more than that number is left,
   **Then** the line is hidden again.
4. **Given** a field with no characters left, **When** a person types or pastes more, **Then**
   the field takes none of it and the line says that none are left.
5. **Given** a form drawn with an initial or submitted value close to the limit, **When** the
   page has loaded, **Then** the line is shown with the number left before anything is typed.
6. **Given** a field holding a value longer than its limit, **When** the page has loaded,
   **Then** the line says the value is over the limit and by how many characters, and the value
   is not cut.
7. **Given** a textarea with the line turned on, **When** a person writes text holding line
   breaks until the line says none are left and submits, **Then** the field accepts the text.
8. **Given** a person using a screen reader, **When** the line first appears, when they stop
   typing, and when no characters are left, **Then** the number left is announced politely, and
   it is not announced for each key they press.
9. **Given** the line, **When** it is shown under any daisyUI theme the pack's legibility check
    covers, **Then** it can be read against the page.
10. **Given** a field with the line turned on in a formset row added in the browser, in a `Modal`,
    or in a form that htmx swaps into the page, **When** a person types into it, **Then** the
    line works as it does on a page loaded in full, with no script written by the developer.
11. **Given** a page that holds the script more than once, **When** a person types into a field,
    **Then** there is one line under it.
12. **Given** a page that does not load the script, **When** a person types into the field,
    **Then** the field still stops at its limit, no line is shown and no error is raised.

---

### Edge Cases

- The field is disabled or read-only. Nothing can be typed, so the line only appears if the value
  drawn is already close to the limit or over it (FR-007, FR-008).
- A field's text is changed by a script rather than by typing. The line is brought up to date the
  next time the person types or the field takes focus.
- A person types characters made of more than one code unit, such as an emoji. The line counts as
  the browser's limit counts, which is never fewer than the field's validation counts, so the
  number it shows never lets through a text the field refuses (FR-009).
- The limit is lowered below the number from which the line appears. The line is shown from the
  first character.
- A masked input of FS-015 is a text input. The line is not promised on it, because its mask
  already fixes what can be typed (Out of scope).
- A developer subclasses a widget with the line turned on. The subclass shows the line as its
  parent does.
- The field's help text and errors are drawn as before, and stay tied to the input (FR-012).

### Out of scope

- Tom Select controls, the package's own and django-tomselect's. The line belongs on a control
  only where a person can create an option by typing it, with the length of a new option's text
  as its limit. The package's Tom Select widgets cannot create options.
- Masked inputs, number inputs, and every widget other than a text input and a textarea.
- Counting words, lines or bytes rather than characters.
- A lower limit, or a count of characters typed rather than characters left.
- Wording a developer states for the line. Its words are the package's, translated.
- Changing what the field's validation accepts, beyond FR-009.

## Requirements *(mandatory)*

### Functional Requirements

#### Turning it on

- **FR-001**: A developer MUST be able to turn the line on for one field from Python, on its
  widget, for a text input and a textarea, writing no script and no template.
- **FR-002**: The limit MUST be the field's own `max_length`. A limit stated on the widget MUST
  raise an error when the form class is defined, and turning the line on for a field with no
  `max_length` MUST raise an error naming the field no later than when the form is drawn.
- **FR-003**: The line MUST NOT be offered on the package's Tom Select widgets, which let a person
  choose only among the field's choices.
- **FR-004**: The line MUST appear once the characters left are at or below a number the package
  sets, and MUST be hidden while more are left.
- **FR-005**: A developer MUST be able to state that number for one field. A value that is not a
  whole number above zero MUST raise an error naming the setting when the form class is defined.
- **FR-006**: The attributes written MUST be the same whether the form is drawn through the pack,
  through another template pack or through Django's own form rendering.

#### What a person sees

- **FR-007**: The line MUST say how many characters are left, under the field's control, and MUST
  follow every character typed, deleted, pasted or cut. It MUST be up to date when the page has
  loaded, for a value drawn with the form.
- **FR-008**: For a value longer than its limit the line MUST say that it is over and by how many
  characters. Nothing MUST cut a value that is already there.
- **FR-009**: The line MUST count as the browser's limit counts, so the field stops taking
  characters exactly when the line says none are left. A text the line says fits,
  line breaks included, MUST be accepted by the field when it is submitted.
- **FR-010**: The line's words MUST be translatable, in the package's catalogue, with the plural
  forms of the language the page is drawn in.
- **FR-011**: The line MUST be announced to assistive technology politely: when it first appears,
  when the person stops typing, and when no characters are left. It MUST NOT be announced for
  each key pressed.
- **FR-012**: The field's label, help text and errors MUST stay tied to its input as they are
  today.

#### The script

- **FR-013**: The package MUST ship one script for the line. Each widget that turns the line on
  MUST name it in its media, so a page that renders the form's media needs nothing else, and a
  page with no such field loads none of it.
- **FR-014**: The script MUST work on fields added to the page after it has loaded, by any script,
  including formset rows, modals and content swapped in by htmx. A page that holds the script more
  than once MUST draw one line under each field.
- **FR-015**: The script MUST leave every input alone that no widget marked for the line,
  including a Tom Select control's typing box.
- **FR-016**: The widgets and the script MUST use no inline script and no inline event handler.
- **FR-017**: A page that does not load the script MUST draw the field as it would without the
  line, still stopping at its limit, and MUST raise no error.

#### Constraints the package keeps

- **FR-018**: The pack's own templates MUST still need no script and no stylesheet. The line MUST
  be drawn from daisyUI's classes and Tailwind utilities as the pack's other text is, with no
  stylesheet of its own, and MUST meet the pack's legibility check under every theme it covers.
- **FR-019**: A field that does not turn the line on MUST be drawn with the same markup as before
  the feature.
- **FR-020**: The feature MUST add no dependency, field, model, view or URL.

#### Shipping it

- **FR-021**: The README MUST gain a section on the line: how to turn it on for each widget, where
  the limit comes from, the number from which it appears and how to change it, what assistive
  technology hears, and what is not supported. Whatever the developer names MUST appear in the
  README's public surface.
- **FR-022**: The demo MUST gain a page in its Custom widgets group, with live examples of the line
  on a text input, a textarea, a formset whose rows can be added, and a
  field drawn with a value already over its limit.
- **FR-023**: `CONTEXT.md` MUST gain the terms under Key Entities.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1 | FR-001 to FR-006, FR-013, FR-016, FR-019 to FR-023 |
| US-2 | FR-007 to FR-012, FR-014, FR-015, FR-017, FR-018 |

### Key Entities

- **Characters-left line**: The line under a field's control that says how many characters the
  field has left before its limit, shown once only a few are left.
- **Limit**: The most characters a field takes, its `max_length`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer adds the line to a field by changing its widget alone, and writes no
  script, no template and no stylesheet.
- **SC-002**: A person who types into a field with the line turned on is told the characters left
  before the field stops taking them, every time they come within the number from which it
  appears.
- **SC-003**: No text the line says fits is refused by the field's length validation on submit,
  including a textarea's text with line breaks.
- **SC-004**: A screen reader user typing a text that reaches the limit hears the count a handful
  of times, never once per key.
- **SC-005**: The line works in a formset row added in the browser, in a modal and in content
  swapped in by htmx, with no script written by the developer.
- **SC-006**: Every form in the suite and the demo that does not turn the line on is drawn with
  the same markup as before, and the package installs with no new dependency.
