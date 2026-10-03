# Feature Specification: Tabs, accordion, modal and alert in a layout

**Feature Branch**: `005-container-layout-objects`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G2 (every layout object django-crispy-forms ships can be used)

**Roadmap**: R3

**Issue**: #9

**Input**: "Long forms need parts grouped behind tabs or an accordion, a form shown in a modal, and a notice placed in the layout. Each should use daisyUI's own component, and a tab or accordion group holding a field with an error should be the one that opens, so nobody submits a form and sees nothing wrong."

## Summary

django-crispy-forms ships six layout objects that hold part of a form behind an interaction or show a notice: `TabHolder` and `Tab`, `Accordion` and `AccordionGroup`, `Modal`, and `Alert`. This feature makes the pack draw all six, each with its daisyUI counterpart: tabs, collapse, modal and alert.

A developer keeps writing the layout the way django-crispy-forms documents it. What changes is what a person filling in the form gets. When a submitted form comes back with an error in a field that sits inside a tab, an accordion group or a modal, that tab, group or modal is already open, so the error is in view.

Together with the structural and field-decorating layout objects (issues #7 and #8), this covers every layout object django-crispy-forms ships.

## Depends on

- Issue #7, layout objects for structure and buttons. Tabs, accordion groups and modals hold those objects, and a host project usually opens a modal from a button delivered there.
- Issue #5, text inputs. Every field inside these layout objects is drawn through it, along with its label, help text and errors.

This specification says nothing about how fields, rows, fieldsets or buttons are drawn. It only says where they end up.

## Clarifications

### Session 2026-10-03

- Q: Which Python classes does a developer use? → A: django-crispy-forms' own `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, imported from where django-crispy-forms provides them, with the arguments it documents. This feature adds no layout object names of its own.
- Q: When several tabs or accordion groups hold a field with an error, which one opens? → A: The first one in layout order. This is the rule django-crispy-forms already applies, and the pack draws the state it is given.
- Q: Does a modal holding a field with an error open too? → A: Yes. The request names tabs and accordion groups, but its stated purpose is that nobody submits a form and sees nothing wrong, and a closed modal hides an error just as well as a closed tab does.
- Q: Who opens the modal in the first place? → A: The host project. The pack draws the modal with the id the developer gave it and draws no control to open it, which matches django-crispy-forms. The demo page shows one way of opening it.
- Q: Is a dismissed alert remembered? → A: No. Dismissing hides it on the page in front of the person. A reload or the next response draws it again.
- Q: What may the host project be asked to load for any of this to work? → A: daisyUI and nothing else. No script file, no stylesheet and no build step.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Group parts of a form behind tabs (Priority: P1)

A developer with a long form splits its fields across tabs by placing a `TabHolder` of `Tab` objects in the layout. A person filling in the form sees one tab's fields at a time and moves between tabs without leaving the page. If they submit and a field in a tab they were not looking at has an error, the form comes back with that tab open.

**Why this priority**: Tabs are the commonest way to break up a long form, and the error handling is the part of the request that protects people from a silent failure.

**Independent Test**: Draw a form whose layout holds three tabs, submit it with invalid data for a field in the second tab, and check that the second tab is the one marked open and that the field's error is inside it.

**Acceptance Scenarios**:

1. **Given** a layout with a tab holder of several tabs, each naming fields, **When** the form is drawn, **Then** it is drawn with daisyUI's tabs, with one tab for each `Tab`, each labelled from the name the developer gave and each holding its own fields and layout objects.
2. **Given** a form with no errors, **When** it is drawn, **Then** exactly one tab is marked open, and it is the first unless django-crispy-forms' own rules pick another.
3. **Given** a submitted form with an error in a field that sits in the second tab, **When** it is drawn again, **Then** the second tab is the one marked open and the field's error is drawn inside it.
4. **Given** a submitted form with errors in fields in both the second and third tabs, **When** it is drawn again, **Then** the second tab is open.
5. **Given** a field with an error that sits inside another layout object within a tab, such as a row or a fieldset, **When** the form is drawn again, **Then** the tab holding that layout object is open.
6. **Given** a submitted form whose only errors belong to the form as a whole and to no field, **When** it is drawn again, **Then** the tab that opens is the same one that opens with no errors.
7. **Given** two tab holders on one page, in one form or in two, **When** a person changes tab in one, **Then** the open tab in the other does not change.
8. **Given** a form laid out with tabs, **When** it is submitted, **Then** the fields in every tab are sent, open or not, and the tabs themselves add nothing to what is sent.

---

### User Story 2 - Group parts of a form in an accordion (Priority: P1)

A developer groups fields under headings that open and close by placing an `Accordion` of `AccordionGroup` objects in the layout. A person opens the group they want to fill in. A group holding a field with an error is open when the form comes back.

**Why this priority**: It carries the same risk as tabs. A closed group hides an error completely, so the error handling cannot wait for a later release.

**Independent Test**: Draw a form whose layout holds an accordion of three groups, submit it with invalid data for a field in the third group, and check that the third group is the one marked open with the error inside it.

**Acceptance Scenarios**:

1. **Given** a layout with an accordion of several groups, **When** the form is drawn, **Then** it is drawn with daisyUI's collapse, with one group for each `AccordionGroup`, each headed by the name the developer gave and each holding its own fields and layout objects.
2. **Given** a form with no errors, **When** it is drawn, **Then** the first group is marked open, unless the developer used the argument django-crispy-forms provides to say which groups start open or closed.
3. **Given** a submitted form with an error in a field in a group that would otherwise start closed, **When** it is drawn again, **Then** that group is marked open and the field's error is drawn inside it.
4. **Given** errors in fields in more than one group, **When** the form is drawn again, **Then** the first of those groups in layout order is open.
5. **Given** an accordion placed inside a tab, with an error in a field inside one of its groups, **When** the form is drawn again, **Then** both the tab and the group are open.
6. **Given** two accordions on one page, **When** a person opens a group in one, **Then** the groups of the other do not change.
7. **Given** a form laid out with an accordion, **When** it is submitted, **Then** the fields in every group are sent, open or not, and the accordion itself adds nothing to what is sent.

---

### User Story 3 - Show part of a form in a modal (Priority: P2)

A developer puts fields in a `Modal` so they stay out of the way until asked for. The host project opens the modal from a control of its own. A person fills in the fields, closes the modal and carries on with the rest of the form, and the fields in the modal are submitted with everything else.

**Why this priority**: It is used less often than tabs or an accordion, and a form is usable without it. G2 still needs it.

**Independent Test**: Draw a form whose layout holds a modal with two fields, check the modal is drawn closed with its title and id, then submit invalid data for one of the two fields and check the modal is drawn open.

**Acceptance Scenarios**:

1. **Given** a layout with a modal holding fields, **When** the form is drawn, **Then** the modal is drawn with daisyUI's modal, carries the id the developer gave, holds those fields, and is closed.
2. **Given** a modal with a title, **When** it is drawn, **Then** the title is shown in the modal and is what assistive technology announces as the modal's name.
3. **Given** a drawn modal, **When** a host project's control targets its id in one of the ways daisyUI documents, **Then** the modal opens.
4. **Given** an open modal, **When** a person closes it with the modal's own close control, **Then** the form is not submitted and what they typed in any field is kept.
5. **Given** a form with fields inside a modal, **When** the form is submitted, **Then** those fields are sent with the rest of the form, whether the modal is open or closed.
6. **Given** a submitted form with an error in a field inside a modal, **When** it is drawn again, **Then** the modal is drawn already open and the field's error is inside it.
7. **Given** a modal drawn already open because of an error, **When** a person closes it, **Then** it closes as it would if they had opened it themselves.

---

### User Story 4 - Place a notice in a layout (Priority: P2)

A developer places an `Alert` between other layout objects to tell people something about the form: a warning before a risky section, say, or a note about what happens after saving. By default a person can dismiss it. The developer can also make it permanent.

**Why this priority**: It is the simplest of the four and nothing else depends on it. G2 needs it.

**Independent Test**: Draw a form whose layout holds one dismissible alert and one that is not, and check that both are drawn in their place in the layout, that only the first has a dismiss control, and that the control does not submit the form.

**Acceptance Scenarios**:

1. **Given** a layout with an alert between two other layout objects, **When** the form is drawn, **Then** the alert is drawn with daisyUI's alert, in that position, with the content the developer gave, and assistive technology treats it as a notice.
2. **Given** an alert the developer left dismissible, which is django-crispy-forms' default, **When** it is drawn, **Then** it has a control to dismiss it, and the control has a name assistive technology can announce.
3. **Given** a dismissible alert, **When** a person uses the dismiss control, **Then** the alert leaves view, the form is not submitted, the page is not reloaded and what they typed is kept.
4. **Given** an alert the developer marked as not dismissible, **When** it is drawn, **Then** it has no dismiss control.
5. **Given** an alert whose content the developer wrote with markup in it, **When** it is drawn, **Then** the markup is drawn as markup, as django-crispy-forms documents.
6. **Given** an alert the developer gave an extra class to, such as one of daisyUI's alert modifiers, **When** it is drawn, **Then** the class is on the alert.

---

### Edge Cases

- A tab holder or an accordion with a single tab or group is drawn, with that one open.
- A tab or group name containing characters that mean something in markup is escaped when drawn as a label. A lazily translated name is drawn in the active language.
- A tab, group or modal that holds only layout objects and no fields is drawn, and never opens on account of an error.
- A field with an error inside a group inside a tab inside a modal opens all three.
- An error on a hidden field inside a closed tab or group counts like any other field's error when deciding which one opens.
- An argument of one of these layout objects that has no daisyUI counterpart, such as the alert's `block`, is accepted and does not raise.
- A dismissed alert comes back after a reload, or when the form is drawn again after a submit.
- Two modals on one page need two ids. The developer supplies them, as django-crispy-forms documents, and the pack does not invent them.
- A form drawn with the crispy filter and no layout uses none of these layout objects and is unaffected.

## Requirements *(mandatory)*

### Functional Requirements

Tabs (User Story 1)

- **FR-001**: The pack MUST draw django-crispy-forms' `TabHolder` and `Tab` with daisyUI's tabs: one tab per `Tab`, labelled from its name, holding the fields and layout objects placed in it.
- **FR-002**: Exactly one tab MUST be marked open when a tab holder is drawn, so the open tab is right when the page arrives and does not wait for a script to run.
- **FR-003**: When one or more tabs hold a field with an error, the open tab MUST be the first of them in layout order, however deeply the field is nested inside that tab.
- **FR-004**: When no tab holds a field with an error, the open tab MUST be the one django-crispy-forms' own rules pick, which is the first by default.

Accordion (User Story 2)

- **FR-005**: The pack MUST draw django-crispy-forms' `Accordion` and `AccordionGroup` with daisyUI's collapse: one group per `AccordionGroup`, headed by its name, holding the fields and layout objects placed in it.
- **FR-006**: When one or more groups hold a field with an error, the first of them in layout order MUST be marked open, however deeply the field is nested.
- **FR-007**: When no group holds a field with an error, the groups marked open MUST be the ones django-crispy-forms' own rules pick, including the developer's choice of a group to start open or closed.

Modal (User Story 3)

- **FR-008**: The pack MUST draw django-crispy-forms' `Modal` with daisyUI's modal, carrying the id the developer gave and holding the fields and layout objects placed in it.
- **FR-009**: The modal's title MUST be shown in the modal and be tied to it as its accessible name.
- **FR-010**: The modal MUST have a close control of its own that neither submits the form nor clears what was typed, and that has a name assistive technology can announce.
- **FR-011**: The pack MUST NOT draw a control that opens the modal. A host project opens it by its id in any of the ways daisyUI documents.
- **FR-012**: A modal MUST be drawn closed, except when it holds a field with an error. Then it MUST be drawn already open, and a person MUST still be able to close it.
- **FR-013**: Fields inside a modal MUST stay part of the form the layout belongs to and be submitted with it.

Alert (User Story 4)

- **FR-014**: The pack MUST draw django-crispy-forms' `Alert` with daisyUI's alert, at its position in the layout, exposed to assistive technology as a notice.
- **FR-015**: A dismissible alert MUST carry a dismiss control with a name assistive technology can announce. Using it removes the alert from view without submitting the form or reloading the page. An alert marked as not dismissible MUST carry no such control.
- **FR-016**: Alert content MUST be drawn as the developer wrote it, markup included, as django-crispy-forms documents. The documentation MUST say that this content is trusted, and that anything a person typed has to be escaped before it is put there.

All four (User Stories 1 to 4)

- **FR-017**: Each of these layout objects MUST accept the arguments django-crispy-forms documents for it. An id, extra classes or extra attributes given by the developer MUST appear on the element they describe. An argument with no daisyUI counterpart MUST be accepted without raising.
- **FR-018**: Everything in this feature MUST work on a page that loads daisyUI's full CDN build and nothing else. The host project adds no script file, no stylesheet and no build step, and the markup uses only daisyUI's standard classes and modifiers.
- **FR-019**: Controls drawn by these layout objects (tab labels, group headings, close and dismiss controls) MUST NOT add to or change the data the form submits, and MUST NOT submit the form.
- **FR-020**: Two of the same layout object on one page MUST work independently of each other, whether they are in one form or in two.
- **FR-021**: Tabs and accordion groups MUST be reachable and operable from the keyboard.
- **FR-022**: Text the pack itself supplies, such as the names of the close and dismiss controls, MUST be translatable. Names and titles supplied by the developer MUST be escaped when drawn.
- **FR-023**: These layout objects MUST hold any layout object or field the pack can draw, and may be nested in one another.
- **FR-024**: The demo project MUST gain one page for each of tabs, accordion, modal and alert. The tabs, accordion and modal pages MUST let a visitor submit invalid data and see the right one open. The modal page MUST include a control that opens the modal.
- **FR-025**: The README's public surface MUST list the six layout objects as supported, say how a host project opens a modal, and carry the note on alert content from FR-016.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A layout written from django-crispy-forms' documented examples for tabs, accordion, modal and alert draws with the pack with no change to the layout code, for all six layout objects.
- **SC-002**: In every case where a submitted form comes back with a field error inside a tab, an accordion group or a modal, a person can see an error without opening anything.
- **SC-003**: All four work on a page whose only added asset is daisyUI's CDN build. The host project writes no script and runs no build.
- **SC-004**: A form laid out with any of the four submits the same field data as the same form laid out without them.
- **SC-005**: With this feature and the layout objects from issues #7 and #8, no layout object django-crispy-forms ships is left without a drawing in the pack.
- **SC-006**: A developer can open one demo page per layout object, four in all, and on three of them produce the error case in under a minute.

## Assumptions

- A person can have errors in more than one tab or group. They see the first, fix it and submit again. Marking every tab or group that holds an error is not part of this feature. Issue #46 asks whether it should be added.
- The rule for which tab or group opens lives in django-crispy-forms' Python classes. The pack draws the state those classes give it and adds no rule of its own, except for the modal in FR-012, where django-crispy-forms has none.
- An alert's colour is chosen by passing one of daisyUI's alert modifiers as an extra class. A first-class Python option for size, colour and variant belongs to issue #11.
- Whether the pack's interactive pieces have to work under a Content Security Policy that forbids inline script is not settled. Issue #47 asks, and the answer may constrain how FR-010, FR-012 and FR-015 are met.
- Forms split across steps, with a tab per step and validation between them, are a form view's business and belong to django-mvp.
- A formset inside a tab or group is drawn by issue #10's work. Nothing here is specific to one.
- The demo pages are the demo project's own pages, on django-mvp's shell. Nothing in them is distributed.
