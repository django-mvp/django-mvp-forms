# Tasks — 013 A stated support window

**Branch**: `013-support-window` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation lands in the task that introduces what
it describes.

No test asserts wording. A disagreement is asserted by its `source`, `package` and `version`,
never by its `problem` sentence. An error is asserted by its type and its attributes. The README
is read only between its marked comments, and a table row is found by the package name in its
first cell. Each check is tested twice over: against this repository as it stands, where it finds
nothing, and against a window or a document changed in one direction, where it names the version.

Code standards for every task: no leading-underscore names anywhere (functions, helpers,
constants, module-level names); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. `support_window.py`
imports the standard library only. Nothing under `mvp_forms/` changes, and nothing under
`.github/`. `pyproject.toml` and `uv.lock` do not change. A document reads as current state: no
dated notes and no "amended" stamps in README, CHANGELOG or CONTEXT. README links are absolute.

## Decision records

The record named in the plan is written at convergence, after the last story, with its number
read from `origin/main` at that moment. No task writes it.

## Order

**US1 → US2 → US3 → US4, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Someone deciding whether to adopt reads what is supported (P1)

Issue: #107. Delivers FR-001 to FR-008, FR-022, FR-024; SC-001, SC-002, SC-007.

### T001 — The declaration, and the package metadata held to it

**Files**: `support-window.toml` (new), `support_window.py` (new),
`tests/test_support_window.py` (new)

Plan, *The declaration*, *Reading the declaration*, *Comparing* (`Disagreement`,
`metadata_disagreements`); research R1, R2, R6.

- `support-window.toml` as the plan gives it, without the `first` keys and the `dropped` comment,
  which arrive with US3, and without the sentence of its opening comment that points at the
  README, which arrives with T005.
- `InvalidWindow`, `Window` with `read` and `from_mapping`, `ROOT`, `DECLARATION`,
  `Disagreement`, `Window.metadata_disagreements` without its dropped part. Every comparison in
  this feature is a method of `Window` (plan, *Constitution Check*, Article X).
- Tests, `TestWindow`: a window built from a mapping the test supplies has the versions the
  mapping gave; a file the test writes under `tmp_path` reads as the same window; the
  repository's declaration reads without error. No test asserts the versions the repository
  declares today. A Django version, a
  django-crispy-forms version and a daisyUI version each written with a patch number raise
  `InvalidWindow` carrying the package and the version; a pair naming a release or a Django
  series the window does not name raises it too.
- Tests, `TestMetadata`: the repository's `pyproject.toml` has no disagreement; a window with a
  Django series added, and one with a series removed, each give a metadata disagreement naming
  that series; a raised django-crispy-forms minimum names the version the metadata requires; a
  requirement with an upper limit (`django>=5.2,<7`) is a disagreement; a Python version added
  to the window names that version.

### T002 — The statement in the README

**Files**: `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `AGENTS.md`, `support_window.py`,
`tests/test_support_window.py`

Plan, *The README*, *Comparing* (`relative_links`); research R7.

- `## Supported versions` after "Installation", as the plan lays it out: the marked block with
  the table and the pairs table; the prose for FR-002, FR-005, FR-006, FR-007,
  FR-008, FR-015, FR-016 and FR-018 and the edge cases the plan lists; the second marked block,
  empty, with its sentence. The status note at the top of the README and the sentence "Pages
  that draw these forms must load daisyUI 5" point at the section where they touch on versions.
- CHANGELOG, under `[Unreleased]`, `Added`: the statement, written for someone deciding whether
  to upgrade.
- CONTEXT: "Support window", "Named version", "Period" and "Dropped version", each with what to
  avoid.
- AGENTS.md: the "Stack" line points at `support-window.toml` as where the versions are
  declared.
- `relative_links`.
- Tests, `TestReadmeLinks`: the section of the repository's README holds no relative link; a
  section given a relative link returns it.

---

## US2 — Every version the statement names is tested (P2)

Issue: #109. Delivers FR-009 to FR-014, FR-023, FR-024; SC-003, SC-004.

### T003 — The README, the lockfile and the installed versions held to the declaration

**Files**: `support_window.py`, `tests/test_support_window.py`

Plan, *Comparing* (`readme_disagreements` for the statement, `lockfile_disagreements`,
`installed_versions`, `installed_disagreements`).

- Tests, `TestReadme`: the repository's README has no disagreement; a window with a Django
  series added, one with a series removed, one with a django-crispy-forms release added, one
  with the daisyUI minimum raised, one with the daisyUI newest lowered, one with a Python
  version added and one with a pair removed each give a README
  disagreement naming the version; a README with no marked block
  is a disagreement.
- Tests, `TestLockfile`: the repository's `uv.lock` has no disagreement; a lock holding Django
  7.0.1, and one holding django-crispy-forms 3.0, each name that version.
- Tests, `TestInstalled`: the versions this run is on are inside the window; installed Django
  7.0 with nothing asked names it; Django 6.1.1 installed when 5.2 was asked names 6.1.1;
  Django 5.2.17 installed when 5.2 was asked is no disagreement; django-crispy-forms 2.8
  installed when 2.7 was asked names 2.8; 2.7 installed when 2.7 was asked is no disagreement.

### T004 — A class list for every named daisyUI version

**Files**: `support_window.py`, `tests/test_support_window.py`, `tests/conftest.py`,
`tests/data/daisyui-classes-5.0.txt` (new), `tests/data/daisyui-classes-5.7.txt` (new),
`tests/data/daisyui-classes.txt` (removed), `docs/adr/0003-daisyui-classes-and-tailwind-for-layout-only.md`

Plan, *The class lists*, *`classes`*, *Comparing* (`class_list`); research R3.

- `class_names`, `write_class_list`, `class_list`, `MissingClassList`, `fetch_json` and
  `fetch_text`. Each `urlopen` call carries `# noqa: S310` with its reason on the line (plan,
  *Security*, R-S1). `pyproject.toml` gains no lint exemption.
- ADR 0003 names the old list's path. Change that path to name the two lists, and nothing
  else in the record.
- The two lists, written by `write_class_list` (this is the one step of the feature that uses
  the network, and it is run by hand, never by a test). The old list is removed.
- The `daisyui_classes` fixture takes one parameter for each version `Window.daisyui` returns,
  with the version as its id. This is the one change to existing test code in the feature, and
  no test that uses the fixture changes. Say so in the report.
- Tests, `TestClassNames`: a stylesheet's class selectors are returned with escapes undone
  (`.md\:flex-row` is `md:flex-row`, `.\32 xl\:btn` is `2xl:btn`), a selector that starts with
  a digit in a number such as `0.5` is not a class, and a class is found inside a compound
  selector.
- Tests, `TestClassLists`: every version `Window.daisyui` returns has a list that is not empty;
  a version with no list raises `MissingClassList` carrying the version; `write_class_list`
  given a registry and a fetch function writes the list of the newest patch release of the
  minor version asked for, to a directory the test supplies, and refuses a version that is not
  two numbers.

### T005 — The suite on one named pair

**Files**: `support_window.py`, `tests/test_support_window.py`, `tests/conftest.py`,
`README.md`, `AGENTS.md`, `support-window.toml`

Plan, *`test`*, *`main`*; research R4.

- `Window.run_suite` (`subprocess.run` is only ever called through its `run` parameter), the
  opening comment of `support-window.toml` pointing at the README section, the two hooks in `tests/conftest.py`, `main` with `test` and `classes`.
- README, contributing, "Changing the support window": the `test` command and what it reports;
  how to add a version (the declaration, the README table, the metadata, a class list for a
  daisyUI version, and running the pair) so the four change together (FR-013); that the test
  workflow runs every named Django and Python version and the one named django-crispy-forms
  release, and that a second named release needs #92 (FR-014). AGENTS.md names the command.
- Tests, `TestRunSuite`, with a `run` function given by the test that records what it was
  called with: a named pair runs one command that pins both versions and carries both
  environment variables, and returns that command's status; a Django series the window does not
  name runs nothing and returns a failing status; so does a django-crispy-forms release it does
  not name, and a pair `pairs` does not hold.
- Tests, `TestMain`: `test 5.2 2.7` reaches `run_suite` with those versions.
- By hand, recorded in the report with its output: `uv run python support_window.py test 5.2
  2.7` passes and its header names Django 5.2; `SUPPORT_WINDOW_DJANGO=5.2 uv run pytest
  tests/test_smoke.py` stops with a usage error and runs no test.

---

## US3 — A host project on a version that has left the window (P3)

Issue: #110. Delivers FR-009, FR-013, FR-015 to FR-018, FR-024; SC-005.

### T006 — Dropped versions

**Files**: `support-window.toml`, `support_window.py`, `tests/test_support_window.py`,
`README.md`, `CHANGELOG.md`

Plan, *The declaration* (`first`, `dropped`), *Comparing* (`dropped_disagreements`, the dropped
part of `metadata_disagreements` and `readme_disagreements`).

- `first` for each of the three in the declaration, and the `dropped` comment. `Dropped`,
  `django_series_from`, `dropped_disagreements`, and the dropped parts of the two functions.
- README, contributing: taking a version out, step by step (the declaration's `versions` and a
  `dropped` table, the README's two tables, the metadata minimum, the CHANGELOG entry naming
  the version and the last release that supported it), and that a drop ships in a minor or
  major release and never a patch (FR-016). CHANGELOG.
- Tests, `TestDropped`: the repository has no disagreement; `django_series_from("5.2", "7.0")`
  is 5.2, 6.0, 6.1, 6.2, 7.0; a window whose Django starts at 6.0 with `first` 5.2 and nothing
  dropped names 5.2; the same window with 5.2 dropped at a release the changelog records has no
  disagreement; a version both named and dropped names it; a dropped version whose last release
  the changelog does not record names it; a daisyUI minimum of 5.2 with `first` 5.0 names 5.0
  and 5.1; a django-crispy-forms window of 2.9 alone with `first` 2.7 names 2.7 and 2.8.
- Tests, `TestMetadata` gains: a dropped Django version that the metadata's minimum still
  admits names it. `TestReadme` gains: a dropped version missing from the README's table names
  it, one in the table that the declaration does not drop names it, and a different last
  release names it.

---

## US4 — The maintainer learns that the window has fallen behind (P3)

Issue: #111. Delivers FR-019 to FR-021, FR-023, FR-024; SC-006.

### T007 — The `releases` command

**Files**: `support_window.py`, `tests/test_support_window.py`, `README.md`, `AGENTS.md`

Plan, *`releases`*, *`main`*; research R5.

- `SOURCES`, `final_releases`, `Outstanding`, `Window.outstanding`, `Window.report_releases`,
  and `releases` in `main`.
- README, contributing: the command, its three statuses, and that it is run by hand because
  running it on a schedule needs a workflow (#92). AGENTS.md names it.
- Tests, `TestFinalReleases`: a package-index payload gives each final version the date of its
  first file; a pre-release (`6.2a1`, `6.2rc1`) is left out; an npm payload leaves out `5.6.0-beta.0` and the `created` and `modified`
  entries of `time`.
- Tests, `TestOutstanding`: a window naming the newest of each has nothing outstanding; a
  Django 6.2 the window does not name is outstanding with its release date; a django-crispy-forms 2.8 and a daisyUI 5.8 likewise; a django-crispy-forms 3.0
  and a daisyUI 6.0 are each returned with `new_major` set; a newer patch release of a named
  version (Django 6.1.2, daisyUI 5.7.48) is not outstanding.
- Tests, `TestReportReleases`, with a `fetch` function given by the test: nothing outstanding
  returns 0; a missing release returns 1 and a line holds the package and the version; a new
  major version alone returns 0 and a line holds it; a `fetch` that raises `OSError` returns 2;
  a payload that is not the shape expected returns 2; with one source failing and another
  showing a missing release, the status is 2 and the missing release is still printed.
- By hand, recorded in the report with its output: `uv run python support_window.py releases`
  against the real sources.

---

## Convergence

- The decision record of the plan.
- `git diff origin/main -- mvp_forms/` is empty (SC-007).
- The file lists of the wheel and the source distribution built from this branch and from
  `origin/main` are the same (FR-023).
- `uv run python support_window.py test` for each of the three named pairs.

### T008 — The theme stylesheet and the newest class list name one version

**Files**: `tests/test_legibility/test_themes.py`, `README.md`, `docs/adr/0020-…`, `docs/adr/0032-…`

Added when the legibility check arrived on main beside this feature. It reads daisyUI's themes
from `tests/data/daisyui-themes.css` and has a test that this file and the class list name the
same daisyUI version. That test now reads the class list of the newest version the window names,
found through the declaration, so the window is the one place the version is chosen. The
contributing text says to replace the theme stylesheet when the newest version changes. Two
decision records that named the old class list name the lists under `tests/data/`.
