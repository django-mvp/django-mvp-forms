## 2026-10-11T22:06:34Z · Orchestrator · plan

Research, plan and task list written: 6 stories, 8 tasks. No sketch. The build continues on pull request #171.

## 2026-10-11T22:18:39Z · Implementer US1 · T001

Did: Added TomSelectMultiple (a SelectMultiple that writes data-tom-select holding {} in build_attrs and names mvp_forms/tomselect.js in its media). Tests first: widget tests in tests/test_widgets.py, pack tests in tests/test_pack/test_tom_select_widgets.py, forms in tests/forms.py. No change to the pack's templates or tags, since the pack picks the select component by isinstance of forms.Select.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py -q, 345 passed. Red seen first as an ImportError on the missing widget. Probed the media and markup tests by giving forms.SelectMultiple the same Media: two tests failed, then reverted.
Next: T002, the script and its Chrome tests.
Watch: the test_widgets.py module docstring now names the Tom Select widgets too. The stock-select comparison test strips script tags and blank lines, since {% crispy form %} draws the form's media.

## 2026-10-11T22:29:17Z · Implementer US1 · T002

Did: Added mvp_forms/tomselect.js: one flag on window, waits for the load event, starts a control on each select[data-tom-select] that has no tomselect property when window.TomSelect is a function, passes placeholder, maxItems and plugins from the attribute plus maxOptions null, copies aria-describedby to the control's input, leaves a refused select alone. Added the Chrome tests in tests/test_tomselect_e2e.py with a test page, view and routes (tests/urls.py, tests/templates/tests/tomselect_page.html, TomSelectPageForm in tests/forms.py). The static-files list test gained the script.
Verified: uv run pytest tests/test_tomselect_e2e.py -q -n 4, 16 passed. Red seen first with the script moved aside: the control tests failed on a missing control. Probed by breaking the script six ways (no Tom Select guard, no flag and no per-select guard, no maxOptions, no aria copy, selector widened to any select, no try/catch): each broke the test that covers it. Starting at once instead of after load broke 14.
Next: T003, documents and the demo.
Watch: a select Tom Select refuses keeps a stray tomselect property but no wrapper and stays visible, so the test asserts on the wrapper and visibility. The refused test relies on plugins naming one that does not exist. The label test clicks label[for=id_fruit-ts-control], since Tom Select moves the for to its input.

## 2026-10-11T22:35:27Z · Implementer US1 · T003

Did: Added the README section "Tom Select widgets", the CHANGELOG entries, four CONTEXT.md terms and the widened option group entry, and reworded the head of tomselect.css and the module docstring of widgets.py. Added the demo pages at /tom-select-widgets/ and /tom-select-widgets/standalone/ (forms, views, routes, a sidebar entry after django-countries, two templates). The standalone page loads Tom Select's complete build and default stylesheet from jsdelivr with sha384 integrity hashes. The script's hash is computed from tests/data/tom-select-2.5.2.complete.min.js and matches the CDN file byte for byte. The stylesheet hash is of the file fetched from the CDN.
Verified: uv run pytest tests/test_pack tests/test_widgets.py tests/test_demo.py -q -n 4 --dist loadscope, 4627 passed. Red seen first as a missing demo module. Both pages answer 200 and hold the widget's select, once each of the form's script. A test runs the README's python example and draws it.
Next: full verify, then the report.
Watch: the README says a select added after the page loads is left as a stock select, which T007's observer will change. The sidebar entry sits after django-countries, because an existing test pins django-countries directly after django-tomselect.

## 2026-10-11T22:37:17Z · Implementer US1 · T002

Did: Full verify found one red step. Conformance refused tests/test_tomselect_e2e.py as a test that mirrors no source module. Listed it beside the other two browser test files under [tool.forge.conformance] non-mirror-paths in pyproject.toml, as the standard says to declare such a path.
Verified: forge verify, all six steps on the three task commits: lint, typecheck, test (63 s), build and docs passed, conformance failed on that one line. After the change, forge verify --steps conformance passed and pre-commit passed.
Next: report.
Watch: pyproject.toml is outside the brief's file list for T002.

## 2026-10-11T22:48:38Z · Implementer US2 · T004

Did: Added TomSelect, a Select that writes data-tom-select holding {} and names mvp_forms/tomselect.js. What it shares with TomSelectMultiple is one mixin in mvp_forms/widgets.py, TomSelectAttribute, which holds the attribute and the media. Tests first: TestTomSelect and TestWhatTheTomSelectFieldReceives in tests/test_widgets.py, TestTomSelect in tests/test_pack/test_tom_select_widgets.py, TestTheSingleWidget in tests/test_tomselect_e2e.py, with TomSelectSingleForm, StockSingleForm and two fields on TomSelectPageForm in tests/forms.py. README names TomSelect in the surface, the example and the section. CHANGELOG has an entry. The demo forms gained a single field beside the multiple one in the form, each state, each size, each colour and the comparison, and the shell page's two intro texts name both widgets.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py -k TomSelect, 105 passed. uv run pytest tests/test_tomselect_e2e.py -k TheSingleWidget, 4 passed. uv run pytest tests/test_demo.py tests/test_pack/test_tom_select_widgets.py -k "TomSelectWidgets or TomSelect", 132 passed. Red seen first as an ImportError on the missing widget and a missing field on the demo pages. The browser tests were probed by removing the attribute write: all four failed. pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: Tom Select ignores typed keys in a single control that holds a value, so the control cannot be searched until it is cleared or a choice is clicked. The browser tests click the option for that reason. The script needed no change. The README's Backspace sentence rests on the browser test only.
