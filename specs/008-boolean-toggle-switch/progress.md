
## 2026-10-03T18:52:35Z · Forge · plan

Did: rebased onto main after FS-001 to FS-007 merged; wrote research.md, plan.md and tasks.md (3 stories, 5 tasks); created the ledger; appended D10 to D14.

Verified: full verify green on the rebased branch at ec40828 before any code.

Next: design review, then US1.

Watch: FS-004 builds in parallel and may move README, CHANGELOG, the demo and the tag library under this branch.

## 2026-10-03T19:02:44Z · Implementer US1 · T001

Did: Choice gains a keyword-only `drawing` (merged by `over` like the other three); Modifiers.drawings names checkbox, toggle and switch with their component; FieldInput gets own_choice, resolve_drawing (widget checked first, name tested against a tuple of the table), component, is_single_checkbox, fixed_size and error_modifiers for the toggle, and role="switch" for a switch; DrawnButton.resolve_modifiers refuses a stated drawing (a hidden input still raises nothing). Docstrings that list the kinds name the drawing where it applies. resolve_modifiers now takes the merged choice, not the placed one.

Verified: new tests were red first (65 TypeError on Choice(drawing=), 3 AttributeError). `uv run pytest tests/test_choices.py tests/test_templatetags/test_daisyui.py -q`: 335 passed. `uv run pytest tests/test_pack/test_checkbox.py tests/test_pack/test_choices.py tests/test_pack/test_independence.py -q`: 420 passed. pre-commit and mypy clean.

Next: T002, forms through the pack, STATES, README, CHANGELOG, CONTEXT, and the SC-003 comparison.

Watch: SC-003 baseline of the 51 original STATES entries is saved under /tmp/fs008 (accordion and tab ids are random and are normalised in the comparison).
