# Feature Specification: Floating labels and joined inputs

**Feature Branch**: `011-floating-labels-and-joined-inputs`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G9 (daisyUI's other form components, such as rating, range, floating label and joined
inputs, are reachable from a layout)

**Roadmap**: R7 (daisyUI's other form components)

**Issue**: #87

**Depends on**: FS-007 (#11) for the size, colour and variant choices and for the place in Python
where a choice is stated. FS-004 (#8) for the field frame a decorated field is drawn in. Through
them, FS-001 (#5) and FS-002 (#6) for labels, required markers, help text, errors and the inputs
themselves. All four are delivered.

**Input**: A developer should be able to draw a field with daisyUI's floating label, where the
label sits inside the input and moves up when it has a value, and to join several fields into one
control, such as a country code beside a phone number.

## Clarifications

### Session 2026-10-03

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals, the constitution and the decision records.
Longer rationale is in `decisions.md`.

- **Q: Is a floating label stated for one field, for a whole form, or both?**
  A: Both. It is a choice, stated where a size, a colour and a variant are stated: once for a
  form, and for one field, with the field's own statement winning. A dense form wants it
  everywhere, and one field must be able to opt out. Recorded as FR-001 and FR-002.

- **Q: Which fields can take a floating label?**
  A: A field the pack draws as a daisyUI input, textarea or select. A checkbox, a toggle, a radio
  or checkbox group, a file input, a multi-widget field and a date drawn as three selects have
  nowhere for the label to float. Stated for the form, the choice passes those over. Stated on
  one of them by name, it raises. Recorded as FR-003 and FR-011.

- **Q: What does a person see in an empty field with a floating label, and in a disabled one?**
  A: daisyUI shows the input's placeholder while the field is empty, and shows the label once the
  field has focus or a value. So an empty field with no placeholder of the developer's own shows
  the label's text, and a placeholder the developer set is kept. daisyUI hides a floating label
  on a disabled input, which would leave a disabled field with no visible label at all, so a
  disabled field keeps the ordinary label. Recorded as FR-006 and FR-007.

- **Q: When several fields are joined, whose label, help text and errors are drawn?**
  A: The group has one label, which the developer gives it. Each field keeps its own label as
  its input's name for assistive technology, and keeps its own help text and errors, drawn once
  with the group and tied to its own input. Each field is still validated and cleaned on its
  own. Recorded as FR-014 to FR-018.

- **Q: What may a joined group hold?**
  A: Fields the pack draws as a daisyUI input or select. Anything else named in it, such as a
  checkbox, a textarea or another layout object that draws a frame of its own, raises an error
  naming it. Buttons are not part of this feature: one field with buttons is the existing
  `FieldWithButtons`, and #94 asks whether a group of fields should take buttons too. Recorded as
  FR-013 and FR-021.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer gives a field a floating label (Priority: P1)

A developer has a dense form: a sign-in box, a filter bar, an address block. The labels above each
input cost a line each. They say in Python that the form's fields, or one field, are drawn with
daisyUI's floating label. They write no template and no CSS class. A person filling in the form
still has the label tied to the input, the required marker, the help text and the errors, and the
form validates and saves exactly as it did before.

**Why this priority**: It is the first half of the request and the one that needs no layout, so it
reaches every form the pack already draws, through the crispy filter and the crispy tag alike.

**Independent Test**: Build a form with a text field, a textarea, a select and a checkbox. State
a floating label for the form and undo it on one field. Draw it through the pack and submit it.
The text field, the textarea and the select each have a floating label tied to their input, the
opted-out field and the checkbox are drawn as before, and the cleaned data is unchanged.

**Acceptance Scenarios**:

1. **Given** a form that states nothing about floating labels, **When** the pack draws it,
   **Then** every field is drawn exactly as it was before this feature.
2. **Given** a field for which the developer stated a floating label, **When** the pack draws the
   form, **Then** the field is drawn with daisyUI's floating label, and the label is drawn once:
   the ordinary label above the input is not drawn as well.
3. **Given** a field with a floating label, **When** the pack draws it, **Then** the label is tied
   to the input, so that it names the input to assistive technology and activating it moves focus
   to the input.
4. **Given** a form that states a floating label for all its fields, **When** the pack draws it,
   **Then** every field drawn as a daisyUI input, textarea or select has one, and every other
   field is drawn as it is without the statement and raises nothing.
5. **Given** a form that states a floating label for all its fields and one field that undoes it,
   **When** the pack draws the form, **Then** that field has its ordinary label and the others
   float.
6. **Given** a form drawn with no layout, through the crispy filter, **When** it states a floating
   label for the form or for one field by name, **Then** the statement takes effect.
7. **Given** an empty field with a floating label and no placeholder of the developer's own,
   **When** the pack draws it, **Then** the field shows the label's text while it is empty.
8. **Given** a field with a floating label and a placeholder the developer set, **When** the pack
   draws it, **Then** the developer's placeholder is kept.
9. **Given** a required field with help text, drawn with a floating label in a bound form that
   failed validation, **When** the pack draws it, **Then** it carries the required marker, the
   help text and the errors, each tied to the input the way FS-001 ties them to any field, and the
   input is marked invalid.
10. **Given** a disabled field for which a floating label is stated, **When** the pack draws it,
    **Then** it is disabled and has its ordinary label, so a person can still see what it is.
11. **Given** a form whose helper turns labels off, **When** a floating label is stated, **Then**
    no label is drawn and the input is named for assistive technology as FS-001 names it.
12. **Given** a formset whose form states a floating label, **When** the pack draws it stacked,
    **Then** every form draws the field that way.

---

### User Story 2 - A developer joins several fields into one group (Priority: P2)

A developer has fields that belong together: a country code and a phone number, an amount and a
currency, a house number and a street. In the form's layout they name those fields as one joined
group and give the group a label. The pack draws the inputs side by side as one daisyUI join,
under that one label. Each field is still its own field: it has its own name for assistive
technology, its own help text and errors, and its own place in the cleaned data.

**Why this priority**: It is the second half of the request. It needs a layout, which the first
story does not, and it leans on the frame and the decorations FS-004 built.

**Independent Test**: Build a form with a select for a country code and a text field for a phone
number, join them in the layout with a group label, and submit it once valid and once with the
phone number missing. The two inputs are drawn in one join under one label, each input has its
own accessible name, the error is drawn once and tied to the phone number, and the cleaned data
holds both values under their own names.

**Acceptance Scenarios**:

1. **Given** a layout that joins two fields, **When** the pack draws the form, **Then** their
   inputs are drawn inside one daisyUI join, in the order the layout names them.
2. **Given** a joined group with a label of its own, **When** the pack draws it, **Then** the
   group is framed with that label the way the pack frames any group of inputs, and no field's
   own label is drawn beside it.
3. **Given** a joined group, **When** the pack draws it, **Then** each input is named for
   assistive technology by its own field's label, and a name the developer wrote on the widget is
   kept.
4. **Given** a joined group in which one field has help text, **When** the pack draws it,
   **Then** the help text is drawn once, with the group, and is tied to that field's input and to
   no other.
5. **Given** a bound form in which one field of a joined group failed validation, **When** the
   pack draws it, **Then** that field's input alone is marked invalid, and its errors are drawn
   once, with the group, and tied to it.
6. **Given** a joined group holding a required field, **When** the pack draws it, **Then** the
   group's label carries the required marker and the required input is exposed as required.
7. **Given** a form with a joined group, **When** it is submitted, **Then** each field is
   validated and cleaned under its own name, exactly as it is when the fields are not joined.
8. **Given** a joined group holding a disabled or a hidden field, **When** the pack draws it,
   **Then** the disabled field is drawn disabled in its place, and the hidden field is drawn as
   its hidden input and takes no place in the join.
9. **Given** a joined group that names a field the pack cannot join, such as a checkbox or a
   textarea, **When** the pack draws the form, **Then** it raises an error naming the field.
10. **Given** a joined group with a class or an attribute of the developer's own, **When** the
    pack draws it, **Then** the class and the attribute are on the group, and a class written for
    another template pack is dropped.
11. **Given** a formset whose helper's layout joins two fields, **When** the pack draws it
    stacked, **Then** every form draws the group.
12. **Given** a page that loads daisyUI's documented CDN install and nothing else, **When** it
    shows a form with a joined group, **Then** the group is drawn joined, with no build step and
    no script from the pack.

---

### User Story 3 - Floating labels and joined groups take the form's choices (Priority: P3)

A developer has stated a size, a colour or a variant through FS-007, for a form or for one field.
A field with a floating label follows it as it would with an ordinary label. The fields of a
joined group follow it too, so a small form has a small joined group.

**Why this priority**: The roadmap item asks for these components "with the same size, colour and
variant choices". It is last because both earlier stories are usable without it, and because most
of it is FS-007's behaviour carried through.

**Independent Test**: State a size and a colour for a form, wrap a joined group in a different
size, and give one floating-label field its own colour. Each input takes the choice in force for
it, and the markup uses only classes daisyUI defines.

**Acceptance Scenarios**:

1. **Given** a form with a size, a colour or a variant stated for its inputs, **When** the pack
   draws a field with a floating label, **Then** the input takes each of them as it does with an
   ordinary label.
2. **Given** a field with a floating label and a size, colour or variant of its own, **When** the
   pack draws it, **Then** the field's own choice wins over the form's.
3. **Given** a form with a size stated, **When** the pack draws a joined group, **Then** every
   input in the group takes that size.
4. **Given** a size, a colour or a variant stated around a joined group in the layout, **When**
   the pack draws it, **Then** every input in the group takes it, over the form's.
5. **Given** a joined group in which one field is in error and a colour is in force, **When** the
   pack draws it, **Then** the field in error carries the error modifier alone and the other
   fields keep the colour.
6. **Given** any size, colour and variant FS-007 offers, **When** the pack draws a floating label
   or a joined group with them, **Then** every class it writes is one daisyUI's CDN build defines
   or a layout utility the class test names.

---

### Edge Cases

- A floating label is stated on one field by name and the field is a checkbox, a toggle, a radio
  or checkbox group, a file input, a multi-widget field or a date drawn as three selects. The pack
  raises an error naming the field.
- A floating label is stated for the form and a field has attached text, has buttons joined to
  it, is drawn inline or is a member of a joined group. The statement passes that field over.
  Stated on such a field itself, it raises.
- A value other than the ones the pack knows is stated for the label. The pack raises, as it does
  for an unknown size.
- A field with a floating label has no label text at all. Nothing floats and the field is drawn
  as FS-001 draws a field with no label.
- A formset is drawn as a table. A field's label is its column heading there, and a layout is not
  applied, so a floating label has no effect, a joined group is not drawn, and neither raises.
- A joined group holds one field. It is drawn as a group of one. A group that holds nothing draws
  nothing.
- A joined group is given no label. No group label is drawn, and each input is still named by its
  own field's label.
- A joined group names a field the form does not have. django-crispy-forms decides what happens,
  as it does for any layout object.
- A joined group holds a field wrapped only to pass it attributes or a choice. The attributes and
  the choice reach that field's input. Any other layout object inside the group raises.
- One field of a joined group states a size of its own that differs from the group's. FS-007's
  rule holds and the field's own size is drawn. Whether the parts of one joined input should be
  held to one size is the question #15 already asks about attached text and buttons.
- A joined group holds a telephone or a search widget. Whether the pack draws those as daisyUI
  inputs is #70. Until it is settled they are not, so they cannot be joined.
- The same field is named both inside and outside a joined group. django-crispy-forms draws a
  field once and this feature does not change that.
- The host project's Content Security Policy forbids inline script. Nothing in this feature needs
  a script, so both parts work under it.

## Requirements *(mandatory)*

### Functional Requirements

#### Stating a floating label

- **FR-001**: A developer MUST be able to state, in Python, that a field is drawn with daisyUI's
  floating label, for one field and once for every field of a form. The statement needs no
  template and no CSS class from the developer.
- **FR-002**: The statement MUST be made in the same place and in the same manner as the size,
  colour and variant choices of FS-007, and MUST follow the same order: one field's own statement
  wins over the form's, and a field can undo the form's. It MUST be honoured wherever those
  choices are honoured, including a form drawn with no layout and a formset drawn stacked.
- **FR-003**: A floating label MUST apply to a field the pack draws as a daisyUI input, textarea
  or select, and to no other. Stated for the form, it MUST pass every other field over without an
  error.
- **FR-004**: A form that states nothing about floating labels MUST be drawn exactly as it was
  before this feature.

#### What a floating label keeps

- **FR-005**: A field drawn with a floating label MUST have its label drawn once, tied to its
  input so that it names the input to assistive technology, and MUST keep its required marker,
  help text, errors, invalid state and read-only state as FS-001 gives them.
- **FR-006**: An empty field with a floating label and no placeholder of the developer's own MUST
  show the label's text. A placeholder the developer set MUST be kept.
- **FR-007**: A disabled field MUST keep a visible label. Where a floating label is stated for
  it, it MUST be drawn with the ordinary label.
- **FR-008**: When the form's helper turns labels off, a floating label MUST NOT be drawn, and the
  input MUST be named as FS-001 names an input with labels off.
- **FR-009**: A floating label MUST NOT change what the form receives. Validation and cleaned data
  MUST be the same as with ordinary labels.

#### Floating labels and other decorations

- **FR-010**: A field with attached text, with buttons joined to it, drawn inline, or drawn as a
  member of a joined group MUST NOT take a floating label. The form's statement passes such a
  field over.

#### Mistakes with a floating label

- **FR-011**: A floating label stated on one field that cannot take it under FR-003 or FR-010, or
  stated with a value the pack does not know, MUST raise an error that names the field, no later
  than when the form is drawn. The pack MUST NOT draw the field some other way silently.

#### Joining fields

- **FR-012**: A developer MUST be able to name, in a form's layout, several fields to be drawn as
  one joined group, and MAY give the group a label. The pack MUST draw their inputs inside one
  daisyUI join, in the order named, with no template and no CSS class from the developer.
- **FR-013**: A joined group MUST accept a field the pack draws as a daisyUI input or select. It
  MUST also accept such a field wrapped only to pass it attributes or a choice.
- **FR-014**: A joined group MUST be framed the way the pack frames a group of inputs, with the
  group's label as the one visible label. No member's own label is drawn beside it. With no group
  label given, none is drawn.
- **FR-015**: Each input in a joined group MUST be named for assistive technology by its own
  field's label, unless the developer wrote a name on the widget, which is kept.
- **FR-016**: Each member's help text and errors MUST be drawn once, with the group, and each MUST
  be tied to that member's input the way FS-001 ties them to any field. A member in error MUST be
  marked invalid, and no other member is.
- **FR-017**: When any member of a joined group is required, the group's label MUST carry the
  required marker. Each required input MUST be exposed as required as FS-001 exposes it.
- **FR-018**: Joining MUST NOT change what the form receives. Each member is validated and cleaned
  under its own name, exactly as when it is not joined.
- **FR-019**: A disabled or read-only member MUST be drawn in that state in its place. A hidden
  member MUST be drawn as its hidden input and take no place in the join.
- **FR-020**: A class or an attribute the developer gives the group MUST be written on the group.
  A class written for another template pack MUST be dropped, as it is on every layout object.

#### Mistakes with a joined group

- **FR-021**: A joined group that names a field the pack cannot join, or holds a layout object
  other than the wrappers FR-013 allows, MUST raise an error that names it, no later than when the
  form is drawn.

#### Size, colour and variant

- **FR-022**: A field with a floating label MUST take the size, colour and variant in force for it
  under FS-007, exactly as it does with an ordinary label.
- **FR-023**: Every input in a joined group MUST take the size, colour and variant in force for
  it under FS-007: the form's, then one stated around the group in the layout, then the member's
  own. A member in error MUST carry the error modifier and no other colour.

#### Constraints the pack keeps

- **FR-024**: The markup for both parts MUST be built from daisyUI's own floating label and join.
  Every class the pack writes MUST be one daisyUI's CDN build defines, or a layout utility the
  class test names. The pack adds no stylesheet and no class of its own (Article XIV).
- **FR-025**: Both parts MUST work on a page that loads daisyUI's documented CDN install, with no
  build step in the host project and no script from the pack.
- **FR-026**: The templates this feature adds or changes MUST be plain Django templates with no
  django-cotton or daisy-cotton. The feature MUST add no import from django-mvp and no runtime
  dependency (Article XIII).
- **FR-027**: Any text the pack itself adds MUST be translatable (Article VIII).

#### Shipping it

- **FR-028**: The demo project MUST gain a page for floating labels and a page for joined groups,
  each reachable from the sidebar. Between them they MUST show every kind of field that takes a
  floating label, a joined group, each state from FR-005, FR-007, FR-016 and FR-019, and the
  sizes, colours and variants from FR-022 and FR-023. Both MUST also be shown on a page that
  loads only daisyUI's CDN install.
- **FR-029**: The README's public surface MUST say how a floating label is stated and how fields
  are joined, what each is refused for, and what is passed over. The CHANGELOG MUST record the
  addition, and the glossary in `CONTEXT.md` MUST gain the terms this feature introduces
  (Article VI).

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A developer gives a field a floating label | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-024, FR-025, FR-026, FR-027, FR-028, FR-029 |
| US-2: A developer joins several fields into one group | FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-024, FR-025, FR-026, FR-027, FR-028, FR-029 |
| US-3: Floating labels and joined groups take the form's choices | FR-022, FR-023, FR-024, FR-028 |

FR-028 and FR-029 land with the first story and are extended by the stories that follow, so each
story shows its own behaviour in the demo project and documents its own surface.

### Key Entities

- **Floating label**: daisyUI's label that is drawn inside a field's frame in place of the label
  above the input, and is shown at the input's edge once the input has focus or a value. A
  choice, stated for a form or for one field. A field that states none has its ordinary label.
- **Joined group**: several fields that a layout names to be drawn as one daisyUI join, side by
  side, under one label. Each member stays a field of its own.
- **Member**: one field of a joined group.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gives every field of a form a floating label with one statement in
  Python, and one field with one statement at that field, and edits no template and writes no CSS
  class.
- **SC-002**: A developer joins a country code and a phone number into one group with one entry in
  the form's layout, and edits no template and writes no CSS class.
- **SC-003**: A form that states neither a floating label nor a joined group produces the same
  output before and after this feature.
- **SC-004**: For every form, the submitted data validates and cleans to the same result with
  floating labels and joined groups as without them.
- **SC-005**: Every input drawn with a floating label or in a joined group has an accessible name,
  and each of the required marker, help text, errors and invalid state a field has without them
  is still present and tied to the right input. None is lost and none is drawn twice.
- **SC-006**: No field is left without a visible label by a floating label: an empty field, a
  filled one and a disabled one each show what the field is.
- **SC-007**: Every size, colour and variant FS-007 offers can be applied to a field with a
  floating label and to a joined group, and the demo project shows each on a page that loads
  daisyUI's CDN install with no build step.
- **SC-008**: Every statement the pack cannot honour is reported with an error naming the field
  or the layout object. None results in a field drawn some other way without notice.

## Assumptions

- A floating label is a new kind of choice beside size, colour, variant and drawing, and goes
  wherever FS-007 puts a choice. How it is spelt in Python is for the plan.
- Joining is stated in a layout only. A form drawn without a layout has no way to join fields,
  because joining names several fields at once and is not a statement about one.
- A joined group holds fields and no buttons. One field with buttons is `FieldWithButtons`, which
  FS-004 delivers. #94 asks whether a group of fields should take buttons as well.
- A joined group is drawn side by side. A developer who wants it stacked writes daisyUI's own
  class on the group, which FR-020 keeps. How the width is shared between the members is a matter
  for the build, and a width the developer sets on a member is kept as it is on any input.
- Which widgets the pack draws as a daisyUI input, textarea or select is what FS-001 and FS-002
  built. This feature adds none. Search, telephone and colour widgets are #70's to decide.
- The label, required marker, help text, errors, ids and disabled state of a field are specified
  by FS-001, FS-002 and FS-004. This feature keeps them and does not redefine them.
- Which sizes, colours and variants exist, and which wins, are FS-007's. This feature adds no
  name to them.
- The template paths a host project may override are being listed under #85. The templates this
  feature adds join that list in whichever of the two is delivered second.
- Whether every state stays legible under every daisyUI theme, a floating label included, is
  #88's to check.
- Rating and range inputs, the other half of R7, are #86.
- A host project with its own Tailwind build makes sure daisyUI's floating-label and join classes
  are in its stylesheet. The pack promises only daisyUI's documented CDN install.
- No change to the continuous-integration workflows is needed.
- No sketch is needed before the build. The feature places two stock daisyUI components in a form
  and adds demo pages, and nothing in it calls for a new design.
