# Research: floating labels and joined inputs

Done on 2026-10-04 against `origin/main` at `1b5802d`, after FS-001 to FS-009 merged and v0.1.0
was released. FS-010, FS-012 and FS-013 are being built at the same time and are not on main.

Resolved versions: Django 6.1.1 and django-crispy-forms 2.7 in the project's environment, and
daisyUI 5.7.47, which is what `https://cdn.jsdelivr.net/npm/daisyui@5` serves and what
`tests/data/daisyui-classes.txt` was listed from.

## Planning notes, answered

Each note in `planning-notes.md`, under its own words.

### From the maintainer

- **"Class policy, as ADR 0003 has it."** Adopted. The feature writes `floating-label`, `join` and
  `join-item`, all in the class list (`tests/data/daisyui-classes.txt:603,710,712`), and the
  modifiers FS-007 already writes. One layout utility is new, `w-auto` (R6), and is added to the
  class test by name.
- **"Pack templates are plain Django templates."** Adopted. Three templates are added and two
  change. All are plain, and each added one gets its row in the README's template list (ADR 0029).
- **"The package never depends on django-mvp at runtime and never imports from it."** Adopted. The
  new module imports Django and django-crispy-forms only.
- **"Size, colour and variant are stated through `FormChoices` and `Choice`. A new kind of input
  takes them by adding its rows to `Modifiers`."** Adopted in spirit. This feature adds no kind of
  input, so no row is added to the three tables. The floating label is a fifth kind of choice
  and gets a table of its own beside `Modifiers.drawings`, so its class is a literal (R3).
- **"There is no support for migrating layouts from other packs."** Adopted. Nothing here reads a
  class or an argument written for another pack. A class written for another pack on a joined
  group is dropped by the existing `daisyui_classes` filter.
- **"Each feature adds its own demo page or pages, and its own entry in the README's public
  surface."** Adopted. Two pages in the shell, each with a standalone twin, and two README
  sections.
- **"Nothing under `.github/` is changed by this work."** Adopted. Nothing there is needed.

### From writing the specification

- **"Check each of these against the daisyUI version the pack pins."** Adopted, and each holds in
  5.7.47 (R1).
- **"`floating-label` and `join`, `join-item`, `join-vertical` and `join-horizontal` are already
  in the class list."** Confirmed at the lines above.
- **"The frame draws the ordinary label from `drawn.show_labels`, and `InlineField` already
  offers the label as a placeholder. FR-005 and FR-006 probably reuse both."** Adopted in part.
  The placeholder rule is reused as it stands: `FieldInput.requires_placeholder` gains a second
  case. `show_labels` is not reused to hide the ordinary label, because it also decides whether
  the input is given an `aria-label`, and a field with a floating label has a label. The frame
  asks a new property, `drawn.is_floating` (R4).
- **"A member's input has to be a direct child of the join."** Confirmed (R2). It also rules out
  a hidden input inside the join, which the note did not say: the join squares its first and
  last child, and a hidden input in either place would take the rounding from the visible one.
- **"A select for a country code beside a text input should not each take half the width."**
  Adopted (R6).
- **"FR-016 should need no new id."** Confirmed (R5). The help text and the errors move to a
  template of their own so that the frame and the joined group draw the same elements.
- **"Confirm that a form-wide floating label leaves the table unchanged."** Confirmed by reading
  (R7) and given a test.
- **"Decision records are expected."** Adopted: one for the floating label as a kind of choice
  with the disabled fallback, one for the joined group as a second layout object.

## R1. daisyUI's floating label, as 5.7.47 defines it

Read from `https://cdn.jsdelivr.net/npm/daisyui@5.7.47/daisyui.css`.

- `.floating-label{display:flex;position:relative}` and `.floating-label>span{opacity:0;
  position:absolute;…}`. The label text is a direct child `<span>`. A span nested inside it, such
  as the required marker, is not matched by `>span` and is drawn inside it.
- The span is shown at the edge when
  `.floating-label:focus-within` or
  `.floating-label:not(:has(input:placeholder-shown,textarea:placeholder-shown))`. So while an
  `input` or a `textarea` shows a placeholder and has no focus, the span stays transparent and
  the placeholder is what is read. A `select` never matches `:placeholder-shown`, so its span is
  at the edge at all times. An input with no `placeholder` attribute never matches it either.
- `.floating-label:has(:disabled,[disabled])>span{opacity:0}`. A disabled input's floating label
  is never shown, whatever its value. This is the rule FR-007 answers.
- `.floating-label:has(.input-xs)` to `.floating-label:has(.input-xl)` set the span's font size
  and position, and the same rules exist for `select-*` and `textarea-*`. The label's text
  therefore follows the size of all three.

daisyUI's documented markup is a `<label class="floating-label">` holding a `<span>` and the
input, in that order. A label that contains its input names it, and the pack also writes `for`,
as it does on every label.

## R2. daisyUI's join

- `.join` is `display:inline-flex` and sets the corner variables on `:scope>:first-child`,
  `:scope>:last-child`, `:scope>:only-child` and `:scope>:not(:first-child)`. They are direct
  children, and the first and last are counted among all children, hidden ones included.
- `.join-item` reads those variables for its radius and draws the one-pixel overlap. A disabled
  `join-item` keeps its border.
- `.join-vertical` and `.join-horizontal` switch the direction on the join element itself, so a
  developer's class has to land on the element that carries `join`.

The pack already draws one join, for `FieldWithButtons`, in `daisyui/field_body.html` as
`<div class="join w-full …">` with the developer's id, class and attributes on it (ADR 0026).

## R3. Where a choice is stated and resolved today

- `Choice` (`mvp_forms/choices.py:323`) holds `size`, `color`, `variant` and `drawing`, each
  `INHERIT` by default. `Choice.over` merges one over another, each kind on its own.
- `FormChoices` (`choices.py:413`) holds the form's `size`, `color`, `variant`, the buttons' two
  and `fields`. `FormChoices.check` raises `InvalidChoice` for a form-wide name daisyUI lacks.
- `FieldInput.own_choice` (`templatetags/daisyui.py:181`) merges the layout's `Choice` over the
  one named for the field. `resolve_drawing` (`:197`) is the model for a kind that is not a row
  of the three tables: resolved in `__init__`, raising `InvalidChoice` with the field as target.
- `DrawnButton.resolve_modifiers` (`:639`) refuses a drawing stated around a button.
- Both drawing paths reach `FormChoices.lookup` (`choices.py:475`): the crispy tag through the
  context name `daisyui`, the filter through `form.helper`. A formset drawn stacked passes its
  helper's attributes into each form's context the same way, so a new attribute of
  `FormChoices` reaches every path with no further work.

## R4. The frame

`daisyui/field.html` and each decorating layout object's template call `daisyui_field` and
include `daisyui/frame.html`, which includes `daisyui/field_body.html` (ADR 0023).

- The frame draws the ordinary label when `field.label and drawn.show_labels and not
  drawn.is_single_checkbox` (`frame.html:14`).
- `field_body.html` already has three shapes for the input: a single checkbox in its label, an
  input inside the attached-text wrapper, and the bare input. A floating label is a fourth.
- `FieldInput.requires_placeholder` (`daisyui.py:517`) offers the label's plain text as the
  placeholder of an unlabelled input or textarea, unless the widget has one.
- `FieldInput.requires_aria_label` names the input when `show_labels` is off.
- A field is disabled for one of three reasons: the form field's `disabled`, which Django writes
  as the attribute; the `disabled` option `UneditableField` passes; or `disabled` in the
  widget's own attributes.

## R5. How django-crispy-forms draws a field in a layout

Read from `crispy_forms/utils.py` and `crispy_forms/layout.py` in the installed 2.7.

- `render_field(field, form, context, template=None, attrs=None, template_pack=…,
  extra_context=None)` (`utils.py`): for a layout object it calls
  `field.render(form, context, template_pack=template_pack)` and passes nothing else on. For a
  name it looks the bound field up, writes `attrs` onto the widget, records the name in
  `form.rendered_fields`, reports a name the form lacks (raising unless `CRISPY_FAIL_SILENTLY`),
  and renders `template` with the flattened context plus `field`.
- `Field` (`layout.py:877`) holds names in `fields`, the widget attributes in `attrs`, and a
  `template` that defaults to `%s/field.html`. A `template` given to its constructor replaces
  the default. `PrependedText`, `InlineField`, `UneditableField` and `MultiWidgetField` are
  subclasses of `Field`.
- `LayoutObject.get_rendered_fields` renders each entry through `render_field`.
- `MultiField.render` shows the route for a template that needs the helper's switches: it
  renders its own template with the flattened context.
- Django writes `aria-describedby` on an input from the ids of its help text and its error
  element, and `aria-invalid` on a field in error. A member drawn through `FieldInput.render`
  gets both exactly as any field does (ADR 0005).

So a member can be drawn by django-crispy-forms' own `Field`, given a template that draws the
input alone, and the existing `Choice.render` can place a choice around it. Nothing of
`render_field` has to be copied.

## R6. Sharing the width of a joined group

ADR 0007 gives every text-like input `w-full`. In a flex container two `w-full` items shrink to
equal shares, which is the half-and-half the planning note warns against. daisyUI's `input` and
`select` are otherwise `width: clamp(3rem, 20rem, 100%)`, so a select with no width class is
twenty rems wide whatever it holds.

Chosen: the join is `join w-full`, as the existing one is. A member drawn as an input takes
`flex-1`, which is already in the class test, and fills what is left. A member drawn as a select
takes `w-auto`, the one new utility, and is as wide as its longest option. A width the developer
wrote on the member (a class starting `w-`) is kept and the pack adds neither, which is ADR
0007's rule.

Rejected: leaving `w-full` on every member (equal shares); no width class at all (two fixed
twenty-rem boxes that never fill the row); `grow` (not in the class test, and `flex-1` already
is).

## R7. Formsets

- Stacked: each form is drawn as a form, with the helper's layout and its `daisyui` attribute, so
  both parts apply to every form.
- As a table: `daisyui/table_inline_formset.html` applies no layout and includes the field
  template `with form_show_labels=False`. `daisyui_field` reads that switch, so a floating label
  is never drawn there, and a `Join` in the layout is never rendered.

## R8. What the checks need

- `tests/test_pack/test_template_list.py` fails on a distributed template with no row in the
  README's list, and on a name a template reads that its row leaves out. `drawn` is listed one
  level down. A layout object handed to its template, as `div` and `multifield` are, is listed
  by its name alone.
- `tests/template_surface.py` knows `if`, `for`, `with`, `include`, `load` and the pack's simple
  tags. The new templates use nothing else.
- `tests/test_pack/test_replacements.py` replaces every distributed template with a copy and
  compares every entry of `STATES`. A new template is covered once a state draws it.
- `tests/test_pack/test_independence.py` checks every class the states write against the class
  list and `LAYOUT_UTILITIES`, and every class in `Modifiers.tables`.

## Open questions left for the maintainer

None that block the build. #94 (buttons in a joined group), #15 (one size for a joined input)
and #70 (telephone and search widgets) stay open and are not settled here.
