
## 2026-10-03T23:10:34Z · Forge · plan

Did: research against main at 1b5802d, plan and tasks written, ledger created.
Verified: daisyUI 5.7.47 floating-label and join rules read from the CDN stylesheet; django-crispy-forms 2.7 render_field read in the environment.
Next: design review.
Watch: FS-010 and FS-012 are building beside this and will move README, CHANGELOG and the demo.

## 2026-10-03T23:26:43Z · Implementer US1 · T001

Did: Modifiers.labels, Choice(label=) with its merge, FormChoices(label=) with its check; FieldInput.resolve_label, can_float, is_floating, is_disabled and the placeholder for a floating field; DrawnButton refuses a label. Committed as eccedb2.
Verified: uv run pytest tests/test_choices.py tests/test_templatetags/test_daisyui.py -q, 553 passed. The new tests failed first on the missing label argument and the missing is_floating and is_disabled.
Next: T002, the frame and body templates and the forms drawn through the pack.
Watch: can_float leaves out the member option, which US2 adds.

## 2026-10-03T23:26:43Z · Implementer US1 · T002

Did: frame.html draws no ordinary label for a floating field and field_body.html draws the floating-label element; FloatingForm in tests/forms.py; test_floating_labels.py (US-1 scenarios 1 to 12, the data, the mistakes, escaping); two floating states and a label-class check in test_independence.py; the README example drawn by test_documented_examples.py; README section "Floating labels", the refused kind and the two template-list rows; CHANGELOG; CONTEXT.
Verified: uv run pytest tests/test_pack -q -n auto --dist loadscope, 1721 passed. SC-003: all 75 entries of STATES as they stood at 0f158d6 render byte for byte the same after this task.
Next: T003, the demo pages.
Watch: the formset test uses the default stacked template; labels off is drawn through the tag only, since the filter does not read the helper's form_show_labels.

## 2026-10-03T23:29:09Z · Implementer US1 · T003

Did: demo pages /floating-labels/ in the shell and /floating-labels/standalone/ on daisyUI's CDN install, with the sidebar entry and its icon; FloatingLabelsForm, FloatingStatesForm and FloatingByNameForm; FloatingLabelsMixin and its two views; build_cleaned moved to CleanedMixin, which DrawingsMixin now uses; tests for both pages; the README's page list and the CHANGELOG name the two pages.
Verified: uv run pytest tests/test_demo.py -q -k FloatingLabels, 48 passed; they failed first on the missing route.
Next: the full verify, then the report.
Watch: the shell page uses the shell's Cotton components and no include; nothing states a size or a colour.

## 2026-10-03T23:40:56Z · Implementer US2 · T004

Did: mvp_forms/layout.py with InvalidMember, Member and Join (members, draw, render); FieldInput's member option, can_join, is_member, member_widths and join-item; join.html, join_member.html and field_messages.html, which field_body.html now includes; JoinedForm in tests/forms.py; w-auto in LAYOUT_UTILITIES and two joined states; the three README template-list rows and rating and range in the floating label's passed-over list.
Verified: uv run pytest tests/test_layout.py tests/test_templatetags tests/test_pack/test_template_list.py tests/test_pack/test_independence.py tests/test_pack/test_documented_examples.py -q, 863 passed; the new tests failed first on the missing mvp_forms.layout, and the rating and range tests failed when can_float was widened to them.
Next: T005, the acceptance scenarios drawn through the tag, the README section, the CHANGELOG and CONTEXT.
Watch: an empty Join in a layout of its own draws nothing, so the helper's display_form falls back to drawing every field; tests give the layout another field. The STATES that existed before differ after this task only by one added line break at the end of each field's body, from the include.
