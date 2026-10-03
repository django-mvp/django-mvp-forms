
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

## 2026-10-03T22:20:23Z · Implementer US1 · T002

Did: added tests/host_app (an __init__.py and templates/daisyui/widgets/select_date.html) and, in tests/test_pack/test_replacements.py, TestReplacingOneTemplate (scenarios 1, 2, 3, 4, 5, 7 and 9, each part found by a data-replaced attribute the replacement writes or by an id from the fixtures) and TestWhereAReplacementIsFound (app after and before the pack, a widget replacement in DIRS under the default renderer, two replacements one including the other, tab-link beside tab and alone, a template of the host project's own path, a widget subclass naming its own template, a frame that leaves out the errors). D18 in decisions.md records the whitespace choice and the two media states from T001.
Verified: uv run pytest tests/test_pack/test_replacements.py -q: 72 passed in about 12s. Probes, all reverted and none committed: field.html including a copy of the frame by another path failed 8 tests (scenarios 1 and 5, the frame case of 7, two placement tests); the fixture leaving the default form renderer failed 4 (scenario 3, the widget case of 7, the widget-subclass test, the restore test); the fixture not clearing the crispy caches on the way out failed 5; the required marker inlined at its three draw sites failed all 4 cases of scenario 4; row.html drawing through div.html failed scenario 2; an app listed before the pack in the 'after' test, a DIRS widget replacement under TemplatesSetting, a widget subclass without its own template, and a frame that keeps field_body each failed the placement test that guards them. Scenario 9 has no mutation probe, because the own-template rule is django-crispy-forms'; each of its three tests has a control in the same test (a form without the own template does draw the replacement). FR-017: all 73 original states drawn at ff6d75c and at the tip, ids normalised, compared as strings: identical; nothing under mvp_forms/ changed.
Next: the full verify and the report.
Watch: tests/host_app is a directory of the suite that holds no test, so the conformance step may ask for it to be declared.

## 2026-10-03T22:29:22Z · Implementer US2 · T003

Did: tests/template_surface.py (TemplateSurface: distributed, names_read, renderer_route, listed, disagreements), its tests in tests/test_template_surface.py, tests/test_pack/test_template_list.py, and the README section "Replacing one template" with the routes, the restart note and a 42-row table. The sentence in "Template pack daisyui" about the form renderer points at it.
Verified: uv run pytest tests/test_template_surface.py tests/test_pack/test_template_list.py -q, 29 passed. Probes, not committed: a name added to layout/row.html and a new template added to the pack each made the real check fail with the kind, path and name. pre-commit run --all-files passed.
Next: T004, the worked example, readme_template, TestReadmeReplacement, CHANGELOG and CONTEXT.md.
Watch: a Draws cell cannot hold a pipe, so two sentences name the crispy filter in words.

## 2026-10-03T22:30:29Z · Implementer US2 · T004

Did: the worked example under "#### A required marker of your own" in the README, readme_template and TestReadmeReplacement in tests/test_pack/test_documented_examples.py, the CHANGELOG entry under Unreleased/Added, and Replacement and Template list in CONTEXT.md.
Verified: uv run pytest tests/test_pack/test_documented_examples.py tests/test_pack/test_template_list.py tests/test_template_surface.py -q, 116 passed. Probes, not committed: a condition the example never meets (field.field.requiredx) failed the required-field test; an aria-hidden attribute added to the example failed the pack-marker test. pre-commit run --all-files passed.
Next: the full forge verify, then the report and the ledger.
Watch: docs/ holds ADRs, contributing standards and the roadmap only, so no page under docs/ describes what this story touched.

## 2026-10-03T22:32:13Z · Implementer US2 · T003

Did: moved the helper tests to tests/test_pack/test_template_surface.py, because conformance failed a top-level test module with no source module to mirror (decisions.md D19). Earlier T003 entries name the old path.
Verified: uv run pytest tests/test_pack/test_template_surface.py -q, 27 passed.
Next: the full forge verify, then the report.
Watch: Forge may prefer the module beside the helper, which needs tests/test_template_surface.py declared in non-mirror-paths.
