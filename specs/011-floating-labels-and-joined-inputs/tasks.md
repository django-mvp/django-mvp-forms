# Tasks — 011 Floating labels and joined inputs

**Branch**: `011-floating-labels-and-joined-inputs` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, the order of classes or where a label sits on the page.
Elements are found by id, by name, by type, by role and by `for`. A class is asserted only where
it is the daisyUI component this feature writes (`floating-label`, `join`, `join-item`) or a
modifier FS-007 resolves. An error is asserted by its type and its attributes, never by its
sentence.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, module-level names); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates, `{% include %}` of the pack's own templates is expected there, and
django-cotton never appears in anything under `mvp_forms/`. Cotton components are for the demo
project's shell pages only, never `{% include %}` partials there. Every class the pack writes is
a daisyUI class or modifier, written out as a literal string, or a layout utility named in
`LAYOUT_UTILITIES`. Nothing under `mvp_forms/` imports from django-mvp. `.github/` is never
touched. Documents read as current state: no dated notes and no "amended" stamps.

## Decision records

The records named in the plan are written at convergence, after the last story, with numbers read
from `origin/main` at that moment. No task writes them.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A developer gives a field a floating label (P1)

Issue: #112. Delivers FR-001 to FR-011 (FR-010 for attached text, joined buttons and inline
fields; the joined-group case lands with US2), FR-024 to FR-029 for the floating label; SC-001,
SC-003, SC-004, SC-005, SC-006, SC-008.

### T001 — A floating label is stated with `Choice` and `FormChoices` and resolved for one field

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/test_choices.py`,
`tests/test_templatetags/test_daisyui.py`

Plan, *The floating label › `mvp_forms/choices.py`*, *`FieldInput`*, *Buttons*; research R1, R3,
R4.

- `Modifiers.labels`, `Choice(label=...)` and its merge in `over`, `FormChoices(label=...)` and
  its check.
- `FieldInput.resolve_label`, `can_float`, `floats`, `is_floating`, `is_disabled`, and the
  second case of `requires_placeholder`, as the plan describes them.
- `DrawnButton.resolve_modifiers` refuses a label.
- Tests, `tests/test_choices.py`: a `Choice` holds a label; an inner one wins over an outer one;
  `INHERIT` takes the outer one; `None` undoes it; `FormChoices(label="floating")` passes its
  check and an unknown name raises `InvalidChoice` with `kind="label"`, the value and the names
  allowed.
- Tests, `tests/test_templatetags/test_daisyui.py`, a `TestFieldInputLabel` class: the form's
  statement floats an input, a textarea and a select; it passes over a checkbox, a radio group,
  a checkbox group, a file input, a multi-widget field, a date drawn as three selects, a field
  with attached text, a field with joined buttons and an inline field, raising nothing; the
  same statement as the field's own, in a layout and by name, raises `InvalidChoice` with
  `kind="label"`, nothing allowed and the field as `target` for each of those; an unknown name
  raises with `floating` allowed; the field's `None` undoes the form's; a disabled field (by the
  form field, by the option and by the widget's attribute) is not floating and raises nothing; a
  read-only field floats; with labels off nothing floats and the input has its `aria-label`; a
  field with no label does not float; the placeholder is the label's text only when the widget
  has none and the field floats, and a select gets none; a hidden field takes nothing and raises
  nothing.
- Tests, beside `TestDrawnButtonDrawing`: a label stated around a button raises `InvalidChoice`
  with `kind="label"`, nothing allowed and the button as `target`; `None` and `INHERIT` do not.
- The docstrings of `FieldInput`, `daisyui_field`, `DrawnButton`, `Choice`, `FormChoices` and
  `InvalidChoice` name the label where it now applies.

### T002 — Forms drawn through the pack, and the public surface

**Files**: `mvp_forms/templates/daisyui/frame.html`,
`mvp_forms/templates/daisyui/field_body.html`, `tests/forms.py`,
`tests/test_pack/test_floating_labels.py` (new), `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *The floating label › The templates*, *Documentation*.

- The frame and the body as the plan has them.
- Tests, `TestFloatingLabels`, one per acceptance scenario of US-1: a form that states nothing
  has no `floating-label` element (1); a stated field has one `<label class="floating-label">`
  that holds the input, whose `for` is the input's id, and no other label for that input (2, 3);
  the form's statement floats the input, the textarea and the select and leaves the checkbox as
  it is without it (4); a field that undoes it has its ordinary label (5); the statement for the
  form and for one field by name takes effect through `{{ form|crispy }}` (6); an empty field
  with no placeholder carries the label's text as its placeholder (7), found by comparing with
  the field's label and not by a string in the test; a developer's placeholder is kept (8); a
  required field with help text in a failing bound form has the required marker inside the
  floating label, the help text and the error element with their ids, `aria-invalid`, and a
  description naming both (9); a disabled field is disabled and has its ordinary label (10);
  with the helper's labels off no label is drawn and the input has its `aria-label` (11); every
  form of a formset drawn stacked floats the field (12).
- Tests, `TestFloatingLabelKeepsTheData`: a form posted from its drawn inputs cleans to the same
  data with and without the statement (FR-009, SC-004).
- Tests, `TestFloatingLabelMistakes`: each case of FR-011 raises when the form is drawn, by the
  tag and by the filter; a formset drawn as a table with the form's statement draws no
  `floating-label` and raises nothing.
- Tests, `TestFloatingLabelEscaping`: a label holding markup is escaped inside the floating
  label and in the placeholder.
- `STATES` in `test_independence.py` gains a floating form, plain and in error.
  `TestModifierTables` checks `Modifiers.labels` against the class list.
- Verification, reported and not committed: render every entry of `STATES` as it stands at the
  base commit before T001 and after this task, and compare (SC-003).
- README: the section "Floating labels" with an example that `test_documented_examples.py`
  draws; what takes one, what the form's statement passes over, the disabled fallback, the
  placeholder rule, and that the label's text follows the size of an input only (research R1);
  "What is refused and what is passed over" names the `label` kind; the rows of
  `daisyui/frame.html` and `daisyui/field_body.html` in the template list gain
  `drawn.is_floating`. CHANGELOG, under Added. CONTEXT: **Floating label**; **Choice** names
  the label as a fifth kind.

### T003 — The demo pages for floating labels

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py`, `demo/templates/demo/floating_labels.html` (new),
`demo/templates/demo/floating_labels_standalone.html` (new), `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

Plan, *The demo project*.

- `/floating-labels/` in the shell, with its sidebar entry and icon, and
  `/floating-labels/standalone/` on daisyUI's CDN install alone. Both hold: a form to submit with
  an input, a textarea, a select, a field that opts out and a checkbox; a form that already
  fails, with a required field and help text; a disabled and a read-only field; a form drawn
  with no layout that floats one field by name. No size or colour is stated; T007 adds those.
- Tests: each page answers, the shell page is in the sidebar, the standalone page carries the
  CDN install and no shell, the floating fields are drawn floating and the others are not, and
  a post comes back with its cleaned values or its errors.
- README's page list and the CHANGELOG name the two pages.

---

## US2 — A developer joins several fields into one group (P2)

Issue: #113. Delivers FR-012 to FR-021, the joined-group case of FR-010 and FR-011, FR-024 to
FR-029 for the joined group; SC-002, SC-003, SC-004, SC-005, SC-008.

### T004 — `Join`, its members and its templates

**Files**: `mvp_forms/layout.py` (new), `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/layout/join.html` (new),
`mvp_forms/templates/daisyui/layout/join_member.html` (new),
`mvp_forms/templates/daisyui/field_messages.html` (new),
`mvp_forms/templates/daisyui/field_body.html`, `tests/test_layout.py` (new),
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`, `README.md`

Plan, *The joined group*; research R2, R5, R6.

- `InvalidMember`, `Join`, `Join.members`, `Join.render` as the plan describes them.
- `FieldInput`'s `member` option: the check that raises `InvalidMember`, `show_labels` off,
  `join-item`, `member_widths`, and `can_float` false.
- The three templates, and `field_body.html` including `daisyui/field_messages.html` for the
  help text and errors it drew inline.
- `LAYOUT_UTILITIES` gains `w-auto`.
- The README's template list gains the three rows, and `field_body.html`'s row loses nothing it
  still reads. The list test fails until it does, so it lands in this task.
- Tests, `tests/test_layout.py`: `TestJoinMembers` — names, a `Field` holding one and several
  names with its attributes, a `Choice` holding names and a `Field`, a `Choice` inside a
  `Choice` merged, the order kept; a `Div`, a `PrependedText`, an `InlineField` and a button
  each raise `InvalidMember` with the class name as `member`. `TestJoinRender` — a group that
  holds nothing draws nothing; a group of hidden members draws their inputs and no fieldset;
  each member is recorded in `form.rendered_fields`.
- Tests, `tests/test_templatetags/test_daisyui.py`, a `TestFieldInputMember` class: an input and
  a select are accepted; a textarea, a checkbox, a radio group, a file input, a multi-widget
  field, a date drawn as three selects and a widget the pack has no component for each raise
  `InvalidMember` with the field's name; a hidden field raises nothing; the member carries
  `join-item`; a floating label stated on a member raises `InvalidChoice` and the form's passes
  it over.

### T005 — Joined groups drawn through the pack, and the public surface

**Files**: `tests/forms.py`, `tests/test_pack/test_joined_groups.py` (new),
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`, `CONTEXT.md`

- Tests, `TestJoinedGroups`, one per acceptance scenario of US-2: the inputs are the direct
  children of one element carrying `join`, in the layout's order, each carrying `join-item` (1);
  the group is a `<fieldset>` whose `<legend>` holds the group's label, and no `<label>` for a
  member is drawn (2); each input's `aria-label` is its own field's label, and one the developer
  wrote on the widget is kept (3); a member's help text is drawn once, inside the fieldset, and
  only that member's input describes itself by its id (4); in a failing bound form only the
  failing member is `aria-invalid`, and its error element is drawn once and named by that
  input's description (5); a group holding a required member has the required marker in its
  legend and the required input is exposed as required (6); a form posted from its drawn inputs
  cleans to the same data joined and not joined, valid and invalid (7, SC-004); a disabled
  member is disabled in its place, a read-only member keeps its attribute, and a hidden member
  is a hidden input outside the join element (8); a checkbox and a textarea each raise
  `InvalidMember` naming the field when the form is drawn (9); a class, an id and an attribute
  of the developer's are on the join element and a class written for another pack is dropped
  (10); every form of a formset drawn stacked draws the group (11).
- Tests, `TestJoinedGroupEdges`: a group with no label draws no legend and each input still has
  its `aria-label`; a group of one is drawn; with the helper's labels off no legend is drawn and
  the fieldset has an `aria-label`; a `Field` passes its attribute and its class to its member's
  input; a `Choice` around a member reaches that member; a layout object other than those raises
  `InvalidMember` when the form is drawn; a formset drawn as a table draws no join and raises
  nothing; the group's label holding markup is escaped.
- `STATES` in `test_independence.py` gains a joined form, plain and in error.
- Verification, reported and not committed: `STATES` as they stood before T004 are unchanged
  (SC-003).
- README: the section "Joined groups" with an example that `test_documented_examples.py` draws;
  what a group may hold and what raises; the one label, the members' names, help text and
  errors; that a hidden member sits outside the join; that a `Field`'s `wrapper_class` and
  `template` are not used in a group; how the width is shared and that a member's own width is
  kept; that a floating label never applies to a member. "What is refused and what is passed
  over" gains `InvalidMember`. CHANGELOG, under Added. CONTEXT: **Joined group** and **Member**.

### T006 — The demo pages for joined groups

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py`, `demo/templates/demo/joined_groups.html` (new),
`demo/templates/demo/joined_groups_standalone.html` (new), `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

- `/joined-groups/` in the shell, with its sidebar entry and icon, and
  `/joined-groups/standalone/` on daisyUI's CDN install alone. Both hold: a country code and a
  number under one label, to submit; a group that already fails in one member; a group with help
  text on a member; a group with a disabled member and a hidden member; a group with no label; a
  group of one. No size or colour is stated; T007 adds those.
- Tests: as T003's, for these pages, with a post that fails in one member and one that is valid.
- README's page list and the CHANGELOG name the two pages.

---

## US3 — Floating labels and joined groups take the form's choices (P3)

Issue: #114. Delivers FR-022, FR-023, FR-024, FR-028; SC-007.

### T007 — Size, colour and variant on both, shown and proven

**Files**: `tests/test_pack/test_floating_labels.py`, `tests/test_pack/test_joined_groups.py`,
`tests/test_pack/test_independence.py`, `tests/test_demo.py`, `demo/forms.py`, `demo/views.py`,
`demo/templates/demo/floating_labels.html`,
`demo/templates/demo/floating_labels_standalone.html`,
`demo/templates/demo/joined_groups.html`, `demo/templates/demo/joined_groups_standalone.html`,
`README.md`, `CHANGELOG.md`

- Tests, `TestFloatingLabelChoices`: a floating input, textarea and select each take the form's
  size, colour and variant, as the same field does without the floating label (1); a field's own
  choice wins over the form's (2).
- Tests, `TestJoinedGroupChoices`: every member takes the form's size (3); a `Choice` around the
  group wins over the form's for every member, and a member's own wins over that (4); with a
  colour in force and one member in error, that member carries its error modifier and no colour
  modifier and the others keep the colour (5).
- `STATES` gains a floating form and a joined form at every size, colour and variant FS-007
  offers, built from the tables of `Modifiers`, so the class test covers each (6, SC-007).
- Any change this needs under `mvp_forms/` is a defect in US1 or US2 and is fixed here,
  test-first, and named in the report.
- Demo: the floating-labels pages gain a form at each size, a form at each colour and one in the
  variant; the joined-groups pages gain a group at each size, a coloured group with one member
  in error, and a `Choice` around a group.
- README: each of the two sections says size, colour and variant apply as on any field, and in
  which order for a member. CHANGELOG, in the entries of the two features.
