# Feature Specification: django-tomselect support

**Feature Branch**: `014-django-tomselect-support`

**Created**: 2026-10-09

**Status**: Draft

**Serves**: G12 (fields and widgets from popular third-party Django packages draw well in the
pack), G4 (size, colour and variant can be set from Python), G5 (forms follow whichever daisyUI
theme the host project uses)

**Roadmap**: none. Support for a third-party package's widgets is added when a project needs it
and carries no roadmap item (Article XV).

**Issue**: #138

**Depends on**: nothing that is still open. It builds on FS-002 (#6) for the select a
django-tomselect control stands beside, on FS-007 (#11) for size, colour and variant, on FS-005
(#9) for the modal, on FS-006 (#10) for a formset drawn as a table, and on FS-012 for the
legibility standard. All are released.

**Input**: Several projects that use this pack rely on django-tomselect for their select boxes,
mostly where the options are fetched from the server as a person types. Its controls should sit in
a daisyUI form as if the pack had drawn them, including controls that show chosen values as tags
and take new ones, and dropdowns that list their options under group headings.

## Clarifications

The coverage scan found five ambiguities. Each was resolved from what the maintainer said when the
feature was agreed, the goals, the constitution and the decision records. Longer rationale is in
`decisions.md`.

- **Q: Tom Select builds its control and its dropdown in the browser, under class names of its
  own. The pack ships no stylesheet. How can the control be made to match?**
  A: The package ships a stylesheet, `tomselect.css`, for django-tomselect's controls and nothing
  else. The developer adds it to their own pages. The pack never loads it, and neither does the
  widget. Each third-party package supported later gets a stylesheet of its own, and there is
  never one stylesheet for all of them. Article XIV is amended to allow this. Recorded as FR-001
  to FR-006.

- **Q: Which of django-tomselect's widgets are covered?**
  A: The four that draw a select: single and multiple, each for a model-backed field and for a
  field with plain choices. The token widget, which draws a search filter and not a select, is
  not. Recorded as FR-007.

- **Q: What does "tagging" mean here?**
  A: A control that holds several values, shows each as a tag a person can remove, and offers to
  add a value that is typed and does not exist yet. django-tomselect already provides the
  behaviour. This feature draws it. Recorded as FR-016 to FR-019.

- **Q: django-tomselect draws a group heading in the dropdown, but has no setting that says which
  group an option fetched from the server belongs to. Who fills that gap?**
  A: This package does, in its support for django-tomselect. A developer names the group of each
  option in one documented place and writes no template. Recorded as FR-020 to FR-023.

- **Q: Against which themes is legibility checked?**
  A: daisyUI's `light` and `dark`. The check over every shipped theme that FS-012 runs for the
  pack's own markup is not extended to this stylesheet. Recorded as FR-014.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer draws a django-tomselect field in a daisyUI form (Priority: P1)

A developer has a host project that uses the pack and django-tomselect. They add the package's
`tomselect.css` to their base template, once. Every django-tomselect select in every form is then
drawn as a daisyUI control: beside a stock select or text input it has the same height, border,
corner radius, focus state, error state and disabled state, and it changes with the theme. The
dropdown, the options in it, the option under the pointer, the chosen option, the "loading" and
"no results" lines and the clear button all belong to the same theme. The developer writes no CSS
and changes no form.

**Why this priority**: This is the request. Without it, every project that uses both packages
writes and maintains its own stylesheet for the same control.

**Independent Test**: Open the demo page for django-tomselect. A form holds a stock select, a text
input and a single and a multiple django-tomselect control. Compare them at each size, in error
and disabled, switch between a light and a dark theme, open each dropdown, search, and clear a
value. Submit the form and read back the values it cleaned to.

**Acceptance Scenarios**:

1. **Given** a page that loads the stylesheet, **When** a form holding a django-tomselect field is
   drawn through `{{ form|crispy }}` or `{% crispy form %}`, **Then** the control is styled by
   the stylesheet with no class, attribute or template written by the developer.
2. **Given** a size stated for the form or for the field, **When** the control is drawn, **Then**
   it takes that size as a stock select does, and the field's own statement wins over the form's.
3. **Given** a colour or a variant stated for the form or for the field, **When** the control is
   drawn, **Then** it takes the colour or variant a stock select would.
4. **Given** a field in error, **When** the control is drawn, **Then** it shows the error state a
   stock select shows and no stated colour, and its errors and help text describe it as they do
   any field.
5. **Given** a disabled field, **When** the control is drawn, **Then** it is drawn as disabled and
   cannot be opened.
6. **Given** the host project changes its daisyUI theme, **When** the page is drawn again,
   **Then** the control, its tags and its dropdown follow the new theme with no change to the
   stylesheet.
7. **Given** a page that does not load the stylesheet, **When** the same form is drawn, **Then**
   the control works and is styled by django-tomselect alone, as it is today.
8. **Given** a page that loads the stylesheet and holds no django-tomselect control, **When** it
   is drawn, **Then** nothing on it is drawn differently.
9. **Given** a host project without django-tomselect installed, **When** the pack is installed
   and a form is drawn, **Then** it draws exactly as before this feature.
10. **Given** a form with a django-tomselect field, **When** it is submitted, **Then** it
    validates and cleans to the same data as it did before this feature.
11. **Given** a control whose options are being fetched, **When** the fetch is in progress,
    **Then** the control shows that it is loading and daisyUI's own `loading` component is not
    drawn in its place.

---

### User Story 2 - A developer offers tagging (Priority: P2)

A developer has a field that holds several values, such as the keywords of a record. They use
django-tomselect's multiple control and turn on its option to create values. In the form each
chosen value is a tag with a button that removes it. When a person types a value that is not
among the options, the dropdown offers to add it, and choosing that adds a tag like the others.

**Why this priority**: Tagging is the most common reason these projects use the multiple control,
and its tags and "add" option are the parts furthest from anything daisyUI draws by itself.

**Independent Test**: On the demo page, pick three values in the tagging control, remove one with
its button and one with the keyboard, type a value that does not exist, add it, and submit.

**Acceptance Scenarios**:

1. **Given** a multiple control with values chosen, **When** it is drawn, **Then** each value is a
   tag, the tags wrap onto further lines as they need to, and the control grows with them.
2. **Given** a tag, **When** a person uses its remove button or removes it with the keyboard,
   **Then** the tag goes and the value is no longer submitted.
3. **Given** a control that creates values, **When** a person types a value that is not an
   option, **Then** the dropdown offers to add it, set apart from the options that exist.
4. **Given** that offer, **When** the person takes it, **Then** the new value becomes a tag drawn
   as every other tag is.
5. **Given** a tagging control at any stated size, in error or disabled, **When** it is drawn,
   **Then** its tags follow the size and the control shows the state as in the first story.
6. **Given** a single control that creates values, **When** a person types a new one, **Then**
   the same offer is drawn.

---

### User Story 3 - A developer groups the options in a dropdown (Priority: P2)

A developer has options that belong to groups, such as concepts listed under the vocabulary each
comes from. They say, in one place, which group each option is in. The dropdown lists the options
under a heading for each group, whether the options came with the page or were fetched from the
server. The developer writes no template to make this work.

**Why this priority**: The maintainer's projects need it now, and today each one carries a
template of its own to get it.

**Independent Test**: On the demo page, open the grouped control, see the options under their
headings, search so that only some groups have matches, and pick an option from the second group.

**Acceptance Scenarios**:

1. **Given** options that name a group, **When** the dropdown opens, **Then** each group's options
   are listed together under the group's heading.
2. **Given** a group heading, **When** a person moves through the dropdown with the keyboard or
   the pointer, **Then** the heading cannot be chosen.
3. **Given** some options that name a group and some that name none, **When** the dropdown opens,
   **Then** the options with no group are listed without a heading.
4. **Given** a search that matches options in some groups only, **When** the results are drawn,
   **Then** only those groups are shown.
5. **Given** options fetched from the server a page at a time, **When** a later page arrives,
   **Then** its options join the groups they name.
6. **Given** a control where the developer names no group, **When** it is drawn, **Then** its
   dropdown is the plain list it was before.

---

### User Story 4 - A developer puts the control in a modal, a table and a page htmx loads (Priority: P3)

A developer uses the control where their forms already live: in a daisyUI modal, in a formset
drawn as a table, and in a form that htmx puts on the page after it has loaded. In each place the
control starts up without help from the developer and its dropdown can be seen and used in full.

**Why this priority**: The control is of little use to these projects if it only works in a form
that is on the page from the start. It comes after the first three stories because they decide
what the control and its dropdown are.

**Independent Test**: On the demo page, open the modal and pick a value from a dropdown longer
than the modal. Pick a value in the last row of the table formset. Press the button that fetches a
form with htmx, then pick a value in the form that arrives. Follow a boosted link to another demo
page and use the control there.

**Acceptance Scenarios**:

1. **Given** a form in a daisyUI modal, including the pack's own `Modal` layout object, **When**
   the dropdown opens, **Then** it is drawn above the modal, is not cut off by it, and every
   option can be reached and chosen.
2. **Given** a formset drawn as a table, **When** the dropdown of a control in any row opens,
   **Then** it is not cut off by the table or by the element that scrolls the table.
3. **Given** a page that has loaded, **When** htmx swaps in content that holds a control,
   **Then** the control starts up and is styled as one drawn with the page.
4. **Given** a site that moves between pages with htmx, **When** a person arrives at a page that
   holds a control, **Then** the control starts up as it does on a full page load.
5. **Given** content that holds a control is swapped in more than once, **When** the last swap
   settles, **Then** there is one control for each field and none is doubled.

---

### Edge Cases

- A floating label is not supported for a django-tomselect control. The README says so, and this
  feature does not change what the pack draws when one is stated.
- Text attached to the control, buttons joined to it and a joined group that holds it are not
  supported. The README says so, and this feature does not change what the pack draws when one is
  asked for.
- django-tomselect's token widget is not covered. The stylesheet does not style it.
- The developer turns on a plugin other than the clear button and the remove button: the dropdown
  header, the dropdown footer, the search input inside the dropdown or checkboxes beside the
  options. It works and keeps django-tomselect's own look. Support for one is added when a project
  asks for it.
- The host project sets django-tomselect to one of its Bootstrap looks. This is not supported, and
  the README names the one setting that is.
- The host project loads the stylesheet before django-tomselect's own. The README states the
  order that works, and the documented order is the only one supported.
- A control holds more tags than fit on one line. They wrap, and the control grows.
- A tag's text or an option's text is longer than the control is wide. It does not make the
  control or the page wider.
- An option's text is supplied by a person. It is escaped in the dropdown and in a tag exactly as
  django-tomselect escapes it today.
- A group has no options left after a search. Its heading is not drawn.
- The dropdown opens near the bottom of the window or of a modal. Where it opens is
  django-tomselect's to decide, and the stylesheet does not stop it being reached.
- A control is drawn in a form with labels off, or hidden. It is named, or hidden, as a stock
  select is.
- The same form is drawn twice. Both draws give the same markup, and the form's own widget is
  left as it was.
- A page is served with a Content Security Policy. Whatever django-tomselect needs from the
  policy is unchanged by this feature, and the stylesheet needs only that stylesheets from the
  site itself are allowed.

## Requirements *(mandatory)*

### Functional Requirements

#### The stylesheet

- **FR-001**: The package MUST ship a stylesheet named `tomselect.css` among its static files,
  for django-tomselect's controls only.
- **FR-002**: The developer MUST be the one who adds it to a page. The pack's templates, its
  template tags and the widget's media MUST NOT load it.
- **FR-003**: Every rule in the stylesheet MUST apply only to a Tom Select control, to its
  dropdown, to the element django-tomselect announces a choice in, or to a box that holds an
  open control and would otherwise cut its dropdown off. Loading it MUST change nothing on a
  page that holds no control.
- **FR-004**: The stylesheet MUST take every colour, radius, border width and field size from the
  variables the daisyUI theme sets, and MUST name no colour of its own, so that it follows any
  theme with no per-theme work.
- **FR-005**: A page that does not load the stylesheet MUST draw the control as django-tomselect
  styles it. Nothing the pack writes may depend on the stylesheet being present.
- **FR-006**: Article XIV of the constitution, the README's statement that the package ships
  markup and no stylesheet, and the decision records that rest on it MUST be amended to say: the
  pack's own templates still define no class and need no stylesheet, and the package may ship one
  optional stylesheet for each supported third-party package whose controls are built by script,
  which the developer loads. There MUST never be one stylesheet for several packages.

#### What is covered

- **FR-007**: The support MUST cover django-tomselect's single and multiple select widgets, for
  model-backed fields and for fields with plain choices. It MUST NOT cover the token widget.
- **FR-008**: django-tomselect MUST NOT become a dependency of the package. The pack MUST draw
  every form as before in a project where django-tomselect is not installed.
- **FR-009**: The package MUST add no view, URL, field class or widget class for this feature.
  The developer keeps using django-tomselect's own.

#### The control

- **FR-010**: A django-tomselect control MUST take the size stated for the form or for the field,
  from `xs` to `xl`, by the same rules of precedence as a stock select.
- **FR-011**: The control MUST take the colour and the variant stated for the form or for the
  field, for each colour and variant a stock select has. A control in error MUST show the error
  state and no stated colour.
- **FR-012**: The control MUST have a state of its own for each of: resting, focused, in error,
  disabled, and open. Its label, required marker, help text and errors MUST be tied to it as they
  are to a stock select.
- **FR-013**: The dropdown MUST have a drawing for each of: an option, the option under the
  pointer or the keyboard, a chosen option, a disabled option, the line shown while options are
  fetched, the line shown while more are fetched, the line shown when nothing matches, and the
  line shown when there is nothing more to fetch.
- **FR-014**: Under daisyUI's `light` and `dark` themes, every pairing of text and background the
  stylesheet sets MUST meet the contrast standard FS-012 applies to the pack. A pairing that is
  one daisyUI itself draws and that FS-012 already lists as a known exception counts as that
  exception. No other theme is checked.
- **FR-015**: While options are fetched the control MUST show that it is loading, and daisyUI's
  `loading` component MUST NOT be drawn on the control in its place. A developer MUST NOT have to
  set anything per field for this to hold.

#### Tagging

- **FR-016**: In a multiple control each chosen value MUST be drawn as a tag. Tags MUST wrap, the
  control MUST grow with them, and a tag MUST follow the control's size.
- **FR-017**: The button that removes a tag MUST be drawn as part of the tag, MUST be reachable
  as django-tomselect makes it reachable, and MUST show which tag it belongs to when it is under
  the pointer or has focus.
- **FR-018**: The offer to add a typed value MUST be drawn in the dropdown, set apart from the
  options that exist, in a single and in a multiple control.
- **FR-019**: Creating and saving the new value stay with django-tomselect and with the
  developer's own view. This feature MUST NOT change what is submitted or saved.

#### Grouping

- **FR-020**: A developer MUST be able to name the group of each option in one documented place,
  for options that come with the page and for options fetched from the server, and MUST NOT have
  to write or replace a template to do so.
- **FR-021**: The dropdown MUST list each group's options together under the group's heading,
  and options that name no group without one. A heading MUST NOT be choosable.
- **FR-022**: A group with no option to show MUST NOT be drawn, and options that arrive in a
  later fetch MUST join the group they name.
- **FR-023**: A control whose developer names no group MUST draw the dropdown it drew before.

#### Where the control is used

- **FR-024**: In a daisyUI modal, including the pack's `Modal` layout object, the dropdown MUST
  be drawn above the modal and MUST NOT be cut off by it.
- **FR-025**: In a formset drawn as a table, the dropdown of a control in any row MUST NOT be cut
  off by the table or by what scrolls it.
- **FR-026**: A control in content that htmx swaps into a loaded page, and a control on a page
  reached by htmx navigation, MUST start up and be styled as one drawn on a full page load, with
  nothing written by the developer beyond what django-tomselect and htmx already ask for.
- **FR-027**: Swapping the same content in more than once MUST leave one control for each field.

#### Plugins

- **FR-028**: Of django-tomselect's plugins, the support MUST cover the clear button and the
  remove button, which the first two stories rely on. It MUST NOT undertake to draw any other
  plugin. The README MUST say which plugins are covered, and that support for another is added
  when a project asks for it.

#### Demo, documentation and tests

- **FR-029**: The demo project's sidebar MUST list third-party widgets in a group of their own,
  apart from the standard widgets.
- **FR-030**: The demo project MUST gain a page for django-tomselect in that group. It MUST show
  a single and a multiple control beside a stock select and a text input, each state of FR-012,
  each size, the colours and the variant, tagging, grouping, a control in
  a modal, a control in a table formset, a form fetched with htmx, and a form to submit that
  shows the values it cleaned to. The same controls MUST be shown on a page styled by daisyUI's
  CDN install alone, with no django-mvp.
- **FR-031**: The README MUST say how to turn the support on: what to install, which stylesheet
  and scripts to load and in what order, the one django-tomselect look that is supported, how a
  group is named, and what is not supported. It MUST name the django-tomselect releases the
  support is tested against. The CHANGELOG MUST record the addition, and the glossary MUST gain
  "Tagging" and "Option group".
- **FR-032**: The suite MUST run with django-tomselect installed as a development dependency, and
  MUST also show that the package imports nothing from it.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A developer draws a django-tomselect field in a daisyUI form | FR-001 to FR-015, FR-028 to FR-032 |
| US-2: A developer offers tagging | FR-016 to FR-019, FR-028, FR-030, FR-031 |
| US-3: A developer groups the options in a dropdown | FR-020 to FR-023, FR-030, FR-031 |
| US-4: A developer puts the control in a modal, a table and a page htmx loads | FR-024 to FR-027, FR-030, FR-031 |

FR-030 and FR-031 land with the first story and are extended by each story after it, so every
story shows its own behaviour on the demo page and documents its own surface.

### Key Entities

- **Control**: what django-tomselect draws in place of a select: the box a person types in, the
  chosen value or tags inside it, and the dropdown.
- **Tagging**: a control that holds several values, draws each as a tag that can be removed, and
  offers to add a value that is typed and does not exist.
- **Option group**: a named set of options listed together in a dropdown under a heading that
  cannot be chosen.
- **Plugin**: one of the additions to a control that django-tomselect lets a developer turn on.
  This feature covers two, the clear button and the remove button.
- **Supported package**: a third-party Django package whose widgets the pack undertakes to draw
  well. django-tomselect is the first with a stylesheet of its own.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gets every django-tomselect control in a host project drawn as a
  daisyUI control by adding one stylesheet to one template. They write no CSS, no class and no
  template, and change no form.
- **SC-002**: Every size, colour and variant a stock select takes can be stated for a
  django-tomselect control in the same words, and takes effect.
- **SC-003**: A form with a django-tomselect field validates and cleans to the same data before
  and after this feature, with and without the stylesheet.
- **SC-004**: A project without django-tomselect, and a page that loads the stylesheet and holds
  no control, are drawn exactly as before.
- **SC-005**: A developer groups the options of a dropdown without writing or replacing a
  template.
- **SC-006**: The control starts up and its dropdown can be used in full in a modal, in a table
  formset and in content htmx loads, with nothing added by the developer.
- **SC-007**: A project that carries its own stylesheet and template for django-tomselect can
  delete both and keep every control it has.

## Assumptions

- How the control, its tags and its dropdown look is settled with the maintainer on running
  pages before the build is planned. This specification says what must be drawn and what it must
  follow, and no acceptance scenario fixes a measurement, a colour or a wording.
- "Matches a stock select" means that it takes the same daisyUI theme variables for the same
  parts. It is not a promise that the two are identical to the pixel in every browser.
- django-tomselect goes on providing searching, fetching, creating, the plugins and starting a
  control after an htmx swap. Where it falls short of an acceptance scenario here, the gap is
  recorded as an issue in this repository and the scenario is marked as waiting on it. This
  package does not patch django-tomselect's scripts.
- Grouping is the one place this package adds to django-tomselect's behaviour and not only to its
  look, because django-tomselect has no setting for it. If a later django-tomselect release
  provides one, this package's way is retired in favour of it.
- The developer loads django-tomselect's own scripts as its documentation says. Whether
  `tomselect.css` is loaded beside django-tomselect's stylesheet or in its place is decided when
  the build is planned, and the README states exactly what to load.
- Which django-tomselect releases are supported is stated in the README and is not part of the
  support window of FS-013, whose periods apply to Django, django-crispy-forms and daisyUI.
