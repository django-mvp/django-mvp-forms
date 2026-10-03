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

## Decisions taken while planning the build

## D10. Buttons added to the form helper are placed by this feature

**Decision:** The form wrapper gains one include, `daisyui/inputs.html`, after the fields and inside the form element. It draws each button the helper holds with the same template a button in a layout uses.

**Why:** D5 expected FS-001's form wrapper to place these buttons and said the placement would need an owner if it did not. FS-001 was delivered without it, and its own decisions say buttons belong to this feature. The second story's seventh scenario cannot pass unless something draws them, so the owner is this feature.

**Revisit if:** A later feature needs the helper's buttons somewhere other than after the fields.

## D11. A field inside a `MultiField` keeps its own errors

**Decision:** Each field in a `MultiField` is drawn by the field frame, with its own label, help text and errors. The group does not collect its fields' errors at the top.

**Why:** The Bootstrap packs gather the errors above the group and drop each field's own. FR-008 and the fourth story's second scenario require an error to stay tied to its field, and ADR 0006 puts every input inside the one frame.

**Revisit if:** A host project needs the gathered form. It can pass `field_template` to the `MultiField`.

## D12. A hidden input has no class and no id

**Decision:** `Hidden` is drawn as an input with its type, name, value and any attributes passed as keyword arguments. The `hidden` class and the generated id django-crispy-forms gives it are not written.

**Why:** `hidden` is not a daisyUI class and does nothing on an input that is already hidden. The Bootstrap packs leave both out, and Article XIV says the pack matches documented behaviour. A developer who needs an id passes `id=` as a keyword.

**Revisit if:** Never, short of django-crispy-forms changing it.

## D13. Class names written for other packs are dropped by name

**Decision:** A filter in the pack's template library, `daisyui_classes`, removes `btn-inverse`, `ctrlHolder`, `blockLabel` and `error` from a class string, and removes repeats. Button and `MultiField` templates pass django-crispy-forms' class strings through it. The buttons keep `btn` and `btn-primary`, which django-crispy-forms writes itself and daisyUI defines.

**Why:** django-crispy-forms joins its own default classes and the developer's into one string, so a template cannot tell them apart. Its defaults were written for Bootstrap and uni-form. Three of the four buttons already come out as daisyUI buttons. Subclassing the layout objects to change the defaults is ruled out by D1.

**Revisit if:** django-crispy-forms changes the classes it writes. The button tests fail when it does.

## D14. A row is a flex container and a column takes an equal share

**Decision:** `Row` is drawn with `flex flex-col gap-4 md:flex-row` and `Column` with `flex-1 min-w-0`. `ButtonHolder`, `FormActions` and the helper's buttons are drawn with `flex flex-wrap gap-2 mt-4`. The developer's classes are added after these.

**Why:** daisyUI has no component for either job, and ADR 0003 allows a Tailwind utility for layout in that case. Flex gives equal columns for any number of them without counting, and every one of these utilities is in django-mvp's packaged stylesheet as well as in Tailwind's browser build. A grid with automatic columns would have stacked on a django-mvp page. This is the working answer to issue #18.

**Revisit if:** The maintainer picks another option on issue #18, or daisyUI gains a layout component.

## D15. What the design review changed

One reviewer read the plan before any code, as a check on fit with the specification, on security and on structure. It approved the plan. Nothing it found forced a change of approach. Its findings were applied as edits:

- The test of django-crispy-forms' documented examples names where each example comes from. Three do not parse as printed and are repaired by quoting a string. `MultiField` has none.
- Each demo form builds its own layout, and every id and button name carries the form's prefix. A form prefix does not reach a layout object's id.
- A layout object is built per form instance and never shared. django-crispy-forms stores a button's rendered value back on the object, so a second draw renders the first draw's output as a template again. Implementers are told to keep to this.
- `tests/settings.py` already lists the test template directory, so that edit was dropped.
- `ButtonHolder` accepts no attributes beyond an id and classes, so that case is tested on `FormActions` only.
- The demo gains a row that holds fields directly with no column, which is the form django-crispy-forms documents, so the maintainer sees it when confirming issue #18.

**ADR:** none — a record of plan edits, nothing a later feature inherits

## D16. The first layout objects page draws its form without the helper's form element

**Decision:** `LayoutObjectsForm` sets `form_tag` off and the demo page writes the `<form>`, its CSRF token and its submit button itself, as the text inputs page does. Both pages build the submittable form and the form that already fails from the one class, each with a prefix.

**Why:** The buttons that belong inside the helper's form element arrive in the next story. Until then the page needs a submit button, and the only place for one is the page. One class with a prefix keeps every id apart and repeats no layout.

**Revisit if:** The buttons story moves the submit button into the layout, at which point the submittable form draws its own `<form>`.

## D17. The class test's list and states grow with each story

**Decision:** Each story adds parametrised states and layout utility names to `tests/test_pack/test_independence.py`, a test file that existed before this feature. The check that guards existing tests flags those edits, and they are accepted.

**Why:** ADR 0003 says a feature that needs a layout utility adds it to that test by name. The edits add cases and names. No existing assertion is changed or removed.

**ADR:** none — a note on how one test file is maintained, already covered by ADR 0003

## D18. The submittable form draws its own form element, and the extra demo forms are GET forms

**Decision:** `LayoutObjectsForm` keeps `form_tag` on for the form to submit, which now ends in a `FormActions`, and the page no longer writes a `<form>` or a submit button of its own. The form that already fails is built with `form_tag=False`, so its buttons are drawn with no form element. The helper-buttons form and the small `Row` layout use `form_method = "get"`, so submitting one only reloads the page and the view's `post` is not reached by them.

**Why:** D16 left the page writing the form until the buttons arrived. Two further submittable POST forms would need the view to tell which one was posted, which this story does not need. `novalidate` moves to `helper.attrs`, so an empty submit still comes back from the server with field errors.

**Revisit if:** A story needs the extra forms to post to the view.

**ADR:** none — a demo arrangement
