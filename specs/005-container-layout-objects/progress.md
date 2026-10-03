
## 2026-10-03T17:22:29Z · Forge · plan

Planned the build: research.md, plan.md and tasks.md written. Four stories, eight tasks, four dispatches. Planning notes answered in research.md. Next: design review.

## 2026-10-03T17:38:00Z · Implementer US1 · T001

Did: TabHolder and Tab drawn by layout/tab.html, tab-pane.html and tab-link.html, a branch in layout/div.html for a Tab, the filter daisyui_tab_group with TAB_GROUP_PLACEHOLDER, and tab-pane and active added to UPSTREAM_ONLY_CLASSES. Tests: tests/test_pack/test_tabs.py (30), the filter and the dropped names in test_daisyui.py, a tabs state (unbound, invalid) in test_independence.py, the TabHolder and Tab docstring examples in test_documented_examples.py. README gains a Tabs section and the dropped-names sentence is rewritten to name all six names and every object; CHANGELOG entry; ADR 0010 names updated.
Verified: `uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope` 737 passed; `uv run pre-commit run --all-files` clean. Red observed first (TemplateDoesNotExist for tab-link.html, 30 failed). Probes: removing form="" from the radio fails the submission tests; removing aria-label fails 16.
Next: T002, the tabs demo page and the standalone page.
Watch: tests/forms.py gains StructureWideErrorForm, StructureHiddenForm and form_field_3 on DocumentedExamplesForm (additions only). The csrf token is a named control the crispy tag draws even with form_tag off, so the submission test names it.

## 2026-10-03T17:39:41Z · Implementer US1 · T002

Did: the tabs page on the shell (route tabs, template demo/tabs.html on Cotton components, menu entry and the icon name tabs in EASY_ICONS) and the standalone page (route containers-standalone, demo/containers_standalone.html, daisyUI's CDN stylesheet alone), each linking the other. TabsForm in demo/forms.py: three tabs, the second and third holding required fields, novalidate on its helper, the prefix in every id. TabsMixin in demo/views.py supplies a form to post and one bound and already failing in its third tab. The standalone page holds only the tabs forms for now; later stories add theirs.
Verified: `uv run pytest tests/test_demo.py -n auto --dist loadscope` 587 passed (20 of them new, red first on NoReverseMatch); `uv run pre-commit run --all-files` clean.
Next: report US1 after the full verify.
Watch: README's Demo section lists the demo pages and does not name the two new routes; it is not in T002's file list, so it is left for Forge to decide (see concerns in the report).

## 2026-10-03T17:44:59Z · Implementer US2 · T003

Did: Accordion and AccordionGroup drawn by daisyui/accordion.html and accordion-group.html (beside field.html): a div holding one details.collapse per group, each with a summary.collapse-title and a collapse-content element, open following div.active only, no name attribute. Tests: tests/test_pack/test_accordion.py (22), an accordion state (unbound, invalid) in test_independence.py, the Accordion and AccordionGroup docstring examples in test_documented_examples.py. README gains an accordion section; CHANGELOG entry. UPSTREAM_ONLY_CLASSES is unchanged: the group templates do not use daisyui_classes, so ADR 0010 needed no edit.
Verified: `uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope` 767 passed; `uv run pre-commit run --all-files` clean. Red observed first (TemplateDoesNotExist for accordion-group.html). Probes: dropping the open clause fails 8, `|safe` on the name fails the escaping test, a name on the details fails the name test.
Next: T004, the accordion demo page.
Watch: AccordionGroup has css_class "" so crispy writes no active class on it; nothing to drop.

## 2026-10-03T17:48:06Z · Implementer US2 · T004

Did: the accordion page on the shell (route accordion, demo/accordion.html on Cotton components, menu entry and the icon name accordion in EASY_ICONS) and its two forms added to the standalone page. AccordionForm (three groups, the third required, novalidate, the prefix in every id and the submit name) and ChosenGroupsForm (first group active=False, second active=True, no form element) in demo/forms.py; AccordionMixin in demo/views.py. ContainersStandaloneView combines both mixins and binds the accordion form only when the post names its submit button, otherwise the tabs form (decisions.md D16). README's Demo section now lists the tabs, accordion and standalone routes, and CHANGELOG has the entry.
Verified: `uv run pytest tests/test_demo.py -n auto --dist loadscope` 609 passed (22 new, red first on NoReverseMatch); `uv run pre-commit run --all-files` clean. Probes: removing active= from the chosen form fails 4, removing the standalone post override fails the tabs-post test.
Next: full verify, then the report.
Watch: a post with an empty body to the standalone page still binds the tabs form, because US1's tests post {} there and expect it (D16).

## 2026-10-03T17:54:34Z · Implementer US3 · T005

Did: Modal drawn by daisyui/layout/modal.html: a dialog.modal with the developer's id, a modal-box holding an h3 title (id <title_id>-label, which aria-labelledby names), the fields and one type=button close control with translatable text; `open` when the drawn fields hold aria-invalid="true", tested in the template. "Close" added to the English catalogue with makemessages (en, from inside mvp_forms/). Tests: tests/test_pack/test_modal.py (19), a modal state (unbound, invalid) in test_independence.py, the Modal docstring example (unclosed quote repaired) in test_documented_examples.py. README gains a Modal section with how a host project opens it by id; CHANGELOG entry. UPSTREAM_ONLY_CLASSES unchanged: the modal template uses no daisyui_classes, so the README sentence on dropped names stays as US1 left it.
Verified: `uv run pytest tests/test_pack -n auto --dist loadscope` 675 passed; `uv run pre-commit run --all-files` clean. Red observed first (TemplateDoesNotExist for daisyui/layout/modal.html). Probe: removing the open clause fails 4 tests.
Next: T006, the modal demo page.
Watch: a test attribute named title collides with Modal's own title argument, so the developer-attrs test uses lang.

## 2026-10-03T17:56:53Z · Implementer US3 · T006

Did: the modal page on the shell (route modal, demo/modal.html on Cotton components with a c-button that calls showModal() on the dialog's id, menu entry, the icon name modal in EASY_ICONS) and its form added to the standalone page with a plain button for the same job. ModalForm in demo/forms.py: name outside the modal, street and city required inside it, novalidate, the prefix in every id and the submit name, `dialog_id` the one source of the dialog's id. ModalMixin in demo/views.py; ContainersStandaloneView adds a modal-submit branch before the accordion one and still falls back to the tabs form. README's Demo section lists /modal/ and the standalone page's three forms; CHANGELOG entry.
Verified: `uv run pytest tests/test_demo.py -n auto --dist loadscope` 629 passed (20 new, red first on NoReverseMatch); `uv run pre-commit run --all-files` clean. Probe: removing the standalone modal branch fails 3 tests.
Next: full verify, then the report.
Watch: the standalone page's open control is a plain button with daisyUI's btn classes because that page has no Cotton.

## 2026-10-03T18:01:58Z · Implementer US4 · T007

Did: Alert drawn by daisyui/layout/alert.html: a div with role="alert", the alert class from the layout object's css_class passed through daisyui_classes, the content drawn with |safe in a span, and a type=button dismiss control named by a translatable aria-label that removes the alert; no button with dismiss=False. `alert-block` joins UPSTREAM_ONLY_CLASSES so block=True draws without the name. "Dismiss" added to the English catalogue with makemessages. Tests: tests/test_pack/test_alert.py (12), an alert state (unbound, invalid) in test_independence.py, the Alert docstring example (apostrophe repaired) in test_documented_examples.py, the alert-block case in test_daisyui.py. README: status line and Layout objects intro name the six as supported, an Alert section with the trusted-content note, the dropped-names sentence rewritten to seven names and the four objects they leave (buttons, MultiField, Tab, Alert). ADR 0010 lists alert-block and Alert. CHANGELOG entry.
Verified: `uv run pytest tests/test_pack tests/test_templatetags -n auto --dist loadscope` 809 passed; `uv run pre-commit run --all-files` clean. Red observed first (TemplateDoesNotExist for daisyui/layout/alert.html). Probe: renaming alert-block in UPSTREAM_ONLY_CLASSES fails the block test and the filter test. The README Alert example run against this branch draws the alert between the two fields.
Next: T008, the alert demo page.
Watch: Alert.css_class is a plain str, so block=True sets it on the instance, never on the class.

## 2026-10-03T18:03:30Z · Implementer US4 · T008

Did: the alert page on the shell (route alert, demo/alert.html on Cotton components, menu entry and the icon name alert in EASY_ICONS) and its form added to the standalone page. AlertForm in demo/forms.py: a dismissible alert, a permanent one (dismiss=False) and one with alert-success between the fields, a required name field, novalidate, the prefix in every id and the submit name. AlertMixin in demo/views.py; ContainersStandaloneView adds an alert-submit branch before the modal one and still falls back to the tabs form. The standalone page now holds a tabs element, details, a dialog and an alert. README's Demo section lists /alert/ and the standalone page's four forms; CHANGELOG has the entry.
Verified: `uv run pytest tests/test_demo.py -n auto --dist loadscope` 652 passed (23 new, red first on NoReverseMatch); `uv run pre-commit run --all-files` clean. Probe: removing the standalone alert branch fails the bind-only-that-form test.
Next: full verify, then the report.
Watch: the alert form posts so that a bound render shows the alerts drawn again; its text is plain English in the demo, as the other pages' prose is.
