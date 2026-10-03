
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
