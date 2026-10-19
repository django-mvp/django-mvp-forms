# Feature Specification: Tom Select widgets for choice fields

**Feature Branch**: `017-tom-select-widgets`

**Created**: 2026-10-11

**Status**: Approved

**Serves**: G11 (the package offers its own fields and widgets, each looking native beside the
pack's own inputs) and G4 (the variant, colour and size of any form component can be set from
Python)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #170

**Depends on**: nothing still to be delivered. It builds on the select the pack already draws
(FS-002), the size, colour and variant choices of FS-007, and the stylesheet for Tom Select's
parts that FS-014 shipped.

**Input**: A developer should be able to put a [Tom Select](https://tom-select.js.org/) control
on an ordinary Django choice field by naming a widget, with the options written into the page
along with the form. There is a widget for a single choice and one for several. Neither needs a
view, a URL or django-tomselect. The host project loads Tom Select itself.

## Why

daisyUI's own multiple select works for a handful of short options. With longer labels or more
than a few options it is hard to read and hard to use. django-tomselect gives a better control,
and the pack already draws it, but its fields are built to load their options from a view. A
project that wants the same control over a short, fixed list has to write an endpoint for every
field.

Most Django choice fields are not like that. Their options are known when the form is built and
are written into the page with it. These widgets give those fields the same control, so a form
can use one select interface throughout and write an endpoint only where the list is too long to
send with the page.

## Clarifications

### Session 2026-10-11

The maintainer confirmed the reading of the feature before this was written: two widgets, the
options they take from Python, what is left out, and that the feature has no sketch. The coverage
scan then found seven ambiguities. Each was resolved from that conversation, the goals, the
constitution and the decision records. Longer rationale is in `decisions.md`.

- **Q: What are the widgets called, and where do they live?**
  A: `TomSelect` and `TomSelectMultiple`, in `mvp_forms.widgets`, beside Django's `Select` and
  `SelectMultiple`, which they stand in for. Recorded as FR-001.

- **Q: Who supplies Tom Select?**
  A: The host project, as it supplies IMask for the mask widgets. The package ships the widgets
  and one script that starts a control on each select they draw. django-tomselect's own script
  already puts Tom Select on the page, so a page that loads it needs no second copy. A page
  without django-tomselect loads Tom Select from wherever the project keeps it. Recorded as
  FR-016 to FR-021.

- **Q: Which of Tom Select's settings can be stated from Python?**
  A: A placeholder, a clear button, a remove button on each chosen value, and the largest number
  of values that may be chosen. These are the settings a short list needs and each is plain
  data. Anything else, including every setting that is a JavaScript function, is reached through
  the event the script sends with the Tom Select instance. Recorded as FR-006 to FR-009 and
  FR-022.

- **Q: Is there a limit on the number of options?**
  A: None is enforced. Every option the field has can be found by typing, however many there
  are. The README says the widgets suit a list short enough to send with the page, and names
  django-tomselect as the answer for a long one, since every option is written into the page each
  time the form is drawn. Recorded as FR-005 and FR-030.

- **Q: How does a control get started in a formset row added in the browser?**
  A: The script starts it, whichever script added the row, as the mask script does for a masked
  input. The developer and django-mvp write nothing. Recorded as FR-019.

- **Q: How does a developer mark one option as unavailable?**
  A: Django has no argument for that, and this feature adds none. A developer who needs it writes
  the `disabled` attribute on the option from a subclass, the way they would for a stock select.
  The control shows such an option and does not let it be chosen. Recorded as FR-011.

- **Q: The stylesheet `mvp_forms/tomselect.css` was shipped for django-tomselect, and ADR 0042
  gives each supported package a stylesheet of its own. Do these widgets get another?**
  A: No. That stylesheet styles Tom Select's own parts, and these widgets build the same parts.
  A control from this package and one from django-tomselect are drawn by the same rules and look
  the same on one page. The decision record is rewritten to say the stylesheet serves Tom Select
  controls from either source. Recorded as FR-012, FR-013 and FR-032.

### Session 2026-10-18

The maintainer asked for the control the demo drew from a subclass, a count in place of the
tags with a tick on each chosen option (issue #182), to be a setting of the multiple widget, and
settled the questions the issue raised. They are recorded in ADR 0057.

- **Q: Is it one setting for the whole control or one per plugin?**
  A: One, `counted`, on `TomSelectMultiple`. It turns on both `checkbox_options` and
  `dropdown_input`. Recorded as FR-034.

- **Q: How are the two words in the control translated?**
  A: They are settings of the widget, `none_text` and `count_text`, whose defaults, "Nothing
  selected" and "selected", are translated. Recorded as FR-035.

- **Q: Should Backspace in an empty search box go on removing the value chosen last?**
  A: Yes. Tom Select's default is kept. Recorded as FR-036.

- **Q: Does the single widget get the search box in its dropdown as well?**
  A: No. `TomSelect` is unchanged. Recorded as FR-034.

- **Q: Where are the rules that draw it?**
  A: In `mvp_forms/tomselect.css`, under Article XIV: every colour from the daisyUI theme.
  Recorded as FR-037.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer gives a multiple choice field a Tom Select control (Priority: P1)

A developer has a field where a person picks several values from a list known when the form is
built: the days a shop opens, the topics of an article, the members of a small team. They name
the multiple widget on the field and change nothing else. A person filling in the form types to
find an option, picks it, sees it listed in the control as a value of its own, and picks more.

**Why this priority**: Choosing several values is where the stock control falls short and is the
reason for the feature. This story also sets up what every other story uses: the script, the way
options reach it, and the control drawn as one of the pack's own.

**Independent Test**: Define a form with a `MultipleChoiceField` using the multiple widget, load
Tom Select, the stylesheets and the form's media on the page, choose two values and submit. The
form can be drawn, filled in and submitted with no other story delivered.

**Acceptance Scenarios**:

1. **Given** a `MultipleChoiceField` using the multiple widget, **When** its form is drawn,
   **Then** the page holds a multiple select with every choice of the field as an option, drawn
   as the pack draws any select, and marked so the script can find it.
2. **Given** a page that loads Tom Select and the form's media, **When** it has loaded, **Then**
   the select is a Tom Select control whose options are the ones written in the page, and no
   request is made for them.
3. **Given** such a control, **When** a person types part of an option's label, **Then** the
   options that match are offered, and every option of the field can be found this way.
4. **Given** such a control, **When** a person picks two options and submits the form, **Then**
   the field receives both values and validates them as it would from a stock multiple select.
5. **Given** a form with initial values, or a submitted form drawn again, **When** the control
   starts, **Then** those values are shown as chosen.
6. **Given** a field using the multiple widget, **When** a size, colour or variant is stated for
   the form or the field, **Then** the control takes it as a stock select does.
7. **Given** a submitted form whose field has an error, **When** it is drawn again, **Then** the
   control is drawn in the error state as a stock select is, and the error is tied to it.
8. **Given** a field that is disabled, **When** its form is drawn, **Then** the control shows its
   values and cannot be changed.
9. **Given** a control on a page, **When** a person activates the field's label or reaches the
   field with the keyboard, **Then** the control takes focus and assistive technology announces
   the label.
10. **Given** a page that draws the form and does not load Tom Select, **When** a person fills in
    and submits the form, **Then** the field is a stock multiple select that works, and no error
    is raised in the browser.

---

### User Story 2 - A developer gives a single choice field the same control (Priority: P1)

A developer has a field where a person picks one value: a country, a category, a status. They
name the single widget on the field. A person filling in the form types to find an option and
picks it, in a control that looks and behaves like the multiple one beside it.

**Why this priority**: A form that uses the multiple control and leaves its single selects stock
has two select interfaces. One interface across the form is half of what was asked for.

**Independent Test**: Define a form with a `ChoiceField` using the single widget, pick a value on
a page that loads Tom Select, and submit.

**Acceptance Scenarios**:

1. **Given** a `ChoiceField` using the single widget, **When** its form is drawn, **Then** the
   page holds a select with every choice of the field as an option, drawn as the pack draws any
   select, and marked so the script can find it.
2. **Given** a page that loads Tom Select and the form's media, **When** a person picks an
   option and submits the form, **Then** the field receives that one value.
3. **Given** a control holding a value, **When** a person picks another option, **Then** the new
   value takes the place of the old one.
4. **Given** a field that is not required and has an empty choice, **When** a person has picked
   a value, **Then** they can return the field to no value.
5. **Given** a `TypedChoiceField`, a `ModelChoiceField` or a `ModelMultipleChoiceField` using the
   widget for its kind, **When** its form is drawn and submitted, **Then** the field cleans the
   value to what it would have cleaned from a stock select.

---

### User Story 3 - A developer sets the control's options from Python (Priority: P2)

A developer wants the control to say what it is for before anything is chosen, to offer a button
that empties it, to let a chosen value be removed with a click, or to stop a person choosing more
than three values. They state each as a named argument on the widget.

**Why this priority**: The control is usable without these. They are what makes it comfortable,
and they are the settings a developer would otherwise write script for.

**Independent Test**: Define a form with the multiple widget given a placeholder, a clear button,
a remove button and a largest number of values, and use each on a page that loads Tom Select.

**Acceptance Scenarios**:

1. **Given** a widget with a placeholder, **When** the control holds no value, **Then** the
   placeholder is shown in it.
2. **Given** a widget with the clear button, **When** the control holds a value, **Then** one
   button empties it.
3. **Given** a multiple widget with the remove button, **When** the control holds values,
   **Then** each has a button that removes that value alone.
4. **Given** a multiple widget with a largest number of values, **When** a person has chosen that
   many, **Then** no further value can be chosen until one is removed.
5. **Given** a widget with none of these stated, **When** its form is drawn, **Then** nothing is
   written for them and Tom Select's own defaults apply.
6. **Given** a widget given an option it does not have, a largest number of values that is not a
   whole number above zero, or a single widget given an option that only the multiple widget
   has, **When** the form class is defined, **Then** an error is raised that names the option.
7. **Given** a developer's own `attrs` on the widget, **When** the form is drawn, **Then** they
   are on the select as they would be on a stock select.

---

### User Story 4 - A developer groups options and marks some unavailable (Priority: P2)

A developer writes the field's choices in groups, as Django allows, so that a list of cities is
headed by country. They may also write one option as unavailable from a subclass. A person
filling in the form sees the headings in the dropdown and cannot pick the unavailable option.

**Why this priority**: Grouped choices are part of Django's own choice fields, and a widget that
flattened them would lose something a stock select shows.

**Independent Test**: Define a form whose field has choices in two groups, open the dropdown on a
page that loads Tom Select, and search for an option in the second group.

**Acceptance Scenarios**:

1. **Given** a field whose choices are grouped, **When** the dropdown is opened, **Then** each
   option is listed under its group's heading, in the order the developer wrote.
2. **Given** such a control, **When** a person types part of an option's label, **Then** the
   option is offered under its heading.
3. **Given** a field whose choices mix grouped and ungrouped options, **When** the dropdown is
   opened, **Then** every option is offered.
4. **Given** an option drawn with the `disabled` attribute, **When** the dropdown is opened,
   **Then** the option is shown and cannot be chosen.

---

### User Story 5 - A developer uses the control in a formset, a modal and content loaded later (Priority: P2)

A developer puts a field with one of these widgets in a formset whose rows are added in the
browser, in a `Modal`, and in a form that htmx swaps into the page. In each the control starts
without the developer writing any script.

**Why this priority**: The projects this package serves add formset rows in the browser and load
forms with htmx as a matter of course. A control that starts only on selects present when the
page loads would fail in most of the places it is used.

**Independent Test**: Draw a formset with one of these widgets, add a row in the browser, and
choose a value in the new row.

**Acceptance Scenarios**:

1. **Given** a page that loads Tom Select and the form's media, **When** a select of one of these
   widgets is added to the page after it has loaded, by any script, **Then** a control is started
   on it.
2. **Given** a formset using one of these widgets, **When** a row is added by copying the
   formset's empty form, **Then** the new row holds one working control with the field's options
   and the widget's settings, and the values chosen in it are submitted under the new row's name.
3. **Given** a select whose control has been started, **When** the script meets it again,
   **Then** no second control is started.
4. **Given** a control in a `Modal`, a `Tab` or an `AccordionGroup`, **When** the container is
   opened, **Then** the control is in place and its dropdown is not cut off by the container.
5. **Given** a page that holds the script more than once, **When** it has loaded, **Then** each
   select has one control.
6. **Given** a select whose control has been started, **When** the select leaves the page, alone
   or with the form that htmx swaps out, **Then** its control is destroyed, and a select moved
   within the page keeps its control.
7. **Given** a select whose control was destroyed when it left the page, **When** it is put
   back, **Then** a new control is started on it.
8. **Given** a page reached through a boosted htmx link, whose select shares its `id` with a
   select on the page being left, **When** the swap has settled, **Then** the select is hidden
   behind a visible control, as it is on a page loaded in full.

---

### User Story 6 - A developer changes something that needs JavaScript (Priority: P3)

A developer needs a setting this package does not carry, such as drawing each option with an
icon. They listen for the event the script sends from each select once its control has started,
take the Tom Select instance from it, and make the change in a few lines of their own script.

**Why this priority**: It serves the few cases outside the settings it carries. Without it those
cases have no route but to stop using the widget.

**Independent Test**: On a page with one of these controls, listen for the event on the document
and call a method of the instance it carries.

**Acceptance Scenarios**:

1. **Given** a page that loads Tom Select and the form's media, **When** a control is started on
   a select, **Then** an event is sent from that select, reaches a listener on the document, and
   carries the Tom Select instance.
2. **Given** a select added to the page after it has loaded, **When** its control is started,
   **Then** the same event is sent from it.

---

### User Story 7 - A developer shows a count in place of the chosen values (Priority: P3)

A developer has a multiple choice field where a person ticks several options from a list, such
as the countries a survey covered, and the chosen values matter less than finding and ticking
them. They name the multiple widget with `counted=True`. A person sees "3 selected" in the
control, opens the list, searches it from a box at its top, and ticks or unticks each option.

**Why this priority**: The control works without it. A list of tags grows with each value and
pushes the form about, and the demo had to draw this control from a subclass and a stylesheet of
its own.

**Independent Test**: Define a form with a `MultipleChoiceField` using the multiple widget with
`counted=True`, on a page that loads Tom Select, the stylesheets and the form's media, tick two
options and submit.

**Acceptance Scenarios**:

1. **Given** a multiple widget with `counted=True`, **When** its form is drawn, **Then** the
   settings name the plugins `checkbox_options` and `dropdown_input`, after any button the
   widget was given.
2. **Given** a counted widget, **When** its form is drawn, **Then** the select holds the two
   words of the control, translated by default, or the ones the developer stated.
3. **Given** a page that loads Tom Select and the form's media, **When** a counted control has
   started, **Then** the box that holds its chosen values carries the two words.
4. **Given** a counted control and the package's stylesheet, **When** it holds no value, **Then**
   it shows the first word, and **When** it holds values, **Then** it shows their number
   followed by the second word, with no tag for each, and each chosen option has a tick in the
   dropdown.
5. **Given** a counted control, **When** a person ticks two options and submits the form,
   **Then** the field receives both values.
6. **Given** a multiple widget given a word and not counted, a counted widget given the remove
   button, or the single widget given `counted` or a word, **When** the form class is defined,
   **Then** an error is raised that names the setting.

---

### Edge Cases

- The page loads the form's media and never loads Tom Select. Every field is a stock select, no
  error is raised in the browser, and the form submits (FR-020).
- The page loads Tom Select and not `mvp_forms/tomselect.css`. The control works and is drawn by
  Tom Select's own stylesheet, and daisyUI cuts its dropdown off, as it does for a
  django-tomselect control. The README says so (FR-030).
- A page holds a control from this package and a django-tomselect control. Both work, they look
  the same, and the page loads Tom Select once (FR-013, FR-017).
- A select drawn by django-tomselect's widgets is on the page. The script leaves it alone. It
  starts a control only on a select one of this package's widgets drew (FR-018).
- A `ModelChoiceField` over a large table writes every row into the page. Nothing stops it. The
  README says which list the widgets suit (FR-030).
- A field has no choices. The control starts empty and nothing can be chosen.
- An option's label holds a quote, an angle bracket or an ampersand. It is shown as text in the
  dropdown and in the control, and is never read as markup (FR-014).
- A value is submitted that is not among the field's choices. The field rejects it as it always
  did. The widgets add no way to create a value.
- A required field is submitted empty. The field's own validation reports it, and the form is
  drawn again with the control in its error state.
- A person picks values in one order in a multiple control. The field receives the same set of
  values. Their order is whatever the browser submits and is not promised.
- A developer subclasses one of the widgets. The subclass is drawn and started as its parent is.
- A form is drawn with `|crispy`, `{% crispy form %}` or `|as_crispy_field`, or with Django's own
  form rendering and no crispy-forms at all. The widget writes its settings in each, and the
  control starts. The daisyUI classes on the select come from the pack, so without the pack the
  control is in Tom Select's own look.
- A host project bundles Tom Select into its own script and exposes it under the name Tom Select
  publishes. The widgets work as they do with a copy loaded on its own.

### Out of scope

- Tom Select itself. The package does not distribute it, load it or name a CDN outside the demo
  and the README's example.
- Options loaded from a view as a person types. That is django-tomselect's, which the pack
  already draws.
- Adding a value that is not among the field's choices. The field would reject it.
- Every Tom Select setting and plugin other than those of FR-006 to FR-009 and FR-034,
  including the ones written as JavaScript functions, dragging chosen values into an order,
  checkboxes in the dropdown of a control that still shows its tags, and a search box in the
  dropdown of a single control.
- A way to mark an option unavailable from Python.
- A limit on the number of options, or a warning when there are many.
- Fields. This feature adds widgets only.
- Changing how the pack draws a stock select or a django-tomselect control.

## Requirements *(mandatory)*

### Functional Requirements

#### The widgets

- **FR-001**: The package MUST provide two widgets in `mvp_forms.widgets`: `TomSelect` for one
  value and `TomSelectMultiple` for several. Each is a Django form widget a developer names on a
  field in place of `Select` or `SelectMultiple`.
- **FR-002**: Each widget MUST work on every field Django draws with a select of its kind,
  including `ChoiceField`, `TypedChoiceField`, `MultipleChoiceField`, `TypedMultipleChoiceField`,
  `ModelChoiceField` and `ModelMultipleChoiceField`.
- **FR-003**: Each widget MUST draw a select element holding every choice of the field as an
  option, and the pack MUST draw it as it draws any select, with the size, colour and variant
  stated for the form or the field, the error state of a field in error, and the `disabled`
  attribute of a disabled field.
- **FR-004**: The options MUST be the ones written in the page. Starting or using a control MUST
  make no request for them.
- **FR-005**: Every option of the field MUST be reachable by typing part of its label, however
  many options there are.

#### Settings stated from Python

- **FR-006**: Both widgets MUST take a placeholder, shown while the control holds no value.
- **FR-007**: Both widgets MUST take a setting that adds one button to empty the control.
- **FR-008**: The multiple widget MUST take a setting that adds a button to each chosen value to
  remove it.
- **FR-009**: The multiple widget MUST take the largest number of values that may be chosen.
- **FR-010**: Each setting MUST be a named argument. A widget MUST raise an error when the form
  class is defined if it is given an argument it does not have or a value that cannot be right,
  and the error MUST name the argument. A setting the developer did not state MUST NOT be
  written, so Tom Select's own default applies.

#### What the control shows

- **FR-011**: Choices grouped as Django allows MUST be listed under their group's heading. An
  option drawn with the `disabled` attribute MUST be shown and MUST NOT be choosable.
- **FR-012**: A control MUST be drawn by `mvp_forms/tomselect.css`, the stylesheet the package
  already ships for Tom Select's parts. The package MUST NOT ship a second stylesheet, and no
  widget's media may name the first. The host project loads it.
- **FR-013**: A control from one of these widgets and a django-tomselect control of the same
  kind, size, colour and variant MUST be drawn alike on one page.
- **FR-014**: An option's label and value MUST be shown as text. Neither may be read as markup,
  in the dropdown or in the control.
- **FR-015**: The field's label MUST name the control for assistive technology, activating the
  label MUST move focus to the control, and the field's help text and errors MUST stay tied to
  it.

#### The script

- **FR-016**: The package MUST ship one script that starts a Tom Select control on every select
  these widgets draw, using the settings the widget wrote. Each widget MUST name the script in
  its media, so a page that renders the form's media loads it and a page with none of these
  widgets does not.
- **FR-017**: The script MUST use the Tom Select the page provides under the name Tom Select
  publishes. A page that loads django-tomselect's script MUST need no other copy.
- **FR-018**: The script MUST start a control only on a select one of these widgets drew. It MUST
  leave every other select alone, including one drawn by django-tomselect's widgets.
- **FR-019**: The script MUST start a control on a select added to the page after it has loaded,
  whichever script added it, including a formset row made by copying the formset's empty form.
  It MUST NOT start two controls on one select, however many times the page includes the script.
  It MUST destroy the control of a select that has left the page, checked once each batch of
  changes has been made, so that a select moved within the page keeps its control. It MUST
  start the control of a select that htmx swaps in once the swap has settled.
- **FR-020**: On a page where Tom Select is not present, the script MUST do nothing and MUST raise
  no error, and each field MUST be a stock select that works.
- **FR-021**: The widgets and the script MUST use no inline script and no inline event handler.
- **FR-022**: The script MUST send an event from each select once its control has started. The
  event MUST reach a listener on the document and MUST carry the Tom Select instance.

#### What the form receives

- **FR-023**: Each widget MUST hand the field what `Select` or `SelectMultiple` would have handed
  it for the same choice, and MUST show initial and submitted values as chosen.
- **FR-024**: The widgets MUST add no validation on the server and MUST NOT change the validation
  of the field they are named on.

#### Constraints the package keeps

- **FR-025**: Neither Tom Select nor django-tomselect may become a dependency of the package, and
  no module of the package may import django-tomselect. Tom Select MUST NOT be distributed with
  the package.
- **FR-026**: The pack's own templates MUST still need no script. A page that loads daisyUI and
  nothing else MUST draw every form that uses none of these widgets exactly as before.
- **FR-027**: A django-tomselect control MUST be drawn and MUST behave as it did before the
  feature.
- **FR-028**: The widgets MUST write the same settings whether the form is drawn through the
  pack, through another template pack, or through Django's own form rendering.
- **FR-029**: The feature MUST add no field, model, view or URL.

#### Shipping it

- **FR-030**: The README MUST gain a section on the widgets: each widget and its settings, what
  the host project loads and in which order, the major version of Tom Select the widgets are
  written for, the event and what it carries, what a page without Tom Select or without the
  stylesheet does, how a page that also uses django-tomselect is set up, which list the widgets
  suit and when to use django-tomselect, and what is not supported. Each widget MUST appear in
  the README's public surface.
- **FR-031**: The demo MUST gain a Tom Select page in its Custom widgets group, with live
  examples of each widget with its settings, grouped choices, a control in a formset whose rows
  can be added, one in a modal, and one beside a django-tomselect control and a stock select.
- **FR-032**: The decision records MUST state that `mvp_forms/tomselect.css` serves Tom Select
  controls from this package's widgets as well as django-tomselect's, and that the package ships
  a script for these widgets. ADR 0042 MUST read true beside them.
- **FR-033**: `CONTEXT.md` MUST gain the terms under Key Entities, and its entry for an option
  group MUST cover a group written as Django's grouped choices.

#### A counted control

- **FR-034**: The multiple widget MUST take `counted`. `True` MUST turn on Tom Select's
  `checkbox_options` and `dropdown_input` plugins together. There MUST be no setting for either
  plugin alone, and the single widget MUST NOT take `counted`.
- **FR-035**: The multiple widget MUST take `none_text`, shown by a counted control holding no
  value, and `count_text`, shown after the number of values it holds. Each MUST default to a
  translated word, "Nothing selected" and "selected", MUST accept a lazy translation, and MUST be
  written on the select of a counted widget only. The script MUST copy both to the box that
  holds the chosen values. Either word on a widget that is not counted, and the remove button on
  a counted widget, MUST raise an error that names the setting.
- **FR-036**: A counted control MUST keep Tom Select's own keys, including Backspace in an empty
  search box removing the value chosen last.
- **FR-037**: `mvp_forms/tomselect.css` MUST draw a counted control: the count from the two
  words in place of the tags, a tick on each chosen option, and the search box in the dropdown,
  with every colour from the daisyUI theme. The chosen values MUST stay in the control for
  assistive technology. A django-tomselect control that uses `checkbox_options` MUST keep its
  tags.
- **FR-038**: The demo's Tom Select page MUST show counted controls: a short list, a long list to
  search, options with long labels and a disabled field.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1 | FR-001 to FR-005, FR-012 to FR-018, FR-020, FR-021, FR-023 to FR-033 |
| US-2 | FR-001 to FR-005, FR-015, FR-023, FR-024 |
| US-3 | FR-006 to FR-010, FR-028 |
| US-4 | FR-011, FR-014 |
| US-5 | FR-019, FR-031 |
| US-6 | FR-022, FR-030 |
| US-7 | FR-034 to FR-038 |

### Key Entities

- **Tom Select control**: The searchable select Tom Select builds in the browser in place of a
  select element. One built from a widget of this package and one built by django-tomselect are
  both Tom Select controls.
- **Options that come with the form**: The choices of a field written into the page as option
  elements when the form is drawn, as opposed to options a control requests from a view.
- **Chosen value**: A value held by a control. A multiple control lists each one in the control
  as an item of its own.
- **Counted control**: A multiple control that shows how many values it holds in place of the
  values themselves, ticks each chosen option in its dropdown and has its search box at the top
  of the dropdown.
- **Option group**: The heading a dropdown lists a set of options under. For these widgets it is
  a group in Django's grouped choices.
- **Form's media**: The scripts and stylesheets Django collects from a form's widgets, which the
  host project's template renders.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer turns a stock select or multiple select into a Tom Select control by
  naming one widget on the field, and writes no view, no URL and no JavaScript.
- **SC-002**: A project that already uses django-tomselect adds at most the form's media to a
  page to make every one of these controls on it work. A project without it adds Tom Select, its
  stylesheet and the package's stylesheet.
- **SC-003**: A form whose fields use these widgets cleans to the same data as the same form
  with stock selects, for every field kind of FR-002.
- **SC-004**: A control from this package beside a django-tomselect control of the same kind and
  size has the same height, colours and dropdown under the light and the dark theme.
- **SC-005**: A page that loads none of Tom Select draws and submits every form that uses these
  widgets, with no error in the browser.
- **SC-006**: Every form in the suite and the demo that uses none of these widgets is drawn with
  the same markup as before the feature, and the package still installs with no new dependency.
- **SC-007**: A control works in a formset row added in the browser, in a modal and in content
  swapped in after the page loads, with no script written by the developer.
- **SC-008**: A page with a Content Security Policy that allows scripts from the site's own
  origin and the origin serving Tom Select, and forbids inline script, starts every control.
