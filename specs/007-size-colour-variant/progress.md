
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

## 2026-10-03T18:04:59Z · Implementer US1 · T002

Did: the first full gate failed its docs step (Choice, Inherit, Modifiers, Stated had no page quoting them), so I dropped the Stated alias, documented Choice, Modifiers, Inherit and the per-field `fields` mapping in the README, and drew that README example through the filter and the tag in test_documented_examples.py. Filled in the ledger rows for T001 and T002.
Verified: `forge verify --repo . --base origin/main` second run: conformance, docs, lint, typecheck, test, build all passed, exit 0. SC-005: `uv run python /tmp/fs007_sc005.py <out>` over the 35 STATES entries of the base test_independence.py, compared with `cmp` against the render at bd11a24, before and after T002 and again at the end: identical each time.
Next: the Forge review of US1; US2 gives Choice its layout drawing.
Watch: Choice is a plain class here and becomes a LayoutObject in T003; the README's by-name `fields` paragraph is true today and T003 extends it.

## 2026-10-03T18:10:40Z · Implementer US2 · T003

Did: Choice is now a layout object (subclass of crispy-forms' LayoutObject): render merges itself over any outer Choice, pushes one context layer under Choice.context_name, draws what it holds, and removes that layer by identity in a finally block. US1 had already built the by-name path and the placed argument in FieldInput and daisyui_field; the by-name tests were proved by mutation, not assumed. One real fix in FieldInput.resolve_modifiers: LayoutObject defines __len__, so a Choice holding nothing (the merged one a nested Choice places) is falsy and the old `placed or named or Choice()` dropped it; it now tests `is None`. README gains "One field's own choice" and CHANGELOG an entry. README example added to test_documented_examples.py.
Verified: uv run pytest tests/test_choices.py tests/test_pack/test_choices.py tests/test_pack/test_documented_examples.py -> 270 passed. New tests seen failing first (no Choice.render; 9 + 1 red). Mutations each turned the new tests red and were reverted: by-name lookup removed (5 failed), or-chain falsy trap (6), pop-top instead of identity (9), no removal (13). pre-commit run --all-files and mypy clean. forge verify --repo . --base origin/main: conformance, docs, lint, typecheck, test, build all passed, exit 0.
Next: US3 (T004) buttons: DrawnButton and daisyui_button; Choice already renders any layout object it holds.
Watch: LayoutObject.__len__ makes an empty Choice falsy, so never test a Choice for truth. Choice.render reaches context.dicts to remove its own layer. The README example test was written alongside the README section, so its red step was the missing heading rather than an observed assertion failure. tests/forms.py needed no change.

## 2026-10-03T18:16:47Z · Implementer US3 · T004

Did: DrawnButton and the daisyui_button tag beside FieldInput; baseinput.html writes drawn.css_class for a visible input and button.html writes drawn.flat_attrs. Size reaches every button, button_color and button_variant reach buttons only, a Choice around one button states its own, a Submit given a colour drops the default btn-primary and keeps one passed as css_class. StrictButton modifiers go inside the class attribute, matched by its leading space; unchanged when nothing is stated. Hidden resolves nothing. README Buttons section and CHANGELOG entry, a README example test, a STATES entry for a buttoned form with every choice.
Verified: tests written first, 31 of the pack tests red and the nothing-stated guards green before the code; `uv run pytest tests/test_pack tests/test_templatetags tests/test_choices.py -n auto --dist loadscope` 1026 passed; pre-commit and mypy clean. Probe: matching class= without the leading space failed the aria_class test (flatatt sorts, so data_class sorts after class and cannot show it). SC-005: `.venv/bin/python /tmp/fs007_render.py /tmp/fs007-states-after-T004.txt` then diff against /tmp/fs007-states-base.txt showed no difference (35 states).
Next: T005, every mistake path through a drawn form, with target for every way of stating.
Watch: with `{{ form|crispy }}` no button is drawn, so a misspelt button_color or button_variant is not reported there; T005 decides how the filter reports it.
