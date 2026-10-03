
## 2026-10-03T17:40:03Z · Forge · plan

Did: wrote research.md, plan.md and tasks.md (5 stories, 7 tasks) and the ledger; rebased onto origin/main at 23d5139.
Verified: forge verify on c70391f, all steps green.
Next: design review, then US1.
Watch: FS-005 and FS-007 build alongside; README, CHANGELOG, demo and the class test will move.

## 2026-10-03T17:51:35Z · Implementer US1 · T001

Did: added daisyui/whole_uni_formset.html and uni_formset.html (stacked layout; management form field by field; each form in a bare div by display_form.html with include_media off; divider between forms), the line form, formsets and formset_helper in tests/forms.py, the posted and formset builder fixtures in tests/conftest.py, TestStackedFormset (26 cases) and a stacked formset state in test_independence.py.
Verified: uv run pytest tests/test_pack/test_formsets.py -q: 26 passed. uv run pytest tests/test_pack/test_independence.py -q: 72 passed. pre-commit run --all-files: all hooks passed. Mutations probed: leaving include_media on per form, dropping the per-form div, doubling inputs.html each failed tests.
Next: T002, glossary, README and CHANGELOG.
Watch: model and inline fixtures need the django_db marker on the class; requesting db dynamically as the first database user of a session fails with no such table.

## 2026-10-03T17:52:11Z · Implementer US1 · T002

Did: CONTEXT.md defines formset, stacked layout and table layout and keeps form view as a term not used with the drawing/handling line; README has a Formsets part; CHANGELOG has one Added line under Unreleased. The README layout example (name, quantity, DELETE, one Submit) was drawn once to confirm DELETE appears only because the layout names it.
Verified: pre-commit run --all-files passed. No docs/ page describes formsets (docs/ROADMAP.md only lists the item, unchanged).
Next: full verify, then the report.
Watch: the README says nothing of the table layout, which a later story adds.

## 2026-10-03T17:56:39Z · Implementer US2 · T003

Did: added FormsetTable (columns, rows) and the daisyui_formset_table tag to mvp_forms/templatetags/daisyui.py, with TestFormsetTable (9 tests) in tests/test_templatetags/test_daisyui.py. Red first: ImportError for FormsetTable.
Verified: uv run pytest tests/test_templatetags/test_daisyui.py::TestFormsetTable -x, 9 passed; uv run pre-commit run --all-files passed.
Next: T004, the table template and TestTableFormset.
Watch: the cell list for a row with no columns is [None]; a form is assumed to have the first form fields.

## 2026-10-03T17:58:54Z · Implementer US2 · T004

Did: added daisyui/table_inline_formset.html (form wrapper, media once, management form field by field, one overflow-x-auto div holding table.table, a th scope=col per visible field with the required marker, a row per form with hidden fields in the first cell, each field drawn by field_template with form_show_labels=False, inputs.html once; no table when there are no rows). Added TestTableFormset (24 tests), ChoiceLineForm and ChoiceLineFormSet in tests/forms.py, a table formset state and overflow-x-auto in test_independence.py, README section and CHANGELOG line.
Verified: uv run pytest tests/test_pack/test_formsets.py::TestTableFormset tests/test_pack/test_independence.py, 98 passed; red first was TemplateDoesNotExist. Probes: dropping the hidden-field loop fails 8 tests, dropping the required marker fails 1.
Next: US3 adds formset-wide and row errors.
Watch: the template reads no form.form_html; a form missing a column gets an empty cell.

## 2026-10-03T18:04:55Z · Implementer US3 · T005

Did: added daisyui/errors_formset.html (formset.non_form_errors once in the role=alert element, formset_error_title when set, nothing without errors), included it in uni_formset.html and table_inline_formset.html unless form_show_errors is off; the table row now draws its form-wide and hidden-field errors in the first cell (id <prefix>_errors) and the tr carries aria-describedby only then. Added RuledLineForm, RuledLineFormSet, MarkupRuledLineFormSet and ruled_data to tests/forms.py, TestFormsetErrors (23 cases over both layouts), three error states in test_independence.py, README Errors part and a CHANGELOG line.
Verified: red first, 15 of 23 failed (TemplateDoesNotExist for errors_formset.html, missing alert, missing row errors; the field-error and stacked form-wide cases passed on their first run as the brief predicted). uv run pytest tests/test_pack/test_formsets.py tests/test_pack/test_independence.py: 151 passed. pre-commit run --all-files passed. Probe: removing the form_show_errors guard in both templates failed the errors-off test in both layouts.
Next: T006, delete and order inputs.
Watch: the row's aria-describedby is also gated on form_show_errors, so a row never names an element that is not drawn.

## 2026-10-03T18:04:55Z · Implementer US4 · T006

Did: added OrderedLineFormSet and KeptLineFormSet (can_delete_extra off) to tests/forms.py and TestDeleteAndOrder (12 cases) with a README part and a CHANGELOG line. No template change: table_inline_formset.html already draws an empty td where a row's cell is None.
Verified: uv run pytest tests/test_pack/test_formsets.py::TestDeleteAndOrder: 12 passed. The tests passed on their first run, so each claim was probed: drawing no td for a None cell failed the cell-count test, and drawing the table's inputs with labels on failed the aria-label test. pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: the delete and order checks rest on the pack's existing checkbox and number input; nothing new is drawn for them.

## 2026-10-03T18:13:41Z · Implementer US5 · T007

Did: added OrderLineForm (quantity below one is a field error; a line total past ORDER_LINE_LIMIT is a form-wide error with code over_limit), BaseOrderLineFormSet (the same item twice is a formset-wide error with code duplicate_item), OrderLineFormSet with can_delete and can_order, and StackedOrderHelper and TableOrderHelper to demo/forms.py; four views, four routes, two menu entries and two icon names; four templates (shell pages on Cotton components, standalone twins on daisyUI's CDN build); contract classes for the four pages in tests/test_demo.py (92 tests); a README paragraph naming the four pages; one CHANGELOG line. Read the README's Formsets part against the finished pack and found it true, so changed nothing there. No page under docs/ describes the demo or the formset pack.
Verified: red first, NoReverseMatch for the new route names. uv run pytest tests/test_demo.py -k Formset: 92 passed. Probes: dropping can_order failed 12, removing the duplicate-item check failed 8, giving both formsets one prefix failed 24. Full verify (pre-commit, mypy, pytest -n auto --dist loadscope, uv build): exit 0, 1452 passed.
Next: the story's report.
Watch: the failing formset is drawn with form_tag off yet still carries a csrfmiddlewaretoken input, because the pack draws the token outside its form_tag guard as crispy's own whole_uni_form does; a template in mvp_forms/ is outside this task.
