
## 2026-10-03T18:31:10Z · Forge · plan

Planned the build: research.md, plan.md and tasks.md written. Six stories, twelve tasks, six dispatches in sequence. No planning notes and no sketch to answer. Next: design review.

## 2026-10-03T18:39:52Z · Forge · design-review

Design review: approve, one medium and five low findings, all applied to spec.md, plan.md, tasks.md, research.md and decisions.md (D19, D20). Main merged in after FS-006 landed. Next: build US1.

## 2026-10-03T18:45:56Z · Implementer US1 · T001

Did: moved the frame to daisyui/frame.html (field.html is now the tag and the include), gave daisyui_field its keyword options and FieldInput wrapper_class, prepended and appended, split the classes into own_classes and pack_classes, added has_attached_text and attached_class, the attached-text branch in field_body.html and layout/prepended_appended_text.html. Tests first: tests/test_pack/test_attached_text.py (49), the FieldInput and tag tests in test_daisyui.py, an attached-text state (unbound and failing) in test_independence.py and the three docstring examples in test_documented_examples.py. README section and CHANGELOG entries.
Verified: uv run pytest tests/test_pack/test_attached_text.py (46 failed, 3 passed before the code, all green after); uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope: 1008 passed; pre-commit run --all-files and mypy clean. Probed by mutation: removing |safe fails the markup test, removing the group check fails the date-as-selects test.
Next: T002, the attached-text demo page and the standalone page.
Watch: ADRs 0006, 0011 and 0012 still name daisyui/field.html as the frame; the feature's ADR at the end amends them. multifield.html includes field.html, so a MultiField draws through the tag as before.
