# Implementation Plan: rating and range inputs

**Branch**: `010-rating-and-range-inputs` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

Two drawings are added beside the three a boolean field has: `rating` for a single-choice field
and `range` for a number field. Each is stated wherever a drawing is stated today, with a
`Choice` in a layout or by the field's name on the form's statement.

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from mvp_forms.choices import Choice, FormChoices


class ReviewForm(forms.Form):
    score = forms.ChoiceField(choices=[(n, f"{n} stars") for n in range(1, 6)])
    volume = forms.IntegerField(min_value=0, max_value=100, step_size=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(fields={"score": Choice(drawing="rating")})
        self.helper.layout = Layout("score", Choice("volume", drawing="range"))
```

`score` is drawn as daisyUI's rating, one star for each choice, and `volume` as daisyUI's range,
limited to 0 to 100 in steps of 5. The form posts and cleans exactly as it does with a select and
a number input. From the third story on, both take a size and a colour as every other input does;
until then the README's example and the demo page state a drawing only.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; daisyUI classes only, written out as
literals; no leading-underscore names; line length 88; no compatibility aliases; nothing written
to a widget that outlives the draw.

**Scale/Scope**: two modules of the pack change, one pack template is added, one demo page in
two forms, and the existing drawings demo page names its three drawings itself.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | every task is test-first; a class is asserted only as the daisyUI component or modifier a consumer depends on; no wording, order or appearance is asserted |
| II Simplicity | two names in an existing table, one small table of which field takes which drawing, one template. No new module, no widget, no field |
| III Anti-abstraction | no new class and no registry. The drawing rides the mechanism FS-007 and FS-008 built (ADR 0019, ADR 0022), and the widget is drawn through a copy as ADR 0012 has it |
| IV Integration-first | story tests draw forms through `{{ form\|crispy }}` and `{% crispy form %}` and submit what was drawn |
| V Security | every class comes from a closed literal table. A choice's label and value are escaped by the template. Nothing a developer typed is written to the page as a class |
| VI Documentation | README, CHANGELOG and the glossary change in the task that adds the public name |
| VII Dependencies | none added |
| VIII i18n | the pack adds no text: a star is named by its choice's own label. `InvalidChoice`'s message is for the developer |
| X Cohesion | the names and their classes stay in `Modifiers`; the drawing of one field stays in `FieldInput` |
| XI Compatibility | additive. A form that states no rating and no range draws the same markup (SC-003) |
| XIII Plain templates | the new template is plain Django; no Cotton and no django-mvp import under `mvp_forms/` |
| XIV Stock daisyUI | every class written is in the CDN build, checked against `tests/data/daisyui-classes.txt`; no layout utility is added |
| XV Fields and widgets | none is added. The developer's field and widget are not changed |

No violation, so no complexity is tracked.

## Project Structure

```text
mvp_forms/choices.py                          Modifiers.drawings, rating and range rows
mvp_forms/templatetags/daisyui.py             FieldInput: which drawings a field takes, and drawing them
mvp_forms/templates/daisyui/widgets/rating.html   new
tests/test_choices.py                         Modifiers
tests/test_templatetags/test_daisyui.py       FieldInput
tests/test_pack/test_rating.py                new: a rating drawn through the pack
tests/test_pack/test_range.py                 new: a range drawn through the pack
tests/test_pack/test_independence.py          STATES gains forms with a rating and a range
tests/test_pack/test_documented_examples.py   the README example
tests/forms.py                                the forms those tests draw
tests/test_demo.py                            the demo page
demo/forms.py, views.py, urls.py, menus.py, settings.py
demo/templates/demo/rating_and_range.html, rating_and_range_standalone.html
README.md, CHANGELOG.md, CONTEXT.md
```

## The pack

### `mvp_forms/choices.py`

- `Modifiers.drawings` gains `"rating": "rating"` and `"range": "range"`.
- Third story: `Modifiers.sizes` gains a `rating` row (`rating-xs` to `rating-xl`) and a `range`
  row (`range-xs` to `range-xl`). `Modifiers.colors` gains a `range` row (`range-neutral` to
  `range-error`) and a `rating` row whose values are daisyUI's background colour classes,
  `bg-neutral` to `bg-error`, written out. `Modifiers.variants` gains neither, so a form's
  variant is passed over and a field's own raises, by the rule `Modifiers.resolve` already has.
- The docstrings of `InvalidChoice` and `Choice` say which field takes which drawing. Neither
  class changes, and `FormChoices` does not change.

### `FieldInput`: which drawings a field takes

A new method, `drawings_of`, returns the names of the drawings the field's widget takes, as a
tuple (research R7):

| The field's widget | Drawings |
|---|---|
| `CheckboxInput` or a subclass | `checkbox`, `toggle`, `switch` |
| `Select` or `RadioSelect` or a subclass, with `allow_multiple_selected` false, not a `NullBooleanSelect`, still naming its Django class's `template_name` and `option_template_name` | `rating` |
| `NumberInput` or a subclass | `range` |
| anything else | none |

`resolve_drawing` keeps its place in `__init__` and its two early returns, and then has one
rule: a name that is not among the field's drawings raises `InvalidChoice` with
`kind="drawing"`, the field's name as `target` and the field's drawings as `allowed`. That
covers every case of FR-021: an unknown name, a rating on a field that is not a single-choice
field, a range on a field that is not a number field, a rating on a widget with a template of
its own, and a boolean field's drawing on a single-choice or a number field. The name is tested
against the tuple, so a value that cannot be hashed raises `InvalidChoice` too. A hidden field
resolves no drawing, as today.

### `FieldInput`: a rating

- `is_group` is true for a rating whatever the widget, and otherwise `field.use_fieldset` as
  today. `requires_aria_required`, `requires_aria_label` and `hides_error_element` ask `is_group`
  where they ask `field.use_fieldset` today, so a select drawn as a rating is treated as a radio
  group is. The frame then draws the fieldset, the legend with the required marker, the help
  text, the errors and the description of the group with no change to any frame template.
- `widget` returns the widget a rating is drawn through (research R4): for a radio group a
  shallow copy of the field's widget, for a select a `RadioSelect` made for this draw from the
  select's attributes and choices. Either names the template `daisyui/widgets/rating.html`. The
  rating is chosen before the inline template, so `InlineRadios` around a rating draws the
  rating.
- The copy's `get_context` is wrapped, as `removal_context` wraps it for a file input, so that
  what the pack resolved reaches the template:
  - `widget.rating_class`: `rating`, then the size modifier when one resolves.
  - on every option with a value, the class: the developer's own classes, `mask`, `mask-star-2`,
    then the colour class when one resolves, or `bg-error` when the field is in error.
  - on an option whose value is empty, the developer's own classes and `rating-hidden`, with no
    mask and no colour. Empty means the empty string and nothing else: a choice whose value is
    `0` is a star.
  - on every option, `aria-label` set to the choice's label as plain text, unless the option
    already has one. The text is made by the rule `label_text` applies to the field's label,
    moved into one helper both use, so a label marked safe has its tags dropped and is escaped
    once by the template.
  - the options are handed to the template with the clearing input first, whatever its place
    among the choices, and the stars after it in the field's order. daisyUI raises every star
    before the checked input, so a clearing input drawn after the stars would show them all as
    picked on a field with no value (FR-008).
- `attrs` passes no class to the widget for a rating, so the class is written once, by the
  wrapper above. Everything else `attrs` adds is unchanged.
- A select drawn as a rating does not carry Django's own `aria-describedby` on each star: the
  fieldset carries it. `render` builds the attributes itself for that case, as it already does
  when errors are not drawn, and keeps an `aria-describedby` the developer set on the widget.
  The stars of a select and of a radio group with the same choices are then the same markup.
- A rating is never widened and never takes `join-item`.

### `daisyui/widgets/rating.html`

```django
<div{% if widget.attrs.id %} id="{{ widget.attrs.id }}"{% endif %} class="{{ widget.rating_class }}">
  {% for group_name, options, group_index in widget.optgroups %}
    {% for option in options %}
      <input type="radio" name="{{ option.name }}" value="{{ option.value|stringformat:'s' }}"{% include "daisyui/widgets/attrs.html" with widget=option %}>
    {% endfor %}
  {% endfor %}
</div>
```

One input for each choice, in the field's order, with no label element and no group name
(research R2). The wrapped context puts the clearing input first.
`checked`, `required`, `disabled` and `aria-invalid` reach each input through the option's
attributes, as they do for a radio group.

### `FieldInput`: a range

- The component is `range`. It is not fixed-size, so it takes `w-full` unless the developer's own
  class holds a width, as an input does (FR-015). `error_modifiers` gains
  `"range": "range-error"` and `"rating": "bg-error"`.
- `widget` returns a shallow copy of the field's widget with `input_type = "range"`, drawn by
  Django's own input template (research R5). The field's `min`, `max` and `step` and the
  developer's attributes are on the widget already and are kept.
- A range is one input, so the frame draws it as it draws a number input: the label tied to it,
  the help text and errors described by Django's own `aria-describedby`, `aria-invalid` and
  `disabled`.
- A range never holds attached text, because its component is not `input` or `select`.

### Size and colour (third story)

`self.modifiers` is resolved for the component as today, which also raises for a variant the
field states. For a rating the size and the colour are written in different places, so the
wrapper asks for the size alone and the stars for the colour alone, through `resolve_modifiers`
and its `kinds` argument. A range's modifiers are all on the input, through `classes_for`.

### The existing drawings demo page

`DrawingsMixin.drawing_names` in `demo/views.py` reads the whole of `Modifiers.drawings` and
states each name on a boolean field. With two more names in the table it would state a rating on
a checkbox and raise. It names the three drawings a boolean field takes instead, in the task that
adds `rating` to the table.

### What does not change

The frame templates. `FormChoices`, `Choice` and `InvalidChoice` as classes. The three drawings
of a boolean field. A field with no drawing stated. A hidden field, which the frame draws before
the tag is reached.

## The demo project

One page, "Rating and range", in the shell (`rating-and-range`) and standalone
(`rating-and-range-standalone`), built the way the "Checkbox, toggle and switch" page is: a mixin
that builds the forms, a view on `MVPTemplateView`, a view on `TemplateView`, a Cotton template
for the shell and a plain one for the standalone page, a route each, one sidebar entry and one
icon.

- US1: a form with a required rating and an optional one that can be cleared, which posts and
  shows what it cleaned to; then a rating with help text, in error and disabled.
- US2: the same form gains a range with limits and a step; then a range with help text, in error
  and disabled.
- US3: a rating and a range at every size and in every colour, generated from `Modifiers`, and
  one form whose fields override the form's size and colour.

## Tests

- `tests/test_choices.py`: the drawings table, and the rating and range rows resolve.
- `tests/test_templatetags/test_daisyui.py`: `FieldInput` for each drawing, by layout and by
  name; which drawings each kind of widget takes; every mistake of FR-021, by the error's type
  and attributes.
- `tests/test_pack/test_rating.py` and `test_range.py`: one class per story concern, one test
  per acceptance scenario, drawing a form through the filter and the tag. Inputs are found by
  id, name, type and role. Submitted data is built from the drawn inputs and asserted through
  `form.cleaned_data`, beside the same form with no drawing stated (SC-002).
- SC-003 is shown by comparing the markup of every entry in `STATES` before and after the
  change, reported and not committed.
- `tests/test_pack/test_independence.py`: `STATES` gains forms with a rating and a range, plain,
  in error and with a size and colour, so every class written is checked against daisyUI's list.
- `tests/test_demo.py`: the page answers in both forms, is in the sidebar, and draws each state.

No test asserts wording, the order of classes, a width, or where a label sits. The classes
asserted are `rating`, `rating-hidden`, `range` and the size, colour and error modifiers, because
they are the component a consumer depends on.

## Story order

US1 → US2 → US3, sequential, in the feature worktree. All three touch `FieldInput`, so they are
not built in parallel.

## Decisions to record

Judged at convergence, with numbers read from `origin/main` at that moment.

- Each kind of field has its own drawings, and a drawing is no longer a boolean field's alone
  (D2, D11). Expected to earn a record that amends ADR 0022.
- A stated drawing may set the element drawn, through a widget made for the draw, where the
  submitted value is the same (D3, D12). Expected to earn a record that amends ADR 0002.
- A rating's colour is daisyUI's background colour class on each star (D4). Expected to earn a
  record.
