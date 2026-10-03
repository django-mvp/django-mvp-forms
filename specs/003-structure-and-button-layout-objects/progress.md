
## 2026-10-03T16:27:24Z · Forge · plan

Planned the build: research.md, plan.md and tasks.md written. Four stories, nine tasks, three dispatches. Planning notes answered in research.md. Next: design review.

## 2026-10-03T16:36:54Z · Implementer US1 · T001

**Did:** Wrote `TestDiv` and `TestFieldset` first (16 tests) and watched them fail on the missing `daisyui/layout/div.html`. Added `daisyui/layout/div.html` and `daisyui/layout/fieldset.html`, the `StructureForm` in tests/forms.py, the `draw_layout` fixture in tests/conftest.py and the developer's own template `tests/templates/tests/own_container.html`.
**Verified:** `uv run pytest tests/test_pack/test_structure.py -q` -> 16 passed, exit 0. Mutation probe: dropping the legend guard, `flat_attrs` and the developer's class from the two templates failed 4 tests; restored. `uv run pre-commit run --all-files` clean.
**Next:** T002, `Row` and `Column`, nesting and errors, and the class test.
**Watch:** Tests build their layout objects per test inside the test, never on a module constant (crispy stores rendered values back on objects).

## 2026-10-03T16:37:49Z · Implementer US1 · T002

**Did:** Wrote `TestRowAndColumn` and `TestNesting` and two structural states in the class test first; 12 failed, 10 of them on the missing `daisyui/layout/column.html`. Added `daisyui/layout/row.html` and `daisyui/layout/column.html`. `LAYOUT_UTILITIES` gains `flex`, `flex-col`, `gap-4`, `md:flex-row`, `flex-1` and `min-w-0`.
**Verified:** `uv run pytest tests/test_pack/test_structure.py tests/test_pack/test_independence.py -q` -> 63 passed, exit 0. Probe: removing `min-w-0` from `LAYOUT_UTILITIES` failed both new class-test states; restored. `uv run pre-commit run --all-files` clean.
**Next:** T003, the demo page pair, README and CHANGELOG.
**Watch:** No test names a layout utility outside `LAYOUT_UTILITIES`; the developer-class tests assert the developer's classes are a strict subset of the drawn ones.

## 2026-10-03T16:39:46Z · Implementer US1 · T003

**Did:** Wrote the page contract tests in tests/test_demo.py first (failed on `NoReverseMatch` for `layout-objects`). Added `LayoutObjectsForm`, `LayoutObjectsMixin`, the two views, the two routes, the sidebar entry and its icon, the Cotton shell page and the standalone page. README gains a Layout objects part and the two new demo pages; CHANGELOG gains one Added line under Unreleased. D16 records why the page, not the helper, draws the form element for now.
**Verified:** `uv run pytest tests/test_demo.py -q` -> 180 passed, exit 0. Rendered `/layout-objects/` with the test client and read the markup: fieldset, legend, row, two columns, div, ids all prefixed. The README example drawn against the branch gave the fieldset, the legend with the context value, and the div with its id. `uv run pre-commit run --all-files` clean.
**Next:** Report. Forge re-verifies.
**Watch:** README status line (`draws text-like fields so far`) still omits layout objects; left alone because the parallel feature edits README too.

## 2026-10-03T16:43:53Z · Implementer US2 · T004

Did: added the daisyui_classes filter and UPSTREAM_ONLY_CLASSES in mvp_forms/templatetags/daisyui.py, and layout/baseinput.html for Submit, Reset and Button (type, name, value, class through the filter, id, flat_attrs). Tests: TestDaisyuiClasses and TestBaseInputs.
Verified: uv run pytest tests/test_templatetags/test_daisyui.py::TestDaisyuiClasses tests/test_pack/test_buttons.py -q (29 passed); red first: 19 failed with TemplateDoesNotExist daisyui/layout/baseinput.html. pre-commit clean.
Next: T005 StrictButton, ButtonHolder, FormActions.
Watch: baseinput.html has no hidden branch yet; US3 adds it.

## 2026-10-03T16:44:33Z · Implementer US2 · T005

Did: added layout/button.html, layout/buttonholder.html and layout/formactions.html. Tests TestStrictButton and TestHolders; test_independence.py gains buttons-in-a-layout states (valid and invalid) and the utilities flex-wrap, gap-2, mt-4.
Verified: uv run pytest tests/test_pack -q (176 passed). Red first: 15 failed with TemplateDoesNotExist for the three templates. Probe: renaming flex-wrap in LAYOUT_UTILITIES fails both new states. pre-commit clean.
Next: T006 helper buttons (inputs.html), demo, README, CHANGELOG.
Watch: ButtonHolder takes no attributes, so its template reads none.
