
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
