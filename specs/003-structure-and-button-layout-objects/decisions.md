# Decisions: layout objects for structure and buttons

Decisions taken while writing this specification without a maintainer in the loop. Each one filled a gap the feature request (issue #7) left open. Any of them can be overturned by editing `spec.md` before the build starts.

Decisions marked **ADR: yes** are durable, architectural and non-obvious. Each gets a record under `docs/adr/` when the feature is built.

## The reading of issue #7 this specification is written from

A developer who writes a `Layout` can arrange fields with django-crispy-forms' structural layout objects, put raw HTML between them, and end the form with buttons, and the pack draws each of those as daisyUI markup. Fields inside them are drawn by FS-001. Objects that change how a single field is presented are issue #8, tabs and the other containers are issue #9, and choosing size, colour and variant from Python is issue #11. The feature serves G2, because these are most of the layout objects django-crispy-forms ships, and G3, because a group of fields has to be announced as a group and a field must not lose its label or errors by being arranged.

## D1. Layouts use django-crispy-forms' own layout classes

**Decision:** A developer imports `Fieldset`, `Row`, `Submit` and the rest from django-crispy-forms. This feature supplies templates for them and adds no layout classes of its own.

**Why:** The constitution's Article XIV says that where django-crispy-forms documents how a layout object behaves, the pack matches it. Shipping parallel classes would give every object two names and make the documentation of the upstream package wrong for this pack. Article III rules out a wrapper with no second use.

**Revisit if:** A later feature, most likely the size, colour and variant choices in issue #11, needs an argument the upstream classes cannot carry.

**ADR:** yes

## D2. `Hidden` and `StrictButton` are in this feature

**Decision:** "Plain buttons" covers both `Button` and `StrictButton`. `Hidden` is drawn here as well.

**Why:** The roadmap's R2 lists "submit, reset, plain and hidden buttons". Issue #7 names the first three and no other feature request names `Hidden` or `StrictButton`, so leaving them out would leave two documented layout objects with no owner. `Hidden` is built on the same base as `Submit` upstream, and `StrictButton` is a button.

**Revisit if:** The feature for issue #8 claims `StrictButton` because a field with buttons is where it is most used. One of the two specifications then drops it.

**ADR:** no

## D3. `MultiField` is in this feature

**Decision:** `MultiField` is drawn here, as the lowest-priority story.

**Why:** It is a documented layout object that groups fields under one label, which makes it structural. CONTEXT.md says the pack is complete when every documented layout object has a template, and G2 is an Essential goal. No feature request names it.

**Revisit if:** The maintainers decide `MultiField` is legacy and the pack should not carry it. The story can be removed without touching the other three.

**ADR:** no

## D4. A `Row` arranges its columns with no classes from the developer

**Decision:** The specification requires that a `Row` whose `Column`s have no classes still arranges them as columns, and that this works on a page loading only what FS-001 requires of a host project. Classes the developer supplies are added to the drawn container. How the pack achieves it is left to planning.

**Why:** A `Row` that does nothing until the developer adds utility classes would not serve G1's "no per-form work" in spirit, and would not match what a developer coming from the upstream documentation expects. The mechanism is not a specification matter, and it is constrained by the ruling that the pack keeps to daisyUI's standard classes. daisyUI has no column component, so the mechanism is an open question, filed as issue #18.

**Revisit if:** Issue #18 concludes that no arrangement is possible within daisyUI's own classes. FR-005 and acceptance scenario 8 of the first story would then change to say the containers carry the developer's classes and nothing more.

**ADR:** yes, once issue #18 is settled

## D5. Buttons added to the form helper draw the same as buttons in a layout

**Decision:** A `Submit` added with the helper's `add_input` is drawn by the same template as one in a layout. Where those buttons are placed in the form is FS-001's.

**Why:** Upstream documents both ways of declaring a button. The button template belongs with the buttons. The form wrapper that loops over helper-added buttons belongs with the form.

**Revisit if:** FS-001's specification does not cover helper-added buttons at all. That placement would then need an owner.

**ADR:** no

## D6. Developer-written content is not escaped, context values are

**Decision:** The content of an `HTML` object, a `Fieldset` legend, a `MultiField` label and a `StrictButton` is treated as template source and drawn as written. Values it reads from the page context are escaped by the template layer.

**Why:** This is upstream's documented behaviour, and the content is written by the developer in Python, not typed by a person using the host project. Article V requires that interpolated values go through the template layer, which this keeps.

**Revisit if:** Never, short of upstream changing it.

**ADR:** no

## D7. No size, colour or variant choices here

**Decision:** This feature draws buttons with daisyUI's button and passes through any class the developer gives a single button. It offers no way to set a size, colour or variant for all buttons at once.

**Why:** That is issue #11, which depends on this feature. Passing a class through is upstream behaviour and costs nothing.

**ADR:** no

## D8. Demo pages use text fields only

**Decision:** The demo pages for this feature use the fields FS-001 draws.

**Why:** This feature depends on issue #5 and not on issue #6. Using a select or a checkbox on its demo pages would add a dependency the feature request does not have.

**ADR:** no

## D9. No prototype before the build

**Decision:** The feature is built without a prototype stage for the maintainer to look at first.

**Why:** The markup is stock daisyUI and the structure is the one upstream documents, so there is little design to judge. The demo pages are reviewed when the feature is.

**ADR:** no

## How the specification was produced

The spec number, directory and branch were fixed in advance because several specifications were being written at the same time, so the files were written from the specification template by hand and no script chose a number.

The clarification scan was run against the draft and answered from the repository's own documents. Its six questions and answers are in `spec.md` under Clarifications. Categories with nothing to resolve: data model (the feature has none), performance and scale, observability, and compliance.
