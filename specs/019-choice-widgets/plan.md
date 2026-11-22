# Implementation Plan: Choice widgets drawn as a scale, pills, chips or cards

**Branch**: `019-choice-widgets` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

Seven widgets in `mvp_forms/widgets.py`: `ScaleSelect`, `PillSelect`, `PillSelectMultiple`,
`ChipSelect`, `ChipSelectMultiple`, `CardSelect` and `CardSelectMultiple`. They subclass Django's
`RadioSelect` and `CheckboxSelectMultiple`, name templates of their own under
`mvp_forms/templates/mvp_forms/widgets/`, and are drawn with daisyUI's classes and Tailwind's
utilities. One mixin holds what the chip and card widgets share (the values on show, the fold's
words, the split into shown and folded choices). One script, `mvp_forms/choice-fold.js`, keeps a
chosen choice on show when its fold is closed. The pack's tag resolves size, colour and the error
state for these widgets into their context, as it does for a rating, and keeps `radio` and
`checkbox` off their inputs.

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7. No new dependency.
- Plain Django templates, never Cotton (README, `AGENTS.md`).
- No stylesheet. Layout classes are written out in full in the widgets' own attributes and
  templates, so a host project's Tailwind build finds them when it scans the package.
- The script is browser-tested in headless Chrome as the other scripts are.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, test first | Every task writes its tests first and sees them fail before the code |
| II and III, least machinery | One mixin for the fold, one for the card extras. Two new components in the existing modifier tables. No registry, no setting, no stylesheet |
| VIII | Every string the package writes is wrapped for translation and the English catalogue is regenerated |
| XI, public surface | Seven classes, their settings, the template paths and the script's path are public from this release and listed in the README |
| XII, scope | Widgets only. No field, model, view or URL |
| XIII | Plain Django templates. `widgets.py` imports Django and the standard library only |
| XIV | daisyUI's `join`, `btn`, `card`, `radio`, `checkbox` and Tailwind utilities |
| XV | Classes, templates, tests, README, demo and changelog arrive in this pull request |

## The widgets

```python
ScaleSelect(low="", high="", attrs=None, choices=())
PillSelect(attrs=None, choices=())
PillSelectMultiple(attrs=None, choices=())
ChipSelect(show=None, fold_label="", attrs=None, choices=())
ChipSelectMultiple(show=None, fold_label="", attrs=None, choices=())
CardSelect(show=None, fold_label="", descriptions=None, icons=None, meta=None,
           columns=2, attrs=None, choices=())
CardSelectMultiple(...same as CardSelect...)
```

- Settings are keyword-only. A setting the widget does not have is Python's own `TypeError`,
  which names it. A value that cannot be used raises `ValueError` naming the setting: `columns`
  other than 1, 2 or 3, `show` that is a string or not iterable, `descriptions`, `icons` or `meta`
  that is not a mapping.
- `show`, `descriptions`, `icons` and `meta` are replaced, never mutated in place, since a form's copy of a widget shares them by reference. `show` is a plain attribute holding a set of strings (every value passed through `str`). Django
  deep-copies a form's widgets for each form instance, so assigning `widget.show` in the form's
  `__init__` changes that form's copy alone. `None` means every choice is on show.
- `descriptions`, `icons` and `meta` are mappings keyed by choice value. Lookup is by `str(value)`
  so a model's primary key matches. A key the field does not offer is never looked at, so it is
  passed over without an error. Text not marked safe is escaped by Django's autoescape. An icon is
  drawn as the markup given: the developer marks it safe.
- A mixin, `ChoiceLayout`, carries `choice_component` (`"choice-button"` for the scale, pills and
  chips, `"choice-card"` for cards), `input_classes` (the layout's own classes for each input,
  written out in full) and the context code every widget shares:
  - `optgroups` are flattened: group names are not drawn and choices keep the field's order.
  - The choice whose value is the empty string is taken out of the order for a single-choice
    widget and given as `widget.clearing`, to be drawn after the others. A multiple widget draws it
    as any other.
  - Each option's `attrs["aria-label"]` is the label as plain text (tags dropped when marked
    safe, entities read), written by the widget itself so a form drawn without crispy-forms is
    named too. `choice_context` does not call `name_input` for these widgets. On an input drawn
    as `btn` the `aria-label` is also the text a person sees, so it holds the label alone. A
    scale's first and last inputs are named with `aria-labelledby` holding the input's own id and
    the id of their end's word element, which gives label plus end words (FR-004).
  - Each option's `attrs["class"]` is the layout's `input_classes` followed by the developer's own
    `attrs` class. The pack then appends the resolved classes (below).
- `FoldedChoices` (chip and card widgets) adds `shown`, `folded` and `fold_open` to the context.
  A choice is folded when `show` is set, its value is not in `show` and it is not chosen. A fold
  holding every choice with none chosen is open. A fold that would hold no choice is not drawn
  (`folded` empty). `fold_label` empty means the package's own words, `{n} more`, written with
  `ngettext` so the count has plural forms. The widget's `Media` names `mvp_forms/choice-fold.js`.
- `CardChoices` adds `description`, `icon`, `meta` to each option and `columns` to the context.

## The agreed look: what each layout is carried over from

Sam approved this look in an application's prototype. The prototype's paths are in the build's
brief (workspace only, never in the repository). Each piece is ported, then brought inside the
pack's rules: stock daisyUI markup, no class or stylesheet of the package's own.

| Piece of the agreed look | Becomes |
|---|---|
| Scale: a row of equal segments with a 3px gap, a tall target with the number centred, the chosen segment filled with the primary colour, the low and high words under the ends in small quiet type | `join` of `input.btn.join-item` named by `aria-label`, each `flex-1` and `h-12`, a checked segment drawn in the colour table's checked classes. Below it a `flex justify-between text-xs text-base-content/90` row, `aria-hidden`, since the words are read with the first and last segments |
| Pills: wrapping row, 0.5rem gap, rounded toggles, 2.75rem target, chosen filled, a tick before the label when a multiple pill is chosen | `div.flex.flex-wrap.gap-2` of `input.btn.rounded-full`. A multiple pill draws its tick with `checked:before:content-['✓']` |
| Chips: as pills, larger (3rem), long labels wrapping in full, the "none" choice quieter with a dashed edge and softer text | `btn rounded-3xl h-auto min-h-12 whitespace-normal`, `btn-dash text-base-content/90` for the clearing choice. The fallback in `research.md` applies if a label drawn through `aria-label` does not wrap |
| Cards: grid of one, two or three columns on a wide screen and one on a phone; icon tile at the left; short line in small capitals, bold label, softer description; round (square when multiple) mark at the right that fills when chosen; chosen card takes a primary edge and a light tint and its tile fills with primary | `grid grid-cols-1 gap-2` with `sm:grid-cols-1`, `sm:grid-cols-2` or `sm:grid-cols-3` written whole in the template, never built from `columns`. Each choice is `label.card.card-border` with `has-checked:border-primary has-checked:bg-primary/10 has-focus-visible:outline`, holding a tile `div.bg-base-200 size-9 rounded-field`, a text block, and the input drawn as `radio` or `checkbox` as the mark. The tile fills with primary through `group-has-checked` utilities |
| Fold control: a link-coloured line with a small circled plus and "N more" under the row (chips), a disclosure whose summary is a circled plus, the words and the count (cards) | One `details` for both. `summary.link.inline-flex.items-center.gap-2.min-h-11` with a circled-plus `span` that becomes a minus while open (`group-open:` utilities) |

The side-by-side check against the prototype's screens is made by the orchestrating session at
the walkthrough, with the pages served by the demo. Differences from the prototype are named in
the pull request.

## What the pack applies

All in `mvp_forms/templatetags/daisyui.py` and `mvp_forms/choices.py`.

- `component_of` returns `widget.choice_component` for a `ChoiceLayout` before it tries the class
  match, so the widgets are never a `radio` or `checkbox` component.
- `Modifiers` gains two components in the size and colour tables, written out in full:
  - `choice-button`: sizes `btn-xs` to `btn-xl`; colours `neutral` to `error`, each a string of the
    classes that draw a checked choice in that colour (`checked:bg-primary
    checked:border-primary checked:text-primary-content` and its seven siblings). No variants.
  - `choice-card` holds only the card's edge and tint (`has-checked:border-primary
    has-checked:bg-primary/10` and its siblings), resolved for colour alone. The card's mark is
    the `radio` component for `CardSelect` and `checkbox` for `CardSelectMultiple`, so its size
    and colour come from the existing tables, resolved as `removal_modifiers` resolves a second
    component for a file input. No variants.
  - These entries are Tailwind state utilities, not daisyUI names. T004 extends
    `TestModifierTables` to split an entry on whitespace and accept each name in
    `LAYOUT_UTILITIES`, and each utility the templates and tables write is added there. The
    feature's decision record extends ADR 0020 and ADR 0003 for it.
  - With no variant table a variant stated for the form resolves to nothing and one stated on the
    field raises `InvalidChoice(kind="variant")`: the existing rule in `Modifiers.resolve`.
- `attrs` writes no `class` for them (as for a rating): the classes go onto each option instead.
- `widget` gains a branch: a `ChoiceLayout` is copied and its `get_context` wrapped by
  `choice_context`, which appends the resolved size, colour and error classes to every option's
  `attrs["class"]`, sets `widget["choice_class"]` for the elements that are not inputs (the card's
  label) and `widget["labelled"]`. The field's own widget is never changed (ADR 0004, ADR 0012).
- `drawings_of` already returns nothing for a radio group that names its own templates, so a
  drawing stated for these fields raises `InvalidChoice(kind="drawing")`. A test pins it.
- The error colour: a field in error resolves the colour to the error entry (`border-error`,
  `checked:bg-error`, `radio-error`) and nothing else.
- `InlineRadios` and `InlineCheckboxes` around these widgets draw the widget as anywhere else:
  a widget with its own template is drawn by it, inline too. T004 tests it.

## The script

`mvp_forms/static/mvp_forms/choice-fold.js`, shaped as `partial-date.js` is:

- One guard variable at the top, so including it twice acts once.
- A `toggle` listener on `document`, in the capture phase (the event does not bubble), for a
  `details[data-choice-fold]` that has just closed: every checked input inside it is moved, with
  its option element, into the shown row (`[data-choice-shown]`) in the field's order (each option
  carries `data-choice-index`), and the count is written to `[data-choice-count]`. A count of zero
  removes the fold.
- Because the listener is on the document it acts on a fold added later by any script and in a
  formset row added in the browser or content swapped in by htmx, with no setup call.
- The count is written with `textContent`, so the script never parses markup. The card label and the `details` carry the `group` class that `group-has-checked:` and `group-open:` need. No inline script, no inline handler. Without the script the `details` still opens and every
  folded choice can be chosen and submitted.

## Testing

- Widget tests (`tests/test_widgets.py`, `tests/test_pack/test_choice_layouts.py`): rendered HTML
  parsed and asserted by input, name, value, order, `aria-label`, `checked`, `disabled`,
  `aria-invalid`, the fold's presence, openness and count, the `Media`, the escaping of a
  description and the drawing of a safe icon, `show` set per form instance. Cleaned data compared
  with `RadioSelect` and `CheckboxSelectMultiple` for the same submissions. Size and colour tables
  asserted by the classes they write. No test asserts wording, a colour or a width.
- Browser tests (`tests/test_choice_fold_e2e.py`, marked `e2e`): tap, tick, clear, fold and close
  keeps the chosen choice on show with the right count, a page without the script still submits
  folded choices, a row added by script and a form swapped by htmx fold, the script included twice
  acts once, keyboard operation of every widget, and a long label wraps in a chip.
- Legibility: pairings for the text of a choice and the mark of a chosen choice under every
  theme the suite measures, added to `tests/legibility/`.
- Existing tests pass unchanged: the pack's markup for every form that uses none of the widgets is
  identical (FR-026).

## Documentation

README: a "Choice widgets" section in the public surface (each widget and setting, the fold and
what a page without the script does, how a single choice is cleared, size and colour, which lists
each suits, what is unsupported), the template list and the surface list. `CONTEXT.md` gains Scale,
Pill, Chip, Card, Fold and Choices on show. `CHANGELOG.md` under Unreleased, Added. The demo gains a
Choice widgets page in the Custom widgets group. One ADR (extending ADRs 0003 and 0020, and covering the native `details` fold and its script) records that these layouts are widgets
with templates of their own whose size and colour the pack resolves into their context, and names the utilities added to the class test.

## Risks

- A label drawn through `aria-label` may not wrap or tick in a browser: the fallback is in
  `research.md` and is decided in the build against headless Chrome.
- Several siblings change `README.md`, `CHANGELOG.md`, `widgets.py` and the demo at once: the branch
  is brought up to date with `origin/main` before the ready push and whenever main moves.
