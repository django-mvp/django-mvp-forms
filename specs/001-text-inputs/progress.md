
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

## 2026-10-03T15:32:48Z · Implementer US2 · T003

Did: the label drawn as the frame's caption (fieldset-legend) with a marker span, aria-hidden, on required fields; no label element when the label is empty; FieldInput.attrs gains aria-required="true" through requires_aria_required, when the field is required, the form turns use_required_attribute off and the widget is not a group. Tests in test_field_frame.py (TestLabel, TestRequiredMarker) and four in TestFieldInput.
Verified: red first, 5 failed for the right reason (no marker, an empty label element left behind, no aria-required); then `uv run pytest tests/test_pack tests/test_templatetags tests/test_demo.py` 54 passed; pre-commit clean. Passed on first run, pinning markup US1 already had: label for equals the input id, required on the input, an optional field has no marker, no aria-required when the form keeps required, none on an optional field, none on a grouped widget. Mutation probes: dropping the use_fieldset guard failed the grouped test, dropping the use_required_attribute condition failed the keeps-required test.
Next: T004, errors and help text tied to the input.
Watch: label_class and form_show_labels are US3 (T006), so the label ignores both for now.

## 2026-10-03T15:34:05Z · Implementer US2 · T004

Did: the error modifier on the input (FieldInput.css_class adds `<component>-error` when the field has errors); tests for the description (help only, errors only, both, neither: the input names exactly what is drawn and every named id exists), aria-invalid and the modifier, every message inside the one error element, escaping of label, help text and error with safe help text kept, two prefixed forms, and a form with auto_id=False. README paragraph and a CHANGELOG line under Unreleased; decisions.md D17.
Verified: red first, 10 failed for the right reason (no error modifier on any kind; my first description test also failed from a bug of its own, the input's id counted as drawn, fixed in the test). Then `uv run pytest tests/test_pack tests/test_templatetags tests/test_demo.py` 87 passed; pre-commit clean. Passed on first run, pinning what US1's field.html and Django already do: the help text and error ids, aria-describedby, aria-invalid, escaping, several errors in one element, unique prefixed ids, no ids with auto_id=False. Mutation probes against field.html each failed a test: `|safe` on the label, on the help text and on an error; renaming the error id; printing only the first error; writing `for` and the help text id without their auto_id guards. aria-invalid and aria-describedby come from Django and were not mutated.
Next: nothing in US2; US3 owns form-wide errors, label_class, field_class and the helper's switches.
Watch: the error modifier does not yet look at form_show_errors; US3 adds that argument (D17). Escaping is one test over label, help text and error, so a failure there names the behaviour, not which of the three.
