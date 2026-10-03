
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
