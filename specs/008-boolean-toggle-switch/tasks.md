# Tasks — 008 Booleans drawn as a checkbox, toggle or switch

**Branch**: `008-boolean-toggle-switch` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

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
plain Django templates and django-cotton never appears in anything under `mvp_forms/`. Cotton
components are for the demo project's shell page only, never `{% include %}` partials there.
Every class the pack writes is a daisyUI class or modifier, written out as a literal string.
Nothing under `mvp_forms/` imports from django-mvp. `.github/` is never touched.

## Decision records

The records named in the plan are written at convergence, after the last story, with numbers read
from `origin/main` at that moment. No task writes them.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A developer chooses how a boolean field is drawn (P1)

Issue: #28. Delivers FR-001 to FR-008, FR-010, FR-012, FR-013, FR-014, FR-016, FR-017; SC-001,
SC-002, SC-003, SC-006.

### T001 — A drawing is stated with `Choice` and resolved for one field

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/test_choices.py`,
`tests/test_templatetags/test_daisyui.py`

Plan, *`mvp_forms/choices.py`*, *`FieldInput`*; research R2, R3, R4, R5.

- `Choice(drawing=...)` and its merge in `over`. `Modifiers.drawings`.
- `DrawnButton.resolve_modifiers` refuses a drawing (plan, *Buttons*).
- `FieldInput.own_choice`, `resolve_drawing`, `component`, `is_single_checkbox`, `fixed_size`,
  `error_modifiers` and `attrs` as the plan describes them.
- Tests, `tests/test_choices.py`: a `Choice` holds a drawing; an inner drawing wins over an outer
  one; `INHERIT` takes the outer one; `None` undoes it.
- Tests, `tests/test_templatetags/test_daisyui.py`, a `TestFieldInputDrawing` class: the
  component for each drawing, stated in a layout and by name, and with the layout's winning; the
  role of a switch and no role on a toggle or a checkbox; an unknown name raises `InvalidChoice`
  with `kind`, `value`, `allowed` and `target`; any drawing on a text field, a checkbox group and
  a null-boolean field raises with nothing allowed, `checkbox` included; an unknown name on a
  text field raises with nothing allowed; a list given as the name raises `InvalidChoice` and
  not `TypeError`; a subclass of `CheckboxInput` takes a
  drawing; a field in error drawn as a toggle does not raise.
- Tests, in `TestDrawnButton`'s file beside it, a `TestDrawnButtonDrawing` class: a drawing
  stated around a button raises `InvalidChoice` with `kind="drawing"`, nothing allowed and the
  button as `target`; `None` and `INHERIT` do not; a hidden input does not.
- The docstrings of `FieldInput`, `daisyui_field`, `DrawnButton` and `Choice` that list size,
  colour and variant name the drawing where it now applies.

### T002 — Forms drawn through the pack, and the public surface

**Files**: `tests/forms.py`, `tests/test_pack/test_drawings.py` (new),
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`, `CONTEXT.md`

- Tests, `TestDrawings` in `tests/test_pack/test_drawings.py`, one per acceptance scenario of
  US1: no drawing stated is the checkbox FS-002 draws (1); a toggle has the toggle component and
  no role (2); a switch has it and the switch role (3); a form posted with a toggle on and a
  switch off cleans to `True` and `False`, the same as checkboxes, with the posted data built
  from the drawn inputs (each one's `name`, and its `value` attribute when it has one) and not
  from a dict written by hand (4, SC-002); a bound `True` is
  drawn checked in each drawing (5, FR-010); the input is a checkbox input with the field's name
  and no script is drawn with it (6, FR-008); only the field stated changes (7); every row of a
  formset draws the field as stated on the helper (8). Each through `{{ form|crispy }}` and
  `{% crispy form %}` where both apply.
- Tests, `TestDrawingMistakes`: the two cases of FR-012 raise when the form is drawn, by either
  path; `checkbox` stated on a boolean field is accepted; a hidden boolean field with a drawing
  stated raises nothing and is a hidden input.
- `STATES` in `test_independence.py` gains a form with a toggle and a switch, plain and in error.
- Verification, reported and not committed: render every entry of `STATES` as it stands at the
  base commit before T001 and after this task, and compare (SC-003).
- README: a section under the public surface naming the three drawings and how one is chosen,
  with an example that `test_documented_examples.py` draws; the example states a drawing only,
  with no size or colour on a toggle or a switch, which T005 adds; the sentence in *One field's
  own choice* that counts three kinds; the kinds `InvalidChoice` carries in
  *What is refused and what is passed over*. CHANGELOG, under Added. CONTEXT: add
  **Drawing** and **Boolean field**; amend **Choice** to name the drawing as a fourth kind;
  reword **Variant** so that it is not defined with the word drawing.

### T003 — The demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py`, `demo/templates/demo/drawings.html` (new),
`demo/templates/demo/drawings_standalone.html` (new), `tests/test_demo.py`

Plan, *The demo project*.

- The page in the shell and standalone, with the sidebar entry and its icon, holding the US1
  form: three boolean fields drawn three ways, which posts and shows what it cleaned to. No size
  or colour is stated on it; T005 adds those sections.
- Tests, a `DrawingsPageContract` with a class for each form of the page: it answers, the shell
  page is in the sidebar, the three drawings are each drawn, and a post with fields on and off
  shows the cleaned values.

---

## US2 — A toggle or switch keeps everything a checkbox has (P2)

Issue: #29. Delivers FR-009, FR-015, FR-016; SC-004.

### T004 — Label, help text, errors, required and disabled, in every drawing

**Files**: `tests/forms.py`, `tests/test_pack/test_drawings.py`, `tests/test_demo.py`,
`demo/forms.py`, `demo/views.py`, `demo/templates/demo/drawings.html`,
`demo/templates/demo/drawings_standalone.html`, `README.md`

- Tests, `TestDrawingKeepsWhatACheckboxHas`, each run for a toggle and for a switch beside the
  checkbox: the label's `for` is the input's id (1); the input is described by the help text's
  id (2); a required field left off is `aria-invalid`, carries the component's error modifier and
  is described by the error element (3); the required marker is in the label (4); a disabled
  field's input is `disabled` (5). The same holds with labels off, where the input is named by
  `aria-label`.
- These hold on arrival if T001 is right, so each is proven by a probe: break the code it
  guards, see it fail, restore it. Report the probes. Anything a probe shows missing is fixed
  here, in `FieldInput`.
- FR-015: the pack adds no text for either drawing, so nothing is translated and no test is
  written. Say so in the report.
- The demo page gains each drawing in each state: off, on, with help text, required and in
  error, disabled. `tests/test_demo.py` finds each state in each drawing.
- README: one sentence in the new section saying what a toggle and a switch keep.

---

## US3 — A boolean field takes the form's size and colour (P3)

Issue: #30. Delivers FR-006, FR-011, FR-013, FR-016; SC-005.

### T005 — Size and colour reach a toggle and a switch

**Files**: `mvp_forms/choices.py`, `tests/test_choices.py`, `tests/forms.py`,
`tests/test_pack/test_drawings.py`, `tests/test_pack/test_independence.py`, `tests/test_demo.py`,
`demo/forms.py`, `demo/views.py`, `demo/templates/demo/drawings.html`,
`demo/templates/demo/drawings_standalone.html`, `README.md`, `CHANGELOG.md`

Plan, *`mvp_forms/choices.py`*; research R6.

- The `toggle` rows of `Modifiers.sizes` and `Modifiers.colors`, as literals.
- Tests, `tests/test_choices.py`: every size and colour resolves for `toggle`; a variant stated
  for the form is passed over and one stated on the field raises.
- Tests, `TestDrawingSizeAndColour`, one per acceptance scenario of US3, for a toggle and a
  switch: the form's size (1); the form's colour (2); the field's own wins (3); a drawing, a size
  and a colour stated together on one field (4); nothing stated writes no modifier (5); every
  size and colour, each class checked against daisyUI's list by `TestModifierTables` (6); a field in error
  keeps the error modifier and drops the colour.
- `STATES` gains a toggle and a switch with a size and a colour.
- The demo page gains each drawing at every size and in every colour, generated from
  `Modifiers`, and one field overriding the form's size and colour. `tests/test_demo.py` finds
  them.
- README: the section says a drawing takes the size and colour like any input and has no
  variant. CHANGELOG entry extended.
