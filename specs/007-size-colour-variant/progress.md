
## 2026-10-03T17:50:40Z · Forge · plan

Did: rebased onto main after FS-001, FS-002 and FS-003 merged; wrote research.md, plan.md and tasks.md (5 stories, 6 tasks); created the ledger; appended D11 to D20; applied the design review's seven findings.

Verified: full verify green on the rebased branch before any code.

Next: US1.

Watch: FS-005 and FS-006 build in parallel and may move README, CHANGELOG, the demo and the tag library under this branch.

## 2026-10-03T17:57:16Z · Implementer US1 · T001

Did: wrote mvp_forms/choices.py (INHERIT, InvalidChoice, Modifiers with the 100-class literal tables and the five resolution rules, Choice as a plain value with over(), FormChoices with lookup()), its unit tests in tests/test_choices.py, and the table-against-daisyUI test in test_independence.py. Saved the SC-005 "before" render of all 35 STATES at bd11a24 to /tmp (not committed).
Verified: `uv run pytest tests/test_choices.py tests/test_pack/test_independence.py -q` 149 passed; RED observed first (module missing), and a probe changing input-ghost to input-ghostly failed the independence test; `uv run mypy` clean; `uv run pre-commit run --all-files` passed.
Next: T002, FieldInput takes choices and placed, the removal-checkbox filter, the drawn-form tests.
Watch: a helper.daisyui that is None raises TypeError like any other non-FormChoices (only an absent attribute means no statement). Choice does not subclass LayoutObject yet; T003 adds that.

## 2026-10-03T18:02:41Z · Implementer US1 · T002

Did: FieldInput takes choices and placed and resolves its modifiers in __init__; daisyui_field passes the statement (context, then the field's form's helper) and the placed Choice; daisyui_removal_checkbox filter used by the clearable file input template (file-input-error never mapped); EveryInputForm in tests/forms.py; TestFormWideChoices, TestFormWideChoicesOnAFieldInError and TestRemovalCheckboxOfAFileInError in tests/test_pack/test_choices.py; FieldInput, daisyui_field and removal-filter unit tests; two STATES entries with every choice stated; README section, CHANGELOG entry, four CONTEXT terms, README example drawn by test_documented_examples.py.
Verified: drawn-form tests red first (90 failed, 34 passed before the code; the 34 are the nothing-stated and hidden guards). `uv run pytest tests/test_pack tests/test_choices.py tests/test_templatetags -n auto --dist loadscope` 926 passed. Probes: colour not dropped in error, colour wired to size, and file-input-error mapped each fail tests. SC-005: `uv run python /tmp/fs007_sc005.py <out>` renders every STATES entry of the base test_independence.py (35) and cmp against the render at bd11a24 is identical. mypy and pre-commit clean.
Next: full gate, then the completion report.
Watch: a form-wide colour of error writes file-input-error, which the removal-checkbox filter cannot tell from the error mark, so that checkbox takes no colour. FormChoices docstring already names button_color and button_variant, which reach buttons in a later story.
