
## 2026-10-09T22:47:14Z · Orchestrator · plan

Research, plan and task list written from the approved sketch: 5 stories, 8 tasks. The option finest is renamed resolution in the prototype.

## 2026-10-09T23:03:53Z · Implementer US1 · T001

Did: tests/test_fields.py (78 cases) and tests/test_pack/test_partial_dates.py (15) written first. Red against the prototype: 6 cases, the three non-ASCII digit forms and `2021--`, `2021---`, `2021-03--`; the rest probed by stubbing parse and prepare_value (67 of 78 failed) and by giving the field the three-part widget (all 15 pack cases failed). parse now drops one trailing hyphen with removesuffix, refuses an empty last part, and matches [0-9]. Static-directory test widened to both scripts. README: section "Partial dates" (values, codes, hand-off to a model), template row, the two route bullets name mvp_forms/widgets/. CHANGELOG entry, CONTEXT.md partial date / precision / part, English catalogue regenerated with makemessages. No other page under docs/ describes what this task touched; ADR 0047 is T003's.
Verified: uv run pytest tests/test_fields.py tests/test_pack/test_partial_dates.py -q: 93 passed. uv run pytest -n auto -q: 5507 passed, 1 failed. uv run pre-commit run --all-files: all hooks passed.
Next: the one red test is tests/test_pack/test_template_list.py::TestTheListMatchesThePackage::test_the_list_and_the_package_do_not_differ, which now reports only ('outside the directories', 'mvp_forms/widgets/partial_date.html'). tests/template_surface.py accepts only daisyui/ and django_tomselect/. The README row is in; the helper and its own test in tests/test_pack/test_template_surface.py (TestRendererRoute pins the exact route set) are not named by T001, so T001 is reported blocked on that, and nothing was changed there.
Watch: widening the helper needs PACK_DIRECTORY to take mvp_forms/ and renderer_route() to include PartialDateInput.template_name so the row's FORM_RENDERER is the expected route; a scratch run of exactly that turned the list test green and made TestRendererRoute fail until its expected set gains the template.

## 2026-10-09T23:09:14Z · Implementer US2 · T002

Did: TestPartialDateMaskInput in tests/test_widgets.py (7 cases) and in tests/test_pack/test_partial_dates.py (kind and resolution drawn through all four sources, attrs and keypad, the pack's input class, size/colour/variant, the formset's empty form, the form's media); PartialDateMaskForm and a line formset in tests/forms.py. The prototype widget already matches the plan, so the cases passed on first run. Probed by swapping the class for a plain TextInput subclass: 14 of 26 failed (kind, keypad, media, data-imask in every source). Widget restored unchanged. README: "The masked input" under Partial dates, the widget in the surface list.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_partial_dates.py tests/test_pack/test_documented_examples.py tests/test_pack/test_template_list.py -q: 319 passed. uv run pre-commit run --all-files: all hooks passed.
Next: T003. The prototype's partial-date kind in imask.js has no pasted-date padding and no FR-042 hold-off; both are built test-first there.
Watch: the field still tells its widget in __init__ (limit_widget). Moving that to get_bound_field is T006's.
