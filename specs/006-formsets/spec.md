# Feature Specification: Formsets drawn stacked or as a table

**Feature Branch**: `006-formsets`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G1 (any Django form or formset draws as correct daisyUI markup with no per-form work)

**Roadmap**: R4

**Input**: Issue #10: "A formset handed to the pack should draw as a set of forms, either one after another or as a table with a form per row, with its errors beside the row they belong to and its delete and ordering inputs matching the rest of the pack. Adding and removing rows in the browser belongs to django-mvp and stays out."

## Summary

A host project hands a formset to the template pack and gets back the whole formset: every form in it, the hidden bookkeeping Django needs to read the submission, and every error the formset holds. The developer picks one of two layouts in Python. In the stacked layout the forms follow one another, each drawn the way the pack draws a single form. In the table layout each form is one row and each field is one column. Nothing is written per form in either layout.

The pack draws what it is given and stops there. It does not add or remove rows in the browser, it does not supply the view that builds or saves the formset, and it does not supply the page around it. Those belong to django-mvp or to the host project.

## Clarifications

### Session 2026-10-03

- Q: How does a developer choose between the stacked and the table layout? → A: In Python, on the helper passed with the formset, using the setting django-crispy-forms already documents for choosing a formset's template. With no choice made, the formset draws stacked. There is no project-wide setting.
- Q: In the table layout a field's label sits in the column heading, away from the inputs. How do the inputs stay named for assistive technology? → A: Every input in a table row keeps a programmatic name and description of its own, taken from its field's label and help text, even though the label is shown once per column.
- Q: Where does an error go when it belongs to one form but to no single field? → A: With that form: inside the form in the stacked layout, and in or directly beside that form's row in the table layout. Only errors that belong to the formset as a whole are shown apart from the forms, once.
- Q: Does a layout set on the helper apply to a formset? → A: In the stacked layout, yes: it is applied to each form in turn, as django-crispy-forms does. In the table layout, no: the columns are the form's visible fields in the form's own order.
- Q: Does the pack draw a spare, empty form for a script to copy when a row is added? → A: No. Adding rows in the browser is outside this package. The pack guarantees only that each form is one distinguishable unit in the output: one container per form when stacked, one table row per form in the table.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A formset draws stacked with no per-form work (Priority: P1)

A developer has a formset: a plain one, a model formset or an inline formset. They hand it to the pack from a template and the whole formset appears, one form after another. Each form's fields are drawn exactly as the pack draws them in a single form. When the page is submitted, Django can read the formset back, because the management form and every hidden field were in the output.

**Why this priority**: This is the feature at its smallest. A formset that draws and submits correctly is usable on its own, and the table layout, the error placement and the delete and ordering inputs all build on it.

**Independent Test**: Hand the pack an unbound formset of three forms with no layout choice made, submit the drawn page unchanged, and confirm the formset binds and validates with three forms.

**Acceptance Scenarios**:

1. **Given** a formset of three forms and no layout choice, **When** it is handed to the pack, **Then** all three forms are drawn in the formset's own order, each as its own distinguishable unit, with every visible field of every form present.
2. **Given** any formset, **When** it is drawn, **Then** the management form is present exactly once and the submitted page binds to a formset with the same number of forms.
3. **Given** a model formset or an inline formset whose forms carry hidden fields, **When** it is drawn, **Then** every hidden field of every form is in the output and takes up no visible place.
4. **Given** a formset drawn stacked, **When** one of its fields is compared with the same field drawn in a single form by the pack, **Then** the two are drawn the same way, with the label, required marker, help text and input tied together as they are for a single form.
5. **Given** a helper that asks for a surrounding form element, **When** the formset is drawn, **Then** one form element wraps the whole formset and there is none per form. **Given** a helper that asks for no form element, **Then** none is drawn.
6. **Given** a formset with no forms at all, **When** it is drawn, **Then** the page renders, the management form is present, and submitting it yields a valid empty formset.
7. **Given** a formset handed to the pack without a helper, **When** it is drawn, **Then** it draws stacked.

---

### User Story 2 - The same formset draws as a table (Priority: P1)

A developer whose forms are short and repetitive, such as the lines of an order, wants them as a table: one row per form, one column per field. They say so once in Python, on the helper, and change nothing in the template. The table uses daisyUI's own table.

**Why this priority**: The issue asks for both layouts, and a table is the usual way to edit many small forms at once. It is a separate story because the stacked layout is complete without it.

**Independent Test**: Take the formset from the first story, choose the table layout on its helper, and confirm that each form is one row, each visible field one column, and the submitted page still binds and validates.

**Acceptance Scenarios**:

1. **Given** a formset of three forms with the table layout chosen, **When** it is drawn, **Then** there is one table with one body row per form, in the formset's own order, and one column per visible field.
2. **Given** a formset drawn as a table, **When** the column headings are read, **Then** each visible field's label appears once as its column's heading, and a required field is marked as required there.
3. **Given** a formset drawn as a table, **When** any input in any row is inspected, **Then** it has a programmatic name taken from its field's label, and a programmatic description taken from its field's help text where the field has one.
4. **Given** a formset drawn as a table, **When** the output is inspected, **Then** the management form is present exactly once, every hidden field of every form is present, and hidden fields add no column.
5. **Given** the same formset and template, **When** the layout choice on the helper is changed from stacked to table or back, **Then** the layout changes and nothing else in the host project had to change.
6. **Given** a formset drawn as a table and submitted unchanged, **When** Django binds it, **Then** it validates with the same number of forms as were drawn.

---

### User Story 3 - Every error appears beside what it belongs to (Priority: P2)

A person filling in a formset submits it with mistakes. The page comes back and each problem is shown where it applies: a field's error with that field, a form's own error with that form or row, and a problem with the formset as a whole once, apart from the forms. Nobody has to work out which row a message is about.

**Why this priority**: A formset that hides or misplaces an error cannot be corrected. It comes after the two layouts because it has nothing to attach to until they exist.

**Independent Test**: Bind a formset with one field error in the second form, one form-wide error in the third and one formset-wide error. Draw it in each layout and confirm each error appears once, with its owner and nowhere else.

**Acceptance Scenarios**:

1. **Given** a bound formset in which one field of the second form has an error, **When** it is drawn in either layout, **Then** the error appears within the second form's unit, tied to that field's input so assistive technology announces it, and appears in no other form.
2. **Given** a bound formset in which the third form has an error that belongs to no single field, **When** it is drawn stacked, **Then** the error appears inside the third form. **When** it is drawn as a table, **Then** the error appears in or directly beside the third form's row and is associated with that row.
3. **Given** a bound formset with an error that belongs to the formset as a whole, **When** it is drawn in either layout, **Then** the error appears exactly once, outside every form's unit.
4. **Given** a bound formset holding all three kinds of error, **When** it is drawn in either layout, **Then** every error the formset reports is in the output exactly once.
5. **Given** an unbound formset, or a bound one that is valid, **When** it is drawn, **Then** no error and no empty error container meant for one is announced to assistive technology.
6. **Given** an error message containing markup characters, **When** it is drawn, **Then** it is escaped.

---

### User Story 4 - Delete and ordering inputs match the rest of the pack (Priority: P3)

A developer turns on deletion or ordering for a formset. Django adds a delete checkbox and an order number to each form. Each of those is drawn the way the pack draws any other checkbox or number input, in both layouts, and Django still reads them on submission.

**Why this priority**: These two inputs exist only on formsets, so no other feature covers them. They are last among the drawing stories because a formset without them is already complete.

**Independent Test**: Draw a formset with deletion and ordering turned on in each layout, tick one form's delete input and give the forms an order, submit, and confirm Django reports the ticked form as deleted and the forms in the given order.

**Acceptance Scenarios**:

1. **Given** a formset with deletion turned on, **When** it is drawn in either layout, **Then** each form that Django gives a delete field has a delete input, drawn the same way the pack draws a boolean field's checkbox.
2. **Given** a formset with ordering turned on, **When** it is drawn in either layout, **Then** each form has an order input, drawn the same way the pack draws a number field's input.
3. **Given** a formset drawn as a table with deletion and ordering turned on, **When** it is inspected, **Then** the delete and order inputs each have a column of their own with a heading, and each input has a programmatic name.
4. **Given** a drawn formset in which one form's delete input is ticked and the page is submitted, **When** Django binds it, **Then** that form and no other is reported as deleted.
5. **Given** a formset where Django gives extra forms no delete field, **When** it is drawn, **Then** those forms have no delete input and the table's columns still line up across every row.

---

### User Story 5 - Both layouts can be seen in the demo project and found in the README (Priority: P3)

A developer deciding whether to use the pack, or a contributor changing it, opens the demo project and sees a formset in each layout: untouched, and again with errors after a bad submission. The README's public surface says how to hand a formset to the pack and how to choose a layout.

**Why this priority**: The repository asks each feature to bring its own demo page and its own public-surface entry. It is last because it shows the other four stories and adds no drawing behaviour of its own.

**Independent Test**: Run the demo project, reach each formset page from the navigation, submit each with a mistake and see the errors, and follow the README entry to draw a formset in a fresh host project.

**Acceptance Scenarios**:

1. **Given** the demo project, **When** its navigation is opened, **Then** there is a page for the stacked layout and a page for the table layout, and each responds successfully.
2. **Given** either demo page, **When** it is submitted with invalid data, **Then** the page is shown again with a field error, a form-wide error and a formset-wide error visible in the response.
3. **Given** either demo page, **When** it is opened, **Then** the formset on it has deletion and ordering turned on.
4. **Given** the README, **When** its public surface section is read, **Then** it names how a formset is handed to the pack and how each layout is chosen, and the CHANGELOG records the addition.

---

### Edge Cases

- A formset with no forms draws its management form and nothing else that could fail, and submits as a valid empty formset.
- A form marked for deletion and then redisplayed after a failed submission keeps its delete input ticked.
- Extra forms that Django gives no delete field leave their place in the delete column empty. The row keeps the same number of cells as every other row.
- A field that is hidden in the form never gets a column, a heading or a visible place. Its input and any error it carries are still in the output, with the error shown with its form.
- A field with no help text gets no empty description for assistive technology to announce.
- A formset whose forms do not all have the same fields is outside what the table layout promises. The stacked layout draws it correctly.
- A field drawn by a widget from outside the pack is drawn inside the formset the same way it would be in a single form.
- The pack draws forms in the order the formset yields them. It never reorders them from the order inputs.
- A formset nested inside another formset's form is out of scope.
- The limits Django enforces on a formset, such as the least or most forms allowed, are reported by Django as formset-wide errors and are drawn as such. The pack enforces none itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pack MUST draw a formset handed to it through django-crispy-forms as a whole: every form the formset yields, in the order it yields them.
- **FR-002**: The pack MUST offer two layouts for a formset, stacked and table, and MUST draw stacked when no choice is made or no helper is given.
- **FR-003**: A developer MUST be able to choose the layout in Python, per formset, on the helper, through the setting django-crispy-forms documents for choosing a formset's template. Changing the choice MUST require no change to the host project's templates.
- **FR-004**: In both layouts the pack MUST emit the formset's management form exactly once, and every hidden field of every form, so that a drawn formset submitted unchanged binds to the same number of forms.
- **FR-005**: In both layouts each form MUST be one distinguishable unit in the output: one container per form when stacked, one table body row per form in the table.
- **FR-006**: In the stacked layout each form's fields MUST be drawn the same way the pack draws those fields in a single form, including a layout set on the helper, which is applied to each form in turn.
- **FR-007**: In the table layout the pack MUST draw one table using daisyUI's table, with one column per visible field in the form's own field order, each field's label shown once as the column heading, and a required field marked as required in that heading.
- **FR-008**: In the table layout every input MUST keep a programmatic name taken from its field's label, and a programmatic description taken from its field's help text when it has one.
- **FR-009**: Hidden fields MUST NOT produce a column, a heading or a visible place in either layout.
- **FR-010**: A field's errors MUST be drawn within the unit of the form they belong to and tied to that field's input, in both layouts, in the same way the pack ties errors to an input in a single form.
- **FR-011**: A form's errors that belong to no single field MUST be drawn with that form: inside the form when stacked, and in or directly beside its row, associated with that row, in the table.
- **FR-012**: Errors that belong to the formset as a whole MUST be drawn exactly once, outside every form's unit, in both layouts.
- **FR-013**: Every error a bound formset reports MUST appear in the output exactly once, and all error text MUST be escaped through the template layer.
- **FR-014**: The delete input Django adds to a form MUST be drawn the way the pack draws a boolean field's checkbox, and the order input the way it draws a number field's input, in both layouts. In the table each MUST have its own column with a heading.
- **FR-015**: Every row of the table MUST have the same number of cells, including rows whose form lacks a delete field.
- **FR-016**: When the helper asks for a surrounding form element, the pack MUST draw exactly one around the whole formset, and none when the helper asks for none.
- **FR-017**: The formset templates MUST be plain Django templates built from daisyUI's standard classes and modifiers, so that the result works on a page loading daisyUI's full CDN build with no build step in the host project.
- **FR-018**: The pack MUST NOT add or remove formset rows in the browser, ship a script for doing so, or draw a spare empty form for one. It MUST NOT ship a view, a URL or a page template for a formset.
- **FR-019**: The demo project MUST gain one page per layout, reachable from its navigation, each showing a formset with deletion and ordering turned on, and each redisplaying with field, form-wide and formset-wide errors after an invalid submission.
- **FR-020**: The README's public surface MUST state how a formset is handed to the pack and how each layout is chosen, and the CHANGELOG MUST record the addition.
- **FR-021**: The repository's glossary (CONTEXT.md) MUST define formset, stacked layout and table layout as this package uses them, and MUST stop listing formset as a word this package does not use. The glossary MUST keep the line between drawing a formset, which is this package's, and handling one, which is django-mvp's.

Requirements map to stories as follows. US1: FR-001, FR-002, FR-004, FR-005, FR-006, FR-009, FR-016, FR-017, FR-018. US2: FR-002, FR-003, FR-004, FR-005, FR-007, FR-008, FR-009, FR-017. US3: FR-010 to FR-013. US4: FR-014, FR-015. US5: FR-019, FR-020, FR-021.

### Key Entities

- **Formset**: A set of forms of one kind that Django builds, validates and saves together. The pack receives one already built and draws it. It covers plain formsets, model formsets and inline formsets alike.
- **Management form**: The hidden form Django adds to every formset to record how many forms were drawn. Without it the submission cannot be read.
- **Stacked layout**: A formset drawn with its forms one after another, each drawn as a single form would be.
- **Table layout**: A formset drawn as one table, with a row per form and a column per visible field.
- **Form-wide error**: An error on one form that belongs to no single field.
- **Formset-wide error**: An error that belongs to the formset as a whole and to no one form.
- **Delete input and order input**: The checkbox and the number input Django adds to each form when deletion or ordering is turned on for the formset.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer draws a plain formset, a model formset and an inline formset in either layout with no template code written per form: one line in the template, whatever the number of forms.
- **SC-002**: Moving a formset between the stacked and the table layout takes one change in Python and no change to any template.
- **SC-003**: Every formset the pack draws, in both layouts and with any number of forms from none upward, binds on submission to the number of forms that were drawn.
- **SC-004**: For a bound formset, every error it reports appears once in the output, inside its own form's unit or, for a formset-wide error, outside all of them. No error is missing, repeated or shown with the wrong form.
- **SC-005**: Every input in a drawn formset, in both layouts and including the delete and order inputs, has a programmatic name. An automated accessibility check of both demo pages reports no input without a name and no error without an owner.
- **SC-006**: Ticking a delete input or filling an order input on a drawn formset is read back by Django for exactly that form, in both layouts.
- **SC-007**: Both demo pages draw correctly on a page that loads daisyUI's full CDN build, with no build step and no stylesheet from this package.
- **SC-008**: The package still ships no script, view, URL, model or migration, and none of its templates uses django-cotton or daisy-cotton.

## Assumptions

- The inputs inside a formset are drawn by the features that own them. Text-like inputs, labels, required markers, help text and field errors come from the text inputs feature (issue #5). Checkboxes, selects and the other choice, boolean and file inputs come from issue #6, which is why this feature depends on #6 and, through it, on #5. This specification says where those inputs are placed in a formset and does not restate how they are drawn.
- Layout objects (issues #7, #8 and #9) are not needed by this feature. A layout on the helper is applied to each form in the stacked layout to whatever extent the pack can draw that layout when this feature is built.
- Buttons declared on the helper are drawn once for the whole formset by whichever feature delivers buttons (issue #7). This feature adds no button of its own.
- The size, colour and variant choices of issues #11 and #12 reach formset inputs when those features are built. Nothing here anticipates them.
- Following the README's rule that django-crispy-forms' documented behaviour wins over inventing a new one, the layout is chosen with the helper setting crispy-forms already has. The pack adds no new setting, argument or helper class for it.
- In the table layout a helper's layout is not applied, which matches the table formset templates django-crispy-forms users already know. A developer who needs a laid-out form per row uses the stacked layout.
- The table layout assumes every form in the formset has the same fields, which is true of every formset Django builds from one form class.
- How the table behaves on a narrow screen, where help text sits in the table, and whether an empty table shows its headings are matters of appearance. They are settled by eye when the feature is built and are not requirements here.
- The names and paths of the two formset templates become part of the public surface under Article XI of the constitution when they are built. Documenting every overridable template path is roadmap item R6.
- django-mvp adds and removes rows in the browser. What it needs from this pack's output to do that, beyond one distinguishable unit per form, is an open question tracked in issue #13. It does not block this feature.
- The demo pages are the demo project's own and may use django-mvp's shell and components. Nothing the package distributes does.
