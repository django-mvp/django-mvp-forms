# Tasks — 020 Characters left under a text field

**Branch**: `020-characters-left` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I: the tests are written and seen to
fail for the right reason, then the code is written. A task is done when its tests pass, the tree
is green and the work is committed. Documentation lands in the task that introduces what it
describes.

No test asserts wording, a colour, a width or a class used only for looks. A widget test asserts
the attributes written, the error raised for each refused option and the media. A browser test
asserts what the script does to the page and to the field's value.

Code standards for every task: no leading-underscore names, methods, helpers, templates or
constants; line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. The pack's templates are plain Django templates, not
Cotton. `CONSTITUTION.md` and everything under `.github/` do not change. A document reads as
current state. README links are absolute. Every `ValueError` names the option at fault.

## Order

**US1 → US2, sequential, in the feature worktree.**

---

## Phase 1: User Story 1 — A developer shows how many characters are left under a field (P1)

Issue: #253. Delivers FR-001 to FR-003, FR-005, FR-006, FR-009 (the field's half), FR-010, FR-012, FR-013, FR-019 to FR-021, FR-023; SC-001, SC-003, SC-006.

- [ ] T001 [US1] The mixin, the two widgets and their words

**Files**: `tests/test_widgets.py`, `mvp_forms/widgets.py`,
`mvp_forms/locale/en/LC_MESSAGES/django.po`

Plan, *The mixin and the widgets*, *Translations*.

- `CharactersLeftInput` and `CharactersLeftTextarea` on the mixin `CharactersLeft`, with
  `CHARACTERS_LEFT_FROM = 8`. Attributes `data-characters-left-from`, `-words` and `-over`, as the
  plan fixes them. Media names `mvp_forms/characters-left.js` once per widget that has it.
- Refusals at construction: `show_from` that is not a whole number, a `bool`, zero or negative;
  a `maxlength` in `attrs`. At render: no `maxlength` raises `ValueError` naming the field.
- The words table has one entry for each count from 0 to the smaller of the number and the limit,
  and follows `ngettext` under a language with more than two plural forms.
- `CharactersLeftTextarea.value_from_datadict` turns `\r\n` and `\r` into `\n`. A form test:
  `max_length=5`, text `ab\r\ncd` is valid and cleans to `ab\ncd`; six characters are refused
  with `max_length`.
- The script file may be an empty placeholder here; T003 writes it. A test of the media asserts
  the path only.

- [ ] T002 [US1] Through every renderer, and the developer's documentation

**Files**: `tests/test_pack/test_characters_left.py` (new), `README.md`, `CONTEXT.md`,
`CHANGELOG.md`

Plan, *The tests*, *Documentation and the demo*.

- The same attributes are drawn by `{{ form|crispy }}`, `{% crispy form %}`,
  `{{ form.field|as_crispy_field }}` and `{{ form.as_div }}`. A form with none of the widgets
  names no script in its media. A field without the widget is drawn with the markup it had before.
  A subclass of either widget carries the attributes of its parent.
- README section "Characters left"; the public surface gains `CharactersLeftInput`,
  `CharactersLeftTextarea`, `CharactersLeft` and `CHARACTERS_LEFT_FROM`. CHANGELOG entry under
  `[Unreleased]`. `CONTEXT.md` gains the two terms. Run the repo's tests that check the README's
  public surface and its examples.

---

## Phase 2: User Story 2 — A person sees how many characters are left as they type (P1)

Issue: #254. Delivers FR-004, FR-007, FR-008, FR-009 (the browser's half), FR-011, FR-014, FR-015, FR-017, FR-018, FR-022; SC-002, SC-004, SC-005.

- [ ] T003 [US2] The script

**Files**: `tests/test_characters_left_e2e.py` (new), `mvp_forms/static/mvp_forms/characters-left.js`,
`pyproject.toml` (the e2e file list), `tests/urls.py` and a test page as the other e2e modules have

Plan, *The script*, *The tests*.

- Write the browser tests first for each scenario of the spec's US-2 and watch them fail with
  the placeholder script, then write the script until they pass. Look at `tests/test_imask_e2e.py`
  and `tests/test_partial_date_e2e.py` for the page, the fixtures and how Chrome is found.
- Also: a `Join` of two marked members each keep their own line; an emoji typed to the limit says none left. Watch items: create the status region before the first write, clear it when the line hides, write words with `textContent` only.
- Behaviour to build, from the plan: marker, count in UTF-16 code units as the browser does, line placement after the
  outermost `.join` or `label` ancestor, the visible line and the status region, the three
  announcement moments, the document listeners, the observer, one line per input, nothing cut.

- [ ] T004 [US2] The demo page

**Files**: `demo/docs/custom-widgets/characters-left.md`, `demo/examples/custom_widgets/` (one
file per example), `demo/examples/urls.py`, the Custom widgets contents list,
`tests/test_demo.py` only if the existing test needs to know the page

Plan, *Documentation and the demo*. Follow `AGENTS.md`, "Adding a page". Examples: a text input,
a textarea, a formset whose rows can be added by a small script of the demo's own (look at how
other formset examples add rows), and a field drawn with initial data over its limit. Build the
pages with `uv run python manage.py build_docs` and run `tests/test_demo.py`.
