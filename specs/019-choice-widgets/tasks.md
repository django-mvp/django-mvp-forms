# Tasks — 019 Choice widgets drawn as a scale, pills, chips or cards

**Branch**: `019-choice-widgets` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I: the tests are written and seen to
fail for the right reason, then the code is written. A task is done when its tests pass, the tree
is green and the work is committed. Documentation lands in the task that introduces what it
describes.

No test asserts wording, a colour, a width or a layout preference. A widget test asserts the
inputs drawn, their names, values, order, accessible names, checked and disabled state, the fold's
presence, openness and count, the media and what the field receives. A browser test asserts what
this package's script does.

Code standards for every task: no leading-underscore names, ever (methods, helpers, templates,
constants); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. `mvp_forms/widgets.py` imports Django and the standard
library only. Templates are plain Django templates, not Cotton. `CONSTITUTION.md` and everything
under `.github/` do not change. A document reads as current state. README links are absolute.

## Order

**US1 groups 1 to 4, then US2 groups 5 and 6, sequential, in the feature worktree.**

---

## User Story 1 — A developer draws a choice field as a scale, pills, chips or cards (P1)

Issue: #256. Delivers FR-001 to FR-015, FR-021 to FR-027, FR-029 to FR-031.

### Group 1 — the widgets, the scale and the pills

- [ ] T001 [US1] The seven widget classes and their settings

**Files**: `tests/test_widgets.py`, `mvp_forms/widgets.py`

Plan, *The widgets*. `ChoiceLayout`, `FoldedChoices` and `CardChoices` mixins and the seven
classes. Settings validated as the plan states. `show` a per-instance attribute (a deep copy of a
form's widgets does not share it). Option context: flattened optgroups in the field's order, the
empty choice taken out of a single-choice widget's order as `clearing` and left in a multiple
widget's, `aria_label` as plain text with a scale's end words on its first and last options,
`description`, `icon`, `meta`, `columns`, `shown`, `folded`, `fold_open`. Tests: settings refused
by name, `show` set on one form's widget leaves another form untouched, a value keyed by a
choice the field does not offer is passed over, a model choice matched by primary key, the context
for a bound and an initial value, `cleaned_data` equal to a radio group's and a checkbox group's for
the same submissions, grouped choices drawn in the field's order with no group name, and a multiple widget drawing an empty-string choice among the others.

- [ ] T002 [US1] The scale and pill templates

**Files**: `tests/test_pack/test_choice_layouts.py`, `mvp_forms/templates/mvp_forms/widgets/scale.html`,
`mvp_forms/templates/mvp_forms/widgets/pills.html`

Plan, *The agreed look*. Templates drawn through Django's own renderer, so a form with no
crispy-forms still draws inputs, labels and the end words. The scale is a `join` of
`input.btn.join-item` with the end words under it. Pills are a wrapping row of `input.btn`
toggles. The clearing choice is drawn after the others. Tests assert the inputs and what each
carries, not the classes used for looks.

### Group 2 — chips and cards

- [ ] T003 [US1] The chip and card templates and the fold

**Files**: `tests/test_pack/test_choice_layouts.py`, `mvp_forms/templates/mvp_forms/widgets/chips.html`,
`mvp_forms/templates/mvp_forms/widgets/cards.html`,
`mvp_forms/templates/mvp_forms/widgets/card_option.html`

Plan, *The widgets* and *The agreed look*. A chip shows its label in full. A card holds an icon
tile, the short line, the label, the description and a mark; a choice given no extras is drawn
with its label alone; an icon marked safe is markup and a description with an angle bracket is
escaped. The fold is a `details` with a `summary` holding the words and the count: open when it
holds every choice and none is chosen, absent when it would hold none, the developer's words when
given. A chosen choice is on show whether or not its value was named. Tests cover every
acceptance scenario of US-1 that concerns chips and cards. The `Media` is added in T008.

### Group 3 — what the pack applies

- [ ] T004 [US1] Size, colour, error state and the frame

**Files**: `tests/test_pack/test_choice_layouts.py`, `tests/forms.py`, `mvp_forms/choices.py`,
`mvp_forms/templatetags/daisyui.py`

Plan, *What the pack applies*. The two components in the modifier tables, `component_of`, the
`widget` branch and `choice_context`, `fixed_size`, no class written on the widget's `attrs`.
Tests: every size and every colour reaches the inputs (and the card's label) of every widget; a
variant stated for the form is passed over and one stated for the field raises `InvalidChoice`
with `kind="variant"`; a drawing stated for the field raises with `kind="drawing"`; a field in
error, a disabled field and a required field are framed as a group with a legend, the help text
and the errors describing it, every input `aria-invalid` and `disabled` as the field is; the same
drawing through `{{ form|crispy }}`, `{% crispy form %}`, `|as_crispy_field`, a stacked and a
table formset, `Row`, `Fieldset`, `Tab`, `AccordionGroup`, `Modal`, `InlineRadios` and
`InlineCheckboxes`; a host project's replacement template is used. Every existing test in the
suite still passes (FR-026), with one edit: `TestModifierTables` in `tests/test_pack/test_independence.py` splits an entry on whitespace and accepts names in `LAYOUT_UTILITIES`, each utility the widgets write being added there. A form holding the seven widgets (with a fold, a clearing choice and one in error) joins `STATES` in that file, so the class test covers FR-003. Assert each template has `summary` inside `details` and no `script` element or `on*` attribute.

### Group 4 — shipping the widgets

- [ ] T005 [US1] README, context, changelog, catalogue and decision record

**Files**: `README.md`, `CONTEXT.md`, `CHANGELOG.md`, `mvp_forms/locale/en/LC_MESSAGES/django.po`,
`docs/adr/NNNN-choice-layouts-are-widgets-the-pack-resolves-into.md`,
`tests/test_pack/test_template_surface.py` (extended only if the list test needs the new names)

FR-029 and FR-031. A "Choice widgets" section in the README's public surface: each widget and
its settings, the fold and what a page without the script does, how a single choice is cleared,
size and colour, which lists each suits (a scale for an ordered set of up to eleven, pills for
short labels, chips and cards for long ones), and what is not supported. Each widget and each
template appears in the surface list and the template list. The paragraph on what the script adds
is written in T008. `CONTEXT.md` terms under Key Entities. CHANGELOG Added entry. The English
catalogue regenerated. One decision record per the plan; its number is the next free on
`origin/main`, checked again after every rebase.

- [ ] T006 [US1] The demo page

**Files**: `demo/examples/custom_widgets/choice_widgets.py`, `demo/docs/custom-widgets/choice-widgets.md`,
`demo/examples/urls.py`, `demo/docs/index.md` (contents), `tests/test_demo.py` as needed

FR-030. A Choice widgets page in the Custom widgets group: a live example of each widget and each
setting (the scale's end words, chips with a fold and a clearing choice, cards in one, two and
three columns with icons, descriptions and the short line, a fold set in the form's `__init__`),
a field in error, a disabled field, and a fold inside a formset whose rows can be added. Icons are
inline SVG written in the demo. The documented examples test passes.

---

## User Story 2 — A person answers a question by tapping a choice (P2)

Issue: #257. Delivers FR-004, FR-007, FR-013, FR-016 to FR-020, FR-028, FR-030.

### Group 5 — the script

- [ ] T007 [US2] The browser tests for tap, tick, clear and keyboard

**Files**: `tests/test_choice_fold_e2e.py`, `tests/templates/tests/choice_page.html`, `tests/urls.py`

Tests first, in headless Chrome, against a page of the test project that holds every widget:
tap and tick, a single choice replaced, a multiple choice unticked, the clearing choice, Tab and
arrow keys and the space bar reach and choose every widget with the focus visible, the accessible
name of each input and the scale's end words on the first and last, a long label wrapping in a
chip. These pass on the markup of US1 and pin it.

- [ ] T008 [US2] The fold script and the widgets' media

**Files**: `tests/test_choice_fold_e2e.py`, `tests/test_pack/test_choice_layouts.py`,
`mvp_forms/static/mvp_forms/choice-fold.js`, `mvp_forms/widgets.py`, `README.md`

Plan, *The script*. Browser tests first: a choice chosen from inside the fold stays on show when
the fold is closed and the count is the number still folded; a page that does not load the script
can open the fold, choose a folded choice and submit; a form drawn again after a failed submission
has every chosen choice on show and chosen; a fold added by a script and one in a form swapped in
by htmx behave as on a page load; the script included twice acts once; a disabled field's fold
opens and nothing in it can be chosen. Then the script, and the chip and card widgets' `Media`
naming it (a test that the scale and the pills name none). README: what the script adds.

### Group 6 — legibility

- [ ] T009 [US2] Legibility under every theme

**Files**: `tests/legibility/`, `tests/test_pack/test_legibility.py`, `README.md` (known exceptions
table, only if the report prints any)

FR-028. Pairings for the text of a choice, the end words, a chip's quiet choice, a card's
description and the mark of a chosen choice, measured under every theme the suite measures
against the surface behind them. A pairing that falls short is fixed in the widget's classes where
daisyUI's own colour allows it, and otherwise published as a known exception as the harness
prescribes (`uv run python -m tests.legibility`).
