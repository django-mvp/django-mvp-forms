
## 2026-10-03T23:28:42Z · Forge · plan

Did: rebased the branch onto main at 2f761f4 and pushed it; wrote research.md, plan.md and tasks.md (4 stories, 7 tasks); created the ledger; appended D11 to D17.

Verified: full verify green at 4c154bd before any code (lint, types, 3,811 tests, build, conformance, docs).

Next: design review, then US1.

Watch: FS-011 and FS-012 build in parallel and may move README, CHANGELOG and the test fixtures under this branch, and may write a class daisyUI 5.0 does not define. The record number is provisional until the merge gate.

## 2026-10-03T23:38:33Z · Implementer US1 · T001

Did: Added support-window.toml (python, django, django-crispy-forms with pairs, daisyui minimum and newest; no first keys, no dropped comment), support_window.py (InvalidWindow, Disagreement, Window with read, from_mapping, parse_versions, daisyui, metadata_disagreements and two helper static methods; ROOT, DECLARATION) and tests/test_support_window.py (TestWindow, TestMetadata).
Verified: red first (ModuleNotFoundError for support_window), then `uv run pytest tests/test_support_window.py -x -q` 19 passed; mutation probe (upper-limit check disabled) failed 3 tests; `uv run pre-commit run --all-files` all hooks passed.
Next: T002, the README section, CHANGELOG, CONTEXT, AGENTS.md stack line, relative_links and TestReadmeLinks.
Watch: Window has no *_first fields yet (US3 adds them with the first keys). The Window mapping fields are dicts, so a Window is not hashable.

## 2026-10-03T23:39:41Z · Implementer US1 · T002

Did: Added `relative_links` to support_window.py and TestReadmeLinks; wrote the README section "Supported versions" after Installation (marked table block with the pairs table, period, kinds of release, major versions, CDN interval, no upper limit, how each version leaves, drop in minor or major, empty dropped-versions block with its sentence); pointed the status note and the daisyUI 5 sentence at it; added the CHANGELOG entry under Unreleased/Added, the four CONTEXT terms and the AGENTS.md Stack pointer.
Verified: red first (ImportError for relative_links), then `uv run pytest tests/test_support_window.py -q` 25 passed; the three README-reading test files (test_documented_examples, test_template_surface, test_template_list) plus the new file passed; `uv run pre-commit run --all-files` all hooks passed. No page under docs/ describes versions, so none changed.
Next: ledger, then the full verify and the report.
Watch: relative_links returns [] for a README with no marked block; US2's readme_disagreements is what fails a README with no block.

## 2026-10-03T23:46:24Z · Implementer US2 · T003

Did: Added Window.readme_disagreements (statement block only, read between the support-window comments: package rows by first cell, pairs rows by release), Window.lockfile_disagreements, installed_versions, Window.installed_disagreements and three small static helpers (series, table_rows, set_disagreements); TestReadme, TestLockfile and TestInstalled.
Verified: red first (ImportError for installed_versions), then `uv run pytest tests/test_support_window.py -x -q` 44 passed; two mutation probes (pairs loop emptied, asked branch disabled) each failed one test; `uv run pre-commit run --all-files` all hooks passed.
Next: T004, the class lists, the fixture and the network fetch by hand.
Watch: a README with no block names every declared version as missing, which is what fails it. installed_disagreements takes asked as a dict of package to series with unasked packages absent: the T005 hook must build it that way and keep only disagreements for asked packages.

## 2026-10-03T23:49:28Z · Implementer US2 · T004

Did: Added MissingClassList, fetch_json, fetch_text, class_names, class_list and write_class_list to support_window.py (each urlopen carries `# noqa: S310` with its reason); wrote tests/data/daisyui-classes-5.0.txt (from 5.0.55) and -5.7.txt (from 5.7.47) with write_class_list, once, by hand, from registry.npmjs.org and cdn.jsdelivr.net; removed tests/data/daisyui-classes.txt; made the daisyui_classes fixture in tests/conftest.py session-scoped and parametrised by Window.daisyui with the version as id; changed the one path in ADR 0003 to name both lists; added D19 to decisions.md.
Verified: red first (ImportError for MissingClassList), then `uv run pytest tests/test_support_window.py -q` 57 passed before the fix to the string pattern and again after; `uv run pytest tests/test_support_window.py tests/test_pack/test_independence.py -q -n auto --dist loadscope` 287 passed, the two independence classes now run once per version (ids 5.0-... and 5.7-...); mutation probe (escapes left in) failed 2 tests; `uv run pre-commit run --all-files` all hooks passed.
Next: T005, run_suite, the two conftest hooks, main, the README contributing text and the AGENTS.md line.
Watch: the lists hold 4,034 and 3,660 names, two fewer than research R3 counts, because the old reading also returned `w3` and `org` from an SVG address (D19). ADR 0032 line 24 still names the removed tests/data/daisyui-classes.txt: outside this story's files, left for Forge.

## 2026-10-03T23:52:28Z · Implementer US2 · T005

Did: Added Window.run_suite (subprocess.run reached only through its run parameter), main with test and classes, and the ASKED and SUITE_ARGUMENTS constants to support_window.py; the two hooks in tests/conftest.py (pytest_report_header, pytest_sessionstart); TestRunSuite and TestMain; README "Changing the support window" under Contributing; the pointer in support-window.toml's opening comment; the AGENTS.md command line.
Verified: red first (ImportError for main), then `uv run pytest tests/test_support_window.py -x -q` 67 passed; mutation probe (pair check disabled) failed 3 tests; `uv run python support_window.py test 5.2 2.7` exit 0, header "django: version: 5.2.17", "django 5.2.17", "django-crispy-forms 2.7", 3964 passed in 37.62s; `SUPPORT_WINDOW_DJANGO=5.2 uv run pytest tests/test_smoke.py` on the development environment (Django 6.1.1) exit 4, "ERROR: This run was asked for other versions: django 6.1.1", no test collected; `uv run python support_window.py test 4.2 2.7` exit 2 and nothing run; `uv run pre-commit run --all-files` all hooks passed.
Next: ledger, then the full verify and the report.
Watch: the classes subcommand is only exercised through its refusal of a version that is not two numbers, because running it for real uses the network, which only T004 may. The hooks have no test of their own: the by-hand run above is their evidence.

## 2026-10-04T00:05:59Z · Implementer US3 · T006

Did: Added `first` keys and the commented `[[dropped]]` example to support-window.toml. Added `Dropped`, `Window.parse_dropped`, `Window.dropped_disagreements`, `Window.admitted_disagreements` (the dropped part of metadata_disagreements), `Window.dropped_table_disagreements` (the dropped part of readme_disagreements), `Window.minors_from`, `Window.numbers`, `Window.table_cells` and `django_series_from`. Window gained the three `*_first` fields and `dropped`. README gets the dropped-version sentence and the step-by-step for taking a version out; CHANGELOG extends the Supported versions bullet.
Verified: uv run pytest tests/test_support_window.py (exit 0, 93 passed). Seven mutations of the new mechanisms each failed the suite. uv run pre-commit run --all-files (exit 0). uv run mypy (exit 0). uv run pytest -n auto --dist loadscope (exit 0, 4268 passed).
Next: US4, the releases command.
Watch: `first` is now required in every mapping, so the mappings in tests/test_support_window.py gained it. For django-crispy-forms and daisyUI the walk from `first` is empty when `first` and the newest named are on different major versions.

## 2026-10-04T00:13:29Z · Implementer US4 · T007

Did: Added SOURCES, Outstanding, Window.outstanding, Window.later_series (the series walk shared by the three packages), Window.report_releases, final_releases and the `releases` command in main (with a `fetch` parameter so a test passes its own). fetch_json and fetch_text moved above Window because report_releases takes fetch_json as a default. README "Changing the support window" gets the command, its three statuses, the separate listing of a new major version, the pre-release rule and the pointer to issue 92. AGENTS.md gets one command line.
Verified: red first (ImportError for SOURCES), then `uv run pytest tests/test_support_window.py -x -q` 129 passed. Six mutations of the new mechanism (new_major, one line per major, first-release date, status 1 test, min to max date, final filter) each failed the suite, except min to max, which survived until the test used files on different days; it fails now. `uv run python support_window.py releases` by hand against the real sources: one line, "The window names the newest release of each package.", exit 0. `uv run pre-commit run --all-files` exit 0, `uv run mypy` exit 0, `uv run pytest -n auto --dist loadscope` exit 0, 4304 passed.
Next: the report.
Watch: the by-hand run found nothing outstanding, and no test covers a live payload, so a change in the shape of either source shows up as status 2, not as a wrong 0. No CHANGELOG entry, as the brief says, because the command is not distributed.

## 2026-10-04T00:21:21Z · Forge · converge

Did: accepted US1 to US4; merged main twice (FS-010 record, FS-012); pointed the theme stylesheet check at the newest named class list (T008); small cleanup of support_window.py (one duplicate pattern, two sorts through Window.numbers, the module docstring); wrote ADR 0036; gave every decision its verdict.

Verified: full verify green; the suite passes on each named pair through the test command (Django 5.2.17, 6.0.8 and 6.1.1 with django-crispy-forms 2.7, 4,304 tests each); a pair the window does not offer exits 2 and runs nothing; a run asked for Django 5.2 on 6.1.1 stops with a usage error; no file under mvp_forms/ differs from main; the wheel and source distribution list the same files as main; releases reports nothing outstanding.

Next: code review.

Watch: FS-011 is still building and will take record numbers; 0036 is re-checked at every update of the branch.

## 2026-10-04T00:29:48Z · Implementer review fixes · T009

Did: COR-001. The tests that change a window in one direction now build it from the module's CURRENT mapping and compare it with a README text, a dependency list with classifiers and a lock that the test module supplies. The real files are read only by the seven tests that say the repository agrees with its declaration, through fixtures named repository_*. Added one test each that the supplied README, dependency list and lock agree with the supplied window, so a mutation test starts from agreement.
Verified: before the change, with Django 6.2, daisyUI 5.8 and Python 3.14 added to support-window.toml, the README tables and the pyproject classifiers, `uv run --no-sync pytest tests/test_support_window.py` gave 5 failed and 1 error. After the change the same scratch edit gave 131 passed and 1 error, the error being the check that a class list exists for every daisyUI version the real window names (5.8 has none). Files restored with git checkout; pyproject.toml and uv.lock show no diff. Without the change: 132 passed.
Next: T011, then T010.
Watch: hatchling refuses the classifier Framework :: Django :: 6.2 as unknown, so `uv run` fails to build the project in that scratch state; I used --no-sync for the proof. The README steps do not mention it.

## 2026-10-04T00:30:49Z · Implementer review fixes · T011

Did: COR-002, COR-006, SEC-003. final_releases raises ValueError when an answer lists no final release, and its date check now sits inside the try, so a stamp that is a list is a ValueError too. FINAL takes numbers of at most nine digits, so a version of thousands of digits is not a final release. report_releases catches http.client.HTTPException beside OSError and ValueError. Everything that can raise for one package now happens inside final_releases, which sits inside the try.
Verified: 13 new cases failed first for the right reasons (TypeError on a list stamp, ValueError 'Exceeds the limit (4300 digits)', IncompleteRead leaving report_releases, an empty listing returning status 0). Then `uv run pytest tests/test_support_window.py` gave 145 passed; `uv run pre-commit run --all-files` passed.
Next: T010.
Watch: a listing that holds only versions the window does not name, such as only 1.0, is still read as a listing with a final release. COR-002's fix and this brief ask only for the empty case.

## 2026-10-04T00:33:51Z · Implementer review fixes · T010

Did: COR-003 (README says the daisyUI ends are those named above), COR-004 (requirement names are normalised with [-_.]+ and a package no requirement names is a disagreement with an empty version), COR-005 (a README cell is read with one pattern that takes the whole dotted number), COR-007 (daisyUI minimum and newest are parsed apart; a minimum above the newest, a first above the oldest named version and an empty list of versions raise InvalidWindow), COR-008 (a lock with no Django or django-crispy-forms entry is a disagreement with an empty version), COR-009 (relative_links reads reference definitions, src and angle-bracketed targets), COR-010 (a name after @layer or @container is not a class), SEC-001 (write_class_list encodes before it writes; class_list reads as UTF-8), SEC-002 (preludes are read by splitting, not by a backtracking scan), COR-011 (Window.django_series_from, caller and test updated; the plan's Article X row says why class_names, class_list and write_class_list stay functions). The version patterns use [0-9] instead of \d. README gains the two additions to the take-out steps and AGENTS.md drops the repeated Django list.
Verified: 24 new cases failed first for the right reasons (the long-run case by hanging: `timeout 20 pytest -k long_run` exited 124 before the fix). After: `uv run pytest tests/test_support_window.py` gave 172 passed (173 with test_smoke); `uv run pre-commit run --all-files` passed.
Next: ledger, full verify, report.
Watch: test_a_long_run_with_no_brace_is_read can only fail by taking minutes, since no test may time a run. Empty-list refusal sits in a new Window.named_versions because a pair may legitimately list no Django series.

## 2026-10-04T00:39:13Z · Forge · review

Did: two reviews, both approve; fourteen findings, every one closed by a change (T009 to T012); review write-up posted; ledger at ready.

Verified: full verify green after the fixes; releases against the real sources reports nothing outstanding; no file under mvp_forms/ differs from main.

Next: mark the pull request ready and hand over at the merge gate.

Watch: record number 0036 is free on main as of this push; FS-011 is still building and may claim it first.
