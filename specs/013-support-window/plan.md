# Implementation Plan: a stated support window

**Branch**: `013-support-window` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

The window is declared once, in `support-window.toml` at the repository root. One module beside
it, `support_window.py`, reads the declaration and compares it with the README, the package
metadata, the lockfile, the changelog and the daisyUI class lists. The suite runs those
comparisons on every run. The same module is the two commands a contributor and a maintainer run:

```bash
uv run python support_window.py test 5.2 2.7   # the whole suite on one named pair
uv run python support_window.py releases       # is a release missing from the window?
```

The README gains one section, "Supported versions", which holds the statement. No file under
`mvp_forms/` changes, so every form is drawn as before and nothing new is distributed.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: none added. `support_window.py` uses the standard library only
(`tomllib`, `json`, `re`, `urllib.request`, `subprocess`, `importlib.metadata`, `argparse`,
`datetime`).

**Storage**: none

**Testing**: pytest, in `tests/test_support_window.py`. The network is never used: the functions
that decide anything take the data as an argument, and the one that fetches is replaced by a
function given in the test.

**Project Type**: Django package (a template pack)

**Constraints**: nothing under `.github/`; nothing under `mvp_forms/`; no leading-underscore
names; line length 88; no compatibility aliases; no test of wording.

**Scale/Scope**: one declaration file, one module of about 400 lines, one test module, two class
lists, one README section and three additions to its contributing section.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | every task is test-first. A check is asserted by the package and the version it names, never by its sentence. No wording in the README is asserted: the facts are read from marked tables |
| II Simplicity | one file and one module. No class hierarchy, no plug-in point, no configuration beyond the declaration |
| III Anti-Abstraction | the three packages are read by three short functions, because their numbering really differs. There is no "package" base class |
| IV Integration-First | the checks read the real README, `pyproject.toml`, `uv.lock`, `CHANGELOG.md` and class lists of this repository |
| V Security | R-S1 to R-S3 below |
| VI Documentation | README, CHANGELOG and CONTEXT change in the story that introduces what they describe. README links are absolute |
| VII Dependencies | none added, runtime or development |
| VIII Internationalization | nothing a person using a host project sees is added |
| XI Compatibility | no public API changes. Dropping a version is not a removal under this article (decisions D5), and the record of that decision is written at convergence |
| XII Scope, XIII Plain templates, XIV Stock daisyUI | no template, class or import is added to the package |

## The declaration: `support-window.toml`

```toml
# The support window: the versions of Django, django-crispy-forms and daisyUI this
# package states it works with. The README, the package metadata and the test
# suite are checked against this file. To change it, follow "Changing the support
# window" in the README.

# Days from a final release within which the package supports it.
period-days = 30

# The Python versions the suite runs on.
python = ["3.12", "3.13"]

[django]
# The oldest release series any release of this package supported.
first = "5.2"
versions = ["5.2", "6.0", "6.1"]

[django-crispy-forms]
first = "2.7"
versions = ["2.7"]

# The Django release series each named release supports.
[django-crispy-forms.pairs]
"2.7" = ["5.2", "6.0", "6.1"]

[daisyui]
first = "5.0"
minimum = "5.0"
newest = "5.7"

# One table for each version that has left the window:
#
# [[dropped]]
# package = "django"
# version = "5.2"
# last-release = "1.4.0"
```

`first` is what makes "a version that appears in neither the window nor the list of dropped
versions" something a check can decide (US-3, scenario 5): every version from `first` to the
newest named is either in the window or in `dropped`, and never both.

## `support_window.py`

One module at the repository root. Every name is public. Full Google-style docstrings, as
`docs/contributing/standards/code-documentation.md` asks.

### Reading the declaration

- `InvalidWindow(ValueError)`, carrying `package` and `version`: raised when the declaration
  cannot be read as a window.
- `Dropped`: a frozen dataclass of `package`, `version`, `last_release`.
- `Window`: a frozen dataclass of `period_days`, `python`, `django`, `django_first`,
  `crispy_forms`, `crispy_forms_first`, `pairs`, `daisyui_first`, `daisyui_minimum`,
  `daisyui_newest`, `dropped`. `Window.read(path)` reads the file; `Window.from_mapping(data)`
  builds one from a parsed mapping, which is what the tests of a changed window use.
  - A Django or django-crispy-forms version must be two numbers, `5.2` or `2.7`. A daisyUI
    version must be two numbers. Anything else, such as `5.2.17`, raises `InvalidWindow` naming
    the package and the version (the edge case of a version written at another level of detail).
  - Every key of `pairs` is a named django-crispy-forms release, and every Django it lists is a
    named Django series; otherwise `InvalidWindow`.
  - `Window.daisyui` returns the two versions the suite checks, minimum then newest (one when
    they are the same).
- `ROOT`, the repository root, and `DECLARATION`, the path of `support-window.toml`.

### Comparing

- `Disagreement`: a frozen dataclass of `source` (`"README"`, `"metadata"`, `"lockfile"`,
  `"dropped"`, `"changelog"`, `"installed"`), `package`, `version` and `problem`. A test asserts
  the first three. `problem` is a sentence for the person reading the failure.
- `metadata_disagreements(window, pyproject)`, given the parsed `pyproject.toml`:
  - the Django and django-crispy-forms requirements are `>=` the oldest named version and
    nothing else: an upper limit, a pin or a different minimum is a disagreement naming the
    version found;
  - the `Framework :: Django :: X.Y` classifiers are exactly the named Django series, and the
    `Programming Language :: Python :: 3.N` classifiers exactly the declared Python versions,
    each difference naming its version;
  - every dropped Django or django-crispy-forms version is below the required minimum (FR-017).
- `readme_disagreements(window, readme)`, given the README's text. It reads the block between
  `<!-- support-window -->` and `<!-- /support-window -->`:
  - the row whose first cell holds `Django`, `django-crispy-forms`, `daisyUI` or `Python`, and
    the versions in its second cell, compared with the declaration. For daisyUI the two versions
    are the minimum and the newest;
  - the rows of the pairs table, compared with `pairs`;
  - the period, written in digits, compared with `period_days`;
  - and the block between `<!-- dropped-versions -->` and `<!-- /dropped-versions -->`, whose
    rows are compared with `dropped`: package, version and last release.
  A version in one and not the other is a disagreement naming it. A block that is missing is a
  disagreement.
- `relative_links(readme)`: the link targets from the first comment of the section to the last
  that are not absolute. The suite asserts there are none (US-1, scenario 4).
- `dropped_disagreements(window, changelog)`:
  - a version both named and dropped;
  - a version from `first` up to the newest named that is neither. `django_series_from(first,
    newest)` walks `A.0`, `A.1`, `A.2`, `(A+1).0`; django-crispy-forms and daisyUI count the
    second number up. For daisyUI the versions below `minimum` are the ones that must be dropped;
  - a dropped version whose `last_release` is not a release heading in the changelog
    (`## [v0.1.0]`, with or without the `v`).
- `lockfile_disagreements(window, lock)`, given the parsed `uv.lock`: the locked Django series
  and django-crispy-forms release are named ones (FR-010).
- `installed_versions()`: Django and django-crispy-forms as `importlib.metadata` reports them.
  `installed_disagreements(window, installed, asked)`: the installed versions are named ones,
  and where `asked` names a version, the installed one is that version (FR-012, US-2 scenarios 6
  and 7).
- `class_list(version)`: the set of class names in `tests/data/daisyui-classes-<version>.txt`.
  A version with no file raises `MissingClassList`, a `LookupError` carrying `version` (FR-011).

### `test`: the suite on one named pair

`run_suite(window, django, crispy_forms, extra, run=subprocess.run)`:

1. A pair the declaration does not offer returns a failing status and runs nothing: either
   version is not named, or `pairs` does not hold the pair.
2. Otherwise it runs
   `uv run --isolated --with django==<django>.* --with django-crispy-forms==<crispy>.* pytest
   <extra>` with `SUPPORT_WINDOW_DJANGO` and `SUPPORT_WINDOW_CRISPY_FORMS` set in the
   environment, and returns its status. `extra` defaults to `-n auto --dist loadscope`.

`tests/conftest.py` gains two hooks, each one line over the module:

- `pytest_report_header` returns the installed versions, so every run says what it ran on;
- `pytest_sessionstart` raises `pytest.UsageError` when `installed_disagreements`, with the two
  environment variables as `asked`, names a version that was asked for and is not the one
  installed. A run asked for Django 5.2 that finds 6.1 stops before a test runs and reports no
  result. An installed version outside the window with nothing asked for is left to the test
  that checks it, so the run still reports which check failed.

### `releases`: a release the window does not name

- `final_releases(payload, source)`: version to date of its first publication, for a payload of
  the package index or of the npm registry. Pre-releases are left out, and a release of the
  package index whose every file is yanked.
- `Outstanding`: a frozen dataclass of `package`, `version`, `released` and `due` (`released`
  plus the period), and `new_major`, true for a new major version of django-crispy-forms or
  daisyUI.
- `outstanding(window, django, crispy_forms, daisyui)`, given the three mappings of
  `final_releases`:
  - Django: every release series newer than the newest named;
  - django-crispy-forms: every feature release of the current major series newer than the newest
    named, and the first release of each later major series with `new_major` set;
  - daisyUI: every minor release of the current major version newer than `newest`, and each
    later major version with `new_major` set.
- `report_releases(window, fetch=fetch_json, out=print)`: fetches the three, prints one line for
  each outstanding release and one for each new major version, and returns the status:
  - `0` nothing outstanding;
  - `1` at least one release under the period is missing. A new major version alone is `0`;
  - `2` a source could not be reached or its answer could not be read. The line names the
    package, and nothing says the window is current.
- `fetch_json(url)`: `urllib.request.urlopen` with a timeout, for the three addresses in
  `SOURCES` only.

### `classes`: a class list for a daisyUI version

- `class_names(stylesheet)`: every class selector of a stylesheet, with CSS escapes undone.
- `write_class_list(version, fetch=fetch_text, registry=fetch_json)`: finds the newest patch
  release of the minor version in the npm registry, downloads
  `https://cdn.jsdelivr.net/npm/daisyui@<patch>/daisyui.css`, and writes
  `tests/data/daisyui-classes-<version>.txt` with a header naming the patch release and the
  address. The version must be two numbers, so it cannot name another path.

### `main(argv)`

`argparse` with three subcommands, `test`, `releases` and `classes`. `python support_window.py`
ends with `sys.exit(main())`.

## Security

- **R-S1.** The module fetches three fixed HTTPS addresses and one address built from a daisyUI
  version. The version is matched against two or three numbers before it is put in an address or
  a file name. Nothing a person types reaches a shell: `subprocess.run` takes a list.
- **R-S2.** What comes back from the network is read as JSON or as a stylesheet and is never
  executed or written anywhere but the one class list.
- **R-S3.** None of this is distributed, so a host project never runs it.

## The class lists

`tests/data/daisyui-classes.txt` is replaced by `tests/data/daisyui-classes-5.0.txt` (from
5.0.55) and `tests/data/daisyui-classes-5.7.txt` (from 5.7.47), both written by
`python support_window.py classes`.

The `daisyui_classes` fixture in `tests/conftest.py` is given one parameter for each version
`Window.daisyui` returns, so every test that uses it runs once for each named version and its id
names the version. No test that uses the fixture changes. A failure shows the missing class in
its assertion and the version in its id.

## The README

A new section, `## Supported versions`, after "Installation". Between the first pair of comments:

| | Supported |
|---|---|
| Django | 5.2, 6.0, 6.1 |
| django-crispy-forms | 2.7 |
| daisyUI | 5.0 to 5.7 |
| Python | 3.12, 3.13 |

then the pairs table, one row for each django-crispy-forms release, and the period in digits.
Around them, prose a reader judges and no test reads: that the newest patch release of each is
meant (FR-002); which kinds of release the period covers, and what the statement says when one
cannot be supported in time (FR-006); that a new major version of django-crispy-forms or daisyUI
has no period (FR-007); that daisyUI is checked at the two ends of its range (FR-005); what a
host page loading `daisyui@5` from the CDN can expect between a daisyUI release and its naming;
that a newer Django or django-crispy-forms installs and is simply not vouched for (FR-008); that
Python versions carry no period; the rule by which each leaves (FR-015); that a drop ships in a
minor or major release (FR-016); and that a release before the last one that supported a dropped
version gets no fixes (FR-018). Then the second pair of comments, holding the table of dropped
versions, which is empty today, with a sentence saying none has left.

The contributing section gains "Changing the support window": adding a version, taking one out,
the `test` command, the `releases` command and the `classes` command. Every link is absolute.

## Story order

**US1 → US2 → US3 → US4, sequential, in the feature worktree.** Each later story adds to
`support_window.py`, `tests/test_support_window.py` and the README, so they cannot be built side
by side.

| Story | Adds |
|---|---|
| US1 | the declaration, `Window`, `InvalidWindow`, `Disagreement`, `metadata_disagreements`, `relative_links`, the README section, CONTEXT terms, CHANGELOG |
| US2 | `readme_disagreements` for the statement, `lockfile_disagreements`, `installed_versions`, `installed_disagreements`, `class_list`, `class_names`, `write_class_list`, the two class lists, the fixture, `run_suite`, the two hooks, `main`, the contributing text |
| US3 | `Dropped`, `dropped_disagreements`, the dropped part of `metadata_disagreements` and `readme_disagreements`, the contributing text on taking a version out |
| US4 | `final_releases`, `Outstanding`, `outstanding`, `report_releases`, `fetch_json`, the contributing text |

## Decision records

Written at convergence, numbered from `origin/main` at that moment:

- **The support window: what is in it, how a version enters and how one leaves** (decisions D2, D4
  and D5). It says a drop is not a removal under Article XI.

Where the declaration lives (D7) earns no record: a file at the repository root named for what it
holds is where a reader looks.

## What this plan does not do

- It changes nothing under `.github/`. The workflow reading its versions from the declaration,
  and the `releases` command on a schedule, are #92.
- It adds no demo page (FR-024).
- It does not check a daisyUI release between the minimum and the newest (decisions D3).
