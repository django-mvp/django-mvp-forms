# Implementation Plan: Tom Select widgets for choice fields

**Branch**: `017-tom-select-widgets` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

Two widgets in `mvp_forms/widgets.py`, `TomSelect(forms.Select)` and
`TomSelectMultiple(forms.SelectMultiple)`, and one script, `mvp_forms/tomselect.js`. Each widget
draws Django's own select, writes its settings on it as JSON in `data-tom-select`, and names the
script in its media. The script starts a Tom Select control on every `select[data-tom-select]`,
with the Tom Select the page provides. Nothing in the pack's templates or template tags changes.

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7. No new dependency.
- Tom Select 2, loaded by the host project. The tests run against 2.5.2, served from
  `tests/data/`.
- No models, migrations, views or URLs in the package.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, test first | Every task writes its tests first and sees them fail |
| XIV, stock daisyUI | The select carries daisyUI's `select`, and the control is drawn by the one stylesheet already shipped. The article is amended in a pull request of its own, which merges before this one (research R7) |
| XV, fields and widgets | Both widgets arrive complete in this pull request: class, tests, README surface |
| Quality bar | README and CHANGELOG change in the task that adds each public name |

## The widgets

```python
class TomSelect(forms.Select):
    def __init__(self, attrs=None, choices=(), *, placeholder=None, clear_button=None): ...

class TomSelectMultiple(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), *, placeholder=None, clear_button=None,
                 remove_button=None, max_items=None): ...
```

- Settings are keyword-only. `placeholder` is text and not empty. `clear_button` and
  `remove_button` are `True` or `False`. `max_items` is a whole number above zero. Each is
  checked with the module's existing `Check` and a wrong value raises `ValueError` naming the
  argument. An argument a widget does not have raises Python's own `TypeError`, which names it.
- The settings stated are written as JSON in `data-tom-select`, under Tom Select's own names:
  `placeholder`, `maxItems`, and `plugins` as a list holding `clear_button` and `remove_button`
  when asked for. Nothing stated writes `{}`. The attribute is always present, because it is how
  the script finds the select.
- A lazy translation given as a placeholder passes the check as it is, and is turned into text
  in `build_attrs`, when the attribute is written, so it is read in the language of the request.
- The attribute is added in `build_attrs`, so the developer's own `attrs` are kept and the
  select is drawn the same through the pack, another pack, or Django's own rendering.
- Both name `mvp_forms/tomselect.js` in `Media`. Neither names a stylesheet.
- `mvp_forms/widgets.py` still imports Django and the standard library only.

## The script

`mvp_forms/static/mvp_forms/tomselect.js`, in the shape of `imask.js`:

- A flag on `window` makes every copy after the first return at once.
- It waits for the document to finish loading, then, if `window.TomSelect` is a function, starts
  a control on each `select[data-tom-select]` that has no `tomselect` property. Without Tom
  Select it does nothing.
- The script reads `placeholder`, `maxItems` and `plugins` from the JSON written on the select
  and passes those and `maxOptions: null` to Tom Select. Nothing else in the attribute is passed.
- After a control starts, the script copies the select's `aria-describedby` to the control's own
  input, so help text and errors stay tied to what takes focus (FR-015).
- A select that Tom Select refuses is left as it is and the script goes on to the next.
- After a control starts it sends `mvp-forms:tomselect` from the select, bubbling, with the
  instance in `event.detail.tomselect`.
- US-5 adds a `MutationObserver` on the document for added nodes. It looks only at added
  elements that are, or hold, a `select[data-tom-select]`, so the nodes Tom Select itself adds
  cost one selector match each.
- No inline script and no inline handler anywhere.

## Tests

- `tests/test_widgets.py`: one class for each widget. The attribute's JSON for each setting,
  nothing written for a setting not stated, the developer's `attrs` kept, the media, each wrong
  value refused, what the field receives and cleans for each field kind of FR-002.
- `tests/test_pack/test_tom_select_widgets.py`: drawn through `|crispy`, `{% crispy %}`,
  `|as_crispy_field` and Django's own rendering. The daisyUI classes, size, colour, variant,
  error and disabled states, the formset's empty form.
- `tests/test_tomselect_e2e.py`, marked `e2e`: pages of the test project in Chrome. What the
  script does, and nothing of Tom Select's own beyond what shows the settings arrived.
- No test asserts wording, a colour, a size in pixels or a class used only for looks. FR-013 and
  SC-004, that a control matches django-tomselect's, rest on both being drawn by the same rules
  from the same classes. They are shown side by side on the demo page and looked at in the
  walkthrough, and get no pixel test.

## The demo

A page "Tom Select widgets" at `/tom-select-widgets/` in the django-mvp shell, beside django-tomselect's
in the sidebar, and at `/tom-select-widgets/standalone/` on daisyUI's CDN build.

- The shell page loads django-tomselect's script and stylesheets and `mvp_forms/tomselect.css`,
  so one copy of Tom Select serves both kinds of control. It holds a section that puts a control
  of this package beside a django-tomselect control and a stock select.
- The standalone page loads Tom Select's complete build and its default stylesheet from a CDN,
  with integrity hashes, and has no django-tomselect control.
- Sections, added by the story that builds what they show: multiple and single, the settings,
  grouped choices with an unavailable option, a formset whose rows are added from its empty form
  kept in a `<template>`, a modal, and a form that submits and shows what it cleaned to.

## Documents

- README: a section "Tom Select widgets" after "django-tomselect", the two names in the public
  surface, and the django-tomselect section's sentences about the stylesheet reworded so the
  file is described as drawing Tom Select controls.
- CHANGELOG, under Unreleased. CONTEXT.md gains the terms and widens "Option group".
- `CONSTITUTION.md` does not change in this pull request. Article XIV is amended in its own.
- The comment at the head of `mvp_forms/tomselect.css` and the module docstring of
  `mvp_forms/widgets.py` are reworded to read true beside the new widgets.
- Decision records, written at convergence: one for the script, and ADR 0042 rewritten.

## Risks

- A later django-tomselect may stop putting Tom Select on the page. The browser test of research
  R4 fails when that happens, and the README then tells such a page to load Tom Select itself.
- Tom Select mutates the document as it starts a control, inside the observer's view. The
  observer ignores a select that already has a control, and a test holds the script twice on one
  page and adds a row.
