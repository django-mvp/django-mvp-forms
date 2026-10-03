# ADR 0012 — The pack's own widget templates are drawn through a copy of the widget

**Status:** accepted

## Decision

Most widgets are drawn by Django's own template with the pack's class added, as ADR 0004
describes. Three are drawn from templates of the pack's, under `daisyui/widgets/`:

- a radio group and a checkbox group, from `group.html`
- a date drawn as three selects, from `select_date.html`
- a file input that can hold a file, from `clearable_file_input.html`

`FieldInput.templates` maps the Django widget class to the pack's template. `FieldInput` makes a
shallow copy of the field's widget, points the copy's `template_name` at the pack's template and
draws the copy through `BoundField.as_widget`. The field's own widget is never written to.

The pack's template is used only while the widget still names the templates its Django class
declares: `template_name`, and `option_template_name` where the class has one. A subclass that
names a template of its own is drawn by that template and gets the pack's class only.

A later feature that needs its own markup for a widget adds a template and an entry. It does not
subclass the widget and does not ask the host project to swap one.

The frame gets a field's `FieldInput` from `{% daisyui_field field as drawn %}`. That tag
replaces `{% daisyui_input %}`, which ADR 0004 names. The rest of ADR 0004 stands.

The form's renderer has to be one that loads Django templates from installed apps. Django's
default renderer and `TemplatesSetting` both do.

## Why

A class is not always enough. Django's group template writes the widget's class on the wrapping
element as well as on every option, so daisyUI's `radio` class would style the wrapper as a
radio button. It gives an option's label, a file field's removal checkbox and the link to the
current file no class at all, and it gives a date's three selects no names of their own.

A copy keeps ADR 0004's promise. Setting `template_name` on the form's widget would leave the
change on the form after the draw, which is what that record rules out.

Checking the template names is what lets a host project's own widget keep its own template,
while a plain subclass still draws as its parent does.

The frame now asks which shape to draw before it draws the input, so it needs the object and not
only its markup. The frame was the old tag's only caller, and keeping both would have left a tag
that nothing uses.

## Revisit if

Django lets a caller name the template for one render, or a covered widget gains a third
template attribute.
