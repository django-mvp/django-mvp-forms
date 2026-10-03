# Tasks — 003 Layout objects for structure and buttons

**Branch**: `003-structure-and-button-layout-objects` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a layout object lands in the task
that adds it.

No test asserts wording, width, spacing, alignment or which utility arranges a row. Elements are
found by id, by name, by role and by element type. A class is asserted only where it is a daisyUI
component (`btn`, `fieldset`, `fieldset-legend`), which the testing standard counts as behaviour
for a published pack ("Markup that consumers depend on").

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell page only.
Layout objects are imported from django-crispy-forms. The package adds none of its own.

## Order

**US1 → US2 → US3 → US4, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Arrange fields in groups, rows and columns (P1)

Issue: #48. Delivers FR-001 (less `MultiField`), FR-002, FR-003, FR-005 – FR-008, FR-019; SC-004.

### T001 — `Div` and `Fieldset`

**Files**: `mvp_forms/templates/daisyui/layout/div.html`,
`mvp_forms/templates/daisyui/layout/fieldset.html`, `tests/forms.py`,
`tests/test_pack/test_structure.py`, `tests/templates/tests/own_container.html`

Plan, *The templates*; research R1, R5, R7.

- `div.html` and `fieldset.html` as the plan's table has them.
- `tests/settings.py` already lists `tests/templates` in the template directories. The one
  template that stands for a developer's own goes there.
- Tests, `TestDiv`: fields inside the container in layout order; id, classes and attributes on
  it (US1.5); an empty `Div` draws and raises nothing; a `Div` given its own template is drawn
  with it (FR-019).
- Tests, `TestFieldset`: both fields inside one `fieldset` element whose `legend` is the one
  given (US1.1); an empty legend draws no `legend` element (US1.2); a legend reading a context
  value shows it, and markup in that value is escaped (US1.3, FR-016); id, classes and
  attributes with daisyUI's `fieldset` class kept beside the developer's (US1.5).

### T002 — `Row` and `Column`, nesting and errors

**Files**: `mvp_forms/templates/daisyui/layout/row.html`,
`mvp_forms/templates/daisyui/layout/column.html`, `tests/test_pack/test_structure.py`,
`tests/test_pack/test_independence.py`

Plan, *The templates*; research R4, R6.

- `row.html` and `column.html` as the plan's table has them.
- Tests, `TestRowAndColumn`: each field inside its own column, both columns inside the row, in
  layout order (US1.4); id, classes and attributes on each, the developer's classes beside the
  pack's (US1.5); a `Column` outside a `Row` and a `Row` holding a field directly both draw their
  contents in order. No test names a layout utility.
- Tests, `TestNesting`: a layout nested four deep draws every field exactly once and the drawn
  containers nest as the layout does (US1.6); an invalid field inside `Fieldset` inside `Column`
  has its error element inside its own frame, and the input's `aria-describedby` names it
  (US1.7, FR-008).
- `test_independence.py`: a state for a layout using `Fieldset`, `Div`, `Row` and `Column`,
  unbound and invalid. `LAYOUT_UTILITIES` gains `flex`, `flex-col`, `gap-4`, `md:flex-row`,
  `flex-1` and `min-w-0`.

### T003 — The layout objects page, its standalone twin, README and CHANGELOG

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`
(one icon name), `demo/templates/demo/layout_objects.html`,
`demo/templates/demo/layout_objects_standalone.html`, `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

Plan, *The demo project*; research R8.

- The page pair, the routes `layout-objects` and `layout-objects-standalone`, the menu entry, and
  the first two forms of the plan with the structural objects only. Later stories add to them.
  Each form builds its own layout in `__init__`, and every `css_id` in it carries the form's
  prefix, so no id repeats on the page.
- Tests: both pages respond; each holds a `fieldset` with a `legend`, and the fields of the row
  by id; a post of the empty form comes back with a field error; no id repeats; each page links
  the other; the shell wraps one and the other carries only daisyUI's stylesheet (FR-022, SC-003).
- README: a "Layout objects" part of the public surface naming `Fieldset`, `Div`, `Row` and
  `Column`, where they are imported from, what each is drawn as, and that a developer's id,
  classes and attributes are kept. It says a row sets its columns side by side on a wide page
  using Tailwind layout utilities. The contributing section names the new pages. CHANGELOG: one
  line under Unreleased, Added (FR-023).

---

## US2 — Finish a form with buttons (P2)

Issue: #49. Delivers FR-009 – FR-014.

### T004 — The class filter, and `Submit`, `Reset` and `Button`

**Files**: `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/layout/baseinput.html`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_buttons.py`, `tests/forms.py`

Plan, *The `daisyui_classes` filter*, *The templates*; research R1, R2.

- The filter and its constant. `baseinput.html` for the three visible input types.
- Tests, `TestDaisyuiClasses` (parametrised): a name written for another pack is dropped, a
  repeat is dropped, order is kept, the developer's names stay, `None` and an empty string give
  an empty string.
- Tests, `TestBaseInputs`: each of the three is an `input` of its own type with its name and
  value (US2.1 – US2.3); each carries `btn`; a `Reset` carries no `btn-inverse`; id, classes and
  attributes arrive with the pack's class kept (US2.5); a button given `disabled` is drawn
  disabled; a value reading the context is filled in.

### T005 — `StrictButton`, `ButtonHolder` and `FormActions`

**Files**: `mvp_forms/templates/daisyui/layout/button.html`,
`mvp_forms/templates/daisyui/layout/buttonholder.html`,
`mvp_forms/templates/daisyui/layout/formactions.html`, `tests/test_pack/test_buttons.py`,
`tests/test_pack/test_independence.py`

Plan, *The templates*; research R1, R4.

- The three templates.
- Tests, `TestStrictButton`: a `button` element holding the developer's markup with a context
  value filled in and escaped; `type` is `button` unless the developer chose another; id,
  classes and attributes arrive with `btn` kept (US2.4, US2.5).
- Tests, `TestHolders`: parametrised over the two, the buttons are inside one container in the
  order given and the container carries its id and classes. Other attributes are tested on
  `FormActions` only, since `ButtonHolder` accepts none (US2.6).
- `test_independence.py`: the layout state gains a `FormActions` with all four buttons and a
  `ButtonHolder`. `LAYOUT_UTILITIES` gains `flex-wrap`, `gap-2` and `mt-4`.

### T006 — Buttons added to the helper, and the buttons on the demo page

**Files**: `mvp_forms/templates/daisyui/inputs.html`,
`mvp_forms/templates/daisyui/whole_uni_form.html`, `tests/test_pack/test_buttons.py`,
`tests/test_pack/test_independence.py`, `demo/forms.py`, `demo/views.py`,
`demo/templates/demo/layout_objects.html`, `demo/templates/demo/layout_objects_standalone.html`,
`tests/test_demo.py`, `README.md`, `CHANGELOG.md`

Plan, *The templates*, *The demo project*; research R3.

- `inputs.html`, and its include in the wrapper.
- Tests, `TestHelperButtons`: with no layout, each helper-added button is inside the form element
  and has the same element, type, name, value and classes as the same button in a layout
  (US2.7, FR-014); a helper with no buttons draws no container; with `form_tag` off, a layout's
  buttons are still drawn (US2.8).
- `test_independence.py`: a state for a helper with added buttons.
- Demo: the submittable form ends in a `FormActions` with the four buttons, and the third and
  fourth forms of the plan are added. Every button name and `css_id` carries its form's prefix. Tests: the page holds each button by name, and the helper-added ones.
- README: the buttons and the two holders join the "Layout objects" list, with a line saying
  buttons added with `add_input` are drawn after the fields. CHANGELOG: one line.

### T010 — Review fixes to the helper's buttons

**Files**: `mvp_forms/templatetags/daisyui.py`, `mvp_forms/templates/daisyui/inputs.html`,
`tests/test_pack/test_buttons.py`, `tests/test_templatetags/test_daisyui.py`, `README.md`

- A `StrictButton` added to the helper is drawn by its own `render`, through the tag
  `daisyui_layout_object`, so it is the button a layout draws (CR-001).
- A `Hidden` added to the helper is drawn outside the buttons' container, and a helper holding
  only hidden inputs draws no container, through the filter `daisyui_shown` (CR-003).
- README: a helper-added input's value is drawn as written, `template=` applies in a layout only
  (CR-002), and the four class names that are never drawn are named (CR-004).

---

## US3 — Place raw HTML and hidden values in a layout (P3)

Issue: #50. Delivers FR-015 – FR-017.

### T007 — `HTML` and `Hidden`

**Files**: `mvp_forms/templates/daisyui/layout/baseinput.html`,
`tests/test_pack/test_raw_content.py`, `tests/test_pack/test_independence.py`, `demo/forms.py`,
`demo/templates/demo/layout_objects.html`, `demo/templates/demo/layout_objects_standalone.html`,
`tests/test_demo.py`, `README.md`, `CHANGELOG.md`

Plan, *The templates*; research R1, R2, R7.

- The hidden branch of `baseinput.html`: no `class`, no `id`.
- Tests, `TestHTML`: output sits between the two fields it was placed between (US3.1); a context
  value is filled in and markup in it is escaped, while the developer's own markup is kept
  (US3.2, FR-016); parametrised over `Fieldset`, `Column`, `ButtonHolder` and `FormActions`, the
  output is inside that container (US3.3).
- Tests, `TestHidden`: an `input` of type `hidden` with its name and value, inside the form
  (US3.4); no `class` attribute (US3.5); an attribute passed as a keyword arrives.
- `test_independence.py`: the layout state gains an `HTML` and a `Hidden`.
- Demo, README and CHANGELOG gain both objects.

---

## US4 — Group fields under one shared label (P3)

Issue: #51. Delivers FR-001 (`MultiField`), FR-004; SC-001, SC-002, SC-005.

### T008 — `MultiField`

**Files**: `mvp_forms/templates/daisyui/layout/multifield.html`,
`mvp_forms/templates/daisyui/multifield.html`, `tests/test_pack/test_structure.py`,
`tests/test_pack/test_independence.py`, `demo/forms.py`, `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

Plan, *The templates*; research R1, R2, R5.

- The two templates.
- Tests, `TestMultiField`: both fields inside one `fieldset` element whose `legend` is the label
  (US4.1); an invalid field inside it has its error in its own frame and its `aria-describedby`
  names it (US4.2); id, classes and attributes on the group (US4.3); none of `ctrlHolder`,
  `blockLabel` or `error` is drawn, bound or unbound, and drawing the same layout twice changes
  nothing.
- `test_independence.py`: the layout state gains a `MultiField`, which makes it a layout of all
  thirteen objects (SC-001).
- Demo, README and CHANGELOG gain the object.

### T009 — The documented examples draw as written

**Files**: `tests/test_pack/test_documented_examples.py`, `tests/forms.py`

Plan, *Tests*.

- One parametrised test, `TestDocumentedExamples`: the example from each object's docstring in the
  installed django-crispy-forms where it has one, drawn against a form that has the fields the
  example names. Each draws without raising and holds each named field once (SC-002). No argument
  is added for the pack's sake. The three examples that do not parse (`ButtonHolder`,
  `FormActions`, `Column`) are repaired by quoting the string and nothing else. `Submit`, `Reset`,
  `Button` and `Hidden` are built with the arguments their docstrings show and placed in a layout.
  `MultiField` has no docstring example and is covered by T008.
- Check the README's "Layout objects" list against the thirteen, and that every one of them is on
  the demo page (SC-005).

### T011 — Review fixes to the documented examples and the demo

**Files**: `tests/test_pack/test_documented_examples.py`, `demo/forms.py`, `README.md`

- Every documented example now names an element that must be drawn once, so an example that
  draws nothing fails (CR-005).
- The demo's legend and note are wrapped for translation like the labels beside them (CR-006).
- README: what a `Column` carries outside a `Row`, that a `MultiField` label is not a template,
  and that `css_id` and `css_class` do nothing on a `Hidden`.
