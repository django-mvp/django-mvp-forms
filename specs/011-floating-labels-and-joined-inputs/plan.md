# Implementation Plan: floating labels and joined inputs

**Branch**: `011-floating-labels-and-joined-inputs` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

Two additions, both stock daisyUI.

`Choice` and `FormChoices` gain a fifth kind of choice, `label`. Its one name is `"floating"`.
`None` is the ordinary label.

`Join` is a new layout object in a new module, `mvp_forms/layout.py`. It names several fields to
be drawn as one daisyUI join under one label.

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from mvp_forms.choices import Choice, FormChoices
from mvp_forms.layout import Join


class ContactForm(forms.Form):
    name = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea, required=False)
    country_code = forms.ChoiceField(choices=[("+49", "+49"), ("+44", "+44")])
    number = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            label="floating", fields={"notes": Choice(label=None)}
        )
        self.helper.layout = Layout(
            "name",
            "notes",
            Join("country_code", Field("number", autocomplete="tel"), label="Phone"),
        )
```

`name` has a floating label. `notes` undoes it and has its ordinary label. `country_code` and
`number` are one join under the legend "Phone", each named for assistive technology by its own
label, and the form's floating label passes them over.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms 2.7. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; daisyUI classes only, written out as
literals, and layout utilities named in the class test; no leading-underscore names; line length
88; no compatibility aliases; nothing written to a widget by the pack; every distributed
template listed in the README (ADR 0029).

**Scale/Scope**: two modules change and one is added; two pack templates change and three are
added; two demo pages, each in the shell and standalone.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | Every behaviour is written test-first. No test asserts wording, width, spacing or order of classes. |
| II Simplicity, III Anti-abstraction | No base class and no registry. `Join` is one class. The floating label reuses `Choice`, `FieldInput` and the frame. The help text and errors become a template of their own only now that a second template draws them. |
| IV Integration-first | Acceptance tests draw forms through `{{ form|crispy }}` and `{% crispy form %}`. |
| V Security | Every value is escaped by the template layer. The group's label is escaped (see *The group's label*). |
| VI Documentation | README, CHANGELOG and CONTEXT change in the task that introduces each public name. |
| VII Dependencies | None added. |
| VIII i18n | The pack adds no text of its own: every name it writes is the field's label or the developer's. |
| X Cohesion | The new behaviour is methods of `FieldInput`, `Choice`, `FormChoices` and `Join`. |
| XI Compatibility | Additive. No template path moves. `field_body.html` reads the same names plus new ones. |
| XIII Plain templates | No Cotton in `mvp_forms/`. No import of django-mvp. |
| XIV Stock daisyUI | `floating-label`, `join`, `join-item`, the frame's `fieldset` and `fieldset-legend`. One layout utility is new, `w-auto`. |

No violation to justify.

## The floating label

### `mvp_forms/choices.py`

- `Modifiers.labels: ClassVar[dict[str, str]] = {"floating": "floating-label"}`, beside
  `Modifiers.drawings`, written out as a literal.
- `Choice.__init__` gains `label: str | Inherit | None = INHERIT`. `Choice.over` merges it as it
  merges the other four.
- `FormChoices.__init__` gains `label: str | None = None`. `FormChoices.check` raises
  `InvalidChoice("label", value, tuple(Modifiers.labels))` for a name that is not in the table.
- `InvalidChoice`'s docstring names the fifth kind. The class itself does not change.

### `FieldInput`

A new method, `resolve_label`, called from `__init__` after the decorations are stored, and a
property, `can_float`.

`can_float` is true when all of these hold:

- the component is `input`, `textarea` or `select`;
- the field is not a group (`is_group`) and not a multi-widget;
- it has no attached text (`has_attached_text`), no buttons joined to it (`is_joined`), is not
  drawn inline (`unlabelled`) and is not a member of a joined group (`member`).

`resolve_label(own, choices)` returns whether a floating label is in force:

1. A hidden field takes nothing: false.
2. The value is the field's own (`own.label`) when it is not `INHERIT`, otherwise the form's
   (`choices.label`). `None` is false.
3. A value not in `Modifiers.labels` raises `InvalidChoice("label", value, allowed, target)`,
   with the field's name as `target` when the statement was its own.
4. When `can_float` is false: the field's own statement raises
   `InvalidChoice("label", value, (), field.name)`; the form's is passed over, false.
5. Otherwise true.

The result is stored as `self.floats`. A property decides what is drawn:

- `is_floating`: `self.floats` and `self.show_labels` and the field has a label and the field is
  not disabled. With labels off nothing floats and the input is named by `aria-label` as it is
  today (FR-008). A disabled field falls back to the ordinary label (FR-007). A field with no
  label text is drawn as FS-001 draws it.
- `is_disabled`: the `disabled` option, or the form field's `disabled`, or a `disabled` entry in
  the widget's own attributes.

`requires_placeholder` gains the second case: a floating input or textarea with no placeholder
of its own is given the label's plain text (FR-006). A select has no placeholder.

Nothing else in `FieldInput` changes for a floating label. The input keeps its component, its
choices, `w-full` and its error modifier, so size, colour and variant reach it exactly as they do
with an ordinary label (FR-022).

### Buttons

`DrawnButton.resolve_modifiers` refuses a label stated around a button the way it refuses a
drawing: `InvalidChoice("label", value, (), target)`. A `Choice` in a layout is checked against
everything it holds, which is the rule ADR 0020 and FS-008 set.

### The templates

`daisyui/frame.html`: the ordinary label of a field that is not a group is drawn when
`field.label and drawn.show_labels and not drawn.is_single_checkbox and not drawn.is_floating`.

`daisyui/field_body.html` gains a fourth shape, before the bare input:

```django
{% elif drawn.is_floating %}
  <label{% if field.id_for_label %} for="{{ field.id_for_label }}"{% endif %} class="floating-label">
    <span>{{ field.label }}{% include "daisyui/required_marker.html" %}</span>
    {{ drawn.render }}
  </label>
```

`label_class` is the developer's class for the ordinary label and is not written on the floating
one, whose only class is daisyUI's.

### What follows without code

- The crispy filter, the crispy tag and a formset drawn stacked all reach
  `FormChoices.lookup`, so the statement is honoured on each (FR-002).
- A formset drawn as a table draws every field with labels off, so nothing floats (research R7).
- Help text, errors, `aria-invalid`, `aria-describedby` and the read-only attribute are untouched
  (FR-005).

## The joined group

### `mvp_forms/layout.py` (new)

`InvalidMember(ValueError)`: something in a joined group that cannot be joined. It carries
`member`: the field's name, or the class name of a layout object.

`Join(LayoutObject)`:

```python
Join(*fields, label=None, css_id=None, css_class=None, **attrs)
```

- `template = "%s/layout/join.html"` and `member_template = "%s/layout/join_member.html"`.
- `fields`, `label`, `css_id`, `css_class`, and `flat_attrs` built from `attrs` with
  django-crispy-forms' `flatatt`, underscores in a name becoming hyphens, as its own layout
  objects do.
- `members()` walks what the group holds and returns one entry per field name, in order. A name
  is a member. A `Field`, and only that exact class, contributes each name it holds with its
  `attrs`. A `Choice` contributes what it holds, with itself merged over any `Choice` further
  out in the group. Anything else raises `InvalidMember` with the object's class name.
- `render(form, context, template_pack, **kwargs)`:
  1. Each member is drawn by a django-crispy-forms `Field` built for it with the member
     template and the wrapping `Field`'s attributes, held in the accumulated `Choice` when
     there is one, and rendered through `render_field`. django-crispy-forms therefore marks the
     field as rendered, applies the attributes and reports a name the form lacks, and
     `Choice.render` places the choice over any `Choice` around the group.
  2. After a member is drawn, `form[name].is_hidden` says whether its markup goes inside the
     join or beside it (research R2).
  3. A group with no members returns an empty string. A group whose members are all hidden
     returns their hidden inputs alone.
  4. Otherwise it renders its template with the flattened context plus: `join` (itself),
     `inputs` (the visible members' markup), `hidden` (the hidden members' markup), `members`
     (the visible members' bound fields, in order) and `required` (the first visible member
     that is required, or None).

A `Field`'s `wrapper_class` and `template` have no frame to apply to in a group and are not
used. The README says so.

### `FieldInput`, the `member` option

`daisyui_field field member=True as drawn`, following ADR 0023.

- A member that is not hidden and is not drawn as a lone `input` or `select` raises
  `InvalidMember(field.name)`: any other component, no component, a group or a multi-widget
  (FR-021). Resolved in `__init__`, so it is raised from the tag.
- `show_labels` is off for a member, so `requires_aria_label` names the input by the field's
  label unless the widget has an `aria-label` of its own (FR-015).
- `classes_for` writes `join-item` for a member, and in place of `w-full` writes the member's
  width: `flex-1` for an input, `w-auto` for a select, from a literal table
  `member_widths`. A class of the developer's that starts `w-` still means the pack adds none
  (research R6).
- `can_float` is false for a member, so the form's floating label passes it over and one stated
  on it raises (FR-010, FR-011).
- Size, colour, variant and the error modifier resolve as for any field (FR-023).

### The templates

`daisyui/layout/join_member.html`: a hidden field is drawn as its input; any other calls
`daisyui_field field member=True as drawn` and draws `drawn.render`.

`daisyui/field_messages.html` (new): the help text and the error element of `field`, moved out of
`field_body.html` unchanged, with the ids they have today. `field_body.html` includes it.

`daisyui/layout/join.html`:

```django
{% load daisyui %}{% with join_class=join.css_class|daisyui_classes %}
<fieldset class="fieldset"{% if join.label and form_show_labels == False %} aria-label="{{ join.label }}"{% endif %}>
  {% if join.label and form_show_labels != False %}
    <legend class="fieldset-legend{% if label_class %} {{ label_class }}{% endif %}">
      {{ join.label }}{% if required %}{% with field=required %}{% include "daisyui/required_marker.html" %}{% endwith %}{% endif %}
    </legend>
  {% endif %}
  <div{% if join.css_id %} id="{{ join.css_id }}"{% endif %} class="join w-full{% if join_class %} {{ join_class }}{% endif %}"{{ join.flat_attrs }}>{{ inputs }}</div>
  {{ hidden }}
  {% for field in members %}{% include "daisyui/field_messages.html" %}{% endfor %}
</fieldset>{% endwith %}
```

The developer's id, class and attributes go on the element that carries `join`, where
`join-vertical` has to be and where `FieldWithButtons` already puts them (FR-020).

### The group's label

The label is escaped. ADR 0025 draws a developer's text as markup only where
django-crispy-forms documents it as markup, and `Join` is this package's own. Escaped text can
also be the fieldset's `aria-label` when the helper turns labels off.

## Story order

**US1 → US2 → US3, sequential, in the feature worktree.** All three edit
`mvp_forms/templatetags/daisyui.py` and `daisyui/field_body.html`, and the README, so they cannot
run side by side.

- **US1** builds the floating label end to end, with its demo page and README section.
- **US2** builds `Join` end to end, with its demo page and README section, and the rule that a
  member takes no floating label.
- **US3** proves size, colour and variant on both, and extends both demo pages and README
  sections. It is expected to need no change under `mvp_forms/`.

There is no foundational phase. Nothing is shared by the first two stories that the first does
not itself need.

## Tests

| Module | Subject |
|---|---|
| `tests/test_choices.py` | `Choice(label=)`, its merge, `FormChoices(label=)` and its check, `Modifiers.labels` |
| `tests/test_templatetags/test_daisyui.py` | `FieldInput.resolve_label`, `can_float`, `is_floating`, the placeholder, the `member` option, a label around a button |
| `tests/test_layout.py` (new) | `Join.members`, `InvalidMember`, what `Join.render` returns for none, hidden-only and unknown members |
| `tests/test_pack/test_floating_labels.py` (new) | US-1's scenarios through the filter and the tag, and the edge cases |
| `tests/test_pack/test_joined_groups.py` (new) | US-2's scenarios through the tag, and the edge cases |
| `tests/test_pack/test_independence.py` | `STATES` gains floating and joined forms, plain and in error; `LAYOUT_UTILITIES` gains `w-auto`; `Modifiers.labels` is checked against the class list |
| `tests/test_pack/test_documented_examples.py` | The README's two examples are drawn |
| `tests/test_demo.py` | The four demo pages answer, are in the sidebar, draw what they claim, and post |

Elements are found by id, name, type, role and `for`. A class is asserted only where it is the
daisyUI component this feature writes (`floating-label`, `join`, `join-item`) or a modifier
FS-007 resolves. No test asserts a width class, the order of classes or any wording. An error is
asserted by its type and attributes.

SC-003 is demonstrated by rendering every entry of `STATES` at the base commit and after each
story and comparing. It is reported and not committed.

## The demo project

- `/floating-labels/` and `/floating-labels/standalone/`: a form to submit with an input, a
  textarea, a select, a field that opts out and a checkbox the statement passes over; a form
  that already fails, with a required field and help text; a disabled and a read-only field;
  one field stated by name on a form drawn with no layout. US3 adds sizes, colours and the
  variant.
- `/joined-groups/` and `/joined-groups/standalone/`: a country code and a number under one
  label, to submit; a group that already fails in one member; a group with help text on a
  member; a group with a disabled member and a hidden member; a group with no label; a group of
  one. US3 adds a group at each size, a coloured group with one member in error, and a `Choice`
  around a group.
- Each shell page has a `MenuItem` and an icon, as every page has. Shell pages use the shell's
  Cotton components and no `{% include %}` partial. Standalone pages load daisyUI's documented
  CDN install and nothing else.

## Documentation

- README, *Public surface*: a section "Floating labels" after "Checkbox, toggle and switch", and
  a section "Joined groups" after "A multi-widget field" under the layout objects that decorate
  a field. "What is refused and what is passed over" gains the `label` kind, what the form's
  statement passes over, and `InvalidMember`. The template list gains three rows and the rows
  for `frame.html` and `field_body.html` gain the names they now read. The demo's page list
  gains the four pages.
- CHANGELOG, under Added.
- CONTEXT: **Floating label**, **Joined group** and **Member**; **Choice** names the label as a
  fifth kind.

## Decision records, at convergence

Two are expected, numbered from what `origin/main` holds at that moment:

1. A floating label is a kind of choice, with what takes it, what it is passed over for, and the
   ordinary label on a disabled field (decisions D2 to D5).
2. `Join` is a second layout object the package defines; the group has one label and each member
   keeps its own name, help text and errors; how the width is shared (D6, D7, research R6). It
   amends ADR 0019's sentence that no second layout object is added.

## Cost estimate

Three implementer dispatches on the Sonnet tier, one design review and one code review. About
$25 to $40 of dispatched work, against a soft budget of $60.
