
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
