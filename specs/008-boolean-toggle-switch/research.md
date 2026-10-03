# Research: booleans drawn as a checkbox, toggle or switch

Done on 2026-10-03 against `origin/main` at `a50b13e`, after FS-001, FS-002, FS-003, FS-005,
FS-006 and FS-007 merged. FS-004 is being built at the same time and is not on main.

## Planning notes, answered

Each of the maintainer's notes in `planning-notes.md`, under its own words.

- **"The pack limits itself to daisyUI's standard classes and modifiers."** Adopted. The feature
  writes `toggle`, five size modifiers and eight colour modifiers, all in daisyUI's CDN stylesheet
  (`tests/data/daisyui-classes.txt:2900-2913`). It writes no class of its own.
- **"Pack templates are plain Django templates."** Adopted, and it costs nothing: no template in
  the pack changes (R3).
- **"This package never depends on django-mvp at runtime and never imports from it."** Adopted.
  The change is in `mvp_forms/choices.py` and `mvp_forms/templatetags/daisyui.py`, which import
  Django and django-crispy-forms only.
- **"The pack draws formsets handed to it."** Adopted. A drawing stated on a formset's helper
  reaches every row through the path FS-007 built (R2). Nothing is added for rows in the browser.
- **"There is no support for carrying layouts over from other packs."** Adopted. Nothing here
  reads a class or an argument written for another pack.
- **"Each feature adds its own demo page or pages, and its own entry in the README's public
  surface."** Adopted. One page in two forms, in the shell and standalone, and one README section.

## R1. What the delivered features left in place

A single checkbox is drawn by `FieldInput` in `mvp_forms/templatetags/daisyui.py`:

- `FieldInput.components` maps `forms.CheckboxInput` to the component `checkbox`
  (`daisyui.py:77`). The component is the daisyUI class written on the input.
- `is_single_checkbox` (`daisyui.py:249`) is true for the component `checkbox` outside a group.
  `field.html` and `field_body.html` read it to put the input inside its own label.
- `fixed_size` (`daisyui.py:88`) keeps `w-full` off a checkbox and a radio.
- `error_modifiers` (`daisyui.py:100`) holds the error class of each component, as literals, and
  is indexed by the component, so a component with no entry there raises `KeyError` on a field in
  error.
- The label tie, required marker, help text and errors are drawn by the frame around the input
  and do not depend on the component. `disabled` is Django's attribute on the input (ADR 0013).

So a field drawn with the component `toggle` in place of `checkbox`, and still counted as a
single checkbox, keeps everything a checkbox has with no template change.

## R2. Where the choice is made

ADR 0019 settles it: "A later feature that needs a statement for one field or one button adds an
argument to `Choice`. It does not add a second layout object and does not subclass an upstream
one."

`Choice` (`mvp_forms/choices.py:297`) holds `size`, `color` and `variant`, each `INHERIT` by
default. It is used two ways, and both reach `FieldInput`:

- in a layout, `Choice("agree", size="lg")`, placed in the context and merged over any `Choice`
  around it by `Choice.over`;
- by name, `FormChoices(fields={"agree": Choice(size="lg")})`.

`FieldInput.resolve_modifiers` merges the two (`placed.over(named)`) and resolves each kind. A
fourth argument on `Choice` therefore travels every path a size does, including a formset whose
helper carries the statement, with no new plumbing. `FormChoices` gains nothing: the
specification rules out a drawing for a whole form (FR-001, D4).

## R3. What a toggle and a switch are in markup

- daisyUI's toggle is a checkbox input with the class `toggle`. It has the sizes `toggle-xs` to
  `toggle-xl` and the eight colours `toggle-neutral` to `toggle-error`, and no variant
  (`tests/data/daisyui-classes.txt:2900-2913`; there is no `toggle-ghost`).
- A switch is the same input with `role="switch"`. WAI-ARIA defines the `switch` role as a
  checkbox that represents on and off, and the HTML-ARIA specification allows `role="switch"` on
  `<input type="checkbox">`. The state is still the input's own `checked`, so no script is needed
  and the value submitted is the checkbox's.
- Django's `BoundField.as_widget` merges the attributes it is given over the widget's own for one
  render (`django/forms/boundfield.py:85-97`, Django 6.1.1 as resolved in this project's
  environment). `FieldInput.attrs` already adds `class` and the ARIA attributes this way, so
  `role` is one more key and the widget is not written to (ADR 0004).

Neither drawing adds text, so there is nothing for the pack to translate (FR-015).

## R4. Which fields can take it

`forms.CheckboxInput` is a class of its own (`django/forms/widgets.py:692`).
`CheckboxSelectMultiple` descends from `RadioSelect` and `ChoiceWidget` (`widgets.py:982`), and
`NullBooleanSelect` from `Select` (`widgets.py:907`). Neither is a `CheckboxInput`, so
`isinstance(widget, forms.CheckboxInput)` is exactly FR-003's test: Django's single checkbox or a
subclass of it.

A hidden field never reaches `FieldInput`: `field.html` draws it before the tag is called. A
drawing stated for it is never resolved and raises nothing, which is the edge case the
specification asks for.

## R5. How a mistake is reported

FS-007's rule (ADR 0020) is that a name outside the table raises `InvalidChoice` when the form is
drawn, naming the field, and that a choice stated on one field which its input cannot take raises
too. `InvalidChoice` carries `kind`, `value`, `allowed` and `target`, and `allowed` is empty
"when the input drawn has no modifier of this kind at all".

Both of FR-012's cases fit it without a new error:

- an unknown drawing name: `kind="drawing"`, `allowed` the three names;
- a drawing on a field that is not a boolean field: `kind="drawing"`, `allowed` empty.

A drawing is only ever a field's own statement, so `target` is always the field's name.

`checkbox` stated on a field that is not a boolean field raises as well. It cannot be honoured
there, and the README already says that any choice stated on a field by name raises when the
input cannot take it.

## R6. Size, colour and variant on a toggle

`Modifiers` holds one row per component in each table, and ADR 0020 says a new kind of input
adds a row. A `toggle` row in `sizes` and `colors`, and none in `variants`, gives:

- the form's size and colour reach a toggle and a switch, and a field's own wins (FR-011);
- a variant stated for the form is passed over, and a variant stated on the field raises, which
  is what a checkbox does (D8);
- a field in error keeps `toggle-error` and drops a chosen colour (ADR 0021).

`Modifiers.names` gathers every name any input has, so the new row adds no name to it.

## R7. What stays out

- A drawing for a whole form (D4).
- Toggles in a checkbox group, and the removal checkbox of a held file, which stays a checkbox.
- A look of its own for the switch (D2).
- Any change to a template in the pack.
