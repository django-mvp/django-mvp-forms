# Implementation Plan: booleans drawn as a checkbox, toggle or switch

**Branch**: `008-boolean-toggle-switch` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

`Choice` gains a fourth argument, `drawing`, beside size, colour and variant. A boolean field
states `"checkbox"`, `"toggle"` or `"switch"` wherever it states a size: in a layout, or by name
on the form's statement.

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from mvp_forms.choices import Choice, FormChoices


class SettingsForm(forms.Form):
    remember = forms.BooleanField(required=False)
    notify = forms.BooleanField(required=False)
    publish = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm", fields={"notify": Choice(drawing="toggle")}
        )
        self.helper.layout = Layout(
            "remember",
            "notify",
            Choice("publish", drawing="switch", color="primary"),
        )
```

`remember` is a checkbox, `notify` a toggle and `publish` a switch in the primary colour, all
small. A toggle and a switch are daisyUI's toggle: the same checkbox input with the class
`toggle`. A switch also carries `role="switch"`.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; daisyUI classes only, written out as
literals; no leading-underscore names; line length 88; no compatibility aliases; nothing written
to a widget that outlives the draw.

**Scale/Scope**: two modules change, no pack template changes, one demo page in two forms.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | every task is test-first; a class is asserted only as the daisyUI component or modifier a consumer depends on; no wording, order or appearance is asserted |
| II Simplicity | one argument on an existing class, one small table, no new module, no template change |
| III Anti-abstraction | no new class, no registry. The drawing rides the mechanism FS-007 built (ADR 0019) |
| IV Integration-first | story tests draw forms through `{{ form\|crispy }}` and `{% crispy form %}` and submit them |
| V Security | the class and the role come from a closed literal table. Nothing a developer typed is written to the page |
| VI Documentation | README and CHANGELOG change in the task that adds the public name |
| VII Dependencies | none added |
| VIII i18n | the pack adds no text. `InvalidChoice`'s message is for the developer |
| X Cohesion | the names and their classes stay in `Modifiers`; the drawing of one field stays in `FieldInput` |
| XI Compatibility | additive. A form that states no drawing draws the same markup (SC-003) |
| XIII Plain templates | no pack template changes; no Cotton and no django-mvp import under `mvp_forms/` |
| XIV Stock daisyUI | `toggle` and its modifiers are in the CDN build, checked against `tests/data/daisyui-classes.txt` |

No violation, so no complexity is tracked.

## Project Structure

```text
mvp_forms/choices.py                      Choice.drawing, Modifiers.drawings, toggle rows
mvp_forms/templatetags/daisyui.py         FieldInput resolves the drawing
tests/test_choices.py                     Choice and Modifiers
tests/test_templatetags/test_daisyui.py   FieldInput
tests/test_pack/test_drawings.py          new: forms drawn through the pack
tests/test_pack/test_independence.py      STATES gains forms with drawings
tests/test_pack/test_documented_examples.py   the README example
tests/forms.py                            the forms those tests draw
tests/test_demo.py                        the demo page
demo/forms.py, views.py, urls.py, menus.py, settings.py
demo/templates/demo/drawings.html, drawings_standalone.html
README.md, CHANGELOG.md, CONTEXT.md
```

## The pack

### `mvp_forms/choices.py`

- `Choice.__init__` takes `drawing: str | Inherit | None = INHERIT`, keyword-only like the other
  three. `Choice.over` merges it the same way. `None` is the ordinary drawing, as it is for the
  others, so `Choice("agree", drawing=None)` undoes a drawing stated around it.
- `Modifiers.drawings` maps each drawing's name to the component it is drawn with, written out:
  `{"checkbox": "checkbox", "toggle": "toggle", "switch": "toggle"}`.
- `Modifiers.sizes` and `Modifiers.colors` each gain a `toggle` row of literals (research R6).
  `variants` gains none.
- `InvalidChoice`'s docstring names `"drawing"` as a fourth kind. The class does not change.
- `FormChoices` does not change.

### `FieldInput`

- The merge of a field's own choice (the layout's over the one named on the form) moves out of
  `resolve_modifiers` into one method, `own_choice`, so the drawing and the modifiers read the
  same merged choice.
- `resolve_drawing` runs in `__init__`, before the modifiers, because the component depends on
  it. It returns the drawing's name, or None when none is stated. It raises `InvalidChoice` with
  `kind="drawing"` and the field's name: with the three names as `allowed` for a name outside
  the table, and with nothing allowed for any drawing stated on a field whose widget is not a
  `forms.CheckboxInput`.
- `component` returns `Modifiers.drawings[drawing]` when a drawing is stated, and the widget's
  component otherwise. With `checkbox` stated, that is the component it had anyway.
- `is_single_checkbox` is true for the component `toggle` too, so the frame draws the same label
  around it. `fixed_size` gains `toggle`. `error_modifiers` gains `"toggle": "toggle-error"`.
- `attrs` adds `role="switch"` when the drawing is `switch`.

Raised from `__init__`, a mistake surfaces from the tag and not from inside a template's
`{% if %}`, which is the rule `resolve_modifiers` already follows.

### What does not change

No template under `mvp_forms/templates/`. `FormChoices`, `DrawnButton`, the removal checkbox of a
held file, checkbox groups and the null-boolean select. A hidden boolean field, which the frame
draws before the tag is reached.

## The demo project

One page, "Checkbox, toggle and switch", in the shell (`drawings`) and standalone
(`drawings-standalone`), built the way the size, colour and variant page is: a mixin that builds
the forms, a view on `MVPTemplateView`, a view on `TemplateView`, a Cotton template for the shell
and a plain one for the standalone page, a route each, one sidebar entry and one icon.

- US1: one form that draws three boolean fields three ways, posts, and shows what it cleaned to.
- US2: each drawing in each state: off, on, with help text, required and in error, disabled.
- US3: each drawing at every size and in every colour, generated from `Modifiers`, and one field
  that overrides the form's size and colour.

## Tests

- `tests/test_choices.py`: `Choice` holds and merges a drawing; `Modifiers.drawings` names;
  the toggle rows resolve.
- `tests/test_templatetags/test_daisyui.py`: `FieldInput` for each drawing, by layout and by
  name; the two mistakes, by the error's type and attributes.
- `tests/test_pack/test_drawings.py`: one class per story, one test per acceptance scenario,
  drawing a form through the filter and the tag. Inputs are found by id and type. The component
  class and `role` are asserted because they are the behaviour a consumer depends on. Submitted
  data is asserted through `form.cleaned_data`.
- SC-003 is shown by comparing the markup of every entry in `STATES` before and after the
  change, reported and not committed, as FS-007 did for its SC-005.
- `tests/test_pack/test_independence.py`: `STATES` gains forms with each drawing, plain, in
  error and with a size and colour, so every class written is checked against daisyUI's list.
- `tests/test_demo.py`: the page answers in both forms, is in the sidebar, and draws each
  drawing in each state.

No test asserts wording, the order of classes, or where the label sits.

## Story order

US1 → US2 → US3, sequential, in the feature worktree. All three touch `FieldInput`, so they are
not built in parallel.

## Decisions to record

- A switch is daisyUI's toggle with `role="switch"` (D2). Expected to earn a record.
- The drawing is a fourth argument of `Choice` and has no form-wide counterpart (D10). Follows
  ADR 0019; judged at convergence.
