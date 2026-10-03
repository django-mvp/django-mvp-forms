# Feature Specification: Booleans drawn as a checkbox, toggle or switch

**Feature Branch**: `008-boolean-toggle-switch`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G4 (the variant, colour and size of any form component can be set from Python, per form and per field, including toggles and switches)

**Roadmap**: R5 (variants, colours and sizes from Python)

**Issue**: #12

**Depends on**: FS-007 (#11) for the size and colour choices and for the place in Python where a
per-field choice is made. Through it, FS-002 (#6) for the checkbox a boolean field is drawn as
today, and FS-001 (#5) for labels, required markers, help text and errors.

**Input**: A boolean field should be drawable as a checkbox, a toggle or a switch, chosen per field
from Python, and take the same size and colour choices as every other input.

## Clarifications

### Session 2026-10-03

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals and the constitution. Longer rationale is in
`decisions.md`.

- **Q: daisyUI has a checkbox and a toggle and nothing called a switch. What sets a switch apart
  from a toggle?**
  A: What a person using assistive technology hears. A toggle is still a checkbox to a screen
  reader, announced as checked or not checked. A switch is announced as a switch that is on or off.
  Both are built from the same daisyUI toggle, so the pack defines no classes of its own
  (Article XIV). Recorded as FR-004 and FR-005, and raised with the maintainer in #17.

- **Q: How is a boolean field drawn when the developer makes no choice?**
  A: As a checkbox, exactly as FS-002 draws it. A form that never mentions this feature is drawn
  the same before and after it lands. Recorded as FR-002.

- **Q: Which fields can take the choice?**
  A: A field whose widget is Django's single checkbox. A null-boolean field, which Django draws as
  a select, and a checkbox group, which is a multiple-choice field, are not boolean fields in this
  sense and keep the drawing FS-002 gives them. Recorded as FR-003.

- **Q: What happens when the choice cannot be honoured: an unknown name, or a toggle asked for on a
  field that is not a boolean field?**
  A: The pack raises an error that names the field, no later than when the form is drawn. It never
  falls back to another drawing without saying so. Recorded as FR-012.

- **Q: Can the drawing be set once for every boolean field in a form?**
  A: No. The issue and the roadmap both say the drawing is chosen per field, and this feature stops
  there. Size and colour can still be set once for the form, because FS-007 provides that.
  Recorded as FR-001 and in the assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer chooses how a boolean field is drawn (Priority: P1)

A developer has a form with boolean fields: "Remember me", "Email me about replies", "Publish
this record". Some read best as a checkbox and some as an on/off setting. For each field they say
in Python whether it is drawn as a checkbox, a toggle or a switch. They write no template and no
CSS class. The form validates and saves exactly as it did before.

**Why this priority**: This is the feature. Without it a developer who wants a toggle has to
replace a pack template or put daisyUI classes on the widget by hand, which is what G4 exists to
end.

**Independent Test**: Build a form with three boolean fields, choose a different drawing for each
in Python, draw the form through the pack, and submit it with each field on and off. The three
fields are drawn three ways and the form's cleaned data is the same as for three checkboxes.

**Acceptance Scenarios**:

1. **Given** a boolean field with no drawing chosen, **When** the pack draws the form, **Then**
   the field is drawn as the checkbox FS-002 provides, unchanged by this feature.
2. **Given** a boolean field for which the developer chose a toggle in Python, **When** the pack
   draws the form, **Then** the field is drawn with daisyUI's toggle and is still exposed to
   assistive technology as a checkbox.
3. **Given** a boolean field for which the developer chose a switch, **When** the pack draws the
   form, **Then** the field is drawn with daisyUI's toggle and is exposed to assistive technology
   as a switch.
4. **Given** a form with a toggle and a switch, **When** it is submitted with one turned on and
   the other turned off, **Then** the form's cleaned data holds `True` for the first and `False`
   for the second, the same as for checkboxes.
5. **Given** a bound form whose boolean field is `True`, **When** the pack draws the field as a
   toggle or a switch, **Then** the field is drawn turned on.
6. **Given** a page with no JavaScript from the pack, **When** a person turns a toggle or a switch
   on and submits the form, **Then** the value reaches the server.
7. **Given** a form with two boolean fields and a drawing chosen for only one, **When** the pack
   draws the form, **Then** only that field changes and the other is still a checkbox.
8. **Given** a formset whose form chooses a toggle for a boolean field, **When** the pack draws
   the formset, **Then** every row draws that field as a toggle.

---

### User Story 2 - A toggle or switch keeps everything a checkbox has (Priority: P2)

A person filling in the form gets the same help from a toggle or a switch as from a checkbox. The
label names it and activating the label changes it. Help text and errors are read out with it. A
required field is marked as required and a disabled one cannot be changed.

**Why this priority**: A toggle that loses its label tie or its error is a step backwards from the
checkbox it replaced, and G3 is an Essential goal. It comes second only because the first story has
to exist before there is anything to hold to this standard.

**Independent Test**: Draw the same boolean field three times, once per drawing, with help text, a
validation error, the required flag and the disabled state. Everything FS-001 and FS-002 tie to
the checkbox is tied to the toggle and to the switch in the same way.

**Acceptance Scenarios**:

1. **Given** a boolean field drawn as a toggle or a switch, **When** the pack draws it, **Then**
   its label is tied to it, so that the label names it to assistive technology and activating the
   label changes its state.
2. **Given** a boolean field with help text, drawn as a toggle or a switch, **When** the pack draws
   it, **Then** the help text is tied to the field the way FS-001 ties help text to any field.
3. **Given** a bound form in which a required boolean field was left off, **When** the pack draws
   that field as a toggle or a switch, **Then** the field is marked invalid and its errors are
   tied to it the way FS-001 ties errors to any field.
4. **Given** a required boolean field drawn as a toggle or a switch, **When** the pack draws it,
   **Then** it carries the same required marker a required checkbox carries.
5. **Given** a disabled boolean field drawn as a toggle or a switch, **When** the pack draws it,
   **Then** it is disabled and a person cannot change its state.
6. **Given** a form in a language other than English, **When** the pack draws a toggle or a
   switch, **Then** any text the pack itself adds is translated.

---

### User Story 3 - A boolean field takes the form's size and colour (Priority: P3)

A developer has set a size and a colour for a form through FS-007, or for one field. Boolean
fields follow those choices whichever way they are drawn, so a small form has small toggles and a
field given its own colour keeps it as a switch.

**Why this priority**: The issue asks for it by name and it is what makes a toggle sit properly
beside the other inputs. It is last because the first two stories are usable without it, and
because it rests on FS-007 more heavily than they do.

**Independent Test**: Set a size and a colour for a form, override both on one boolean field, and
draw a checkbox, a toggle and a switch. Each takes the form's size and colour, and the overridden
field takes its own.

**Acceptance Scenarios**:

1. **Given** a form with a size set for all its inputs, **When** the pack draws a boolean field as
   a toggle or a switch, **Then** the field takes that size.
2. **Given** a form with a colour set for all its inputs, **When** the pack draws a boolean field
   as a toggle or a switch, **Then** the field takes that colour.
3. **Given** a boolean field with its own size or colour, in a form that sets a different one,
   **When** the pack draws it as a toggle or a switch, **Then** the field's own choice wins.
4. **Given** a boolean field with a drawing, a size and a colour all chosen for it, **When** the
   pack draws it, **Then** all three choices take effect together.
5. **Given** a form with no size or colour set, **When** the pack draws a toggle or a switch,
   **Then** the field carries no size or colour modifier and takes daisyUI's defaults.
6. **Given** any size and colour FS-007 offers, **When** the pack draws a toggle or a switch with
   them, **Then** the markup uses only daisyUI's documented classes and modifiers.

---

### Edge Cases

- The developer names a drawing the pack does not know. The pack raises an error naming the field
  and does not draw the form.
- The developer asks for a toggle or a switch on a field that is not a boolean field, such as a
  text field or a checkbox group. The pack raises an error naming the field.
- The developer asks for a checkbox on a boolean field. This is the default stated out loud and is
  accepted.
- A null-boolean field is given no drawing. It stays the select FS-002 draws.
- The host project has replaced the boolean field's widget with one of its own. The choice applies
  only if that widget is still Django's single checkbox or a subclass of it. Otherwise the field
  is not a boolean field in this feature's sense.
- A boolean field is hidden. It is drawn as a hidden input and any drawing chosen for it has no
  effect and raises nothing.
- A boolean field sits inside a layout object from FS-003, FS-004 or FS-005. Its drawing is the
  same as it would be outside one.
- The same form class is drawn twice on one page. Each instance draws its boolean fields the same
  way.
- A variant is in force for the form through FS-007. A toggle or a switch treats it exactly as a
  checkbox does under FS-007, whatever that specification rules.

## Requirements *(mandatory)*

### Functional Requirements

#### Choosing the drawing

- **FR-001**: A developer MUST be able to choose, in Python and for one field at a time, whether a
  boolean field is drawn as a checkbox, a toggle or a switch. The choice needs no template and no
  CSS class from the developer.
- **FR-002**: A boolean field with no choice made MUST be drawn as the checkbox FS-002 provides. A
  form that makes no choice MUST be drawn exactly as it was before this feature.
- **FR-003**: The choice MUST apply to a field whose widget is Django's single checkbox, and to no
  other. A null-boolean field and a checkbox group are outside it.
- **FR-004**: A boolean field drawn as a toggle MUST use daisyUI's toggle and MUST remain a
  checkbox to assistive technology.
- **FR-005**: A boolean field drawn as a switch MUST use daisyUI's toggle and MUST be exposed to
  assistive technology as a switch with an on or off state.
- **FR-006**: The choice MUST be made in the same place and in the same manner as the per-field
  size and colour choices of FS-007, so that one field can carry a drawing, a size and a colour
  together. It MUST be honoured wherever FS-007's per-field choices are honoured, including in a
  formset handed to the pack.
- **FR-007**: The drawing MUST NOT change what the form receives. For the same action by the
  person filling it in, a toggle and a switch MUST submit what a checkbox submits, and the form's
  validation and cleaned data MUST be the same.
- **FR-008**: A toggle or a switch MUST work with no JavaScript from the pack: a person can change
  its state and submit it on a page that loads only daisyUI's stylesheet.

#### What a toggle or switch keeps

- **FR-009**: A boolean field drawn as a toggle or a switch MUST carry everything FS-001 and FS-002
  give it as a checkbox: its label tied to it, its required marker, its help text, its errors and
  invalid state, and its disabled state.
- **FR-010**: A bound or initial value of `True` MUST be drawn as turned on, and `False` as turned
  off, in every drawing.

#### Size and colour

- **FR-011**: A boolean field MUST take the size and colour in force for it under FS-007, whichever
  way it is drawn: the form's choice when the field has none of its own, and the field's own
  choice when it has one. With neither, it carries no size or colour modifier.

#### Mistakes

- **FR-012**: A choice the pack cannot honour MUST raise an error that names the field, no later
  than when the form is drawn. This covers a drawing name the pack does not know, and a toggle or
  a switch asked for on a field that is not a boolean field. The pack MUST NOT fall back to another
  drawing silently.

#### Constraints the pack keeps

- **FR-013**: The markup for every drawing MUST use only daisyUI's documented classes and
  modifiers, so that it works on a page loading daisyUI's full CDN build with no build step
  (Article XIV). The pack adds no stylesheet and no class of its own.
- **FR-014**: The templates this feature adds or changes MUST be plain Django templates with no
  django-cotton or daisy-cotton, and the feature MUST add no import from django-mvp and no runtime
  dependency (Article XIII).
- **FR-015**: Any text the pack adds for a toggle or a switch MUST be translatable (Article VIII).

#### Shipping it

- **FR-016**: The demo project MUST gain a page that shows a boolean field in each of the three
  drawings, in each state from FR-009, and with the sizes and colours from FR-011. The page MUST be
  reachable from the demo project's sidebar.
- **FR-017**: The README's public surface MUST list the three drawings and how one is chosen, and
  the CHANGELOG MUST record the addition (Article VI).

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A developer chooses how a boolean field is drawn | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-010, FR-012, FR-013, FR-014, FR-016, FR-017 |
| US-2: A toggle or switch keeps everything a checkbox has | FR-009, FR-015, FR-016 |
| US-3: A boolean field takes the form's size and colour | FR-006, FR-011, FR-013, FR-016 |

FR-016 and FR-017 land with the first story and are extended by the stories that follow, so each
story shows its own behaviour on the demo page and documents its own surface.

### Key Entities

- **Boolean field**: a field whose widget is Django's single checkbox. It holds `True` or `False`.
- **Drawing**: which of the three ways a boolean field is drawn. One of checkbox, toggle or switch,
  chosen per field, with checkbox as the default.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer changes how a boolean field is drawn with one change in Python, at the
  field, and edits no template and writes no CSS class.
- **SC-002**: For every boolean field and every drawing, a submitted form validates and cleans to
  the same data as it does with checkboxes.
- **SC-003**: A form that chooses no drawing produces the same output for its boolean fields
  before and after this feature.
- **SC-004**: Each of the label tie, required marker, help text, errors and disabled state that a
  checkbox has is present on a toggle and on a switch. None is lost in either drawing.
- **SC-005**: Every size and colour FS-007 offers can be applied to all three drawings, set for
  the form or for the field, and the demo page shows each on a page that loads daisyUI's full CDN
  build with no build step.
- **SC-006**: Every choice the pack cannot honour is reported with an error naming the field. None
  results in a field drawn some other way without notice.

## Assumptions

- FS-007 provides a place in Python where a choice is made for one field, and this feature adds
  the drawing to it. If FS-007 lands with a different shape from the one assumed here, FR-006 still
  holds: the drawing goes wherever its per-field choices go.
- The drawing is chosen per field only. A way to set it once for every boolean field in a form is
  not part of this feature. It can be asked for separately if forms with many toggles make the
  repetition a nuisance.
- Which size and colour names exist, and what a variant does to a checkbox, are FS-007's to
  specify. This feature follows them and adds none.
- The label, required marker, help text, errors and disabled state of a checkbox are specified by
  FS-001 and FS-002. This feature keeps them and does not redefine them.
- How the label and the toggle are arranged relative to each other is a matter for the build. It
  is not a requirement here because it is appearance.
- Checkbox groups drawn as groups of toggles are out of scope. So are daisyUI's other form
  components, such as rating and range, which belong to R7.
- A host project with its own Tailwind build makes sure daisyUI's toggle classes are in its
  stylesheet. The pack promises only the full CDN build.
- No sketch is needed before the build. The feature places stock daisyUI components in a form and
  adds one demo page, and nothing in it calls for a new design.
