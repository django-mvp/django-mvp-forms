
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

## 2026-10-03T19:06:31Z · Implementer US1 · T002

Did: forms drawn through both {{ form|crispy }} and {% crispy form %} for US1 scenarios 1 to 8 (TestDrawings, TestDrawingsInAFormset), FR-012's two mistakes plus the button and hidden-field cases (TestDrawingMistakes), the submission test building its posted data from the inputs as drawn (each name, and its value attribute when it has one). STATES gains a toggle and a switch plain, bound and in error. The README gains "Checkbox, toggle and switch" with an example that test_documented_examples draws; the sentences that counted three kinds and the kinds InvalidChoice carries now include the drawing. CHANGELOG entry under Added. CONTEXT gains Drawing and Boolean field, Choice names four kinds, Variant no longer uses the word drawing.

Verified: README example test was red first (IndexError, no section). The pack tests passed on first run because T001 already built the mechanism, so each was proved by mutation: removing the switch role (5 fail), ignoring the drawing for the component (16), dropping toggle-error (4), not refusing a drawing around a button (1), not checking the widget (9). `uv run pytest tests/test_pack tests/test_choices.py tests/test_templatetags -q -n auto --dist loadscope`: 1508 passed. SC-003: `uv run python /tmp/fs008/render_states.py /tmp/fs008/after.json && cmp /tmp/fs008/before.json /tmp/fs008/after.json` (the script renders every entry of the original STATES, copied to /tmp/fs008/original_independence.py before the first change, with random tab and accordion ids normalised): all 51 identical, nothing committed for it.

Next: T003, the demo page.

Watch: the README states that a toggle and a switch take no size or colour yet (form-wide ones passed over, a field's own raises). T005 changes that and must update the README sentence and the CHANGELOG sentence that say so. The table template does not apply a helper's layout, so a drawing in a formset's layout reaches stacked formsets only; by name on the helper it reaches both.
