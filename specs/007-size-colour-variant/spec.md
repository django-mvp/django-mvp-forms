# Feature Specification: Size, colour and variant chosen from Python

**Feature Branch**: `007-size-colour-variant`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G4 (roadmap item R5)

**Tracking issue**: [#11](https://github.com/django-mvp/django-mvp-forms/issues/11)

**Input**: "A developer should be able to say once, in Python, that a form's inputs and buttons are small, or ghost, or a given colour, and override that for any single field. Today that means repeating CSS classes on every widget."

## Summary

daisyUI lets every input and button be drawn at one of several sizes, in one of its semantic colours, and in a variant such as ghost. Today a developer who wants a small form has to put the matching class on every widget by hand, and remember a different class name for each kind of input.

With this feature the developer states the choice once, in Python, for the whole form. The pack works out what that means for each kind of input and for the buttons. Any single field or button can state its own choice, which wins over the form's. A form that states nothing draws exactly as it did before.

## Terms

These words are used the same way throughout. They are new to the repository's vocabulary and are added to `CONTEXT.md` when the feature is built.

A **size** is one of the sizes daisyUI defines for inputs and buttons, written with daisyUI's own name for it.

A **colour** is one of daisyUI's semantic colour names. The host project's theme decides what each name looks like, and the pack never names an actual colour.

A **variant** is one of the alternative drawings daisyUI offers for the same input or button. daisyUI's documentation calls this a style. Inputs have one, ghost. Buttons have several.

A **choice** is a size, a colour or a variant stated in Python. The three are independent of each other.

## Boundary

This feature needs two others delivered first and specifies neither.

- Every kind of input the pack draws comes from "Text inputs drawn as daisyUI" (#5) and "Choice, boolean and file inputs drawn as daisyUI" (#6). This feature changes how those inputs are drawn when a choice is stated. What they look like with no choice stated is theirs.
- Buttons come from "Layout objects for structure and buttons" (#7). What a button looks like with no choice stated is that feature's.

Left to other features:

- Drawing a boolean as a toggle or a switch is #12, which takes the choices introduced here.
- Text prepended or appended to an input, and buttons attached to a field, are #8. Whether those attached parts follow the field's size is tracked in [#15](https://github.com/django-mvp/django-mvp-forms/issues/15).
- Rating, range, floating labels and joined inputs are roadmap item R7.
- A default for every form in a host project, set in one place, is not part of this feature. G4 asks for a choice per form and per field.

## Clarifications

### Session 2026-10-03

- Q: Does one statement of colour or variant for the form apply to its buttons as well as its inputs? → A: No. Size is stated once and reaches both. Colour and variant are stated for the inputs and, separately, for the buttons, because a form with ghost inputs seldom wants ghost buttons and the two do not share the same variants.
- Q: What happens when a choice has no meaning for one kind of input, such as a ghost variant on a checkbox? → A: That input is drawn without it and nothing is reported. A choice for the whole form has to be usable on a form that mixes kinds of input.
- Q: What happens when the developer writes a name daisyUI does not have? → A: It is refused with an error that names the choices allowed. Nothing is drawn with a class that does nothing.
- Q: Does a field with errors keep the colour chosen for it? → A: The field stays marked as in error. A chosen colour never hides that.
- Q: Does singling out one field require the form to have a layout? → A: No. A form drawn without a layout can still state a choice for one field, and a form with a layout can state it where the field is placed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose once for every input in a form (Priority: P1)

A developer building a dense settings form wants every input in it small. They state the size once, in the form's Python, and every input the pack draws for that form comes out small, whatever kind it is. The same goes for a colour or a variant. They write no class on any widget.

**Why this priority**: This is the request itself. Without it the developer is back to repeating classes on every widget.

**Independent Test**: Draw a form that holds one of every kind of input, with a size, a colour and a variant stated for the form. Each input carries daisyUI's modifier for each choice that applies to its kind, and the form's Python names no CSS class.

**Acceptance Scenarios**:

1. **Given** a form with a size stated for the form, **When** it is drawn, **Then** every visible input in it is drawn at that size.
2. **Given** a form with a colour stated for its inputs, **When** it is drawn, **Then** every visible input in it is drawn in that colour.
3. **Given** a form with a variant stated for its inputs, **When** it is drawn, **Then** every input whose kind has that variant is drawn in it.
4. **Given** a form with all three choices stated, **When** it is drawn, **Then** each input shows all three, and changing one of them leaves the other two as they were.
5. **Given** a form with no choice stated, **When** it is drawn, **Then** its markup is the same as it was before this feature existed.
6. **Given** a form with a choice stated for the form, **When** it is drawn with the crispy filter and again with the crispy tag, **Then** the choice takes effect both times.
7. **Given** a form with a layout that nests fields inside other layout objects, **When** it is drawn with a choice stated for the form, **Then** every field takes the choice wherever it sits in the layout.
8. **Given** a form with a choice stated for the form, **When** it is drawn, **Then** hidden inputs are unchanged.

---

### User Story 2 - Override the form's choice for one field (Priority: P1)

The same developer wants one field to stand out: a large search box at the top of an otherwise small form, or one input in a warning colour. They state the choice for that field alone. The field takes it, and every other field keeps the form's.

**Why this priority**: The request names it alongside the form-wide choice, and G4 asks for both. A form-wide choice with no way out forces the developer back to hand-written classes the first time one field differs.

**Independent Test**: Draw a form with a size stated for the form and a different size stated for one field. That field is drawn at its own size and every other field at the form's.

**Acceptance Scenarios**:

1. **Given** a form with a size stated for the form and a different size stated for one field, **When** it is drawn, **Then** that field is drawn at its own size and the rest at the form's.
2. **Given** a form with a size and a colour stated for the form and only a colour stated for one field, **When** it is drawn, **Then** that field takes its own colour and the form's size.
3. **Given** a form with no choice stated for the form and a choice stated for one field, **When** it is drawn, **Then** only that field changes.
4. **Given** a form with a choice stated for the form, **When** one field states that it wants the pack's ordinary drawing for that choice, **Then** that field is drawn as it would be on a form that stated nothing.
5. **Given** a form drawn without a layout, **When** a choice is stated for one of its fields, **Then** that field takes it and the developer has not had to list the other fields.
6. **Given** a form with a layout, **When** a choice is stated on a field where it is placed in the layout, **Then** that field takes it.
7. **Given** a field whose widget already carries the developer's own classes, **When** a choice applies to it, **Then** the developer's classes are still present.

---

### User Story 3 - Buttons take the choices too (Priority: P2)

A developer who has made a form small expects its buttons to be small as well, without saying so twice. They can also state a colour and a variant for the form's buttons, and give any one button its own.

**Why this priority**: The request names buttons, and a small form with ordinary-sized buttons looks unfinished. It comes after the inputs because a form is usable with its buttons drawn the ordinary way.

**Independent Test**: Draw a form with a size stated for the form and a layout that ends in a submit and a reset button. Both buttons are drawn at the form's size. State a different colour on one of them and only that one changes.

**Acceptance Scenarios**:

1. **Given** a form with a size stated for the form, **When** it is drawn, **Then** every button in its layout is drawn at that size.
2. **Given** a form with a colour or a variant stated for its buttons, **When** it is drawn, **Then** every button in its layout takes it and the inputs do not.
3. **Given** a form with a colour or a variant stated for its inputs, **When** it is drawn, **Then** its buttons do not take it.
4. **Given** a form with choices stated for its buttons and a different choice stated on one button, **When** it is drawn, **Then** that button takes its own and the others keep the form's.
5. **Given** a form with no choice stated, **When** it is drawn, **Then** its buttons are drawn as "Layout objects for structure and buttons" (#7) draws them.

---

### User Story 4 - A wrong choice is reported, an inapplicable one is passed over (Priority: P2)

A developer mistypes a size, or asks for a colour daisyUI does not have. They find out from an error that names what is allowed, not from a form that silently looks the same as before. A choice that is real but means nothing for one kind of input, such as a variant that a checkbox does not have, is a different case. That input is drawn without it and the rest of the form takes it.

**Why this priority**: A class that does nothing is invisible in the page source and costs an hour to find. It is P2 because the feature works for a developer who types the names correctly.

**Independent Test**: State a size name that daisyUI does not define and draw the form. An error is raised that lists the sizes allowed. Then state a variant for a form that holds a text input and a checkbox. The text input takes it, the checkbox is drawn without it, and no error is raised.

**Acceptance Scenarios**:

1. **Given** a size, colour or variant that is not one of daisyUI's, **When** the form is drawn, **Then** an error is raised that identifies the choice and lists the ones allowed.
2. **Given** the same mistake made on a single field or a single button, **When** the form is drawn, **Then** the error also identifies which field or button it was made on.
3. **Given** a variant stated for the form that one kind of input does not have, **When** the form is drawn, **Then** inputs of that kind are drawn without it, the others take it, and no error is raised.
4. **Given** a variant stated on a single field whose kind does not have it, **When** the form is drawn, **Then** an error is raised, because a choice made for one field that can never apply is a mistake.
5. **Given** any accepted combination of choices, **When** the form is drawn, **Then** every class the pack adds is one daisyUI's full CDN build defines.

---

### User Story 5 - See the combinations in the demo project (Priority: P3)

Someone deciding whether to use the pack, or a contributor checking a change, opens the demo project and finds a page showing a form at each size, in each colour and in each variant, with one field and one button overridden. The README's public surface lists how each choice is stated and which names are allowed.

**Why this priority**: The choices are only useful to someone who knows they exist and what the names are. It is P3 because it documents the other stories and delivers nothing they do not.

**Independent Test**: Open the demo page and find every size, every colour and every variant drawn at least once, along with a form in which one field and one button override the form's choice. The README's public surface names every choice.

**Acceptance Scenarios**:

1. **Given** the demo project, **When** its menu is opened, **Then** it holds an entry that leads to a page for this feature.
2. **Given** that page, **When** it is opened, **Then** every allowed size, colour and variant is drawn at least once on an input and at least once on a button where buttons have it.
3. **Given** that page, **When** it is opened, **Then** it includes a form in which one field and one button are drawn differently from the form's choice.
4. **Given** the README, **When** its public surface is read, **Then** it says how a choice is stated for a form, for a field and for a button, and lists the names allowed.

---

### Edge Cases

- A field with errors on a form with a colour stated stays marked as in error. The chosen colour does not replace or hide the marking that "Text inputs drawn as daisyUI" (#5) gives an invalid field.
- A disabled or read-only field takes the size, colour and variant like any other, and stays disabled or read-only.
- A field made of several inputs, such as a group of radios or a group of checkboxes, takes the choice on every input in the group.
- A field that states the same choice as its form is drawn once with that choice, not twice.
- A developer who has put a daisyUI modifier on a widget by hand and also states a different choice gets both in the markup. The pack does not go looking for classes it did not add.
- The label, help text and error text of a field are not changed by any choice. The choices are about the input and the button.
- A layout may hold the same form's fields in tabs, an accordion or any other container. A field takes the choice in all of them, because the choice travels with the field and not with the container.

## Requirements *(mandatory)*

### Functional Requirements

**Choosing for the whole form**

- **FR-001**: A developer MUST be able to state a size for a form once, in Python, and have it apply to every visible input and every button the pack draws for that form. *(US1, US3)*
- **FR-002**: A developer MUST be able to state a colour and a variant for a form's inputs once, in Python, and have them apply to every visible input the pack draws for that form. *(US1)*
- **FR-003**: A developer MUST be able to state a colour and a variant for a form's buttons once, in Python, separately from the inputs', and have them apply to every button in the form's layout. *(US3)*
- **FR-004**: Size, colour and variant MUST be independent. Stating or changing one MUST NOT alter the other two. *(US1, US2)*
- **FR-005**: The names a developer writes for a size, a colour and a variant MUST be daisyUI's own names for them, so nothing new has to be learned. *(US1)*
- **FR-006**: A form that states no choice MUST draw the same markup as it did before this feature. *(US1, US3)*
- **FR-007**: A choice stated for the form MUST take effect whether the form is drawn with the crispy filter or the crispy tag, and whether or not the form has a layout. *(US1)*
- **FR-008**: A field MUST take the form's choice wherever in the layout it is placed. *(US1)*
- **FR-009**: Hidden inputs MUST NOT be changed by any choice. *(US1)*

**Choosing for one field or one button**

- **FR-010**: A developer MUST be able to state a size, a colour and a variant for a single field. Each one stated MUST win over the form's, and each one not stated MUST fall back to the form's. *(US2)*
- **FR-011**: A developer MUST be able to state, for a single field, that one of the three is to be drawn the pack's ordinary way, undoing the form's choice for that field. *(US2)*
- **FR-012**: A choice for a single field MUST be statable on a form drawn without a layout, without listing the form's other fields, and on a form with a layout, where the field is placed. *(US2)*
- **FR-013**: A developer MUST be able to state a size, a colour and a variant on a single button in a layout, with the same precedence over the form's choices as a field has. *(US3)*
- **FR-014**: Classes the developer has put on a widget, a field's layout entry or a button MUST be kept when a choice is applied. *(US2)*

**What the choices mean**

- **FR-015**: For each kind of input and for buttons, the pack MUST apply the modifier daisyUI documents for that kind and that choice. *(US1, US3)*
- **FR-016**: Every class the pack adds for a choice MUST be one that daisyUI's full CDN build defines, so a host page loading that build needs no build step. *(US4)*
- **FR-017**: A field made of several inputs MUST have the choice applied to each of them. *(US1)*
- **FR-018**: A field with errors MUST stay marked as in error whatever colour is chosen for it or for its form. *(US1, US2)*
- **FR-019**: A choice MUST NOT change a field's label, help text or error text, or whether the field is disabled, read-only or required. *(US1)*

**Mistakes**

- **FR-020**: A size, colour or variant that is not one of daisyUI's MUST be refused with an error that identifies the choice, lists the ones allowed and, when it was made on a field or a button, identifies which. *(US4)*
- **FR-021**: A choice stated for the form that a kind of input has no modifier for MUST be passed over for inputs of that kind, without an error. *(US4)*
- **FR-022**: A choice stated on a single field whose kind has no modifier for it MUST be refused with an error. *(US4)*

**Showing it**

- **FR-023**: The demo project MUST have a page, reachable from its menu, that draws every allowed size, colour and variant at least once and includes a form with one field and one button overriding the form's choice. *(US5)*
- **FR-024**: The README's public surface MUST say how a choice is stated for a form, a field and a button, and list the names allowed. The CHANGELOG MUST record the addition. *(US5)*

### Key Entities

- **Choice**: a size, a colour or a variant, each optional and each taken from a fixed set of daisyUI's names. It can be stated for a form's inputs, for a form's buttons, for one field or for one button.
- **Form-wide choice**: the choices a form states once. Size covers inputs and buttons. Colour and variant are held for inputs and for buttons separately.
- **Field choice** and **button choice**: the choices stated for one field or one button. Each of the three, where stated, wins over the form's.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer changes the size, the colour or the variant of every input in a form with one statement in Python, and writes no CSS class to do it.
- **SC-002**: A developer gives one field, or one button, a different choice from its form with one statement that names only that field or button, and no other field or button changes.
- **SC-003**: Every kind of visible input the pack draws, and every button, responds to a size stated for the form. None is left at the ordinary size.
- **SC-004**: A page that loads only daisyUI's full CDN build shows every accepted combination of choices correctly, with no build step in the host project.
- **SC-005**: A form written before this feature, which states no choice, draws byte-for-byte the same markup after it.
- **SC-006**: Every misspelt or unknown choice is reported as an error that lists the allowed names. None reaches the browser as a class that does nothing.
- **SC-007**: The demo page shows every allowed size, colour and variant at least once, so a reader can see each without writing any code.

## Assumptions

- "Text inputs drawn as daisyUI" (#5), "Choice, boolean and file inputs drawn as daisyUI" (#6) and "Layout objects for structure and buttons" (#7) are delivered before this feature is built. This feature adds no kind of input and no button of its own.
- The sets of sizes, colours and variants are the ones daisyUI documents at the version the pack supports. When daisyUI adds or removes one, the pack follows in a later change.
- The host project supplies daisyUI. With the full CDN build nothing more is needed. A host project that builds its own stylesheet arranges for the classes to be included itself.
- The host project's theme decides what each colour name looks like. This feature does not check any combination for contrast under any theme, which is roadmap item R8.
- A choice is stated in Python only. Stating one from a template, or from a project-wide setting, is not offered.
- Where exactly a choice is written, and what the statement is called, is settled when the feature is planned. The requirements here only fix what can be stated and what it does.
