
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

## 2026-10-03T22:32:32Z · Implementer US2 · T004

Did: a number field drawn as a range. Modifiers.drawings gains range; FieldInput.drawings_of gives a NumberInput or a subclass range; the widget is a copy with input_type "range", drawn by Django's own input template; error_modifiers gains range-error. Tests: TestFieldInputRange (tests/test_templatetags/test_daisyui.py), TestRange, TestRangeKeepsWhatANumberInputHas, TestRangeAmongOtherFields and TestRangeMistakes (tests/test_pack/test_range.py, 69 tests), TestReadmeRange; the forms for them in tests/forms.py; STATES gains a range plain and in error. README "Rating and range" gains the range (which fields, where the limits come from, what it keeps, that a slider always submits a number and what follows for an optional field and for an extra form of a formset), every sentence that listed which fields take a drawing is true for the range, and the example gains a range; CHANGELOG and CONTEXT (Drawing, Number field, Range). Demo page: RatingAndRangeForm (was RatingForm) gains a range with limits and a step, RangeStateForm draws a range with help text, in error and disabled, in the shell and standalone; tests in RangeFormPageContract and RangeStatesPageContract.
Verified: tests/test_pack, tests/test_templatetags and tests/test_choices.py: 2261 passed; tests/test_demo.py: 1285 passed; pre-commit and mypy clean. Probed by removing the input_type line (10 failed) and by changing range-error to input-error (2 failed). SC-003: rendered the 75 STATES entries of the base commit 0d19f7c with /tmp/fs010/render_states.py before the first change and again after the last (the two new range entries excluded): 0 of 75 differ, and two renders of the base agree with each other. Not committed.
Next: the full verify command once, then the completion report.
Watch: the one existing test extended is TestModifiersDrawings.test_each_drawing_names_the_component_it_is_drawn_with (the range row, nothing else). No US1 test needed a change. The demo's mixin lost its rating_states attribute for states, which both the rating and the range states read (D19). A size or a colour stated on a range's own field still raises until T005.

## 2026-10-03T22:46:31Z · Implementer US3 · T005

Did: Modifiers.sizes and Modifiers.colors gained a rating row and a range row, as literals (rating colours are bg-neutral to bg-error). A range takes both through classes_for. A rating's size is on the wrapper through FieldInput.rating_class and its colour is on every star, never on the clearing input, through star_modifiers; in error the stars carry bg-error and the size stays. rating_context's comprehension no longer binds a bare underscore. The demo page gained a rating and a range at every size and in every colour, built from Modifiers, and one form whose fields override the form's size and colour. The choices demo page's input-kinds form gained a rating and a range. README example and section, and CHANGELOG, say both take size and colour and have no variant. STATES gained a rating and a range with a size and a colour, plain and in error.
Changed US1 and US2 tests: test_daisyui.py TestFieldInputRating, test_a_size_stated_on_the_field_itself_raises_until_a_rating_has_sizes and test_a_size_the_form_states_is_passed_over, which pinned the old behaviour (now ..._is_the_ratings_size and ..._the_forms_size_is_the_ratings_size).
FR-021: the mistakes already had tests; added two: TestRatingMistakes.test_a_rating_stated_for_a_widget_with_a_template_of_its_own_is_refused and TestRangeMistakes.test_a_name_that_is_not_a_drawing_names_the_field_and_the_range.
Verified: uv run pytest -n auto --dist loadscope -q: 3677 passed, 2 failed. forge verify: conformance, docs, lint, typecheck and build passed; test failed on the same two. The two are TestChoicesPage and TestStandaloneChoicesPage test_every_kind_of_input_is_drawn_at_a_stated_size[rating], from before this feature. The parameters come from Modifiers.sizes and the test looks for the size class on an input, select or textarea, but a rating's size is on its wrapper div as the brief says. Not edited: the brief forbids changing a test from before the feature.
Next: Forge to triage that test (exclude rating from the parameters, or look on the wrapper element too). Nothing else is open in this task.
Watch: T005 is marked blocked in the ledger for that reason only; every other criterion of the task holds.
