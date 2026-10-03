
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
