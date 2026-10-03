# Tasks — 007 Size, colour and variant chosen from Python

**Branch**: `007-size-colour-variant` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing or the order of classes. Elements are found by id, by
name, by type and by role. A class is asserted only where it is the daisyUI modifier this feature
writes, which the testing standard counts as behaviour for a published pack ("Markup that
consumers depend on"). An error is asserted by its type and its attributes, never by its sentence.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, module-level names); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell page only.
Every class the pack writes is a daisyUI class or modifier, written out as a literal string.
Nothing under `mvp_forms/` imports from django-mvp. `.github/` is never touched.

## Decision records

The records named in the plan are written at convergence, after the last story, with numbers read
from `origin/main` at that moment. No task writes them.

## Order

**US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Choose once for every input in a form (P1)

Issue: #36. Delivers FR-001 (inputs), FR-002, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009,
FR-015, FR-016, FR-017, FR-018, FR-019; SC-001, SC-003, SC-004, SC-005.

### T001 — The table of modifiers and the form-wide statement

**Files**: `mvp_forms/choices.py` (new), `tests/test_choices.py` (new),
`tests/test_pack/test_independence.py`

Plan, *`mvp_forms/choices.py`*; research R2, R4, R6.

- `INHERIT`, `InvalidChoice`, `Modifiers` and `FormChoices` as the plan describes them. `Choice`
  is added here as the plain value `Modifiers` resolves against (its three arguments and `over`);
  its drawing in a layout is T003.
- `Modifiers`' tables hold the 100 classes of research R4 as literals.
- Tests, `tests/test_choices.py`: each of the five resolution rules for an input component and
  for `btn`; a component with no modifier for a name; a widget with no component;
  `InvalidChoice`'s `kind`, `value`, `allowed` and `target`; `FormChoices`' lookup from a context,
  from a form's helper and from neither; a value that is not a `FormChoices`.
- Test, `tests/test_pack/test_independence.py`: every class in `Modifiers`' tables is in
  daisyUI's class list.

### T002 — Every input takes the form's choices

**Files**: `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/widgets/clearable_file_input.html`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_choices.py` (new),
`tests/test_pack/test_independence.py`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *`FieldInput`*, *The removal checkbox*; research R1, R5, R7.

- `FieldInput` takes `choices` and `placed`, resolves in `__init__`, and writes the modifiers
  after the component. `daisyui_field` passes them from the context and the field's form.
- `daisyui_removal_checkbox` filter, used by the clearable file input's template.
- Tests, `TestFormWideChoices` in `tests/test_pack/test_choices.py`, one per acceptance scenario
  of US1: a form holding one of every kind of input (text, textarea, select, date selects,
  checkbox, radio group, checkbox group, file, clearable file holding a file, hidden) with a
  size, a colour and a variant; each scenario through the filter and the tag where scenario 6
  says so; a nested layout (scenario 7); hidden inputs unchanged (scenario 8); the same markup
  with nothing stated as with no `FormChoices` at all (scenario 5, SC-005); a field in error
  keeps its error modifier and drops the colour (FR-018); a disabled and a read-only field keep
  their attribute (FR-019); the developer's own classes are kept; every option of a group and
  every select of a date carries the modifier (FR-017); the removal checkbox takes the size and
  the colour; an optional clearable file field that holds a file and is in error, with nothing
  stated, draws its removal checkbox with the class it has today.
- `STATES` in `test_independence.py` gains a form with every choice stated.
- Verification, reported and not committed: render every entry of `STATES` as it stands at the
  task's base commit, before and after the task, and compare the outputs as strings (SC-005).
- README: a section "Size, colour and variant" in the public surface, covering the form-wide
  statement for inputs and the names allowed, and that it is set on the helper instance, with
  the reason. The README and `CONTEXT.md` do not call a daisyUI class family a component.
  CHANGELOG entry. `CONTEXT.md` gains the four terms
  of the spec (size, colour, variant, choice).

---

## US2 — Override the form's choice for one field (P1)

Issue: #37. Delivers FR-010, FR-011, FR-012, FR-014; SC-002.

### T003 — One field states its own choice

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_choices.py`, `tests/test_pack/test_choices.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *`Choice`*, *The precedence, for one field*; research R3.

- `Choice` becomes a layout object: it renders what it holds with itself, merged over any outer
  `Choice`, placed in the context, and removes its own context layer afterwards.
- `daisyui_field` reads the placed `Choice`; `FieldInput` merges it over the by-name `Choice`.
- Tests, `TestFieldChoices`, one per acceptance scenario of US2: a different size on one field;
  one kind overridden and the others inherited; a choice on a form that states none; `None`
  undoing the form's choice; by name under the filter and the tag with no layout; in a layout;
  with `helper["name"].wrap(Choice, ...)`; the developer's widget classes kept; a `Choice` inside
  a `Choice`; a `Choice` holding a `Row`; a field after a `Choice` in the same layout is not
  affected by it; the context holds no placed `Choice` after the layout is drawn.
- README: the per-field statement, both ways, and `None`. The README's example joins
  `test_documented_examples.py`. CHANGELOG entry.

---

## US3 — Buttons take the choices too (P2)

Issue: #38. Delivers FR-001 (buttons), FR-003, FR-013, FR-014 (buttons); SC-002, SC-003.

### T004 — Buttons take the size, and a colour and variant of their own

**Files**: `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/layout/baseinput.html`,
`mvp_forms/templates/daisyui/layout/button.html`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_choices.py`,
`tests/test_pack/test_independence.py`, `README.md`, `CHANGELOG.md`

Plan, *Buttons*; research R1, R2.

- `DrawnButton` and the `daisyui_button` tag; the two templates read it.
- Tests, `TestButtonChoices`, one per acceptance scenario of US3, each for `Submit`, `Reset`,
  `Button` and `StrictButton`: the form's size; `button_color` and `button_variant` reach buttons
  and not inputs; `color` and `variant` reach inputs and not buttons; a `Choice` around one
  button; a button added to the helper takes the form's choices; the same markup as before with
  nothing stated; a `Hidden` is unchanged; the developer's `css_class`, `css_id` and attributes
  are kept on each kind, including an attribute whose name ends in `class`
  (`data_class="x"`); a `Submit` under `button_color` carries the chosen colour and not the
  default `btn-primary`, and one given `css_class="btn-primary"` keeps it; a page whose form is
  not named `form` in the context.
- Verification, reported and not committed: the same before-and-after comparison of `STATES` as
  T002.
- `STATES` gains a buttoned form with choices.
- README: buttons in the "Size, colour and variant" section. CHANGELOG entry.

---

## US4 — A wrong choice is reported, an inapplicable one is passed over (P2)

Issue: #39. Delivers FR-020, FR-021, FR-022; SC-006.

### T005 — Mistakes are reported where the form is drawn

**Files**: `mvp_forms/choices.py`, `mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_choices.py`, `tests/test_pack/test_choices.py`, `README.md`, `CHANGELOG.md`

Plan, *`InvalidChoice`*, *`Modifiers`* rules 3 and 4; research R6.

- Tests, `TestMistakes`, one per acceptance scenario of US4, drawn through the filter and the
  tag: an unknown size, colour and variant for the form, for inputs and for buttons, each raising
  `InvalidChoice` with its `kind`, `value` and `allowed`; the same on one field by name, on one
  field in a layout and on one button, each with `target`; a form-wide variant passed over for a
  checkbox, a radio group and a checkbox group with no error; the same variant on one checkbox
  raising; a choice on a field whose widget the pack does not cover raising; the error is raised
  when the frame is the template that draws the field (not swallowed by `{% if %}`); a
  `helper.daisyui` that is not a `FormChoices` raising `TypeError` when a form is drawn (T001
  holds the unit case); a page variable named `daisyui` that is not a `FormChoices` is ignored.
- Close whatever those tests find. The resolution rules were built in T001 to T004; this task is
  where each is proved through a drawn form and where `target` is proved for every way of
  stating.
- README: what is refused and what is passed over. CHANGELOG entry.

---

## US5 — See the combinations in the demo project (P3)

Issue: #40. Delivers FR-023, FR-024; SC-007.

### T006 — The demo page and the README's list

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/templates/demo/choices.html` (new), `demo/templates/demo/choices_standalone.html` (new),
`demo/templates/demo/overview.html`, `tests/test_demo.py`, `README.md`, `CHANGELOG.md`

Plan, *The demo project*.

- The page in the shell and standalone, its route, its menu entry, and the forms generated from
  `Modifiers`' tables.
- Tests, `TestChoicesPage` and `TestStandaloneChoicesPage` on a shared contract, as the existing
  pairs are: both respond; the sidebar links the shell page; each page links the other; every
  size, colour and input variant in the table is on at least one input; every size, colour and
  button variant on at least one button; the override form holds a field and a button whose
  modifiers differ from the form's; no id repeats; the standalone page carries daisyUI's CDN
  stylesheet and none of the shell's.
- README: the contributing section names the new pages; the public surface lists every allowed
  name for inputs and for buttons (FR-024). CHANGELOG entry for the demo page.
