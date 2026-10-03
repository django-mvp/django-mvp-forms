
## 2026-10-03T21:59:34Z · Forge · plan

Did: confirmed the branch is on main at v0.1.0; wrote research.md, plan.md and tasks.md (3 stories, 6 tasks); created the ledger; appended D12 to D16; filed #115 for the open question about template tags.

Verified: probed both routes in this environment: a replacement in a DIRS directory is drawn for a page template, and for a widget template only with the TemplatesSetting renderer or from an app listed before the pack.

Next: design review, then US1.

Watch: FS-012 builds in parallel, with FS-010, FS-011 and FS-013 to follow. Each may add templates, and every one they add has to join the README list once this feature's check is on main. README, CHANGELOG, tests/conftest.py and tests/test_pack/test_independence.py may move under this branch.

## 2026-10-03T22:16:11Z · Implementer US1 · T001

Did: added the replace and pack_source fixtures to tests/conftest.py and the fifth cache clear (whole_uni_formset_template) to clear_crispy_template_caches. Wrote tests/test_pack/test_replacements.py: TestEveryTemplate (42 templates found on disk, every entry of STATES drawn with a marker copy and with nothing replaced, equal as strings with the marker removed, marker drawn in at least one state except layout/tab-link.html) and TestTheReplaceFixture (settings restored, the five crispy caches empty, a formset replacement gone afterwards). Added two states to STATES, in their own block at the end: a form with media through the filter and through the tag, because dropping form.media from uni_form.html went unnoticed without one. No template reached by no state.
Verified: uv run pytest tests/test_pack/test_replacements.py tests/test_pack/test_independence.py -q: 179 passed in about 12s, so the file is well under a minute. Probes, all reverted and none committed: (1) with every {{ }} dropped from a copy, equality failed for all 74 template copies after the media states were added (before: uni_form.html passed, which is why the states were added); (2) an extra daisyui/unreached.html nobody draws failed the marker half; (3) inlining required_marker.html into frame.html, field_body.html and table_inline_formset.html failed the marker half for required_marker.html; (4) deleting the whole_uni_formset_template clear failed the two cache tests. pre-commit clean.
Next: T002, the scenarios and the placement cases.
Watch: the form renderer strips what a widget template draws, so comparing needs whitespace collapsed; this is in a comment in the test. The equality half cannot detect the pack narrowing the context for a template, as the copy gets the same narrower context.
