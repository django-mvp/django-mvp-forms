# Tasks — 001 Text inputs drawn as daisyUI

**Branch**: `001-text-inputs` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, order of decoration or which colour was chosen. Elements
are found by id, by `for`, by role and by name. A class is asserted only where it is the daisyUI
component or its error modifier, which the testing standard counts as behaviour for a published
pack ("Markup that consumers depend on").

Code standards for every task: no leading-underscore names anywhere (methods, helpers,
constants, templates); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell page only.
Every class the pack writes is a daisyUI component class or modifier.

## Order

**US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Text-like fields draw as daisyUI inputs with no layout (P1)

Issue: #41. Delivers FR-001 – FR-009; SC-001, SC-002.

### T001 — Select the pack and draw each covered input

**Files**: `mvp_forms/templatetags/__init__.py`, `mvp_forms/templatetags/daisyui.py`,
`mvp_forms/templates/daisyui/uni_form.html`, `mvp_forms/templates/daisyui/field.html`,
`demo/settings.py`, `pyproject.toml` (conformance paths and the deptry note only),
`tests/forms.py`, `tests/conftest.py`, `tests/test_templatetags/`, `tests/test_pack/__init__.py`,
`tests/test_pack/test_inputs.py`, `README.md`, `CHANGELOG.md`

Plan, *`{% daisyui_input field %}` and `FieldInput`*, *The field frame contract*, *The demo
project* (settings only); research R1, R3, R4.

- Demo settings select `daisyui` and stop installing `crispy_tailwind`. The existing demo tests
  stay green.
- `FieldInput`: `component`, `css_class` and `render()` through `as_widget`. The tag
  `daisyui_input`. `attrs` carries the class only in this task.
- `uni_form.html` loops the fields through `field_template`. `field.html` in this task is the
  wrapper, a plain label and the input; hidden fields print bare. US2 completes the frame.
- `tests/forms.py` holds the forms the suite draws. A fixture in `tests/conftest.py` parses a
  rendered fragment with BeautifulSoup. No wrapper class around it.
- The frame's element is a fixed `div`. `field.html` reads no `tag` and no `wrapper_class` from
  the context (plan, *The field frame contract*).
- Tests, `TestFieldInput`: the component for each of the nine kinds (parametrised); a subclass
  of a covered widget; an uncovered widget gets no pack class; the developer's class is kept and
  not repeated; the widget's `attrs` are unchanged after a render.
- Tests, `test_inputs.py` `TestCoveredInputs`: through `|crispy`, each of the nine kinds is the
  right element with its component class (US1.1, US1.2); a developer's placeholder, class, input
  type and row count all arrive (US1.5); name, id and value are Django's (FR-008).
- README: the quickstart (settings, a form, a template) and the first public-surface entry
  naming the pack `daisyui`, the two settings that select it and the nine input kinds. The
  `daisyui_input` tag is the pack's own and is not listed. Drop the "pack is not written yet" status line. CHANGELOG: one line under
  Unreleased, Added.

### T002 — The tag, a single field, bound values and fields the pack does not cover

**Files**: `mvp_forms/templates/daisyui/whole_uni_form.html`,
`mvp_forms/templates/daisyui/display_form.html`, `tests/test_pack/test_inputs.py`, `tests/forms.py`

Plan, *The form templates*; research R1.

- `whole_uni_form.html` and `display_form.html`, enough to draw the fields through
  `{% crispy form %}`. The form element and token are present here and are tested in US3.
- Tests: the fields drawn through the tag equal the fields drawn through the filter, for a form
  with no helper and for one whose helper carries the default layout (US1.3, FR-003); a bound
  form's inputs hold what Django would put there, and a password holds nothing unless the widget
  has `render_value` (US1.4); one field through `|as_crispy_field` equals that field inside the
  whole form (US1.6, FR-004); a form with a select, a checkbox and a file field still draws each
  in order with its label, help text and errors and raises nothing (US1.7, FR-009); a form with
  no fields draws no field and raises nothing, and through the tag still has its form element
  (edge case).

### T012 — Inputs fill the width of their field

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_inputs.py`, `tests/test_templatetags/test_daisyui.py`, `README.md`,
`docs/adr/0003-daisyui-classes-and-tailwind-for-layout-only.md`

Asked for at the walkthrough. Every text-like input and textarea carries `w-full`, which the
class test allows by name. The width itself gets no test.

### T013 — A developer's own width wins

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/test_templatetags/test_daisyui.py`,
`docs/adr/0007-inputs-fill-their-container.md`, `README.md`

The pack leaves `w-full` out when the widget's class already holds an unprefixed width utility.
Recorded as ADR 0007.

---

## US2 — Label, required marker, help text and errors belong to their input (P1)

Issue: #42. Delivers FR-010 – FR-019; SC-003, SC-008.

### T003 — The label and the required marker

**Files**: `mvp_forms/templates/daisyui/field.html`, `mvp_forms/templatetags/daisyui.py`,
`tests/test_pack/test_field_frame.py`, `tests/test_templatetags/test_daisyui.py`

Plan, *The field frame contract*; research R2 case 2.

- The label as the frame's caption, with the marker on required fields. `FieldInput.attrs`
  gains `aria-required` when the field is required and the form's `use_required_attribute` is
  off.
- Tests: the label's `for` is the input's id (US2.1); a required field has the marker and an
  optional one has none, and the input carries `required` (US2.2); a form with
  `use_required_attribute = False` still has the marker and the input carries `aria-required`
  (edge case); the marker is hidden from assistive technology; an empty label leaves no label
  element and the input is still drawn (US2.9).

### T004 — Help text and errors, tied to the input

**Files**: `mvp_forms/templates/daisyui/field.html`, `mvp_forms/templatetags/daisyui.py`,
`tests/test_pack/test_field_frame.py`, `tests/test_templatetags/test_daisyui.py`

Plan, *The field frame contract*; research R2, R6.

- Help text and errors, written inside the frame. The error modifier on the input.
- Tests: with help text, an element with the id the input's `aria-describedby` names (US2.3);
  with errors, every message inside the one error element, `aria-invalid` on the input, the
  error element named by the description, and the error modifier on the input (US2.4, FR-013,
  FR-014); with both, the description names both and both exist (US2.5); with neither, the input
  has no description (US2.6); every id an input describes itself by exists on the page, for each
  of those four cases (FR-015); a label, help text and error containing markup are escaped, and
  help text marked safe is kept (US2.7); two forms of one class with different prefixes share no
  id and every `for` and description resolves inside its own form (US2.8, FR-017); a form with
  `auto_id=False` emits no id, no `for` and no description.

---

## US3 — The form and its own errors (P2)

Issue: #43. Delivers FR-020 – FR-025; SC-004.

### T005 — Form-wide errors

**Files**: `mvp_forms/templates/daisyui/errors.html`,
`mvp_forms/templates/daisyui/uni_form.html`, `mvp_forms/templates/daisyui/display_form.html`,
`tests/test_pack/test_form.py`, `tests/forms.py`

Plan, *The form templates*.

- Tests: each form-wide error appears once, outside every field frame, inside an element with
  `role="alert"`, through the filter and through the tag (US3.1); a form with none draws no such
  element (US3.2); `|as_crispy_errors` draws the same element (US3.3); a helper's
  `form_error_title` is drawn inside it, escaped.

### T006 — The form element and the helper's switches

**Files**: `mvp_forms/templates/daisyui/whole_uni_form.html`,
`mvp_forms/templates/daisyui/field.html`, `mvp_forms/templatetags/daisyui.py`,
`tests/test_pack/test_form.py`, `tests/test_templatetags/test_daisyui.py`, `README.md`

Plan, *The form templates*, *Errors turned off*; research R2 cases 1 and 3.

- Tests: through the tag with no helper, a form element holding a CSRF token (US3.4); a helper's
  method, action, id, class and extra attributes are on the form element (US3.5); a form with a
  file field is multipart; `form_tag = False` leaves no form element, `disable_csrf = True` no
  token, and a get form no token (US3.6); `form_show_labels = False` leaves no label and every
  input carries an `aria-label` (US3.7, FR-024); `form_show_errors = False` on an invalid form
  draws no field error and no form-wide error, the input has no error modifier, and its
  description names nothing missing, both with and without help text (US3.8, FR-015);
  `label_class` and `field_class` are on every label and on an element holding each input
  (US3.9); `help_text_inline` and `error_text_inline` change nothing (edge case).
- `TestFieldInput`: `aria-label` only with labels off and never over the developer's own; a
  label marked safe that holds a quoted attribute arrives in `aria-label` with its tags
  stripped; the description with errors off, with help text and without; a widget carrying the
  developer's `aria-describedby` keeps it; a `RadioSelect` with labels off and errors off
  receives none of `aria-label`, `aria-required` and `aria-describedby`.
- README public surface: the helper settings the pack honours and the two it ignores.

### T009 — Two corrections found once every story was in

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/test_templatetags/test_daisyui.py`

Added at convergence. A label marked safe that holds an HTML entity is named in `aria-label` by
the character. The tag reads `form_show_labels` and `form_show_errors` as the templates do: off
only when `False`.

### T010 — Review fixes to the input tag

**Files**: `mvp_forms/templatetags/daisyui.py`, `tests/test_templatetags/test_daisyui.py`, `README.md`

The error modifiers are written out as literals. A label not marked safe is named in
`aria-label` exactly as written. The tag reads a falsy switch as off, as the templates do.

---

## US4 — The pack works in any daisyUI project (P2)

Issue: #44. Delivers FR-026 – FR-030; SC-005, SC-006.

### T007 — Classes checked against daisyUI's build, and no reliance on django-mvp

**Files**: `tests/data/daisyui-classes.txt`, `tests/conftest.py`,
`tests/test_pack/test_independence.py`, `README.md`

Research R5, R8, R9. The class list is already downloaded and extracted: the brief names where
to copy it from, unchanged, into `tests/data/daisyui-classes.txt`.

- Tests, `TestEmittedClasses`: draw the suite's forms in every state (unbound, bound and
  invalid, with help text, with form-wide errors, through the filter and the tag), collect every
  class, remove the ones the test's own forms and helper supplied, and assert each of the rest is
  in the list (US4.2, FR-026, SC-005). Assert the collected set is not empty.
- Tests, `TestWithoutDjangoMvp`: with `INSTALLED_APPS` reduced to `crispy_forms` and
  `mvp_forms` and a bare template engine, a form draws (US4.1, SC-006). django-crispy-forms
  caches its compiled pack templates per process, so a fixture in `tests/conftest.py` calls
  `cache_clear()` on `uni_form_template`, `uni_formset_template`, `whole_uni_form_template` and
  `default_field_template` on entering the override and again on leaving it.
- Tests, `TestDistributedFiles`: no template under `mvp_forms/templates/` loads or uses Cotton
  or extends or includes a path outside `daisyui/`; no module under `mvp_forms/` imports `mvp`,
  `django_cotton` or `daisy_cotton`; the package has no `static/` directory (US4.4, FR-027 –
  FR-029).
- README: under Installation, that the page must load daisyUI 5, that daisyUI's CDN build needs
  no build step, and that a host project with its own Tailwind build has to make that build
  produce the classes the pack writes.

These tests describe what US1 to US3 already built and may pass on their first run. That is
expected here: they pin a property no earlier test covered. Prove each one can fail by breaking
the thing it guards once, locally, with the whole suite running and not the test alone, and say
so in the report.

---

## US5 — See it and install it (P3)

Issue: #45. Delivers FR-031 – FR-034; SC-007.

### T008 — The text inputs page, its standalone twin, and the README checked as written

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py` (the icon name only), `demo/templates/demo/text_inputs.html`,
`demo/templates/demo/text_inputs_standalone.html`, `tests/test_demo.py`, `tests/conftest.py`,
`README.md`, `CHANGELOG.md`

Plan, *The demo project*; research R7.

- Tests, `TestTextInputsPage`: the page responds inside the shell; the sidebar links it
  (US5.3); for each of the five states, an input of each of the nine kinds is present, found by
  its prefixed id (US5.1, SC-007); a post comes back 200 with an error element for a field and
  an alert for the form (US5.2); every input and textarea has a label that names it, every id in
  a description exists and no id repeats (SC-003).
- Tests, `TestStandaloneTextInputsPage`: it responds; it carries the link to daisyUI's CDN
  stylesheet and none of the shell's navigation or stylesheet; it holds the same inputs; a post
  comes back with errors; the same label, description and id checks (US5.4).
- README: read the installation and quickstart sections as a developer would and correct
  anything that would not work as written (US5.5); add the demo's two pages to the contributing
  section. CHANGELOG: the demo pages.

### T011 — Review fixes to the demo tests

**Files**: `tests/test_demo.py`

The submit button is found by its type. No test pins which script the standalone page loads.
