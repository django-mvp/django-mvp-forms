
## 2026-10-03T16:27:33Z · Forge · plan

Did: rebased the branch onto main after FS-001 merged; wrote research.md, plan.md and tasks.md (7 stories, 8 tasks); created the ledger; appended D9 to D15.

Verified: spec-kit prerequisite check lists research.md and tasks.md.

Next: design review, then US1.

Watch: FS-003 builds in parallel and may move README, CHANGELOG and the demo under this branch.

## 2026-10-03T16:38:23Z · Implementer US1 · T001

Did: Select and SelectDateWidget join FieldInput.components as select, with select-error. Re-pointed the FS-001 uncovered-widget examples (UncoveredWidgetsForm, UncoveredForm) at UncoveredInput, a widgets.Input subclass defined in tests/forms.py, and find("select") became find("input"). Added TestSelect, the select cases of TestFieldInput and two select states in the class test. README and CHANGELOG updated.
Verified: RED first: 14 TestSelect cases and 7 TestFieldInput cases failed for the missing class. Then `uv run pytest tests/test_pack/test_choice_inputs.py tests/test_templatetags tests/test_pack/test_independence.py tests/test_pack/test_inputs.py -q` green; `uv run pre-commit run --all-files` passes.
Next: T002, the group frame, widget copy, daisyui_field and select_date.html.
Watch: The brief names SplitDateTimeWidget as the uncovered example, tasks.md, plan.md and D15 name a test-defined widget subclassing Input, because SplitDateTimeWidget is a group and would change what the frame tests assert. Followed tasks.md.
