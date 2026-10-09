# Progress — 015 Input mask widgets for IMask

## 2026-10-09T19:24:50Z · Implementer US1 · T001

Did: Rebuilt the pattern widget and the three block classes test-first in mvp_forms/widgets.py (MaskInput base, PatternMaskInput, RangeBlock, EnumBlock, PatternBlock). Removed the prototype's regex, number and dynamic widgets. Moved the demo's pattern fields to the block classes and took out the three widgets' forms, the disabled number field of MaskStatesForm and the price field of MaskedLineForm, with their entries in the view's widgets list. Widened the static-directory test to name the script.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_masked_inputs.py tests/test_pack/test_independence.py tests/test_demo.py -n auto -q, all green. Red seen first: tests/test_widgets.py failed to import the block classes. The pack tests were probed by making MaskInput a bare Input subclass, which failed 8 of them. /input-masks/ answers 200 with data-imask on every pattern field.
Next: T002, the script in Chrome and its fixtures.
Watch: a definition is written as its expression text, or as an object holding the expression and placeholderChar when a placeholder character is stated for it, and as an object with placeholderChar alone for a built-in. The prototype script reads text only, so T002 must read the object. The formset section's sentence on the demo page still names the price field of a NumberMaskInput; the template is not in T001's files.
