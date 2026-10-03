# Research: rating and range inputs

Done on 2026-10-03 against `origin/main` at `8622e54`, after FS-001 to FS-008 merged and v0.1.0
was released. FS-009, FS-011, FS-012 and FS-013 are being built at the same time and are not on
main. Django citations are to the installed package, Django 6.1.1, under the project's virtual
environment. daisyUI citations are to the CDN stylesheet of 5.7.47, the version
`tests/data/daisyui-classes.txt` was listed from.

## Planning notes, answered

Each of the maintainer's notes in `planning-notes.md`, under its own words.

- **"Every input, button and component is drawn with daisyUI's component classes and modifiers. A
  plain Tailwind utility is used only for layout."** Adopted. The feature writes `rating`,
  `rating-hidden`, `mask`, `mask-star-2`, `range`, the five size modifiers of each, the eight
  `range-` colour modifiers and the eight `bg-` colour classes daisyUI defines for its semantic
  colours. Every one is in `tests/data/daisyui-classes.txt` (lines 50 to 230 for `bg-`, 1295 and
  1307 for the mask, 1957 to 1979 for the rest). No layout utility is added: a range uses
  `w-full`, which ADR 0007 already allows.
- **"Pack templates are plain Django templates. `{% include %}` is fine inside the pack."**
  Adopted. One template is added, `daisyui/widgets/rating.html`, and it includes the pack's own
  `daisyui/widgets/attrs.html`.
- **"This package never depends on django-mvp at runtime and never imports from it."** Adopted.
  The change is in `mvp_forms/choices.py` and `mvp_forms/templatetags/daisyui.py`, which import
  Django and django-crispy-forms only.
- **"Size, colour and variant are stated through `FormChoices` and `Choice`. A new kind of input
  takes them by adding its rows to `Modifiers`."** Adopted. `rating` and `range` each get a row
  in `Modifiers.sizes` and `Modifiers.colors`, and none in `Modifiers.variants` (R6).
- **"There is no support for carrying layouts over from other packs. Fields and widgets beyond
  the roadmap arrive as a project needs them."** Adopted. No widget and no field class is added
  (decisions D2).
- **"Each feature adds its own demo page or pages, and its own entry in the README's public
  surface."** Adopted. One page in two forms, in the shell and standalone, and one README section.
- **"Nothing under `.github/` is changed by this work."** Adopted. No dependency and no supported
  version is added.

## R1. What the delivered features left in place

- `Choice(drawing=...)` and `Modifiers.drawings` (`mvp_forms/choices.py:232`), a table from a
  drawing's name to the component it is drawn with. Three names today, all for a boolean field.
- `FieldInput.resolve_drawing` (`mvp_forms/templatetags/daisyui.py:196`) refuses a drawing on any
  widget that is not a `CheckboxInput`, with nothing allowed, and an unknown name on one that is,
  with the three allowed. A hidden field resolves none (`daisyui.py:153`).
- `FieldInput.component` returns the drawing's component when one is stated
  (`daisyui.py:272`), and the modifiers are resolved for that component (`daisyui.py:167`).
- `FieldInput.widget` (`daisyui.py:314`) draws a widget the pack has a template for through a
  shallow copy that names the pack's template (ADR 0012). `removal_context` (`daisyui.py:358`)
  wraps the copy's `get_context` so that classes resolved in Python reach the widget's template.
- The frame (`daisyui/frame.html`) draws a fieldset and a legend when `drawn.is_group`, which is
  `field.use_fieldset` today (`daisyui.py:380`), and a labelled block otherwise.
- `FieldInput.error_modifiers` and `fixed_size` are keyed by component.

## R2. daisyUI's rating, as the stylesheet has it

```css
.rating { display: inline-flex; --size: ... * 6 }
.rating input { cursor: pointer; appearance: none }
.rating * { background-color: var(--color-base-content); opacity: .2; width: ...; height: ... }
.rating .rating-hidden { background-color: #0000; width: .5rem }
.rating :checked, .rating :has(~ :checked) { opacity: 1 }
.rating-xs { --size: ... * 4 }  /* and -sm, -md, -lg, -xl */
```

What follows from it:

- **A rating with nothing checked shows no star as picked.** Every child starts at opacity 0.2 and
  only a checked input and the ones before it are raised to 1. This settles the open point in
  decisions D5: daisyUI 5 does not fill the stars of an unchecked group, so FR-008 needs nothing
  beyond the stock markup. (daisyUI 4 dimmed the stars after the checked one instead, which is
  where the concern came from.)
- **Every child of `.rating` is drawn as a star.** A `<label>` around each input, as the radio
  group's template writes, would itself be a star. So the stars are bare inputs, each named by
  `aria-label`, which is also how daisyUI's documentation writes them.
- **The size is a modifier of the wrapper** and there is no colour modifier. A star takes its
  colour from its own background, so the colour is a class on each star (decisions D4).
- **The way to clear is an input with `rating-hidden`**, drawn first, transparent and narrow.
  Checked, it raises nothing before it, so no star shows as picked.
- **The star's shape is the mask** `mask mask-star-2`, the one daisyUI's documentation uses for
  its ordinary rating.
- **daisyUI has no disabled look for a rating.** A disabled star is not clickable and is not
  submitted, and looks as it did.

## R3. daisyUI's range

`.range` is a class on one `<input type="range">`. It has `range-xs` to `range-xl`, eight colour
modifiers including `range-error`, and `.range:disabled` dims it. Its width is
`clamp(3rem, 20rem, 100%)`, as an input's is, so `w-full` makes it fill its field.

## R4. Drawing a select or a radio group as a rating

A rating is radio inputs. Django's `RadioSelect` already produces what the template needs: each
option carries the widget's attributes (`option_inherits_attrs`, `widgets.py:738`), an id with an
index (`add_id_index`, `widgets.py:736`) and `checked` (`widgets.py:737`). `Select` produces none
of them (`widgets.py:873-875`) and withholds `required` when its first choice has a value
(`widgets.py:889`).

So the widget drawn for a rating is:

- for a radio group, a shallow copy of the field's widget with the rating's template, as ADR 0012
  does for the group's own template;
- for a select, a `RadioSelect` made for the draw from the select's attributes and its choices,
  with the rating's template. The select is not written to.

`BoundField.as_widget(widget=...)` draws either with the field's name, value and id.

Two things in Django read the form's own widget and not the one drawn:

- `BoundField.use_fieldset` (`boundfield.py:325`). The frame's `is_group` has to be true for a
  rating whatever the widget, so `FieldInput.is_group` takes the drawing into account, and the
  three properties that ask `field.use_fieldset` ask `is_group` instead.
- `BoundField.build_widget_attrs` adds `aria-describedby` when the form's widget is not a
  fieldset (`boundfield.py:300`). For a select drawn as a rating that would put the description
  on every star as well as on the fieldset. `FieldInput.render` already has a path that builds
  the attributes itself and drops that one; the rating of a select takes it, unless the developer
  set `aria-describedby` on the widget.

An optional field with no value is drawn with its empty choice checked: `ChoiceWidget.format_value`
turns `None` into `""`, which matches the empty choice. That is the clearing input, so no star is
picked.

Named groups: `widget.optgroups` yields `(group_name, options, index)`. The template walks the
options of every group in order and never writes the name (FR-010).

A widget that names a template of its own cannot be drawn through the pack's template. The test
ADR 0012 uses, that `template_name` and `option_template_name` are still the Django class's own,
decides whether a single-choice field takes a rating (FR-021).

## R5. Drawing a number input as a range

`NumberInput` is drawn by `django/forms/widgets/input.html`, which writes
`type="{{ widget.type }}"` from the widget's `input_type` and then every attribute. Passing
`type` as an attribute would write it twice. So the widget drawn is a shallow copy with
`input_type = "range"`, drawn by Django's own template. `min`, `max` and `step` are written by
`IntegerField.widget_attrs` and its relatives onto the widget's attributes, which the copy
shares, so FR-013 holds with nothing added.

A localised `DecimalField` has a `TextInput`, not a `NumberInput`, so it is not a number field
and a range stated for it raises (spec, edge cases).

## R6. Size, colour, variant and error

- `Modifiers.sizes` and `Modifiers.colors` gain a `rating` row and a `range` row.
  `Modifiers.variants` gains none, and `Modifiers.resolve` then already passes a form's variant
  over and raises for a field's own (`choices.py:313-317`).
- A rating's size is written on the wrapper and its colour on each star, so `FieldInput` resolves
  the two kinds separately for a rating. A range's are both on the input, like any input.
- In error, a range takes `range-error` and a rating's stars take `bg-error`, daisyUI's class
  for the error colour, as a radio takes `radio-error`. The chosen colour is left out by
  `Modifiers.resolve(in_error=True)` as it is for every input (FR-020).
- A rating is never widened and never joined. A range is widened like an input.

## R7. Which drawings a field takes

FR-021 asks the error to say which drawings the field can take. Today the allowed names are all
three or none. With five drawings the allowed names depend on the field's widget:

| The field's widget | Drawings |
|---|---|
| `CheckboxInput` or a subclass | `checkbox`, `toggle`, `switch` |
| `Select` or `RadioSelect` or a subclass, holding one value, not `NullBooleanSelect`, naming its class's templates | `rating` |
| `NumberInput` or a subclass | `range` |
| anything else | none |

`CheckboxSelectMultiple` is a subclass of `RadioSelect` and `SelectMultiple` of `Select`. Both
set `allow_multiple_selected`, which is what tells them apart. `NullBooleanSelect` is a subclass
of `Select` and is excluded by name.

`resolve_drawing` then has one rule: the name stated has to be among the field's drawings, and
the error carries those. The existing tests of a drawing on a text field, a checkbox group and a
null-boolean select still hold, with nothing allowed.

## R8. What other layout objects do with them

- A layout object that attaches text (`has_attached_text`, `daisyui.py:465`) applies only to the
  components `input` and `select`. A range's component is `range` and a rating is a group, so
  both are drawn without the attached text, as the spec's edge case says.
- `InlineRadios` names an inline template for a radio group. The rating's template is chosen
  first, so the rating is drawn.
- The table layout of a formset draws each cell through the same tag, so a rating and a range
  are drawn in a cell as elsewhere.
