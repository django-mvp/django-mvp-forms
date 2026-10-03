# Research: size, colour and variant chosen from Python

Written 2026-10-03 on the feature branch, rebased onto `origin/main` at `23d5139` (FS-001, FS-002
and FS-003 merged). Paths under `site-packages/` are the packages this repository's lockfile
resolves: django-crispy-forms 2.7. daisyUI's class names were read from
`tests/data/daisyui-classes.txt` (5.7.47), the list the suite checks against.

The specification has no planning notes and no sketch, so everything below is what the plan needs
settled.

## R1. What the three delivered features left in place

- `mvp_forms/templatetags/daisyui.py`: `FieldInput` maps a widget class to a daisyUI component
  through `components`, builds the class string in `css_class` (the widget's own classes, the
  component, `w-full`, the error modifier) and renders through `BoundField.as_widget(attrs=...)`,
  so nothing is written to the widget (ADRs 0004, 0012). The frame gets it from
  `{% daisyui_field field as drawn %}`.
- The frame, `daisyui/field.html`, prints a hidden field bare before it asks for a `FieldInput`,
  so a hidden input never passes through the code this feature changes (FR-009 holds by
  construction).
- A radio group, a checkbox group and a date's selects are drawn by the pack's templates under
  `daisyui/widgets/`. Each writes the widget's attributes on every input of the field through
  `widgets/attrs.html`, so a class added in `FieldInput.css_class` reaches every option and every
  select (FR-017) with no template change.
- `daisyui/widgets/clearable_file_input.html` writes the removal checkbox with a literal
  `class="checkbox"`. It is the one input of a field that does not take the widget's class.
- Buttons: `Submit`, `Reset` and `Button` are drawn by `daisyui/layout/baseinput.html`, which
  writes `input.field_classes` through the `daisyui_classes` filter. `StrictButton` is drawn by
  `daisyui/layout/button.html`, which writes `button.flat_attrs`, a string django-crispy-forms
  flattened when the button was constructed and which always holds a `class`. Buttons added to a
  helper are drawn by `daisyui/inputs.html` with the same two templates.
- ADR 0008 says the package defines no layout classes, and names this feature as the likely
  reason to revisit it.

## R2. Where a statement for the whole form can live

The crispy filter builds its own context from the form alone and never reads a helper
(`crispy_forms_filters.as_crispy_form`). The crispy tag reads the helper and renders the layout
before the form's own template, with a context that holds the helper's attributes and **not the
form**: `helper.render_layout(actual_form, node_context)` runs before `final_context["form"]` is
set (`crispy_forms_tags.py`, lines 109 to 133). A button in a layout therefore has no reliable way
to reach the form. A page that names its form `contact_form` leaves no `form` in the context at
all.

django-crispy-forms does pass every attribute set on a helper into that context, by name
(`FormHelper.get_attributes`, the loop over `self.__dict__`, and "Handles custom attributes added
to helpers" in `get_response_dict`). It documents this as the way to give a template pack a
setting of its own.

Options weighed:

| Home | Fields, filter | Fields, tag | Buttons in a layout |
|---|---|---|---|
| An attribute on the form | `field.form` | `field.form` | not reachable |
| An attribute on the helper | `field.form.helper` | context | context |
| A helper subclass of the pack's | as above | as above | as above, plus a second `FormHelper` name |
| Arguments on each layout object | none | repeats on every object | repeats |

**Chosen: one attribute on the form's helper, `helper.daisyui`, holding a `FormChoices`.** It is
the only home every drawing path can read, it uses the mechanism django-crispy-forms documents,
and it needs no helper subclass. Under the tag the value arrives in the context. Under the filter
and `|as_crispy_field` the pack reads `field.form.helper`, the standard name the tag itself falls
back to.

A plain attribute per choice (`helper.size = "sm"`) was rejected: a misspelt attribute name does
nothing and reports nothing, which is the failure US4 exists to remove. A constructor refuses a
keyword it does not know.

## R3. Where a statement for one field or one button can live

`Field("name", size="lg")` cannot carry it: django-crispy-forms writes a `Field`'s keyword
arguments into `widget.attrs` (`utils.render_field`), so the input would gain an HTML `size`
attribute, and the write stays on the form. `Submit("save", "Save", size="lg")` cannot either:
`BaseInput.__init__` flattens its keyword arguments into HTML attributes at once.

Options weighed:

- **Subclasses of `Field`, `Submit`, `Reset`, `Button` and `StrictButton`.** Five new names, each
  shadowing an upstream one. This is what ADR 0008 ruled out, for the reason it gives.
- **One layout object of the pack's that holds fields and buttons and states a choice for them.**
  One new name, and every upstream object keeps its own.

**Chosen: one layout object, `Choice`.** `Choice("search", size="lg")` and
`Choice(Submit("save", "Save"), color="accent")`. It renders what it holds with the choice placed
in the context for the duration, which is the only channel that reaches both a field's frame and
a button's template. It works with django-crispy-forms' own `helper["search"].wrap(Choice,
size="lg")`.

A layout object only exists under the tag with a layout, and FR-012 asks for a statement on a
form drawn without one. So the same `Choice`, holding nothing, is also the value in
`FormChoices(fields={"search": Choice(size="lg")})`, which names one field and lists no other.

Context handling: django-crispy-forms leaves layers on the context (`context.update` in
`BaseInput.render`, `StrictButton.render` and `render_field`). `Choice.render` therefore pushes
one layer and afterwards removes that layer by identity, not by popping the top.

## R4. Names and modifiers

From `tests/data/daisyui-classes.txt`:

| | Sizes | Colours | Variants |
|---|---|---|---|
| `input`, `textarea`, `select`, `file-input` | xs sm md lg xl | neutral primary secondary accent info success warning error | ghost |
| `checkbox`, `radio` | xs sm md lg xl | the same eight | none |
| `btn` | xs sm md lg xl | the same eight | outline dash soft ghost link |

Every one of those 100 classes is in the list. `checkbox-ghost` and `radio-ghost` are not, which
is the case FR-021 and FR-022 describe.

A host project's Tailwind build finds a class only where it is written out (README,
*Installation*; the note on `FieldInput.error_modifiers`). The modifiers are therefore a literal
table, not a format string.

`md` is daisyUI's name for the ordinary size and has a class of its own, so it is accepted and
writes `input-md`.

## R5. A field in error and a chosen colour

`input-primary` and `input-error` both set the same custom property, and which wins depends on
the order of the rules in the stylesheet. Writing both would rest FR-018 on that order. **Chosen:
a field drawn as in error does not get the colour modifier.** The size and the variant still
apply. With errors off (`form_show_errors=False`) the field is not drawn as in error and takes
its colour.

## R6. When a mistake is reported

A `Choice` in `FormChoices.fields` is constructed before it knows which field it is for, so
checking names in a constructor cannot name the field (FR-020). **Chosen: every name is checked
where it is resolved, at draw time, in one place**, which knows the field or button and the kind
of input.

The frame reads a `FieldInput` inside `{% if %}`, and Django's `{% if %}` swallows an exception
raised while evaluating an operand of `and`, `or` or `not` (`smartif`). The check therefore runs
when the `daisyui_field` tag builds the `FieldInput`, not in a property the template reads.

The error is `InvalidChoice`, a `ValueError` that carries what was stated, the names allowed and
the field or button, so a test reads those and not the message's wording.

## R7. The removal checkbox of a file field

SC-003 leaves no visible input at the ordinary size. The removal checkbox is drawn by the pack's
template from a widget context Django builds, and nothing but the widget's final attributes
reaches that template. **Chosen: a filter in the pack's tag library turns the file input's class
string into the checkbox's**, mapping each size and colour modifier through the table. The
checkbox has no variant and is not marked in error today, and neither changes.

## R8. What stays out

- `SplitDateTimeWidget` is drawn without a class and belongs to FS-004 (#8). It has no component,
  so a form-wide choice passes over it and a choice stated on it alone is an error.
- A toggle is #12, which adds a row to the table.
- Attached text and attached buttons are #15.
- A formset's forms are FS-006's. Each form of a formset has its own helper only if the host
  gives it one; nothing here is specific to formsets.
