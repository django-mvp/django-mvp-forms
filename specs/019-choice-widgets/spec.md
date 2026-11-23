# Feature Specification: Choice widgets drawn as a scale, pills, chips or cards

**Feature Branch**: `019-choice-widgets`

**Created**: 2026-11-22

**Status**: Draft

**Serves**: G11 (the package offers its own fields and widgets, each looking native beside the
pack's own inputs) and G9 (daisyUI's other form components are reachable from a layout). It also
serves G4 (the size and colour of any form component can be set from Python).

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #250

**Depends on**: nothing still to be delivered. It builds on the radio and checkbox groups the pack
already draws (FS-002), the size and colour choices of FS-007, the rating of FS-010 and the way a
widget names a script in the form's media (FS-015).

**Input**: A choice field drawn as a select or a column of radios works, but many questions read
better laid out differently: a 0 to 10 rating as a row of segments with a word at each end, a short
set of options as toggle pills, a long set as chips with the rarely used ones folded behind
"more", and options that need explaining as cards with an icon and a line of description. A
developer should be able to pick one of these as the widget for a `ChoiceField` or
`MultipleChoiceField`, drawn with daisyUI's own markup, and keep a chosen option visible even when
the rest are folded away.

## Why

The pack draws a choice field as a select, a radio group, a checkbox group or a rating. Those suit
a form a person reads down. They suit badly a question a person answers at a glance or on a
phone: a select hides its options behind a tap, and a column of small radios is a poor target for
a finger. The layouts in this feature give each choice a large target and show the choices the way
the question is shaped: in order along a scale, side by side as pills, or as cards that say what
each one means. Every project that asks such questions otherwise writes the templates and the
styles itself.

## Clarifications

### Session 2026-11-22

The reading of the feature was settled before this was written: seven widgets, the settings each
takes, and what is left out. The coverage scan then found eight ambiguities. Each was resolved
from the issue, the goals, the constitution and the decision records. Longer rationale is in
`decisions.md`.

- **Q: Widgets, or drawings stated with `Choice` as the rating is?**
  A: Widgets, as the issue asks. Each layout has settings of its own (the words at the ends of a
  scale, a card's description and icon, the choices that stay on show), and a widget is where
  Django puts settings like these. A drawing takes none. Recorded as FR-001.

- **Q: What are the widgets called?**
  A: `ScaleSelect`, `PillSelect`, `PillSelectMultiple`, `ChipSelect`, `ChipSelectMultiple`,
  `CardSelect` and `CardSelectMultiple`, in `mvp_forms.widgets`. They follow Django's
  `RadioSelect` and `CheckboxSelectMultiple`, which they stand in for, and the package's own
  `TomSelect` and `TomSelectMultiple`. A scale holds one value, so it has no multiple widget.
  Recorded as FR-001.

- **Q: How is a single choice cleared?**
  A: By the field's own empty choice, as for a rating. A choice whose value is the empty string is
  not drawn as a segment, a pill, a chip or a card among the others. It is drawn after them as the
  way to say "none", and choosing it submits the field empty. A field with no empty choice offers
  no way to clear it. No script is needed, and a second tap on a chosen choice does nothing
  special. Recorded as FR-007.

- **Q: How does a developer say which choices stay on show?**
  A: By naming their values, for a chip or a card widget. The rest are folded behind a "More
  options" button. The values can be named when the widget is made or in the form's
  `__init__`, since which choices matter often depends on who is filling in the form. A chosen
  choice is always on show, whether or not it was named. Naming none shows every choice. Recorded
  as FR-011 to FR-015.

- **Q: Which part needs a script, and what happens without it?**
  A: Only the fold. The package ships one script for it, named in the media of the chip and card
  widgets. Every choice is drawn in the same row or grid, and the folded ones are marked. Without
  the script every choice is on show and the button that would show the folded ones stays hidden.
  What the script adds is that it hides the marked choices and shows the button, and the button
  shows them again in place.
  The scale and the pill widgets need no script. Recorded as FR-016 to FR-020.

- **Q: Where does a card's icon come from?**
  A: From the developer, as markup they hand the widget for each choice, such as an inline SVG or
  an icon tag their project already draws. The package names no icon set and gains no dependency.
  Text that is not marked safe is escaped. Recorded as FR-010.

- **Q: What happens to grouped choices?**
  A: The group names are not drawn, and the choices are drawn in the field's order, as a rating
  draws them. A grouped list of choices is a select's way of organising a long list, and these
  widgets organise one by folding instead. Recorded as FR-006.

- **Q: Which choices do the widgets take?**
  A: The form's and the field's size and colour, as every input does. They take no variant: a
  variant stated for the form is passed over for them, and one stated on the field raises
  `InvalidChoice`, as for a rating. No drawing can be stated for a field with one of these
  widgets. Recorded as FR-021 to FR-023.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer draws a choice field as a scale, pills, chips or cards (Priority: P1)

A developer has a question that a select or a column of radios draws poorly: how likely someone
is to recommend a product from 0 to 10, which of five colours they want, which of a long list of
interests apply to them, how they want an order delivered. They name one of the seven widgets on
the field, with the settings that widget takes: the words at the two ends of a scale, the choices
of a chip or card widget that stay on show, and for cards the description, the icon, the short
line above the label and how many cards sit across. The form is drawn with daisyUI's own markup,
needs no template, stylesheet or script written by the developer, and cleans exactly as it would
with a radio or checkbox group.

**Why this priority**: It is the feature. Nothing a person filling in the form sees exists until a
developer can name the widgets.

**Independent Test**: Define a form with one field for each widget, draw it with `{% crispy %}` on
a page that loads daisyUI and nothing from this package but the form's media, submit it, and read
`cleaned_data`.

**Acceptance Scenarios**:

1. **Given** a `ChoiceField` using `ScaleSelect` with words for the two ends, **When** its form is
   drawn, **Then** every choice that has a value is one radio input with the field's name, in the
   field's order, the words are drawn at the two ends of the row, and the first and last inputs
   are named with their end's words as well as their own label.
2. **Given** a `ChoiceField` using `PillSelect`, or a `MultipleChoiceField` using
   `PillSelectMultiple`, **When** its form is drawn, **Then** every choice is one radio input, or
   one checkbox input, with the field's name, in the field's order, each named by its label.
3. **Given** a field using `ChipSelect` or `ChipSelectMultiple`, **When** its form is drawn,
   **Then** every choice is one input as for pills, and a label of any length is shown in full.
4. **Given** a field using `CardSelect` or `CardSelectMultiple` with a description, an icon and a
   short line for some choices, **When** its form is drawn, **Then** every choice is one input
   inside a card that holds its label and the extras given for that choice, and a choice given
   none is drawn with its label alone.
5. **Given** a card widget given a number of cards across, **When** its form is drawn on a wide
   screen, **Then** at most that many cards sit side by side, and on a narrow screen one does.
   A number other than 1, 2 or 3 raises an error when the widget is made.
6. **Given** a chip or card widget given the values that stay on show, **When** its form is drawn,
   **Then** every choice is drawn in the one row or grid in the field's order, those not named
   and not chosen are marked as folded, and a button that shows them follows the choices.
7. **Given** a chip or card widget whose values on show are set in the form's `__init__`, **When**
   the form is drawn, **Then** the fold follows what was set there for that form alone, and
   another form using the same form class is not affected.
8. **Given** a chip or card widget given words of the developer's own for the fold, **When** its
   form is drawn, **Then** the button shows those words, and without them it shows the package's own.
9. **Given** a single-choice widget whose field has a choice whose value is the empty string,
   **When** its form is drawn, **Then** that choice is drawn after the others as the way to clear
   the field, and choosing it submits the field empty.
10. **Given** a form using any of the seven widgets, **When** it is submitted, **Then**
    `cleaned_data` holds the same value it would hold if the field used `RadioSelect` or
    `CheckboxSelectMultiple` with the same choices and the same submission.
11. **Given** a bound or initial value, **When** the form is drawn, **Then** the inputs of the
    chosen choices are checked, whether they are on show or folded by the developer's setting.
12. **Given** a form that states a size and a colour, and a field that states its own, **When** the
    form is drawn, **Then** each widget takes them as any input does, and a variant stated on the
    field raises `InvalidChoice`.
13. **Given** a field in error, a disabled field and a required field, **When** the form is
    drawn, **Then** each widget is drawn as a group is: in a fieldset named by a legend with the
    field's label and the required marker, with the help text and the errors describing it, every
    input `aria-invalid` when the field is in error and disabled when the field is.
14. **Given** a card widget given an icon as markup marked safe and a description holding an
    angle bracket, **When** its form is drawn, **Then** the icon is drawn as markup and the
    description is escaped.
15. **Given** a widget made with a setting it does not have, or a drawing stated for its field,
    **When** the widget is made or the form is drawn, **Then** an error is raised that names the
    setting.
16. **Given** values on show or extras keyed by a value the field does not offer, **When** the
    form is drawn, **Then** that value is passed over without an error, since the choices of a
    model field change with the data.
17. **Given** any of the seven widgets, **When** it is drawn through `{{ form|crispy }}`,
    `{% crispy form %}`, `|as_crispy_field`, a formset stacked or as a table, or inside a `Row`, a
    `Fieldset`, a `Tab`, an `AccordionGroup` or a `Modal`, **Then** it is drawn the same, and a
    host project can replace any of its templates as it replaces any template of the pack.
18. **Given** a `ModelChoiceField` or a `ModelMultipleChoiceField` using one of the widgets, with
    extras and values on show keyed by primary key, **When** its form is drawn, **Then** the extras
    and the fold apply to the right choices.

---

### User Story 2 - A person answers a question by tapping a choice (Priority: P2)

A person filling in a form on a phone or at a desk sees the question's choices laid out as the
developer chose, taps the one they mean, or several, and sees at once which are chosen. They can
clear a single choice where the developer offered a way to, press the button to find a choice not on
show, and do all of it with a keyboard or a screen reader as well as by touch. A choice they have
made is never hidden from them.

**Why this priority**: It is what the widgets are for, but it is delivered by the markup the first
story draws, so it is tested once that exists.

**Independent Test**: In a browser, on the demo's choice widgets page, answer every field by touch
and then by keyboard alone, press the button of the chip and card fields, and submit.

**Acceptance Scenarios**:

1. **Given** any of the widgets, **When** a person taps or clicks a choice, **Then** it is shown as
   chosen and, for a single-choice widget, the choice chosen before is not.
2. **Given** a multiple widget, **When** a person taps a chosen choice, **Then** it is no longer
   chosen.
3. **Given** a single-choice widget with a way to clear it, **When** a person chooses it, **Then**
   no other choice is shown as chosen and the form submits the field empty.
4. **Given** any of the widgets, **When** a person uses only a keyboard, **Then** they reach the
   group with the Tab key, move between the choices of a single-choice widget with the arrow keys,
   choose with the space bar, and see where the focus is at every step.
5. **Given** a screen reader, **When** a person reaches a widget, **Then** it announces the
   group's label, each choice's label, whether it is chosen, and for a scale the words of its ends
   on the first and last choices.
6. **Given** a page that loads the form's media and a chip or card widget with folded choices,
   **When** the page has loaded, **Then** the folded choices that are not chosen are hidden and
   the "More options" button is shown after the choices.
7. **Given** that button, **When** a person presses it by touch, mouse or keyboard, **Then** the
   hidden choices are shown in place, in the field's order, the button goes, and the focus moves
   to the first choice shown.
8. **Given** a page that does not load the package's script, **When** a person answers a chip or
   card field with folded choices, **Then** every choice is shown, the button is not, and they
   can choose any choice and submit the form.
9. **Given** a form drawn again after a failed submission, **When** the page loads, **Then** every
   choice the person had chosen is shown and chosen, folded or not.
10. **Given** a chip or card field in a formset row added in the browser, or in a form swapped
    into the page by htmx, **When** the row arrives, **Then** its folded choices are hidden and
    its button works as on a field drawn with the page, with no script written by the developer.
11. **Given** each of the daisyUI themes the test suite measures, **When** a widget is drawn,
    **Then** the text of every choice and the mark that shows a choice is chosen meet the standard
    against the surface behind them, or are published as known exceptions.

---

### User Story 3 - A developer places the mark of a card at its start (Priority: P3)

A developer draws a list of cards where the radio or checkbox is the first thing a person looks
for, such as a list of plans or of permissions. They set one setting on the card widget, `mark`,
to `"start"`, and each card draws its mark, then its text, then its icon: the mark and the icon
change places. Without it the card
draws its icon, its text, then its mark, as before.

**Why this priority**: It is a placement of what story 1 draws. The cards work without it.

**Independent Test**: Draw a `CardSelect` and a `CardSelectMultiple` with `mark="start"`, an icon
for one choice and none for another, and read the order of the parts of each card.

**Acceptance Scenarios**:

1. **Given** a card widget with `mark="start"`, **When** its form is drawn, **Then** each card
   holds its input first, then its text, then its icon where one is given.
2. **Given** a card widget with `mark="end"`, or with no `mark`, **When** its form is drawn,
   **Then** each card holds its icon where one is given, then its text, then its input.
3. **Given** a card widget given a `mark` other than `"start"` or `"end"`, **When** the widget is
   made, **Then** an error is raised that names `mark`.
4. **Given** a card widget with `mark="start"`, **When** a person taps a card or uses the
   keyboard, **Then** the card behaves as it does with the mark at the end.

---

### Edge Cases

- A field has no choices. The widget is drawn with its frame and no inputs, and a chip or card
  widget draws no button.
- Every choice is folded by the developer's setting and none is chosen. Nothing is folded, so the
  field never shows as empty.
- The values on show name every choice, or the choices folded number zero. No button is drawn.
- A scale has any number of choices. It is drawn as one row of that many segments, and the words
  at the ends belong to the first and last. The README recommends a scale for an ordered set of up
  to eleven choices, since segments narrow as their number grows.
- A scale with no words at its ends draws none and names its inputs by their labels alone.
- A choice's value is `0`. It is a segment, a pill, a chip or a card like any other, and only the
  empty string is the way to clear.
- A multiple field holds a choice whose value is the empty string. It is drawn as an ordinary
  choice: clearing a multiple field is unticking its choices.
- A label is long. A chip and a card show it in full, wrapping onto more lines. A pill and a scale
  are for short labels, and the README says so.
- A developer sets `attrs` on the widget, such as a class or a `data-` attribute. They are kept on
  every input, as on a radio group.
- A developer subclasses one of the widgets. The subclass is drawn as its parent is.
- `InlineRadios` or `InlineCheckboxes` is placed around a field using one of the widgets. The
  widget is drawn as it is anywhere else.
- The page holds several forms drawn with `{% crispy %}`, so the script is included more than
  once. It acts once on each button.
- A disabled field has folded choices. The button still shows them, so they can be read, and none
  can be chosen.
- A form is drawn with Django's own form rendering and no crispy-forms. The widgets still draw
  their inputs, labels, extras and button, without the size, colour and frame the pack adds.

### Out of scope

- A second tap on a chosen single choice clearing it. The empty choice is the way to clear.
- Reordering the choices in the browser, or folding by a count rather than by named values.
- Hiding the other choices once one is chosen, as daisyUI's filter does.
- An icon set, or icons on pills, chips or the scale.
- Group headings for grouped choices.
- A stylesheet. The widgets are drawn with daisyUI's classes and Tailwind's utilities only.
- Fields. This feature adds widgets only.

## Requirements *(mandatory)*

### Functional Requirements

#### The widgets

- **FR-001**: The package MUST provide `ScaleSelect`, `PillSelect`, `PillSelectMultiple`,
  `ChipSelect`, `ChipSelectMultiple`, `CardSelect` and `CardSelectMultiple` in
  `mvp_forms.widgets`. The single-choice widgets MUST be subclasses of `RadioSelect` and the
  multiple ones of `CheckboxSelectMultiple`.
- **FR-002**: Each widget MUST draw one input of type `radio` or `checkbox` for each choice it
  draws, with the field's name and the choice's value, so that the field validates and cleans as
  it would with Django's widget of the same kind.
- **FR-003**: Each widget MUST be drawn with daisyUI's classes and Tailwind's utilities alone. Its
  templates MUST define no class of the package's own and MUST need no stylesheet.
- **FR-004**: Each widget's choice MUST be named for assistive technology by its label. A scale's
  first and last inputs MUST also be named with the words at their end.
- **FR-005**: Each widget MUST take its settings as named arguments and MUST raise an error naming
  the setting for an argument it does not have or a value it cannot use.
- **FR-006**: Each widget MUST draw its choices in the field's order and MUST NOT draw the names of
  grouped choices.
- **FR-007**: A single-choice widget MUST draw a choice whose value is the empty string after the
  others, as the way to clear the field, and MUST NOT draw it as one of the others. A multiple
  widget MUST draw such a choice as any other.

#### Scale

- **FR-008**: `ScaleSelect` MUST take the words for its low end and its high end, each optional,
  and MUST draw its choices as one row of segments with the words at the two ends.

#### Chips and cards

- **FR-009**: A chip MUST show its label in full, however long.
- **FR-010**: A card widget MUST take, keyed by choice value, a description, an icon and a short
  line drawn above the label, each optional for every choice. An icon MUST be drawn as the markup
  the developer gives. Text not marked safe MUST be escaped.
- **FR-011**: A card widget MUST take the number of cards that sit across on a wide screen, 1, 2 or
  3, with 2 when none is given, and MUST draw one across on a narrow screen.

- **FR-032**: A card widget MUST take the side of the card on which the radio or checkbox mark is
  drawn, `mark`, "end" or "start", with "end" when none is given. A value other than those two
  MUST raise an error naming `mark` when the widget is made. With "start" the card draws the
  mark, the text and then the icon, in that order, and with "end" the icon, the text and then
  the mark.

#### The fold

- **FR-012**: A chip or card widget MUST take the values of the choices that stay on show, when the
  widget is made or afterwards on the form's own copy of the widget. With none given, every choice
  MUST be on show.
- **FR-013**: A chosen choice MUST always be on show, whether or not its value was named.
- **FR-014**: Every choice MUST be drawn in the same row of chips or grid of cards in the field's
  order, the choices not on show marked as folded, followed by a button, hidden in the markup,
  that shows a plus sign and the words "More options" or the words the developer gives. The
  package's words MUST be translatable. A chip button MUST be drawn as a chip, and a card button
  as a card-shaped tile.
- **FR-015**: When no choice would stay on show, nothing MUST be folded. When no choice would be
  folded, no button MUST be drawn.
- **FR-016**: The button MUST be a native button, operable by keyboard.

#### The script

- **FR-017**: The package MUST ship one script for the fold, and the chip and card widgets MUST
  name it in their media. The scale and pill widgets MUST name no script.
- **FR-018**: Without the script, every choice MUST be shown, the button MUST stay hidden, and the
  form MUST be answerable and submittable.
- **FR-019**: With the script, the folded choices that are not chosen MUST be hidden and the
  button shown on load. Pressing the button MUST show them in place and remove the button, and
  MUST move the focus to the first choice shown.
- **FR-020**: The script MUST act on choices added to the page after it has loaded, whichever
  script added them, MUST act once on each button however many times the page includes it, and
  MUST use no inline script and no inline event handler.

#### Choices the pack applies

- **FR-021**: Each widget MUST take the form's and the field's size and colour.
- **FR-022**: A variant stated for the form MUST be passed over for these widgets, and one stated
  for the field MUST raise `InvalidChoice` with `kind="variant"`.
- **FR-023**: A drawing stated for a field using one of these widgets MUST raise `InvalidChoice`
  with `kind="drawing"`.
- **FR-024**: Each widget MUST be framed as a group: a fieldset named by a legend holding the
  field's label and the required marker, the help text and the errors describing it, every input
  `aria-invalid` on a field in error and disabled on a disabled field.
- **FR-025**: Each widget MUST be drawn the same through every way the pack draws a field, in a
  formset stacked or as a table, and in every container layout object.

#### Constraints the package keeps

- **FR-026**: Every form in the suite and the demo that uses none of these widgets MUST be drawn
  with the same markup as before the feature.
- **FR-027**: The feature MUST add no field, model, view, URL, stylesheet or dependency.
- **FR-028**: The widgets' text and the mark that shows a choice is chosen MUST meet the standard
  under every shipped theme the suite measures, or be published as known exceptions.

#### Shipping it

- **FR-029**: The README MUST gain a section on the widgets: each widget and its settings, the
  fold and what a page without the script does, how a single choice is cleared, the choices they
  take, which lists each suits, and what is not supported. Each widget and each template MUST
  appear in the README's public surface and template list.
- **FR-030**: The demo MUST gain a Choice widgets page in its Custom widgets group with a live
  example of each widget and its settings, a field in error, a disabled field, a fold, and a fold
  in a formset whose rows can be added.
- **FR-031**: `CONTEXT.md` MUST gain the terms under Key Entities.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1 | FR-001 to FR-015, FR-017, FR-021 to FR-027, FR-029 to FR-031 |
| US-2 | FR-004, FR-007, FR-013, FR-016, FR-018 to FR-020, FR-028, FR-030 |
| US-3 | FR-032 |

### Key Entities

- **Scale**: A single-choice field drawn as one row of segments, one for each choice, with words
  that say what each end means.
- **Pill**: A choice drawn as a small button-like toggle, in a row that wraps.
- **Chip**: A choice drawn as a large toggle that shows a label of any length in full.
- **Card**: A choice drawn as a card holding its label and, where given, a description, an icon
  and a short line above the label.
- **Fold**: The choices of a chip or card widget that are not on show, marked in the row or grid
  with a button after them that shows them.
- **Choices on show**: The choices a developer names to be drawn outside the fold, together with
  every chosen choice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer draws a choice field in any of the four layouts by naming one widget and
  its settings in Python, and writes no template, stylesheet or script.
- **SC-002**: A page that loads daisyUI and no stylesheet from this package draws every one of the
  seven widgets.
- **SC-003**: For every widget and every submission, `cleaned_data` equals what Django's radio or
  checkbox group gives for the same choices.
- **SC-004**: A chosen choice is on show in every drawn form, and, on a page with the script, after
  every load of the page.
- **SC-005**: On a page that does not load the script, every choice of every widget can be reached,
  chosen and submitted.
- **SC-006**: A person can answer every widget on the demo page with a keyboard alone.
- **SC-007**: Every form that uses none of the seven widgets is drawn with the same markup as
  before, and the package installs with no new dependency.

## Assumptions

- The look of the four layouts is the one already agreed for them. It is described for the build
  in `planning-notes.md`, and the build keeps to it within daisyUI's own markup.
- A form drawn with `{% crispy %}` brings its media with it. Any other form needs the host project
  to render the form's media, as for the other widgets that name a script.
- The script's behaviour is tested in a browser, as the other scripts of the package are.
- The widget names and the names of their settings are public surface under Article XI from the
  release that ships them.
