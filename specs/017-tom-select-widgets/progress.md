## 2026-10-11T22:06:34Z · Orchestrator · plan

Research, plan and task list written: 6 stories, 8 tasks. No sketch. The build continues on pull request #171.

## 2026-10-11T22:18:39Z · Implementer US1 · T001

Did: Added TomSelectMultiple (a SelectMultiple that writes data-tom-select holding {} in build_attrs and names mvp_forms/tomselect.js in its media). Tests first: widget tests in tests/test_widgets.py, pack tests in tests/test_pack/test_tom_select_widgets.py, forms in tests/forms.py. No change to the pack's templates or tags, since the pack picks the select component by isinstance of forms.Select.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py -q, 345 passed. Red seen first as an ImportError on the missing widget. Probed the media and markup tests by giving forms.SelectMultiple the same Media: two tests failed, then reverted.
Next: T002, the script and its Chrome tests.
Watch: the test_widgets.py module docstring now names the Tom Select widgets too. The stock-select comparison test strips script tags and blank lines, since {% crispy form %} draws the form's media.
