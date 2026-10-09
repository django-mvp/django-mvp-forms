
## 2026-10-09T10:51:30Z · Forge · plan

Did: brought the branch up to date with main at 0b7d859; wrote research.md, plan.md and tasks.md (4 stories, 7 tasks) from the approved sketch; created the ledger; appended D7 to D11; tightened FR-003 to name the three rules that reach outside a control. Opened #144 for the Article XIV amendment.

Verified: the suite on the sketch: 4,935 pass and 4 fail, each a check the sketch's two new files run into (no static directory, templates named, the template list, replacements). T001 narrows them.

Next: design review, then US1.

Watch: #144 has to merge before this pull request. Record numbers are provisional until the merge gate.

## 2026-10-09T11:09:11Z · Implementer US1 · T001

Did: narrowed the four checks the sketch's files ran into. The three checks that name every distributed template now read `daisyui/`; a second test holds that a template under `django_tomselect/` names only its own path; the README gains a second table for a supported package's templates and `tests/template_surface.py` reads it (a template outside `daisyui/` and `django_tomselect/` is reported); the marker-copy test draws `daisyui/` templates only; the static-directory test now holds `mvp_forms/tomselect.css` and nothing else; `django_tomselect` joins the modules no package module may import. Added `tests/tomselect_stylesheet.py` (one class, `Stylesheet`) and `tests/test_pack/test_tomselect_stylesheet.py` for scope and no colour of its own.
Verified: `uv run pytest tests/test_pack/test_tomselect_stylesheet.py tests/test_pack/test_template_list.py tests/test_pack/test_independence.py::TestDistributedFiles tests/test_pack/test_replacements.py -n auto --dist loadscope`: 194 passed. Seen red by taking each mechanism out and back: a `.btn` rule, a widened exception, a hex, a named and an `oklch` colour (also in a keyframe), a second static file, a static directory elsewhere, `other/x.html`, a module importing `django_tomselect`, a `daisyui/` template naming a foreign path, the grouping template extending another path. tomselect.css restored byte for byte (sha256 checked). `uv run pre-commit run --all-files` green.
Next: T002, the pack's markup on the four widgets.
Watch: the tests that cover the stylesheet reader sit in the stylesheet test module, and the new template-list cases sit in `test_template_list.py`, as the brief limits which existing test files change.

## 2026-10-09T11:13:19Z · Implementer US1 · T002

Did: added `tests/test_pack/test_tomselect.py` (50 tests) holding the markup on a form with all four widgets (single and multiple, over auth `Group` and over a list), each drawn through `{{ form|crispy }}` and `{% crispy form %}`: the `select` and `w-full` classes, each size, each colour and the variant the form states, `select-error` with no colour on a field in error, the `disabled` attribute on the disabled fields only, the label tied to its select, `aria-describedby` naming the help text and, in error, the error element (asserted only on fields that have them), a second draw giving the same markup with the widgets' `attrs` unchanged, and no draw naming `mvp_forms/tomselect.css`. Added `TomSelectForm` to `tests/forms.py` and the `ac-groups` route (an `AutocompleteModelView` over `Group`) to `tests/urls.py`. No production change.
Verified: `uv run pytest tests/test_pack/test_tomselect.py`: 50 passed. Seen red by breaking the pack and putting it back: no `w-full`, the error modifier renamed, the label's `for` removed, the help-text id removed, the error id removed, the widget's `attrs` changed in place, size, variant and the colour-in-error dropped in `Modifiers.resolve`, the stylesheet named in `daisyui/field.html`, and no request held. `git diff origin/main -- mvp_forms` shows only the two files from the sketch.
Next: T003, legibility under light and dark.
Watch: the `disabled` and help-text `aria-describedby` attributes are Django's, not the pack's, so no change to the pack can turn those two tests red; they hold the contract. Selects are drawn with a `RequestFactory` request given a user and run through `TomSelectMiddleware`, because a test needs the form object to compare `attrs` before and after. A page with no django-tomselect field is held by the rest of the pack suite and the diff above, not by a new test.
