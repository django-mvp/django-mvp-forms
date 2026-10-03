# Implementation Plan: choice, boolean and file inputs drawn as daisyUI

**Branch**: `002-choice-boolean-file-inputs` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-choice-boolean-file-inputs/spec.md`. Evidence for
every claim below about Django and daisyUI is in [research.md](research.md).

## Summary

`FieldInput` learns the rest of Django's widgets: select, checkbox, radio and file input each get
their daisyUI component and error modifier. Three widgets whose stock Django template cannot carry
daisyUI's markup (a radio or checkbox group, a date drawn as three selects, and a file input that
already holds a file) are drawn from templates of the pack's own, through a throwaway copy of the
widget so nothing is written to the form. The field frame draws a group as a `<fieldset>` with a
`<legend>` and a single checkbox inside its own label. The form-wide alert gains the errors of
hidden fields. Disabled and read-only states are the browser's and daisyUI's, drawn from the
attributes Django and the developer already put on the input; the feature holds them in place
with tests and documents them. The demo gains one page on the shell and one standalone.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms 2.7 or later. No new
dependency.

**Storage**: none

**Testing**: pytest with pytest-django; `beautifulsoup4` to read rendered markup

**Project Type**: library (a Django app) with an undistributed demo project

**Constraints**: plain Django templates only (`{% include %}` between the pack's own templates is
expected); no import of django-mvp; daisyUI component classes and modifiers for every input, and
plain Tailwind utilities only for layout where daisyUI has no component; no stylesheet, no script,
no class of the pack's own

**Scale/Scope**: one tag module extended, the frame and the alert changed, four small templates
added, two demo pages

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first. Tests read rendered markup for the element, the ids, the attributes and the component classes. No test asserts wording, width, spacing or order of decoration. |
| II Simplicity | No new dependency. Django's own widget template is used wherever a class is enough; the pack writes a template only for the three widgets where it is not (research R2). |
| III Anti-abstraction | No widget subclasses and no registry beyond the two dicts FS-001 already has plus one for templates. The demo's shared mixin is parametrised only because there are now two page pairs. |
| IV Integration-first | Every pack test draws through `\|crispy`, `{% crispy %}` or `\|as_crispy_field`. |
| V Security | Choice labels, group names, file names and the hidden-field message go through autoescaping. No `\|safe`, no `mark_safe` on data. |
| VI Documentation | README and CHANGELOG change in the story that draws each widget. |
| VII Dependencies | None added. |
| VIII i18n | The pack's own text is three date-part names, marked for translation and shipped in a base English catalogue at `mvp_forms/locale/en/LC_MESSAGES/django.po`. The hidden-field message is Django's own, already translated by Django. |
| XI Compatibility | The frame's ids, the template paths and `FieldInput.components` stay as FS-001 published them. The frame's outer element changes for a group only (ADR to record). |
| XIII Plain templates | Checked by the existing tests, which read every template under `mvp_forms/templates/`. |
| XIV Stock daisyUI | Every component is daisyUI's. Three layout utilities are added by name (research R8). |

No violations, so no complexity table.

## Project Structure

```text
mvp_forms/
├── templates/daisyui/
│   ├── field.html                    # the frame: div, fieldset for a group, label around a checkbox
│   ├── errors.html                   # form-wide errors, now with hidden fields' errors
│   └── widgets/
│       ├── attrs.html                # an input's attributes
│       ├── group.html                # a radio group or a checkbox group
│       ├── select_date.html          # a date as three named selects
│       └── clearable_file_input.html # a file input, with the file it holds
├── templatetags/daisyui.py           # FieldInput, {% daisyui_field %}, the daisyui_date_part filter
└── locale/en/LC_MESSAGES/django.po   # the pack's three strings

demo/                                 # one new form, one mixin shared by both page pairs, two templates

tests/
├── forms.py                          # the forms the new tests draw
├── test_templatetags/test_daisyui.py # FieldInput, extended
└── test_pack/
    ├── test_choice_inputs.py         # US1, US3
    ├── test_checkbox.py              # US2
    ├── test_file_inputs.py           # US4
    ├── test_hidden_inputs.py         # US5
    └── test_states.py                # US6
```

## The pack

### `FieldInput`

`components`, in this order (first `isinstance` match wins, so a subclass comes before its
parent):

| Widget | Component | Error modifier | Fills its container |
|---|---|---|---|
| the six text widgets of FS-001 | `input`, `textarea` | as today | yes |
| `Select` (so `NullBooleanSelect`, `SelectMultiple`), `SelectDateWidget` | `select` | `select-error` | yes |
| `CheckboxInput`, `CheckboxSelectMultiple` | `checkbox` | `checkbox-error` | no |
| `RadioSelect` | `radio` | `radio-error` | no |
| `FileInput` (so `ClearableFileInput`) | `file-input` | `file-input-error` | yes |

`CheckboxSelectMultiple` is listed before `RadioSelect`, its parent. Every error modifier is
written as a literal. `w-full` is added only for a component that has a width to fill, named in
one class attribute beside `width`.

`templates` maps a Django widget class to the pack's template for it:

| Widget | Template |
|---|---|
| `CheckboxSelectMultiple`, `RadioSelect` | `daisyui/widgets/group.html` |
| `SelectDateWidget` | `daisyui/widgets/select_date.html` |
| `ClearableFileInput` | `daisyui/widgets/clearable_file_input.html` |

`template_name` is the pack's template for the field's widget, or `None`. It is the first entry
whose class the widget is an instance of **and** whose `template_name` the widget still has
unchanged from that class. A widget that names a template of its own gets `None` and is drawn by
its own template with the component class only (FR-004).

`render()` draws through `BoundField.as_widget`, as today. When `template_name` is set it passes
`widget=` a shallow copy of the field's widget with `template_name` replaced. The field's own
widget is never written to (ADR 0004). The one FS-001 path that calls the widget's `render`
directly (errors off, no help text) uses the same copy.

`is_group` is `field.use_fieldset`, Django's own flag (research R4). The three ARIA corrections of
ADR 0005 stay off for a group, as today.

`group_description` is what a group's `<fieldset>` is described by: the help text's id when there
is help text, then the error element's id when the field has errors and errors are shown. Empty
when neither is drawn or the form has no `auto_id`.

`label_text`, already there, is also what names a group whose label is not drawn.

### The tags

- `{% daisyui_field field as drawn %}`: returns the `FieldInput` for the field, built with the
  two switches read from the context. The frame asks it which shape to draw and calls
  `drawn.render`. It replaces `{% daisyui_input %}`, which the frame was the only caller of and
  which is deleted in the same task. No alias is kept.
- The filter `daisyui_date_part`, used by `select_date.html` only.

The form-wide alert needs no tag: see *The form-wide alert*.

### The field frame

`daisyui/field.html`, still given `field` and reading only `form_show_labels`,
`form_show_errors`, `label_class` and `field_class`:

```text
hidden field → the widget alone (unchanged)

a group (field.use_fieldset):
<fieldset id="div_<auto_id>" class="fieldset" aria-describedby="<group_description>">
  <legend class="fieldset-legend [label_class]">label  marker</legend>   ← with a label and labels on
  [<div class="<field_class>">] the widget [</div>]
  help text, errors                                                   ← as today, same ids
</fieldset>
  – labels off and the field has a label: the fieldset carries aria-label, the label's text
  – aria-describedby only when group_description is not empty

a single checkbox (component "checkbox", not a group):
<div id="div_<auto_id>" class="fieldset">
  [<div class="<field_class>">]
  <label for="<id_for_label>" class="label [label_class]">the checkbox  label  marker</label>
  [</div>]
  help text, errors
</div>
  – labels off: the checkbox alone, named by aria-label as FS-001 already does

every other field: unchanged
```

The required marker, the help text and the errors are each written once in the template, or
moved to an include of the pack's own if writing them once needs it (ADR 0006 allows the split
when a second place needs them).

The frame's ids do not change: `div_<auto_id>`, `<auto_id>_helptext`, `<auto_id>_error`.

### The widget templates

All four are plain Django templates under `daisyui/widgets/`, reading only the `widget` context
Django's own widget builds.

- **`attrs.html`**: the attribute loop of Django's `attrs.html`, so the others can include it.
- **`group.html`** (radio and checkbox groups): a wrapping `<div>` with the group's id and the
  layout utilities `flex flex-col gap-2`, never the widget's class. Each option is
  `<label class="label" for="<option id>">` holding the option's `<input>` (its type, name,
  value and attributes from the option, so the component class, `checked`, `disabled`,
  `required`, `aria-invalid` and anything a widget set on one option all arrive) and then the
  option's label. Options under a named group sit in a nested
  `<fieldset class="fieldset">` whose `<legend class="fieldset-legend">` is the group's name
  (FR-011).
- **`select_date.html`**: a `<div class="flex gap-2">` holding the three selects in the order
  Django gives them. Each is drawn as Django's `select.html` draws it, plus an `aria-label`
  naming the part: Year, Month or Day, chosen from the end of the part's name by the filter
  `daisyui_date_part`, and marked for translation. A part whose name ends in none of the three
  gets no `aria-label`.
- **`clearable_file_input.html`**: when the field holds a file, Django's "Currently" text and a
  `<a class="link">` to the file; when the field is also optional, a
  `<label class="label" for="<checkbox id>">` holding the removal checkbox with `class="checkbox"`,
  `disabled` when the widget is disabled and `checked` as Django sets it, then Django's "Clear"
  text; then Django's "Change" text. Always the file `<input>` with its attributes. The words are
  the widget's own (`initial_text`, `clear_checkbox_label`, `input_text`) and are not reworded.

### The form-wide alert

`daisyui/errors.html` draws from Django's own list, `form.get_context.errors`, read once with
`{% with %}`. `Form.get_context` already returns the form-wide errors followed by each hidden
field's errors, worded and translated by Django (research R7). The alert appears when that list is
not empty and holds each message once, autoescaped. Everything else about it is unchanged. If
this cannot work when built, the fallback is a tag that builds the same list, and the report says
why.

### Disabled and read-only

No code beyond the above. Django writes `disabled`; daisyUI draws its disabled state from that
attribute for every component the pack uses (research R6). A developer's `readonly` reaches the
input because `as_widget` merges the pack's attributes over the widget's and the pack never
writes `readonly`. The pack adds no class for either state. US6 is the tests that hold this in
place for every input, the removal checkbox, and the README section that states it.

## The demo project

- **`demo/forms.py`**: `ChoiceInputsForm`, one field per input this feature draws: a select, a
  select with named groups, a multiple select, a null-boolean select, a date as three selects, a
  radio group, a checkbox, a checkbox group, a file input (`FileInput`), a clearable file input
  and a hidden input. Its constructor takes the same `required` and `with_help` switches as
  `TextInputsForm`, plus `disabled`. A small form with a text input and a textarea, drawn once
  disabled and once read-only.
- **`demo/views.py`**: the forms-per-state logic of `TextInputsMixin` is shared by both page
  pairs and not copied: one mixin parametrised by the form class, the held values and the
  refused values. The new page has six states (the five of FS-001 plus disabled) and the
  submittable form. "Holding a value" and "disabled" give the clearable file field an object with
  a `url` and a name. The error state's hidden field holds a refused value, so the alert shows a
  hidden field's error.
- **Templates**: `choice_inputs.html` on the shell (Cotton components, as `text_inputs.html`) and
  `choice_inputs_standalone.html` (a whole document, daisyUI's CDN install, no Cotton). Both draw
  the submittable form inside a `multipart` form. Each links to the other.
- **Routes, menu, icon**: `choice-inputs/` and `choice-inputs/standalone/`, one `MenuItem`, one
  icon name registered in `demo/settings.py`.

## Tests

Elements are found by id, `for`, role, name and type, never by wording. A class is asserted only
where it is the daisyUI component or its error modifier.

FS-001 tests that use a select, a checkbox or a file input as "a widget the pack does not cover"
are re-pointed at a widget defined in the tests that subclasses `forms.Input` directly: one
input, a label `for` that is its id, not a group, and in no entry of `FieldInput.components`.
Every frame assertion then holds unedited. The sanctioned edits to tests this feature did not
write are exactly these: the example widget in those three places; `find("select")` becoming
`find("input")` at `tests/test_templatetags/test_daisyui.py:84`; and any test that loads
`{% daisyui_input %}` loading `{% daisyui_field %}` instead, asserting the same thing.

Each new pack module draws through both `{{ form|crispy }}` and `{% crispy form %}` where FR-003
applies, by parametrising the source.

## Story order

US1 → US2 → US3 → US4 → US5 → US6 → US7, sequential, in the feature worktree. Every story edits
the tag module or the frame, so none can run beside another. US1 carries the foundation the
others stand on: the frame's group shape and the widget-copy mechanism.

## Decisions to record

Appended to `decisions.md` from D9, with ADR verdicts settled at convergence: a group is framed
as a fieldset (amends ADR 0006); the pack's own widget templates are drawn through a copy of the
widget, and only when the widget still names Django's template; read-only is the browser's and
nothing imitates it (D2); disabled is drawn by daisyUI from Django's attribute; hidden-field
errors use Django's message; the three layout utilities.
