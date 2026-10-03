# Implementation Plan: layout objects that decorate a field

**Branch**: `004-field-decorating-layout-objects` · **Date**: 2026-10-03 · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

django-crispy-forms asks a template pack for one template per layout object. This feature adds
the six templates its nine field-decorating layout objects ask for. Each is two lines: it tells
the pack's `daisyui_field` tag how the field is decorated and then draws the one field frame
every field already uses. The decoration itself (text attached to the input, buttons joined to
it, options in a line, a disabled input, a hidden label, classed parts of a multi-widget field)
is drawn by `FieldInput` and the frame's body. A developer keeps importing the nine from
django-crispy-forms. The package gains no layout classes, no dependency, no script and no
stylesheet.

## Technical Context

**Language/Version**: Python 3.12 and 3.13
**Primary Dependencies**: Django 5.2, 6.0 and 6.1; django-crispy-forms 2.7 or later. No new dependency.
**Storage**: none
**Testing**: pytest with pytest-django, BeautifulSoup for reading drawn markup (`tests/conftest.py`, the `draw` and `draw_layout` fixtures)
**Target Platform**: any Django project that loads daisyUI 5 as its CDN install documents
**Project Type**: a published Django package with an undistributed demo project
**Constraints**: plain Django templates only; daisyUI classes for every component; a Tailwind utility only for layout and named in the class test; no import from django-mvp; no script file
**Scale/Scope**: nine new templates, three changed templates, one changed tag and class, two entries in the English catalogue, six demo pages and one standalone page

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I, testing | Every task is test-first. No test asserts wording, spacing, width or appearance. A class is asserted only where it is a daisyUI component (`input`, `select`, `label`, `join`, `join-item`, `checkbox`, `radio`, the error modifiers), which the testing standard counts as markup a host project depends on. |
| II, simplicity | Six two-line templates over the existing frame. No new dependency. |
| III, anti-abstraction | No layout classes of the pack's own. The decorations are keyword options on the one class that already draws a field's input, not a class each. |
| IV, integration-first | Tests draw a real form with a real `Layout` through `{% crispy %}`, the way a host project does. |
| V, security | Labels, choice labels, help text, errors and values are escaped by the template layer. Prepended and appended text is drawn as written, which django-crispy-forms documents, and the README says it is trusted and must be escaped first when built from input (research R9). Buttons are drawn once, by django-crispy-forms, and never rendered a second time (research R3). |
| VI, documentation | README public surface and CHANGELOG are updated in the task that adds each layout object. |
| VII, dependencies | None added. |
| VIII, i18n | The two names the pack supplies, for the parts of a split date and time, are translatable and join `mvp_forms/locale/en/LC_MESSAGES/django.po`. |
| X, cohesion | The decoration lives on `FieldInput`, the class that already decides how a field's input is drawn. |
| XI, compatibility | The template paths are the ones django-crispy-forms defines, so they are the override points a host project already expects. |
| XIII, plain templates | No Cotton in `mvp_forms/`. The existing test over every distributed template covers the new files. |
| XIV, stock daisyUI | Attached text is daisyUI's label inside an `input` or `select`. A field with buttons is daisyUI's `join`. No Tailwind utility is added. Each object keeps the arguments django-crispy-forms documents. |

One amendment to record: the frame reads `wrapper_class` from the context, which ADR 0006 said
it would not (research R5). It gets an ADR.

## Project Structure

```text
mvp_forms/
├── templatetags/daisyui.py          # FieldInput gains the decorations; daisyui_field takes them
├── locale/en/LC_MESSAGES/django.po  # gains Date and Time
└── templates/daisyui/
    ├── field.html                   # changed: the tag, then the frame
    ├── frame.html                   # new: the frame, moved out of field.html
    ├── field_body.html              # changed: attached text and joined buttons
    ├── widgets/
    │   ├── group.html               # changed: its options move to group_options.html
    │   ├── group_options.html       # new: the options of a group
    │   └── inline_group.html        # new: the same options along a line
    └── layout/
        ├── prepended_appended_text.html        # new
        ├── checkboxselectmultiple_inline.html  # new
        ├── radioselect_inline.html             # new
        ├── field_with_buttons.html             # new
        ├── uneditable_input.html               # new
        └── inline_field.html                   # new

demo/
├── forms.py                         # gains the forms for six pages
├── views.py, urls.py, menus.py      # gain six shell pages and one standalone page
├── settings.py                      # six icon names for the menu entries
└── templates/demo/
    ├── attached_text.html, inline_choices.html, field_with_buttons.html,
    │   uneditable_field.html, inline_field.html, multi_widget_field.html
    └── decorated_fields_standalone.html   # all six, on daisyUI's CDN install alone

tests/
├── forms.py                              # gains the forms these tests draw
├── test_templatetags/test_daisyui.py     # gains the decorations of FieldInput
├── test_pack/test_attached_text.py       # new
├── test_pack/test_inline_groups.py       # new
├── test_pack/test_field_with_buttons.py  # new
├── test_pack/test_uneditable_field.py    # new
├── test_pack/test_inline_field.py        # new
├── test_pack/test_multi_widget.py        # new
├── test_pack/test_documented_examples.py # gains upstream's examples for the nine
├── test_pack/test_independence.py        # gains a state for each of the six kinds
└── test_demo.py                          # gains the seven pages
```

## The pack

### One frame, told how the field is decorated

`daisyui/field.html` today holds the frame and calls the tag. The frame moves, unchanged apart
from what is listed below, to `daisyui/frame.html`, and `field.html` becomes:

```django
{% load daisyui %}
{% daisyui_field field as drawn %}{% include "daisyui/frame.html" %}
```

`frame.html` keeps the hidden-field branch at its top (`{% if field.is_hidden %}{{ field }}`), so
a decorated hidden field is drawn as a hidden input and nothing else (spec, Edge Cases). It reads
`field`, `drawn`, and the names ADR 0006 lists. `drawn` is always set by the pack template that
includes the frame, on the line before, so it is never the page's.

Every layout template is the same two lines with its own options on the tag:

| Template | Tag |
|---|---|
| `layout/prepended_appended_text.html` | `{% daisyui_field field prepended=crispy_prepended_text appended=crispy_appended_text as drawn %}` |
| `layout/checkboxselectmultiple_inline.html`, `layout/radioselect_inline.html` | `{% daisyui_field field inline=True as drawn %}` |
| `layout/field_with_buttons.html` | `{% daisyui_field field join=div as drawn %}` |
| `layout/uneditable_input.html` | `{% daisyui_field field disabled=True as drawn %}` |
| `layout/inline_field.html` | `{% daisyui_field field unlabelled=True as drawn %}` |

Each name a layout template reads bare (`crispy_prepended_text`, `crispy_appended_text`, `div`)
is one django-crispy-forms always supplies to that template (research R1). `input_size`,
`active` and `inline_class` are not read (FR-027).

**The tag**, in `mvp_forms/templatetags/daisyui.py`:

```python
@register.simple_tag(takes_context=True)
def daisyui_field(context: Context, field: BoundField, **decoration: Any) -> FieldInput:
    return FieldInput(
        field,
        show_labels=context.get("form_show_labels") != False,  # noqa: E712
        show_errors=context.get("form_show_errors") != False,  # noqa: E712
        wrapper_class=context.get("wrapper_class") or "",
        **decoration,
    )
```

**`FieldInput`** gains keyword-only arguments, each off by default and documented in its
docstring. Each arrives in the task that gives it behaviour: the first three in T001, `inline`
in T003, `join` in T005, `disabled` in T007 and `unlabelled` in T009. The tag passes any keyword
on, so it does not change again.

| Argument | Meaning |
|---|---|
| `wrapper_class: str = ""` | a class for the frame's outer element |
| `prepended`, `appended: str \| None = None` | text drawn before and after the input, as markup |
| `join: Any = None` | the `FieldWithButtons` whose buttons are joined to the input |
| `inline: bool = False` | a group's options are drawn along a line |
| `disabled: bool = False` | the input is drawn disabled, whatever the form field says |
| `unlabelled: bool = False` | no visible label, the label offered as the placeholder |

What changes inside it:

- The classes are built in two parts. `own_classes` is the widget's own class names, without
  `uneditable-input` (research R1, R7): the name joins `UPSTREAM_ONLY_CLASSES`, as ADR 0010 asks of a class daisyUI
  lacks, and `own_classes` drops that one name. An input's classes are not run through the whole
  set, which would start dropping a developer's own `active` or `error` from every input.
  `pack_classes` is the component, the width unless the
  component is fixed-size or an own class is a width, `join-item` when the field is joined, has
  a component and is not a group, and the error modifier. `css_class` stays what it is today: the two together,
  each name once.
- `has_attached_text`: a prepended or appended text is set, the component is `input` or
  `select`, and the field is not a group (a date drawn as three selects is a group). Then the input is drawn bare: its class attribute is `own_classes`, or `False` when
  there are none, which drops the attribute. `attached_class` is `pack_classes` as one string, for
  the wrapper.
- `is_joined`: `join` is set, tested by truth.
- `attrs` adds `disabled: True` when `disabled` is set. It adds `placeholder`, holding
  `label_text`, when `unlabelled` is set, the component is `input` or `textarea`, the widget sets
  no placeholder and the field has a label.
- `show_labels` is turned off by `unlabelled`, except for a single checkbox (FR-020). From
  T009 the frame and its body read `drawn.show_labels` where they read
  `form_show_labels != False` today, so
  one field can be drawn without its label. The existing `requires_aria_label` then names the
  input by `aria-label` (FR-017), and a group is named as FS-002 names one with labels off.
- `template_name` looks in `inline_templates` first when `inline` is set: the same two widget
  classes as `templates`, both naming `daisyui/widgets/inline_group.html`. The rule that a widget
  naming its own template is drawn by that template is unchanged.
- `widget` classes and names the parts of a multi-widget (see *Multi-widget fields*).

Every literal class stays written out in the module, so a host's Tailwind build finds it.

### The frame takes a wrapper class

In `frame.html` the outer element's class becomes
`fieldset{% if drawn.wrapper_class %} {{ drawn.wrapper_class }}{% endif %}`, on the `fieldset`
and on the `div`. It is escaped like any other value. This is what django-crispy-forms documents
for `wrapper_class` (FR-024), for the eight of the nine that take it (all but
`FieldWithButtons`) and for a plain `Field`.

### Attached text

In `field_body.html`, between the single-checkbox branch and the plain `{{ drawn.render }}`:

```django
{% elif drawn.has_attached_text %}
  <label class="{{ drawn.attached_class }}">
    {% if drawn.prepended %}<span class="label">{{ drawn.prepended|safe }}</span>{% endif %}
    {{ drawn.render }}
    {% if drawn.appended %}<span class="label">{{ drawn.appended|safe }}</span>{% endif %}
  </label>
```

- One wrapper holds the texts and the input (FR-001). A text that is empty or None draws no
  `span` (FR-002). With neither set, or on a widget that is not an `input` or a `select`,
  `has_attached_text` is false and the field is drawn as it would be undecorated (FR-025).
- The wrapper is a `<label>`, so the texts are part of the input's accessible name (FR-004,
  research R2). The frame's own label, help text and errors are untouched (FR-005), and so are
  the input's name and value (FR-006).
- The component, the width and the error modifier are on the wrapper. The developer's own
  classes stay on the input.
- `|safe` on the two texts is the only place the pack draws a value as markup (FR-007, FR-026).

### Inline groups

`widgets/group.html` keeps its outer `div` and includes `widgets/group_options.html`, which holds
the loop over option groups and options it has today. `widgets/inline_group.html` is the same
with `flex flex-wrap gap-4` on the outer `div` in place of `flex flex-col gap-2` (FR-009). The
frame, the fieldset and legend, the description, the checked and disabled options and the error
modifier are reached by the code FS-002 wrote (FR-010, FR-011).

### Field with buttons

In `field_body.html`, around the three branches that draw the input:

```django
{% if drawn.is_joined %}<div{% if drawn.join.css_id %} id="{{ drawn.join.css_id }}"{% endif %} class="join w-full{% if join_class %} {{ join_class }}{% endif %}"{{ drawn.join.flat_attrs }}>{% endif %}
  …the input, as today…
{% if drawn.is_joined %}{{ buttons }}</div>{% endif %}
```

`join_class` is `drawn.join.css_class|daisyui_classes`, set by a `{% with %}` around the body.
`buttons` is read only inside the joined branch, where django-crispy-forms has always supplied
it. The buttons are what FS-003 drew, in the order given, after the input (FR-012). With no
buttons the string is empty and the group holds the input alone. The input carries `join-item`
(research R3). The label, help text and errors are the frame's (FR-014).

### Uneditable field

`disabled` reaches the input through the attributes `as_widget` is given, so every widget the
pack draws shows its value and is disabled, and a group's options are each disabled (FR-015,
research R7). No class is added: ADR 0013 draws the state from the attribute. ADR 0013 also says
the pack writes no attribute for the state, and this is the one case where it does, for one
render, because the layout object asks for it. The ADR and the README are amended to say so.

### Inline field

Described under `FieldInput` above. Errors and help text are the frame's and are tied to the
input by Django as for any field (FR-019).

### Multi-widget fields

`FieldInput.widget` already returns a copy of the widget when the pack has a template for it.
For a `forms.MultiWidget` it returns a deep copy whose parts are each given, for this render:

- a class: the part's own class names, then what `pack_classes` would give a field with that
  part's widget (the component for its kind, the width, the error modifier when the field has
  errors and errors are drawn). A part with no component keeps its own classes only.
- an `aria-label`, unless the part has one or is hidden: for a `forms.SplitDateTimeWidget` the translated
  `Date` and `Time`, in that order, and for any other multi-widget the field's label text.

`SPLIT_DATE_TIME_PARTS = (gettext_lazy("Date"), gettext_lazy("Time"))` sits beside `DATE_PARTS`.
`component` stays None for a multi-widget, so no class is passed to `as_widget` and each part's
own stays (FR-021, research R6). The frame is the fieldset FS-002 draws for a group (FR-022).

This also draws a `SplitDateTimeField` with no layout object as daisyUI inputs, which was left
to this feature.

## The demo project

Six shell pages on `MVPTemplateView`, each with a route, a template on Cotton components, a
`MenuItem` and an icon name in `EASY_ICONS`, as `AGENTS.md` describes, and one standalone page,
`decorated-fields-standalone`, that draws the forms of all six with daisyUI's CDN stylesheet and
Tailwind's browser build alone (SC-005). Each story adds its page and adds its forms to the
standalone page. US1 creates the standalone page.

| Story | Route | Shows |
|---|---|---|
| US1 | `attached-text` | the three layout objects on an input and on a select, a form to post that fails when empty, and one already failing |
| US2 | `inline-choices` | inline radios and inline checkboxes, to post and already failing |
| US3 | `field-with-buttons` | a field with one button and one with several, to post and already failing |
| US4 | `uneditable-field` | an uneditable field beside an editable one |
| US5 | `inline-field` | a short form of inline fields, to post and already failing |
| US6 | `multi-widget-field` | a split date and time with a different attribute on each part, to post and already failing |

Each form has a prefix of its own so no id repeats on a page, and `novalidate` on its helper so
the browser lets an empty form through to show the errors, as the FS-005 pages do.

## Traceability

| Requirement | Task |
|---|---|
| FR-001 to FR-008, SC-004 for the three | T001 |
| FR-009 to FR-011 | T003 |
| FR-012 to FR-014 | T005 |
| FR-015, FR-016 | T007 |
| FR-017 to FR-020 | T009 |
| FR-021, FR-022 | T011 |
| FR-023 to FR-029, SC-001 to SC-003 | every pack task, for its own layout objects |
| FR-030, SC-005, SC-006 | T002, T004, T006, T008, T010, T012 |
| FR-031 | every pack task, for its own layout objects |

## Story order

US1 → US2 → US3 → US4 → US5 → US6, sequential, in the feature worktree. Every story edits
`mvp_forms/templatetags/daisyui.py`, `README.md`, `CHANGELOG.md`, `tests/forms.py` and the demo's
shared files, so they cannot run side by side. US1 moves the frame and adds the tag's options,
and the five after it each add one option's behaviour.

## Decisions to record as ADRs when the feature converges

- Developer-written text in a layout is drawn as markup (D4).
- The frame takes a wrapper class from the context, amending ADR 0006 (research R5).
- A layout object decorates a field through options on the tag that draws it, and the frame
  stays one.
- The parts of a multi-widget field are classed and named on a copy, extending ADR 0012.
- `UneditableField` is the one case where the pack writes `disabled`, amending ADR 0013.

The convergence step writes these, and updates the status lines of the ADRs they amend. No task
in `tasks.md` carries them.
