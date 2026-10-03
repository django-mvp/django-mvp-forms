
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
