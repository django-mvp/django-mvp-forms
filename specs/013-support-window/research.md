# Research: a stated support window

Done on 2026-10-04 against `origin/main` at `2f761f4`, after FS-001 to FS-010 merged and v0.1.0 was
released. FS-011 and FS-012 are being built at the same time and are not on main. Citations to
Django and django-crispy-forms are to the packages in the project's virtual environment, Django
6.1.1 and django-crispy-forms 2.7 (`uv.lock`). Release histories were read from the package index,
the npm registry and daisyUI's CDN on the same day.

The specification directory has no `planning-notes.md` and the feature has no sketch, so there is
nothing of either to answer.

## R1. What the repository states today, and where

| Where | What it says |
|---|---|
| `pyproject.toml` `dependencies` | `django>=5.2`, `django-crispy-forms>=2.7`, no upper limit |
| `pyproject.toml` `classifiers` | Django 5.2, 6.0, 6.1; Python 3.12, 3.13 |
| `pyproject.toml` `requires-python` | `>=3.12,<4.0` |
| `uv.lock` | Django 6.1.1, django-crispy-forms 2.7 |
| `.github/workflows/tests.yml` | calls `django-mvp/shared` `tests.yml@v0.6.0` with no version inputs |
| the shared workflow's defaults | Python `["3.12", "3.13"]`, Django `["5.2", "6.0", "6.1"]`; each leg runs `uv sync --locked`, then `uv pip install "django~=<series>.0"`, and fails when the installed series is not the one asked for |
| `tests/data/daisyui-classes.txt` | every class selector of daisyUI 5.7.47's CDN stylesheet, 3,493 names |
| `README.md` | "Pages that draw these forms must load daisyUI 5", and nothing about Django or django-crispy-forms versions |
| `AGENTS.md` | "Django 5.2, 6.0 and 6.1" |

The metadata already agrees with the window the specification names, so this feature changes no
line of `pyproject.toml` and none of `uv.lock`.

## R2. The versions that exist

**Django** (package index). Supported by the Django project today: 5.2 (long-term support, first
final release 2025-04-02), 6.0 (2025-12-03) and 6.1 (2026-08-05). 5.1 had its last release on
2025-12-02 and 5.0 on 2025-04-02. A release series is numbered `A.0`, `A.1`, `A.2`, then `(A+1).0`,
and has been since 2.0, so the series after any given one can be computed.

**django-crispy-forms** (package index). The current major series is 2. Its feature releases are
numbered `2.N` with no patch component; the newest is 2.7 (2026-07-29), after 2.6 (2026-03-01) and
2.5 (2025-11-06). The metadata of 2.7 requires `django>=5.2` and advertises Django 5.2, 6.0 and
6.1, so every pair of a named Django and the one named django-crispy-forms release is supported.

**daisyUI** (npm registry). Version 5 has eight minor releases: 5.0 (2025-02-28, newest patch
5.0.55), 5.1 (5.1.32), 5.2 (5.2.5), 5.3 (5.3.11), 5.4 (5.4.8), 5.5 (5.5.23), 5.6 (5.6.22) and 5.7
(2026-07-20, newest patch 5.7.47). The newest release is 5.7.47. Pre-releases carry a hyphen
(`5.6.0-beta.0`).

## R3. The daisyUI minimum is 5.0

The specification leaves the minimum to the build: the oldest daisyUI 5 minor release whose CDN
stylesheet defines every daisyUI class the pack writes.

The classes the pack writes were collected the way `TestEmittedClasses` collects them: every state
in `STATES` of `tests/test_pack/test_independence.py` drawn, the classes a form supplied taken out,
the three tables of `Modifiers` added and the eleven Tailwind layout utilities taken out. That is
177 daisyUI class names. The class selectors of a stylesheet were read with CSS escapes undone
(`.md\:flex-row` is the class `md:flex-row`).

| Stylesheet | Class names | Of the 177 the pack writes, missing |
|---|---|---|
| 5.0.0 | 3,077 | none |
| 5.0.55 | 3,662 | none |
| 5.1.32 | 3,662 | none |
| 5.7.47 | 4,036 | none |

So the minimum is **5.0**, checked at its newest patch release, 5.0.55, and the newest minor
release checked is **5.7**, at 5.7.47. FR-002 says the newest patch release of a named version is
the one meant, which is why the minimum is checked at 5.0.55 and not at 5.0.0.

The list in the repository today was made by a method that is not recorded. It leaves out the
names that carry a responsive prefix (`2xl:alert`) and holds one stray name, `32`, cut from the
escaped selector `.\32 xl\:…`. Reading the selectors with escapes undone gives 4,036 names for
5.7.47: every name the present list holds except `32`, and 543 more. A larger list of names the
stylesheet really defines cannot hide a class it does not define, so both lists are made the same
way by one command kept in the repository, and the method is no longer a comment at the top of a
file.

## R4. Running the suite on another Django and django-crispy-forms

`uv run --isolated --with 'django==5.2.*' --with 'django-crispy-forms==2.7.*' pytest -n auto --dist
loadscope` was run in this worktree: 3,811 tests passed in 40 seconds on Django 5.2.17, and
`uv run python -c "import django; print(django.__version__)"` afterwards still printed 6.1.1.
`--with` installs the named versions in a layer over the project's environment for that one
command, and `--isolated` keeps the layer out of the development environment. Nothing is written
to `.venv` and nothing to `uv.lock`. The workers of pytest-xdist are started from the same
interpreter and ran on the same Django.

This is what the test workflow does by another route (`uv pip install` into the synced
environment), with the difference that the workflow's environment is thrown away and a
contributor's is not.

**Considered and not adopted:** tox and nox. Either would do the job and either is a new
development dependency, where Article VII says development tooling comes from the shared bundle.
`uv` is already the tool every command in `AGENTS.md` runs through.

What `uv run --with` cannot do alone is what FR-012 asks for: report the versions the run used,
fail when they are not the ones asked for, and refuse a pair the statement does not offer. Those
three need a few lines around it (R6).

## R5. Finding out about a new release

| Package | Source | What it gives |
|---|---|---|
| Django | `https://pypi.org/pypi/Django/json` | `releases`: every version with its files, each file with `upload_time_iso_8601` and `yanked` |
| django-crispy-forms | `https://pypi.org/pypi/django-crispy-forms/json` | the same |
| daisyUI | `https://registry.npmjs.org/daisyui` | `versions` and `time`, a date for each version |

All three answer with JSON over HTTPS and need no credentials, so the standard library's
`urllib.request` and `json` are enough. A final release is one whose version is digits and dots
only: the package index writes a pre-release as `6.2a1` or `6.2rc1`, and npm as `5.6.0-beta.0`.

**Considered and not adopted:** the repository's dependency updates. They raise a new Django or
django-crispy-forms release as a pull request against the lockfile, but they cannot see daisyUI,
which is a dependency of nothing here, and they say nothing about the period. Running anything on
a schedule needs a workflow, which this feature may not add (#92).

## R6. Where the declaration and the checks live

Nothing this feature adds may be distributed (FR-023). The wheel is `packages = ["mvp_forms"]` and
the source distribution is `/mvp_forms`, `/README.md` and `/LICENSE`, so anything outside
`mvp_forms/` is already left out and no build setting changes.

- **The declaration** is a file of its own at the repository root, `support-window.toml`. A table
  in `pyproject.toml` was the alternative. It was not taken because `pyproject.toml` is the file
  the release workflow watches, and because a contributor changing the window should have one
  short file to read, not a table two hundred lines into a build file.
- **The code that reads it** is one module at the repository root, `support_window.py`, using the
  standard library only. It is imported by the tests (`pythonpath` already holds the root) and run
  by a contributor as `uv run python support_window.py …`. A module under `tests/` was the
  alternative, as `tests/template_surface.py` is; it was not taken because two of its three jobs
  are commands a maintainer runs, and `python -m tests.…` is not where anyone would look for them.
- **Its tests** are `tests/test_support_window.py`, which mirrors the module under the rule the
  structure check applies to a module at the repository root.

`deptry` scans the repository root. The module imports the standard library only, so it adds
nothing for `deptry` to report. `mypy` checks `mvp_forms` only.

## R7. Reading the README without testing its wording

`tests/template_surface.py` finds the README's template list by its heading and reads the table
under it. A heading is wording, and the testing standard says a test finds an element by a hook
and never by the words around it. The statement is therefore held between two pairs of HTML
comments, `<!-- support-window -->` … `<!-- /support-window -->` and `<!-- dropped-versions -->`
… `<!-- /dropped-versions -->`. A comment is drawn neither on GitHub nor on the package index.

Inside the first pair are the facts a check can decide: one table row for each of Django,
django-crispy-forms, daisyUI and Python, found by the package's name in its first cell; the table
of pairs; and the period as a number. Everything else in the section is prose that only a reader
judges, and no test reads it.

## R8. What cannot be read from this repository

The Python and Django versions the test workflow runs are defaults of a workflow in another
repository. No check here can read them, which is the gap #92 records. The declaration states the
Python versions and the suite checks them against the package metadata, which is the only other
place this repository states them.

## R9. Every form is drawn as before

No file under `mvp_forms/` changes. SC-007 is shown by `git diff origin/main -- mvp_forms/` being
empty, and FR-023 by the file lists of the built wheel and source distribution being the same
before and after.
