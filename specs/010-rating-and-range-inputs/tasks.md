# Tasks — 010 Rating and range inputs

**Branch**: `010-rating-and-range-inputs` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, the order of classes or where a label sits. Elements are
found by id, by name, by type and by role. A class is asserted only where it is the daisyUI
component or modifier this feature writes. An error is asserted by its type and its attributes,
never by its sentence.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, module-level names); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates and django-cotton never appears in anything under `mvp_forms/`;
`{% include %}` is fine there. Cotton components are for the demo project's shell page only,
never `{% include %}` partials there. Every class the pack writes is a daisyUI class or modifier,
written out as a literal string. Nothing under `mvp_forms/` imports from django-mvp. `.github/`
is never touched. A document reads as current state: no dated notes and no "amended" stamps in
README, CHANGELOG or CONTEXT.

## Decision records

The records named in the plan are written at convergence, after the last story, with numbers read
from `origin/main` at that moment. No task writes them.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A developer draws a choice field as a rating (P1)

Issue: #105. Delivers FR-001 to FR-004, FR-006 to FR-011, FR-016, FR-017, FR-021 to FR-026;
SC-001 to SC-004, SC-006.

### T001 — A field's own drawings, and a rating drawn for one field

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/widgets/rating.html` (new), `demo/views.py`,
`tests/test_choices.py`, `tests/test_templatetags/test_daisyui.py`

Plan, *`mvp_forms/choices.py`*, *`FieldInput`: which drawings a field takes*, *`FieldInput`: a
rating*, *`daisyui/widgets/rating.html`*; research R2, R4, R7.

- `Modifiers.drawings` gains `rating`. `FieldInput.drawings_of` and the one rule in
  `resolve_drawing`. `is_group` and the three properties that ask it. The widget a rating is
  drawn through, its wrapped context, the template, and `error_modifiers["rating"]`.
- `DrawingsMixin.drawing_names` in `demo/views.py` stops reading the whole of
  `Modifiers.drawings` and names the three drawings a boolean field takes (plan, *The existing
  drawings demo page*). No new test: the drawings contract in `tests/test_demo.py` is the guard.
- Tests, `tests/test_choices.py`: `rating` is in the drawings table with its component. This
  extends one existing test, `TestModifiersDrawings.test_each_drawing_names_the_component_it_is_drawn_with`,
  which pins the table to its exact rows: the table gains a row, so the expected table gains
  the same row. Nothing else in an existing test changes. Say so in the report.
- Tests, in `TestFieldInputRating`: a choice label marked safe that holds a tag and a double
  quote is written into `aria-label` as plain text, with the quote escaped.
- Tests, `tests/test_templatetags/test_daisyui.py`, a `TestFieldInputRating` class: a select and
  a radio group each take `rating` and nothing else; the component is `rating` and the field is
  a group; stated in a layout and by name, the layout's winning; a multiple select, a checkbox
  group, a null-boolean select, a text input and a boolean field refuse `rating`, each with its
  own drawings as `allowed`; a boolean field's drawing on a select is refused with `rating`
  allowed; a select and a radio group that name a template of their own refuse `rating` with
  nothing allowed; an unknown name on a select has `rating` allowed; a list given as the name
  raises `InvalidChoice` and not `TypeError`; a hidden select with `rating` stated raises
  nothing; the form's own widget is the same object, with the same attributes and template
  name, after a draw.
- The docstrings of `FieldInput`, `daisyui_field`, `Choice` and `InvalidChoice` say which field
  takes which drawing.

### T002 — Forms drawn as a rating through the pack, and the public surface

**Files**: `tests/forms.py`, `tests/test_pack/test_rating.py` (new),
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`, `CONTEXT.md`

- Tests, `TestRating`, one per acceptance scenario of US1, through `{{ form|crispy }}` and
  `{% crispy form %}` where both apply: no drawing stated is the select or radio group it was
  (1); a rating is one radio input for each choice with a value, in order, sharing the field's
  name, inside an element with the class `rating` (2), and a field whose first choice has the
  value `0` draws that choice as a star; a form posted with a star picked cleans
  to that choice's value, the same as the same form with no drawing stated, with the posted
  data built from the drawn inputs and not from a dict written by hand (3, SC-002); a bound and
  an initial value are drawn checked (4); with no value no star is checked (5); the empty choice
  is one input with `rating-hidden`, is not a star, and submitting it cleans to the field's
  empty value (6), and a field whose empty choice is its last choice draws the clearing input
  before every star; choices in named groups are stars in order and no group name is drawn
  (FR-010); a field with no choices is drawn with its frame and no input; a model choice field
  is drawn with its empty label as the clearing input.
- Tests, `TestRatingKeepsWhatARadioGroupHas`: the stars are in a fieldset whose legend is the
  field's label, and each star has an `aria-label` equal to its choice's label (7); help text
  and errors are drawn and the fieldset is described by both ids, each star of a required
  rating left empty is `aria-invalid`, and the legend holds the required marker a radio group's
  holds (8); every star of a disabled field is `disabled` (9); no script is drawn (10); with
  labels off the fieldset is named by `aria-label` and each star keeps its own; a select and a
  radio group with the same choices are drawn as the same inputs; a class and an attribute the
  developer set on the widget are on every input of the rating, the clearing input included
  (FR-017); the form drawn twice gives the same
  markup.
- Tests, `TestRatingAmongOtherFields`: only the field stated changes (11); every form of a
  formset draws the field as a rating, in the stacked layout and in the table, and no id and no
  group name repeats across forms (12); inside `Row`, `Fieldset`, `Tab` and `AccordionGroup` it
  is drawn as it is outside; `PrependedText` and `InlineRadios` around it draw the rating.
- Tests, `TestRatingMistakes`: each case of FR-021 that concerns a rating raises when the form
  is drawn, by either path, with the field as `target`; a hidden field raises nothing and is a
  hidden input. `README.md` and `CONTEXT.md` are searched for every sentence that says only a
  boolean field takes a drawing, or that any other field allows nothing, and each is made true.
- `STATES` in `test_independence.py` gains a form with a rating, plain and in error.
- Verification, reported and not committed: render every entry of `STATES` as it stands at the
  base commit before T001 and after this task, and compare (SC-003).
- README: a section under the public surface, "Rating and range", naming the rating, which
  fields take it and how it is stated, what the empty choice is, and what a rating keeps, with
  an example that `test_documented_examples.py` draws; the example states a drawing only. The
  sentences in the README that say only a boolean field takes a drawing are made true.
  CHANGELOG, under Added. CONTEXT: **Drawing** covers the rating; add **Single-choice field**
  and **Rating**; amend **Choice** and **Boolean field** where they say only a boolean field
  takes a drawing.

### T003 — The demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py`, `demo/templates/demo/rating_and_range.html` (new),
`demo/templates/demo/rating_and_range_standalone.html` (new), `tests/test_demo.py`

Plan, *The demo project*.

- The page in the shell and standalone, with the sidebar entry and its icon, holding the US1
  forms: a required rating and an optional one, which post and show what they cleaned to; a
  rating with help text, in error and disabled. No size or colour is stated; T005 adds those.
- Tests, a `RatingAndRangePageContract` with a class for each form of the page: it answers, the
  shell page is in the sidebar, each state is drawn as a rating, and a post with a star picked
  shows the cleaned value.

---

## US2 — A developer draws a number field as a range (P2)

Issue: #106. Delivers FR-001 to FR-003, FR-005, FR-012 to FR-017, FR-021 to FR-026; SC-001 to
SC-004, SC-006.

### T004 — A range drawn, kept whole, documented and shown

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/test_choices.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/forms.py`, `tests/test_pack/test_range.py`
(new), `tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`tests/test_demo.py`, `demo/forms.py`, `demo/views.py`,
`demo/templates/demo/rating_and_range.html`,
`demo/templates/demo/rating_and_range_standalone.html`, `README.md`, `CHANGELOG.md`,
`CONTEXT.md`

Plan, *`FieldInput`: a range*; research R3, R5.

- `Modifiers.drawings` gains `range`, and the one existing test that pins the table,
  `TestModifiersDrawings.test_each_drawing_names_the_component_it_is_drawn_with`, gains the same
  row. `drawings_of` gives a number input `range`. The widget a
  range is drawn through. `error_modifiers["range"]`.
- Tests, `TestFieldInputRange`: an integer, a float and a decimal field's number input take
  `range` and nothing else; a subclass of `NumberInput` takes it; a text input, a select, a
  boolean field and a localised integer and a localised decimal field refuse it with their own drawings as `allowed`; a
  boolean field's drawing and `rating` on a number input are refused with `range` allowed; a
  hidden number field raises nothing; the form's own widget keeps its `input_type` after a
  draw.
- Tests, `TestRange` in `tests/test_pack/test_range.py`, one per acceptance scenario of US2: no
  drawing stated is the number input it was (1); a range is one `input` of type `range` with
  the field's name and the class `range` (2); `min`, `max` and `step` are the field's (3), and
  an integer field that declares none has none written; a form posted with the slider's value cleans to
  the number, the same as the same form with no drawing stated, for a value inside the limits
  and one outside them (4, SC-002); a bound and an initial value are the input's `value` (5);
  the label's `for` is the input's id (6); help text and errors are drawn and the input is
  described by both, is `aria-invalid`, carries `range-error`, and a required field has the
  required marker (7); a disabled field's input is `disabled` (8); no script is drawn (9);
  attributes and classes the developer set on the widget are kept, and a width among them
  leaves the pack's width out (10, FR-015); with labels off the input is named by `aria-label`;
  the form drawn twice gives the same markup; every form of a formset draws it with an id of
  its own; `PrependedText` around a range draws the range with no attached text.
- Tests, `TestRangeMistakes`: each case of FR-021 that concerns a range raises when the form is
  drawn, by either path, with the field as `target`; a hidden field raises nothing.
- `STATES` gains a form with a range, plain and in error. The SC-003 comparison is run again
  and reported.
- The demo page gains a range with limits and a step in the form that posts, and a range with
  help text, in error and disabled. `tests/test_demo.py` finds each and posts a value.
- README: the section gains the range: which fields take it, where its limits come from, what
  it keeps, and that a slider always submits a number, so an optional number field drawn as a
  range is never submitted empty, and an extra form of a formset that holds a range is always
  submitted as changed. The example gains a range. CHANGELOG entry extended. CONTEXT:
  **Drawing** covers the range; add **Number field** and **Range**.

---

## US3 — A rating and a range take the form's size and colour (P3)

Issue: #108. Delivers FR-018 to FR-022, FR-025, FR-026; SC-005, SC-006.

### T005 — Size and colour reach a rating and a range

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/test_choices.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/forms.py`, `tests/test_pack/test_rating.py`,
`tests/test_pack/test_range.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `tests/test_demo.py`, `demo/forms.py`,
`demo/views.py`, `demo/templates/demo/rating_and_range.html`,
`demo/templates/demo/rating_and_range_standalone.html`, `README.md`, `CHANGELOG.md`

Plan, *`mvp_forms/choices.py`*, *Size and colour*; research R6.

- The `rating` and `range` rows of `Modifiers.sizes` and `Modifiers.colors`, as literals. A
  rating's size on its wrapper and its colour on each star.
- Tests, `tests/test_choices.py`: every size and colour resolves for `rating` and for `range`;
  a variant stated for the form is passed over and one stated on the field raises.
- Tests, `TestRatingSizeAndColour` and `TestRangeSizeAndColour`, one per acceptance scenario of
  US3: the form's size (1); the form's colour (2); the field's own wins, stated by name and in
  a layout (3); a drawing, a size and a colour stated together on one field (4); nothing stated
  writes no size and no colour (5); a form's variant is passed over (6); a variant on the field
  raises naming it (7); a field in error drops the colour, keeps the size and carries the error
  class (8); every size and colour is written as its class, each checked against daisyUI's list
  by `TestModifierTables` (10). For a rating the size is on the element with the class `rating`
  and the colour on every star and never on the clearing input.
- Tests, `TestDrawingMistakes` in `tests/test_pack/test_drawings.py` gains nothing: scenario 9
  is covered by `TestRatingMistakes` and `TestRangeMistakes`. Confirm each case of FR-021 has a
  test and name them in the report.
- `STATES` gains a rating and a range with a size and a colour, plain and in error.
- The demo page gains a rating and a range at every size and in every colour, generated from
  `Modifiers`, and one form whose fields override the form's size and colour.
  `tests/test_demo.py` finds them.
- README: the section says a rating and a range take the size and colour like any input and
  have no variant, where a rating's colour is written, and what a field in error keeps. The
  example gains a size and a colour. CHANGELOG entry extended.
