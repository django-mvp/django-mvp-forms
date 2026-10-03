# Research: layout objects that decorate a field

Read against `origin/main` at `23b5933` (FS-001, FS-002, FS-003 and FS-005 merged), with
django-crispy-forms 2.7 and Django 6.1.1 as `uv sync` resolves them. Paths under
`crispy_forms/` and `django/` are in the project's virtualenv. The daisyUI rules quoted are from
the 5.7.47 CDN stylesheet, the version `tests/data/daisyui-classes.txt` was listed from.

The specification has no planning notes and no sketch, so there is nothing of either to answer.

## R1. What django-crispy-forms asks the pack for

Each of the nine is a class in django-crispy-forms that names a template under the pack and
renders it through `render_field` (`crispy_forms/utils.py:29`), which puts `field` (the bound
field), `flat_attrs` and the layout object's extra context into a flattened copy of the page's
context (`utils.py:127-137`).

| Layout object | Template it asks for | Extra context | Source |
|---|---|---|---|
| `PrependedText`, `AppendedText`, `PrependedAppendedText` | `layout/prepended_appended_text.html` | `crispy_prepended_text`, `crispy_appended_text`, `input_size`, `active`, `wrapper_class`, always all five | `bootstrap.py:61`, `:91-112` |
| `InlineCheckboxes` | `layout/checkboxselectmultiple_inline.html` | `inline_class`, and `wrapper_class` when set | `bootstrap.py:354-357` |
| `InlineRadios` | `layout/radioselect_inline.html` | the same | `bootstrap.py:400-403` |
| `FieldWithButtons` | `layout/field_with_buttons.html` | `div` (the layout object), `buttons` (already drawn) | `bootstrap.py:453-495` |
| `UneditableField` | `layout/uneditable_input.html` | `wrapper_class` when set | `bootstrap.py:1005-1009` |
| `InlineField` | `layout/inline_field.html` | `wrapper_class` when set | `bootstrap.py:1052` |
| `MultiWidgetField` | `field.html`, the ordinary field template | `wrapper_class` when set | `layout.py:957-1001`, `:918` |

So the feature is six new templates. `MultiWidgetField` asks for no template of its own.

Attributes given to a layout object (`css_class`, extra HTML attributes, and the per-part
attribute sets of `MultiWidgetField`) are written by django-crispy-forms onto the field's widget
before the template runs (`utils.py:71-91`). A single dictionary goes to every part, a sequence
goes one per part by `zip`, so a short sequence leaves the later parts alone and raises nothing.
FR-021 is therefore django-crispy-forms' own behaviour: the pack's job is not to lose those
attributes when it draws the parts (R6).

`UneditableField` sets `attrs = {"class": "uneditable-input"}` (`bootstrap.py:1008`), so that
class name lands on the widget. daisyUI does not define it.

`input_size` and `active` are passed to the template and nothing more. A template that does not
read them satisfies FR-027.

## R2. Attached text: daisyUI's label inside an input

daisyUI 5 attaches text to an input by putting the `input` class on a wrapping `<label>` and the
text in a `<span class="label">` beside a bare `<input>`. The same works for `select`. The rules
are `.input input{appearance:none;background-color:#0000;border:none;width:100%;…}`,
`.select select{…border-style:none…}` and `.label:is(.input>*,.select>*){…&:first-child{border-inline-end:…}&:last-child{border-inline-start:…}}`.

That fixes three things:

- The component class, the width and the error modifier go on the wrapper, and the inner input
  carries none of them. `daisyui/field_body.html` draws the input through `FieldInput.render`,
  which today always adds the class, so `FieldInput` needs a way to draw the input bare.
  A class of `False` in the attributes passed to `as_widget` drops the attribute altogether
  (`django/forms/templates/django/forms/widgets/attrs.html`).
- A wrapping `<label>` names the input, together with the field's own `<label for>`. The
  prepended or appended text becomes part of the input's accessible name, which is what FR-004
  asks for, with no extra id and without competing with the `aria-describedby` Django writes.
- Only `input` and `select` have this markup. A textarea, a checkbox, a radio group, a file input
  and a multi-widget field do not, so on those the field is drawn as it would be undecorated
  (FR-025).

**Rejected:** tying the text to the input with `aria-describedby` and an id per attachment. Django
writes `aria-describedby` itself for help text and errors and steps aside as soon as the widget
or the caller supplies one (`django/forms/boundfield.py`, `build_widget_attrs`), so the pack would
have to rebuild the whole list for every state.

**Rejected:** daisyUI's `join` with a separate element for the text. It is the markup for joining
controls, the text would need a border and padding of its own from utilities, and the README
says stock daisyUI markup wins.

## R3. Field with buttons: daisyUI's join

`join` is daisyUI's way to attach controls. In 5.7.47 the container sets the corner variables on
its direct children (`.join{…@scope(&){…& :where(:scope>:first-child){--join-ss:var(--radius-field);…}`)
and `input`, `select` and `btn` read them
(`border-start-start-radius:var(--join-ss,var(--radius-field))`). So a button inside a `join`
is squared off on its joined side with no class added to it. `join-item` adds only the one-pixel
overlap that hides the doubled border.

django-crispy-forms draws the buttons before the template runs and hands them over as one string
(`bootstrap.py:462-476`), so the template cannot add a class to them. It does not need to: the
pack puts `join-item` on the input, which it does draw, and leaves the buttons exactly as FS-003
draws them (FR-012). A developer who wants the doubled border gone writes
`css_class="join-item"` on the button.

**Rejected:** drawing each button a second time from a copy carrying `join-item`. A button's
`render` runs its content through the template engine and stores the result back on the object
(`bootstrap.py:559`, `layout.py:253`), so a second render would evaluate already-rendered text as
a template. That is a way for text a person typed to be run as template code.

`FieldWithButtons` is a `Div`, so `css_id`, `css_class` and its extra attributes belong to the
group: `div.css_id`, `div.css_class` and `div.flat_attrs` go on the `join` element (FR-024).
When its first item is a `Field`, that object's attributes are already on the widget (R1), which
is FR-013.

## R4. Inline groups

FS-002 draws a radio group and a checkbox group from `daisyui/widgets/group.html`, chosen by
`FieldInput.templates` and drawn through a copy of the widget (ADR 0012). The options sit in a
`div` with `flex flex-col gap-2`. The inline arrangement is the same options in a `div` with
`flex flex-wrap gap-4`, all three already in `LAYOUT_UTILITIES`. A widget template sees only
`widget`, so the arrangement cannot be a flag in its context: it is a second template,
`daisyui/widgets/inline_group.html`, and the options move to a shared
`daisyui/widgets/group_options.html` that both include.

Everything else about the group (the fieldset and legend, the description, the disabled options,
the error modifier, a widget that names its own template) is FS-002's and is reached by the
same code, so FR-010 and FR-011 hold by construction and are tested against the inline templates.

A field with no choices, or with a widget that is not a radio or checkbox group, has no group
template and is drawn as it would be undecorated.

## R5. `wrapper_class` and what the frame reads

FR-024 requires `wrapper_class` to do what django-crispy-forms documents: put a class on the
element around the field. Six of the nine take it, and `MultiWidgetField` draws through
`field.html`.

ADR 0006 says the frame reads four names from the context and takes no wrapper class, because
`{% crispy %}` hands the template a copy of the page's context and any bare name could be the
page's. Its "Revisit if" asks a feature that needs an extra class on the frame to pass it by a
route that does not read a bare page variable.

No such route exists. `render_field` flattens the context before the template sees it
(`utils.py:137`), the layout object is not in it for a `Field` subclass, and a `Field` adds
`wrapper_class` only when it was given one (`layout.py:941-942`). The template cannot tell a
layout object's `wrapper_class` from a page's.

The plan therefore has the tag read `wrapper_class` from the context and hand it to the frame as
a class. What made ADR 0006 refuse bare names was `tag`, a name used as an element: a class is
written inside an attribute and escaped, so the worst a page variable called `wrapper_class` can
do is add a class to every field's frame. This amends ADR 0006 and gets an ADR of its own.

A side effect is that `wrapper_class` on a plain `Field` now works too, which is what
django-crispy-forms documents.

## R6. Multi-widget fields

`forms.MultiWidget.use_fieldset` is true, so the frame already draws a `SplitDateTimeField` as a
fieldset with a legend, one help text and one error element. What is missing is the parts:
`FieldInput.components` has no entry for a multi-widget, so each part is drawn without a class
and without a name.

`MultiWidget.get_context` builds each part from `build_attrs(part.attrs, attrs)`, so a class
passed to `as_widget` would replace every part's own class, including one `MultiWidgetField`
gave it. The parts have to be classed one by one. ADR 0012 already draws through a copy of the
widget and never writes to it. `MultiWidget.__deepcopy__` copies the parts, so the copy's parts
can each take the pack's class for their own kind, after the part's own classes, and nothing on
the form's widget changes.

Each part needs a name (SC-003). The parts of a `SplitDateTimeWidget` are a date and a time, and
the pack names them so, translatably, as FS-002 names a date's three selects. The parts of any
other multi-widget have no kind the pack can know, so each takes the field's label. A part that
already has an `aria-label`, which is exactly what `MultiWidgetField` lets a developer give it,
keeps it.

`SplitHiddenDateTimeWidget` is hidden and never reaches this code.

## R7. Uneditable field

ADR 0013 draws the disabled state from the `disabled` attribute and adds no class. `as_widget`
merges the attributes it is given over the widget's for one render, and a group copies them to
every option, so passing `disabled` there draws any input, select, checkbox, radio group or file
input disabled, with its value, without touching the form field. The form field is not disabled,
so the browser leaves the value out and Django validates what is left, which is FR-016's warning.

`uneditable-input` (R1) is dropped when the input's classes are built.

## R8. Inline field

`FieldInput` already draws an input with no visible label and names it by `aria-label`
(`requires_aria_label`), for a helper with `form_show_labels = False`. An inline field is that,
for one field, plus a placeholder taken from the label when the widget has none. A single
checkbox keeps its label (FR-020), and a group keeps the name FS-002 gives a group with labels
off. Help text and errors are the frame's, unchanged (FR-019).

A placeholder means something on an `input` and a `textarea` only. Other widgets get none.

## R9. Text the developer writes is drawn as markup

Decision D4 in `decisions.md`. The two texts are drawn with `|safe`. Everything else in these
templates is escaped by the template layer. The README says the text is markup and must be
escaped first when it is built from anything a person typed (FR-008).

## R10. What needs no new dependency, script or stylesheet

Nothing does. Classes used and not yet in a pack template: `join`, `join-item` and `label` inside
an `input`, all in `tests/data/daisyui-classes.txt`. No Tailwind utility is added: `flex`,
`flex-wrap`, `gap-4` and `w-full` are already listed in `LAYOUT_UTILITIES`.
