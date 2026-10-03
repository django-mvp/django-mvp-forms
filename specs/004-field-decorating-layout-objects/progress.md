
## 2026-10-03T18:31:10Z · Forge · plan

Planned the build: research.md, plan.md and tasks.md written. Six stories, twelve tasks, six dispatches in sequence. No planning notes and no sketch to answer. Next: design review.

## 2026-10-03T18:39:52Z · Forge · design-review

Design review: approve, one medium and five low findings, all applied to spec.md, plan.md, tasks.md, research.md and decisions.md (D19, D20). Main merged in after FS-006 landed. Next: build US1.

## 2026-10-03T18:45:56Z · Implementer US1 · T001

Did: moved the frame to daisyui/frame.html (field.html is now the tag and the include), gave daisyui_field its keyword options and FieldInput wrapper_class, prepended and appended, split the classes into own_classes and pack_classes, added has_attached_text and attached_class, the attached-text branch in field_body.html and layout/prepended_appended_text.html. Tests first: tests/test_pack/test_attached_text.py (49), the FieldInput and tag tests in test_daisyui.py, an attached-text state (unbound and failing) in test_independence.py and the three docstring examples in test_documented_examples.py. README section and CHANGELOG entries.
Verified: uv run pytest tests/test_pack/test_attached_text.py (46 failed, 3 passed before the code, all green after); uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope: 1008 passed; pre-commit run --all-files and mypy clean. Probed by mutation: removing |safe fails the markup test, removing the group check fails the date-as-selects test.
Next: T002, the attached-text demo page and the standalone page.
Watch: ADRs 0006, 0011 and 0012 still name daisyui/field.html as the frame; the feature's ADR at the end amends them. multifield.html includes field.html, so a MultiField draws through the tag as before.

## 2026-10-03T18:48:51Z · Implementer US1 · T002

Did: AttachedTextForm (three attached-text layout objects on inputs, one on a select, every field required, prefixed ids), AttachedTextMixin, AttachedTextView on the shell and DecoratedFieldsStandaloneView, routes attached-text and decorated-fields-standalone, sidebar entry and icon, templates demo/attached_text.html (Cotton) and demo/decorated_fields_standalone.html (plain, CDN only). Tests first in tests/test_demo.py (57 selected, all failed with NoReverseMatch before the pages existed). README demo section and CHANGELOG entry.
Verified: uv run pytest tests/test_demo.py tests/test_smoke.py: 802 passed; pre-commit run --all-files clean.
Next: full verify, then the completion report.
Watch: the standalone view only binds the attached-text form; later stories choose by the submit button's name, as the containers view does.

## 2026-10-03T18:58:17Z · Implementer US2 · T003

Did: FieldInput takes the keyword-only `inline`, with `inline_templates` naming widgets/inline_group.html for RadioSelect and CheckboxSelectMultiple; template_name draws them from it while a widget naming its own template or option template keeps its own. widgets/group.html and the new inline_group.html both include widgets/group_options.html. layout/radioselect_inline.html and layout/checkboxselectmultiple_inline.html are the two-line templates. Tests first: tests/test_pack/test_inline_groups.py (56), TestFieldInputInline in test_daisyui.py, four inline states in test_independence.py, two docstring examples and a README example test in test_documented_examples.py; InlineRadiosForm and InlineCheckboxesForm in tests/forms.py. README section "Choices in a line" and a CHANGELOG entry.
Verified: uv run pytest tests/test_pack/test_inline_groups.py (all failed with TemplateDoesNotExist before the templates existed); uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope: 1449 passed; pre-commit run --all-files clean. Probed by mutation: dropping inline=True from the radio layout template fails the template_name test.
Next: T004, the inline-choices demo page and the standalone page's forms.
Watch: the layout test reads the template through FieldInput.template_name by recording the FieldInputs built in a draw; no test compares the two containers. docs/ has no page for these objects; ADR 0012 names group.html and is left as written.

## 2026-10-03T19:00:53Z · Implementer US2 · T004

Did: InlineChoicesForm (a required radio group and a required checkbox group, layout built per instance, prefixed submit name), InlineChoicesMixin and InlineChoicesView on the shell, route inline-choices, sidebar entry and icon, demo/inline_choices.html on Cotton components. The standalone page gains both inline forms and a link to the shell page; DecoratedFieldsStandaloneView now binds the form whose submit button a post names, the attached-text form when it names none. Tests first in tests/test_demo.py (InlineChoicesPageContract, run against both pages; 42 failed or errored before the page existed). README demo section and CHANGELOG entry.
Verified: uv run pytest tests/test_demo.py -n auto --dist loadscope: 885 passed; pre-commit run --all-files clean.
Next: full verify, then the completion report.
Watch: the failing form is bound to an invalid size and no extras, so both groups show an error; the forms of US3 to US6 add their own mixin to the standalone view and their submit names to its post.

## 2026-10-03T19:08:28Z · Implementer US3 · T005

Did: FieldWithButtons is drawn as one `join` element around the input (carrying `join-item`) and the buttons crispy already drew, read once from `buttons` inside the joined branch of `field_body.html`. `FieldInput` gained `join`, `is_joined` and `join-item` in `pack_classes` (never on a group). `layout/field_with_buttons.html` is the two-line template. Size tests for attached text and for joined buttons passed with no production change, as the brief predicted (FS-007 already resolves them). README gets a "A field with buttons" section and the size rule in it and in the attached-text bullets; CHANGELOG entry under Added.
Verified: red first, 24 of 26 tests in test_field_with_buttons.py failed before the template existed; `uv run pytest tests/test_pack/test_field_with_buttons.py tests/test_pack/test_attached_text.py tests/test_pack/test_independence.py tests/test_pack/test_documented_examples.py tests/test_templatetags/test_daisyui.py -q` exit 0, 503 passed; `uv run pre-commit run --all-files` exit 0; `uv run mypy` exit 0.
Next: T006, the field-with-buttons demo page and its forms on the standalone page.
Watch: the join element is inside the `field_class` div and wraps the input of any widget with a template, so on a radio group it holds the group and the buttons. A single checkbox gets `join-item` as the plan says.

## 2026-10-03T19:10:17Z · Implementer US3 · T006

Did: the field-with-buttons demo page: route `field-with-buttons`, `FieldWithButtonsForm` (a field with one button and a field with three, every id prefixed), `FieldWithButtonsMixin` and `FieldWithButtonsView`, the shell template on Cotton components, a menu item and an icon name, and both forms on `decorated-fields-standalone`. `DecoratedFieldsStandaloneView.post` binds the buttons form when its submit button is named. README demo section lists the route, CHANGELOG has an entry.
Verified: red first, 31 failed and 12 errored before the page existed; `uv run pytest tests/test_demo.py tests/test_smoke.py -q -n auto --dist loadscope` exit 0, 931 passed; `uv run pre-commit run --all-files` exit 0; `uv run mypy` exit 0.
Next: the full verify, then the completion report.
Watch: the buttons in the demo are `StrictButton` of the default type `button`, so they post nothing; the form's own submit is the one the standalone view reads.
