
## 2026-10-03T15:17:24Z · Forge · PLAN

Research, plan and task list written: 5 stories, 8 tasks. The pack is seven plain templates and one tag; no sketch recorded, so research went straight to plan.

## 2026-10-03T15:28:39Z · Implementer US1 · T001

Did: the daisyui pack's uni_form.html and a minimal field.html (wrapper div, plain label, input; hidden fields bare), FieldInput and the daisyui_input tag in mvp_forms/templatetags/daisyui.py, the demo settings selecting the pack, tests/forms.py and the parse and draw fixtures, README quickstart and public-surface entry, a CHANGELOG line. The conformance paths gain tests/test_pack/.
Verified: red first (ModuleNotFoundError for the tag module, TemplateDoesNotExist daisyui/uni_form.html), then `uv run pytest tests/test_templatetags tests/test_pack tests/test_demo.py` 33 passed; a mutation writing into widget.attrs failed both attrs-unchanged tests, restored; `uv run pre-commit run --all-files` clean including mypy.
Next: T002, the tag path (whole_uni_form.html, display_form.html), bound values, single field, uncovered widgets, empty form.
Watch: T002's acceptance names help text and errors on uncovered widgets, so field.html will carry the frame's help text and error elements in T002 although T001 calls the frame minimal.

## 2026-10-03T15:29:40Z · Implementer US1 · T002

Did: whole_uni_form.html and display_form.html so `{% crispy form %}` draws the fields, with the form element and token present; help text and error elements written into field.html (decision D16); tests for the tag against the filter with no helper and with FormHelper(form), bound values, a password empty unless render_value, as_crispy_field against the whole form, uncovered widgets keeping label, help text and errors in order, and a form with no fields.
Verified: red first (TemplateDoesNotExist daisyui/whole_uni_form.html; missing help text and error ids), then `uv run pytest tests/test_templatetags tests/test_pack tests/test_demo.py` 43 passed; pre-commit clean. The bound-value, single-field and empty-filter tests passed on first run: T001's as_widget path already satisfied them, so they pin existing behaviour.
Next: US2, the label marker, aria hooks and error modifier.
Watch: the layout path of the tag (FormHelper(form)) was confirmed to go through form.form_html; the form element and token have no tests yet (US3).
