# Implementation Plan: Input mask widgets for IMask

**Branch**: `015-input-mask-widgets` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

Four widgets in a new module, `mvp_forms.widgets`, each a `forms.TextInput` subclass that writes
its options as JSON in `data-imask`, and one script, `mvp_forms/static/mvp_forms/imask.js`, named
in their media, that applies IMask to each such input. The approved prototype is on the branch.
Its demo page is kept as approved. The widgets and the script behind it are rebuilt test-first.

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7. No new dependency of the
  package, and no new development dependency: `pytest-playwright` is already installed.
- IMask 7, loaded by the host project. A copy of 7.6.1 under `tests/data/` serves the browser
  tests and is not distributed.
- No models, migrations, views or URLs in the package.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, test first | Every task writes its tests first and sees them fail. Code from the prototype is removed or broken for the red step |
| III, least machinery | One base class holding what the four share, three block classes with an `__init__` and one method. No registry, no settings, no dataclass |
| XI, public surface | The four widgets, the three blocks, the attribute `data-imask`, the script's path and the event's name are public from this release and are listed in the README |
| XII, scope | Widgets only |
| XIII, independence | The module imports Django alone |
| XIV | Untouched: no class, no stylesheet |
| XV | Class, tests and README entry arrive in this pull request |

## The widgets

`MaskInput(forms.TextInput)` is the base: it holds the options, names the script in `Media`, and
adds `data-imask` in `build_attrs`. It is not exported as public surface and is not documented as
a widget to use.

| Widget | Positional | Keyword-only options |
|---|---|---|
| `PatternMaskInput` | `mask`, `attrs` | `definitions`, `blocks`, `lazy`, `placeholder_char`, `overwrite`, `eager`, `display_char` |
| `RegexMaskInput` | `mask`, `attrs` | `flags` |
| `NumberMaskInput` | `attrs` | `scale`, `thousands_separator`, `radix`, `map_to_radix`, `pad_fractional_zeros`, `normalize_zeros`, `min_value`, `max_value`, `autofix` |
| `DynamicMaskInput` | `masks`, `attrs` | none |

Blocks: `RangeBlock(minimum, maximum, *, max_length, autofix, placeholder_char)`,
`EnumBlock(values, *, placeholder_char)`, `PatternBlock(mask, *, repeat, placeholder_char)`.

What is refused, each with a `ValueError` naming the option:

- pattern: an empty or non-text `mask`; a definition whose key is not one character or whose
  value is not text; a `placeholder_char` or `display_char` that is not one character; a
  `placeholder_char` mapping whose key is not `0`, `a`, `*` or a stated definition; a block that
  is not one of the three classes; `overwrite` other than true, false or `"shift"`; `eager` other
  than true, false, `"append"` or `"remove"`
- regular expression: an empty or non-text `mask`, which refuses a compiled Python pattern;
  `flags` holding a character JavaScript does not have
- number: a negative `scale`; a `thousands_separator` or `radix` longer than one character; a
  `thousands_separator` equal to the decimal mark in force, which is a comma when `radix` is not
  stated; a `min_value` or `max_value` that is not an `int`, a `float` or a `Decimal`;
  `min_value` above `max_value`
- dynamic: an empty list; an item that is not one of the other three widgets
- range block: `minimum` above `maximum`. Enum block: an empty list

The number widget also sets `inputmode`, `decimal` or `numeric` when `scale` is zero, unless the
developer's `attrs` state one, and overrides `value_from_datadict` and `format_value` as research
R5 describes.

## The script

One immediately invoked function. In order: return if the flag on `window` is set, and set it;
wait for the document; apply to every `input[data-imask]`; watch for added nodes. Applying to an
input: return if IMask is absent or the input already has a mask; build IMask's options from the
JSON; create the mask; where the input has a form, attach a `formdata` listener that sets the
field's entry to the mask's value while the input still belongs to that form and is enabled; send `mvp-forms:imask` from the input, bubbling, with the mask in
`detail.mask`. No inline script, no `eval`, no network.

## The tests

- `tests/test_widgets.py`, mirroring `mvp_forms/widgets.py`, with a class for each widget and
  each block. They assert the attribute's JSON, the media, `attrs` kept, what is refused, and the
  number widget's two overrides against a `DecimalField` and an `IntegerField`.
- `tests/test_pack/test_masked_inputs.py`: a masked input drawn through the pack, with a choice
  applied, in a formset's empty form, and through `|crispy`, `{% crispy %}` and plain Django.
- `tests/test_imask_e2e.py`, marked `e2e`: the script in Chrome, against pages of the test
  project. Fixtures in `tests/conftest.py` skip the module where Chrome is absent and fail it in
  CI, and serve IMask from `tests/data/`. The module is declared in `non-mirror-paths`, since its
  subject is a script.
- `tests/test_demo.py`: the demo page answers, the sidebar links it, each widget's section is
  present and a post returns what each field received. No wording is asserted.
- `tests/test_pack/test_independence.py`: the static directory holds the stylesheet and the
  script.

## The demo

The page approved in the sketch is kept: its sections, order, help text and links. Its forms move
to the final interface. The reference field and the formset's article field state a placeholder
character for each definition and no longer need blocks, so their help text states the pattern
`aa-0000` directly. That is the one place the page differs from the prototype, and it is shown at
the walkthrough. A standalone page without django-mvp is added, as every other demo page has.
The page's own inline script stays in the demo. Both pages load IMask at an exact version with
an integrity value.

## Documentation

- README: a section "Input masks" under the public surface, covering each widget and block with
  its options, loading IMask and the form's media, what the form receives, the event, a page
  without IMask, what is not supported, and the two cautions the specification names. Written in
  the task that introduces each part.
- ADR 0014 and ADR 0041 each say the pack ships no script file. Both sentences are edited to say
  the pack's templates need none. New records at convergence.
- `CONTEXT.md`: the terms under Key Entities.
- CHANGELOG entry.

## Story order

US1 → US2 → US3 → US5 → US4 → US6, sequential, in the feature worktree. US5 comes before US4 so
the formset and modal tests can use every widget.

## What this plan does not do

- No date widget, no function options, no pipes, no preset formats.
- No server validation.
- No change to the pack's templates, to `CONSTITUTION.md` or to anything under `.github/`.
- No test of IMask's own masking rules.
