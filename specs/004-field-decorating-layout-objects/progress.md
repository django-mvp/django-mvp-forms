
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

## 2026-10-03T19:00:53Z · Implementer US2 · T004

Did: InlineChoicesForm (a required radio group and a required checkbox group, layout built per instance, prefixed submit name), InlineChoicesMixin and InlineChoicesView on the shell, route inline-choices, sidebar entry and icon, demo/inline_choices.html on Cotton components. The standalone page gains both inline forms and a link to the shell page; DecoratedFieldsStandaloneView now binds the form whose submit button a post names, the attached-text form when it names none. Tests first in tests/test_demo.py (InlineChoicesPageContract, run against both pages; 42 failed or errored before the page existed). README demo section and CHANGELOG entry.
Verified: uv run pytest tests/test_demo.py -n auto --dist loadscope: 885 passed; pre-commit run --all-files clean.
Next: full verify, then the completion report.
Watch: the failing form is bound to an invalid size and no extras, so both groups show an error; the forms of US3 to US6 add their own mixin to the standalone view and their submit names to its post.

## 2026-10-03T19:08:28Z · Implementer US3 · T005

Did: FieldWithButtons is drawn as one `join` element around the input (carrying `join-item`) and the buttons crispy already drew, read once from `buttons` inside the joined branch of `field_body.html`. `FieldInput` gained `join`, `is_joined` and `join-item` in `pack_classes` (never on a group). `layout/field_with_buttons.html` is the two-line template. Size tests for attached text and for joined buttons passed with no production change, as the brief predicted (FS-007 already resolves them). README gets a "A field with buttons" section and the size rule in it and in the attached-text bullets; CHANGELOG entry under Added.
Verified: red first, 24 of 26 tests in test_field_with_buttons.py failed before the template existed; `uv run pytest tests/test_pack/test_field_with_buttons.py tests/test_pack/test_attached_text.py tests/test_pack/test_independence.py tests/test_pack/test_documented_examples.py tests/test_templatetags/test_daisyui.py -q` exit 0, 503 passed; `uv run pre-commit run --all-files` exit 0; `uv run mypy` exit 0.
Next: T006, the field-with-buttons demo page and its forms on the standalone page.
Watch: the join element is inside the `field_class` div and wraps the input of any widget with a template, so on a radio group it holds the group and the buttons. A single checkbox gets `join-item` as the plan says.

## 2026-10-03T19:10:17Z · Implementer US3 · T006

Did: the field-with-buttons demo page: route `field-with-buttons`, `FieldWithButtonsForm` (a field with one button and a field with three, every id prefixed), `FieldWithButtonsMixin` and `FieldWithButtonsView`, the shell template on Cotton components, a menu item and an icon name, and both forms on `decorated-fields-standalone`. `DecoratedFieldsStandaloneView.post` binds the buttons form when its submit button is named. README demo section lists the route, CHANGELOG has an entry.
Verified: red first, 31 failed and 12 errored before the page existed; `uv run pytest tests/test_demo.py tests/test_smoke.py -q -n auto --dist loadscope` exit 0, 931 passed; `uv run pre-commit run --all-files` exit 0; `uv run mypy` exit 0.
Next: the full verify, then the completion report.
Watch: the buttons in the demo are `StrictButton` of the default type `button`, so they post nothing; the form's own submit is the one the standalone view reads.

## 2026-10-03T19:16:02Z · Implementer US4 · T007

Did: FieldInput takes the keyword-only `disabled`, which adds `disabled` to the attrs given to as_widget (the form's field and widget are untouched). `uneditable-input` joins UPSTREAM_ONLY_CLASSES through the constant UNEDITABLE_CLASS and own_classes drops that one name only. New two-line template layout/uneditable_input.html. README section "An uneditable field" and the corrected sentence under "Disabled and read-only fields"; CHANGELOG entry.
Verified: `uv run pytest tests/test_pack/test_uneditable_field.py tests/test_templatetags/test_daisyui.py tests/test_pack/test_documented_examples.py tests/test_pack/test_independence.py -q` 451 passed (24 failed first, for the missing template and the unknown `disabled` argument). pre-commit clean.
Next: T008, the uneditable-field demo page and its forms on the standalone page.
Watch: docs/adr/0013 still says the pack writes no attribute for either state; the plan says the ADR is amended at the end of the feature, and it is outside this story's files.

## 2026-10-03T19:19:20Z · Implementer US4 · T008

Did: route `uneditable-field` (UneditableFieldView, UneditableFieldMixin, UneditableFieldForm), menu item and icon, template demo/uneditable_field.html on Cotton components, the form added to demo/decorated_fields_standalone.html and a branch for `uneditable-submit` in DecoratedFieldsStandaloneView.post. The account is declared disabled in the form class so a post keeps its value with no error. README demo section and CHANGELOG entry.
Verified: `uv run pytest tests/test_demo.py tests/test_pack/test_documented_examples.py -q` 1031 passed (the new demo tests failed first on the missing route). pre-commit clean.
Next: full verify, then the report.
Watch: the demo has no failing-form state for this page, as the task says.

## 2026-10-03T19:25:14Z · Implementer US5 · T009

Did: InlineField drawn by layout/inline_field.html (daisyui_field unlabelled=True); FieldInput gains unlabelled (show_labels off except single checkbox; placeholder from label on input/textarea); frame and body read drawn.show_labels. README, CHANGELOG, state in STATES, README example, docstring example.
Verified: uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope: 1589 passed; pre-commit clean; mypy clean.
Next: T010 demo page inline-field and its forms on the standalone page.
Watch: table_inline_formset passes form_show_labels=False, still read by the tag.

## 2026-10-03T19:27:07Z · Implementer US5 · T010

Did: demo route inline-field (InlineFieldForm, InlineFieldMixin, InlineFieldView, template, menu, icon), forms added to the standalone page and its post dispatch; README demo section and CHANGELOG.
Verified: uv run pytest tests/test_demo.py tests/test_pack -n auto --dist loadscope: 2336 passed; pre-commit clean; mypy clean.
Next: full verify, ledger evidence, report.
Watch: standalone post dispatch picks the form by submit name; inline-field prefix does not collide with inline.

## 2026-10-03T19:34:44Z · Implementer US6 · T011

Did: FieldInput deep-copies a MultiWidget and classes and names each part (decorate_part): own class names, then the pack's for the part's component (resolve_modifiers per part, so size, colour and variant reach each one, the error modifier replaces the colour), and an aria-label unless the part has one or is hidden (Date and Time from the new SPLIT_DATE_TIME_PARTS for a split date and time, the field's label otherwise). FieldInput keeps `choices` and `placed`; classes_for, own_names and component_of take the part of own_classes, pack_classes and component. The field-level modifiers are empty for a multi-widget. Date and Time in the catalogue; README section "A multi-widget field" and the widgets sentence; CHANGELOG entry; MultiWidgetsForm in tests/forms.py.
Verified: `uv run pytest tests/test_pack/test_multi_widget.py` 14 failed of 31 first (parts had no class or name), then 31 passed; `uv run pytest tests/test_pack/test_multi_widget.py tests/test_templatetags/test_daisyui.py tests/test_pack/test_documented_examples.py tests/test_pack/test_independence.py -n auto --dist loadscope` 506 passed; pre-commit and mypy clean.
Next: T012, the multi-widget-field demo page and its forms on the standalone page.
Watch: a part of a SplitDateTimeField made hidden through MultiWidgetField crashes validation in Django and crispy (its hidden widget is a multi-widget), so that case is tested on another multi-widget and the README says not to.

## 2026-10-03T19:36:31Z · Implementer US6 · T012

Did: route `multi-widget-field` (MultiWidgetFieldForm, MultiWidgetFieldMixin, MultiWidgetFieldView, template demo/multi_widget_field.html on Cotton components, menu item and icon); a required split date and time through MultiWidgetField with a placeholder on each part and an optional one with no layout object, to post and already failing; both forms added to the standalone page and a branch for `multi-widget-submit` in its post dispatch. README demo section and CHANGELOG entry.
Verified: `uv run pytest tests/test_demo.py -k MultiWidget` failed first (28 failed, 10 errors, no route), then `uv run pytest tests/test_demo.py tests/test_pack -n auto --dist loadscope` 2414 passed; pre-commit and mypy clean.
Next: full verify, ledger evidence, report.
Watch: the standalone page's no-django-mvp, no-Cotton check is the one the attached-text class already runs on it.

## 2026-10-03T19:40:10Z · Forge · converge

Converged: no gap between the specification and what was built. Six decision records written (0022 to 0027), three earlier ones marked as amended, README status line brought up to date. Main merged in after each story. Next: code review.
