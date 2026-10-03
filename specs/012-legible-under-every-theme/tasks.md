# Tasks — 012 Forms stay legible under every daisyUI theme

**Branch**: `012-legible-under-every-theme` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, the order of classes or where a label sits. Elements are
found by id, by name, by type and by role. A class is asserted only where it is the daisyUI
class this feature writes. A pairing is asserted by its part, its ink, its surface and whether it
is held, never by a ratio written into the test, except for the fixed vectors that hold the
colour maths itself.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, module-level names); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates and django-cotton never appears in anything under `mvp_forms/`;
`{% include %}` is fine inside the pack. Cotton components are for the demo project's shell page
only, never `{% include %}` partials there. Every class the pack writes is a daisyUI class,
written out as a literal string. Nothing under `mvp_forms/` imports from django-mvp. `.github/`
is never touched. `pyproject.toml` gains no dependency.

A test written before this feature is changed only where it asserts a class this feature
repairs, and only by that class name. Each such edit is listed in the report.

## Decision records

The records named in the plan are written at convergence, after the last story, with numbers read
from `origin/main` at that moment. No task writes them.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A person can read the form whatever theme the host project chose (P1)

Issue: #99. Delivers FR-001 to FR-007, FR-010, FR-011, FR-017, FR-018, FR-019, FR-024; SC-001,
SC-002, SC-003, SC-006.

### T001 — The themes and the colour maths

**Files**: `tests/data/daisyui-themes.css` (new), `tests/data/daisyui-classes.txt` (header only),
`tests/legibility/__init__.py`, `tests/legibility/colours.py`, `tests/legibility/themes.py`,
`tests/test_legibility/__init__.py`, `tests/test_legibility/test_colours.py`,
`tests/test_legibility/test_themes.py` (all new), `pyproject.toml` only if `forge conformance`
asks for `tests/test_legibility/` to be declared

Plan, *`Colour`*, *`Theme`, `Themes`*; research R2, R4.

- `tests/data/daisyui-themes.css` is
  `https://cdn.jsdelivr.net/npm/daisyui@5.7.47/themes.css`, byte for byte. The header of
  `daisyui-classes.txt` says to refresh both files together.
- `Colour` and `Themes` as the plan describes them.
- Tests, `TestColour`: black on white is 21 and a colour on itself is 1; for `light`, `retro`,
  `dark` and `cupcake` the sRGB values and the four ratios in research R4 are reproduced, sRGB
  to within one step and ratios to two places; a faded colour composited on a surface gives the
  listed value; `parse` refuses text that is not `oklch(...)`.
- Tests, `TestThemes`: 35 themes; each has a scheme and all twenty colours; a rule without a
  `[data-theme=...]` selector is not read as a theme; the version in the banner equals the
  version in the header of `daisyui-classes.txt` (FR-015); a theme added to a copy of the text
  is returned by `Themes.read` (US2 scenario 5).

### T002 — Reading what the pack drew

**Files**: `tests/legibility/pairings.py`, `tests/legibility/reader.py`,
`tests/legibility/catalogue.py`, `tests/test_legibility/test_pairings.py`,
`tests/test_legibility/test_reader.py`, `tests/test_legibility/test_catalogue.py` (all new)

Plan, *`Ink`, `Pairing`, `Measurement`*, *`Reader`*, *`Catalogue`*; research R3, R5.

- `Ink`, `Pairing`, `Measurement`, `Reader`, `Uncovered` and `Catalogue` as the plan describes
  them. `Reader.paints` holds every row of the table in research R3.
- Tests, `TestInk` and `TestPairing`: an ink resolves to the theme's colour; a faded ink and a
  mixed ink resolve to the values in research R4 under `light`; two inks built the same way are
  equal; a pairing's name is the same for the same part, ink and surface; the figure is 4.5 for
  text and 3.0 for a border or a mark.
- Tests, `TestReader`, one per rule in the plan, each drawing a small fragment: text with no
  class is `base-content` on `base-100`; `label` is 60%; `label text-base-content` is
  `base-content`; `text-error` is `error`; a table header is 60% and one with
  `text-base-content` is not; text in a `bg-base-200` group is on `base-200`; text in a
  `modal-box` is on `base-100`; the pack's error alert gives `error` on its tinted fill, and
  `base-content` when it carries `text-base-content`; an alert with a developer's colour yields
  nothing; an input yields a border, its value and, with a placeholder, the placeholder; a
  colour modifier and the error modifier set the border; a ghost input yields no border; a
  select yields its arrow; a file input yields its button's text; a checkbox, a radio and a
  toggle are each read off and on, with and without a colour; a button is read for no colour,
  a colour, and each variant, with `btn-neutral btn-soft` as research R3 gives it; a tab is read
  chosen and not chosen with its bar; an accordion group yields its arrow; a disabled input, a
  disabled checkbox and a disabled toggle yield dimmed pairings that are not held; a read-only
  input is read as an ordinary one; a hidden input yields nothing; a class in `supplied` is
  passed over; a daisyUI class the reader has no row for raises `Uncovered` with the class and
  the form state. `own` is true for text coloured by `label`, `text-error`, a table header, a
  tab and the pack's alert, and false for a border, a placeholder and a button's text.
- Tests, `TestCatalogue`: every id in `STATES` is a state; every class in `Modifiers.tables`,
  `FieldInput.components` and `FieldInput.error_modifiers` is written by at least one state;
  reading every state raises nothing.

### T003 — The check, the repairs and the published list

**Files**: `tests/legibility/exceptions.py`, `tests/legibility/__main__.py`,
`tests/test_legibility/test_exceptions.py`, `tests/test_pack/test_legibility.py` (all new),
`tests/test_pack/test_independence.py`, the pack templates named in the plan's *The repairs*,
the tests that assert a repaired class, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `AGENTS.md`

Plan, *`KnownExceptions`*, *The report*, *The check*, *The repairs*, *The published list*;
research R6, R7.

- `KnownExceptions` and the report command.
- Tests, `TestKnownExceptions`: `found` gives the pairing and themes of a measurement that falls
  short and nothing for one that is not held; `published` reads back what `table` wrote;
  `unlisted` and `stale` give the two differences.
- Tests, `tests/test_pack/test_legibility.py`: `TestEveryTheme`, `TestPublishedExceptions` and
  `TestRepairs` as the plan describes them. Write them first and see them fail on the pack as it
  stands: `TestRepairs` names each piece of text the pack colours that falls short.
- Make the repairs in the plan's table until `TestRepairs` passes. Update the class named in any
  earlier test that asserted `text-error` or a bare `label` on a repaired element, and nothing
  else in it.
- Verification, reported and not committed: render every entry of `STATES` at the base commit
  and after this task, strip every `class` attribute from both, and compare. They are identical
  (FR-010, SC-006).
- `TestDistributedFiles` gains: no pack template or module names a theme, `data-theme` or
  `theme-controller` (FR-011).
- README: the *Themes* section in the public surface, with the table between its two markers
  pasted from `uv run python -m tests.legibility`. CHANGELOG, under Changed: each class the pack
  now writes differently, by what it is on. CONTEXT: **Form state**, **Shipped theme**,
  **Pairing**, **Standard** and **Known exception**, in the spec's words. AGENTS.md: the report
  command, beside the test commands.

---

## US2 — A change that makes a form hard to read is caught before it merges (P2)

Issue: #100. Delivers FR-008, FR-009, FR-012 to FR-016; SC-004, SC-007.

### T004 — The check catches what it must and covers what the pack draws

**Files**: `tests/test_pack/test_legibility.py`, `tests/legibility/reader.py`,
`tests/legibility/exceptions.py`, `tests/legibility/__main__.py`, `README.md`

Plan, *The check*.

- Tests, `TestTheCheckCatches`, one per acceptance scenario of US2: the pack as delivered passes
  under every theme (1); a fragment of the pack's own markup with `text-base-content` taken off
  a help text falls short under at least one theme, and the failure's text carries the form
  state, the theme's name and the pairing's name (2); a published list holding an entry that now
  passes is reported stale (3); a shortfall not in the published list is reported unlisted (4);
  a theme added to a copy of the pinned text is checked and its shortfalls are found (5); a
  class the reader has no row for raises `Uncovered` (6).
- Tests, `TestCoverage`: every daisyUI class written as a literal in a pack template, read from
  the template sources, is in `Reader.paints` or `Reader.silent`; every theme in
  `Themes.shipped()` is a parameter of `TestEveryTheme`; every disabled control in the catalogue
  yields dimmed pairings, none held, and each has a ratio under every theme (FR-004).
- These hold on arrival where T001 to T003 are right, so each is proven by a probe: break what
  it guards, see it fail, restore it. Report the probes. Anything a probe shows missing is fixed
  here.
- The report lists the disabled controls' dimmed pairings per theme, and `--theme` prints every
  measurement under one theme.
- README, in *Themes*: how a contributor runs the report and what to do when the check fails.
- FR-013 and SC-007: nothing under `.github/` changes. Say so in the report.

---

## US3 — A developer can see the forms under any theme and knows what is promised (P3)

Issue: #101. Delivers FR-020 to FR-024; SC-005.

### T005 — The demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`,
`demo/settings.py` if the icon needs it, `demo/templates/demo/themes.html` (new),
`demo/templates/demo/themes_standalone.html` (new), `tests/test_demo.py`

Plan, *The demo project*; research R2, R9.

- The page in the shell and standalone, with the sidebar entry and its icon. The chooser is one
  `theme-controller` radio per shipped theme, named from a list in `demo/forms.py`. Each page
  loads daisyUI's `themes.css` for the pinned version.
- The page shows every form state the check covers: the forms the demo has, unbound and bound
  with errors, the container layout objects, both formset layouts with their errors, disabled
  and read-only fields, each drawing off and on, and every colour, variant and size on every
  kind of input and button.
- Tests, a `ThemesPageContract` with a class for each form of the page: it answers; the shell
  page is in the sidebar; there is one chooser entry per theme in `Themes.shipped()` and no
  other; the list in `demo/forms.py` equals the names in the pinned file; the pairings `Reader`
  reads from the page include every pairing in the catalogue; the standalone page loads no
  stylesheet of django-mvp's and draws no Cotton component; each page links daisyUI's themes
  stylesheet at the pinned version.

### T006 — What is promised, in the README

**Files**: `README.md`, `CHANGELOG.md`, `tests/test_pack/test_legibility.py`

- README, *Themes*: what the pack promises under a theme, the standard and its figures, that the
  35 themes of the pinned daisyUI version are covered, what a host project with a theme of its
  own should know, that a disabled control's own content is measured and not held, and where the
  demo page is. The table is already there from T003.
- Test, in `TestPublishedExceptions`: every theme the README's table names is a shipped theme,
  and the section names the pinned daisyUI version the themes file carries.
- CHANGELOG, under Added: the check, the demo page and the README section.
