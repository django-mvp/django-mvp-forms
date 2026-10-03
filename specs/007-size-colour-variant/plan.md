# Implementation Plan: size, colour and variant chosen from Python

**Branch**: `007-size-colour-variant` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

A developer states a size, a colour and a variant once, on the form's helper, and the pack adds
daisyUI's modifier for each to every input and button it draws. One field or one button states
its own with a layout object, `Choice`, or by name on the form-wide statement.

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from mvp_forms.choices import Choice, FormChoices


class SettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm",
            color="primary",
            variant="ghost",
            button_color="neutral",
            button_variant="outline",
            fields={"notes": Choice(color=None)},
        )
        self.helper.layout = Layout(
            Choice("search", size="lg"),
            "name",
            "notes",
            Submit("save", "Save"),
            Choice(Submit("delete", "Delete"), color="error"),
        )
```

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms 2.7. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Target Platform**: any Django project that loads daisyUI 5

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; daisyUI classes only, written out as
literals; no leading-underscore names; line length 88; no compatibility aliases; nothing written
to a widget or a layout object that outlives the draw.

**Scale/Scope**: one new module, one tag-library change, three template changes, one demo page in
two forms.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | every task is test-first; classes are asserted only as the daisyUI modifier a consumer depends on; no wording, order or appearance is asserted |
| II Simplicity | one module, one statement for the form, one layout object. No dependency |
| III Anti-abstraction | no base class, no registry. `Choice` serves both the layout and the by-name mapping, so there is one class and not two |
| IV Integration-first | story tests draw forms through `{{ form\|crispy }}` and `{% crispy form %}` as a host project does |
| V Security | every class the pack writes comes from a closed literal table. Nothing a developer or a user typed is written as a class by this feature. A button's attributes are extended inside the already-escaped string django-crispy-forms built |
| VI Documentation | README public surface and CHANGELOG change in the story that adds each public name |
| VII Dependencies | none added |
| VIII i18n | `InvalidChoice`'s message is a developer-facing exception, not user-facing text. The demo page's text is in the demo, which is not distributed |
| X Cohesion | the table and its resolution are one class, `Modifiers`. Button drawing is one class, `DrawnButton`, beside `FieldInput` |
| XI Compatibility | additive. A form that states nothing draws the same bytes (SC-005) |
| XIII Plain templates | no Cotton in `mvp_forms/`. The new module imports from Django and django-crispy-forms only |
| XIV Stock daisyUI | every class is one the CDN build defines, checked against `tests/data/daisyui-classes.txt` |

No violation, so no complexity is tracked.

## Project Structure

```text
mvp_forms/
  choices.py                         new: INHERIT, InvalidChoice, Modifiers, Choice, FormChoices
  templatetags/daisyui.py            FieldInput takes choices; DrawnButton; daisyui_button tag;
                                     daisyui_removal_checkbox filter
  templates/daisyui/layout/baseinput.html           class from the drawn button
  templates/daisyui/layout/button.html              attributes from the drawn button
  templates/daisyui/widgets/clearable_file_input.html   removal checkbox takes size and colour
demo/
  forms.py, views.py, urls.py, menus.py             one page, in the shell and standalone
  templates/demo/choices.html, choices_standalone.html
tests/
  test_choices.py                    mirrors mvp_forms/choices.py
  test_templatetags/test_daisyui.py  FieldInput and DrawnButton with choices
  test_pack/test_choices.py          the stories, drawn through the filter and the tag
  test_pack/test_independence.py     the table against daisyUI's class list; new states
  test_pack/test_documented_examples.py   the README's example
  test_demo.py                       the demo page
  forms.py                           forms for the above, by addition
docs/adr/                            records written at convergence
README.md, CHANGELOG.md, CONTEXT.md
```

## The pack

### `mvp_forms/choices.py`

**`INHERIT`**: a module constant, the default of every argument of `Choice`. It means "not
stated here". A developer never has to write it.

**`InvalidChoice(ValueError)`**: raised for every mistake. Attributes: `kind` (`"size"`,
`"color"` or `"variant"`), `value` (what was stated), `allowed` (a tuple of the names allowed, in
daisyUI's order) and `target` (the field's name, or the button's name or content, or `None` when
the statement was the form's). Its message is built from those four.

**`Modifiers`**: the table and the resolution.

- `sizes`, `colors`, `variants`: each a dict from component (`"input"`, `"textarea"`, `"select"`,
  `"file-input"`, `"checkbox"`, `"radio"`, `"btn"`) to a dict from daisyUI's name to the class,
  every class written out as a literal string. A comment says why they are not built from the
  component's name.
- Two families a statement is checked against, inputs and buttons: the names allowed for a
  family are the union over its components, in table order.
- One classmethod resolves a component's classes from the statements that apply to it and raises
  `InvalidChoice`. Its rules, per kind of choice:
  1. The field's or button's own statement wins when it is not `INHERIT`; otherwise the form's.
  2. `None` means the pack's ordinary drawing: no class.
  3. A name not allowed for the family raises, with `target` set when the statement was the
     field's or button's own.
  4. A name the component has no modifier for is passed over when the statement was the form's,
     and raises when it was the field's or button's own, with `allowed` listing what that
     component has. A widget with no component at all is the same case with nothing allowed.
  5. A field drawn as in error leaves the colour out.

**`Choice(LayoutObject)`**: `Choice(*fields, size=INHERIT, color=INHERIT, variant=INHERIT)`.

- Holding nothing, it is a value: `FormChoices(fields={"search": Choice(size="lg")})`.
- In a layout it renders what it holds, in order, with itself placed in the context under
  `Choice.context_name` (`"daisyui_choice"`). A `Choice` inside a `Choice` is merged over the
  outer one, each kind separately, before it is placed. `render` pushes one context layer and
  removes that same layer afterwards by identity, because django-crispy-forms leaves layers of
  its own on top (research R3).
- It applies to every field and button inside it, at any depth, so it may hold a `Row` or a
  `FormActions`.
- `over(outer)` returns the merged `Choice`; it is what nesting and the by-name mapping both use.

**`FormChoices`**: `FormChoices(*, size=None, color=None, variant=None, button_color=None,
button_variant=None, fields=None)`. Set as `helper.daisyui`. `size` reaches inputs and buttons;
`color` and `variant` the inputs; `button_color` and `button_variant` the buttons (decisions D1).
`fields` maps a field's name to a `Choice`.

- `FormChoices.attribute` is `"daisyui"`, the helper attribute and context name.
- A classmethod finds the statement for a draw: the context's value under that name, else the
  `daisyui` attribute of `form.helper` when a form is at hand, else nothing. A value that is not a
  `FormChoices` raises `TypeError`.

### The precedence, for one field

placed `Choice` (layout) over `fields[name]` over the form's. Each of the three kinds separately
(FR-004, FR-010). A field that states the form's own value is drawn with one class (the class
string is already de-duplicated).

### `FieldInput`

- Gains two arguments, `choices` (the `FormChoices` or `None`) and `placed` (the `Choice` from
  the context or `None`), both defaulting to `None` so existing callers are unchanged.
- Resolves its modifier classes **in `__init__`**, so a mistake raises from the tag and never
  from inside a template `{% if %}` (research R6).
- `css_class` puts them straight after the component, before the width and the error modifier.
- With nothing stated the list is empty and the class string is byte-for-byte what it was.

`daisyui_field` passes the `FormChoices` found from the context and the field's form, and the
placed `Choice` from the context.

### Buttons

**`DrawnButton`**, beside `FieldInput`: built from a button object, the `FormChoices` and the
placed `Choice`. It resolves the `btn` modifiers in `__init__` from `size`, `button_color` and
`button_variant` and the placed choice. Its target for an error is the button's `name`, or its
`content` for a `StrictButton`.

- `css_class`: for `Submit`, `Reset` and `Button`. The button's `field_classes` cleaned as
  `daisyui_classes` cleans them today, then the modifiers, de-duplicated.
- `flat_attrs`: for `StrictButton`. The button's own `flat_attrs` with the modifiers added inside
  its `class` attribute, and returned unchanged when there are none. The string was escaped by
  `flatatt`, so a quote can only end an attribute, and a `StrictButton` always has a `class`.

`{% daisyui_button input as drawn %}` returns it. `baseinput.html` writes `drawn.css_class`
where it writes the filter's output today, for a visible input only; a hidden one is unchanged.
`button.html` writes `drawn.flat_attrs`. Both templates are also what `inputs.html` draws
helper-added buttons with, so those take the form's choices with no further change.

The `daisyui_classes` filter stays: `multifield.html` uses it.

### The removal checkbox

`clearable_file_input.html` writes the removal checkbox's class through a new filter,
`daisyui_removal_checkbox`, applied to the file input's class string. It returns `checkbox` and
the checkbox's modifier for each size and colour modifier of `file-input` found in the string
(research R7). With nothing stated it returns `checkbox`, as today.

### What does not change

Labels, help text, error text, the frame, `aria-` attributes, `required`, `disabled`, `readonly`
(FR-019). Hidden inputs (FR-009). The width class. The error modifier.

## The demo project

One page, "Size, colour and variant", in the shell (`/choices/`) and standalone
(`/choices/standalone/`), built as the three existing pairs are: a mixin that builds the forms,
an `MVPTemplateView` and a `TemplateView`, a menu entry, a route each. The shell page uses Cotton
components for its sections, as `layout_objects.html` does. The standalone page is daisyUI's CDN
build alone.

The forms are generated from the table, so the page cannot fall behind it:

- one small form per size, each with one of every kind of input and a button
- one per colour, the same
- one for the input variant, and one button bar holding a button in each button variant
- one form that states choices for the form, overrides one field with a `Choice` in its layout,
  one field by name, undoes the colour for one field, and overrides one button
- every form is drawn with `{% crispy %}` and `form_tag = False`: none of them posts anywhere

## Tests

- `tests/test_choices.py`: `Modifiers` rule by rule; `Choice.over`; `FormChoices`' lookup;
  `InvalidChoice`'s attributes. The message is asserted only for holding the allowed names, which
  are data.
- `tests/test_templatetags/test_daisyui.py`: `FieldInput` and `DrawnButton` with choices.
- `tests/test_pack/test_choices.py`: one class per story, each scenario of the spec drawn through
  the filter, the tag or both as the scenario says. SC-005 is asserted by drawing the same form
  with and without an empty `FormChoices` and comparing the markup.
- `tests/test_pack/test_independence.py`, by addition: every class in the table is in daisyUI's
  list (FR-016, SC-004); new entries in `STATES` for a form with every choice stated.
- `tests/test_pack/test_documented_examples.py`: the README's example draws.
- `tests/test_demo.py`: the page is in the sidebar, both pages respond, every size, colour and
  variant in the table appears at least once on an input and on a button where buttons have it,
  and the override form holds a field and a button that differ from the form's choice.

No test asserts wording, order of classes or anything a person judges by eye.

## Story order

US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree. US1 carries the foundation
(`choices.py`'s table and `FormChoices`). US4 follows US3 because it reports mistakes on buttons
too.

## Decisions to record

Written at convergence, numbered from `origin/main` at that moment: where a choice is stated
(the helper attribute and the one layout object, amending ADR 0008); the closed set of daisyUI's
names and the literal table (D2); size shared and colour and variant held twice (D1). The rest
stay in `decisions.md`.
