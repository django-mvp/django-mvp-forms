# Feature Specification: Text inputs drawn as daisyUI

**Feature Branch**: `001-text-inputs`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G1, G3, G6 (see [GOALS.md](../../GOALS.md))

**Roadmap**: R1 (see [docs/ROADMAP.md](../../docs/ROADMAP.md))

**Feature request**: [#5](https://github.com/django-mvp/django-mvp-forms/issues/5)

**Input**: "A project that selects the pack should get its text-like fields drawn as daisyUI inputs without writing a layout: text, email, number, password, URL, date and time, and textarea. Each comes with its label, required marker, help text and errors, tied to the input so a screen reader announces them. This is the base every other part of the pack draws through, and it should work on a page loading daisyUI's full CDN build with no build step."

## Summary

A host project selects the template pack by name and hands django-crispy-forms an ordinary Django form. Every text-like field in that form is drawn as a daisyUI input or textarea, with its label, a required marker, its help text and its errors. The label, help text and errors are tied to the input, so assistive technology announces them with the field. Errors that belong to the whole form are drawn with the form. No layout is written and no field is touched.

This is the first feature of the pack. It also settles the things every later feature draws through: the name the pack is selected by, how one field is framed, how a form is wrapped, and the limit on which classes the markup may use.

### What this feature covers

- Text, email, URL, number and password inputs, date, time and date-time inputs, and textareas. These are the widgets Django ships for them, whichever field uses the widget.
- The frame around each field: label, required marker, help text, errors, and the links between them.
- Errors that belong to the form as a whole.
- The form element itself when django-crispy-forms is asked to draw it, including the CSRF token.
- Each documented way of asking django-crispy-forms to draw: a whole form through the filter, a whole form through the tag, one field, and the form's errors on their own.
- One demo page, and the README's installation, quickstart and first public-surface entry.

### What this feature leaves to others

- Select and multiple select, radio groups, checkboxes and checkbox groups, file inputs and hidden inputs, and how disabled and read-only fields are drawn, belong to [#6](https://github.com/django-mvp/django-mvp-forms/issues/6). That feature reuses the field frame defined here.
- Layout objects of every kind, buttons included, belong to [#7](https://github.com/django-mvp/django-mvp-forms/issues/7), [#8](https://github.com/django-mvp/django-mvp-forms/issues/8) and [#9](https://github.com/django-mvp/django-mvp-forms/issues/9). A field split across several inputs, such as a split date and time, is one of the things #8 presents.
- Formsets belong to [#10](https://github.com/django-mvp/django-mvp-forms/issues/10).
- Choosing a size, colour or variant from Python belongs to [#11](https://github.com/django-mvp/django-mvp-forms/issues/11) and [#12](https://github.com/django-mvp/django-mvp-forms/issues/12). This feature draws each input in daisyUI's default presentation.
- Replacing one template as a documented, stable interface is roadmap item R6. Legibility under every daisyUI theme is R8. Range inputs and floating labels are R7.
- Form views and form page templates are django-mvp's and are never part of this package.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Text-like fields draw as daisyUI inputs with no layout (Priority: P1)

A developer adds the package to a project that already loads daisyUI, selects the pack by name in settings, and renders an existing form with django-crispy-forms. Every text-like field comes out as a daisyUI input or textarea with its label beside it. The developer wrote no layout and changed nothing on the form.

**Why this priority**: This is the feature. Nothing else in the pack can be drawn until a field can, and a pack that needs per-form work to look right has missed its first goal.

**Independent Test**: Render a form holding one field of each covered kind with the pack selected and no layout, and check that each field is drawn as the matching daisyUI input with its label.

**Acceptance Scenarios**:

1. **Given** a host project with the pack selected and a form holding text, email, URL, number, password, date, time and date-time fields, **When** the form is drawn through the django-crispy-forms filter, **Then** each of those fields is drawn as a daisyUI input.
2. **Given** the same project and a form with a field that uses a textarea, **When** the form is drawn, **Then** that field is drawn as a daisyUI textarea.
3. **Given** a form drawn through the filter, **When** the same form is drawn through the django-crispy-forms tag with no layout, **Then** each field is drawn the same way.
4. **Given** a bound form with submitted values, **When** it is drawn, **Then** each input holds the value Django would have put in it, and a password input holds none unless the widget is set to show it.
5. **Given** a widget that the developer has given attributes of their own, such as a placeholder, an extra class, a different input type or a row count, **When** the field is drawn, **Then** those attributes are all present on the input alongside what the pack adds.
6. **Given** a template that asks django-crispy-forms to draw a single field of a form, **When** it renders, **Then** that one field is drawn exactly as it would be inside the whole form.
7. **Given** a form that also holds a field whose widget this feature does not cover, **When** the form is drawn, **Then** that field still appears with its label, help text and errors, in the same position, and nothing raises.

---

### User Story 2 - Label, required marker, help text and errors belong to their input (Priority: P1)

Someone filling in a form with a screen reader moves to a field and hears what it is called, that it is required, what the help text says and, after a failed submission, what was wrong with it. Someone looking at the same form sees the same four things placed with the field.

**Why this priority**: A field without a working label or a readable error is not a usable field. G3 is an Essential goal, and every later feature inherits this frame, so it has to be right in the base.

**Independent Test**: Render a form with a required field that has help text, submit it invalid, and inspect the output for the links between the input and its label, help text and errors.

**Acceptance Scenarios**:

1. **Given** a field with a label, **When** it is drawn, **Then** the label is programmatically associated with the input, so activating the label focuses the input and assistive technology reads the label as the input's name.
2. **Given** a required field, **When** it is drawn, **Then** it carries a required marker that an optional field does not, and the requirement is exposed to assistive technology and not only to sight.
3. **Given** a field with help text, **When** it is drawn, **Then** the help text appears with the field and the input names it as its description.
4. **Given** a bound form in which a field failed validation, **When** it is drawn, **Then** every error message for that field appears with the field, the input is marked invalid for assistive technology, the input names the errors as part of its description, and the input is drawn in daisyUI's error state.
5. **Given** a field with both help text and errors, **When** it is drawn, **Then** the input's description refers to both.
6. **Given** a field with no help text and no errors, **When** it is drawn, **Then** the input's description refers to nothing that is not on the page.
7. **Given** help text that the form author marked as safe markup, **When** it is drawn, **Then** the markup is kept. **Given** a label, help text or error message that contains markup and is not marked safe, **When** it is drawn, **Then** it is escaped.
8. **Given** a form with a prefix, or two forms of the same class on one page with different prefixes, **When** they are drawn, **Then** every label, help text and error still points at its own input and no two elements share an id.
9. **Given** a field whose label is empty, **When** it is drawn, **Then** no empty label element is left behind and the input is still drawn.

---

### User Story 3 - The form and its own errors (Priority: P2)

A developer lets django-crispy-forms draw the whole form, element and all. A user submits it and validation fails for a reason that belongs to no single field. The form comes back with that reason shown as part of the form, and assistive technology reads it as an error.

**Why this priority**: Field errors cover most failures, but a form-wide failure with nothing drawn leaves the user with a form that silently refuses to submit. It ranks below the field itself because a host project can draw these errors by hand in the meantime.

**Independent Test**: Render a form that raises a form-wide validation error through the tag, and check for the form element, the CSRF token and the error.

**Acceptance Scenarios**:

1. **Given** a bound form with one or more errors that belong to the form as a whole, **When** it is drawn through the filter or the tag, **Then** each of those errors appears once, with the form and not attached to any one field, and is exposed to assistive technology as an error.
2. **Given** a form with no form-wide errors, **When** it is drawn, **Then** no empty error container is drawn.
3. **Given** a template that asks django-crispy-forms for a form's errors on their own, **When** it renders, **Then** the form-wide errors are drawn in the same way.
4. **Given** a form drawn through the tag with no helper settings, **When** it renders, **Then** it is wrapped in a form element that carries a CSRF token.
5. **Given** a helper that sets the form's method, action, id, CSS class or other attributes, **When** the form is drawn through the tag, **Then** the form element carries them.
6. **Given** a helper that turns off the form element, **When** the form is drawn, **Then** the fields are drawn with no form element around them. **Given** a helper that turns off the CSRF token, **Then** no token is drawn.
7. **Given** a helper that turns off labels, **When** the form is drawn, **Then** no visible label is drawn and each input still has a name that assistive technology can read.
8. **Given** a helper that turns off errors, **When** an invalid form is drawn, **Then** no field error and no form-wide error is drawn.
9. **Given** a helper that sets a class for labels or a class for the element holding the input, **When** the form is drawn, **Then** each label or holder carries that class.

---

### User Story 4 - The pack works in any daisyUI project (Priority: P2)

A developer whose project is not built on django-mvp, and whose pages load daisyUI from its CDN build with no build step of their own, installs the package and selects the pack. The forms draw correctly. Nothing asks for django-mvp, django-cotton or daisy-cotton, and no class in the output is missing from the stylesheet the page loaded.

**Why this priority**: G6 is an Expected goal, and the limit it places on the markup has to be set in the base, because every later feature copies what the base does. It ranks below the first two stories because it constrains how they are met and adds no behaviour of its own.

**Independent Test**: Install the package into a project that has neither django-mvp nor django-cotton, draw the form from User Story 1, and compare every class in the output against the classes daisyUI's CDN build defines.

**Acceptance Scenarios**:

1. **Given** a project with django-crispy-forms and this package installed and neither django-mvp, django-cotton nor daisy-cotton present, **When** a form is drawn with the pack, **Then** it draws without error.
2. **Given** a form drawn with the pack in any of its states, **When** the classes the pack put in the output are collected, **Then** every one of them is defined by daisyUI's full CDN build.
3. **Given** a page that loads daisyUI's full CDN build and nothing else for styling, **When** a form is drawn on it with the pack, **Then** every part of each field is styled without a build step in the host project.
4. **Given** the package as distributed, **When** its templates are inspected, **Then** none of them uses a django-cotton or daisy-cotton tag, include or parent template, and no module imports from django-mvp.

---

### User Story 5 - See it and install it (Priority: P3)

A developer deciding whether to use the pack opens the README and finds how to install it, how to select it, and a short example that draws a form. A contributor or reviewer opens the demo project and finds a page showing each covered input in each of its states.

**Why this priority**: The pack is usable without either, but a public interface with no documentation does not meet the project's own standard, and reviewers need somewhere to look at the result.

**Independent Test**: Follow the README from a clean project to a drawn form, and load the demo page.

**Acceptance Scenarios**:

1. **Given** the demo project is running, **When** the text inputs page is opened, **Then** it shows every input kind this feature covers, each in these states: empty, holding a value, required, with help text, and with an error.
2. **Given** the demo project is running, **When** the same page is submitted, **Then** it comes back with real validation errors on its fields and a form-wide error, drawn by the pack.
3. **Given** the demo project's sidebar, **When** it is drawn, **Then** it holds an entry that leads to the text inputs page.
4. **Given** the demo project is running, **When** the standalone variant of the page is opened, **Then** the same form is drawn on a page that takes its styling from daisyUI's CDN build alone.
5. **Given** the README, **When** a developer follows its installation and quickstart sections in a project that loads daisyUI, **Then** the steps as written produce a form drawn by the pack.
6. **Given** the README's public surface section, **When** it is read, **Then** it names the pack, the settings that select it and the input kinds it draws.

---

### Edge Cases

- A form with no fields draws nothing for its fields and raises nothing. Through the tag it still draws the form element and its token.
- A field whose widget is one this feature does not cover is still drawn, as described in User Story 1, scenario 7. How it finally looks is settled by the feature that owns that widget.
- A date, time or date-time field is drawn with whatever input type its widget declares. Django's own default for these is a plain text input, and the pack does not change it. A developer who wants the browser's own picker sets the type on the widget, and the pack draws that input as a daisyUI input too.
- A field split across several inputs, such as a split date and time, is outside this feature. Under this feature it is treated like any other widget the feature does not cover.
- A form class that turns off the browser's required attribute still shows the required marker, and the requirement still reaches assistive technology.
- A field with several error messages shows all of them, and the input's description covers all of them.
- A field that is disabled on the form keeps the disabled attribute Django gives its input. Whether a disabled or read-only field is drawn differently is settled by [#6](https://github.com/django-mvp/django-mvp-forms/issues/6).
- A host project that has not allowed the pack's name in its django-crispy-forms settings gets django-crispy-forms' own error, unchanged.
- The helper switches that place help text or errors inline or as a block change nothing. The pack places each of them one way.
- The helper switch for a horizontal form, with the label beside the input, is not part of this feature. Whether the pack should offer it is an open question, tracked in [#14](https://github.com/django-mvp/django-mvp-forms/issues/14).

## Requirements *(mandatory)*

### Functional Requirements

#### Selecting the pack

- **FR-001**: The package MUST provide one template pack for django-crispy-forms, selected by the name `daisyui` through django-crispy-forms' own settings.
- **FR-002**: Selecting the pack MUST be the only step a host project takes for its forms to be drawn by it. No layout, helper, mixin, base form class or per-field change may be required.
- **FR-003**: The pack MUST draw a form identically whether it is asked through the django-crispy-forms filter or through the tag with no layout.
- **FR-004**: The pack MUST draw a single field, asked for on its own, exactly as it draws that field inside a whole form.

#### Inputs

- **FR-005**: The pack MUST draw each of these as a daisyUI input: text, email, URL, number and password inputs, and date, time and date-time inputs.
- **FR-006**: The pack MUST draw a textarea as a daisyUI textarea.
- **FR-007**: The pack MUST keep every attribute the widget carries, including a class, a placeholder and an input type set by the developer, and add its own classes beside them.
- **FR-008**: The pack MUST leave the value, name and id of each input as Django produces them.
- **FR-009**: The pack MUST draw a field whose widget this feature does not cover, with its label, help text and errors and in its place among the other fields, without raising.

#### The field frame

- **FR-010**: Each field MUST be drawn with its label, and the label MUST be programmatically associated with the input.
- **FR-011**: A required field MUST carry a required marker, an optional field MUST NOT, and the requirement MUST be exposed to assistive technology.
- **FR-012**: A field's help text MUST be drawn with the field and MUST be named by the input as its description.
- **FR-013**: Every error message on a field MUST be drawn with the field and MUST be named by the input as part of its description.
- **FR-014**: An input whose field has errors MUST be marked invalid for assistive technology and MUST be drawn in daisyUI's error state.
- **FR-015**: An input's description MUST refer only to elements that are present on the page.
- **FR-016**: Labels, help text and error messages MUST be escaped by the template layer, keeping markup only where the form author marked the text safe.
- **FR-017**: Every id the pack emits MUST be unique on the page when forms carry different prefixes.
- **FR-018**: The links between an input and its label, help text and errors MUST follow the conventions of the Django versions the package supports, so that what Django emits on the input and what the pack emits around it agree.
- **FR-019**: The frame around a field MUST be one shared definition that later features draw their own inputs through, so that every kind of field gets the same label, marker, help text and error handling.

#### The form

- **FR-020**: Errors that belong to the form as a whole MUST be drawn once, with the form, and exposed to assistive technology as errors. A form with none MUST draw no container for them.
- **FR-021**: The pack MUST draw a form's errors when they are asked for on their own.
- **FR-022**: Through the tag, the pack MUST wrap the fields in a form element with a CSRF token, and MUST honour the helper's method, action, id, class and extra attributes for that element.
- **FR-023**: The pack MUST honour the helper switches that turn off the form element, the CSRF token, labels and errors.
- **FR-024**: With labels turned off, each input MUST still have a name assistive technology can read.
- **FR-025**: The pack MUST apply the helper's label class and field class to each label and to each element that holds an input.

#### Any daisyUI project

- **FR-026**: Every class the pack emits MUST be one that daisyUI's full CDN build defines. The pack MUST NOT rely on a class that only a Tailwind build in the host project would produce.
- **FR-027**: The pack MUST ship no stylesheet and no script, and MUST define no class of its own.
- **FR-028**: Every template the package distributes MUST be a plain Django template. None may use django-cotton or daisy-cotton by tag, include or inheritance.
- **FR-029**: The package MUST NOT import from django-mvp or require it at runtime.
- **FR-030**: Any text the pack itself adds to the page MUST be translatable.

#### Demo and documentation

- **FR-031**: The demo project MUST use the pack for its own forms and MUST have a page, reachable from its sidebar, that shows every covered input kind in each of these states: empty, holding a value, required, with help text, and with an error.
- **FR-032**: That page MUST be submittable, and MUST come back showing field errors and a form-wide error.
- **FR-033**: The demo project MUST offer the same form on a page that takes its styling from daisyUI's full CDN build alone.
- **FR-034**: The README MUST carry installation and quickstart sections that lead from a clean project to a drawn form, and a public surface entry naming the pack, the settings that select it and the input kinds it draws. The CHANGELOG MUST record the addition.

### Requirement to story map

| Requirements | Story |
|---|---|
| FR-001 to FR-009 | User Story 1 |
| FR-010 to FR-019 | User Story 2 |
| FR-020 to FR-025 | User Story 3 |
| FR-026 to FR-030 | User Story 4 |
| FR-031 to FR-034 | User Story 5 |

### Key Entities

- **Template pack**: the set of templates django-crispy-forms selects by name. This feature creates it and gives it its name.
- **Field frame**: what the pack draws around one field's input. It is the label, the required marker, the help text, the errors and the links between them. Every input the pack ever draws sits inside one.
- **Form-wide errors**: validation errors that belong to the form and to no single field.
- **Host project**: the Django project that installs the package. It supplies daisyUI and decides the theme, the page and the view.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A host project draws a form of text-like fields as daisyUI inputs after adding the package and selecting the pack, with no line of layout, helper or per-field code.
- **SC-002**: Every one of the nine covered input kinds (text, email, URL, number, password, date, time, date-time, textarea) is drawn as its daisyUI counterpart.
- **SC-003**: For every covered input kind, the label, the required state, the help text and each error are announced with the field by assistive technology. An automated accessibility check of the demo page reports no missing label, no missing description and no duplicate id.
- **SC-004**: A form that fails for a form-wide reason always shows that reason. No invalid submission comes back with nothing drawn to explain it.
- **SC-005**: Every class the pack emits is found in daisyUI's full CDN build, so a page that loads that build and has no build step shows the form fully styled.
- **SC-006**: The package installs and draws a form in a project where django-mvp, django-cotton and daisy-cotton are absent.
- **SC-007**: The demo page shows every covered input kind in all five states, and a developer following only the README reaches a drawn form.
- **SC-008**: The features that depend on this one ([#6](https://github.com/django-mvp/django-mvp-forms/issues/6) and [#7](https://github.com/django-mvp/django-mvp-forms/issues/7)) can draw their own inputs inside the field frame without redefining the label, marker, help text or error handling.

## Clarifications

### Session 2026-10-03

- Q: Which name is the pack selected by? → A: `daisyui`. Crispy packs are named after the CSS framework they emit, and the package itself is described as a daisyUI template pack. The name is public interface from the first release. (FR-001)
- Q: The roadmap item lists form-wide errors, and neither this request nor [#6](https://github.com/django-mvp/django-mvp-forms/issues/6) names them. Who draws them? → A: This feature. It introduces error handling, and a form of text fields that fails form-wide would otherwise come back with nothing shown. (User Story 3, FR-020, FR-021)
- Q: Django draws a date field as a plain text input by default. Does the pack turn it into a date picker? → A: No. The pack draws the widget it is handed with the input type that widget declares. Changing the type would change what the browser submits and how the field parses it, which is the form's business. (Edge cases, FR-007)
- Q: Which django-crispy-forms helper settings does a form with no layout have to honour? → A: Those that govern the form element, the CSRF token, labels, errors, and the label and field classes. The settings that place help text and errors inline are a matter of appearance and change nothing. A horizontal form is left as an open question in [#14](https://github.com/django-mvp/django-mvp-forms/issues/14). (FR-022 to FR-025, Edge cases)
- Q: What happens to a field whose widget belongs to a later feature? → A: It is still drawn with the same frame, in place, and nothing raises. A form never loses a field because the pack is incomplete. (FR-009)

## Assumptions

- The host project already loads daisyUI. The package ships markup only.
- "daisyUI's full CDN build" means the single stylesheet daisyUI publishes for use without a build step. This is stricter than the wording of Article XIV of the constitution, which also allows Tailwind utilities. Bringing the article into line is tracked in [#16](https://github.com/django-mvp/django-mvp-forms/issues/16). A host project with its own Tailwind build is responsible for making that build produce the classes the pack emits. The package documents that this is needed and does not do it for them.
- The supported versions are those the repository already declares: Django 5.2, 6.0 and 6.1, with django-crispy-forms 2.7 or later. The accessibility links follow what those Django versions emit.
- "Date and time" in the request means the date, time and date-time inputs Django ships as single inputs.
- Disabled and read-only states are drawn by [#6](https://github.com/django-mvp/django-mvp-forms/issues/6), as that request says. This feature only keeps the attributes Django emits.
- The pack draws each input in daisyUI's default presentation. Any choice of size, colour or variant arrives with [#11](https://github.com/django-mvp/django-mvp-forms/issues/11).
- The class names inside the rendered markup are not public interface, as the project's compatibility rule already says. The pack's name is.
- The demo project is the only place django-mvp and django-cotton appear. Its own pages may use them. The standalone demo page does not, because it stands in for a host project that has neither.
