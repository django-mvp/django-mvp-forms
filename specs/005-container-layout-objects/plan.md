# Implementation Plan: tabs, accordion, modal and alert in a layout

**Branch**: `005-container-layout-objects` · **Date**: 2026-10-03 · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

django-crispy-forms asks a template pack for one template per layout object. This feature adds
the templates for `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, and two
small template filters: one gives each tab holder's radios a group name of their own, the other
tells the modal template whether the fields it holds carry an error. A developer keeps importing
the six layout objects from django-crispy-forms. The package gains no layout classes, no
dependency, no script file and no stylesheet.

## Technical Context

**Language/Version**: Python 3.12 and 3.13
**Primary Dependencies**: Django 5.2, 6.0 and 6.1; django-crispy-forms 2.7 or later. No new dependency.
**Storage**: none
**Testing**: pytest with pytest-django, BeautifulSoup for reading drawn markup (`tests/conftest.py`, the `draw` and `draw_layout` fixtures)
**Target Platform**: any Django project that loads daisyUI 5 as its CDN install documents
**Project Type**: a published Django package with an undistributed demo project
**Constraints**: plain Django templates only; daisyUI classes for every component; a Tailwind utility only for layout and named in the class test; no import from django-mvp; no script file
**Scale/Scope**: seven new templates, one changed template, two filters, three more names in one constant, five demo pages

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I, testing | Every task is test-first. No test asserts wording, spacing or appearance. A class is asserted only where it is a daisyUI component (`tabs`, `tab`, `tab-content`, `collapse`, `collapse-title`, `collapse-content`, `modal`, `modal-box`, `alert`), which the testing standard counts as markup a host project depends on. |
| II, simplicity | Templates and two filters. No new dependency. |
| III, anti-abstraction | No layout classes of the pack's own and no base template shared between the six. |
| IV, integration-first | Tests draw a real form with a real `Layout` through `{% crispy %}`, the way a host project does. |
| V, security | Names, titles and field values are escaped by the template layer. Alert content is drawn as written, which django-crispy-forms documents, and the README says it is trusted. The one string the pack swaps in Python is a literal it wrote itself, replaced by a random token (research R4). |
| VI, documentation | README public surface and CHANGELOG are updated in the task that adds each object. |
| VII, dependencies | None added. |
| VIII, i18n | The two names the pack supplies, for the close and dismiss controls, are translatable. |
| X, cohesion | The two filters are decorator-registered template filters, which the article exempts. |
| XI, compatibility | The template paths are the ones django-crispy-forms defines, so they are the override points a host project already expects. |
| XIII, plain templates | No Cotton in `mvp_forms/`. The existing test over every distributed template covers the new files. |
| XIV, stock daisyUI | Tabs, collapse, modal and alert are daisyUI's own components. The only Tailwind utilities are four layout utilities the pack already uses. Each object keeps the arguments and the open-or-closed rule django-crispy-forms gives it. |

No violation to justify.

## Project Structure

```text
mvp_forms/
├── templatetags/daisyui.py          # gains two filters and three class names
└── templates/daisyui/
    ├── accordion.html               # new: Accordion
    ├── accordion-group.html         # new: AccordionGroup
    └── layout/
        ├── div.html                 # changed: a Tab is drawn by tab-pane.html
        ├── tab.html                 # new: TabHolder
        ├── tab-pane.html            # new: one Tab, its radio and its content
        ├── tab-link.html            # new, empty: django-crispy-forms loads it
        ├── modal.html               # new: Modal
        └── alert.html               # new: Alert

demo/
├── forms.py                         # gains one form per page
├── views.py, urls.py, menus.py      # gain four shell pages and one standalone page
├── settings.py                      # four icon names for the menu entries
└── templates/demo/
    ├── tabs.html, accordion.html, modal.html, alert.html
    └── containers_standalone.html   # all four, on daisyUI's CDN install alone

tests/
├── test_templatetags/test_daisyui.py     # gains the two filters and the three names
├── test_pack/test_tabs.py                # new
├── test_pack/test_accordion.py           # new
├── test_pack/test_modal.py               # new
├── test_pack/test_alert.py               # new
├── test_pack/test_documented_examples.py # gains upstream's examples for the six
├── test_pack/test_independence.py        # gains a state for each of the four
└── test_demo.py                          # gains the five pages
```

## The pack

Every template writes the developer's id only when there is one, the pack's classes first and
the developer's after them, then the object's own `flat_attrs`. `flat_attrs` is read only as an
attribute of the template's own object (`tabs.flat_attrs`, `div.flat_attrs`, `modal.flat_attrs`,
`alert.flat_attrs`), never as a bare name, because django-crispy-forms leaves earlier objects'
names in the context. Names, titles and ids go through the template engine's escaping.

### Tabs

`layout/tab.html` (context: `tabs`, `content`, and `links`, which is not drawn):

```django
{% load daisyui %}
<div{% if tabs.css_id %} id="{{ tabs.css_id }}"{% endif %} class="tabs tabs-border{% if tabs.css_class %} {{ tabs.css_class }}{% endif %}"{{ tabs.flat_attrs }}>
  {{ content|daisyui_tab_group }}
</div>
```

`layout/tab-pane.html` (context: `div`, which is the `Tab`, and `fields`):

```django
{% load daisyui %}
{% with pane_class=div.css_class|daisyui_classes %}
<input type="radio" name="daisyui-tab-group" form="" class="tab" aria-label="{{ div.name }}"{% if div.active %} checked{% endif %}>
<div{% if div.css_id %} id="{{ div.css_id }}"{% endif %} class="tab-content mt-4{% if pane_class %} {{ pane_class }}{% endif %}"{{ div.flat_attrs }}>
  {{ fields }}
</div>
{% endwith %}
```

`layout/div.html` keeps what it draws for a `Div` and gains one branch at the top: when
`div.link_template` is set, which is true of a `Tab` and of nothing else django-crispy-forms
ships, it includes `daisyui/layout/tab-pane.html` and draws nothing more (research R1).

`layout/tab-link.html` holds a template comment and no markup. django-crispy-forms renders it
for every tab and the pack does not draw the result (research R3).

- The radio is what a person uses to change tab. It is a native radio group, so the Tab key
  reaches it and the arrow keys move within it (FR-021). Its name for assistive technology is
  the tab's name, escaped (FR-022).
- `form=""` keeps it out of the submitted data (research R5, FR-019).
- `checked` follows `div.active`, which django-crispy-forms sets on exactly one tab (research R2,
  FR-002 to FR-004).
- `daisyui_classes` drops `tab-pane` and `active` (research R10).

**`daisyui_tab_group`**, in `mvp_forms/templatetags/daisyui.py`:

```python
TAB_GROUP_PLACEHOLDER = 'name="daisyui-tab-group"'


@register.filter
def daisyui_tab_group(panes: str) -> SafeString:
    """Give the radios of one tab holder a group name no other holder has."""
```

It replaces every occurrence of the placeholder in the drawn panes with
`name="tabs-<token>"`, where the token is `secrets.token_hex(4)`, made once per call. An inner
holder has already had its placeholder replaced by the time an outer one is drawn, so nested
holders get different names (research R4, FR-020). The pane template writes the placeholder as a
literal. The constant in Python and the literal in the template are the same string, and a test
draws a holder and fails if any radio still carries the placeholder name.

### Accordion

`accordion.html` (context: `accordion`, `content`):

```django
<div id="{{ accordion.css_id }}" class="flex flex-col gap-2{% if accordion.css_class %} {{ accordion.css_class }}{% endif %}"{{ accordion.flat_attrs }}>
  {{ content }}
</div>
```

`accordion-group.html` (context: `div`, which is the `AccordionGroup`, and `fields`):

```django
<details{% if div.css_id %} id="{{ div.css_id }}"{% endif %} class="collapse collapse-arrow bg-base-200{% if div.css_class %} {{ div.css_class }}{% endif %}"{{ div.flat_attrs }}{% if div.active %} open{% endif %}>
  <summary class="collapse-title">{{ div.name }}</summary>
  <div class="collapse-content">
    {{ fields }}
  </div>
</details>
```

- `open` follows `div.active` and nothing else (research R2, FR-006, FR-007).
- No `name` on the `details`, so a group the browser would otherwise close stays open (research
  R6). Every group opens and closes on its own, which also gives FR-020.
- A `details` element holds no input of its own (FR-019) and the browser operates its `summary`
  from the keyboard (FR-021).
- django-crispy-forms always gives an `Accordion` an id, a random one when the developer gives
  none, so the id is written unconditionally.

### Modal

`layout/modal.html` (context: `modal`, `fields`):

```django
{% load daisyui i18n %}
<dialog id="{{ modal.css_id }}" class="modal{% if modal.css_class %} {{ modal.css_class }}{% endif %}"{{ modal.flat_attrs }}{% if fields|daisyui_invalid %} open{% endif %}>
  <div class="modal-box">
    <h3 id="{{ modal.title_id }}-label"{% if modal.title_class %} class="{{ modal.title_class }}"{% endif %}>{{ modal.title }}</h3>
    {{ fields }}
    <div class="modal-action">
      <button type="button" class="btn" onclick="this.closest('dialog').close()">{% translate "Close" %}</button>
    </div>
  </div>
</dialog>
```

- `modal.flat_attrs` already carries `aria-labelledby="<title_id>-label"`, so the title is the
  dialog's accessible name (FR-009).
- The close control is a `type="button"` button, so it never submits the form, and closing a
  dialog leaves its inputs as they were (FR-010). Its text is its name and is translatable
  (FR-022).
- The pack draws nothing that opens the modal (FR-011). The dialog sits where the layout put it,
  inside the form element, so its fields are submitted with the rest (FR-013).
- The title carries no class of the pack's. daisyUI has no class for a modal title and a
  typography utility is not a layout utility. A developer styles it with `title_class`.

**`daisyui_invalid`**, in `mvp_forms/templatetags/daisyui.py`:

```python
@register.filter
def daisyui_invalid(fields: str) -> bool:
    """Whether drawn fields include an input Django marked invalid."""
```

It returns whether `aria-invalid="true"` occurs in the drawn fields (research R7, FR-012).

### Alert

`layout/alert.html` (context: `alert`, `content`, `dismiss`):

```django
{% load daisyui i18n %}
{% with alert_class=alert.css_class|daisyui_classes %}
<div{% if alert.css_id %} id="{{ alert.css_id }}"{% endif %} role="alert" class="{{ alert_class }}"{{ alert.flat_attrs }}>
  <span>{{ content|safe }}</span>
  {% if dismiss %}<button type="button" class="btn btn-sm btn-ghost" aria-label="{% translate "Dismiss" %}" onclick="this.parentElement.remove()">✕</button>{% endif %}
</div>
{% endwith %}
```

- `alert.css_class` always starts with `alert`, which is daisyUI's own class, followed by the
  developer's. `daisyui_classes` drops `alert-block` (research R9, FR-017).
- `content|safe` is what django-crispy-forms documents (FR-016).
- The dismiss control is a `type="button"` button named by `aria-label`, and removes the alert
  from the page (FR-015).

### The three class names

`UPSTREAM_ONLY_CLASSES` gains `tab-pane`, `active` and `alert-block`. The README's sentence
listing the names that are never drawn is updated in the task that adds each.

## The demo project

Four pages on the shell, each with a route, a view on `MVPTemplateView`, a menu entry with an
icon, and a template that extends `page_view.html` and uses Cotton components for the page
around the form. Each has a prefix on every form so no id repeats.

| Page | Route name | What it holds |
|---|---|---|
| Tabs | `tabs` | A posting form with three tabs whose second and third hold required fields. A second form, already bound and failing, whose third tab is open. |
| Accordion | `accordion` | A posting form with three groups whose third holds a required field. A second form with one group made open and one made closed by the developer. |
| Modal | `modal` | A posting form with a modal holding two required fields, and a button in the page that opens it with `showModal()`. |
| Alert | `alert` | A form with a dismissible alert, a permanent one, and one carrying a daisyUI colour modifier. |
| Standalone | `containers-standalone` | All four forms on a page with daisyUI's CDN install and nothing of the shell. |

The standalone page is one page, not four. Its job is to show the four working without the
shell (SC-003), and each shell page links to it.

## Testing

- `tests/test_pack/test_tabs.py`, `test_accordion.py`, `test_modal.py`, `test_alert.py`: one
  module per story, classes per behaviour. They draw `StructureForm` with a layout through the
  `draw_layout` fixture, unbound and bound, and find elements by id, by element and by role.
- What "open" means in a test: the `checked` attribute on the tab's radio, the `open` attribute
  on a `details` or a `dialog`. These are the attributes the browser acts on with no script.
- FR-019 is tested by what a browser would submit: every `input`, `select`, `textarea` and
  `button` inside the drawn form that has a `name` and no `form=""` is one of the form's own
  fields, and no control the pack draws has `type="submit"` or lacks a `type`.
- FR-020 is tested by drawing two holders, in one form and in two, and comparing the radios'
  group names.
- Escaping is tested with a name, a title and a field value that hold markup.
- `tests/test_templatetags/test_daisyui.py` tests the two filters and the three dropped names on
  their own.
- `tests/test_pack/test_independence.py` gains one state per object, unbound and bound, so every
  class the six templates write is checked against daisyUI's list.
- `tests/test_pack/test_documented_examples.py` gains the examples from the docstrings of the six
  classes, drawn as written (SC-001).

What a browser does with the markup (a radio with `form=""` is not submitted, `dialog[open]` is
shown by daisyUI, the inline handlers close and dismiss) is not reachable from the test client.
It is checked on the running pages before the pull request is marked ready, and listed in the
walkthrough.

## Story order

**US1 → US2 → US3 → US4, sequential, in the feature worktree.** All four add to
`mvp_forms/templatetags/daisyui.py`, `tests/test_pack/test_independence.py`, `README.md`,
`CHANGELOG.md` and the demo project's shared files, so they are not built side by side. US1
creates the standalone page and each later story adds its form to it.

## Decisions to record with the build

- How the pack's interactive layout objects work with daisyUI alone: radios, `details`, `dialog`,
  and the two inline handlers, with the reason for each (spec D5, issue #47).
- A modal that holds a field with an error is drawn open, and how the template finds the error
  (spec D3).
- A tab's radio is drawn with its pane, and the holder names the group.

Each becomes an ADR at the stage the build prescribes if it meets the bar.

## Cost estimate

Four sequential dispatches on the lighter model, one design review and one code review. Expected
$15 to $30 of dispatched work, against a hard budget of $120.
