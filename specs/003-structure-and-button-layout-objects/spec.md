# Feature Specification: Layout objects for structure and buttons

**Feature Branch**: `003-structure-and-button-layout-objects`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G2, G3 (see [GOALS.md](../../GOALS.md))

**Roadmap**: R2 (see [docs/ROADMAP.md](../../docs/ROADMAP.md))

**Input**: Issue #7: "A developer writing a form layout should be able to arrange fields with fieldsets, divs, rows and columns, drop raw HTML between them, and finish the form with submit, reset and plain buttons in a button holder or form-actions bar. These are the objects nearly every laid-out form uses."

## Summary

A developer who writes a `Layout` for a form can group and arrange its fields, put their own HTML between them, and end the form with buttons. They write that layout with django-crispy-forms' own layout objects, exactly as its documentation describes, and the pack draws each one as daisyUI markup.

The layout objects this feature covers are `Fieldset`, `Div`, `Row`, `Column`, `MultiField`, `HTML`, `Submit`, `Reset`, `Button`, `StrictButton`, `Hidden`, `ButtonHolder` and `FormActions`.

It draws nothing inside them. A field placed in any of these objects is drawn by the pack's field drawing, which FS-001 (issue #5) delivers and which this feature depends on.

## Clarifications

### Session 2026-10-03

- Q: The request names "submit, reset and plain buttons". Which django-crispy-forms layout objects does that cover? → A: `Submit`, `Reset`, `Button` and `StrictButton`. `Button` and `StrictButton` are both plain buttons, one drawn as an input and one as a button element with content of its own. `Hidden` is covered here too: the roadmap lists it with the buttons and no other feature request owns it.
- Q: Does a developer import these layout objects from this package or from django-crispy-forms? → A: From django-crispy-forms. Layout code written from its documentation works with the pack unchanged, and this feature adds no layout classes of its own.
- Q: `MultiField` is a documented layout object that no feature request names. Is it in or out? → A: In. It groups fields under one shared label, which makes it a structural object, and leaving it out would leave a documented layout object with nothing to draw it.
- Q: What does a `Row` do when its `Column`s are given no classes? → A: It still arranges them as columns, side by side where the page is wide enough. Classes the developer gives a `Row` or a `Column` are added to the drawn container, so the developer can change the arrangement.
- Q: django-crispy-forms also lets a developer add buttons to the form helper without writing a layout. Are those covered? → A: Yes. A button draws the same way wherever it was declared. Placing those buttons at the end of the form belongs to the form wrapper that FS-001 delivers.
- Q: Is the content of an `HTML` object, a `Fieldset` legend or a `StrictButton` escaped? → A: No. The developer wrote it, and it is treated as template source, as django-crispy-forms documents. Values it pulls from the page context are escaped the way Django escapes any template variable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Arrange fields in groups, rows and columns (Priority: P1)

A developer has a form with more fields than read well in one long list. They write a layout that puts related fields in a `Fieldset` with a legend, sets two short fields side by side with a `Row` of `Column`s, and wraps a section in a `Div` so it can carry an id or classes of their own. The page shows the fields in that arrangement, and each field still has its label, help text and errors.

**Why this priority**: Arranging fields is the reason a developer writes a layout at all. Every other layout object, in this feature and the ones after it, sits inside these.

**Independent Test**: Draw a form whose layout uses `Fieldset`, `Div`, `Row` and `Column`, nested inside one another, and check that every field is drawn once, in layout order, inside the containers the layout names.

**Acceptance Scenarios**:

1. **Given** a layout with a `Fieldset` that has a legend and two fields, **When** the form is drawn, **Then** both fields are inside one group, and assistive technology reads that group as named by the legend.
2. **Given** a `Fieldset` with an empty legend, **When** the form is drawn, **Then** the group is drawn and no empty legend is.
3. **Given** a `Fieldset` whose legend refers to a value in the page context, **When** the form is drawn, **Then** the legend shows that value.
4. **Given** a `Row` holding two `Column`s with one field each, **When** the form is drawn, **Then** each field is inside its own column, both columns are inside the row, and they come in the order the layout gives.
5. **Given** a `Fieldset`, `Div`, `Row` or `Column` that was given an id, classes or other HTML attributes, **When** the form is drawn, **Then** all of them are on the drawn container, with the developer's classes added to the pack's and not replacing them.
6. **Given** a layout that nests these objects several levels deep, **When** the form is drawn, **Then** every field is drawn exactly once and the nesting of the drawn containers matches the nesting in the layout.
7. **Given** a submitted form with an error on a field inside a `Fieldset` inside a `Column`, **When** the form is drawn again, **Then** the error is drawn with its field and tied to it exactly as it is for a field outside any layout object.
8. **Given** a `Row` whose `Column`s were given no classes, **When** the form is drawn on a page that loads only what FS-001 requires of a host project, **Then** the row arranges its columns with no further work from the developer.

---

### User Story 2 - Finish a form with buttons (Priority: P2)

A developer ends their layout with the buttons the form needs: a `Submit`, perhaps a `Reset`, a `Button` or `StrictButton` that a script listens to. They put them in a `ButtonHolder` or a `FormActions` bar so they sit together. The page shows them as daisyUI buttons, and each one does what its type says.

**Why this priority**: A form that cannot be submitted is not finished, but a developer can still hand-write a submit button in their page template while this is missing. Arrangement has no such workaround.

**Independent Test**: Draw a form whose layout ends in a `FormActions` holding a `Submit`, a `Reset` and a `Button`, submit it with the `Submit`, and check that the submit button's name and value arrive with the form's data.

**Acceptance Scenarios**:

1. **Given** a `Submit` with a name and a value, **When** a person uses it, **Then** the form is submitted and that name and value are in the submitted data.
2. **Given** a `Reset`, **When** the form is drawn, **Then** it is drawn as a button that resets the form and does not submit it.
3. **Given** a `Button`, **When** the form is drawn, **Then** it is drawn as a button that neither submits nor resets the form.
4. **Given** a `StrictButton` whose content includes markup and a value from the page context, **When** the form is drawn, **Then** it is drawn as a button element holding that content, with the context value filled in and the button type the developer chose.
5. **Given** any of the four buttons with an id, classes or other HTML attributes, **When** the form is drawn, **Then** all of them are on the drawn button, with the developer's classes added to the pack's.
6. **Given** a `ButtonHolder` or a `FormActions` holding several buttons, **When** the form is drawn, **Then** the buttons are together inside one container in the order given, and the container carries any id, classes or attributes it was given.
7. **Given** a form with no layout whose buttons were added to the form helper, **When** the form is drawn with the crispy tag, **Then** each button is drawn the same as it would be inside a layout.
8. **Given** a form whose helper says not to draw the form tag, **When** the form is drawn, **Then** the buttons in its layout are still drawn.

---

### User Story 3 - Place raw HTML and hidden values in a layout (Priority: P3)

A developer wants a line of explanation between two groups of fields, or a link beside the submit button, or a value sent with the form that no person fills in. They put an `HTML` object or a `Hidden` object in the layout where it belongs.

**Why this priority**: Both are small and common, and neither blocks a form from being laid out and submitted.

**Independent Test**: Draw a form whose layout has an `HTML` object between two fields and a `Hidden` object, and check the HTML lands between the fields and the hidden value arrives when the form is submitted.

**Acceptance Scenarios**:

1. **Given** an `HTML` object between two fields in a layout, **When** the form is drawn, **Then** its output is between those two fields.
2. **Given** an `HTML` object that refers to a value in the page context, **When** the form is drawn, **Then** the value is filled in and escaped as Django escapes any template variable.
3. **Given** an `HTML` object placed inside a `Fieldset`, a `Column`, a `ButtonHolder` or a `FormActions`, **When** the form is drawn, **Then** its output is inside that container, in layout order.
4. **Given** a `Hidden` object with a name and a value, **When** the form is submitted, **Then** that name and value are in the submitted data.
5. **Given** a `Hidden` object, **When** the form is drawn, **Then** nothing a person can see or reach with the keyboard is added to the page.

---

### User Story 4 - Group fields under one shared label (Priority: P3)

A developer has a few fields that make sense only together, such as the parts of a date range, and wants one label over all of them. They wrap the fields in a `MultiField` with that label.

**Why this priority**: `MultiField` is the least used of the documented structural objects. It is here so that no documented layout object is left without a template.

**Independent Test**: Draw a form whose layout has a `MultiField` with a label and two fields, and check both fields are inside one group that carries the label.

**Acceptance Scenarios**:

1. **Given** a `MultiField` with a label and two fields, **When** the form is drawn, **Then** both fields are inside one group, and assistive technology reads that group as named by the label.
2. **Given** a submitted form with an error on one field inside a `MultiField`, **When** the form is drawn again, **Then** the error is drawn and tied to the field it belongs to.
3. **Given** a `MultiField` that was given an id, classes or other HTML attributes, **When** the form is drawn, **Then** all of them are on the drawn group.

---

### Edge Cases

- A container with nothing in it is drawn as an empty container and raises nothing.
- A `Column` used outside a `Row`, or a `Row` that holds fields directly with no `Column`, is still drawn, with its contents in layout order.
- A layout that names a field the form does not have, names one field twice, or leaves some fields out behaves as django-crispy-forms documents. The pack changes none of that.
- A layout object that was given a template of the developer's own is drawn with that template and not the pack's.
- A button made unavailable through its HTML attributes is drawn unavailable.
- A legend, an `HTML` object or a `StrictButton`'s content that contains markup is drawn as written. Context values inside it are escaped.
- A layout object from another feature, such as a tab or a field with text prepended to it, placed inside one of these containers is drawn by whichever feature owns it. This feature only has to draw its container around it.

## Requirements *(mandatory)*

### Functional Requirements

#### Structure

- **FR-001**: The pack MUST draw `Fieldset`, `Div`, `Row`, `Column` and `MultiField`, each as a container holding its contents in layout order.
- **FR-002**: A `Fieldset` MUST be drawn so that assistive technology reads its fields as one group, named by the legend when there is one. An empty legend MUST NOT be drawn.
- **FR-003**: A `Fieldset`'s legend MUST be able to use values from the page context.
- **FR-004**: A `MultiField` MUST be drawn so that assistive technology reads its fields as one group named by its label.
- **FR-005**: A `Row` MUST arrange its `Column`s as columns when they were given no classes, on a page that loads only what FS-001 requires of a host project.
- **FR-006**: Every structural object MUST carry the id, classes and other HTML attributes the developer gave it. The developer's classes are added to the pack's.
- **FR-007**: Structural objects MUST nest inside one another to any depth, and each field in the layout MUST be drawn exactly once.
- **FR-008**: A field inside any structural object MUST keep the label, help text, required marker and errors it has outside one, tied to it in the same way. Drawing the field is FS-001's work, and these containers MUST NOT interfere with it.

#### Buttons

- **FR-009**: The pack MUST draw `Submit`, `Reset`, `Button` and `StrictButton` using daisyUI's button.
- **FR-010**: A `Submit` MUST submit the form and send its own name and value with it. A `Reset` MUST reset the form without submitting it. A `Button` MUST do neither.
- **FR-011**: A `StrictButton` MUST be drawn as a button element whose content is the developer's, with page-context values filled in, and whose type is the one the developer chose.
- **FR-012**: Every button MUST carry the id, classes and other HTML attributes the developer gave it, with the developer's classes added to the pack's.
- **FR-013**: `ButtonHolder` and `FormActions` MUST each draw one container holding their contents in layout order, and MUST carry the id, classes and attributes the developer gave them.
- **FR-014**: A button added to the form helper, with no layout, MUST be drawn the same as that button in a layout.

#### Raw HTML and hidden values

- **FR-015**: An `HTML` object MUST be drawn at its place in the layout, inside any of this feature's containers, with page-context values filled in.
- **FR-016**: Developer-written content in an `HTML` object, a legend, a label or a `StrictButton` is drawn as written. Any page-context value used in it MUST be escaped by the template layer.
- **FR-017**: A `Hidden` object MUST send its name and value with the form, and MUST add nothing a person can see or reach with the keyboard.

#### Across all of them

- **FR-018**: A layout written from django-crispy-forms' documentation with these layout objects MUST work with the pack without changing the layout code. This feature adds no layout classes of its own.
- **FR-019**: Where a layout object was given a template of the developer's own, that template MUST be used.
- **FR-020**: Every template this feature adds MUST be a plain Django template. None may use django-cotton or daisy-cotton, and nothing this feature adds may import from django-mvp.
- **FR-021**: The markup this feature draws MUST use daisyUI's own classes and modifiers, so that it works on a page that loads only what FS-001 requires of a host project, with no build step.
- **FR-022**: The demo project MUST gain pages that between them show every layout object in this feature, including a form drawn with errors.
- **FR-023**: The README's public surface MUST list every layout object this feature draws, and the CHANGELOG MUST record the addition.

### Requirement to story map

| Story | Requirements |
|---|---|
| US1, arrange fields | FR-001, FR-002, FR-003, FR-005, FR-006, FR-007, FR-008 |
| US2, buttons | FR-009, FR-010, FR-011, FR-012, FR-013, FR-014 |
| US3, raw HTML and hidden values | FR-015, FR-016, FR-017 |
| US4, shared label | FR-001, FR-004, FR-006, FR-008 |
| Every story | FR-018, FR-019, FR-020, FR-021, FR-022, FR-023 |

### Out of scope

- Drawing a field, its label, help text and errors. That is FS-001 (issue #5) and issue #6.
- Layout objects that change how one field is presented: inline checkboxes and radios, a field with buttons, prepended and appended text, uneditable, inline and multi-widget fields. That is issue #8.
- Tabs, accordion, modal and alert. That is issue #9.
- Choosing a size, colour or variant for buttons from one place in Python. That is issue #11. A class given to a single button still reaches it, because django-crispy-forms already does that.
- The form wrapper: the form tag, where helper-added buttons are placed, and form-wide errors. That is FS-001.
- Keeping layouts written for another template pack working. A developer moving from another pack adapts their layouts from this package's documentation.
- Form views and form page templates, which belong to django-mvp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can use all thirteen layout objects this feature names in one layout and get a drawn form, without writing a template of their own.
- **SC-002**: The layout examples for these objects in django-crispy-forms' documentation draw with the pack as written, with no argument added or changed for the pack's sake.
- **SC-003**: The demo pages for this feature draw correctly on a page that loads only what FS-001 requires of a host project, with no build step.
- **SC-004**: Every field placed inside these layout objects keeps its label, help text and errors tied to it, and every `Fieldset` with a legend and every `MultiField` is read by assistive technology as a named group.
- **SC-005**: Every layout object this feature draws appears in the README's public surface and on a demo page.

## Assumptions

- FS-001 (issue #5) is delivered first. It supplies the drawing of a field, the form wrapper, and the definition of what a host project has to load for the pack to work without a build step.
- The fields used on this feature's demo pages are the text fields FS-001 draws. Demo pages do not wait for the widgets issue #6 adds.
- The pack is used with the django-crispy-forms version the package already requires, 2.7 or later, and the layout objects are the ones that version ships.
- This feature adds no wording of its own. Button text, legends and labels all come from the developer, so there is nothing here to translate.
- How a `Row` arranges its columns using only daisyUI's own classes is settled when the feature is planned. daisyUI has no column component, and the question is tracked in issue #18.
