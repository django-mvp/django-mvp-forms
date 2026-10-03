# Research — 005 Tabs, accordion, modal and alert in a layout

Done on 2026-10-03 against `origin/main` at `e0e92c0` (FS-001 and FS-003 merged). Every claim
about django-crispy-forms or Django cites the installed package, `django-crispy-forms 2.7` and
`Django 6.1.1`, under `.venv/lib/python3.13/site-packages/`. Claims about daisyUI cite the
stylesheet its CDN serves at `https://cdn.jsdelivr.net/npm/daisyui@5`, fetched the same day.

## Planning notes, answered by name

### Script-free mechanisms first, an inline handler only where there is none

**Adopted.** Tabs are driven by radio inputs and an accordion group is a `details` element, so
neither needs a script. The modal is a `dialog` element. Two controls have no script-free
mechanism and carry a one-line inline handler each: the modal's close control and the alert's
dismiss control (R6, R8). The decision record written with the build says so, and issue #47 stays
open for the maintainer.

### daisyUI classes for everything daisyUI has, Tailwind layout utilities for the rest

**Adopted.** Every class the six templates write is in `tests/data/daisyui-classes.txt` except
three Tailwind layout utilities, all of which `LAYOUT_UTILITIES` in
`tests/test_pack/test_independence.py` already names: `flex`, `flex-col` and `gap-2` on the
accordion, which daisyUI has no component to stack, and `mt-4` between a tab row and its content.
No utility is added to that set.

### The pack is named daisyui

**Adopted.** The six templates live under `mvp_forms/templates/daisyui/`, at the paths
django-crispy-forms looks them up by (R1).

### Marking every tab or group with an error stays out

**Adopted.** The first tab or group holding an error opens, by django-crispy-forms' own rule
(R2). Nothing else is marked. Issue #46 stays open.

## Findings

### R1. Where django-crispy-forms looks for each template, and what it hands it

| Layout object | Template path | Context | Source |
|---|---|---|---|
| `TabHolder` | `daisyui/layout/tab.html` | the whole page context, plus `tabs`, `links`, `content` | `crispy_forms/bootstrap.py:773`, `:784-786` |
| `Tab`, as a link | `daisyui/layout/tab-link.html` | `link` only | `bootstrap.py:715`, `:722-723` |
| `Tab`, as a pane | `daisyui/layout/div.html` | `div` and `fields` only | `crispy_forms/layout.py:731`, `:750` |
| `Accordion` | `daisyui/accordion.html` | the whole page context, plus `accordion`, `content` | `bootstrap.py:875`, `:898-901` |
| `AccordionGroup` | `daisyui/accordion-group.html` | `div` and `fields` only | `bootstrap.py:831`, `layout.py:750` |
| `Modal` | `daisyui/layout/modal.html` | `modal` and `fields` only | `bootstrap.py:1102`, `:1131` |
| `Alert` | `daisyui/layout/alert.html` | the whole page context, plus `alert`, `content`, `dismiss` | `bootstrap.py:948`, `:961-963` |

Three consequences shape the design.

- The two accordion templates sit beside `field.html`, not under `layout/`. The path is
  django-crispy-forms' and the pack follows it.
- A `Tab` has no template of its own. It is a `Div`, drawn by the pack's `layout/div.html`, which
  FS-003 wrote. A `Tab` is told apart there by its `link_template` attribute, which a plain `Div`
  does not have (`LayoutObject.__getattr__`, `layout.py:41`, raises `AttributeError` for it, and
  the template engine reads that as empty).
- A `Tab` pane, an `AccordionGroup` and a `Modal` are drawn with no `form` in their context. None
  of the three templates can read `form.errors`.

### R2. Which tab or group is open is decided in Python

`ContainerHolder.open_target_group_for_form` (`bootstrap.py:656-671`) sets `active = True` on the
first container that holds a field named in `form.errors`, or on the first container when none
does. `Container.__contains__` (`bootstrap.py:609-613`) searches greedily, so a field nested in a
row, a fieldset, an accordion or a modal inside the tab is found (`layout.py:96`). A hidden
field's error is a key in `form.errors` like any other, so it counts. A form-wide error has the
key `__all__`, which no container holds, so it moves nothing.

`TabHolder.render` resets every tab first (`bootstrap.py:776-777`), so exactly one tab is active
and a developer's `active=` on a `Tab` has no effect. `Accordion.render` does not reset
(`bootstrap.py:888-901`), so a group the developer made `active=True` stays open, and a first
group made `active=False` stays closed (`bootstrap.py:666`).

The pack draws `div.active` and writes no rule of its own for tabs or groups.

### R3. daisyUI's script-free tabs need each radio directly before its content

daisyUI shows a tab's content with `.tab:checked + .tab-content` and has no other script-free
selector for it. The radio and its content must be adjacent siblings.

`TabHolder.render` builds all the panes first, then all the links, and hands the template two
joined strings (`bootstrap.py:781-784`). So the radio cannot come from `tab-link.html`: it would
be separated from its pane. The pane template draws both, the radio and then the content, and
`tab-link.html` is an empty template that exists because `render_link` loads it.

Drawing each pane a second time from `tab.html` was rejected: `render_field` records every field
it draws and reports a second drawing (`crispy_forms/utils.py:101`), raising when
`CRISPY_FAIL_SILENTLY` is off.

### R4. A tab's radio needs a group name only the holder can give

Radios form a group by sharing a `name`. The pane template sees only its own `Tab` (R1), so it
cannot know which holder it is in. It writes a fixed placeholder name, and `tab.html`, which does
see the holder, passes the joined panes through a filter that swaps the placeholder for a name
made for that one drawing.

- An inner tab holder is drawn before the outer one, so by the time an outer holder's filter runs
  the inner radios already carry their own name.
- The name is a random token (`secrets.token_hex`), not one built from ids. Two forms drawn from
  the same form class have tabs with the same ids, and a name built from them would join both
  holders into one group. A random name makes FR-020 hold with no condition on the developer.
- The swap touches a literal the pack wrote. A value a person typed cannot contain it, because
  Django escapes `"` and `<` in every value it draws. Markup a developer wrote in an `HTML`
  object could, and the only effect would be that their own input is renamed.

Storing each pane on its `Tab` and reading it back from `tab.html` was rejected. Layout objects
are often shared between requests, and one request would be able to read another's drawn fields.

### R5. The radios must not be submitted

A checked radio with a name is submitted. An empty `form` attribute gives a form control no form
owner (HTML, "reset the form owner": an attribute that names no form element leaves the owner
null), so the browser leaves it out of the submission and out of the form's `elements`. Radios
with no owner still group by name within the page. This is checked in a browser at the
walkthrough, because the test client does not serialise forms.

An accordion group is a `details` element and holds no input of its own, so it adds nothing to
the submission.

### R6. An accordion group is a `details` element with no group name

daisyUI's collapse supports a `details` element (`.collapse:is(details)`, opened by `[open]`). It
needs no input, is opened and closed from the keyboard by the browser, and is drawn open by the
`open` attribute.

daisyUI's accordion examples add a shared `name` so that opening one group closes the others.
That is left out. With a shared name the browser keeps only the first open group, and
django-crispy-forms can hand the template two (R2: a group left `active` and the group holding the
error). The group holding the error could be the one the browser closes, which is the failure the
feature exists to prevent. Without the name every group opens and closes on its own, and every
group django-crispy-forms marks active is open.

### R7. A modal can only find an error in what it was given to draw

`Modal.render` passes its template the modal and its drawn fields, and no form
(`bootstrap.py:1127-1131`). The one sign of an error the template can read is in the drawn fields.
Django marks every visible input of a field with errors `aria-invalid="true"`
(`django/forms/boundfield.py:296-297`), whether or not the form draws error messages. The modal
template passes `fields` through a filter that looks for that attribute and draws the dialog open
when it is there.

- A value a person typed cannot forge the attribute, for the reason given in R4.
- A hidden field's error is not found, since Django does not mark a hidden input invalid. Nothing
  draws that error today either: FS-002's FR-013 owns it. When it lands, the filter is the one
  place to extend.
- A subclass of `Modal` that reads `form.errors` would be exact, but the specification rules out
  layout classes of the pack's own (D1, ADR 0008).

### R8. How the modal opens and closes

daisyUI documents three ways to build a modal. The `dialog` element is the one the planning notes
name, and the one with real modal behaviour when a host project opens it with `showModal()`:
focus is held inside it and Escape closes it.

- **Drawn open.** daisyUI shows `.modal[open]`, so `<dialog class="modal" open>` is visible when
  the page arrives, with no script. `modal-open` is not used: it holds the modal open until the
  class is removed.
- **Closed by a person.** daisyUI's close control is a `<form method="dialog">`, which cannot sit
  inside the form the modal belongs to. The close control is a `<button type="button">` whose
  inline handler calls `close()` on its dialog. `close()` works on a dialog opened by the
  attribute as well as by `showModal()`, so FR-012's "still be able to close it" holds.
- **The checkbox method was rejected.** It is script-free, but its close control is a `<label>`,
  which the keyboard cannot reach and which assistive technology does not announce as a control
  (FR-010), and the open modal is not a modal to assistive technology.
- `Modal.__init__` already writes `role="dialog"`, `tabindex="-1"` and
  `aria-labelledby="<title_id>-label"` into `flat_attrs` (`bootstrap.py:1123`). The title element
  takes that id, which meets FR-009.

### R9. The alert

`Alert` is a `Div` whose class is `alert`, the same name daisyUI uses, plus `alert-block` when
`block=True` (`bootstrap.py:949-954`). A developer's `css_class` is appended, so a daisyUI modifier
such as `alert-warning` reaches the element. `alert-block` is a name written for another pack and
is dropped (ADR 0010), which is how `block` is accepted without effect (FR-017).

daisyUI has nothing for dismissing an alert. The dismiss control is a `<button type="button">`
whose inline handler removes the alert from the page. Removing rather than hiding means no class
or attribute has to win against the alert's own `display`.

### R10. Class names django-crispy-forms writes for other packs

`Tab` carries `tab-pane` and, when active, `active` (`bootstrap.py:714`, `:726-730`). `Alert`
carries `alert-block`. None is a daisyUI class. All three join `UPSTREAM_ONLY_CLASSES` in
`mvp_forms/templatetags/daisyui.py`, and the templates pass `css_class` through the existing
`daisyui_classes` filter.

### R11. What the demo and the README need

- Four pages on django-mvp's shell: tabs, accordion, modal, alert. The first three hold a form
  that can be posted empty so the right tab, group or modal comes back open (FR-024, SC-006).
- One standalone page drawing all four with daisyUI's CDN install and nothing else, following
  the standalone pages FS-001 and FS-003 added. It is what SC-003 is walked on.
- The modal page's opening control is a button in the page that calls `showModal()` on the
  modal's id, which is the way daisyUI documents for a `dialog`.
- README, *Layout objects*: the six objects, how a host project opens a modal, and the note that
  alert content is trusted (FR-016, FR-025).

### R12. No new dependency, no new term

Nothing is added to `pyproject.toml`. "Container layout object" is not needed in code or
documentation: the README names the six objects, so `CONTEXT.md` is unchanged.
