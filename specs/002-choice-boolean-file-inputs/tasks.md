# Tasks — 002 Choice, boolean and file inputs drawn as daisyUI

**Branch**: `002-choice-boolean-file-inputs` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, order of decoration or which colour was chosen. Elements
are found by id, by `for`, by role, by name and by type. A class is asserted only where it is the
daisyUI component or its error modifier, which the testing standard counts as behaviour for a
published pack ("Markup that consumers depend on").

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears in
anything under `mvp_forms/`. Cotton components are for the demo project's shell page only. Every
input and component is a daisyUI class or modifier; a plain Tailwind utility is used only for
layout where daisyUI has no component, and is named in `LAYOUT_UTILITIES`. `.github/` is never
touched.

Where FR-003 applies, a test draws through both `{{ form|crispy }}` and `{% crispy form %}`.

## Order

**US1 → US2 → US3 → US4 → US5 → US6 → US7, sequential, in the feature worktree** (plan, *Story
order*).

---

## US1 — A field with choices draws as a select (P1)

Issue: #52. Delivers FR-001 (selects), FR-003, FR-004, FR-005, FR-006, FR-008, FR-010, FR-011,
FR-019, FR-020,
FR-017, FR-018; SC-001, SC-002.

### T001 — Draw selects as daisyUI's select

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_choice_inputs.py`,
`tests/test_pack/test_inputs.py`, `tests/test_pack/test_independence.py`, `README.md`,
`CHANGELOG.md`

Plan, *`FieldInput`*; research R1, R2, R8.

- `components` gains `Select` and `SelectDateWidget` as `select`; `error_modifiers` gains
  `select-error` as a literal. `w-full` applies to a select.
- Re-point the FS-001 tests that use a select, a checkbox or a file input as their uncovered
  example at `SplitDateTimeWidget` (`UncoveredWidgetsForm`, `UncoveredForm`,
  `TestUncoveredWidgets`). Change the example widget only, never an assertion's meaning.
- Tests, `TestFieldInput`: the component for `Select`, `NullBooleanSelect`, `SelectMultiple` and
  `SelectDateWidget`; a host subclass of `Select`.
- Tests, `test_choice_inputs.py` `TestSelect`: each is a `<select>` with the component class,
  every choice offered and the label's `for` equal to the select's id (US1.1); the held choice is
  the one selected, on first draw and after a failed submission (US1.2, FR-010); a multiple
  select has `multiple` and every held value selected (US1.3); named groups are `<optgroup>`s
  holding their choices (US1.4); an invalid value gives `aria-invalid`, the error modifier and a
  description naming the error element (US1.5); a null-boolean field offers three options
  (US1.6); no choices draws an empty select; a value no longer among the choices selects nothing;
  markup in a choice label and a group name is escaped; a developer's class and `data-`
  attribute are kept beside the pack's; the widget's `attrs` are unchanged after a draw.
- The class test gains select states (unbound, invalid).
- README public surface and CHANGELOG: selects.

### T002 — Frame a group as a fieldset, and draw a date's three selects

**Files**: `mvp_forms/templatetags/daisyui.py`, `mvp_forms/templates/daisyui/field.html`,
`mvp_forms/templates/daisyui/widgets/attrs.html`,
`mvp_forms/templates/daisyui/widgets/select_date.html`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_choice_inputs.py`,
`tests/test_pack/test_field_frame.py`, `tests/test_pack/test_independence.py`, `README.md`,
`CHANGELOG.md`

Plan, *`FieldInput`*, *The tags*, *The field frame*, *The widget templates*; research R3, R4.

- `FieldInput.templates`, `template_name`, the widget copy in `render()`, `is_group`,
  `group_description`. The tag `daisyui_field`. The filter `daisyui_date_part`.
- The frame draws a group as `<fieldset>` with `<legend>`, described by its help text and errors,
  and named by `aria-label` when labels are off.
- `attrs.html` and `select_date.html`.
- `LAYOUT_UTILITIES` gains `flex` and `gap-2`.
- Tests, `TestFieldInput`: `template_name` for the stock widget, `None` for a subclass that names
  its own template and for a widget with no pack template; the field's widget keeps its own
  `template_name` after a draw; `group_description` for help only, errors only, both, neither,
  errors off, and no `auto_id`.
- Tests, `TestSelectDate`: three selects, each with the component class and an accessible name of
  its own; one legend, one help text and one error element for the field (US1.7, FR-005); the
  fieldset's `aria-describedby` names ids that exist; a held date selects its three parts; with
  labels off the fieldset has an `aria-label`; a subclass naming its own template is drawn by it.
- Tests, `test_field_frame.py`: a non-group field is still a `div` with a `label`.
- README: a group is drawn as a fieldset with a legend. CHANGELOG.

---

## US2 — A boolean field draws as a checkbox (P1)

Issue: #53. Delivers FR-001 (checkbox), FR-006, FR-008, FR-009, FR-010.

### T003 — Draw a single checkbox inside its label

**Files**: `mvp_forms/templatetags/daisyui.py`, `mvp_forms/templates/daisyui/field.html`,
`tests/forms.py`, `tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_checkbox.py`,
`tests/test_pack/test_independence.py`, `README.md`, `CHANGELOG.md`

Plan, *`FieldInput`*, *The field frame* (a single checkbox); research R5.

- `components` gains `CheckboxInput` as `checkbox`, with `checkbox-error`, and no `w-full`.
- The frame draws the checkbox inside `<label class="label" for>` with the label text and the
  required marker after it.
- Tests: the input is a checkbox with the component class and no `w-full`; the label that holds
  it has `for` equal to its id (US2.1); `checked` follows the value, first draw and redrawn
  (US2.2); a required field submitted unticked has its error element, `aria-invalid`, the error
  modifier and a description naming the error (US2.3); help text is described (US2.4); the
  required marker only when required; `label_class` reaches the label; labels off leaves the
  checkbox named by `aria-label` and draws no label element; the frame has exactly one label for
  the field.
- README, CHANGELOG: checkbox.

---

## US3 — Options shown at once draw as a radio group or a checkbox group (P1)

Issue: #54. Delivers FR-001 (groups), FR-007, FR-008, FR-009, FR-010, FR-011, FR-017.

### T004 — Draw radio and checkbox groups from the pack's own template

**Files**: `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/widgets/group.html`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_choice_inputs.py`,
`tests/test_pack/test_independence.py`, `README.md`, `CHANGELOG.md`

Plan, *`FieldInput`*, *The widget templates* (`group.html`); research R2, R4.

- `components` gains `CheckboxSelectMultiple` as `checkbox`, before `RadioSelect` as `radio`,
  with `radio-error`. `templates` gains both, pointing at `group.html`.
- `group.html`. `LAYOUT_UTILITIES` gains `flex-col`.
- Tests, `TestRadioGroup` and `TestCheckboxGroup` (shared cases parametrised over the two): every
  option is an input of the right type with the component class, sharing one name, each inside or
  beside a label whose `for` is its id (US3.1, US3.2); the wrapper around the options carries no
  component class; the frame is a fieldset with a legend (US3.3); exactly the held options are
  checked (US3.4); an invalid submission draws one error element, described by the fieldset
  (US3.5); no option of a required checkbox group has `required` (US3.6, FR-009); named groups
  each sit in an element with the group's name (US3.7); an attribute a widget sets on one option
  (a `disabled` option from a `create_option` override) is on that option only; no choices draws
  no option; markup in an option's label and a group's name is escaped; no id repeats; a
  subclass naming its own template is drawn by it.
- README, CHANGELOG: radio and checkbox groups.

---

## US4 — A file field draws as a file input (P2)

Issue: #55. Delivers FR-001 (file inputs), FR-009, FR-012, FR-018.

### T005 — Draw file inputs, and the file a field already holds

**Files**: `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/widgets/clearable_file_input.html`, `tests/forms.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_file_inputs.py`,
`tests/test_pack/test_independence.py`, `README.md`, `CHANGELOG.md`

Plan, *`FieldInput`*, *The widget templates* (`clearable_file_input.html`); research R2.

- `components` gains `FileInput` as `file-input`, with `file-input-error` and `w-full`.
  `templates` gains `ClearableFileInput`.
- `clearable_file_input.html`.
- Tests: a `FileInput` and an empty `ClearableFileInput` are `<input type="file">` with the
  component class, named by the frame's label (US4.1); an optional field holding a file has a
  link whose `href` is the file's url, a removal checkbox with its own label tied to it, and the
  file input (US4.2); a required field holding a file has the link, no removal checkbox, and no
  `required` on the file input (US4.3, FR-009); a widget allowing several files has `multiple`
  (US4.4); a rejected file gives the error element, `aria-invalid`, the error modifier and a
  description naming the error (US4.5); markup in a file name is escaped; a subclass naming its
  own template is drawn by it.
- README, CHANGELOG: file inputs.

---

## US5 — A hidden field is carried without being seen (P2)

Issue: #56. Delivers FR-002, FR-013; SC-005.

### T006 — Show a hidden field's errors with the form-wide errors

**Files**: `mvp_forms/templatetags/daisyui.py`, `mvp_forms/templates/daisyui/errors.html`,
`tests/forms.py`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_hidden_inputs.py`, `README.md`, `CHANGELOG.md`

Plan, *The tags* (`daisyui_form_errors`), *The form-wide alert*; research R7.

- The tag `daisyui_form_errors`; `errors.html` draws from it.
- Tests: a hidden field is an `<input type="hidden">` with its value, and the page has no frame,
  label, help text or error element for it (US5.1); a `MultipleHiddenInput` draws one input per
  value (US5.2); a hidden field with an invalid value puts one message in the alert, through the
  filter, the tag and `|as_crispy_errors`, and the alert is drawn even when the form has no
  other form-wide error (US5.3, SC-005); the message carries the field's name and the error, as
  data chosen by a condition; markup in a hidden field's error is escaped; a form whose only
  fields are hidden draws no frame; a disabled hidden field is drawn as Django draws it; errors
  off draws no alert.
- README, CHANGELOG: hidden inputs and their errors.

---

## US6 — A disabled or read-only field is drawn as one (P2)

Issue: #57. Delivers FR-014, FR-015, FR-016, FR-023.

### T007 — Hold the disabled and read-only states for every input

**Files**: `tests/forms.py`, `tests/test_pack/test_states.py`, `README.md`, `CHANGELOG.md`, and
`mvp_forms/` only where a test below fails

Plan, *Disabled and read-only*; research R6.

The states are the browser's and daisyUI's, drawn from attributes already on the input. Most of
these tests demonstrate a criterion that already holds once US1 to US4 are in; each still has to
be watched to fail first by breaking the behaviour it guards (for example by removing the
attribute in a scratch edit), and that is said in the report.

- Tests, parametrised over a text input, a number input, a date input, a textarea, a select, a
  checkbox and a file input: a disabled field's input has `disabled` and its component class,
  and still holds its value (US6.1, US6.3, US6.6).
- Every option of a disabled radio group and checkbox group has `disabled` (US6.2).
- A disabled file field holding a file has `disabled` on the removal checkbox (US6.4).
- A `readonly` attribute set on a widget is on the input unchanged, for a text input, a
  textarea, a select, a checkbox and a file input, and the pack adds no class because of it
  (US6.5, FR-016).
- A read-only text input and textarea have `readonly`, no `disabled`, a `name` and their value;
  a disabled one has `disabled` (US6.7, US6.8: a browser sends the first and not the second).
- A text input both disabled and read-only has both attributes; a disabled password input has no
  value.
- README: a section on disabled and read-only fields: what marks each, that daisyUI draws
  disabled from the attribute, that read-only is the browser's and exists only on text inputs
  and textareas. CHANGELOG.

---

## US7 — Every input and state can be seen in the demo project (P3)

Issue: #58. Delivers FR-021, FR-022; SC-003, SC-004, SC-006.

### T008 — The demo page, on the shell and standalone

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py` (the icon name only), `demo/templates/demo/choice_inputs.html`,
`demo/templates/demo/choice_inputs_standalone.html`, `tests/test_demo.py`, `README.md`,
`CHANGELOG.md`

Plan, *The demo project*; research R10.

- The form, the shared mixin, the two views, routes, menu entry and icon.
- Tests in `test_demo.py`, for both pages: it responds; every input kind is present in each of
  the six states and in the submittable form; the disabled state's inputs are disabled; the
  held-value state's clearable file field links its file; the error state's alert is present; a
  text input appears disabled and another read-only; a post comes back with a field error; the
  submittable form is `multipart` with a token and a button; every visible input, select and
  textarea has a label or an `aria-label`; every group is a fieldset with a legend; every
  described id exists; no id repeats (SC-003). The shell page is linked from the sidebar and
  links the standalone page; the standalone page carries daisyUI's CDN install and none of the
  shell.
- The existing text-inputs tests stay green and unedited.
- README: the public-surface list is complete for every widget in FR-001 and FR-002, and the
  demo section names the new pages. CHANGELOG: the demo page.
