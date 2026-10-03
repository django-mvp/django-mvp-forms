
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

## 2026-10-03T16:47:12Z · Implementer US2 · T006

Did: inputs.html (loop over helper inputs through baseinput.html) included by whole_uni_form.html; TestHelperButtons; a helper-buttons state in test_independence.py. Demo: LayoutObjectsForm ends in a FormActions with the four buttons and draws its own form element (form_tag kwarg, off for the failing form); HelperButtonsForm and RowButtonsForm added; both page templates and the view updated; page tests added to the layout contract. README and CHANGELOG name the buttons (D18).
Verified: uv run pytest tests/test_pack/test_buttons.py tests/test_demo.py tests/test_templatetags/test_daisyui.py -q (340 passed). Red first: 9 of 11 TestHelperButtons failed with no button drawn; 40 demo tests failed before the page changed. pre-commit clean. README example drawn against the branch.
Next: full verify, ledger rows, report.
Watch: the page's own submit button is gone and no existing test relied on it.

## 2026-10-03T16:52:03Z · Implementer US3 · T007

Did: wrote TestHTML and TestHidden in tests/test_pack/test_raw_content.py, watched the three Hidden tests fail (class "hidden", id "hidden-id-step"), then made the hidden branch of layout/baseinput.html write no class and no id (D19). Added an HTML and a Hidden to the two layout states in test_independence.py (probed: with the old template the two button states fail on the class `hidden`). Demo: LayoutObjectsForm gains an HTML note inside its fieldset and a Hidden, ids and names prefixed; two tests in test_demo.py (probed red against the old demo/forms.py). README and CHANGELOG gain both.
Verified: uv run pytest tests/test_pack/test_raw_content.py tests/test_pack/test_buttons.py (63 passed); uv run pytest tests/test_demo.py tests/test_pack -n auto --dist loadscope (439 passed); uv run pre-commit run --all-files clean.
Next: full verify, then the report.
Watch: a css_id or css_class on a Hidden is not drawn (D19). The demo page templates needed no edit, the objects live in the form; demo/views.py and tests/forms.py were not touched.

## 2026-10-03T16:56:01Z · Implementer US4 · T008

Did: wrote TestMultiField (16 tests, red on the missing daisyui/multifield.html), then layout/multifield.html (fieldset, legend from the label, css_class and label_class through daisyui_classes, label marked safe) and multifield.html (one include of field.html). Class test gains a layout of all thirteen objects, unbound and invalid. The demo form gains a phone field and a MultiField (email, phone) with the prefixed id; the Div keeps only the note. README and CHANGELOG gain MultiField.
Verified: uv run pytest tests/test_pack/test_structure.py::TestMultiField (16 passed), tests/test_pack/test_independence.py and tests/test_demo.py (291 passed). The demo tests were red against the old demo form (10 failed) and green after. pre-commit and mypy clean.
Next: T009, the documented examples.
Watch: MultiField appends " error" to its own css_class on each draw with errors; the filter drops repeats and "error", and a test draws one layout twice. docs/ROADMAP.md line 55 still lists fieldsets, divs, rows and columns as a plan; not in this story's files.

## 2026-10-03T16:56:55Z · Implementer US4 · T009

Did: tests/test_pack/test_documented_examples.py draws every example from the installed django-crispy-forms docstrings (Fieldset, Div, Row, Column, HTML, Submit, Reset, Button, Hidden, ButtonHolder, FormActions, StrictButton), unbound and invalid, against DocumentedExamplesForm (new in tests/forms.py), 42 cases. The three examples that did not parse (ButtonHolder, FormActions, Column) are repaired by quoting the string and nothing else. The four input objects are built with the arguments their docstrings show and placed in a layout. test_demo.py gains one parametrised test that each of the thirteen objects is on both pages exactly once, by id or name. README's Layout objects part names all thirteen and its status line now says the structural and button layout objects are drawn.
Verified: uv run pytest tests/test_pack/test_documented_examples.py (42 passed); with daisyui/layout/buttonholder.html moved away the two ButtonHolder cases failed, then restored. tests/test_demo.py -k every_layout_object 52 passed. pre-commit and mypy clean.
Next: the full verify, ledger rows, report.
Watch: the examples are drawn with no user in the context, so a context-aware legend or content draws an empty value. docs/ROADMAP.md line 55 still lists fieldsets, divs, rows and columns as plans.

## 2026-10-03T16:59:16Z · Forge · converge

Converged: no gaps against the specification, nothing to simplify in the diff. Three decision records written (0008 to 0010) and every decision given its verdict.
