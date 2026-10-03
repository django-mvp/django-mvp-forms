
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

## 2026-10-03T19:08:57Z · Implementer US1 · T003

Did: one demo page in two forms, "Checkbox, toggle and switch": DrawingsForm (three boolean fields, a checkbox, a toggle by name in FormChoices and a switch in the layout, no size or colour), DrawingsMixin with DrawingsView on MVPTemplateView and StandaloneDrawingsView on TemplateView, a Cotton template for the shell and a plain one for the standalone page, routes drawings and drawings-standalone, one sidebar entry and one icon, a README paragraph and a CHANGELOG line. A post draws the form again as posted and lists what it cleaned to, each value in an element with an id.

Verified: DrawingsPageContract was red first (NoReverseMatch on both names). `uv run pytest tests/test_demo.py -q -k Drawings`: 32 passed; `uv run pytest tests/test_demo.py -q -n auto --dist loadscope`: 816 passed. Probed by mutation: the demo toggle changed to a checkbox (2 fail), the cleaned list removed (2 fail). The post test builds its data from the inputs as drawn.

Next: the full verify, then the report.

Watch: the demo pages are not behind a sign-in (open_page reads them with an anonymous client, as for every other demo page), so "signed in" for the shell page was not needed to answer 200. US2 adds the states section to these two templates and its form; US3 adds sizes and colours.

## 2026-10-03T19:16:52Z · Implementer US2 · T004

Did: Wrote TestDrawingKeepsWhatACheckboxHas (label tie, help text, error with the drawing's own modifier, required marker, disabled, aria-label with labels off; each for checkbox, toggle and switch, by both the filter and the tag) and KeptBooleansForm. They passed on arrival. Probed each: nine mutations of FieldInput and the frame templates (label for removed, toggle not a single checkbox, help id removed, toggle-error renamed, error id removed, never in error, marker removed, widget drawn without Django's attrs, aria-label never added), each failed the test it guards; all restored, nothing committed. Nothing was missing from FieldInput. Added DrawingStateForm, build_drawing_states and a state section to both demo pages, with DrawingStatesPageContract (finds each by input id, class and attribute); four probes of DrawingStateForm each failed. README: one sentence on what a toggle and a switch keep. FR-015: the pack adds no text for either drawing, so no test.
Verified: uv run pytest tests/test_pack/test_drawings.py tests/test_demo.py -k Drawing: 261 passed. pre-commit --all-files and mypy pass.
Next: T005, size and colour rows for toggle.
Watch: c-section supports levels 1 to 4 only, so a state is level 4 under a level 3 heading.

## 2026-10-03T19:21:43Z · Implementer US3 · T005

Did: Wrote TestModifiersToggle, TestDrawingSizeAndColour and TestReadmeDrawingSizeAndColour first; they failed because Modifiers had no toggle row. Added the toggle rows of sizes and colors (literals, none in variants). STATES gained a toggle and a switch with a size and a colour, plain and in error; a toggle-xxl probe failed both the STATES entry and TestModifierTables. A probe removing the in-error colour drop failed 5 of the new tests. Demo: DrawingTrioForm and DrawingOverrideForm, build_sizes/build_colors from Modifiers.names(kind, "toggle"), a Sizes, Colours and Overriding section in both pages, with DrawingSizesPageContract. README bullet and the example now show a size and a colour on a toggle and a switch; the CHANGELOG entry no longer says a toggle takes no size or colour.
Verified: new tests red before the rows, green after. Adding the toggle row made the FS-007 choices-page test test_every_kind_of_input_is_drawn_at_a_stated_size[toggle] fail, because it walks every row of Modifiers.sizes; I did not edit it. I added a toggle field to the demo's InputKindsForm so that page draws a toggle at a stated size, and the test passes unchanged. tests/test_demo.py: 968 passed.
Next: the full verify, then the report.
Watch: InputKindsForm.__init__ states the toggle's drawing into the choices it is given, so the choices page now shows one more field in each of its input-kind forms.
