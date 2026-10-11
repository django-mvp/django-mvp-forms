## 2026-10-11T22:06:34Z · Orchestrator · plan

Research, plan and task list written: 6 stories, 8 tasks. No sketch. The build continues on pull request #171.

## 2026-10-11T22:18:39Z · Implementer US1 · T001

Did: Added TomSelectMultiple (a SelectMultiple that writes data-tom-select holding {} in build_attrs and names mvp_forms/tomselect.js in its media). Tests first: widget tests in tests/test_widgets.py, pack tests in tests/test_pack/test_tom_select_widgets.py, forms in tests/forms.py. No change to the pack's templates or tags, since the pack picks the select component by isinstance of forms.Select.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py -q, 345 passed. Red seen first as an ImportError on the missing widget. Probed the media and markup tests by giving forms.SelectMultiple the same Media: two tests failed, then reverted.
Next: T002, the script and its Chrome tests.
Watch: the test_widgets.py module docstring now names the Tom Select widgets too. The stock-select comparison test strips script tags and blank lines, since {% crispy form %} draws the form's media.

## 2026-10-11T22:29:17Z · Implementer US1 · T002

Did: Added mvp_forms/tomselect.js: one flag on window, waits for the load event, starts a control on each select[data-tom-select] that has no tomselect property when window.TomSelect is a function, passes placeholder, maxItems and plugins from the attribute plus maxOptions null, copies aria-describedby to the control's input, leaves a refused select alone. Added the Chrome tests in tests/test_tomselect_e2e.py with a test page, view and routes (tests/urls.py, tests/templates/tests/tomselect_page.html, TomSelectPageForm in tests/forms.py). The static-files list test gained the script.
Verified: uv run pytest tests/test_tomselect_e2e.py -q -n 4, 16 passed. Red seen first with the script moved aside: the control tests failed on a missing control. Probed by breaking the script six ways (no Tom Select guard, no flag and no per-select guard, no maxOptions, no aria copy, selector widened to any select, no try/catch): each broke the test that covers it. Starting at once instead of after load broke 14.
Next: T003, documents and the demo.
Watch: a select Tom Select refuses keeps a stray tomselect property but no wrapper and stays visible, so the test asserts on the wrapper and visibility. The refused test relies on plugins naming one that does not exist. The label test clicks label[for=id_fruit-ts-control], since Tom Select moves the for to its input.

## 2026-10-11T22:35:27Z · Implementer US1 · T003

Did: Added the README section "Tom Select widgets", the CHANGELOG entries, four CONTEXT.md terms and the widened option group entry, and reworded the head of tomselect.css and the module docstring of widgets.py. Added the demo pages at /tom-select-widgets/ and /tom-select-widgets/standalone/ (forms, views, routes, a sidebar entry after django-countries, two templates). The standalone page loads Tom Select's complete build and default stylesheet from jsdelivr with sha384 integrity hashes. The script's hash is computed from tests/data/tom-select-2.5.2.complete.min.js and matches the CDN file byte for byte. The stylesheet hash is of the file fetched from the CDN.
Verified: uv run pytest tests/test_pack tests/test_widgets.py tests/test_demo.py -q -n 4 --dist loadscope, 4627 passed. Red seen first as a missing demo module. Both pages answer 200 and hold the widget's select, once each of the form's script. A test runs the README's python example and draws it.
Next: full verify, then the report.
Watch: the README says a select added after the page loads is left as a stock select, which T007's observer will change. The sidebar entry sits after django-countries, because an existing test pins django-countries directly after django-tomselect.

## 2026-10-11T22:37:17Z · Implementer US1 · T002

Did: Full verify found one red step. Conformance refused tests/test_tomselect_e2e.py as a test that mirrors no source module. Listed it beside the other two browser test files under [tool.forge.conformance] non-mirror-paths in pyproject.toml, as the standard says to declare such a path.
Verified: forge verify, all six steps on the three task commits: lint, typecheck, test (63 s), build and docs passed, conformance failed on that one line. After the change, forge verify --steps conformance passed and pre-commit passed.
Next: report.
Watch: pyproject.toml is outside the brief's file list for T002.

## 2026-10-11T22:48:38Z · Implementer US2 · T004

Did: Added TomSelect, a Select that writes data-tom-select holding {} and names mvp_forms/tomselect.js. What it shares with TomSelectMultiple is one mixin in mvp_forms/widgets.py, TomSelectAttribute, which holds the attribute and the media. Tests first: TestTomSelect and TestWhatTheTomSelectFieldReceives in tests/test_widgets.py, TestTomSelect in tests/test_pack/test_tom_select_widgets.py, TestTheSingleWidget in tests/test_tomselect_e2e.py, with TomSelectSingleForm, StockSingleForm and two fields on TomSelectPageForm in tests/forms.py. README names TomSelect in the surface, the example and the section. CHANGELOG has an entry. The demo forms gained a single field beside the multiple one in the form, each state, each size, each colour and the comparison, and the shell page's two intro texts name both widgets.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py -k TomSelect, 105 passed. uv run pytest tests/test_tomselect_e2e.py -k TheSingleWidget, 4 passed. uv run pytest tests/test_demo.py tests/test_pack/test_tom_select_widgets.py -k "TomSelectWidgets or TomSelect", 132 passed. Red seen first as an ImportError on the missing widget and a missing field on the demo pages. The browser tests were probed by removing the attribute write: all four failed. pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: Tom Select ignores typed keys in a single control that holds a value, so the control cannot be searched until it is cleared or a choice is clicked. The browser tests click the option for that reason. The script needed no change. The README's Backspace sentence rests on the browser test only.

## 2026-10-11T22:50:23Z · Implementer US2 · T004

Did: The first full verify failed its docs step: the mixin TomSelectAttribute is a new public name that no page quotes, and the house rule against leading underscores makes it public. Named it in the README's public surface and section, gave it a sentence on how a select widget of one's own takes it, added a test that such a widget is drawn with the attribute and the script, and added the line to the CHANGELOG entry.
Verified: uv run pytest tests/test_widgets.py -k TomSelect, 32 passed. The new test fails with the attribute write removed. pre-commit run --all-files passed. The full verify runs again after this entry.
Next: full verify, then the report.
Watch: documenting the mixin makes it a promise to consumers. If Sam would rather keep it out of the surface, the alternative is a docs exemption for it in pyproject.toml, or sharing by subclassing, which makes a multiple widget a TomSelect.

## 2026-10-11T23:04:52Z · Implementer US3 · T005

Did: Added placeholder and clear_button to TomSelect and remove_button and max_items to TomSelectMultiple, keyword-only, written under Tom Select's names (placeholder, maxItems, plugins) and nothing for a setting not stated. TomSelectMultiple now extends TomSelect and SelectMultiple, as Django's SelectMultiple extends Select, and TomSelectAttribute is gone from the code, the README and the CHANGELOG. CONTEXT.md held no mention of it. Wrong values raise ValueError naming the argument, a lazy placeholder is turned into text in build_attrs, and TomSelect given remove_button or max_items raises TypeError. The README gained a "Settings" subsection with the one sentence on searching a single control and the one on max_items=1. The demo pages gained a "Settings" section.
Verified: uv run pytest tests/test_widgets.py tests/test_pack/test_tom_select_widgets.py, 452 passed. uv run pytest tests/test_tomselect_e2e.py, 25 passed. uv run pytest tests/test_demo.py -k TomSelectWidgets, 32 passed. Red seen first on each new test (TypeError on the unknown keyword, a missing demo form). Probed by writing {} in place of the settings (19 widget and pack tests failed), by turning the lazy placeholder into text at definition (the lazy tests failed), and by emptying the script's list of names it reads (the placeholder, clear button, remove button and largest-number browser tests failed). The first largest-number test passed under that last break because it clicked a control that was already focused, so it was rewritten to open the dropdown by clicking the control and to fail without the setting. pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: the one test US2 wrote for TomSelectAttribute, in tests/test_widgets.py, was removed with the mixin. tests/forms.py gained fields and a form, and tests/test_demo.py a test, which T005's file list does not name.

## 2026-10-11T23:13:37Z · Implementer US4 · T006

Did: Added two Chrome tests in tests/test_tomselect_e2e.py: a field with grouped choices lists its options under the group headings in the order written, and an option a subclass draws with disabled is listed and stays unchosen after a click. The test page gained a grouped field and a field on a subclass that overrides create_option (tests/forms.py). The README gained "Groups and unavailable options" with a runnable example, and both demo pages gained a section showing grouped choices on both widgets and one unavailable option. No package code changed.
Verified: uv run pytest tests/test_tomselect_e2e.py -k GroupsAndUnavailable, 2 passed on the unchanged package. Probed by breaking the widget in mvp_forms/widgets.py, then restoring it. Flattening optgroups in TomSelect made the group test fail with an empty list of headings. Stripping disabled from each option's attrs in TomSelect.optgroups made the disabled test fail with items ['b'] where [] was expected. Making the script start no control failed both on the missing wrapper. uv run pytest on tests/test_demo.py, tests/test_pack/test_tom_select_widgets.py and tests/test_widgets.py with -k "TomSelect or Readme", 213 passed. pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: the test for the demo section is in tests/test_demo.py, and the one that runs the README example is in tests/test_pack/test_tom_select_widgets.py, neither named in T006's file list. The CHANGELOG is untouched because no public surface was added. Playwright treats an aria-disabled option as not enabled, so the disabled test clicks with force=True to reach Tom Select's own handler.

## 2026-10-11T23:30:53Z · Implementer US5 · T007

Did: The script now watches the document for added nodes with a MutationObserver started beside its first scan, in the shape of imask.js. It looks only at added elements that are, or hold, select[data-tom-select], and skips a select that already has a control, so the nodes Tom Select adds as it starts one cost a match and a search of their own children. Tests first, in tests/test_tomselect_e2e.py: a select added alone and inside another element, a row made from the empty form of a formset kept in a template with __prefix__ replaced (options, placeholder, submitted under the row's name, aria-describedby copied), the script three times on the page, a moved select, the select in the template, and a control in a Modal. The test page gained the template and a Modal (tests/forms.py, tests/urls.py, tests/templates/tests/tomselect_page.html). Both demo pages gained a formset whose rows are added from its empty form by a few lines of script in the template, and a Modal holding both widgets. The README's "What the script does" and "In a formset" now describe the script as it is, with a runnable example, and the CHANGELOG has an entry.
Verified: uv run pytest tests/test_tomselect_e2e.py, 38 passed (7 of the 11 new tests red first, because a late select got no control; the other four held already, see Watch). uv run pytest tests/test_demo.py -k TomSelectWidgets, 42 passed. Probed by dropping the already-started guard (the moved-select test failed on a script error), by scanning the template's content at load (four failed, including the template test), and by skipping selects in a closed dialog (six failed, both modal tests among them). Both demo pages were opened in Chrome: a row added with the button holds a control, and a value is chosen in the modal. pre-commit passed on every changed file.
Next: full verify, then the report.
Watch: removing the window flag that makes a second copy of the script return at once leaves the three-copies test green, because the already-started guard stops a second control by itself. The test pins the outcome, not the flag. The select in a closed modal and a moved select hold before the observer exists, so those tests are proved by the probes above and not by a red run. Chosen values are picked by clicking the option in the new tests: the existing pick helper presses Enter before Tom Select has filtered the list, which in a modal chooses the first option. The demo's formset template draws the empty form with its management form emptied, so no id repeats.

## 2026-10-11T23:38:52Z · Implementer US6 · T008

Did: The script now sends mvp-forms:tomselect from each select once its control has started, bubbling, with the instance in event.detail.tomselect, in the shape of imask.js. It is sent after the aria-describedby copy, so the select holds its instance by the time a listener runs, and not at all for a select Tom Select refused. Seven Chrome tests in tests/test_tomselect_e2e.py (TestTheEvent): each select once with the instance it holds, once with the script three times on the page, from a select added later and from the select of a row added later, not again for a moved select, not for a refused select, and a listener that calls addOption on the instance changes the control. An eighth takes the README's listener, swaps in the test page's ids, and shows it changes its control. The README gained "The event" under "Tom Select widgets" with that example, the event joins the public surface, the "not supported" list points to it, and the CHANGELOG has an entry.
Verified: uv run pytest tests/test_tomselect_e2e.py::TestTheEvent, 8 passed. Six of the first seven were red first, because no event was sent (the moved-select test held with no event at all). uv run pytest tests/test_tomselect_e2e.py tests/test_pack/test_tom_select_widgets.py, 129 passed. Probed by sending the event twice (four tests failed, the once-each and added-later ones) and by dropping the already-started guard (the existing moved-select test failed on the script error, the new one held, see Watch). uv run pre-commit run --all-files passed.
Next: full verify, then the report.
Watch: the new moved-select test passes with the already-started guard removed, because Tom Select throws on a started select and the script's catch returns before the event. The existing TestAMovedSelect is the test that proves the guard. A listener registered after the page has loaded hears only controls started later, which the README says. No page under docs/ describes the script or the widgets (only ADRs, which are written at convergence).

## 2026-10-11T23:54:34Z · Implementer FIX-1 · T009

Did: Added one Chrome test in tests/test_tomselect_e2e.py: a select added later whose data-tom-select holds create true and a placeholder gets a control whose settings do not have create on, and whose placeholder arrived. No package code changed.
Verified: uv run pytest tests/test_tomselect_e2e.py -k does_not_read, 1 passed. Probed by replacing the loop over the three names in tomselect.js with Object.assign(given, written): the test failed on assert not True for settings["create"]. The script was restored from a copy and git status showed only the test file changed.
Next: T010, then T011, then full verify.
Watch: the control's settings are read from the instance (tomselect.settings), so the test shows what the script handed to Tom Select, not Tom Select's own behaviour for create.

## 2026-10-11T23:57:15Z · Implementer FIX-1 · T010

Did: Removed the pick helper from tests/test_tomselect_e2e.py. Its three users, the no-request test, the two-values test and the remove-button test, now call choose, which clicks the option by its value, and choose sits where pick was. The stylesheet test in tests/test_demo.py no longer asserts that the integrity value starts sha384-, and keeps the check that an integrity attribute is present and crossorigin is anonymous.
Verified: uv run pytest tests/test_tomselect_e2e.py -n 4, 47 passed. uv run pytest tests/test_demo.py -k default_stylesheet_from_the_cdn, 1 passed. The first run after the swap failed two tests, because a second choose on a multiple control clicks a control whose dropdown is still open and the option is not visible. Each of those two tests now presses Escape between its two choices, as the late control tests already do.
Next: T011, then full verify.
Watch: choose now opens a multiple control by its control element, which the earlier tests already did for the late controls.
