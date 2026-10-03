# Implementation Plan: layout objects for structure and buttons

**Branch**: `003-structure-and-button-layout-objects` · **Date**: 2026-10-03 · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

django-crispy-forms asks a template pack for one template per layout object. This feature adds
those templates for the thirteen objects the specification names, a small filter that drops the
class names django-crispy-forms writes for other packs, and one include in the form wrapper so
buttons added to a form helper are drawn. A developer keeps importing the layout objects from
django-crispy-forms. The package gains no layout classes, no dependency and no stylesheet.

## Technical Context

**Language/Version**: Python 3.12 and 3.13
**Primary Dependencies**: Django 5.2, 6.0 and 6.1; django-crispy-forms 2.7 or later. No new dependency.
**Storage**: none
**Testing**: pytest with pytest-django, BeautifulSoup for reading drawn markup (`tests/conftest.py`, the `draw` fixture)
**Target Platform**: any Django project that loads daisyUI 5 as its CDN install documents
**Project Type**: a published Django package with an undistributed demo project
**Constraints**: plain Django templates only; daisyUI classes for every component; a Tailwind utility only for layout and named in the class test; no import from django-mvp
**Scale/Scope**: eleven templates, one filter, one include in an existing template, one demo page pair

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I, testing | Every task is test-first. No test asserts wording, spacing, alignment or which utility arranges a row. A class is asserted only where it is a daisyUI component (`btn`, `fieldset`, `fieldset-legend`), which the testing standard counts as markup a host project depends on. |
| II, simplicity | Templates and one filter. No new dependency. |
| III, anti-abstraction | No layout classes of the pack's own, no base template shared between containers. Three containers that happen to carry the same four utilities stay three short templates. |
| IV, integration-first | Tests draw a real form with a real `Layout` through `{% crispy %}`, the way a host project does. |
| V, security | Context values are escaped by the template layer (research R7). No value is joined into markup in Python. |
| VI, documentation | README public surface and CHANGELOG are updated in the task that adds each object. |
| VII, dependencies | None added. `crispy_forms.bootstrap` is part of a dependency already declared. |
| VIII, i18n | The pack adds no text. |
| X, cohesion | The one filter is a decorator-registered template filter, which the article exempts. |
| XI, compatibility | The template paths are the ones django-crispy-forms defines, so they are the override points a host project already expects. |
| XIII, plain templates | No Cotton in `mvp_forms/`. The existing test over every distributed template covers the new files. |
| XIV, stock daisyUI | `fieldset`, `fieldset-legend` and `btn` are daisyUI's. Layout utilities are used only where daisyUI has no component (research R4). Each object behaves as django-crispy-forms documents. |

No violation to justify.

## Project Structure

```text
mvp_forms/
├── templatetags/daisyui.py          # gains the daisyui_classes filter
└── templates/daisyui/
    ├── whole_uni_form.html          # gains one include, of inputs.html
    ├── inputs.html                  # new: buttons added to the form helper
    ├── multifield.html              # new: a field inside a MultiField
    └── layout/                      # new directory
        ├── div.html
        ├── row.html
        ├── column.html
        ├── fieldset.html
        ├── multifield.html
        ├── baseinput.html           # Submit, Reset, Button, Hidden
        ├── button.html              # StrictButton
        ├── buttonholder.html
        └── formactions.html

demo/
├── forms.py                         # gains the layout forms
├── views.py, urls.py, menus.py      # gain the layout objects page pair
├── settings.py                      # one icon name for the menu entry
└── templates/demo/
    ├── layout_objects.html
    └── layout_objects_standalone.html

tests/
├── forms.py                         # gains the forms the layout tests draw
├── templates/tests/own_container.html   # a developer's own template, for FR-019
├── test_templatetags/test_daisyui.py    # gains TestDaisyuiClasses
├── test_pack/test_structure.py      # new: Div, Row, Column, Fieldset, MultiField
├── test_pack/test_buttons.py        # new: the four buttons, the two holders, helper buttons
├── test_pack/test_raw_content.py    # new: HTML and Hidden
├── test_pack/test_documented_examples.py  # new: upstream's own examples
├── test_pack/test_independence.py   # gains layout states and the layout utilities
└── test_demo.py                     # gains the layout objects pages
```

`HTML` has no template: django-crispy-forms renders it itself (research R1).

## The pack

### The templates

Each template writes the developer's id only when there is one, the pack's classes first and the
developer's after them, then `flat_attrs`, then the already-rendered contents. Those contents
are safe strings already, so no template adds `|safe` except for a `MultiField`'s label. The
names each one reads are those in research R1 and no others. `flat_attrs` is read only as an
attribute of the template's own object, never as a bare name: django-crispy-forms leaves earlier
objects' names in the context.

| Template | Element | The pack's classes |
|---|---|---|
| `layout/div.html` | `div` | none. With no developer class it has no `class` attribute. |
| `layout/row.html` | `div` | `flex flex-col gap-4 md:flex-row` |
| `layout/column.html` | `div` | `flex-1 min-w-0` |
| `layout/fieldset.html` | `fieldset`, with a `legend` only when the legend is not empty | `fieldset`, and `fieldset-legend` on the legend |
| `layout/multifield.html` | `fieldset`, with a `legend` only when the label is not empty | `fieldset`, and `fieldset-legend` on the legend |
| `multifield.html` | includes `daisyui/field.html` | the field frame's own |
| `layout/baseinput.html` | `input` | what django-crispy-forms wrote, through `daisyui_classes` |
| `layout/button.html` | `button` | what django-crispy-forms wrote, inside `flat_attrs` |
| `layout/buttonholder.html` | `div`, with no `flat_attrs`: a `ButtonHolder` accepts none | `flex flex-wrap gap-2 mt-4` |
| `layout/formactions.html` | `div` | `flex flex-wrap gap-2 mt-4` |
| `inputs.html` | `div`, only when the helper has buttons | `flex flex-wrap gap-2 mt-4` |

Points that are easy to get wrong:

- **`baseinput.html`** writes `type`, `name`, `value`, then `class` and `id` unless the input is
  hidden, then `flat_attrs`. The name is slugified when it is more than one word, as the
  Bootstrap packs do. A hidden input has no `class` and no `id` (research R2).
- **`button.html`** is `<button{{ button.flat_attrs }}>{{ button.content }}</button>`. The id,
  class and type are already in `flat_attrs`.
- **`layout/multifield.html`** passes `multifield.css_class` and `multifield.label_class` through
  `daisyui_classes`, so `ctrlHolder`, `blockLabel` and `error` are not drawn. The label is printed
  as written, marked safe.
- **`multifield.html`** is one line, an include of the field frame. A field inside a `MultiField`
  keeps its label, help text and errors (research R5).
- **`whole_uni_form.html`** includes `daisyui/inputs.html` after `daisyui/display_form.html` and
  inside the form element. `inputs.html` loops over `inputs` and includes
  `daisyui/layout/baseinput.html` for each, so a helper-added button and a button in a layout are
  drawn by one template (FR-014).

### The `daisyui_classes` filter

In `mvp_forms/templatetags/daisyui.py`, beside the input tag:

```python
UPSTREAM_ONLY_CLASSES = frozenset({"btn-inverse", "ctrlHolder", "blockLabel", "error"})


@register.filter
def daisyui_classes(value: str | None) -> str:
    """Return a class string without the names written for other template packs."""
```

It splits the string, drops the names in the set, drops repeats while keeping order, and joins
what is left. `None` and an empty string give an empty string. The names are literals in one
constant, so the list is easy to find and to extend.

It does not add `btn`. django-crispy-forms writes `btn` on all four buttons itself, and the
button tests fail if a later release stops.

### What the pack leaves to django-crispy-forms

- Which fields are drawn, in what order, and what happens to a field named twice or not at all.
- Rendering a legend, an `HTML` object, a button's value and a `StrictButton`'s content as
  templates.
- A layout object's own `template=` argument.

## The demo project

`LayoutObjectsMixin` in `demo/views.py` builds four forms. Each form builds its own layout in
`__init__`, and every `css_id` and button name in it carries the form's prefix, so no id repeats
on the page. A layout object is never shared between two forms (research R7):

1. **A form to submit.** Its layout holds a `Fieldset` whose legend reads a context value, a `Row`
   of two `Column`s, a `Div` with an id, a `MultiField`, an `HTML` object, a `Hidden`, and a
   `FormActions` with `Submit`, `Reset`, `Button` and `StrictButton`. Its fields are required, so
   submitting it empty brings it back with errors.
2. **The same layout bound to data that fails**, with `form_tag` off, so errors inside nested
   containers can be seen without submitting.
3. **A form with no layout** whose buttons were added with `add_input`.
4. **A small layout** that puts two fields straight in a `Row` with no `Column`, the way
   django-crispy-forms' own documentation writes it, and ends in a `ButtonHolder`.

Stories add to the page as they land: US1 creates the page pair with the structural objects, US2
adds the buttons, US3 the `HTML` and `Hidden` objects, US4 the `MultiField`.

`LayoutObjectsView` (on `MVPTemplateView`) draws them inside the shell with Cotton components for
the page around the forms. `StandaloneLayoutObjectsView` draws them on a page that loads daisyUI's
CDN install and nothing else. Each page links the other. The sidebar gains one entry.

## Tests

- **`test_structure.py`**: `TestDiv`, `TestRowAndColumn`, `TestFieldset`, `TestMultiField`,
  `TestNesting`. Each container holds its fields in layout order, carries the developer's id,
  classes and attributes, and keeps the pack's classes beside the developer's. A legend names the
  group, an empty one is not drawn, a context value in it is filled in and escaped. A field's
  error inside nested containers is drawn in the field's own frame and the input's
  `aria-describedby` names it. Every field is drawn exactly once. An empty container draws and
  raises nothing. A `Column` outside a `Row` and a `Row` holding a field directly both draw. A
  container given its own template is drawn with it.
- **`test_buttons.py`**: `TestBaseInputs` (type, name and value for each of the three, `btn`
  present, the developer's id, classes and attributes, `btn-inverse` absent, a `disabled`
  attribute passed through), `TestStrictButton`, `TestHolders`, `TestHelperButtons` (a
  helper-added button is the same element with the same attributes as one in a layout, it sits
  inside the form element, and a form with `form_tag` off still draws its layout's buttons).
- **`test_raw_content.py`**: `TestHTML` (position between two fields, inside each container, a
  context value escaped, markup kept), `TestHidden` (type, name and value, no class, an attribute
  given as a keyword arrives, inside the form).
- **`TestDaisyuiClasses`** in `test_templatetags/test_daisyui.py`: the filter, parametrised.
- **`test_independence.py`**: the parametrised states gain a layout that uses all thirteen objects,
  unbound and invalid, and a helper with added buttons. `LAYOUT_UTILITIES` gains the nine
  utilities by name. This one drawn layout is also the demonstration of SC-001.
- **Documented examples (SC-002)**, `test_documented_examples.py`: one parametrised test draws the
  example from each object's own docstring in django-crispy-forms 2.7, where it has one, against a
  form that has the fields it names, and checks it draws without raising and holds each named
  field once. Three examples do not parse as printed (`ButtonHolder`, `FormActions`, `Column`) and
  are repaired by quoting the string and nothing else. The four input objects' examples are
  direct calls, so they are built with the same arguments and placed in a layout. `MultiField`
  has no example.
- **`test_demo.py`**: both pages respond, hold every one of the thirteen objects' elements by id or
  name, come back from a post with a field error, repeat no id, and link each other. The
  standalone page carries only daisyUI's stylesheet.

FR-005 and the look of every container are judged on the demo pages. No test pins a utility.

## Story order

**US1 → US2 → US3 → US4, sequential, in the feature worktree.** They share `test_demo.py`, the
demo page, the README section and the class test, so they do not run side by side. US3 and US4
are small and are built in one dispatch.

There is no foundational phase. FS-001 delivered the field frame, the form wrapper and the test
fixtures everything here stands on.

## Decisions to record

Graduate to `docs/adr/` when the build converges, numbered from the next number free on
`origin/main` at that point:

- Layouts use django-crispy-forms' own layout classes (D1).
- How a row arranges its columns, and the utilities the button containers use (D4, research R4).
- Class names written for other packs are dropped by name, and the buttons keep the daisyUI
  names django-crispy-forms already writes (research R2).

Recorded in `decisions.md` only: buttons added to the helper are placed by this feature (D10); a
field inside a `MultiField` keeps its own errors (D11); a hidden input has no class and no id
(D12).
