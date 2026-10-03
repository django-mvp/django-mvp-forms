# Decisions: 006 Formsets

The reading of issue #10 this specification was written from, and the choices made where the issue
was silent. The maintainer handed the specification over on 2026-10-03, so each of these was
settled from the repository's own documents and is open to veto on the pull request.

## D1: The reading of the request

A formset handed to the pack through django-crispy-forms draws whole: every form, the management
form, every hidden field and every error. The developer picks stacked or table in Python. The pack
draws and nothing more. Adding and removing rows in the browser, the view that builds and saves the
formset, and the page around it stay with django-mvp or the host project. The feature serves G1 and
is the whole of roadmap item R4. It depends on #6 for the checkbox the delete input is drawn with,
and through #6 on #5 for every other input, label and field error.

**ADR:** none. This restates the issue and the README's scope section.

## D2: The layout is chosen with the helper setting crispy-forms already has

The issue says "either one after another or as a table" and does not say how a developer chooses.
django-crispy-forms already documents a helper attribute for selecting a formset's template, and
its own packs use it to offer a table. The README says matching crispy-forms' documented behaviour
wins over inventing a new one, and Article III rules out a new abstraction without a second use.
So the pack adds no setting, no template tag argument and no helper subclass. Stacked is the
default because it is what crispy-forms draws when nothing is chosen, and it is the only layout
available when a formset is drawn without a helper.

**ADR:** none at this stage. It qualifies: it fixes a public interface and a later reader would ask
why there is no setting. Record it under `docs/adr/` when the feature is built, since a number is
claimed only when the file lands on the main branch.

## D3: In the table, labels are column headings and every input is still named

A table with a visible label in every cell repeats itself, and a table with labels only in the
headings leaves each input unnamed for a screen reader. G3 does not allow the second. So the label
is shown once per column and each input carries a programmatic name and description of its own. How
that is done in markup is a planning question.

**ADR:** none. It follows from G3 and binds only the table template.

## D4: A helper's layout applies when stacked and not in the table

In the stacked layout each form is drawn as a single form, so a layout applies to each in turn. In
the table a layout object such as a fieldset or a row of columns has no meaning inside a table row.
The table templates crispy-forms users know take the form's visible fields in order and ignore the
layout, and the pack does the same.

**ADR:** none. It matches crispy-forms' behaviour, which the README already makes the rule.

## D5: Where each kind of error goes

The issue says errors sit "beside the row they belong to". A formset has three kinds. A field's
error goes with its input, as in a single form. A form-wide error goes with that form: inside it
when stacked, in or directly beside its row in the table. A formset-wide error belongs to no row,
so it is shown once, apart from the forms. Whether the table uses a cell or a row of its own for a
form-wide error is left to planning.

**ADR:** none. Placement inside one feature's templates.

## D6: No empty form and no promised script hooks

django-mvp has to add rows in the browser, and a script that does so usually copies a spare empty
form. Drawing one would put half of that behaviour in this package, which the maintainer ruled out.
The specification promises only that each form is one distinguishable unit. What django-mvp needs
beyond that could not be settled from this repository's documents, so it is filed as issue #13 and
does not block the feature.

**ADR:** none. The boundary is already Article XII. The open part is tracked in #13.

## D7: Scope limits taken without asking

- Nested formsets are out of scope.
- The table layout assumes every form has the same fields. A formset whose forms differ draws
  correctly when stacked.
- The pack draws forms in the order the formset yields them and never reorders from the order
  inputs.
- Buttons on the helper belong to #7. Size, colour and variant belong to #11 and #12.
- How the table behaves on a narrow screen, where help text sits and whether an empty table shows
  its headings are judged by eye at build time, because the testing standard gives appearance no
  test.

**ADR:** none. Each is a boundary of this feature and none constrains later work.

## D8: The glossary changes with this feature

CONTEXT.md lists formset among the words this package does not use and says an issue needing it is
probably filed in the wrong repository. The README, G1 and roadmap item R4 all say the pack draws
formsets, and the maintainer confirmed that on 2026-10-03. The glossary is the document out of
step, so the feature's build defines formset, stacked layout and table layout there and keeps the
line between drawing a formset and handling one (FR-021).

**ADR:** none. A correction to a document, not a decision about structure.

## D9: No prototype before the build

Both layouts are assembled from daisyUI's stock table and the inputs issues #5 and #6 already
define. Nothing here needs a new design, so the feature goes to planning without a prototype
round. The appearance points in D7 are looked at on the demo pages when the build is reviewed.

**ADR:** none. A process choice for this feature only.

## D10: In the table, a form's own errors sit in its row's first cell

D5 left a cell or a row of its own to planning. A row of its own would mean a form with an error
takes two rows, which breaks the one structural promise the specification makes about the table,
one body row per form, at the moment a script reading the rows needs it. So a form's form-wide
errors, and its hidden fields' errors with them, are drawn in the row's first cell ahead of the
field, in an element whose id is the form's prefix followed by `_errors`, and the row names that
element with `aria-describedby`. The form's hidden fields sit in the same cell.

**Why**: FR-005 and FR-011 together. **Revisit if**: the walkthrough finds the first cell too
narrow to read an error in.

## D11: A formset with no forms draws no table

The specification leaves whether an empty table shows its headings to the build. Headings with no
rows would have to come from `formset.empty_form`, which the pack otherwise never touches, and an
empty table says nothing. The management form, any formset-wide error and the helper's buttons
are still drawn, so the page submits as a valid empty formset.

**Why**: the simplest thing that meets US1.6 in the table. **Revisit if**: django-mvp's row
adding needs the headings on the page before the first row exists (#13).

## D12: A formset's media is drawn once

The single-form template draws `form.media` when the helper asks for it. Included per form that
would repeat every script and stylesheet for every form, so the formset templates draw
`formset.media` once and include each form with media off.

**Why**: the same assets, once. **Revisit if**: never expected.

## D13: A stacked form's container is a bare element

Each stacked form is drawn in a `<div>` of its own with no class, id or attribute, and a daisyUI
`divider` at the head of every one but the first. What a script needs to find a form's container
is the open question in #13, and nothing is promised ahead of its answer.

**Why**: D6. **Revisit if**: #13 settles on a hook.

## D14: A helper layout decides whether a delete or order input is drawn

In the stacked layout a helper layout is applied to each form, and django-crispy-forms draws only
the fields a layout names, plus hidden ones. A laid-out formset therefore shows a delete or order
input only when the layout names `DELETE` or `ORDER`. The pack does not add them back, because
the README makes django-crispy-forms' documented behaviour the rule, and the README says what to
write.

**Why**: matching django-crispy-forms. **Revisit if**: a developer reports the omission as a
surprise.

## D15: Design review, applied

One reviewer read the plan through three lenses and approved it with two medium and three low
findings. None forced a re-plan. Each was applied as an edit to the plan or the tasks:

- The table gets the same form-element test the stacked layout has (FR-016).
- The table's hidden fields and round trip are tested on a model and an inline formset too
  (SC-001).
- The management form is drawn field by field, so damaged management data shows the formset-wide
  error and not Django's own list beside it.
- The single form a formset's field is compared with is built the way Django builds a formset's
  forms, without the `required` attribute.
- The table's rows-and-columns class is written once, in one task.

**ADR:** none — a record of review edits, each already in the plan.

## D16: Additions to shared test files are accepted

The check for changed tests flags `tests/conftest.py` and `tests/test_pack/test_independence.py`
after each story. Every change there is an addition the tasks name: new fixtures, and new
states in the list of forms whose classes are checked. No existing test or assertion was altered.

**ADR:** none — a record of a check's outcome for this feature.
