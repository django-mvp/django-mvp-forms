# Feature Specification: Layout objects that decorate a field

**Feature Branch**: `004-field-decorating-layout-objects`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G2 (every layout object django-crispy-forms ships can be used, including prepended or appended text), G3 (labels, help text and errors are tied to their inputs the way current Django expects, so forms work with assistive technology)

**Roadmap**: R2

**Issue**: #8

**Input**: A layout should be able to change how a single field is presented: checkboxes and
radios in a line, a field with buttons attached, text prepended or appended to an input, an
uneditable field, an inline field and a multi-widget field.

## Summary

django-crispy-forms ships nine layout objects that take one field and change how it is presented,
without changing what the field is: `PrependedText`, `AppendedText`, `PrependedAppendedText`,
`InlineCheckboxes`, `InlineRadios`, `FieldWithButtons`, `UneditableField`, `InlineField` and
`MultiWidgetField`. A developer who has selected the template pack, named `daisyui`, places any of them in a form's
`Layout`, imported from django-crispy-forms as its documentation describes, and the pack draws the
field that way as daisyUI markup. The field keeps its label, required marker, help text and
errors, still tied to its input, and the form submits the same data it would without the layout
object.

This feature draws those nine and nothing else. The inputs themselves come from FS-001 (#5) and
FS-002 (#6). The buttons attached to a field come from FS-003 (#7). Size, colour and variant
choices are FS-007 (#11).

## Clarifications

### Session 2026-10-03

- Q: Does an uneditable field send its value when the form is submitted? → A: No. django-crispy-forms
  documents `UneditableField` as drawing a disabled field, and a browser leaves a disabled input
  out of the submission. The pack matches that. A form that needs the value kept declares the field
  disabled in the form class, which is Django's own mechanism. See FR-015 and FR-016.
- Q: Is the text given to `PrependedText` and `AppendedText` escaped? → A: No. It is written by the
  developer in the layout, and django-crispy-forms documents that it may be markup, an icon for
  example. The pack draws it as given. Everything that comes from the form or from a person
  using it is escaped as usual. See FR-007 and FR-008.
- Q: An inline field has no visible label. Does it still show its errors? → A: Yes. The label is
  the only thing an inline field gives up, and it stays available to assistive technology. Errors
  and help text are drawn and tied to the input as for any other field. See FR-018 and FR-019.
- Q: Which feature draws the buttons in a field with buttons? → A: FS-003 (#7). This feature
  attaches whatever button layout objects the pack draws and does not define any. That makes #7 a
  dependency alongside #6. See FR-012.
- Q: `PrependedText` and `FieldWithButtons` accept an `input_size` argument holding another pack's
  class name. What does it do here? → A: Nothing is promised. The field is drawn and no error is
  raised. Choosing a size is FS-007 (#11). See FR-027.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Text prepended or appended to an input (Priority: P1)

A developer has an amount field and wants the currency shown in front of it, or a weight field
with the unit after it, or a username with a domain on the end. They wrap the field's name in
`PrependedText`, `AppendedText` or `PrependedAppendedText` in the layout. The pack draws the text
attached to the input as one unit, using daisyUI's own way of attaching things to an input.

**Why this priority**: GOALS.md names prepended and appended text in G2, and it is the most used
of the nine. It also establishes how something is attached to an input, which User Story 3 reuses.

**Independent Test**: Build a form with one text field, wrap it in each of the three layout
objects in turn, render it with the pack, and check that the text is drawn attached to the input,
that the label, help text and errors are still tied to the input, and that the submitted data is
unchanged.

**Acceptance Scenarios**:

1. **Given** a layout that wraps a text field in `PrependedText` with some text, **When** the form
   is rendered, **Then** the text is drawn before the input inside one attached group, and the
   field's label and help text are drawn once for the group.
2. **Given** a layout that wraps a text field in `AppendedText`, **When** the form is rendered,
   **Then** the text is drawn after the input inside one attached group.
3. **Given** a layout that wraps a field in `PrependedAppendedText` with both texts, **When** the
   form is rendered, **Then** both are drawn, one on each side of the input, in the same group.
4. **Given** `PrependedAppendedText` with only one of the two texts set, **When** the form is
   rendered, **Then** only that one is drawn and no empty attachment appears on the other side.
5. **Given** a bound form whose wrapped field failed validation, **When** the form is rendered,
   **Then** the field's errors are drawn for the group and tied to the input, and the input is
   marked invalid, exactly as the same field would be without the layout object.
6. **Given** a wrapped field, **When** the form is rendered, **Then** the prepended or appended
   text is tied to the input so that assistive technology announces it with the field.
7. **Given** a wrapped field whose widget is a select, **When** the form is rendered, **Then** the
   text is drawn attached to the select in the same way.
8. **Given** a form whose field is wrapped, **When** it is submitted with a value, **Then** the
   form receives the same data it would receive with the field unwrapped.
9. **Given** the demo project, **When** its page for prepended and appended text is opened,
   **Then** it shows each of the three layout objects on a field that is valid and on a field that
   has an error.

---

### User Story 2 - Checkboxes and radios in a line (Priority: P1)

A developer has a short choice field, a yes/no/unsure radio or three or four checkboxes, and does
not want it to take a row per option. They wrap the field's name in `InlineRadios` or
`InlineCheckboxes`. The pack draws the same options FS-002 would draw stacked, arranged along a
line instead, wrapping onto further lines when there is not enough room.

**Why this priority**: Short choice groups are in most real forms, and a stacked group of three
radios is the thing a developer most often wants to change about a plain form.

**Independent Test**: Build a form with a radio field and a multiple-choice checkbox field, wrap
each in its inline layout object, render with the pack, and check that every option is present
with its own label, that the group's label, help text and errors are intact, that the group is
drawn in the pack's inline arrangement and not the stacked one, and that submitting returns the
same data.

**Acceptance Scenarios**:

1. **Given** a layout that wraps a radio field in `InlineRadios`, **When** the form is rendered,
   **Then** every choice is drawn as a radio with its own label, in the pack's inline arrangement.
2. **Given** a layout that wraps a multiple-choice checkbox field in `InlineCheckboxes`, **When**
   the form is rendered, **Then** every choice is drawn as a checkbox with its own label, in the
   pack's inline arrangement.
3. **Given** an inline group, **When** the form is rendered, **Then** the group keeps the group
   label, required marker and help text that FS-002 gives the stacked group, and assistive
   technology announces the options as one named group.
4. **Given** a bound form whose inline group failed validation, **When** the form is rendered,
   **Then** the errors are drawn for the group and tied to it, as they are for the stacked group.
5. **Given** a form with initial or submitted values for an inline group, **When** the form is
   rendered, **Then** exactly those options are drawn selected.
6. **Given** an inline group, **When** the form is submitted, **Then** the form receives the same
   data it would receive from the stacked group.
7. **Given** a field whose choices are disabled in the form, **When** it is drawn inline, **Then**
   the options are drawn disabled as FS-002 draws them.
8. **Given** the demo project, **When** its page for inline checkboxes and radios is opened,
   **Then** it shows both layout objects, each on a valid field and on a field that has an error.

---

### User Story 3 - A field with buttons attached (Priority: P2)

A developer wants a search box with its button joined to it, or a code field with an "apply"
button on the end. They put the field and one or more button layout objects in `FieldWithButtons`.
The pack draws the input and the buttons as one attached group.

**Why this priority**: Common, but it needs the buttons FS-003 delivers, so it cannot land before
them.

**Independent Test**: Build a form with one text field, place it in `FieldWithButtons` with one
button and then with two, render with the pack, and check that the input and every button are
drawn in one attached group, in the order given, with the field's label, help text and errors
intact.

**Acceptance Scenarios**:

1. **Given** a layout with `FieldWithButtons` holding a field name and one button, **When** the
   form is rendered, **Then** the input and the button are drawn in one attached group, and the
   field's label and help text are drawn once for the group.
2. **Given** `FieldWithButtons` holding a field and several buttons, **When** the form is
   rendered, **Then** every button is drawn, in the order given, after the input.
3. **Given** `FieldWithButtons` whose first item is a `Field` layout object carrying attributes,
   **When** the form is rendered, **Then** those attributes reach the input.
4. **Given** a bound form whose field failed validation, **When** the form is rendered, **Then**
   the errors are drawn for the group and tied to the input, and the input is marked invalid.
5. **Given** a submit button attached to a field, **When** it is pressed, **Then** the form is
   submitted with the button's name and value in the data, as it would be for the same button
   placed anywhere else in the layout.
6. **Given** the demo project, **When** its page for fields with buttons is opened, **Then** it
   shows a field with one button and a field with several, valid and with an error.

---

### User Story 4 - An uneditable field (Priority: P2)

A developer wants a form to show a value the person filling it in is not allowed to change: an
account number on a profile form, a reference on an edit page. They wrap the field's name in
`UneditableField`. The pack draws the field with its current value, disabled.

**Why this priority**: Needed in most edit forms sooner or later, and small, but less common than
the first two.

**Independent Test**: Build a form with an initial value on one field, wrap that field in
`UneditableField`, render with the pack, and check that the value is shown, that the input is
disabled, and that the label and help text are intact.

**Acceptance Scenarios**:

1. **Given** a layout that wraps a field in `UneditableField` and a form with a value for it,
   **When** the form is rendered, **Then** the field's current value is shown and the input is
   disabled, drawn with the disabled state FS-001 and FS-002 give that input.
2. **Given** an uneditable field, **When** the form is rendered, **Then** its label and help text
   are drawn and tied to the input as for any other field.
3. **Given** an uneditable field with no value, **When** the form is rendered, **Then** the field
   is drawn empty and disabled, without error.
4. **Given** an uneditable field whose form field is declared disabled in the form class, **When**
   the form is submitted, **Then** the form keeps the field's initial value, which is Django's
   behaviour for a disabled field.
5. **Given** an uneditable field whose value contains markup characters, **When** the form is
   rendered, **Then** the value is escaped.
6. **Given** the demo project, **When** its page for uneditable fields is opened, **Then** it
   shows an uneditable field beside an editable one.

---

### User Story 5 - An inline field (Priority: P3)

A developer is building a compact form, a filter bar or a one-line sign-up, where a label above
each input takes too much room. They wrap each field's name in `InlineField`. The pack draws the
input without a visible label, offers the label as the input's placeholder, and keeps the label
available to assistive technology.

**Why this priority**: Used in fewer forms than the others, and a developer can get by without it
by writing the placeholder themselves.

**Independent Test**: Build a form with a text field and a single checkbox, wrap both in
`InlineField`, render with the pack, and check that the text input has no visible label but has an
accessible name and a placeholder taken from the label, that the checkbox keeps its label beside
it, and that errors are still drawn.

**Acceptance Scenarios**:

1. **Given** a layout that wraps a text field in `InlineField`, **When** the form is rendered,
   **Then** the input is drawn with no visible label, and its accessible name is the field's label.
2. **Given** an inline field whose widget sets no placeholder, **When** the form is rendered,
   **Then** the field's label is offered as the input's placeholder.
3. **Given** an inline field whose widget already sets a placeholder, **When** the form is
   rendered, **Then** the widget's placeholder is kept.
4. **Given** a single checkbox wrapped in `InlineField`, **When** the form is rendered, **Then**
   the checkbox keeps its label beside it, because a checkbox with no visible label says nothing.
5. **Given** a bound form whose inline field failed validation, **When** the form is rendered,
   **Then** the errors are drawn and tied to the input, and the input is marked invalid.
6. **Given** an inline field with help text, **When** the form is rendered, **Then** the help
   text is tied to the input so assistive technology announces it.
7. **Given** the demo project, **When** its page for inline fields is opened, **Then** it shows a
   short form made of inline fields, valid and with an error.

---

### User Story 6 - Attributes for each part of a multi-widget field (Priority: P3)

A developer has a field drawn by several widgets at once, a split date and time for example, and
wants to give each part its own attributes: a placeholder on the first, a different one on the
second. They wrap the field's name in `MultiWidgetField` and pass the attributes, either one set
for every part or one set per part.

**Why this priority**: Multi-widget fields are the least common of the six, and a field of this
kind already draws without this layout object.

**Independent Test**: Build a form with a split date-and-time field, wrap it in `MultiWidgetField`
with a different attribute for each part, render with the pack, and check that each part carries
its own attribute, that the field has one label, one help text and one set of errors, and that
submitting returns the same data.

**Acceptance Scenarios**:

1. **Given** `MultiWidgetField` with a sequence of attribute sets, one per part, **When** the form
   is rendered, **Then** each part carries the attributes given for its position.
2. **Given** `MultiWidgetField` with a single attribute set, **When** the form is rendered,
   **Then** every part carries those attributes.
3. **Given** a multi-widget field, **When** the form is rendered, **Then** each part is drawn as
   the pack's input for its kind, and the field has one label, one help text and one set of
   errors, which assistive technology announces for the parts as a group.
4. **Given** fewer attribute sets than the field has parts, **When** the form is rendered,
   **Then** the remaining parts are drawn without extra attributes and no error is raised.
5. **Given** a multi-widget field, **When** the form is submitted, **Then** the form receives the
   same data it would receive without the layout object.
6. **Given** the demo project, **When** its page for multi-widget fields is opened, **Then** it
   shows a multi-widget field with different attributes on each part, valid and with an error.

---

### Edge Cases

- A layout object is given a field whose widget it does not suit: prepended text on a checkbox, a
  radio group or a file input, `InlineRadios` on a field with no choices, `MultiWidgetField` on a
  field with one widget. The field is still drawn and still usable. It is never dropped from the
  form without a word. What the decoration looks like in that case is not promised.
- A layout object names a field the form does not have. django-crispy-forms decides what happens,
  according to its `FAIL_SILENTLY` setting, and the pack changes nothing about that.
- Prepended or appended text is an empty string or `None`. No empty attachment is drawn.
- The developer builds prepended or appended text from something a person typed. The pack draws
  that text as markup, so this is unsafe. The documentation says so and says to escape it first.
- `FieldWithButtons` holds a field and no buttons. The field is drawn as a group with nothing
  attached, without error.
- An inline group has many options or long labels. The options wrap onto further lines. None is
  cut off or pushed out of the form.
- An uneditable field wraps a field that is required and not declared disabled in the form class.
  The browser does not send the value, so validation fails for a missing value. This is the
  documented behaviour of a disabled input and the documentation says how to avoid it.
- A decorated field is hidden (its widget is a hidden input). It is drawn as a hidden input with
  no decoration.
- The same field is drawn under any theme. The decoration takes its colours from the host
  project's theme and sets none of its own.
- The form is drawn with the crispy filter, not the crispy tag. django-crispy-forms draws a
  helper's layout only through the tag, so the filter draws the fields without their layout
  objects, as it does for every layout object. The pack changes nothing about that.
  (**Refined** 2026-10-03: this bullet said both draw these layout objects the same way, which
  django-crispy-forms 2.7 does not allow. See decisions.md D19.)

## Requirements *(mandatory)*

### Functional Requirements

Prepended and appended text (User Story 1)

- **FR-001**: The pack MUST draw `PrependedText`, `AppendedText` and `PrependedAppendedText`, each
  with its text and the field's input in one attached group, built from daisyUI's own means of
  attaching things to an input.
- **FR-002**: The pack MUST draw only the texts that are set. An unset or empty text MUST leave no
  empty attachment.
- **FR-003**: The pack MUST draw prepended and appended text on text-like inputs and on selects.
- **FR-004**: The prepended or appended text MUST be tied to the input so that assistive
  technology announces it with the field.
- **FR-005**: The label, required marker, help text and errors MUST be drawn once for the group
  and tied to the input.
- **FR-006**: The input's name, value and submitted data MUST be the same as for the unwrapped
  field.
- **FR-007**: The pack MUST draw prepended and appended text as the developer gave it, markup
  included, as django-crispy-forms documents.
- **FR-008**: The documentation for these layout objects MUST state that the text is drawn as
  markup and must not be built from untrusted input without escaping.

Inline checkboxes and radios (User Story 2)

- **FR-009**: The pack MUST draw `InlineRadios` and `InlineCheckboxes` with every choice of the
  field as the radio or checkbox FS-002 draws, each with its own label, in an inline arrangement
  that is distinct from the stacked group and that wraps when the options do not fit on one line.
- **FR-010**: An inline group MUST keep the group label, required marker, help text, errors,
  grouping for assistive technology and disabled state that FS-002 gives the stacked group.
- **FR-011**: An inline group MUST show the same options selected, and submit the same data, as
  the stacked group for the same form.

Field with buttons (User Story 3)

- **FR-012**: The pack MUST draw `FieldWithButtons` with the field's input and every button given
  to it in one attached group, in the order given. The buttons are the button layout objects
  FS-003 draws, and this feature defines none of its own.
- **FR-013**: When the first item of `FieldWithButtons` is a `Field` layout object, its attributes
  MUST reach the input.
- **FR-014**: The label, required marker, help text and errors of a field with buttons MUST be
  drawn once for the group and tied to the input.

Uneditable field (User Story 4)

- **FR-015**: The pack MUST draw `UneditableField` with the field's current value shown and the
  input disabled, using the disabled state FS-001 and FS-002 give that input. The label and help
  text MUST be drawn and tied to the input as usual.
- **FR-016**: The documentation for `UneditableField` MUST state that the browser does not submit
  the value, and that a form which needs the value kept declares the field disabled in the form
  class.

Inline field (User Story 5)

- **FR-017**: The pack MUST draw `InlineField` with no visible label for the input, and with the
  field's label as the input's accessible name.
- **FR-018**: An inline field whose widget sets no placeholder MUST offer the field's label as the
  placeholder. A placeholder set on the widget MUST be kept.
- **FR-019**: An inline field MUST draw its errors, tie its errors and help text to the input, and
  mark the input invalid when the field has errors.
- **FR-020**: A single checkbox wrapped in `InlineField` MUST keep its label visible beside it.

Multi-widget field (User Story 6)

- **FR-021**: The pack MUST draw `MultiWidgetField` so that a sequence of attribute sets is
  applied one per part, in order, and a single attribute set is applied to every part. Parts
  beyond the end of the sequence are drawn without extra attributes.
- **FR-022**: Each part of a multi-widget field MUST be drawn as the pack's input for its kind.
  The field MUST have one label, one help text and one set of errors, announced by assistive
  technology for the parts as a group.

All nine layout objects (every user story)

- **FR-023**: A layout MUST use these layout objects as django-crispy-forms ships and documents
  them, imported from django-crispy-forms. The pack supplies how they are drawn and MUST NOT
  require a class of its own in their place.
- **FR-024**: The arguments django-crispy-forms documents for each layout object (`css_class`,
  `wrapper_class`, `css_id` where it applies, `template`, and extra HTML attributes) MUST have the
  effect it documents.
- **FR-025**: A layout object given a field whose widget it does not suit MUST still draw a
  usable field and MUST NOT drop it from the form.
- **FR-026**: Everything drawn from the form or from submitted data (labels, choice labels, help
  text, errors, values) MUST be escaped by the template layer. The only text drawn as markup is
  the developer's own, under FR-007.
- **FR-027**: An `input_size` argument MUST be accepted without error. This feature gives it no
  meaning.
- **FR-028**: The templates for these layout objects MUST be plain Django templates that use
  neither django-cotton nor daisy-cotton, MUST use only daisyUI's standard classes and modifiers,
  and MUST add no stylesheet, script or runtime dependency.
- **FR-029**: Any text the pack itself adds for these layout objects MUST be translatable.
- **FR-030**: The demo project MUST have a page, reachable from its menu, for each of the six
  kinds of decoration in this specification, showing every layout object of that kind on a valid
  field and, where the layout object can show an error, on a field with an error.
- **FR-031**: The README's public surface MUST list the nine layout objects, with where to import
  each from and what the pack draws for it. The CHANGELOG MUST record them.

### Key Entities

- **Layout object**: one of the nine django-crispy-forms classes named in the summary. It wraps
  one field (and, for `FieldWithButtons`, some buttons) and says how that field is presented.
- **Field**: the Django form field being decorated. Its validation, cleaning and widget are
  unchanged by the layout object.
- **Attached group**: the input together with the text or buttons joined to it, drawn as one unit
  with one label, one help text and one set of errors.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All nine layout objects django-crispy-forms ships for decorating a single field can
  be placed in a layout and drawn by the pack. None is left without a template.
- **SC-002**: A layout written from django-crispy-forms' own documentation for any of the nine
  draws with the pack with no change to the layout code.
- **SC-003**: In every one of the nine, in valid and invalid states, every input has an accessible
  name, and every help text and error is tied to the input or group it belongs to.
- **SC-004**: For every one of the nine except `UneditableField`, a form submits the same data
  with the layout object as without it.
- **SC-005**: The demo pages for this feature draw correctly on a page that loads daisyUI's full
  CDN build, with no build step in the host project.
- **SC-006**: A developer can find each of the nine in the README's public surface and see each
  one drawn in the demo project.

## Assumptions

- FS-001 (#5) delivers how a field's label, required marker, help text and errors are drawn and
  tied to its input, and the text-like inputs. This feature reuses that and does not redefine it.
- FS-002 (#6) delivers radios, checkboxes, checkbox and radio groups, selects, and the disabled
  and read-only states. Inline groups and the uneditable field are drawn from those.
- FS-003 (#7) delivers the button layout objects. `FieldWithButtons` needs at least one of them,
  so this feature depends on #7 as well as #6. `StrictButton` is one of the buttons FS-003 draws.
- How a multi-widget field draws when no layout object is involved belongs to FS-001 and FS-002.
  This feature adds only the per-part attributes of `MultiWidgetField`.
- Size, colour and variant for inputs, attached text and buttons are FS-007 (#11). Everything
  here is drawn at daisyUI's defaults. Whether attached text and buttons follow the field's size
  is raised in #15.
- Laying out a whole form in one line is the job of the structural layout objects in FS-003.
  `InlineField` only changes how one field is presented.
- A general way to join arbitrary inputs together, and floating labels, are roadmap item R7.
- Class names another pack understands, passed in `css_class` or `input_size`, carry no meaning
  here. Keeping layouts written for another pack working is not a goal of this package.
- A host project that builds its own Tailwind stylesheet arranges for the pack's classes to be
  included. That is outside this feature.
- django-crispy-forms 2.7 or later, the version this package already requires, ships all nine.
