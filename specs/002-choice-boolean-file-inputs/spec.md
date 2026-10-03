# Feature Specification: Choice, boolean and file inputs drawn as daisyUI

**Feature Branch**: `002-choice-boolean-file-inputs`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G1 (any Django form draws as correct daisyUI markup with no per-form work), G3 (labels, help text and errors are tied to their inputs the way current Django expects)

**Roadmap**: R1, Plain forms draw as daisyUI

**Issue**: [#6](https://github.com/django-mvp/django-mvp-forms/issues/6)

**Depends on**: [#5](https://github.com/django-mvp/django-mvp-forms/issues/5), which draws text inputs and delivers the label, required marker, help text, field errors and form-wide errors that every field in this feature is drawn with.

**Input**: "The remaining widgets Django ships should draw as their daisyUI counterparts: select and
multiple select, radio groups, single checkboxes and checkbox groups, file inputs and hidden
inputs, with disabled and read-only states. With this, any plain Django form looks right with no
per-form work."

## Overview

Once [#5](https://github.com/django-mvp/django-mvp-forms/issues/5) lands, a host project that
selects the pack gets its text-like fields drawn as daisyUI inputs. Every other widget Django ships
still falls outside it: a form with a dropdown, a tick box or a file upload is only partly drawn.

This feature draws the rest. A select, a multiple select, a radio group, a single checkbox, a
checkbox group and a file input each come out as daisyUI's own input for the job. A hidden input
is carried in the form without taking up any room. Each visible field gets the same label,
required marker, help text and errors as a text input, tied to its input so a screen reader
announces them. A field the developer marked as disabled is drawn as unavailable.

With #5 and this feature together, a developer can hand any form built from Django's own widgets
to the pack and get a complete daisyUI form back, without writing a layout and without touching a
single field.

The feature draws inputs and nothing else. Other work stays with its own issue:

- text, email, number, password, URL, date, time and textarea inputs, and the label, required
  marker, help text and errors themselves
  ([#5](https://github.com/django-mvp/django-mvp-forms/issues/5))
- checkboxes and radios set in a line, uneditable fields and multi-widget fields placed from a
  layout ([#8](https://github.com/django-mvp/django-mvp-forms/issues/8))
- the delete and ordering inputs of a set of forms
  ([#10](https://github.com/django-mvp/django-mvp-forms/issues/10))
- size, colour and variant chosen from Python
  ([#11](https://github.com/django-mvp/django-mvp-forms/issues/11))
- a boolean field drawn as a toggle or a switch
  ([#12](https://github.com/django-mvp/django-mvp-forms/issues/12))

## What a person sees

The inputs and states below are everything this feature puts in front of a person. Each one is
daisyUI's stock input for the job. How it looks is daisyUI's decision and the host project's theme,
not this specification's.

A person filling in a form meets these inputs:

- a select, with one choice picked from a list, including a list divided into named groups
- a multiple select, with several choices picked
- a radio group, with one option picked from several shown at once
- a single checkbox
- a checkbox group, with any number of options ticked
- a file input, empty, and a file input for a field that already holds a file
- nothing at all where a hidden input sits

Each visible input appears in these states: untouched, holding a value, required, with help text,
with an error after a failed submission, and disabled.

A developer looking at the demo project sees one page that shows every one of these inputs in
every one of these states.

## Clarifications

### Session 2026-10-03

- Q: Do the disabled and read-only states in this feature also cover the text inputs
  [#5](https://github.com/django-mvp/django-mvp-forms/issues/5) draws? → A: No. This feature
  covers the states of the inputs it draws. See FR-015 and the assumptions.
- Q: A select, a checkbox, a radio button and a file input have no read-only state in HTML. What
  does read-only mean for them? → A: The pack does not invent one. A read-only attribute the
  developer sets reaches the input unchanged, and a field that must not be edited is marked
  disabled. See FR-016.
- Q: Django ships widgets made of several inputs, such as a date picked from three selects. Which
  feature draws them? → A: Each part is drawn by whichever feature draws that kind of input, so
  the three selects are drawn here and the text inputs of a split date and time are #5's. See
  FR-005.
- Q: What happens to an error on a hidden field, which has no place on the page to show it? → A:
  It is shown with the form-wide errors, so the person is never left with a rejected form and no
  message. See FR-013.
- Q: A required checkbox group cannot use the browser's own required check, because that would
  demand every box be ticked. What does required mean for a group? → A: The required marker is
  shown as for any field, and the browser's own check is used only where Django itself uses it.
  See FR-009.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A field with choices draws as a select (Priority: P1)

A developer has a form with a field whose value comes from a list of choices. They select the
pack and draw the form without writing a layout. The field arrives as daisyUI's select, with its
label, required marker, help text and errors, and with the current value already picked. A field
that accepts several choices arrives as a multiple select with all of its current values picked.

**Why this priority**: A dropdown is the most common input after a text box. A form with one in
it cannot be called drawn until this works.

**Independent Test**: Draw a form holding a single-choice field, a multiple-choice field and a
field with grouped choices, with no layout, and check that each is daisyUI's select, carries its
label, help text and errors, and shows its current value.

**Acceptance Scenarios**:

1. **Given** a form with a single-choice field drawn by the pack with no layout, **When** the page
   is drawn, **Then** the field is daisyUI's select, every choice is offered, and the field's label
   is tied to the select.
2. **Given** a single-choice field that already holds a value, **When** the form is drawn,
   **Then** that choice is the one picked.
3. **Given** a multiple-choice field holding several values, **When** the form is drawn, **Then**
   the field is a multiple select and every one of those values is picked.
4. **Given** a field whose choices are divided into named groups, **When** the form is drawn,
   **Then** each choice sits under its group's name.
5. **Given** a select field submitted with an invalid value, **When** the form is drawn again,
   **Then** the field's error is shown with the field and is tied to the select so assistive
   technology announces it.
6. **Given** a boolean field that allows "unknown" as well as yes and no, **When** the form is
   drawn, **Then** it is a select offering all three.
7. **Given** a date field drawn as separate selects for its parts, **When** the form is drawn,
   **Then** each part is daisyUI's select and the field has one label, one help text and one set
   of errors.

---

### User Story 2 - A boolean field draws as a checkbox (Priority: P1)

A developer has a form with a boolean field, such as an agreement to terms. Drawn by the pack,
the field arrives as daisyUI's checkbox. Its label, help text and errors are tied to the
checkbox, and the box is ticked when the field's value is true.

**Why this priority**: A single checkbox relates to its label differently from every other field,
so it is the one most often drawn wrong by a pack that treats every field alike.

**Independent Test**: Draw a form with one boolean field, unticked and then ticked, and check
that it is daisyUI's checkbox, that its label is tied to it, and that the tick follows the value.

**Acceptance Scenarios**:

1. **Given** a form with a boolean field drawn by the pack with no layout, **When** the page is
   drawn, **Then** the field is daisyUI's checkbox and its label is tied to the checkbox, so
   activating the label ticks the box.
2. **Given** a boolean field whose value is true, **When** the form is drawn, **Then** the
   checkbox is ticked. **Given** its value is false, **Then** it is not.
3. **Given** a required boolean field submitted unticked, **When** the form is drawn again,
   **Then** the field's error is shown with the field and tied to the checkbox.
4. **Given** a boolean field with help text, **When** the form is drawn, **Then** the help text is
   shown with the field and tied to the checkbox.

---

### User Story 3 - Options shown at once draw as a radio group or a checkbox group (Priority: P1)

A developer chooses to show a field's choices all at once: as radio buttons where one may be
picked, or as checkboxes where several may. Drawn by the pack, each option is daisyUI's radio or
checkbox with its own label, and the options are presented as one group that carries the field's
label, required marker, help text and errors.

**Why this priority**: Groups are where accessibility most often breaks. Each option needs its
own label and the group needs a name of its own, and a screen reader user who hears neither
cannot answer the question.

**Independent Test**: Draw a form with a radio group and a checkbox group and check that each
option is daisyUI's input with its own label, that the group is named by the field's label, and
that help text and errors are announced with the group.

**Acceptance Scenarios**:

1. **Given** a single-choice field shown as radio buttons, **When** the form is drawn, **Then**
   every choice is daisyUI's radio, each has its own label tied to it, and only one can be picked.
2. **Given** a multiple-choice field shown as checkboxes, **When** the form is drawn, **Then**
   every choice is daisyUI's checkbox, each has its own label tied to it, and any number can be
   ticked.
3. **Given** either kind of group, **When** assistive technology reaches it, **Then** the options
   are announced as one group named by the field's label.
4. **Given** a group whose field holds a value, **When** the form is drawn, **Then** exactly the
   options matching that value are picked.
5. **Given** a group submitted with an invalid value, **When** the form is drawn again, **Then**
   the field's error is shown once for the group, not once per option, and is announced with the
   group.
6. **Given** a required checkbox group, **When** a person ticks one option and submits, **Then**
   the browser does not hold the form back for the options left unticked.
7. **Given** a group whose choices are divided into named groups, **When** the form is drawn,
   **Then** each option sits under its group's name.

---

### User Story 4 - A file field draws as a file input (Priority: P2)

A developer has a form with a file or image field. Drawn by the pack, it arrives as daisyUI's
file input with its label, required marker, help text and errors. When the field already holds a
file, the person can see which file that is and reach it, and where the field is optional they can
ask for it to be removed.

**Why this priority**: File fields are less common than choices and booleans, but a form that
edits a record with an upload is unusable if the person cannot tell whether a file is already
there.

**Independent Test**: Draw a form with an optional file field, first empty and then holding a
file, and check that it is daisyUI's file input, that the existing file is linked, and that the
removal checkbox is offered and tied to its own label.

**Acceptance Scenarios**:

1. **Given** a form with a file field drawn by the pack with no layout, **When** the page is
   drawn, **Then** the field is daisyUI's file input and its label is tied to the input.
2. **Given** an optional file field that already holds a file, **When** the form is drawn,
   **Then** the person is shown a link to the current file, a checkbox to remove it, and a way to
   choose a replacement.
3. **Given** a required file field that already holds a file, **When** the form is drawn,
   **Then** the current file is linked and no removal checkbox is offered.
4. **Given** a file field whose widget accepts several files, **When** the form is drawn,
   **Then** the input lets the person choose more than one.
5. **Given** a file field submitted with a file the form rejects, **When** the form is drawn
   again, **Then** the field's error is shown with the field and tied to the input.

---

### User Story 5 - A hidden field is carried without being seen (Priority: P2)

A developer has a form with a hidden field carrying a value the person never edits. Drawn by the
pack, the value travels with the form and nothing about the field shows on the page. If the hidden
value is rejected, the person still learns that something went wrong.

**Why this priority**: Hidden fields are in most real forms. Drawn like a visible field they
leave a stray label or an empty gap, and an error on one disappears.

**Independent Test**: Draw a form with a hidden field, submit it, and check that the value
arrives, that the page shows no label, help text or space for the field, and that an invalid
hidden value produces a visible error.

**Acceptance Scenarios**:

1. **Given** a form with a hidden field drawn by the pack with no layout, **When** the page is
   drawn, **Then** the field's value is in the form and no label, required marker, help text or
   empty space is drawn for it.
2. **Given** a hidden field holding several values, **When** the form is submitted, **Then**
   every value arrives.
3. **Given** a hidden field submitted with an invalid value, **When** the form is drawn again,
   **Then** its error is shown with the form-wide errors.

---

### User Story 6 - A disabled field is drawn as unavailable (Priority: P2)

A developer marks a field as disabled because the person may see its value and may not change
it. Drawn by the pack, every input belonging to that field is unavailable, in daisyUI's disabled
state, and still shows the field's value.

**Why this priority**: The state applies to every input in this feature, so it follows them. It
matters most in a group, where disabling the field has to reach every option.

**Independent Test**: Draw a form in which a select, a radio group, a checkbox, a checkbox group
and a file field are each disabled, and check that no input of any of them can be changed and
that each still shows its value.

**Acceptance Scenarios**:

1. **Given** a disabled select, checkbox or file field, **When** the form is drawn, **Then** its
   input is unavailable and announced as unavailable by assistive technology.
2. **Given** a disabled radio group or checkbox group, **When** the form is drawn, **Then** every
   option in the group is unavailable.
3. **Given** a disabled field that holds a value, **When** the form is drawn, **Then** the value
   is still shown.
4. **Given** a disabled file field that already holds a file, **When** the form is drawn,
   **Then** the removal checkbox is unavailable too.
5. **Given** a widget on which the developer has set a read-only attribute, **When** the form is
   drawn, **Then** the attribute is on the input exactly as the developer set it.

---

### User Story 7 - Every input and state can be seen in the demo project (Priority: P3)

A contributor, or a developer deciding whether to adopt the pack, opens the demo project and finds
a page showing each input from this feature in each of its states. The README lists the same
inputs under its public surface.

**Why this priority**: How an input looks is judged by eye, so there has to be somewhere to look.
It comes last because it shows the other stories and adds no behaviour of its own.

**Independent Test**: Open the demo page and check that it draws without error, that every widget
this feature covers appears on it, and that each appears in every state listed under "What a
person sees".

**Acceptance Scenarios**:

1. **Given** the demo project is running, **When** a developer follows its menu, **Then** they
   reach a page showing every input this feature draws.
2. **Given** that page, **When** it is drawn, **Then** each input appears untouched, holding a
   value, required, with help text, with an error and disabled.
3. **Given** the README, **When** a developer reads its public surface, **Then** every widget
   this feature draws is listed there.

---

### Edge Cases

- A choice field with no choices at all draws its label and an empty input, and the page does not
  break.
- A choice label, an option group's name or a file name that contains markup is shown as text and
  never run as markup.
- A host project's own widget that subclasses one of Django's is drawn the way its parent is,
  unless that widget names a template of its own.
- A developer's own attributes on a widget, including extra classes and `data-` attributes, are
  kept on the input. Extra classes sit beside the pack's and do not replace them.
- A select holding a value that is no longer among its choices draws with nothing wrongly picked.
- A widget that marks a single option as unavailable keeps that option unavailable while the rest
  of the field stays usable.
- A form whose only fields are hidden draws no visible fields and still submits its values.
- A hidden field that is also disabled is drawn as Django draws it, with nothing shown.
- A third-party package's widget is not covered by this feature, even where it looks like one of
  Django's.

## Requirements *(mandatory)*

### Functional Requirements

Drawing

- **FR-001**: With the pack selected, a form drawn without a layout MUST draw each of these Django
  widgets as daisyUI's matching input: `Select`, `NullBooleanSelect`, `SelectMultiple`,
  `RadioSelect`, `CheckboxInput`, `CheckboxSelectMultiple`, `FileInput` and `ClearableFileInput`.
  (Stories 1 to 4)
- **FR-002**: `HiddenInput` and `MultipleHiddenInput` MUST be carried in the form with their
  values and MUST draw no label, required marker, help text or visible space. (Story 5)
- **FR-003**: Every input in this feature MUST draw the same whether the form is drawn with the
  crispy filter or the crispy tag. (Stories 1 to 6)
- **FR-004**: A widget that subclasses one of the widgets in FR-001 or FR-002 MUST draw the way
  its parent does, unless it names a template of its own. (Stories 1 to 5)
- **FR-005**: A Django widget made of several inputs MUST have each part drawn by the rule for
  that kind of input. Parts that are selects or hidden inputs are drawn by this feature, and the
  field keeps one label, one help text and one set of errors. (Stories 1 and 5)

Labels, help text and errors

- **FR-006**: Every visible field in this feature MUST be drawn with the label, required marker,
  help text and field errors that [#5](https://github.com/django-mvp/django-mvp-forms/issues/5)
  delivers, tied to the field's input so assistive technology announces them. This feature MUST
  NOT introduce a second way of drawing any of them. (Stories 1 to 4)
- **FR-007**: A radio group and a checkbox group MUST be presented to assistive technology as one
  group named by the field's label. Each option MUST have its own label tied to its own input.
  The field's help text and errors MUST be shown once for the group and announced with it.
  (Story 3)
- **FR-008**: An input whose field has an error MUST be marked as invalid for assistive
  technology. In a group, this applies to the group's inputs as current Django marks them.
  (Stories 1 to 4)
- **FR-009**: The required marker MUST be shown for every required visible field. The browser's
  own required check MUST be applied only where Django applies it for that widget, so a required
  checkbox group can be submitted with some options unticked and a file field that already holds
  a file can be submitted without choosing another. (Stories 1 to 4)

Values

- **FR-010**: Each input MUST show the field's current value: the picked choice or choices in a
  select, the picked options in a group, and the tick in a checkbox. This holds for a form drawn
  for the first time and for one drawn again after a failed submission. (Stories 1 to 3)
- **FR-011**: Choices divided into named groups MUST be drawn under their group's name, in a
  select and in a radio or checkbox group alike. (Stories 1 and 3)
- **FR-012**: A file field that already holds a file MUST show a link to that file and a way to
  choose a replacement. Where the field is optional it MUST also offer a removal checkbox with its
  own label tied to it. Where the field is required it MUST NOT. A file widget that accepts
  several files MUST let the person choose several. (Story 4)
- **FR-013**: An error on a hidden field MUST be shown to the person with the form-wide errors.
  It MUST NOT be dropped. (Story 5)

States

- **FR-014**: A field marked as disabled MUST have every one of its inputs drawn in daisyUI's
  disabled state and announced as unavailable: the select, the checkbox, the file input, every
  option of a group, and the removal checkbox of a file field. The field's value MUST still be
  shown. (Story 6)
- **FR-015**: The disabled and read-only behaviour in this feature MUST cover every input this
  feature draws. It does not define those states for the inputs
  [#5](https://github.com/django-mvp/django-mvp-forms/issues/5) draws. (Story 6)
- **FR-016**: A read-only attribute a developer sets on a widget MUST reach the input unchanged.
  The pack MUST NOT imitate a read-only state on an input that HTML gives none: a select, a
  checkbox, a radio button or a file input. (Story 6)

Whatever the input

- **FR-017**: Attributes a developer sets on a widget MUST be kept on the input. Classes among
  them MUST be added to the pack's own and never replace them. An attribute a widget sets on a
  single option MUST be kept on that option. (Stories 1 to 6)
- **FR-018**: Choice labels, option group names, file names and every other value drawn into the
  page MUST be escaped by the template layer. (Stories 1 to 5)
- **FR-019**: The inputs MUST be built from daisyUI's standard classes and modifiers only, so
  they display correctly on a page that loads daisyUI's full CDN build with no build step. The
  templates MUST be plain Django templates, and the feature MUST add no stylesheet and no class of
  its own. (Stories 1 to 6)
- **FR-020**: Any text the pack itself adds to the page MUST be translatable. Text that comes from
  Django's own widgets is left as Django supplies it. (Stories 1 to 6)

Demo and documentation

- **FR-021**: The demo project MUST have a page, reachable from its menu, showing every input
  this feature draws in each of these states: untouched, holding a value, required, with help
  text, with an error, and disabled. (Story 7)
- **FR-022**: The README's public surface MUST list the widgets this feature draws, and the
  CHANGELOG MUST record them, in the same pull request as the code. (Story 7)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A form using every widget Django ships other than the text-like ones draws through
  the pack with no layout and no per-field code, and none of its inputs is left in the browser's
  unstyled default.
- **SC-002**: A developer moving a plain Django form onto the pack changes nothing in the form
  class: no widget is swapped, and no attribute is added to make an input look right.
- **SC-003**: On a page showing every input from this feature, every visible input has a name
  assistive technology can announce, every group has a name of its own, and every help text and
  error is announced with the input or group it belongs to. An automated accessibility check of
  that page reports no labelling or naming failures.
- **SC-004**: The same page displays correctly when the only styling it loads is daisyUI's full
  CDN build, with no build step in the host project.
- **SC-005**: A form rejected because of any field in this feature, hidden fields included, always
  shows the person at least one error message.
- **SC-006**: Every input this feature draws can be seen in every one of its states on the demo
  project, without writing any code.

## Assumptions

- [#5](https://github.com/django-mvp/django-mvp-forms/issues/5) lands first. This feature reuses
  its label, required marker, help text, field errors and form-wide errors as they are and
  specifies none of them. Whatever #5 decides for a widget the pack does not recognise applies
  here too.
- "Disabled" means Django's own `disabled` field argument. "Read-only" means an attribute a
  developer puts on a widget. The text inputs of #5 are the only inputs with a read-only state in
  HTML, and how they look in it belongs to that feature. A layout object that shows a field as
  uneditable is [#8](https://github.com/django-mvp/django-mvp-forms/issues/8).
- The widgets covered are those in Django's own `django.forms`. Widgets from `django.contrib`
  packages, such as the admin's, and from third-party packages are out of scope.
- A boolean field is drawn as a checkbox. Drawing it as a toggle or a switch is
  [#12](https://github.com/django-mvp/django-mvp-forms/issues/12).
- Setting a group's options in a line is
  [#8](https://github.com/django-mvp/django-mvp-forms/issues/8), and this feature offers no such
  choice.
- Inputs come at daisyUI's default size, colour and variant. Choosing others is
  [#11](https://github.com/django-mvp/django-mvp-forms/issues/11).
- Which template paths a host project may override, and the promise that they stay stable, is
  roadmap item R6 and not settled here.
- The words Django's file widget shows beside an existing file come from Django and its
  translations. This feature does not reword them.
- Marking the form as able to carry files when it holds a file field is the form tag's job, which
  django-crispy-forms already does, and is not part of drawing the input.
- The host project supplies daisyUI. Legibility under every daisyUI theme is roadmap item R8.
