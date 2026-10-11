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
