
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

## 2026-10-03T16:43:09Z · Implementer US1 · T002

Did: FieldInput gained templates, template_name, widget (a shallow copy carrying the pack's template), is_group and group_description. {% daisyui_field field as drawn %} replaced {% daisyui_input %}, which is deleted. The frame draws a group as fieldset and legend, with aria-describedby from group_description and aria-label when labels are off. attrs.html and select_date.html added, with the daisyui_date_part filter. The required marker and the field's input, help text and errors moved into the includes required_marker.html and field_body.html so the div and fieldset shapes write them once. Base English catalogue added. LAYOUT_UTILITIES gained flex and gap-2. README and CHANGELOG updated.
Verified: RED first: 22 new tests failed for the missing behaviour. `uv run pytest tests -q` 401 passed. `uv run pre-commit run --all-files` and `uv run mypy` pass. Probed by mutation: dropping the unchanged-template check failed 2 tests, and not setting the copy's template_name failed 3.
Next: story report. The full verify and the ledger follow.
Watch: makemessages also lists the existing "Forms" string from apps.py, so the catalogue holds four msgids. docs/adr/0004 still names {% daisyui_input %}, a landed record that is superseded by the ADR written at convergence.

## 2026-10-03T16:48:06Z · Implementer US2 · T003

Did: A BooleanField is drawn as daisyUI's checkbox inside <label class="label" for>, with the label text and required marker after the box. FieldInput maps CheckboxInput to checkbox with checkbox-error, never adds w-full to it (fixed_size), and answers is_single_checkbox; field_body.html draws the label around the box, field.html leaves its own label out for it. README and CHANGELOG say so.
Verified: uv run pytest tests/test_pack/test_checkbox.py tests/test_templatetags tests/test_pack/test_independence.py -q (110+ green, exit 0); full: uv run pytest -n auto --dist loadscope (432 passed), pre-commit, mypy, uv build all exit 0.
Next: US3 (radio and checkbox groups) can add CheckboxSelectMultiple to components; is_single_checkbox already excludes groups.
Watch: docs/adr/0006 still says the frame's outer element is always a div, and does not mention the single checkbox's label; ADR 0007 does not mention the checkbox exemption. Both are Forge's to record.

## 2026-10-03T16:52:19Z · Implementer US3 · T004

Did: RadioSelect and CheckboxSelectMultiple draw from daisyui/widgets/group.html through FieldInput.templates (components, error modifiers, radio fixed-size). template_name now also requires option_template_name unchanged (DR-006, D19). README and CHANGELOG describe the groups. Tests: TestChoiceGroups (both widgets, both sources), TestRadioGroup, TestCheckboxGroup, four group states in TestEmittedClasses; flex-col joins LAYOUT_UTILITIES.
Verified: tests/test_pack/test_choice_inputs.py 128 passed; probes: dropping the option_template_name comparison fails the option-template test, dropping radio from fixed_size fails the never-widened test, dropping flex-col from LAYOUT_UTILITIES fails TestEmittedClasses. Full: pytest -n auto --dist loadscope 509 passed; pre-commit, mypy, uv build clean; Django 5.2 run of tests/test_pack and tests/test_templatetags 360 passed.
Next: US4 file inputs (T005) reuses the same template check and FieldInput.templates.
Watch: group.html reads only the widget context Django builds; no docs page beyond README describes the groups.

## 2026-10-03T16:56:22Z · Implementer US4 · T005

Did: FileInput and its subclass ClearableFileInput join FieldInput.components as file-input (w-full, file-input-error); ClearableFileInput joins FieldInput.templates and is drawn from daisyui/widgets/clearable_file_input.html: a link with the link class, for an optional field a label holding a checkbox-class removal box (disabled and checked as Django sets them), Django's own words, then the file input through attrs.html. A required field holding a file gets no removal box, and Django already leaves required off its input. Tests: tests/test_pack/test_file_inputs.py (both sources), TestFieldInputFiles, two file states in TestEmittedClasses. FilesForm, HeldFile and two widget subclasses in tests/forms.py. README, CHANGELOG, D20.
Verified: RED first: 29 of 140 new/related cases failed for the missing class and template. Focused: `uv run pytest tests/test_pack/test_file_inputs.py tests/test_templatetags/test_daisyui.py -q` 140 passed. Probes by mutation: removing the required guard, the checkbox class, the label's for, and escaping each failed 2 tests. Full: `uv run pytest -n auto --dist loadscope` 566 passed; `uv run pre-commit run --all-files`, `uv run mypy`, `uv build` exit 0; Django 5.2 run of tests/test_pack and tests/test_templatetags 417 passed.
Next: US5 (T006), hidden fields and the form-wide alert.
Watch: tests/forms.py's OwnTemplateFileInput names django's file.html, not the clearable template, since naming the clearable one is the class's own template and so is covered. The demo project has no file input yet; T007/T008 own that.

## 2026-10-03T16:59:28Z · Implementer US5 · T006

Did: errors.html now draws from {% with errors=form.get_context.errors %}, so a hidden field's errors join the form-wide alert as Django's own "(Hidden field %(name)s) %(error)s". No tag needed; the planned fallback was not required. Added tests/test_pack/test_hidden_inputs.py (27 cases through |crispy, {% crispy %}, |as_crispy_errors) and the hidden-input forms in tests/forms.py. README and CHANGELOG describe hidden inputs and their errors.
Verified: tests/test_pack/test_hidden_inputs.py 27 passed; 12 of them fail with errors.html reverted (the alert cases), so they hold the change. Full: uv run pytest -n auto --dist loadscope 593 passed; pre-commit all passed; mypy clean; uv build ok; Django 5.2 run of the new file 27 passed.
Next: US6 (T007).
Watch: form.get_context also feeds the alert for any future form whose get_context is overridden; a hidden field's errors rely on Django 5.2+ get_context behaviour, confirmed on 5.2 and the installed version.

## 2026-10-03T17:02:37Z · Implementer US6 · T007

Did: Added tests/test_pack/test_states.py (62 cases, both |crispy and {% crispy %}) and three forms in tests/forms.py (DisabledInputsForm, ReadOnlyInputsForm, DisabledAndReadOnlyForm). Disabled: text, number, date, textarea, select, checkbox, file input each have disabled + component class + value; every option of a radio and checkbox group is disabled; the removal checkbox of a held file is disabled; a disabled password has no value. Read-only: readonly reaches text, textarea, select, checkbox, file input unchanged and adds no class; read-only text/textarea have name, value, no disabled; text with both has both. README section and CHANGELOG entry. No change to mvp_forms/ was needed: every test passed on first run.
Verified (scratch edits, each reverted): attrs.html drops disabled -> 6 fail (group options, file input); clearable template drops removal disabled -> 2 fail; fixtures lose disabled=True -> 24 fail; pack adds a class for readonly -> 10 fail; pack drops readonly in FieldInput.attrs -> 12 fail; PasswordInput(render_value=True) -> 2 fail; initial removed -> 4 fail. One probe was ineffective: forcing attrs["disabled"]=False in FieldInput.attrs leaves 62 green because Django's build_widget_attrs writes disabled after the merge, so the pack cannot remove it. Focused: uv run pytest tests/test_pack/test_states.py tests/test_pack/test_independence.py -> 113 passed. pre-commit run --all-files passed.
Next: full verify, ledger, report.
Watch: the readonly tests use widget attrs, so a future FieldInput that stops merging developer attrs would fail them, which is intended.

## 2026-10-03T17:09:27Z · Implementer US7 · T008

Did: ChoiceInputsForm and TextStatesForm; StatesMixin shared by the text and choice page pairs (post binds FILES; the upload is validated and dropped); choice-inputs and standalone views, routes, menu item, icon; two templates (Cotton on the shell, none standalone); tests for both pages; README status, public-surface list by widget class, demo section; CHANGELOG entry; decision D21.
Verified: uv run pytest tests/test_demo.py (397 passed); probes with FILES unbound, enctype removed and disabled switched off each failed tests; uv run pytest -n auto --dist loadscope (904 passed, exit 0); uv run pre-commit run --all-files (all passed); uv run mypy (no issues); uv build (built).
Next: none for US7; Forge verifies and accepts.
Watch: tests/test_demo.py renders a page per parametrised case, about 50s serially for the file; text-inputs tests were not edited.
