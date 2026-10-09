
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
