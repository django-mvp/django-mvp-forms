
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

## 2026-10-03T15:38:51Z · Implementer US3 · T005

Did: errors.html (one `role="alert"` element holding the helper's `form_error_title` and each form-wide error, nothing when there are none, no dependence on `form_show_errors`); uni_form.html and display_form.html draw the form's media when `include_media` and the errors unless `form_show_errors` is explicitly False, for both the default and the laid-out path. Tests in the new tests/test_pack/test_form.py (TestFormWideErrors, TestMedia) over the filter, the tag and `|as_crispy_errors`; four forms added to tests/forms.py.
Verified: red first, 9 of 11 failed (no alert drawn; `|as_crispy_errors` raised TemplateDoesNotExist for daisyui/errors.html), then `uv run pytest tests/test_pack/test_form.py` 15 passed; pre-commit clean. Probes: removing the errors include from display_form.html failed the laid-out test, from uni_form.html failed six; removing the media line from either template failed the matching TestMedia case. Passed on first run after the template existed: the no-alert cases, which pin that a field error is not a form-wide one.
Next: T006, the form element and the helper's switches, `FieldInput(show_labels, show_errors)`.
Watch: the filter never sets `include_media`, so media is drawn through the tag only, as in crispy's own packs; a bare `form_show_errors` that is undefined counts as on, consistent with the tag's default.

## 2026-10-03T15:42:48Z · Implementer US3 · T006

Did: `FieldInput(field, show_labels, show_errors)` and the tag reading both from the context; `aria-label` (tags stripped, plain string) with labels off, the error modifier narrowed to errors shown, `aria-describedby` naming the help text only when errors are off, and the one render that bypasses `as_widget` (errors off, errors, no help text). field.html honours `form_show_labels`, `form_show_errors`, `label_class` and `field_class`. Tests: TestFormElement and TestHelperSwitches in test_pack/test_form.py, TestFieldInputLabelsOff, TestFieldInputErrorsOff and TestFieldInputGroupedWidget in test_daisyui.py. README helper settings, CHANGELOG, decisions.md D18.
Verified: red first, 14 of 55 failed on the missing arguments, then 6 for the right behavioural reasons once the arguments existed (no aria-label, modifier kept, description naming the error element); `uv run pytest tests/test_pack tests/test_templatetags tests/test_demo.py` 133 passed; pre-commit clean including mypy. Found by a test: `strip_tags` returns a safe label with no tag unchanged, so a quoted label broke out of `aria-label`; fixed with `.strip()`. Form element, token, method, multipart and `form_tag` behaviour already worked from US1 and passed on first run, so I probed 21 mutations across whole_uni_form.html, field.html and the tag; one survived (the `use_fieldset` guard in `hides_error_element`, the grouped test had no help text), I added GroupedHelpedForm and all 21 are now killed.
Next: nothing in US3; the full verify runs once before the report.
Watch: the bypass render does not copy `as_widget`'s `localize` line (`widget.is_localized = True`), so a localized field that is invalid, has no help text and is drawn with errors off may format a number differently; aria-label does not unescape entities in a safe label.

## 2026-10-03T15:47:41Z · Implementer US4 · T007

Did: tests/data/daisyui-classes.txt copied unchanged; the daisyui_classes, without_django_mvp fixtures and clear_crispy_template_caches in tests/conftest.py; tests/test_pack/test_independence.py with TestEmittedClasses (14 states through the filter, the tag and as_crispy_errors, subtracting only what the test's forms and helper supplied, asserting the set is not empty), TestWithoutDjangoMvp and TestDistributedFiles; README paragraph on daisyUI 5, the CDN build and a host Tailwind build; decisions.md D19.
Verified: `uv run pytest tests/test_pack/test_independence.py` 31 passed on the first run (they pin properties the pack already had, as the task expected). Mutations, each with the whole suite running (`uv run pytest`, 165 tests): a `p-4` class on the fieldset failed 13 class cases; `<c-button />` in errors.html failed the Cotton test and three bare-install tests; `{% load mvp %}` in errors.html failed 4 with the caches cleared and only 2 with the clearing disabled (the cached uni_form kept drawing), so the clearing is what makes the field tests able to fail; `import mvp` in the tag module, a mvp_forms/static directory and `{% include "base.html" %}` each failed their own test. All restored. `uv build`: neither the wheel nor the sdist holds tests/, the class list or a static directory. Pre-commit clean.
Next: nothing in US4; the full verify runs once before the report.
Watch: an include through a variable (field_template) cannot be checked for its path by reading the template.

## 2026-10-03T15:53:24Z · Implementer US5 · T008

Did: demo/forms.py (TextInputsForm, required and with_help switches, a clean that always raises with a code), TextInputsMixin and the two views, routes, a sidebar MenuItem and the registered icon, text_inputs.html on the shell's Cotton components and the standalone twin on daisyUI's CDN build alone, each drawing the submittable form and five states through `{{ form|crispy }}`. README: installation was `pip install django-mvp-forms` for a package not on PyPI, now from GitHub; the quickstart gained the stylesheet link, a view and a submit button; the demo's two pages are in the contributing section. CHANGELOG under Unreleased.
Verified: red first (NoReverseMatch for text-inputs), then `uv run pytest tests/test_demo.py` 149 passed. Probes: with required and help text removed from the form, the CDN link and csrf_token removed from the standalone page, 7 tests failed, restored. The README quickstart as now written was run in a scratch project against this tree: a GET answers 200, a post with a bad email draws error classes. `uv run pre-commit run --all-files` and `uv run mypy` clean.
Next: nothing in US5; the full verify is the last act before the report.
Watch: no page under docs/ describes the demo; AGENTS.md's demo section is outside T008's files and still lists four things for a page, which holds. The install line points at GitHub and has not been tried against the remote.

## 2026-10-03T15:57:13Z · Forge · CONVERGE

Convergence. The pages were opened in a browser on both the shell and the standalone page, before and after a submission: inputs, labels, markers, help text, field errors and the form-wide alert all drawn as daisyUI. T009 added on US3 for two corrections (entity in aria-label, switches read one way). Six decision records written, 0001 to 0006. Changelog reduced to one entry per thing a host project gets. Tamper-check on US3 had flagged one widened import line in tests/test_templatetags/test_daisyui.py; no assertion changed, accepted.
