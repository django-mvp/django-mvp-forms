# Research: choice, boolean and file inputs drawn as daisyUI

Written 2026-10-03 on the feature branch, rebased onto `origin/main` at `c0a2943` (FS-001
merged). Paths under `site-packages/` are the packages this repository's lockfile resolves:
Django 6.1.1 and django-crispy-forms 2.7. Django 5.2.17 and 6.0.8 were read from clean installs
(`uv run --with "django~=5.2.0"`). daisyUI's rules were read from the 5.x stylesheet's component
files; the class list the suite checks against is `tests/data/daisyui-classes.txt` (5.7.47).

The specification has no planning notes and no sketch, so everything below is what the plan needs
settled.

## R1. What FS-001 left in place

- `mvp_forms/templatetags/daisyui.py`: `FieldInput` maps a widget class to a daisyUI component
  through `components` (first `isinstance` match wins, in dict order), adds `w-full`, adds the
  error modifier from `error_modifiers`, and renders through `BoundField.as_widget(attrs=...)`
  (ADR 0004).
- `mvp_forms/templates/daisyui/field.html`: the field frame. A hidden field prints bare. Every
  other field gets a `div.fieldset`, a `label.fieldset-legend` with `for`, the input, the help
  text (`<auto_id>_helptext`) and one error element (`<auto_id>_error`) (ADRs 0005, 0006).
- `mvp_forms/templates/daisyui/errors.html`: the form-wide alert, drawn from
  `form.non_field_errors` only. A hidden field's error is drawn nowhere.
- `tests/test_pack/test_independence.py` checks every class the pack writes against
  `tests/data/daisyui-classes.txt` plus `LAYOUT_UTILITIES`, and that every template a pack
  template names starts with `daisyui/`.
- Several FS-001 tests use a select, a checkbox or a file input as their example of "a widget the
  pack does not cover": `tests/forms.py` `UncoveredWidgetsForm`,
  `tests/test_templatetags/test_daisyui.py` `UncoveredForm` (lines 37 to 41, 77 to 84, 143) and
  `tests/test_pack/test_inputs.py` `TestUncoveredWidgets` (line 135). Those widgets become covered
  here, so those tests need another example. `SplitDateTimeWidget` stays uncovered: FS-001's
  specification gives a field split across text inputs to #8.

## R2. Which Django widgets need what

Read from `site-packages/django/forms/widgets.py` and
`site-packages/django/forms/templates/django/forms/widgets/`.

| Widget | Parent | Django's template | What a class passed as an attribute lands on |
|---|---|---|---|
| `Select` | `ChoiceWidget` | `select.html` | the `<select>` |
| `NullBooleanSelect` | `Select` | `select.html` | the `<select>` |
| `SelectMultiple` | `Select` | `select.html` | the `<select multiple>` |
| `SelectDateWidget` | `Widget` | `select_date.html` → `multiwidget.html` | each of the three `<select>`s |
| `CheckboxInput` | `Input` | `checkbox.html` → `input.html` | the `<input>` |
| `RadioSelect` | `ChoiceWidget` | `radio.html` → `multiple_input.html` | every option **and the wrapping `<div>`** |
| `CheckboxSelectMultiple` | `RadioSelect` | `checkbox_select.html` → `multiple_input.html` | every option **and the wrapping `<div>`** |
| `FileInput` | `Input` | `file.html` → `input.html` | the `<input>` |
| `ClearableFileInput` | `FileInput` | `clearable_file_input.html` | the file `<input>` only; the removal checkbox and the link get nothing |
| `HiddenInput`, `MultipleHiddenInput` | `Input` | `hidden.html`, `multiple_hidden.html` | not drawn with a class |

Consequences:

- `Select`, `NullBooleanSelect`, `SelectMultiple`, `CheckboxInput` and `FileInput` draw correctly
  through Django's own template with the pack's class added, exactly as text inputs do.
- `multiple_input.html:1` writes `widget.attrs.class` on the wrapping `<div>`, so a `radio` or
  `checkbox` class would style the wrapper as a radio button. Its options' labels
  (`input_option.html`) carry no class, and a named group is a bare `<label>` with no `for`. The
  pack needs its own template for a group.
- `clearable_file_input.html` writes the removal checkbox with no class, its label with no class
  and the link with no class. The pack needs its own template for it.
- `select_date.html` gives the three selects no names of their own. A `<select>` inside a
  `<fieldset>` is not named by the legend, so each part needs an `aria-label` for SC-003. Django's
  context carries the parts as `widget.subwidgets`, each with a `name` ending `_year`, `_month` or
  `_day` (`widgets.py`, `SelectDateWidget.year_field` and its siblings). The pack needs its own
  template for it.
- `CheckboxSelectMultiple` subclasses `RadioSelect`, so it has to be looked up first.

## R3. Drawing a widget with a template of the pack's, without writing to the widget

`BoundField.as_widget(widget=None, attrs=None)` (`boundfield.py`, `as_widget`) renders whichever
widget it is given. A shallow copy of the field's widget (`copy.copy`) with `template_name` set to
the pack's template is rendered for one draw and thrown away. The field's own widget is not
touched, so ADR 0004 holds. `as_widget` still builds the attributes, the id, the name and the
value as it does today.

The copy is rendered by the form's renderer. Django's default renderer and `TemplatesSetting` both
load templates from installed apps, so `daisyui/widgets/...` under `mvp_forms/templates/` is
found. Django's `Jinja2` form renderer does not load Django templates. django-crispy-forms itself
only works with Django templates, so this is not a new limit.

FR-004 says a subclass draws as its parent does unless it names a template of its own. The rule
that follows: the pack's template is used only when the widget's `template_name` is still the one
Django's class declares. A subclass that sets another keeps it and gets the component class only.

The pack's widget templates cannot `{% include %}` Django's `attrs.html`: the independence test
requires every template a pack template names to be the pack's own. The attribute loop is four
lines and is written in a `daisyui/widgets/attrs.html` of the pack's.

## R4. Which fields are groups

`Widget.use_fieldset` is `True` for `RadioSelect`, `CheckboxSelectMultiple`, `SelectDateWidget`
and `MultiWidget` (so `SplitDateTimeWidget`), and `False` for every other widget including
`ClearableFileInput`, on Django 5.2.17, 6.0.8 and 6.1.1 alike.

For a field whose widget sets it:

- `BoundField.build_widget_attrs` (`boundfield.py:300`) adds no `aria-describedby`, because the
  attributes are copied onto every option.
- `RadioSelect.id_for_label` returns an empty string with no index, so the frame's
  `<label for>` has nothing to point at. Django's own field template draws a `<fieldset>` with a
  `<legend>` and puts the description on the fieldset.
- `aria-invalid="true"` and `disabled` are still added and reach every option, since
  `option_inherits_attrs` is true for a radio or checkbox group. FR-008 and FR-014 accept
  Django's marking.
- `CheckboxSelectMultiple.use_required_attribute` returns `False`, and
  `ClearableFileInput.use_required_attribute` returns `False` when the field holds a file.
  `RadioSelect` keeps `required` on every radio, which a browser reads as "one of the group". This
  is FR-009 as Django already behaves; the pack adds nothing.

daisyUI's own markup for a group is `<fieldset class="fieldset">` with
`<legend class="fieldset-legend">`, the same two classes the frame already uses on a `div` and a
`label`. So a native fieldset costs no new class. ADR 0006 says the frame's outer element is always
a `div`. Its reason is that the element must never be read from a page variable. Choosing it from
`field.use_fieldset`, which is Django's and not the page's, keeps that reason and changes the
sentence, so ADR 0006 is amended by a new record.

## R5. A single checkbox

daisyUI's documented markup is `<label class="label"><input type="checkbox" class="checkbox" />
Remember me</label>`. `CheckboxInput.id_for_label` returns the id, so the label also carries
`for`. `CheckboxInput.use_fieldset` is `False`, so Django writes `aria-describedby` on the input
itself and the three corrections of ADR 0005 apply unchanged.

## R6. Disabled and read-only

- Django writes `disabled` on the widget when the field is disabled
  (`boundfield.py`, `build_widget_attrs`), and a group copies it to every option.
- daisyUI draws the disabled state from the attribute, with no modifier class:
  `input.css`, `textarea.css`, `select.css` and `fileinput.css` each carry
  `&:is(:disabled,[disabled])`, and `checkbox.css` and `radio.css` carry `.checkbox:disabled` and
  `.radio:disabled`. `label.css` dims a `.label` that holds a disabled input. So every input the
  pack draws with its component class is already in daisyUI's disabled state when Django disables
  it, the text inputs of FS-001 included. What is missing is the removal checkbox of a file field,
  which Django disables but which has no class today, and tests that hold all of it in place.
- daisyUI has no read-only rule for any component. `readonly` on a text input or textarea makes
  the browser show the value, refuse edits, announce the input as read-only and still submit it,
  which is everything FR-023 asks. FR-023 also limits the pack to daisyUI's standard classes, and
  none of them means read-only, so the pack adds no class and the state is the browser's.
- A `readonly` attribute on a select, checkbox, radio or file input is kept as written and does
  nothing, per FR-016.

## R7. An error on a hidden field

`Form.get_context` (`forms.py:239`) adds each hidden field's errors to the form's top errors as
`_("(Hidden field %(name)s) %(error)s")`. That message is in Django's own catalogues, so using
the same msgid through `gettext` gets every translation Django ships. `form.non_field_errors()`
does not include them, which is why they are lost today. The pack's `errors.html` is what
`|crispy`, `{% crispy %}` and `|as_crispy_errors` all draw, so one change there covers FR-013.

## R8. Classes

In `tests/data/daisyui-classes.txt`: `select`, `select-error`, `checkbox`, `checkbox-error`,
`radio`, `radio-error`, `file-input`, `file-input-error`, `label`, `link`, `fieldset`,
`fieldset-legend`. `select.css` handles `[multiple]` (auto height, no arrow), so a multiple select
needs no class beyond `select`.

daisyUI gives `select` and `file-input` the same fixed width as `input`, so ADR 0007's `w-full`
applies to them. A checkbox and a radio button have no width to fill and get none.

daisyUI has no component that stacks a list of options or sets three selects side by side. Under
ADR 0003 those are layout utilities, named in `LAYOUT_UTILITIES`: `flex`, `flex-col` and `gap-2`.

## R9. Text the pack adds

- The hidden-field message, through Django's msgid (R7).
- The names of a date's three selects: "Year", "Month", "Day", marked for translation.

Everything else on the page is Django's or the developer's.

## R10. The demo

`demo/views.py` has `TextInputsMixin` building one form per state for two pages (shell and
standalone). The new page needs the same shape with a sixth state (disabled), a file field that
already holds a file, and a hidden field that fails. The demo has no models, so "holds a file" is
an object with a `url` and a name, which is all `ClearableFileInput` reads
(`widgets.py`, `ClearableFileInput.is_initial`). The submittable form has to be `multipart`.
Icons are registered by name in `demo/settings.py` `EASY_ICONS`, and an unregistered name raises.
