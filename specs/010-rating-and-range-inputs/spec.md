# Feature Specification: Rating and range inputs

**Feature Branch**: `010-rating-and-range-inputs`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G9 (daisyUI's other form components, such as rating, range, floating label and joined inputs, are reachable from a layout)

**Roadmap**: R7 (daisyUI's other form components)

**Issue**: #86

**Depends on**: nothing that is still open. It builds on FS-007 (#11) for size, colour and the
place in Python where one field states a choice, on FS-008 (#12) for the drawing a field states,
on FS-002 (#6) for the select and the radio group a choice field is drawn as today, and on FS-001
(#5) for the number input and for labels, required markers, help text and errors. All four are
released.

**Input**: daisyUI has a star rating and a range slider, and neither can be reached from a form
today. A developer should be able to draw a choice field as a rating and a number field as a range
from Python, with the same size and colour choices as every other input, and with the label, help
text and errors a normal field gets.

## Clarifications

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals, the constitution and the decision records.
Longer rationale is in `decisions.md`.

- **Q: How does a developer say that a field is a rating or a range?**
  A: As a drawing, the choice FS-008 introduced for boolean fields. It is stated for one field at
  a time, in the same two places: around the field in a layout, and by the field's name for a form
  with no layout. The package adds no field class and no widget class for it, and the developer
  changes neither on their form. Recorded as FR-001 and FR-002.

- **Q: Which fields can be drawn as a rating, and which as a range?**
  A: A rating is for a single-choice field: one whose widget is Django's select or radio group and
  which holds one value. A range is for a number field: one whose widget is Django's number input.
  A multiple select, a checkbox group and a null-boolean select are not single-choice fields here.
  Recorded as FR-004 and FR-005.

- **Q: daisyUI's rating has sizes and no colour modifier. How does a rating take a colour?**
  A: Through daisyUI's own colour classes on the stars, which is how daisyUI's documentation
  colours a rating. They are in daisyUI's CDN stylesheet, so the pack still defines no class of its
  own. A range has daisyUI's colour modifiers and takes them like any input. Recorded as FR-018 and
  FR-022.

- **Q: A choice field can hold an empty choice, such as the blank first option of an optional
  select. What is it in a rating?**
  A: The way to clear the rating. It is never drawn as a star. A field with no empty choice offers
  no way to clear a rating once one is picked. Recorded as FR-009.

- **Q: Where do a range's lowest value, highest value and step come from?**
  A: From what the field already tells its widget, and from attributes the developer set on the
  widget. The pack adds none of its own. Where the field states none, the browser's defaults for a
  slider apply. Recorded as FR-013.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer draws a choice field as a rating (Priority: P1)

A developer has a review form with a field "How would you rate this?" whose choices run from one
to five. Today it is drawn as a select or as a column of radio buttons. They say in Python that
this field is a rating, and the pack draws it as daisyUI's star rating, with one star for each
choice. They write no template and no CSS class, and they change neither the field nor its widget.
A person picks a star, the form submits the value of that choice, and it validates and cleans
exactly as it did before. The field keeps its label, its help text and its errors.

**Why this priority**: It is the first of the two components the request names, and the one a
developer cannot get by putting a class on a widget. A rating is a group of inputs with markup of
its own, so without the pack it means replacing a template.

**Independent Test**: Build a form with a required choice field of five choices and an optional
one with an empty choice, state a rating for both in Python, draw the form through the pack, and
submit it with a star picked and with none. The fields are drawn as ratings and the form's cleaned
data and errors are the same as for the same form with no rating stated.

**Acceptance Scenarios**:

1. **Given** a single-choice field with no drawing stated, **When** the pack draws the form,
   **Then** the field is drawn as the select or radio group it was before this feature.
2. **Given** a single-choice field for which the developer stated a rating, **When** the pack
   draws the form, **Then** the field is drawn with daisyUI's rating, with one star for each choice
   that has a value, in the field's order.
3. **Given** a rating, **When** a person picks a star and submits the form, **Then** the form's
   cleaned data holds the value of that star's choice, the same as when that choice is picked in
   the field's ordinary drawing.
4. **Given** a bound form, or a form with an initial value, **When** the pack draws the field as a
   rating, **Then** the star of the held value is drawn as the one picked.
5. **Given** a rating whose field holds no value, **When** the pack draws it, **Then** no star is
   drawn as picked.
6. **Given** an optional single-choice field with an empty choice, drawn as a rating, **When** a
   person clears the rating and submits the form, **Then** the form's cleaned data holds the
   field's empty value.
7. **Given** a rating, **When** the pack draws it, **Then** the stars are one group named by the
   field's label, and each star is named to assistive technology by the label of its choice.
8. **Given** a field with help text and a required rating left empty in a bound form, **When** the
   pack draws it, **Then** the help text and the errors are drawn and tied to the group, the group
   is marked invalid, and the field carries the required marker a required radio group carries.
9. **Given** a disabled field drawn as a rating, **When** the pack draws it, **Then** every star is
   disabled and a person cannot change the rating.
10. **Given** a page with no JavaScript from the pack, **When** a person picks a star and submits
    the form, **Then** the value reaches the server.
11. **Given** a form with two single-choice fields and a rating stated for only one, **When** the
    pack draws the form, **Then** only that field changes.
12. **Given** a formset whose form states a rating for a field, **When** the pack draws the
    formset, **Then** every form draws that field as a rating and no two forms share an id or a
    group.

---

### User Story 2 - A developer draws a number field as a range (Priority: P2)

A developer has a settings form with a number field "Volume" that runs from 0 to 100 in steps of
5. Today it is drawn as a number input. They say in Python that this field is a range, and the
pack draws it as daisyUI's range slider. The slider's lowest value, highest value and step are the
ones the field already declares. A person drags the slider, the form submits the number, and it
validates and cleans exactly as it did before. The field keeps its label, its help text and its
errors.

**Why this priority**: It is the second component the request names. It comes after the rating
because a developer can already get close to it by hand, with an input type and a class on the
widget, though without the size, colour and error handling the pack gives every other input.

**Independent Test**: Build a form with an integer field that declares a lowest value, a highest
value and a step, state a range for it in Python, draw the form through the pack, and submit it
with a value inside the limits and with one outside them. The field is drawn as a slider with
those limits, and the form's cleaned data and errors are the same as for the same form with no
range stated.

**Acceptance Scenarios**:

1. **Given** a number field with no drawing stated, **When** the pack draws the form, **Then** the
   field is drawn as the number input it was before this feature.
2. **Given** a number field for which the developer stated a range, **When** the pack draws the
   form, **Then** the field is drawn as daisyUI's range, a slider that carries the field's name.
3. **Given** a number field that declares a lowest value, a highest value and a step, drawn as a
   range, **When** the pack draws it, **Then** the slider is limited to those values and moves in
   that step.
4. **Given** a range, **When** a person sets the slider and submits the form, **Then** the form's
   cleaned data holds the number, the same as when that number is typed into the field's ordinary
   drawing.
5. **Given** a bound form, or a form with an initial value, **When** the pack draws the field as a
   range, **Then** the slider is drawn at the held value.
6. **Given** a range, **When** the pack draws it, **Then** its label is tied to the slider, so that
   the label names it to assistive technology.
7. **Given** a field with help text, and a bound form in which the submitted number failed
   validation, **When** the pack draws the field as a range, **Then** the help text and the errors
   are drawn and tied to the slider, the slider is marked invalid, and a required field carries its
   required marker.
8. **Given** a disabled field drawn as a range, **When** the pack draws it, **Then** the slider is
   disabled and a person cannot move it.
9. **Given** a page with no JavaScript from the pack, **When** a person moves the slider and
   submits the form, **Then** the value reaches the server.
10. **Given** a number field whose widget carries attributes the developer set, **When** the pack
    draws it as a range, **Then** those attributes are kept.

---

### User Story 3 - A rating and a range take the form's size and colour (Priority: P3)

A developer has set a size and a colour for a form through FS-007, or for one field. A rating and
a range follow those choices as every other input does, so a small form has a small rating and a
small slider, and a field given its own colour keeps it. A choice neither component has, and a
drawing stated for a field that cannot take it, are reported as mistakes and never drawn as
something else.

**Why this priority**: The request asks for it by name, and it is what makes the two components
sit properly beside the other inputs. It is last because the first two stories are usable without
it.

**Independent Test**: Set a size and a colour for a form, override both on one field, and draw a
rating and a range. Each takes the form's size and colour, and the overridden field takes its own.
Then state a variant on a rating, a rating on a text field and a range on a choice field. Each
raises an error that names the field.

**Acceptance Scenarios**:

1. **Given** a form with a size stated for all its inputs, **When** the pack draws a rating or a
   range, **Then** the field takes that size.
2. **Given** a form with a colour stated for all its inputs, **When** the pack draws a rating or a
   range, **Then** the field takes that colour.
3. **Given** a field with its own size or colour, in a form that states a different one, **When**
   the pack draws it as a rating or a range, **Then** the field's own choice wins.
4. **Given** a field with a drawing, a size and a colour all stated for it, **When** the pack draws
   it, **Then** all three take effect together.
5. **Given** a form with no size or colour stated, **When** the pack draws a rating or a range,
   **Then** the field carries no size or colour of the pack's choosing and takes daisyUI's
   defaults.
6. **Given** a form that states a variant for all its inputs, **When** the pack draws a rating or a
   range, **Then** the variant is passed over for them and nothing is reported.
7. **Given** a rating or a range with a variant stated on the field itself, **When** the pack
   draws the form, **Then** it raises an error that names the field.
8. **Given** a rating or a range with a colour in force and an error on the field, **When** the
   pack draws it, **Then** the chosen colour is left out, so that the error is the only colour the
   field shows, and its size still applies.
9. **Given** a rating stated for a field that is not a single-choice field, or a range stated for
   a field that is not a number field, **When** the pack draws the form, **Then** it raises an
   error that names the field and the form is not drawn.
10. **Given** any size and colour FS-007 offers, **When** the pack draws a rating or a range with
    them, **Then** every class in the markup is one daisyUI's CDN stylesheet defines.

---

### Edge Cases

- The developer names a drawing the pack does not know. The pack raises an error naming the field
  and does not draw the form.
- A rating is stated for a multiple select, a checkbox group, a null-boolean select, a text field
  or a boolean field. A range is stated for a text field, a choice field or a boolean field. Each
  raises an error naming the field.
- A checkbox, toggle or switch is stated for a single-choice field or a number field. It raises as
  it did before this feature.
- A decimal field set to localise its value is drawn by Django as a text input. It is not a number
  field in this feature's sense, so a range stated for it raises.
- A single-choice field has no empty choice and holds no value. The rating is drawn with no star
  picked, and a required field left that way fails validation as it does in its ordinary drawing.
- A single-choice field's choices are in named groups. The rating draws one star for each choice,
  in order, and does not draw the group names.
- A single-choice field has no choices. The rating is drawn with its frame and no star.
- A model choice field is drawn as a rating. Its choices are read when the form is drawn, as they
  are for its select, and its empty label is the way to clear the rating.
- A number field declares no lowest value, highest value or step. The pack writes none, and the
  browser's defaults for a slider apply.
- A number field drawn as a range holds no value. The browser places the slider itself, and the
  form submits that position. A slider always submits a number, so an optional number field drawn
  as a range can never be submitted empty.
- A range does not show its value as a number. The pack adds no readout and no step marks. #90
  asks whether it should.
- A field drawn as a rating or a range is hidden. It is drawn as a hidden input, and the drawing
  stated for it has no effect and raises nothing.
- A rating or a range sits inside a layout object from FS-003 or FS-005. It is drawn as it would
  be outside one.
- A layout object that attaches text to an input holds a rating or a range. There is nowhere to
  attach the text, so the field is drawn as it is without the layout object, as a radio group is
  today.
- A layout object that draws a radio group's options along a line holds a field stated as a
  rating. The rating is drawn.
- The single-choice field's widget is a subclass that names a template of its own. The pack cannot
  draw a rating through a template it does not own, so a rating stated for that field raises an
  error naming the field.
- The same form is drawn twice. Both draws give the same markup, and the form's own widget is left
  as it was.
- The form draws no labels. A rating is named as a radio group is, and a range as a number input
  is, by what FS-001 and FS-002 already do for a form with labels off.

## Requirements *(mandatory)*

### Functional Requirements

#### Stating the drawing

- **FR-001**: A developer MUST be able to state, in Python and for one field at a time, that a
  single-choice field is drawn as a rating and that a number field is drawn as a range. The
  statement needs no template and no CSS class from the developer, and no change to the field or
  to its widget.
- **FR-002**: A rating and a range MUST be stated as drawings, in the same two places and in the
  same manner as the drawing of a boolean field under FS-008, so that one field can carry a
  drawing, a size and a colour together. The statement MUST be honoured wherever a boolean field's
  drawing is honoured, including in a formset handed to the pack. A form has no drawing of its
  own: the drawing is stated per field only.
- **FR-003**: A field with no drawing stated MUST be drawn exactly as it was before this feature.
  A form that states none MUST produce the same output as before.
- **FR-004**: A rating MUST apply to a field whose widget is Django's select or radio group, or a
  subclass of one, and which holds one value, and to no other. A multiple select, a checkbox group
  and a null-boolean select are outside it.
- **FR-005**: A range MUST apply to a field whose widget is Django's number input, or a subclass
  of it, and to no other.

#### A rating

- **FR-006**: A field drawn as a rating MUST use daisyUI's rating, with one star for each of the
  field's choices that has a value, in the field's order. The stars MUST be one group that
  carries the field's name, in which at most one star is picked.
- **FR-007**: A rating MUST NOT change what the form receives. Picking a star MUST submit the
  value of its choice, and the form's validation and cleaned data MUST be the same as when that
  choice is picked in the field's ordinary drawing.
- **FR-008**: A bound or initial value MUST be drawn as the picked star. A field that holds no
  value MUST be drawn with no star picked.
- **FR-009**: A choice whose value is empty MUST NOT be drawn as a star. It MUST be drawn as the
  way to clear the rating, using daisyUI's own means for that, so that an optional field can be
  submitted empty. A field with no empty choice offers no way to clear it.
- **FR-010**: Choices in named groups MUST be drawn as stars in the field's order, without the
  group names.
- **FR-011**: A rating MUST carry everything FS-001 and FS-002 give a radio group: one label that
  names the group, the required marker, help text and errors tied to the group, the invalid state
  and the disabled state. Each star MUST be named to assistive technology by the label of its
  choice.

#### A range

- **FR-012**: A field drawn as a range MUST use daisyUI's range: one slider that carries the
  field's name. It MUST NOT change what the form receives: for the same number, the form's
  validation and cleaned data MUST be the same as in the field's ordinary drawing.
- **FR-013**: A range's lowest value, highest value and step MUST be the ones the field already
  gives its widget and the ones the developer set on the widget. The pack MUST add none of its
  own.
- **FR-014**: A bound or initial value MUST be drawn as the slider's position.
- **FR-015**: A range MUST carry everything FS-001 gives a number input: its label tied to it, the
  required marker, help text and errors tied to it, the invalid state and the disabled state. It
  MUST fill its field as the number input does, and a width the developer set on the widget MUST
  win.

#### What both keep

- **FR-016**: A rating and a range MUST work with no JavaScript from the pack: a person can change
  the value and submit it on a page that loads only daisyUI's documented CDN install.
- **FR-017**: Attributes and classes the developer set on the widget MUST be kept. The pack MUST
  NOT write to the form's own widget, so drawing a form twice gives the same markup.

#### Size, colour and variant

- **FR-018**: A rating and a range MUST take the size and the colour in force for the field under
  FS-007: the form's choice when the field has none of its own, and the field's own when it has
  one. With neither, the field carries no size or colour of the pack's choosing.
- **FR-019**: A rating and a range have no variant. A variant stated for the form MUST be passed
  over for them, and one stated on the field itself MUST raise, as FS-007 rules for any input with
  no variant.
- **FR-020**: A rating or a range in error MUST be drawn without the chosen colour, so that the
  error is the only colour the field shows. Its size MUST still apply.

#### Mistakes

- **FR-021**: A drawing the pack cannot honour MUST raise an error that names the field, no later
  than when the form is drawn. This covers a name the pack does not know, a rating stated for a
  field that is not a single-choice field, a range stated for a field that is not a number field,
  a rating stated for a widget that names a template of its own, and a boolean field's drawing
  stated for a single-choice or a number field. The error MUST say which drawings that field can
  take. The pack MUST NOT fall back to another drawing silently. A hidden field raises nothing.

#### Constraints the pack keeps

- **FR-022**: The markup for a rating and for a range MUST use only classes that daisyUI's CDN
  stylesheet defines, so that it works on a page using daisyUI's documented CDN install with no
  build step (Article XIV). The pack adds no stylesheet and no class of its own.
- **FR-023**: The templates this feature adds or changes MUST be plain Django templates with no
  django-cotton or daisy-cotton, and the feature MUST add no import from django-mvp and no runtime
  dependency (Article XIII).
- **FR-024**: Any text the pack adds for a rating or a range MUST be translatable (Article VIII).

#### Shipping it

- **FR-025**: The demo project MUST gain a page that shows a rating and a range, each in a form to
  submit, with help text, in error, disabled, and in the sizes and colours of FR-018. The page
  MUST be reachable from the demo project's sidebar, and the same forms MUST be shown on a page
  styled by daisyUI's CDN install alone.
- **FR-026**: The README's public surface MUST describe the rating and the range, which fields
  take each and how one is stated. The CHANGELOG MUST record the addition (Article VI), and the
  glossary's entry for a drawing MUST cover them.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A developer draws a choice field as a rating | FR-001, FR-002, FR-003, FR-004, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-016, FR-017, FR-022, FR-023, FR-024, FR-025, FR-026 |
| US-2: A developer draws a number field as a range | FR-001, FR-002, FR-003, FR-005, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-022, FR-023, FR-024, FR-025, FR-026 |
| US-3: A rating and a range take the form's size and colour | FR-018, FR-019, FR-020, FR-021, FR-022, FR-025, FR-026 |

FR-025 and FR-026 land with the first story and are extended by the stories that follow, so each
story shows its own behaviour on the demo page and documents its own surface.

### Key Entities

- **Single-choice field**: a field whose widget is Django's select or radio group and which holds
  one value out of its choices. It is the only kind of field that can be drawn as a rating.
- **Number field**: a field whose widget is Django's number input. It is the only kind of field
  that can be drawn as a range.
- **Drawing**: how one field is drawn when it is not drawn the ordinary way. A boolean field has
  three from FS-008. This feature adds `rating` for a single-choice field and `range` for a number
  field.
- **Rating**: daisyUI's rating. One star for each choice, of which at most one is picked.
- **Range**: daisyUI's range. A slider between a lowest and a highest value.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer turns a choice field into a rating, or a number field into a range, with
  one statement in Python at the field. They edit no template, write no CSS class and change no
  field or widget.
- **SC-002**: For every single-choice field drawn as a rating and every number field drawn as a
  range, a submitted form validates and cleans to the same data as it does in the field's ordinary
  drawing.
- **SC-003**: A form that states no rating and no range produces the same output before and after
  this feature.
- **SC-004**: Each of the label, required marker, help text, errors, invalid state and disabled
  state that a normal field has is present on a rating and on a range. None is lost in either.
- **SC-005**: Every size and colour FS-007 offers can be applied to a rating and to a range,
  stated for the form or for the field, and the demo shows each on a page that uses daisyUI's CDN
  install with no build step.
- **SC-006**: Every statement the pack cannot honour is reported with an error naming the field.
  None results in a field drawn some other way without notice.

## Assumptions

- A rating and a range are stated as drawings because FS-008 made the drawing the per-field
  statement of how a field is drawn, and ADR 0019 says a later statement for one field is added to
  the same object. The package adds no field or widget for them: Article XV keeps those for what a
  real project needs.
- The pack draws a rating as radio inputs even when the field's widget is a select, and a range as
  a slider where the widget is a number input. That is a change of element the developer asked for
  by name, and it leaves what the form submits as it was. ADR 0002, which says the pack never
  changes an input's type, was written for a form that states nothing, and the build records how
  the two fit together.
- The stars are daisyUI's ordinary star. Half stars, other shapes and a rating drawn from a
  multiple-choice field are not part of this feature and can be asked for separately.
- A range is the slider alone. Showing its current value as a number and drawing step marks are
  not part of this feature. #90 asks whether the pack should offer them, and #47 bears on whether
  it could ship the script a live value needs.
- A vertical range is not part of this feature.
- An optional number field drawn as a range always submits a number, because a slider has no empty
  state. The README says so, and the pack does not refuse the combination.
- Which size and colour names exist, how a form-wide choice is passed over and how a mistake is
  reported are FS-007's and FS-008's to specify. This feature follows them and adds no new names
  beyond `rating` and `range`.
- Floating labels and joined inputs, the other half of R7, belong to #87. Replacing one of the
  pack's templates belongs to #85, legibility under every theme to #88, and the supported versions
  to #89. Nothing here depends on them.
- Whether prepended text and attached buttons follow a field's size is #15, and which Tailwind
  utilities Article XIV allows is #16. This feature works with the built behaviour of both and
  needs no utility that daisyUI's CDN stylesheet lacks.
- This feature changes nothing under `.github/`. It adds no dependency and no supported version,
  so the test matrix stays as it is.
- A host project with its own Tailwind build makes sure daisyUI's rating, range and colour classes
  are in its stylesheet. The pack promises only daisyUI's documented CDN install.
- No sketch is needed before the build. The feature places two stock daisyUI components in the
  field frame the pack already has and adds one demo page, and nothing in it calls for a new
  design.
