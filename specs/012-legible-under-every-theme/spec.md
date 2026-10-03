# Feature Specification: Forms stay legible under every daisyUI theme

**Feature Branch**: `012-legible-under-every-theme`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G5 (forms follow whichever daisyUI theme the host project uses, with no per-theme work)

**Roadmap**: R8 (every daisyUI theme)

**Tracking issue**: [#88](https://github.com/django-mvp/django-mvp-forms/issues/88)

**Builds on**: FS-001 to FS-008, all merged. They define every form state this feature checks, and
none of them is respecified here.

**Input**: "A host project picks its own theme, and the pack should look right under all of them
without anyone adjusting anything per theme. Every form state the pack draws, including errors,
disabled fields, help text and the container components, should be checked under each theme daisyUI
ships, light and dark, and anything that fails contrast should be fixed."

## Summary

A host project chooses a theme and the pack has no say in it. The pack names only daisyUI's
semantic colours, so in principle a form follows any theme. Nobody has checked that it does. A red
error message on one theme's page background, or muted help text on another's, can fall below what
a person can comfortably read, and the first to find out is someone filling in a form.

This feature checks every form state the pack draws under every theme daisyUI ships, against a
stated standard for contrast. Where a state falls short and another stock daisyUI class would
pass, the pack changes to it. Where the shortfall is in daisyUI's own theme and no stock class
passes, the pack says so in a published list and adds no styling of its own. The check then stays
in the test suite, so a later change to the pack or a new daisyUI release cannot quietly make a
form hard to read.

The host project does nothing per theme, before or after.

## Terms

These words are used the same way throughout. Those that are new to the repository's vocabulary
are added to `CONTEXT.md` when the feature is built.

A **form state** is one thing the pack draws, in one condition a person can meet it in: a text
input that is empty, filled, invalid, disabled or read-only, a help text, a field error, a
form-wide error, a required marker, a button, a tab that is selected or not, an accordion group
open or closed, and so on.

A **shipped theme** is a theme built into the daisyUI version the test suite is pinned to, used as
daisyUI publishes it. Each one is either light or dark.

A **pairing** is one thing a person has to make out, together with the surface directly behind
it: a piece of text and its background, or the part of a control that shows what it is and what
state it is in and the surface around it.

The **standard** is the minimum contrast WCAG 2.2 sets at level AA: one figure for text, a lower
one for large text, and one for the parts of a control that identify it and show its state.

A **known exception** is a pairing that falls short of the standard under a named shipped theme,
that no stock daisyUI class would bring up to it, and that is published in the README.

## Clarifications

### Session 2026-10-03

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals, the constitution and the decision records.
Longer rationale is in `decisions.md`.

- **Q: The issue says "anything that fails contrast". Fails against what?**
  A: The minimum contrast WCAG 2.2 sets at level AA, for text and for the parts of a control that
  identify it and show its state. It is the published standard most projects are held to, and it
  gives a figure that can be calculated. Recorded as FR-003.

- **Q: What happens when a pairing falls short and the cause is daisyUI's own theme, so that no
  stock daisyUI class passes?**
  A: The pack adds no stylesheet and no class of its own (Article XIV), so it cannot repair it. The
  pairing becomes a known exception: named in the README with its theme, and held by the check so
  the list can neither grow nor go stale without someone noticing. Recorded as FR-007 to FR-009.

- **Q: The issue names disabled fields. WCAG exempts a disabled control from its contrast
  minimum, and daisyUI dims one on purpose. Is a disabled field held to the standard?**
  A: Its label, its help text and everything else around it are. The dimmed content of the
  disabled control itself is measured and reported under every theme and is not held to the
  figure. Recorded as FR-004.

- **Q: Contrast depends on what is behind the form, and the host project decides that. Which
  surfaces are checked?**
  A: The theme's page background, and every surface the pack draws itself, such as an accordion
  group, a modal's box, an alert or a table. A form the host project places on some other surface
  is the host project's to check. Recorded as FR-002.

- **Q: FS-007 lets a developer choose a colour and a variant, and left their contrast to this
  roadmap item. Are those choices checked?**
  A: Yes. Every colour and every variant the pack offers, on every kind of input and button that
  takes one, is a form state like any other. Recorded as FR-001.

## Scope

In scope:

- Every form state drawn by the features already merged (FS-001 to FS-008), under every shipped
  theme.
- Changing which stock daisyUI class the pack writes, where that brings a failing pairing up to
  the standard.
- A check that stays in the test suite, a demo page, and a README section.

Out of scope:

- A theme the host project writes itself or alters. The pack reads it through the same semantic
  names, and nothing here measures it.
- Anything outside the form: the page around it, the shell and the navigation are the host
  project's.
- Shipping a stylesheet, a class or a theme. The pack ships none and this feature adds none.
- New kinds of input. Rating, range, floating labels and joined inputs belong to
  [#86](https://github.com/django-mvp/django-mvp-forms/issues/86) and
  [#87](https://github.com/django-mvp/django-mvp-forms/issues/87). Each brings its own form states
  under the check when it is built (FR-012).
- Which daisyUI versions are supported, which is
  [#89](https://github.com/django-mvp/django-mvp-forms/issues/89). This feature checks the themes
  of the one daisyUI version the test suite already pins.
- Accessibility beyond contrast. Label ties, announced errors and keyboard use are specified by
  the earlier features and are not reopened.
- The continuous-integration workflows. Nothing under `.github/` changes (FR-013).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A person can read the form whatever theme the host project chose (Priority: P1)

A host project runs on one of daisyUI's themes. It may be a pale one, a dark one, or one with
strong colours. A person opens a page with a form on it. They can read every label, every help
text and every error. They can tell an input from the page around it, see which checkbox is ticked
and which tab is selected, and read the buttons. The developer who built the page did nothing for
that theme, and would have done nothing different for any other.

**Why this priority**: This is the goal. G5 says forms follow the host project's theme with no
per-theme work, and a form that follows the theme into something unreadable has not met it.

**Independent Test**: For each shipped theme, measure every pairing in every form state the pack
draws. Each one either meets the standard or is a known exception, and no pairing is a known
exception while a stock daisyUI class exists that would pass.

**Acceptance Scenarios**:

1. **Given** any shipped theme and a form drawn with no choice stated, **When** the pairings of
   its labels, required markers, help text and input values are measured on the theme's page
   background, **Then** each meets the standard or is a known exception.
2. **Given** any shipped theme and a bound form with field errors and form-wide errors, **When**
   the pairings of the error text and of the invalid inputs are measured, **Then** each meets the
   standard or is a known exception.
3. **Given** any shipped theme and a form with a disabled field and a read-only field, **When**
   the pairings are measured, **Then** the label and help text of each meet the standard or are
   known exceptions, the read-only input does too, and the dimmed content of the disabled control
   is measured and reported without being held to the figure.
4. **Given** any shipped theme and a layout using tabs, an accordion, a modal and an alert,
   **When** the pairings of everything the pack draws for them are measured, each on the surface
   that container draws, **Then** each meets the standard or is a known exception.
5. **Given** any shipped theme and a formset drawn stacked and as a table, **When** the pairings
   of its headings, cells, per-form errors and formset-wide errors are measured, **Then** each
   meets the standard or is a known exception.
6. **Given** any shipped theme and each colour and variant the pack offers, **When** an input or a
   button drawn with it is measured, **Then** it meets the standard or is a known exception.
7. **Given** any shipped theme and a boolean field drawn as a checkbox, a toggle and a switch,
   turned on and turned off, **When** the part that shows its state is measured, **Then** it meets
   the standard or is a known exception.
8. **Given** a pairing that falls short under some shipped theme, and a stock daisyUI class that
   would bring it up to the standard under every shipped theme, **When** the feature is delivered,
   **Then** the pack writes that class and the pairing is not a known exception.
9. **Given** a host project that changes from one shipped theme to another, **When** its forms are
   drawn, **Then** the pack's output is the same markup under both and the host project has
   changed no setting, class or template for the pack.
10. **Given** a form that was drawn before this feature, **When** it is drawn after it, **Then**
    its ids, its ties between labels, help text, errors and inputs, its structure and its
    submitted data are unchanged.

---

### User Story 2 - A change that makes a form hard to read is caught before it merges (Priority: P2)

A contributor changes a pack template, adds a new kind of input, or moves the pack to a newer
daisyUI release that alters a theme. They run the test suite as they always do. If the change
leaves any form state below the standard under any shipped theme, the suite fails and names the
form state, the theme and the pairing. Nobody has to open every page under every theme and look.

**Why this priority**: The first story is true on the day it is delivered. This story keeps it
true. It comes second because there has to be a legible pack before there is anything to protect.

**Independent Test**: Introduce a change that puts one pairing below the standard under one
shipped theme, and run the documented test command. It fails and names that form state, theme and
pairing. Revert the change and it passes.

**Acceptance Scenarios**:

1. **Given** the pack as delivered, **When** the documented test command is run, **Then** the
   check covers every form state under every shipped theme and passes.
2. **Given** a change that puts a pairing below the standard under a shipped theme, **When** the
   test command is run, **Then** it fails, and the failure names the form state, the theme and the
   pairing.
3. **Given** a known exception whose pairing now meets the standard, **When** the test command is
   run, **Then** it fails until the exception is removed from the published list.
4. **Given** a pairing that falls short and is not a known exception, **When** the test command is
   run, **Then** it fails. Nothing becomes a known exception without a person adding it to the
   published list.
5. **Given** the pinned daisyUI version is moved to one that adds a theme or changes a theme's
   colours, **When** the pinned data is refreshed and the test command is run, **Then** the new or
   changed theme is checked along with the rest.
6. **Given** a new kind of input or a new layout object is added to the pack and its form states
   are not under the check, **When** the test command is run, **Then** it fails.
7. **Given** the same pinned daisyUI version and the same pack, **When** the test command is run
   twice, on any supported Python and Django, **Then** the check gives the same result both times.

---

### User Story 3 - A developer can see the forms under any theme and knows what is promised (Priority: P3)

A developer is choosing a theme for a project, or deciding whether to adopt the pack at all. In
the demo project they open one page that shows every form state together, and switch it through
daisyUI's themes without editing anything. In the README they read what the pack promises under a
theme, which standard it is measured against, and the short list of places where a particular
daisyUI theme falls short and the pack cannot help.

**Why this priority**: The first two stories deliver the behaviour. This one lets a person see it
and rely on it. It is last because the forms are legible without it.

**Independent Test**: Open the demo page and choose each shipped theme in turn: every form state
is on the page and is redrawn under the chosen theme. Read the README: every known exception the
check holds is listed there, and nothing is listed that the check does not hold.

**Acceptance Scenarios**:

1. **Given** the demo project, **When** a person follows its sidebar, **Then** they reach a page
   that shows every form state the check covers.
2. **Given** that page, **When** a person chooses any shipped theme on the page itself, **Then**
   the whole page is drawn under that theme, and no setting or file was edited.
3. **Given** a page that loads daisyUI's documented CDN install and neither django-mvp nor Cotton,
   **When** the same form states are drawn on it, **Then** a person can choose any shipped theme
   there too.
4. **Given** the README, **When** a developer reads its section on themes, **Then** it states what
   is checked, the standard, which themes, and what a host project with a theme of its own should
   know.
5. **Given** the known exceptions the check holds, **When** they are compared with the list in the
   README, **Then** the two are the same.

---

### Edge Cases

- A theme draws its error colour close to its page background. The error text is a pairing like
  any other. If another stock daisyUI class passes under every shipped theme the pack changes to
  it, and otherwise it is a known exception for that theme.
- A fix that helps one theme harms another. A change of class is made only when the pairing then
  meets the standard under every shipped theme.
- The disabled control itself is dimmed until it is hard to read. It is measured and reported and
  does not fail the check. Its label and help text still have to meet the standard.
- A colour a developer chose is overridden by the error state, as FS-007 specifies. The invalid
  field is measured as an invalid field.
- A field kind the pack draws without a daisyUI class today, such as the search, telephone and
  colour inputs in [#70](https://github.com/django-mvp/django-mvp-forms/issues/70), is measured as
  it is drawn now. This feature does not decide that issue.
- Text a developer writes into a layout, such as raw HTML or attached text, carries whatever
  classes the developer gave it. The pack measures the surface and default text colour it provides
  and not the developer's own classes.
- A pairing sits on a surface inside another surface, such as a field error inside an accordion
  group inside a modal. It is measured against the surface directly behind it.
- The host project uses a theme of its own. Nothing is measured. The pack's output is the same as
  under any other theme.
- A size is in force through FS-007. Where a size makes text large or small enough to change
  which figure of the standard applies, the pairing is measured against the figure for the size
  it is drawn at.
- daisyUI removes a theme in a later version. When the pinned version moves, the theme leaves the
  check, and any known exception naming it has to leave the README with it.

## Requirements *(mandatory)*

### Functional Requirements

#### What is checked

- **FR-001**: The check MUST cover every form state the pack draws: every input kind in every
  state FS-001 and FS-002 give it, labels, required markers, help text, field errors and form-wide
  errors, disabled and read-only fields, every layout object from FS-003, FS-004 and FS-005
  including buttons and the container layout objects in each condition they can be in, formsets in
  the stacked layout and the table layout with their errors, every colour, variant and size choice
  from FS-007 on every kind of input and button that takes it, and every drawing from FS-008
  turned on and turned off.
- **FR-002**: Each pairing MUST be measured against the surface directly behind it: the theme's
  page background, or the surface the pack itself draws there.
- **FR-003**: Each pairing MUST meet the minimum contrast WCAG 2.2 sets at level AA for its kind:
  the figure for text, the figure for large text where the text is drawn large, and the figure for
  the parts of a control that identify it and show its state.
- **FR-004**: For a disabled field, the label, help text and everything the pack draws around the
  control MUST meet the standard. The dimmed content of the disabled control itself MUST be
  measured and reported for every shipped theme and MUST NOT fail the check.
- **FR-005**: The check MUST cover every theme built into the daisyUI version the test suite is
  pinned to, light and dark, as daisyUI publishes them.

#### What is fixed and what is published

- **FR-006**: Where a pairing falls short of the standard under a shipped theme, and a stock
  daisyUI class exists that brings it up to the standard under every shipped theme, the pack MUST
  write that class. A colour or a variant is the developer's to state (FS-007), and the pack
  never writes one as a repair.
- **FR-007**: Where a pairing falls short and no stock daisyUI class or modifier brings it up to
  the standard, it MUST be recorded as a known exception naming the pairing, what it is seen on
  and the theme. The pack MUST NOT add a stylesheet, a class of its own or an inline style to repair
  it.
- **FR-008**: A pairing that falls short and is not a recorded known exception MUST fail the
  check.
- **FR-009**: A recorded known exception whose pairing meets the standard MUST fail the check
  until it is removed, so the published list is never out of date.
- **FR-010**: A fix MUST NOT change anything the earlier features promise: the ids around a field,
  the ties between a label, help text, errors and their input, the structure of the markup, what
  the form submits, or the template paths. Only the daisyUI classes written may change.
- **FR-011**: The pack's output for a form MUST be the same whichever theme the host project uses.
  The host project MUST NOT have to set, pass or override anything per theme.

#### Keeping it true

- **FR-012**: The check MUST run as part of the repository's documented test command and fail it
  when a requirement above is broken. A failure MUST name the form state, the theme and the
  pairing.
- **FR-013**: The check MUST run inside the continuous-integration jobs the repository already
  has. It MUST NOT need a new job, a change to a workflow, or anything else under `.github/`.
- **FR-014**: The check MUST give the same result on every run for the same pack and the same
  pinned daisyUI version, on every supported Python and Django.
- **FR-015**: The themes and their colours MUST be taken from the same pinned daisyUI version as
  the list of classes the pack is already tested against, and MUST be refreshed in the same step
  when that version moves. A theme daisyUI adds, changes or removes comes under the check, or
  leaves it, with that refresh.
- **FR-016**: A form state added to the pack after this feature MUST come under the check. The
  suite MUST fail when a pack template draws something the check does not cover.

#### Constraints the pack keeps

- **FR-017**: Every class the pack writes after this feature MUST still be a daisyUI component
  class or modifier, or a Tailwind layout utility already allowed where daisyUI has no component
  for the job (ADR 0003), so that a page on daisyUI's documented CDN install needs no build step.
- **FR-018**: The templates this feature changes MUST stay plain Django templates with no
  django-cotton or daisy-cotton, and the feature MUST add no import from django-mvp and no runtime
  dependency (Article XIII).
- **FR-019**: Any text the pack adds MUST be translatable (Article VIII).

#### Shipping it

- **FR-020**: The demo project MUST gain a page that shows every form state the check covers, and
  on which a person can choose any shipped theme and see the page drawn under it without editing a
  setting or a file. The page MUST be reachable from the demo project's sidebar.
- **FR-021**: The same form states MUST be viewable under any shipped theme on a demo page that
  loads daisyUI's documented CDN install and uses neither django-mvp nor Cotton.
- **FR-022**: The README's public surface MUST gain a section on themes. It states what the pack
  checks, the standard, which themes are covered, every known exception, and that a theme the host
  project writes itself is not measured.
- **FR-023**: The list of known exceptions in the README and the list the check holds MUST be the
  same, and the suite MUST fail when they differ.
- **FR-024**: The CHANGELOG MUST record the feature and every class the pack now writes
  differently (Article VI). `CONTEXT.md` MUST gain the terms this specification introduces.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A person can read the form whatever theme the host project chose | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-010, FR-011, FR-017, FR-018, FR-019, FR-024 |
| US-2: A change that makes a form hard to read is caught before it merges | FR-008, FR-009, FR-012, FR-013, FR-014, FR-015, FR-016 |
| US-3: A developer can see the forms under any theme and knows what is promised | FR-020, FR-021, FR-022, FR-023, FR-024 |

### Key Entities

- **Form state**: one thing the pack draws, in one condition a person can meet it in.
- **Shipped theme**: a theme built into the pinned daisyUI version. Light or dark.
- **Pairing**: something a person has to make out and the surface directly behind it. It belongs
  to a form state and is measured once per shipped theme.
- **Known exception**: a pairing, what it is seen on and a shipped theme under which the pairing
  falls short and no stock daisyUI class would pass. Published in the README and held by the
  check.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Under every shipped theme, every pairing in every form state the pack draws meets
  the standard or is a published known exception. None falls short unlisted.
- **SC-002**: A host project changes theme with no change made for the pack: no setting, no class
  and no template.
- **SC-003**: Every published known exception is one that no stock daisyUI class would repair.
  Every shortfall that one would repair has been repaired.
- **SC-004**: A change that puts any form state below the standard under any shipped theme fails
  the documented test command, and the failure says which form state, theme and pairing.
- **SC-005**: A person can see every form state under any shipped theme on one demo page, by
  choosing the theme on the page.
- **SC-006**: A form drawn before this feature keeps its ids, its ties to labels, help text and
  errors, its structure and its submitted data. Only daisyUI class names differ.
- **SC-007**: The repository's continuous-integration workflows are the same before and after.

## Assumptions

- "Each theme daisyUI ships" means the themes built into the daisyUI version the test suite pins,
  which is the version its list of daisyUI classes is taken from. Supporting more than one daisyUI
  version at a time is [#89](https://github.com/django-mvp/django-mvp-forms/issues/89).
- "Light and dark" describes those themes, each of which is one or the other. It does not mean a
  second check of every theme with the browser's colour preference changed.
- WCAG 2.2 level AA is the standard because it is the one most projects are held to and it is a
  calculation. A stricter level can be asked for separately.
- The pack can only choose among daisyUI's classes. A shortfall that is in a daisyUI theme itself
  is daisyUI's to repair. The known exception gives the maintainer what is needed to report it
  there, and reporting it is the maintainer's decision.
- If the known exceptions turn out to be many, that is a finding to put to the maintainer when the
  feature is built. It is not a reason to add styling, which Article XIV rules out.
- A form sits on the theme's page background unless the pack draws the surface itself. A host
  project that puts a form on another surface, such as a coloured card, checks that itself.
- Whether a pairing meets the standard is settled by calculation from the theme's published
  colours. Nobody decides it by looking at a page. How the calculation is done is for planning.
- Focus rings, hover and the moment of being pressed are daisyUI's and are the same for every
  component it has. They are not form states here.
- Placeholder text is a form state, because FS-001 draws it.
- Open questions on the tracker are not settled here. Whether every tab holding an error is marked
  ([#46](https://github.com/django-mvp/django-mvp-forms/issues/46)), which extra input kinds get a
  daisyUI class ([#70](https://github.com/django-mvp/django-mvp-forms/issues/70)), and whether a
  container's own buttons follow the form's size
  ([#15](https://github.com/django-mvp/django-mvp-forms/issues/15),
  [#77](https://github.com/django-mvp/django-mvp-forms/issues/77)) are each measured as the pack
  draws them today. Whatever those issues decide comes under the check when it is built.
- Changing which Tailwind utilities are allowed is
  [#16](https://github.com/django-mvp/django-mvp-forms/issues/16). A fix here uses only what
  ADR 0003 already allows.
- The specifications for [#85](https://github.com/django-mvp/django-mvp-forms/issues/85),
  [#86](https://github.com/django-mvp/django-mvp-forms/issues/86),
  [#87](https://github.com/django-mvp/django-mvp-forms/issues/87) and
  [#89](https://github.com/django-mvp/django-mvp-forms/issues/89) are written alongside this one
  and none depends on another. Whichever of this feature and a new kind of input is built second
  brings that input's form states under the check.
- No sketch is needed before the build. The demo page gathers forms the demo project already
  shows and adds a theme chooser, and nothing in it calls for a new design.
