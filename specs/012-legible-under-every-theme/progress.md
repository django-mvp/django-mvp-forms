# Progress — 012 Forms stay legible under every daisyUI theme

## 2026-10-03T22:23:46Z · Implementer US1 · T001

Did: copied daisyUI 5.7.47 themes.css to tests/data/daisyui-themes.css (the end-of-file hook added one trailing newline) and added its refresh note to the classes header. Wrote Colour (parse, mixed, faded, over, luminance, contrast) and Theme/Themes under tests/legibility/. Compositing keeps channels unclipped until the end, as a browser does; clipping first gives dark's 60% base-content 170 in blue where the reference has 178.
Verified: uv run pytest tests/test_legibility (37 passed); forge verify once to learn the conformance rule: it asked for tests/test_legibility/ as a non-mirror path, added to pyproject.toml; all six steps passed after.
Next: T002 Ink, Pairing, Measurement, Reader, Catalogue.
Watch: the vectors in research R4 hold to one step in 255 and two places.

## 2026-10-03T22:33:15Z · Implementer US1 · T002

Did: Ink, Pairing, Element and Measurement (pairings.py); Reader with one paints table, a silent set and Uncovered (reader.py); Catalogue drawing the 73 listed states, the disabled and read-only forms, a disabled file input, a disabled toggle and switch, and the sweeps (157 states in all). Wrote the tests first and saw them fail on the missing modules.
Verified: uv run pytest tests/test_legibility (165 passed). Probed the reader tests by mutation (override, label share, held on a disabled button, radio own, soft fill, unchosen tab): each made one test fail. Read against the 35 themes, the own shortfalls match the brief: label 15, text-error 21, tab 33, error alert 23, plus the dismiss button's btn-ghost on coloured alerts and a radio ring inside label.
Next: T003, the check and the repairs.
Watch: a radio's ring and dot take the inherited text ink, so a label's 60% reaches them; the faded border of a radio is not own.

## 2026-10-03T22:37:47Z · Implementer US1 · T003

Did: KnownExceptions and the report command (python -m tests.legibility); TestEveryTheme (35 themes), TestPublishedExceptions, TestRepairs and the data-theme test in TestDistributedFiles, written first and seen to fail on the pack as it stood (TestRepairs named label 15 themes, text-error 21, tab 33, thead 15, error alert 23, a radio's ring in a label, and the dismiss button's btn-ghost on coloured alerts). Repairs, class attributes only, in field_body, required_marker, errors, errors_formset, table_inline_formset, tab-pane, clearable_file_input, group_options and alert. Pasted the report's table (45 rows) into the README's Themes section; CHANGELOG, CONTEXT and AGENTS.md updated.
Verified: uv run pytest -n auto --dist loadscope: 3447 passed. FR-010: rendered all 73 STATES entries before and after with a throwaway script under /tmp/fs012/work, stripped class attributes and the random tab and accordion ids: identical (a second render at the base is the control). No earlier test needed a change: they find the label by class_="label", which still matches, and none asserts text-error.
Next: Forge reviews the story.
Watch: the end-of-file hook adds one trailing newline to tests/data/daisyui-themes.css, so it is the CDN file plus that newline.

## 2026-10-03T22:47:47Z · Implementer US2 · T004

Did: TestTheCheckCatches (help text without its ink, the failure text, stale, unlisted, an added theme read and checked, Uncovered) and TestCoverage (every daisyUI class literal in a pack template is drawn by a catalogue state; every disabled control's pairings are unheld with a ratio under every theme; dimmed has every theme). The failure text moved into KnownExceptions.failures, which TestEveryTheme now calls. README Themes: how to run the report and what to do on a failure. Nothing under .github/ changed.
Verified: uv run pytest tests/test_pack/test_legibility.py -q, 49 passed. Eleven probes, each reverted: the help text template without text-base-content (cupcake fails TestEveryTheme), the fragment keeping its ink, the failure text without state, theme or pairing, stale and unlisted reversed, Themes.read dropping or skipping the added theme, the reader no longer raising Uncovered, a literal in a branch no state draws, a state dropped from the catalogue, disabled content held, not read, or missing a theme, the README row gaining or losing a theme. Every one failed its test for the right reason. No gap in tests/legibility/ turned up.
Next: full verify, then the report.
Watch: the coverage test reads the template sources, so a class written only in a Python module is not covered by it.

## 2026-10-03T22:59:39Z · Implementer US3 · T005

Did: the Themes page in the shell (themes) and standalone (themes-standalone): ThemesMixin builds groups of forms from the demo's own forms, with a prefix each, drawn apart (no form element, no token); one element, theme-forms, holds only crispy output and plain headings; the chooser, the explanation and the modal button sit outside it. THEME_NAMES and DAISYUI_VERSION in demo/forms.py; routes, one sidebar entry, one icon. Added ReadOnlyKindsForm, AlertColoursForm, LockedKindsForm and UneditableChoicesForm because the catalogue holds pairings only they draw (a disabled ghost input; an invalid uneditable checkbox and radio; an alert in each colour).
Verified: wrote ThemesPageContract first and saw it fail on the missing names; the pairing test then named six missing pairings, two rounds of forms emptied it. uv run pytest tests/test_demo.py -n auto --dist loadscope: 1246 passed. pre-commit run --all-files and mypy clean.
Next: T006, README and CHANGELOG.
Watch: the page weighs about 260 kB because it draws 105 forms; the shell page links themes.css through the styles block with block.super, so django-mvp's own stylesheet stays.

## 2026-10-03T22:59:39Z · Implementer US3 · T006

Did: README Themes section completed: the promise under a theme, the standard and the parts it holds, the 35 themes of the pinned version, error messages in the text colour, disabled content measured and not held, what a project with its own theme should know, the demo pages. The table and its two markers are untouched. CHANGELOG Added: the check, the demo page, the README section; the Changed entry stays.
Verified: the test the task asks for, every theme the table names is a shipped theme, already exists as TestPublishedExceptions.test_every_theme_the_list_names_is_a_shipped_theme (US1). Probed it: a table row naming "bogus" failed it and the staleness test; restored, 3 passed. No new test written.
Next: full verify, then the report.
Watch: README and CHANGELOG already used the word component in earlier entries; none was added.

## 2026-10-03T23:33:49Z · Implementer FIX-1 · T008

Did: Reader reads a rating by its stars (lit mark, unlit border at 20%, in base-content or the bg-{colour} class) and a range (mark of its ink, border at 10%, dimmed to 30% when disabled, not held). Catalogue draws a rating and a range in every colour and size, and disabled. README table pasted from the report, Themes prose and CHANGELOG extended. D27 written.
Verified: uv run pytest tests/test_legibility tests/test_pack/test_legibility.py tests/test_demo.py -n auto --dist loadscope: 1577 passed. pre-commit run --all-files: all passed.
Next: T009, the review's findings (a) to (j).
Watch: a range's empty track and an unlit star fall short under every shipped theme and are published, as the brief asks.
