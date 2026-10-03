# Implementation Plan: text inputs drawn as daisyUI

**Branch**: `001-text-inputs` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-text-inputs/spec.md`. Evidence for every claim
below about django-crispy-forms, Django and daisyUI is in [research.md](research.md).

## Summary

The package gains a template pack named `daisyui`: five plain Django templates under
`mvp_forms/templates/daisyui/` and one template tag. django-crispy-forms finds the templates by
name. The tag draws a field's widget with the pack's class beside the developer's own, without
writing to the widget. The field frame emits the two ids Django already points the input at, so
the label, help text and errors are announced with the field. The demo project selects the pack
and gains a page on the shell and a standalone page. The README gains its quickstart and first
public-surface entry.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms 2.7 or later. No new
dependency.

**Storage**: none

**Testing**: pytest with pytest-django; `beautifulsoup4` from the shared test bundle to read
rendered markup

**Target Platform**: any Django project whose pages load daisyUI 5

**Project Type**: library (a Django app) with an undistributed demo project

**Constraints**: plain Django templates only; no import of django-mvp; daisyUI component classes
and modifiers only; no stylesheet, no script, no class of the pack's own

**Scale/Scope**: five templates, one tag module, two demo pages

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Test-first. Tests read rendered markup for the element, the ids, the attributes and the component classes, which the testing standard counts as behaviour for a published pack. No test asserts wording, width or order of decoration. |
| II Simplicity | No new dependency. One tag, because crispy's own writes a class daisyUI does not define (research R3). |
| III Anti-abstraction | The frame is one template. Help text and errors are written inside it, and are split out by the first later feature that has a second caller for them. |
| IV Integration-first | Every pack test draws through `\|crispy`, `{% crispy %}`, `\|as_crispy_field` or `\|as_crispy_errors`, as a host project does. |
| V Security | Labels, help text and errors go through autoescaping with no `\|safe`. |
| VI Documentation | README and CHANGELOG change in the story that introduces the pack's name. |
| VII Dependencies | None added. `crispy-tailwind` stops being used by the demo. |
| VIII i18n | The pack adds no text of its own (research R9), so there is no catalogue. |
| X Cohesion | The tag's logic is one class, `FieldInput`. The registered tag is a thin wrapper. |
| XI Compatibility | The pack name and the template paths below become public interface. |
| XIII Plain templates | Checked by tests (research R8). |
| XIV Stock daisyUI | The frame is daisyUI's fieldset. Under the ruling recorded as D9, Tailwind layout utilities are allowed only where daisyUI has no component, and this feature needs none, so every emitted class is checked against the CDN build. |

No violations, so no complexity table.

## Project Structure

```text
mvp_forms/
├── templates/daisyui/
│   ├── uni_form.html            # a form's errors and fields (the filter)
│   ├── whole_uni_form.html      # the form element and CSRF token (the tag)
│   ├── display_form.html        # a laid-out form, or uni_form.html
│   ├── errors.html              # form-wide errors
│   └── field.html               # the field frame
└── templatetags/
    ├── __init__.py
    └── daisyui.py               # FieldInput and {% daisyui_input %}

demo/
├── forms.py                     # TextInputsForm
├── views.py                     # the two pages
├── templates/demo/text_inputs.html
└── templates/demo/text_inputs_standalone.html

tests/
├── data/daisyui-classes.txt     # class names in daisyUI's CDN stylesheet
├── forms.py                     # the forms the tests draw
├── conftest.py                  # fixtures, one of which parses a rendered fragment
├── test_templatetags/test_daisyui.py
├── test_pack/                   # one module per story, drawn through crispy
│   ├── test_inputs.py
│   ├── test_field_frame.py
│   ├── test_form.py
│   └── test_independence.py
└── test_demo.py
```

`tests/test_pack/` tests templates, so it is declared in `[tool.forge.conformance]
non-mirror-paths`. `tests/test_templatetags/test_daisyui.py` mirrors the tag module.

## The pack

### `{% daisyui_input field %}` and `FieldInput`

`mvp_forms/templatetags/daisyui.py` holds one class and one tag.

`FieldInput(field, show_labels=True, show_errors=True)` wraps a bound field for one render:

- `component` is the daisyUI class for the widget: `input` for `TextInput` (and so the date and
  time widgets), `EmailInput`, `URLInput`, `NumberInput` and `PasswordInput`; `textarea` for
  `Textarea`; nothing for any other widget. The mapping is a class attribute, matched with
  `isinstance`, so a later feature adds its widgets by adding entries.
- `css_class` is the widget's own class, then the component, then `<component>-error` when the
  field has errors and errors are shown. No class is repeated.
- `attrs` is what the pack adds for this render: `class` when there is one; `aria-required` when
  the field is required and the form's `use_required_attribute` is off; `aria-label` when labels
  are off, the field has a label and the widget carries no `aria-label`; and `aria-describedby`
  only in the case below. The `aria-label` value is the label with its tags stripped, as an
  ordinary string, so a label marked safe cannot break out of the attribute.
- **No ARIA attribute is added when `field.use_fieldset` is true.** Django copies a grouped
  widget's attributes onto every option, and withholds its own description from those widgets
  for the same reason. Grouped widgets are a later feature's.
- `render()` returns `field.as_widget(attrs=self.attrs)`.

**Errors turned off.** When errors are off and the field has errors, Django would name an error
element the pack does not draw. `attrs` then carries `aria-describedby` naming the help text
only. If there is no help text, `render()` builds the attributes with
`field.build_widget_attrs`, removes `aria-describedby`, sets the id the way `as_widget` does,
and calls the widget's `render` itself. That is the only case that bypasses `as_widget`, and it
has its own test. A widget that already carries the developer's `aria-describedby` is left
alone in every case.

The tag is `@register.simple_tag(takes_context=True)`, reads `form_show_labels` and
`form_show_errors` from the context (both default to on) and returns `FieldInput(...).render()`.

A hidden field is never passed to the tag: the frame prints it bare.

### The field frame contract

These paths and context names are public interface from this feature on. Later features draw
through them and do not redefine them.

**`daisyui/field.html`**, given `field` and optionally `form_show_labels`, `form_show_errors`,
`label_class`, `field_class`:

```text
hidden field → the widget alone
otherwise:
<div id="div_<auto_id>" class="fieldset">
  <label for="<id_for_label>" class="fieldset-legend [label_class]">
    label text  <span aria-hidden="true" class="text-error">*</span>   ← required only
  </label>                                             ← only with a label and labels on
  [<div class="<field_class>">]  {% daisyui_input field %}  [</div>]   ← holder only with a field_class
  <p id="<auto_id>_helptext" class="label">help text</p>            ← only with help text
  <div id="<auto_id>_error" class="text-error">                      ← only with errors, and errors on
    <p>one message</p> …
  </div>
</div>
```

- The frame's element is always a `div`. It reads no element name and no wrapper class from the
  context: through `{% crispy %}` the whole page context reaches this template, so an
  unqualified name there would be the host page's to set. A later feature that needs either
  adds it by a route that does not read a bare page variable.
- Every id is written only when the form has an `auto_id`, and the label's `for` only when
  `id_for_label` is not empty, so a form with ids turned off emits none and cannot repeat one.
- Help text, and each error message, is printed autoescaped.
- `label_class` and `field_class` are the host project's own and are added beside the pack's.
- `help_text_inline` and `error_text_inline` are read by nothing.

### The form templates

- **`daisyui/errors.html`**, given `form` and optionally `form_error_title`: when the form has
  form-wide errors, one `<div role="alert" class="alert alert-error alert-soft">` holding the
  title when given and each error once. Nothing otherwise.
- **`daisyui/uni_form.html`**: the form's media when `include_media`, `errors.html` when
  `form_show_errors`, then each field through `field_template`.
- **`daisyui/display_form.html`**: for a laid-out form, media, errors and `form.form_html`;
  otherwise `uni_form.html`.
- **`daisyui/whole_uni_form.html`**: `<form {{ flat_attrs }} method="…">` with the multipart
  attribute when the form needs it, the CSRF token when the method is post and it is not
  disabled, then `display_form.html`. The form element is omitted when `form_tag` is off. A
  helper's buttons are a later feature's and are not drawn.

`flat_attrs` is built by django-crispy-forms from the helper and is already escaped by
`django.forms.utils.flatatt`.

## The demo project

- **Settings:** `CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]`, `CRISPY_TEMPLATE_PACK =
  "daisyui"`, `crispy_tailwind` removed from `INSTALLED_APPS`, and an icon name registered for
  the new page.
- **`demo/forms.py`:** `TextInputsForm`, one field of each covered kind. Its constructor takes
  `required` and `with_help` to switch every field at once, and its `clean()` always raises a
  form-wide error with a code, so a submission shows both kinds of error.
- **`demo/views.py`:** `TextInputsMixin` builds the forms, each with its own prefix: the
  submittable form, and one each for empty, holding a value, required, with help text, and with
  an error (bound to invalid data). `get` and `post` both render the page; `post` binds the
  submittable form. `TextInputsView` puts the mixin on `MVPTemplateView`;
  `StandaloneTextInputsView` puts it on Django's `TemplateView`.
- **Templates:** `text_inputs.html` extends `page_view.html` and uses the shell's Cotton
  components for its sections. `text_inputs_standalone.html` is a whole HTML document with
  daisyUI's stylesheet and Tailwind's browser build from the CDN, no Cotton tag and nothing from
  django-mvp. Both wrap the submittable form in their own `<form>` with a `btn` button and draw
  it with `{{ form|crispy }}`, with `{% csrf_token %}` inside that element; the states are drawn
  the same way. The shell page links to the
  standalone page.
- **Menu:** one `MenuItem` for the shell page.

## Tests

Elements are found by id, by `for`, by role and by name, never by wording. Classes are asserted
only where they are the daisyUI component or its error modifier.

- **`test_templatetags/test_daisyui.py`** — `TestFieldInput`: the component per widget,
  parametrised over the nine kinds; a subclass of a covered widget; an uncovered widget; the
  developer's class kept and not repeated; the error modifier with and without errors shown;
  `aria-required` only when the form turns the required attribute off; `aria-label` only with
  labels off, with tags stripped; no ARIA attribute on a grouped widget; the
  description with errors off, with and without help text; the widget's `attrs` unchanged after a
  render.
- **`test_pack/test_inputs.py`** (US1): each covered kind drawn through the filter carries its
  component class; the tag draws the same markup as the filter, with and without a default
  layout; bound values, and the password left empty unless `render_value`; developer attributes
  kept; one field drawn through `as_crispy_field` equals the same field inside the form; an
  uncovered widget keeps its place, its label, help text and errors; a form with no fields.
- **`test_pack/test_field_frame.py`** (US2): label `for` equals the input's id; the marker on
  required fields only, and `required` or `aria-required` on the input; help text and error ids
  equal what the input's `aria-describedby` names, for help only, errors only, both and neither;
  `aria-invalid` and the error modifier on an invalid field; several errors all drawn inside the
  one error element; markup in an unsafe label, help text and error escaped, and safe help text
  kept; two prefixed forms on one page share no id and every reference resolves; an empty label
  leaves no label element; a form with `auto_id=False` emits no id.
- **`test_pack/test_form.py`** (US3): form-wide errors drawn once with `role="alert"` through
  the filter, the tag and `as_crispy_errors`; none drawn when there are none; the form element,
  its method, action, id, class and extra attributes; the CSRF token present, and absent when
  disabled or when the method is get; no form element with `form_tag` off; labels off leaves no
  label and gives each input an `aria-label`; errors off draws no field or form-wide error and no
  dangling description; `label_class` and `field_class` on every label and holder.
- **`test_pack/test_independence.py`** (US4): every class the pack emits across the states
  above is in `tests/data/daisyui-classes.txt`; a form draws with only `crispy_forms` and
  `mvp_forms` installed, with django-crispy-forms' four cached template loaders cleared on the
  way into and out of that override, since they hold templates compiled by the full engine; no distributed template uses Cotton; no module imports django-mvp or
  Cotton; the package ships no static files.
- **`test_demo.py`** (US5): both pages respond; the sidebar links the shell page; every covered
  kind appears in every state; a submission comes back with field errors and a form-wide error;
  the standalone page carries the CDN stylesheet and no shell markup; on both pages every input
  has a label, every described id exists and no id repeats (SC-003).

## Story order

US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree. Every story edits
`field.html` or the tag, so they cannot run side by side. Each story's documentation lands with
it: US1 writes the README's quickstart and public-surface entry and the CHANGELOG line, because
it introduces the pack's name.

## Decisions to record

Appended to `decisions.md` as D9 to D13, with ADR verdicts settled at convergence: the class
policy as ruled on 2026-10-03; the pack's own input tag in place of crispy's; ids that follow
Django's; the frame contract; no text of the pack's own.
