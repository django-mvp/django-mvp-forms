
## 2026-10-03T21:59:58Z · Forge · plan

Did: confirmed the branch is level with main at 8622e54; wrote research.md, plan.md and tasks.md (3 stories, 5 tasks); created the ledger; appended D11 to D16.

Verified: full verify green at cf71e8a before any code (lint, types, tests, build, conformance).

Next: design review, then US1.

Watch: FS-009, FS-011, FS-012 and FS-013 build in parallel and may move README, CHANGELOG, the demo and the tag library under this branch. Record numbers 0029 to 0031 are provisional until the merge gate.

## 2026-10-03T22:14:21Z · Implementer US1 · T001

Did: FieldInput.drawings_of and the one rule in resolve_drawing; rating row in Modifiers.drawings; is_group true for a rating; a rating drawn through a radio group made for the draw (copy of a radio group, a RadioSelect built for a select) naming daisyui/widgets/rating.html, with the clearing input handed over first; label_text and each star's aria-label share FieldInput.plain_text; bg-error in error_modifiers; DrawingsMixin.drawing_names names the three boolean drawings; docstrings of FieldInput, daisyui_field, Choice and InvalidChoice say which field takes which drawing. One existing test extended: TestModifiersDrawings gains the rating row.

Verified: new TestFieldInputRating (61 tests) red first for the right reason, then green; tests/test_templatetags, test_choices.py, test_demo.py, test_pack/test_drawings.py and test_pack/test_independence.py: 2037 passed; pre-commit and mypy clean.

Next: T002, forms drawn through the pack, STATES, README, CHANGELOG, CONTEXT.

Watch: size and colour rows for a rating are US3, so a size or colour stated on a rating's own field raises and a form-wide one is passed over; a throwaway render of STATES at the base is saved under /tmp/fs010 for the SC-003 comparison after T002.

## 2026-10-03T22:18:41Z · Implementer US1 · T002

Did: tests/test_pack/test_rating.py (TestRating, TestRatingKeepsWhatARadioGroupHas, TestRatingAmongOtherFields, TestRatingMistakes: 88 tests, by the filter and the tag where both apply, posted data built from the drawn inputs); the forms for them in tests/forms.py; STATES gains a rating plain and in error; the README's "Rating and range" section with an example drawn by test_documented_examples.py, and every README sentence that said only a boolean field takes a drawing made true; CONTEXT: Drawing, Choice and Boolean field amended, Single-choice field and Rating added; CHANGELOG under Added and Changed.

Verified: tests/test_pack, tests/test_templatetags and tests/test_choices.py: 2153 passed; pre-commit and mypy clean. SC-003: rendered all 73 STATES entries of the base (script and output under /tmp/fs010, not committed) and again after this task with `uv run python /tmp/fs010/render_states.py /tmp/fs010/after.json /tmp/fs010/ids.json`, then compared as strings with /tmp/fs010/compare.py: 0 of 73 differ (the random accordion and tab-group ids are masked). Probed the clearing-first test by putting the clearing input last: 6 failed.

Next: T003, the demo page "Rating and range".

Watch: the README section describes the rating only; the range joins it in US2 and size and colour in US3.

## 2026-10-03T22:21:15Z · Implementer US1 · T003

Did: the demo page "Rating and range" in the shell and standalone: RatingForm (a required rating by name and an optional one in the layout that posts and shows what it cleaned to) and RatingStateForm (help text, error, disabled) in demo/forms.py; RatingAndRangeMixin and the two views; routes rating-and-range and rating-and-range-standalone; the sidebar entry and its icon; the Cotton shell template and the plain standalone one; RatingAndRangePageContract in tests/test_demo.py with a shell and a standalone class; a paragraph about the page in the README's list of demo pages. No size or colour is stated.

Verified: tests/test_demo.py: 1267 passed (40 of them new); pre-commit and mypy clean.

Next: the full verify command once, then the completion report.

Watch: the page's mixin and test contract are named for the whole page, so the range forms join the same mixin and contract in US2.
