# Tasks — 009 Replace one template without forking the pack

**Branch**: `009-replace-one-template` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a public name lands in the task
that introduces it.

No test asserts wording, width, spacing, the order of classes or where a label sits. Elements are
found by id, by name, by type, by role, or by an attribute a test's own replacement writes. A
warning is asserted by its category and by the paths it names, never by its sentence.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates, fixtures, module-level names); line length 88; no compatibility aliases; docstrings
per `docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates
are plain Django templates and django-cotton never appears in anything under `mvp_forms/`.
Nothing under `mvp_forms/` imports from django-mvp. `.github/` is never touched. No pack
template is changed by this feature. Documents read as current state: no dated notes, no
"amended", no strikethrough.

## Decision records

The record named in the plan is written at convergence, after the last story, with its number
read from `origin/main` at that moment. No task writes it.

## Order

**US1 → US2 → US3, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — A developer replaces one template and keeps the rest (P1)

Issue: #102. Delivers FR-001 to FR-008, FR-017, FR-018; SC-001, SC-002, SC-007.

### T001 — Every template can be replaced, and is handed what the pack's own is

**Files**: `tests/conftest.py`, `tests/test_pack/test_replacements.py` (new),
`tests/test_pack/test_independence.py` (states added only)

Plan, *The test fixtures*, *The first story's tests*, *Tests that pass on arrival*; research R1,
R3, R6.

- The `replace` and `pack_source` fixtures. `clear_crispy_template_caches` also clears
  `crispy_forms_tags.whole_uni_formset_template`, which it missed.
- `TestEveryTemplate`: parametrised over every distributed template. A copy with a marker draws
  every entry of `STATES` the same as the pack once the marker is taken out, and the marker is
  drawn in at least one state. `layout/tab-link.html` is left out of the second half.
- A state added to `STATES` for any template no state reaches.
- Probes, reported and not committed: the test fails when a replacement drops a name the
  original reads, and when a draw site stops going through the path.

### T002 — The acceptance scenarios and where a replacement has to be

**Files**: `tests/host_app/__init__.py` (new),
`tests/host_app/templates/daisyui/widgets/select_date.html` (new),
`tests/test_pack/test_replacements.py`, `tests/forms.py` if a form is missing

Plan, *The first story's tests*; research R1, R3.

- `TestReplacingOneTemplate`, one test per scenario 1, 2, 3, 4, 5, 7 and 9 of US1.
- `TestWhereAReplacementIsFound`: the placement and edge cases the plan lists.
- Verification of FR-017, reported and not committed: every state drawn at the base commit and
  at the tip is the same.

---

## US2 — A developer finds which template to replace and what it is given (P2)

Issue: #103. Delivers FR-007, FR-009, FR-010, FR-011, FR-019; SC-003, SC-004.

### T003 — The list, and the check that keeps it true

**Files**: `tests/template_surface.py` (new), `tests/test_template_surface.py` (new),
`tests/test_pack/test_template_list.py` (new), `README.md`

Plan, *The list*, *The check*; research R2, R5.

- `tests/template_surface.py`: the class `TemplateSurface` with `distributed`, `names_read`,
  `renderer_route`, `listed` and `disagreements`.
- `tests/test_template_surface.py`, `TestNamesRead`: one test per rule of research R5, on
  templates written in the test, `{% csrf_token %}` among them. `TestDisagreements`: each kind
  of disagreement is reported, with a made-up README and a made-up directory.
- `tests/test_pack/test_template_list.py`, `TestTheListMatchesThePackage`: no disagreements
  between the README and the package; every row says what its template draws.
- README: `### Replacing one template` with what a replacement is, where to put it for each
  route, the note on the templates django-crispy-forms keeps in memory, and the table. The
  sentence about the form renderer in *Template pack `daisyui`* points at it.

### T004 — The worked example, the CHANGELOG and the glossary

**Files**: `README.md`, `tests/test_pack/test_documented_examples.py`, `CHANGELOG.md`,
`CONTEXT.md`

Plan, *The worked example*, *The README, the CHANGELOG and the glossary*.

- README: the worked example under a `#### ` heading inside the section.
- `readme_template`, a reader beside `readme_example` that returns the `django` block under a
  `#### ` heading and runs nothing.
- `TestReadmeReplacement`: the example as written, put in place with `replace`, draws its marker
  on a required field and not on an optional one, and the pack's marker is not drawn.
- CHANGELOG, under Added: replacing one template, the list, and that the paths and the names
  handed are public from this release.
- `CONTEXT.md`: **Replacement** and **Template list**.

---

## US3 — An upgrade does not quietly break a replacement (P3)

Issue: #104. Delivers FR-012 to FR-016, FR-019; SC-005, SC-006.

### T005 — A replacement at a path the pack has moved away from is honoured and warned about

**Files**: `mvp_forms/deprecation.py` (new), `mvp_forms/templatetags/daisyui.py`,
`tests/test_deprecation.py` (new), `tests/test_templatetags/test_daisyui.py`,
`tests/host_app/templates/` (templates for the renderer case)

Plan, *Changing a listed template later*; research R7.

- `WITHDRAWN` and `host_template`, which returns the path to draw.
- The tag `daisyui_host_template`.
- `tests/test_deprecation.py` and `TestHostTemplate`, as the plan lists them. A row is put into
  `WITHDRAWN` with `monkeypatch.setitem`, so the registry is empty again after each test. The
  renderer case runs under the default renderer with `tests.host_app` listed before
  `mvp_forms`.

### T006 — The list carries a path on its way out, and the documents say what is promised

**Files**: `tests/template_surface.py`, `tests/test_template_surface.py`, `README.md`,
`CHANGELOG.md`

Plan, *Changing a listed template later*, *The README, the CHANGELOG and the glossary*.

- `TemplateSurface.disagreements` reads the withdrawn paths: one that the table does not list is
  reported, and a listed one is not reported as listed but not distributed.
- `TestDisagreements` gains those two cases. The real check passes with `WITHDRAWN` empty.
- README: the last part of the section. A listed path and the names it is handed change only
  through one minor version in which the old one still works; a replacement at an old path is
  still drawn for that version and raises a `DeprecationWarning` naming what replaces it, which
  a test runner or `python -W default` shows, as they do Django's; an old name keeps its value
  for that version; the CHANGELOG says what replaces each; a path on its way out stays in the
  table with what replaces it; the markup and the classes inside a pack template are not part
  of the promise.
- CHANGELOG: the entry from T004 gains what happens when a listed template changes.
