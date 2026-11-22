# Plan: Characters left under a text field

**Branch**: `020-characters-left` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

Two widgets, `CharactersLeftInput` and `CharactersLeftTextarea`, built on one mixin, write a few
`data-` attributes on the input. One script, `mvp_forms/static/mvp_forms/characters-left.js`, named in
their media, finds every input carrying the marker, draws the line under it and keeps it up to
date. The limit is the `maxlength` Django already writes from the field's `max_length`. The
textarea widget also turns the line breaks of submitted text into `\n`, so the browser, the line
and the field count alike. No dependency, field, model, view, URL or stylesheet is added.

## Python

### The mixin and the widgets (`mvp_forms/widgets.py`)

- `CharactersLeft`, a mixin, and two widgets: `CharactersLeftInput(CharactersLeft,
  forms.TextInput)` and `CharactersLeftTextarea(CharactersLeft, forms.Textarea)`.
- A module constant `CHARACTERS_LEFT_FROM = 8`, the package's number.
- `__init__(self, attrs=None, *, show_from=None)`. `show_from` is the number of characters left
  from which the line appears, and `None` takes the constant.
  - `show_from` that is not an `int`, is a `bool`, or is below one raises `ValueError` naming
    `show_from`, through `Check` as the other widgets do.
  - A `maxlength` in `attrs` raises `ValueError` naming `maxlength` and saying the limit is the
    field's `max_length` (FR-002). Raised in `__init__`, so when the form class is defined.
- `get_context(name, value, attrs)` reads `maxlength` from the widget's attributes after Django
  and the caller have merged them. Without one it raises `ValueError` naming the field, by its
  `name` (FR-002). With one, it writes, through the same attribute dictionary every renderer
  draws:
  - `data-characters-left-from`: the number. This is the marker the script finds the input by.
  - `data-characters-left-words`: a JSON list. Entry `n` is
    `ngettext("%(n)s character left", "%(n)s characters left", n) % {"n": n}`, for `n` from 0 to
    the smaller of the number and the limit.
  - `data-characters-left-over`: `gettext("Over the limit by %(n)s")`, with `%(n)s` left in for
    the script.
  - All strings are produced at render, in the active language.
- Media: a nested `Media` with `js = ["mvp_forms/characters-left.js"]` on the mixin, so each
  widget names the script and a form with none of them names nothing (FR-013).
- `CharactersLeftTextarea.value_from_datadict(data, files, name)` returns the value with `\r\n`
  and `\r` replaced by `\n` (FR-009). `None` stays `None`.
- A subclass is a subclass: nothing is registered by name, so FR-006's "same attributes under
  every renderer" holds because the attributes are the widget's own.
- The Tom Select widgets are not touched (FR-003). Nothing in the mixin refers to them.

### Translations

`ngettext` and `gettext` are the standard ones, called at render. The English catalogue
(`mvp_forms/locale/en/LC_MESSAGES/django.po`) gains the two messages, produced the way the
existing entries were.

## The script (`characters-left.js`)

Plain script, one immediately invoked function, no inline handler, no dependency.

- **Finds** `[data-characters-left-from]` inputs and textareas only. A Tom Select typing box
  never carries it, so it is left alone (FR-015).
- **Count and limit.** Limit is `input.maxLength`, and an input with none (`-1`) is left alone.
  Count is `Array.from(input.value).length`, which is Python's `len` for the same text. Left is
  limit less count.
- **Listeners** on the document, in the capture phase, for `input` and `focusin`, so rows added
  later, modals and htmx swaps need nothing (FR-014). A `MutationObserver` on the document element
  brings up to date the marked inputs inside every added node, and a scan runs once the document
  is ready, so a value drawn near its limit shows the line before anything is typed (FR-007).
- **The line.** One wrapper element `<div data-characters-left-line>` placed after the input's
  nearest `.join` or `label` ancestor, or after the input, whichever is outermost
  (this keeps it under a floating label, attached text and a joined group). Found again by
  looking at the next sibling, so a second copy of the script or a second pass draws no second
  line (FR-014). It holds:
  - a visible `<p class="label text-base-content text-wrap" aria-hidden="true">`, hidden while
    more than the number are left, showing the entry from the words table, or the over phrase
    with the number replaced when the count is above the limit (FR-004, FR-007, FR-008);
  - a visually hidden `<p class="sr-only" role="status">` that is always present, so that
    a change in it is announced. It is written only when the line first appears from a person's
    typing, a second after the last key, and at once when none are left (FR-011).
- **Nothing is cut.** The script never writes to the input's value (FR-008).
- **Classes** are daisyUI's and Tailwind's (`label`, `text-base-content`, `text-wrap`, `sr-only`),
  the help text's own, so the legibility check covers the colour (FR-018). The pack's templates
  gain nothing.
- **Without the script** the input has `maxlength` and the data attributes and is otherwise
  unchanged (FR-017).

## Documentation and the demo

- **README**: a section "Characters left" in the widgets part: how to turn it on for each of the
  two widgets and for a subclass, where the limit comes from, the number and `show_from`, the
  line break rule, what assistive technology hears, and what is not supported (Tom Select
  controls, masked and number inputs). Both widget names and `CHARACTERS_LEFT_FROM` join the
  public surface the README lists.
- **`CONTEXT.md`**: *characters-left line* and *limit* under Key Entities.
- **`CHANGELOG.md`**: an `[Unreleased]` entry under Added.
- **Demo**: `demo/docs/custom-widgets/characters-left.md` in the Custom widgets group, and one file
  per example under `demo/examples/custom_widgets/`: a text input, a textarea, a formset whose
  rows can be added (the rows are added by a script of the demo's own, since adding rows is
  django-mvp's and not this package's), and a field drawn with initial data over its limit. A
  route for each.
- **ADRs**, written at converge, numbered on from origin/main's highest:
  - the line follows `max_length` alone and appears only near the limit (D2, D3);
  - a textarea's line breaks are counted as the browser counts them (D6).

## The tests

Test structure follows `docs/contributing/standards/testing.md`: one `Test<Subject>` class per
unit, files mirroring the source, no wording, no classes used only for looks.

- `tests/test_widgets.py`: the option checks (every refusal by option name), the attributes, the
  words table for counts 0 to the number and its plural forms under a language with more than two
  (Russian, from a catalogue entry the test supplies through `translation.override` and a
  temporary catalogue), the media, the missing `max_length` error, the textarea's line break rule
  through a form (`ab\r\ncd` with `max_length=5` is valid, the cleaned value has `\n`).
- `tests/test_pack/test_characters_left.py`: through `{{ form|crispy }}`, `{% crispy form %}`,
  `{{ form.field|as_crispy_field }}` and `{{ form.as_div }}` the same attributes are written, a
  form with none of the widgets names no script in its media, and a field without the widget is
  drawn as before.
- `tests/test_characters_left_e2e.py` (Chrome, added to the e2e file list in `pyproject.toml`),
  driving a page of the test project: hidden until the number is reached; the number follows
  typing and deleting; the line hides again; none left; a pasted overflow; initial near the limit;
  initial over the limit (not cut); a textarea with line breaks to the limit and submitted;
  the status region written at the three moments and not per key; a formset row, a modal and an
  htmx swap added later; the script twice on one page gives one line; a Tom Select typing box
  beside a marked input is left alone; no script loaded means the field still stops at its limit
  and nothing throws.
- A **mutation** for each browser test is run at converge (S5): remove the observer, drop the
  hide, count code units, announce on every key.
- The legibility check: the line's classes are the help text's, so no new pairing is added; the
  task confirms that and, if the catalogue lists classes the pack writes, adds them.

## Constraints kept

| FR | Where |
|---|---|
| FR-001 to FR-003, FR-005 | the mixin and the two widgets |
| FR-004, FR-007, FR-008, FR-011, FR-014, FR-015, FR-017 | the script |
| FR-006 | attributes through `get_context`, read by every renderer |
| FR-009 | `value_from_datadict` and the script's count |
| FR-010 | `ngettext` words table, `gettext` over phrase |
| FR-012 | the pack's field templates are unchanged |
| FR-013, FR-016, FR-018 to FR-020 | media, no inline script, daisyUI classes, no new dependency |
| FR-021 to FR-023 | README, demo, `CONTEXT.md` |
