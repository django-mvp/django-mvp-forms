# Research: layout objects for structure and buttons

**Feature**: [spec.md](spec.md) · **Date**: 2026-10-03

Investigated against `origin/main` at `c0a2943` (FS-001 merged) and the packages the lockfile
resolves: django-crispy-forms 2.7, Django 6.1.1, django-mvp 0.25.2. File and line references to
django-crispy-forms are to `.venv/lib/python3.13/site-packages/crispy_forms/`.

## Planning notes, answered

### "Rows and columns may use Tailwind layout utilities"

**Adopted.** daisyUI 5 has no grid or column component (`tests/data/daisyui-classes.txt` holds no
such class), and ADR 0003 already allows a Tailwind utility for layout where daisyUI has nothing.
A `Row` is drawn as a flex container that stacks on a narrow page and sets its children side by
side from Tailwind's `md` breakpoint. A `Column` takes an equal share of the row. The utilities
are `flex flex-col gap-4 md:flex-row` on the row and `flex-1 min-w-0` on the column. See R4 for
why these and not a grid. Issue #18 stays open for the maintainer to confirm.

### "StrictButton, Hidden and MultiField stay in this feature"

**Adopted.** All three get a template here. FS-002's specification (pull request #22) covers how
a disabled or read-only *field* is drawn and how a hidden *field* is carried. It does not name the
`Hidden` layout object, `StrictButton` or `MultiField`, so nothing overlaps.

### "The pack is named daisyui"

**Adopted.** Every template this feature adds lives under `mvp_forms/templates/daisyui/`, at the
path django-crispy-forms builds from the pack's name (R1).

## R1. What django-crispy-forms asks the pack for

django-crispy-forms 2.7 ships no template pack of its own. Each layout object names its template
as `"%s/layout/<name>.html"` and fills in the pack's name when it draws
(`TemplateNameMixin.get_template_name`, `layout.py:19`). A `template=` argument replaces that
path, which is all FR-019 needs: the pack does nothing to honour it.

| Layout object | Template asked for | Names given to the template | Context |
|---|---|---|---|
| `Div` | `daisyui/layout/div.html` | `div`, `fields` | those two only (`layout.py`, `Div.render`) |
| `Row` | `daisyui/layout/row.html` | `div`, `fields` | those two only (`Row` inherits `Div.render`) |
| `Column` | `daisyui/layout/column.html` | `div`, `fields` | those two only |
| `Fieldset` | `daisyui/layout/fieldset.html` | `fieldset`, `legend`, `fields` | the page's context, flattened |
| `MultiField` | `daisyui/layout/multifield.html`, and `daisyui/multifield.html` for each field inside it | `multifield`, `fields_output` | the page's context, flattened |
| `ButtonHolder` | `daisyui/layout/buttonholder.html` | `buttonholder`, `fields_output` | the page's context, flattened |
| `FormActions` | `daisyui/layout/formactions.html` | `formactions`, `fields_output` | the page's context, flattened |
| `Submit`, `Reset`, `Button`, `Hidden` | `daisyui/layout/baseinput.html` | `input` | the page's context, flattened |
| `StrictButton` | `daisyui/layout/button.html` | `button` | the page's context, flattened |
| `HTML` | none: it renders its own string as a template | | the page's context |

`FormActions` and `StrictButton` live in `crispy_forms.bootstrap`, not `crispy_forms.layout`.
That is where the documentation tells a developer to import them from, so the pack draws them
where they are.

Where the context is the page's, every name the template reads is one django-crispy-forms sets
itself just before rendering, so a page variable cannot stand in for it. This is the rule ADR 0006
set for the field frame.

Attributes each object carries:

- `Div`, `Row`, `Column`: `css_id`, `css_class`, `flat_attrs`.
- `Fieldset`: `css_id`, `css_class`, `flat_attrs`. Its legend is rendered as a template against the
  page context before the pack's template sees it (`Fieldset.render`), so a context value in it is
  already escaped and the result is marked safe.
- `MultiField`: `css_id`, `css_class`, `label_html`, `label_class`, `flat_attrs`. The label is
  **not** rendered as a template. It is drawn as the developer wrote it.
- `ButtonHolder`: `css_id`, `css_class`. It takes no other attributes.
- `FormActions`: `id`, `css_class`, `flat_attrs`.
- `Submit`, `Reset`, `Button`, `Hidden`: `input_type`, `name`, `value`, `id`, `field_classes`,
  `flat_attrs`. `value` is rendered as a template when the object is in a layout
  (`BaseInput.render`). `css_class` is appended to `field_classes`.
- `StrictButton`: `content` and `flat_attrs`. Its id, its class (`btn` plus the developer's) and its
  type (`button` unless the developer chose another) are all inside `flat_attrs`. `content` is
  rendered as a template before the pack's template sees it.

## R2. The classes django-crispy-forms writes itself

Some class names come from django-crispy-forms' Python, written for Bootstrap and uni-form:

| Object | Class it writes | In daisyUI's stylesheet |
|---|---|---|
| `Submit` | `btn btn-primary` | both |
| `Button` | `btn` | yes |
| `StrictButton` | `btn` | yes |
| `Reset` | `btn btn-inverse` | `btn` only |
| `Hidden` | `hidden` | no |
| `MultiField` | `ctrlHolder`, plus `error` appended on every render that finds a field error, and `blockLabel` for its label | none |

Three of the four buttons come out as daisyUI buttons with no work. That is luck the pack can
use, and the button tests will say so if a later release of django-crispy-forms changes them.

The names daisyUI does not define cannot be told apart from the developer's own in a template,
because django-crispy-forms joins both into one string. A small filter in the pack's template
library drops them by name: `btn-inverse`, `ctrlHolder`, `blockLabel` and `error`. It also drops
repeats, because `MultiField` appends `error` again each time the same layout is drawn.

`Hidden` is drawn with no class and no id, as the Bootstrap packs draw it. An id or any other
attribute a developer needs on it can be passed as a keyword argument and arrives through
`flat_attrs`.

An alternative was to subclass the layout objects with daisyUI defaults, as crispy-tailwind does.
The specification rules it out: layouts use django-crispy-forms' own classes (D1, FR-018).

## R3. Buttons added to the form helper

`FormHelper.add_input` puts the object in `helper.inputs`, and the `{% crispy %}` tag passes that
list to the form wrapper as `inputs` (`helper.py:337`, `templatetags/crispy_forms_tags.py:171`).
Nothing calls `render` on them. A pack draws them by looping over `inputs` in its wrapper.

FS-001's wrapper, `daisyui/whole_uni_form.html`, has no such loop, and FS-001's decisions say
"buttons and layouts are #7's". This specification's D5 expected FS-001 to place them and names
what happens if it did not: the placement needs an owner. It is taken here (decision D10 in
`decisions.md`). The wrapper gains one include, `daisyui/inputs.html`, after the fields. That
template draws each input with `daisyui/layout/baseinput.html`, the same template a button in a
layout uses, which is what FR-014 asks for.

Because `render` is not called, a helper-added button's value is not rendered as a template and
is escaped as an ordinary variable. That is how the Bootstrap packs behave.

## R4. How a row sets its columns side by side

Options weighed for FR-005:

1. **Grid with automatic columns** (`grid md:grid-flow-col md:auto-cols-fr`). Equal columns for
   any number of children. django-mvp's packaged stylesheet does not contain `grid-flow-col` or
   `auto-cols-fr`, so on the demo's shell page the columns would stack. A django-mvp project is
   the first host this pack has.
2. **Grid with a fixed column count** (`md:grid-cols-2`). The template cannot know how many
   columns a row holds without counting them in Python.
3. **Flex** (`flex flex-col gap-4 md:flex-row` on the row, `flex-1 min-w-0` on the column).
   Equal shares for any number of columns, stacked below `md`. Every one of these utilities is in
   django-mvp's packaged stylesheet and in Tailwind's browser build. **Chosen.**

`min-w-0` lets a column shrink below the width of what it holds, so a long input cannot push its
neighbours off the row. A `Column` outside a `Row` carries two utilities that do nothing there. A
`Row` holding fields directly still draws them, in order.

The developer's classes are added after the pack's. A developer who wants another arrangement
adds utilities to the `Column` (for example a fixed share) or draws the row with a template of
their own.

`ButtonHolder`, `FormActions` and the helper's buttons need their buttons in a line with a gap,
and daisyUI has no component for that outside a card or a modal (`card-actions` and
`modal-action` are styled for those parents). They use `flex flex-wrap gap-2 mt-4`.

## R5. Groups and their names

A `Fieldset` is drawn as a `<fieldset>` with daisyUI's `fieldset` class and its legend as a
`<legend class="fieldset-legend">`. Assistive technology reads a `fieldset` as a group named by
its `legend`, which is FR-002 with no ARIA. With no legend the element is still a group and no
`<legend>` is drawn.

A `MultiField` is drawn the same way, with its label as the legend (FR-004). Each field inside it
is drawn by the field frame, through a one-line `daisyui/multifield.html` that includes
`daisyui/field.html`. So a field in a `MultiField` keeps its own label, help text and errors,
tied to it as everywhere else (FR-008, ADR 0006). The Bootstrap packs collect the errors at the
top of the group and drop each field's own. The pack does not follow them there, because a field
whose error sits somewhere else is what G3 is against.

The field frame already uses `fieldset` and `fieldset-legend` on a `div` and a `label`. A group's
legend and a field's label therefore share daisyUI's legend style. That is stock daisyUI, and how
it looks is judged on the demo pages.

## R6. The class test

`tests/test_pack/test_independence.py` compares every class in a drawn form with
`tests/data/daisyui-classes.txt`, less the names in `LAYOUT_UTILITIES`. This feature adds layouts
to the forms it draws and adds these utilities by name: `flex`, `flex-col`, `flex-wrap`, `flex-1`,
`min-w-0`, `gap-2`, `gap-4`, `mt-4`, `md:flex-row`.

## R7. Escaping

- `HTML`, a legend and a `StrictButton`'s content are rendered by django-crispy-forms as templates
  against the page's context, with autoescaping on. A context value is escaped there. The markup
  the developer wrote is kept. The pack's templates print the result without escaping it again.
- A `MultiField` label is printed as written, as the developer's own markup (D6).
- A button's `name`, `value` and `id` are printed as ordinary variables. A value that came through
  `BaseInput.render` is already a safe string with its context values escaped.
- `flat_attrs` is built by Django's `flatatt`, which escapes each value.

Nothing a person using the host project typed reaches these templates unescaped.

One edge is django-crispy-forms' own and no pack template can change it. A button stores its
rendered value back on itself (`layout.py:255`, `bootstrap.py:559`), so a layout object drawn a
second time renders its earlier output as a template again. A layout object is therefore built
per form instance, in the form's `__init__`, and never held on a class or shared between forms.
The demo and the tests follow that.

## R8. The demo project

One page pair, as FS-001 has: `/layout-objects/` on the django-mvp shell and
`/layout-objects/standalone/` styled by daisyUI's CDN install alone. Both draw the same forms:

- a form to submit whose layout uses every structural object, `HTML`, `Hidden`, and a
  `FormActions` holding the four buttons,
- the same layout bound to data that fails, so errors can be seen without submitting,
- a form with no layout whose buttons were added to the helper, and a `ButtonHolder`.

Text fields only (D8). The shell page uses Cotton for the page around the forms. The forms
themselves are drawn by `{% crispy %}`.

FS-002 is being built at the same time and also adds demo pages, routes, menu entries and README
and CHANGELOG sections. Its changes and these are additions to the same lists, so a conflict is
resolved by keeping both.

## R9. Text the pack adds

None. Legends, labels and button text are the developer's. No `locale/` directory is needed
(Article VIII).

## R10. New dependencies

None. `crispy_forms.bootstrap` is part of django-crispy-forms, which is already a runtime
dependency.
