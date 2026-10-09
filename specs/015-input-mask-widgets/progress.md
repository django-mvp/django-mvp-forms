# Progress — 015 Input mask widgets for IMask

## 2026-10-09T19:24:50Z · Implementer US1 · T001

Did: Rebuilt the pattern widget and the three block classes test-first in mvp_forms/widgets.py (MaskInput base, PatternMaskInput, RangeBlock, EnumBlock, PatternBlock). Removed the prototype's regex, number and dynamic widgets. Moved the demo's pattern fields to the block classes and took out the three widgets' forms, the disabled number field of MaskStatesForm and the price field of MaskedLineForm, with their entries in the view's widgets list. Widened the static-directory test to name the script.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_masked_inputs.py tests/test_pack/test_independence.py tests/test_demo.py -n auto -q, all green. Red seen first: tests/test_widgets.py failed to import the block classes. The pack tests were probed by making MaskInput a bare Input subclass, which failed 8 of them. /input-masks/ answers 200 with data-imask on every pattern field.
Next: T002, the script in Chrome and its fixtures.
Watch: a definition is written as its expression text, or as an object holding the expression and placeholderChar when a placeholder character is stated for it, and as an object with placeholderChar alone for a built-in. The prototype script reads text only, so T002 must read the object. The formset section's sentence on the demo page still names the price field of a NumberMaskInput; the template is not in T001's files.

## 2026-10-09T19:32:46Z · Implementer US1 · T002

Did: Wrote the browser tests (tests/test_imask_e2e.py) and their fixtures: a session Chrome launched by channel that skips locally and fails in CI, a page fixture, IMask answered from tests/data/imask-7.6.1.min.js, a MaskedPage view with routes for a plain page, three copies of the script, no IMask and a script-src policy, and a template that draws MaskedPageForm. Rewrote mvp_forms/static/mvp_forms/imask.js: definitions as text or as an object with a placeholder character (built-ins read from IMask.MaskedPattern.InputDefinition.DEFAULT_DEFINITIONS), range, enum and pattern blocks, one formdata listener for every masked input with a form, and the once flag. Dropped the branches for kinds with no widget yet. Added the e2e marker, DJANGO_ALLOW_ASYNC_UNSAFE and the module's non-mirror path to pyproject.toml.
Verified: uv run pytest tests/test_imask_e2e.py, 17 passed. Red seen against the prototype script: the removed-input and per-definition placeholder tests failed. Each behaviour was then probed by removing its part of the script: the once flag, the wait for the document, the IMask guard, the formdata listener, the still-in-form, disabled and name tests, the built-in definition lookup, and the range, enum and block and definition rebuilds each failed a test. Skip and CI failure checked by launching an unknown channel with and without CI=true. Full suite 5208 passed.
Next: T003, the demo page, README, CHANGELOG, CONTEXT and the two ADR sentences.
Watch: the observer is kept and untested here, as the plan's red step for the later story removes it. The script's pattern definitions arrive as text or as an object, which the README need not describe.

## 2026-10-09T19:36:12Z · Implementer US1 · T003

Did: Moved the demo's reference field and the formset's article field to the pattern aa-0000 with a placeholder character for each definition, and their help text and the formset sentence to say so. Added the standalone Input masks page (view, route, template) and linked it from the page as the other demo pages link theirs. Both pages and the README example load imask@7.6.1/dist/imask.min.js with integrity and crossorigin. Wrote the README section "Input masks", the CHANGELOG entry, the glossary terms (Mask, Pattern, Definition, Block, Fixed character, and the Layout object entry's Avoid line reconciled), and the one sentence in ADR 0014 and in ADR 0041.
Verified: tests/test_demo.py -k InputMasks, 16 passed; the new tests failed first on the standalone route, the placeholder options and the pinned script. pre-commit green. Full suite run at the end of the story.
Next: report.
Watch: the integrity value is the hash of the copy of 7.6.1 under tests/data, taken from the npm package, with no request to the CDN. The sentence naming the price field on the page stays until the number story restores the field.
