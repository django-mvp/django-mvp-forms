# Research: text inputs drawn as daisyUI

Written 2026-10-03 against `origin/main` at `4851c2e`. Paths under `site-packages/` are the
packages this repository's lockfile resolves: Django 6.1.1, django-crispy-forms 2.7,
django-mvp 0.25.2, crispy-tailwind 1.0.3. Django 5.2.17 and 6.0.8 were read from clean
installs of each.

## Planning notes, answered

### "The pack limits itself to daisyUI's standard classes and modifiers, so that a host page loading daisyUI's full CDN build needs no build step."

**Adopted, with the maintainer's ruling of 2026-10-03 on top.** Every input, label, help text,
error and alert is built from daisyUI component classes and modifiers. A plain Tailwind layout
utility is allowed only where daisyUI has no component for the job, because daisyUI's documented
CDN install loads Tailwind's browser build beside the stylesheet. This feature needs none: the
field frame is daisyUI's `fieldset`, and nothing here is laid out side by side. See R5 and D9.

### "Pack templates are plain Django templates and never use django-cotton or daisy-cotton."

**Adopted.** `{% include %}` between the pack's own templates is used and expected. A test reads
every distributed template and fails on a Cotton tag, load or parent (R8).

### "The package never depends on django-mvp at runtime and never imports from it."

**Adopted.** Nothing in `mvp_forms/` imports `mvp`. A test reads the package's imports, and
another draws a form with only `crispy_forms` and `mvp_forms` installed (R8).

### "No support for carrying layouts over from other packs."

**Adopted.** Nothing here reads another pack's names or classes.

### "Each feature adds its own demo page or pages and its own README public-surface entry."

**Adopted.** One page on the shell, one standalone, and the README's first public-surface entry.

### "The demo project currently selects the `tailwind` pack and installs `crispy_tailwind`. Check what django-mvp's own pages look like once the setting changes."

**Adopted.** The demo selects `daisyui` and drops `crispy_tailwind` from `INSTALLED_APPS`
(it stays in the environment as a dependency of django-mvp). django-mvp's sign-in page does not
draw through crispy at all: `mvp/templates/mvp/account/login.html:17-28` builds its fields with
its own `c-form.field` component. The only shell templates that call crispy are
`cotton/form/render.html` and `list_view.html`, and the demo has no page using either. No shell
template loads a `crispy_tailwind` tag library. The existing sign-in tests stay as the check.

### "Django 5.0 and later put `aria-describedby` and `aria-invalid` on the widget themselves, and the ids they point at follow a fixed pattern. Check each supported Django version."

**Adopted.** See R2. The three supported versions behave identically.

### "FR-026 needs something to compare against. A list of the classes in daisyUI's CDN stylesheet has to come from somewhere a test can read without the network."

**Adopted.** See R5: a text file of class names taken from the published stylesheet, kept beside
the tests.

### "Keep the frame's template paths and context stable once they are chosen, and say what they are in the plan."

**Adopted.** The plan's section *The field frame contract* is that statement.

## R1. How django-crispy-forms asks a pack to draw

All in `site-packages/crispy_forms/`.

| Asked through | Template looked up | Context given | Source |
|---|---|---|---|
| `{{ form\|crispy }}` | `<pack>/uni_form.html` | `form`, `field_template` (`<pack>/field.html`), `form_show_errors=True`, `form_show_labels=True`, `label_class`, `field_class` | `templatetags/crispy_forms_filters.py:27-61` |
| `{{ form\|as_crispy_errors }}` | `<pack>/errors.html` | `form` only | `crispy_forms_filters.py:64-83` |
| `{{ form.field\|as_crispy_field }}` | the helper's `field_template`, else `<pack>/field.html` | `field`, `form_show_errors`, `form_show_labels`, `label_class`, `field_class`, plus the helper's attributes when the form has one | `crispy_forms_filters.py:86-118` |
| `{% crispy form %}` | `<pack>/whole_uni_form.html` | everything in `get_response_dict`: `form_tag`, `form_method`, `flat_attrs`, `disable_csrf`, `form_show_errors`, `form_show_labels`, `label_class`, `field_class`, `field_template`, `form_error_title`, `help_text_inline`, `error_text_inline`, `include_media`, `inputs`, `csrf_token` | `templatetags/crispy_forms_tags.py:164-212, 225-239` |

Two paths reach the field template from the tag. A form with no `helper` attribute gets a bare
`FormHelper()` with no layout, so `whole_uni_form.html` has to loop over the fields itself
(`crispy_forms_tags.py:123`, `:143`). A form whose helper was built as `FormHelper(form)` has a
default layout, and each field arrives through `render_field`, which renders
`<pack>/field.html` with the node's context plus `field`, `labelclass` and `flat_attrs`
(`utils.py:29-139`). Both paths have to produce the same markup (FR-003).

The pack name is checked only by the tag, against `CRISPY_ALLOWED_TEMPLATE_PACKS`
(`crispy_forms_tags.py:258-266`). The pack adds nothing to that check.

The formset templates (`uni_formset.html`, `whole_uni_formset.html`, `errors_formset.html`) and
`inputs.html` for a helper's buttons belong to later features and are not written here.

## R2. What Django puts on the input, in every supported version

`BoundField.build_widget_attrs` and `BoundField.aria_describedby` are the same in Django 5.2.17,
6.0.8 and 6.1.1 (`django/forms/boundfield.py`, `build_widget_attrs` and the property below it):

- `required` when the field is required, the widget allows it and the form's
  `use_required_attribute` is on.
- `disabled` when the field is disabled.
- `aria-invalid="true"` when the field has errors and is not hidden.
- `aria-describedby`, unless the caller or the widget already set one: `<auto_id>_helptext` when
  the field has help text, then `<auto_id>_error` when it has errors. Nothing when the form has
  no `auto_id`.

So the ids are fixed: one element with id `<auto_id>_helptext`, and **one** element with id
`<auto_id>_error` that holds every error message. Django's own error list uses the same id
(`django/forms/templates/django/forms/errors/list/ul.html`). The pack emits exactly those two
ids and invents none (FR-018). crispy-tailwind's per-message ids (`error_1_id_x`) do not match
what Django points at and are not copied.

Three cases where Django's attributes and the page would disagree, each handled by the pack:

1. **Errors turned off by the helper while the field is invalid.** Django still names
   `<auto_id>_error`, which the pack does not draw. The pack passes its own `aria-describedby`
   naming the help text only. When there is no help text either, an empty value does not stop
   Django adding its own (`if not attrs.get("aria-describedby")`), so in that one case the pack
   builds the attributes with `build_widget_attrs`, drops the description, and renders the widget
   itself.
2. **A form with `use_required_attribute = False`.** Django omits `required`. The pack adds
   `aria-required="true"` so the requirement still reaches assistive technology (spec edge case).
3. **Labels turned off.** The pack adds `aria-label` carrying the field's label (FR-024).

## R3. Adding the pack's class without touching the widget

crispy's own `{% crispy_field %}` tag writes into `widget.attrs` and appends the widget's class
name in lower case, such as `textinput` (`templatetags/crispy_forms_field.py:100-125`). That
class is in no daisyUI build, and the write stays on the form instance.

`BoundField.as_widget(attrs=...)` merges the given attributes over the widget's own for one
render (`Widget.build_attrs`: `{**base_attrs, **extra_attrs}`), so the pack reads the widget's
class, adds its own beside it, and passes the result. Nothing is mutated and every other
attribute the developer set arrives unchanged (FR-007, FR-008).

**Decision:** the pack ships one template tag of its own, `{% daisyui_input field %}`, backed by
one class. It is the only Python in the feature.

## R4. Which widgets are covered

| Widget | Drawn as | Error modifier |
|---|---|---|
| `TextInput` and its subclasses `DateInput`, `TimeInput`, `DateTimeInput` | `input` | `input-error` |
| `EmailInput`, `URLInput`, `NumberInput`, `PasswordInput` | `input` | `input-error` |
| `Textarea` | `textarea` | `textarea-error` |
| anything else | no pack class, inside the same frame | none |

The check is `isinstance`, so a project's subclass of a covered widget is covered. The input's
`type` is never read or changed (decision D3): `TextInput(attrs={"type": "date"})` is a
`TextInput` and is drawn as an `input`.

Django also ships `SearchInput`, `TelInput` and `ColorInput`. The specification does not list
them, so they fall under "anything else" here. Whether they should be drawn as daisyUI inputs is
filed as an open question.

## R5. daisyUI: the classes and the list to check against

Read from `https://cdn.jsdelivr.net/npm/daisyui@5/daisyui.css`, which resolved to daisyUI
**5.7.47** on 2026-10-03. Every class this feature needs is defined there: `fieldset`,
`fieldset-legend`, `label`, `input`, `input-error`, `textarea`, `textarea-error`, `alert`,
`alert-error`, `alert-soft`, `text-error`. Tailwind utilities such as `w-full` and `sr-only` are
not.

django-mvp's packaged stylesheet (`mvp/static/css/django-mvp.css`) defines the same classes, so
the shell page needs nothing extra.

The frame follows daisyUI's documented fieldset: a block carrying `fieldset`, a caption carrying
`fieldset-legend`, the input, and a line of small text carrying `label`. The caption is a real
`<label for>` and the block is a `div`, because `<legend>` cannot be tied to one input.

**The list.** `tests/data/daisyui-classes.txt` holds every class selector in that stylesheet,
one per line, with a header naming the version and the address. A test collects the classes the
pack put in its output and fails on any that is not in the file. Refreshing it for a new daisyUI
release is one download.

## R6. Escaping

crispy-tailwind prints the label and help text with `|safe`. The pack prints the label, the
help text and each error with no filter, so the template layer escapes them and keeps markup
only where the author marked it safe (FR-016, Article V).

## R7. The demo project

- `MVPTemplateView` supplies the shell's title and breadcrumbs. A page needs a view, a route, a
  template extending `page_view.html`, a `MenuItem`, and an icon name registered in
  `EASY_ICONS`, since an unregistered name raises.
- The gallery puts several forms of one class on a page, so each gets a prefix. That is also the
  live case for FR-017.
- The standalone page extends nothing from django-mvp and uses no Cotton tag. It loads daisyUI's
  stylesheet and Tailwind's browser build from the CDN, which is daisyUI's documented install.
- `beautifulsoup4` 4.15 arrives with the shared test bundle, so tests can read the rendered page
  as a tree.

## R8. Proving independence

- **Drawing without django-mvp:** a test overrides `INSTALLED_APPS` to `crispy_forms` and
  `mvp_forms` with a bare template engine and draws a form. Django rebuilds its template engines
  when either setting changes.
- **Templates:** a test walks `mvp_forms/templates/` and fails on `{% load cotton`, a `<c-` tag,
  or an `extends`/`include` of a path outside `daisyui/`.
- **Imports:** a test parses every module under `mvp_forms/` and fails on an import of `mvp`,
  `django_cotton` or `daisy_cotton`. `deptry` covers the declared dependencies.

## R9. Text the pack adds

None. The required marker is an asterisk hidden from assistive technology, with the requirement
carried by `required` or `aria-required`. With no user-facing string, FR-030 is met with no
catalogue, and Article VIII says not to ship an empty `locale/`.
