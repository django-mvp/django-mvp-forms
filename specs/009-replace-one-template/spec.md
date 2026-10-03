# Feature Specification: Replace one template without forking the pack

**Feature Branch**: `009-replace-one-template`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G8 (a host project can replace one template without forking the pack)

**Roadmap**: R6 (replacing one template)

**Issue**: #85

**Depends on**: nothing still open. It builds on the template pack as released in v0.1.0, which
FS-001 to FS-008 delivered, and changes none of what they draw.

**Input**: A project that wants one part of a form drawn differently should be able to replace
that single template and keep the rest of the pack. The template paths a host can override should
be listed and treated as public, so an upgrade does not quietly break an override.

## Clarifications

### Session 2026-10-03

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals, the constitution and the decision records.
Longer rationale is in `decisions.md`.

- **Q: Which templates can a host project replace: all of them, or a chosen few?**
  A: Every template the pack distributes. The roadmap item says "any single template", and the pack
  has no template that is safe to change without telling anyone, because any of them can be
  shadowed by a file at the same path whether the pack lists it or not. Recorded as FR-001 and
  FR-007.

- **Q: What exactly is promised about a listed template? Its path alone would not stop an upgrade
  breaking a replacement.**
  A: Three things: its path, what it is asked to draw, and what it is handed. A replacement is a
  copy of the pack's template with changes, so it reads the same names the pack's own template
  reads. If one of those names disappears, Django draws nothing in its place and raises nothing,
  which is the quiet break the issue is about. Recorded as FR-008, FR-012 and FR-013.

- **Q: Where does a replacement have to live for it to be found?**
  A: Wherever Django already looks for a template of that path ahead of the pack's own. The pack
  adds no setting and no registry. Most templates are found through the host project's template
  settings. The few that draw a widget are loaded by the form renderer, which looks in a different
  set of places, so the list says for each template which of the two applies. Recorded as FR-002,
  FR-004 and FR-009.

- **Q: What happens when the pack itself needs to rename or remove a template, or change what one
  is handed?**
  A: Article XI already answers it: the old form lives for one minor version before it goes. For a
  path, a replacement at the old path keeps taking effect for that version and the host project is
  warned. For a name a template is handed, the old name stays available for that version. The
  CHANGELOG says what replaces each. Recorded as FR-012 to FR-015.

- **Q: Is a host project's replacement held to what the pack promises, such as the ties between a
  label, its input and its errors?**
  A: No. The host project owns what its template draws. The pack promises that the replacement is
  handed what the original was, and that everything the replacement does not draw is drawn as
  before. Recorded as FR-006 and in the assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer replaces one template and keeps the rest (Priority: P1)

A developer likes the pack but wants one part of a form drawn their own way: the required marker,
the frame around a field, the way a radio group is set out, the table a formset is drawn as. They
copy that one template from the pack into their own project at the same path and change it. Every
form in the project now draws that part their way. Everything else is still the pack's, and the
next release of the pack still reaches them for everything they did not touch.

**Why this priority**: This is the goal. Without it the only way to change one part is to copy the
whole pack under another name and maintain all of it, which G8 exists to prevent.

**Independent Test**: In a project that selects the pack, put a replacement for one template at
its listed path, draw forms that use that template and forms that do not, then take the
replacement away and draw them again. The replaced part changes and comes back, and nothing else
differs at any point.

**Acceptance Scenarios**:

1. **Given** a host project with a replacement at the path of the template that frames a field,
   **When** the pack draws a form, **Then** every field is framed by the replacement and the
   inputs, the form-wide errors and the buttons are drawn as the pack draws them.
2. **Given** a host project with a replacement at the path of one layout object's template,
   **When** the pack draws a layout holding that layout object and others, **Then** that layout
   object is drawn by the replacement and the others are drawn by the pack.
3. **Given** a host project with a replacement for one of the templates that draws a widget, placed
   where the list says the form renderer finds it, **When** the pack draws a field with that
   widget, **Then** the widget is drawn by the replacement and its frame is the pack's.
4. **Given** a host project with a replacement for a template that several pack templates include,
   **When** the pack draws a form through any of them, **Then** each of them draws the
   replacement in the place of the original.
5. **Given** a host project with a replacement for one template, **When** the same form is drawn
   through the crispy filter, through the crispy tag and as part of a formset, **Then** the
   replacement is used in all three.
6. **Given** a replacement that reads the names the pack's own template reads, **When** the pack
   draws through it, **Then** every one of those names holds what it holds for the pack's
   template.
7. **Given** a host project whose replacement is taken away, **When** the pack draws the same
   form, **Then** the form is drawn as it was before the replacement existed.
8. **Given** a host project that replaces nothing, **When** the pack draws any form, **Then** the
   output is the same as it was before this feature.
9. **Given** a form that already names a template of its own for one layout object, for its fields
   or for the whole form, **When** the host project also has a replacement for the pack template
   that would otherwise have been used, **Then** the form's own template is still the one drawn.

---

### User Story 2 - A developer finds which template to replace and what it is given (Priority: P2)

A developer who wants to change one part of a form opens the README and finds a list of every
template in the pack. For each one it says what the template draws, what it is handed to draw it
with, and where a replacement has to be placed to be found. They pick the right template without
reading the pack's source, and they know what their copy can rely on.

**Why this priority**: Replacing a template already works for anyone willing to read the source
and guess what is safe to depend on. The list is what turns that into something the pack stands
behind. It comes second because the first story is what the list describes.

**Independent Test**: Compare the list with the templates the installed package holds, and follow
the README's worked example in a fresh project. The two sets of paths are the same, every entry
says what the template draws, what it is handed and where a replacement goes, and the example
does what the README says it does.

**Acceptance Scenarios**:

1. **Given** the published list, **When** it is compared with the templates the package
   distributes, **Then** every distributed template is on the list and every listed path is a
   distributed template.
2. **Given** any entry on the list, **When** a developer reads it, **Then** it says what the
   template draws, names what the template is handed, and says whether a replacement is found
   through the host project's template settings or through the form renderer.
3. **Given** the names an entry says a template is handed, **When** they are compared with the
   names the pack's own template reads, **Then** the pack's template reads nothing the entry
   leaves out.
4. **Given** the README's worked example of replacing one template, **When** it is followed as
   written in a host project, **Then** the form is drawn the way the example says.
5. **Given** a change to the pack that adds, removes or renames a template, or changes what one
   reads, without the list changing to match, **When** the pack's own checks run, **Then** they
   fail.
6. **Given** a template whose replacement is found only through the form renderer, **When** a
   developer reads the list, **Then** they are told what a host project has to have in place for
   a replacement to be found.

---

### User Story 3 - An upgrade does not quietly break a replacement (Priority: P3)

A developer replaced a template some releases ago and has not looked at it since. They upgrade the
pack. If nothing about that template's place in the pack changed, their replacement works exactly
as it did. If the pack moved the template, removed it or changed what it is handed, the release
still honours their replacement for one more minor version, tells them what is changing, and the
CHANGELOG says what to do about it.

**Why this priority**: This is the half of the issue that says "public". It is last because it
describes how the pack behaves when its templates change, and this feature changes none of them.
The first two stories are usable the day they land. This one earns its keep at the first release
that needs to move something.

**Independent Test**: Take a replacement written against one release and draw through it on a
later release in which the pack has renamed that template. The replacement still takes effect, a
warning names the old path and the new one, and the CHANGELOG has an entry for the change.

**Acceptance Scenarios**:

1. **Given** a replacement written against one release of the pack, **When** the host project
   upgrades to a later patch or minor release that announces no change to that template,
   **Then** the replacement is found at the same path and is handed the same names.
2. **Given** a release in which the pack renames a listed template, **When** a host project still
   has a replacement at the old path, **Then** the replacement still takes effect for that minor
   version, and the host project is warned, no later than when a form is drawn, with the old path
   and the new one named.
3. **Given** a release in which the pack stops using a listed template, **When** a host project
   still has a replacement at that path, **Then** the host project is warned in the same way for
   one minor version before the replacement stops taking effect.
4. **Given** a release in which the pack renames or withdraws a name a listed template is handed,
   **When** a replacement still reads the old name, **Then** the old name holds what it held
   before for one minor version.
5. **Given** any release that renames or removes a listed template or a name one is handed,
   **When** a developer reads the CHANGELOG for that release, **Then** it says what changed and
   what replaces it.
6. **Given** a host project with no replacement at a path the pack has renamed, **When** the pack
   draws a form, **Then** no warning is raised.
7. **Given** a release that only changes the markup or the classes inside one of the pack's own
   templates, **When** a host project has replaced a different template, **Then** the replacement
   keeps working and the change reaches the rest of the form.

---

### Edge Cases

- The replacement is placed somewhere Django looks after the pack's own template, such as an app
  listed later than the pack. Django finds the pack's template first and the replacement is not
  used. The README says where a replacement has to be for it to win.
- A replacement for a widget's template is placed where only the host project's page templates are
  found, in a project whose form renderer does not look there. It is not used. The list marks
  these templates and says what the host project needs.
- The replacement leaves out part of what the original drew, such as the errors. The pack draws
  what the replacement draws. Nothing is added back and nothing is raised.
- The replacement reads a name the list does not give for that template. The pack makes no promise
  about it.
- The host project keeps a template of its own under the pack's directory at a path the pack does
  not ship, for a layout object it wrote itself. It is unaffected, and it is not a replacement.
- A widget subclass names a template of its own. It is drawn by that template as before, and a
  replacement for the pack's widget template does not apply to it.
- The host project replaces two templates, one of which includes the other. Both replacements are
  used.
- The same replacement is in force for a formset. Every form in it is drawn through the
  replacement, stacked or as a table.
- A sibling feature adds a template to the pack. It joins the list in the release that adds it,
  and from then on it is held to the same promises.
- The markup inside a pack template changes between releases, including its class names. That is
  not a change to the public surface (Article XI), so a replacement that copied the old markup
  keeps drawing the old markup until its owner updates it.

## Requirements *(mandatory)*

### Functional Requirements

#### Replacing a template

- **FR-001**: A host project MUST be able to replace any one template the pack distributes by
  providing a template of its own at the same path. Every other template MUST still be the pack's.
- **FR-002**: A replacement MUST need nothing but the file in a place Django's template loading
  already finds ahead of the pack's. It MUST need no setting of the pack's, no Python and no
  change to any form.
- **FR-003**: A replacement MUST take effect wherever the pack would have used the original:
  through the crispy filter, through the crispy tag, for a single field drawn on its own, inside
  any layout object, and for a formset in either layout.
- **FR-004**: Wherever one pack template draws another, it MUST find it by the listed path through
  Django's template loading, so that a replacement of the inner template is used by every pack
  template that draws it. This includes the templates that draw a widget, which are found through
  the form renderer.
- **FR-005**: A replacement MUST be handed every name the list gives for that template, holding
  what it holds for the pack's own template.
- **FR-006**: The pack MUST draw what a replacement draws and add nothing to it. What a
  replacement leaves out is left out. Everything outside the replacement MUST be drawn as it is
  with no replacement in place.
- **FR-007**: The pack MUST distribute no template that is outside these promises. A template is
  either on the list or not in the package.
- **FR-008**: The ways django-crispy-forms already gives a single form to name a template of its
  own, for one layout object, for its fields or for the whole form or formset, MUST keep working
  as they do today and MUST still take precedence for that form.

#### The published list

- **FR-009**: The README's public surface MUST list every template the pack distributes. For each
  it MUST give the path, what the template draws, the names it is handed, and whether a
  replacement is found through the host project's template settings or through the form renderer.
- **FR-010**: The README MUST say where a replacement has to be placed to be found ahead of the
  pack's template, for both kinds, including what a host project needs in place for a widget
  template's replacement to be found. It MUST include one worked example of replacing a template,
  and the pack's test suite MUST draw that example as written.
- **FR-011**: The pack's own checks MUST fail when the list and the package disagree: a
  distributed template missing from the list, a listed path the package does not hold, or a pack
  template that reads a name its entry does not give.

#### Staying stable across releases

- **FR-012**: The path of a listed template, and the names it is handed, are public API under
  Article XI from the release that publishes the list. Neither MUST change in a patch or minor
  release except through the deprecation FR-013 and FR-014 describe.
- **FR-013**: When the pack renames a listed template or stops using one, a replacement at the old
  path MUST keep taking effect for one minor version. During that version the host project MUST
  be warned, no later than when a form is drawn through the old path, by a deprecation warning
  that names the old path and what replaces it. A host project with no replacement at the old
  path MUST see no warning.
- **FR-014**: When the pack renames or withdraws a name a listed template is handed, the old name
  MUST keep holding what it held for one minor version.
- **FR-015**: The CHANGELOG entry for any release that changes a listed path or a name a listed
  template is handed MUST say what changed and what replaces it. The list MUST mark a path or a
  name that is on its way out for as long as it is still honoured.
- **FR-016**: The markup a pack template writes, including its class names, is not part of this
  surface and MAY change in any release, as Article XI already says.

#### Constraints the pack keeps

- **FR-017**: A host project that replaces nothing MUST get the same output for every form as it
  did before this feature.
- **FR-018**: Any template this feature adds or changes MUST be a plain Django template with no
  django-cotton or daisy-cotton, and the feature MUST add no import from django-mvp and no runtime
  dependency (Article XIII).
- **FR-019**: The CHANGELOG MUST record that the template paths and the names the templates are
  handed are public from this release (Article VI).

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: A developer replaces one template and keeps the rest | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-017, FR-018 |
| US-2: A developer finds which template to replace and what it is given | FR-007, FR-009, FR-010, FR-011, FR-019 |
| US-3: An upgrade does not quietly break a replacement | FR-012, FR-013, FR-014, FR-015, FR-016, FR-019 |

### Key Entities

- **Replacement**: a template a host project provides at the path of one of the pack's templates,
  which Django's template loading finds ahead of the pack's. It stands in for that one template
  across the whole project.
- **Template list**: the README's record of every template the pack distributes: its path, what it
  draws, what it is handed and where a replacement is found. It is the statement of what is
  public.
- **What a template is handed**: the names a template can read when it is drawn, and for a value
  the pack itself supplies, the parts of that value the pack's own template reads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every template on the list, a host project changes how that part is drawn by
  adding one file, and changes no setting of the pack's, no Python and no form.
- **SC-002**: With one template replaced, every part of a form that template does not draw is the
  same as with nothing replaced.
- **SC-003**: Every template the package distributes is on the list, and every path on the list is
  a template the package distributes. The two never differ in a released version.
- **SC-004**: A developer can tell from the README alone which template draws a given part of a
  form, what a replacement for it can read, and where to put it. They do not need the pack's
  source.
- **SC-005**: A replacement that reads only what the list gives for its template draws the same on
  every later patch and minor release, until a release whose CHANGELOG announces a change to that
  template.
- **SC-006**: No release renames or removes a listed path, or a name a listed template is handed,
  without one minor version in which the old one still works and the change is announced.
- **SC-007**: A host project that replaces nothing sees no difference in any form after this
  feature lands.

## Assumptions

- Replacing a template means providing a whole template at the same path. Changing only a part of
  one, through named blocks the pack would have to add, is not part of this feature. Whether the
  pack should offer that is asked in #91.
- The host project owns what its replacement draws. The ties between a label, its input, its help
  text and its errors, and anything else the pack promises about its own markup, are promises
  about the pack's templates. A replacement keeps them only if its author does.
- The promises are about the pack's own templates. A template the host project adds at a path the
  pack does not ship is the host project's, and the pack says nothing about it.
- Which templates the form renderer loads, and where it looks, is Django's behaviour and the
  README describes it as it is. The pack does not change the host project's form renderer and does
  not ask for a particular one beyond what FS-002 already requires.
- This feature renames no template and changes what none of them is handed. The paths are
  published as they stand in v0.1.0. The deprecation behaviour is specified so that it exists
  before the first release that needs it.
- A template added by a later feature joins the list in the same pull request that adds the
  template. That is the later feature's work, and the check in FR-011 is what holds it to it.
- No demo page is added. The feature changes nothing a person sees in a project that replaces
  nothing, and a replacement in the demo project would change every other demo page. The worked
  example lives in the README and is drawn by the test suite.
- No sketch is needed before the build. Nothing on any page changes.
- No workflow under `.github/` changes. The checks this feature adds run in the existing test
  suite.
