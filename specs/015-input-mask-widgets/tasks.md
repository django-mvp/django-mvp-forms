# Tasks — 015 Input mask widgets for IMask

**Branch**: `015-input-mask-widgets` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. `mvp_forms/widgets.py`,
`mvp_forms/static/mvp_forms/imask.js` and the demo page are on the branch from the approved
sketch, with no tests. A task rebuilds the part it names test-first: the tests are written, seen
to fail against the prototype or with the prototype's code for that part removed, and seen to
pass. Prototype code a task does not rebuild is deleted by the task that replaces it, so nothing
untested is left at the end. A task is done when its tests pass, the tree is green and the work is
committed. Documentation lands in the task that introduces what it describes.

What the maintainer approved on screen is not changed: the demo page's sections, their order, the
help text and the links. The one planned difference is in T003. A test that cannot pass without
changing anything else on that page is reported, not made to pass.

No test asserts wording, a colour or a measurement. A widget test asserts the attribute's JSON,
the media, what is raised and what the field receives. A browser test asserts what this
package's script does and never IMask's own masking rules beyond one keystroke that shows the
options arrived.

Code standards for every task: no leading-underscore names; line length 88; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`, with tests for `mvp_forms/widgets.py` in
`tests/test_widgets.py`, one class for each widget and block. `mvp_forms/widgets.py` imports Django and the standard library only.
`CONSTITUTION.md` and everything under `.github/` do not change. A document reads as current
state. README links are absolute. Every `ValueError` names the option at fault.

## Decision records

Written at convergence, after the last story, with numbers read from `origin/main` at that
moment. No task writes one. T003 edits the one sentence about a script file in ADR 0014 and in
ADR 0041.

## Order

**US1 → US2 → US3 → US5 → US4 → US6, sequential, in the feature worktree.**

---

## US1 — A developer masks a text field with a pattern (P1)

Issue: #152. Delivers FR-001 to FR-007, FR-013 to FR-017, FR-021 to FR-024, FR-026, FR-028 to
FR-034; SC-001, SC-002, SC-004 to SC-006, SC-008.

### T001 — The pattern widget and its blocks

**Files**: `tests/test_widgets.py` (new), `tests/test_pack/test_masked_inputs.py` (new),
`tests/test_pack/test_independence.py`, `tests/forms.py`, `mvp_forms/widgets.py`,
`demo/forms.py`, `demo/views.py`

Plan, *The widgets*; research R1 to R4.

- `MaskInput` and `PatternMaskInput` as the plan's table has them, and `RangeBlock`, `EnumBlock`
  and `PatternBlock`. `data-imask` holds `kind` and every stated option under IMask's name, and
  nothing unstated. A `placeholder_char` mapping becomes definitions that carry a placeholder
  character, with the expression left out for `0`, `a` and `*` unless the developer defined them.
- Everything the plan lists as refused for a pattern and for the three blocks raises
  `ValueError` naming the option. An unknown option is Python's own `TypeError`.
- The widget names `mvp_forms/imask.js` in its media, keeps the developer's `attrs`, and escapes
  a pattern holding a quote or an angle bracket.
- Drawn through the pack it is a daisyUI `input` that takes a stated size, colour and variant.
  The same attribute is drawn through `|crispy`, `{% crispy %}`, `|as_crispy_field` and
  `{{ form.as_div }}`.
- The static-directory test names the stylesheet and the script.
- The prototype's `RegexMaskInput`, `NumberMaskInput` and `DynamicMaskInput` are removed from
  `mvp_forms/widgets.py`. The demo's pattern fields move to the block classes here. Every demo
  field that uses a removed widget comes out until its story puts it back exactly as approved:
  the three widgets' own forms, the disabled number field of `MaskStatesForm` and the price field
  of `MaskedLineForm`, the last two back in T005. The demo page still answers and
  `tests/test_demo.py` is green.

### T002 — The script, tested in Chrome

**Files**: `tests/test_imask_e2e.py` (new), `tests/conftest.py`, `tests/data/imask-7.6.1.min.js`
(new), `tests/urls.py`, `tests/host_app/`, `tests/templates/tests/`, `pyproject.toml` (the
`e2e` marker, the environment variable django-mvp sets for its browser tests, and
`tests/test_imask_e2e.py` under `non-mirror-paths`), `mvp_forms/static/mvp_forms/imask.js`

Plan, *The script*, *The tests*; research R2, R6, R7, R9.

- Fixtures: the module is skipped where Chrome cannot be launched and fails in CI. The rule is
  django-mvp's, and the check is written for the channel: it tries the launch. The browser is launched with `channel="chrome"`. A request
  for IMask is answered from `tests/data/`. The test project gains pages that draw a pattern
  form with and without IMask on the page.
- The script is rewritten against these tests: a mask is applied to each input with the options
  written on it (one keystroke shows a definition, a block and a placeholder arrived); a bound
  value is shown under the mask; a page that includes the script three times gives each input one
  mask; a page without IMask raises no error, leaves the input a text input and submits; a field
  with a display character shows that character and submits what was typed; an input removed
  from its form adds no entry to that form's data; a page served with a Content-Security-Policy
  that allows scripts from its own origin and IMask's, and nothing inline, still masks its input.
  The `formdata` listener is attached for every masked input with a form, with no test for a
  display character.
- The red step for each behaviour is the test failing with that part of the script removed.

### T003 — The demo page, the README section and the records

**Files**: `tests/test_demo.py`, `demo/forms.py`, `demo/views.py`, `demo/urls.py`,
`demo/templates/demo/input_masks.html`, `demo/templates/demo/input_masks_standalone.html` (new),
`README.md`, `CHANGELOG.md`, `CONTEXT.md`, `docs/adr/0041-*.md`

Plan, *The demo*, *Documentation*.

- The reference field and the formset's
  article field state `placeholder_char={"0": "#", "a": "a"}` on the pattern `aa-0000`, and
  their help text and the formset section's sentence state that pattern. Nothing else on the page
  changes.
- A standalone page without django-mvp, linked from the page as the other demo pages link theirs.
  Both pages and the README's example load `imask@7.6.1` with `integrity` and `crossorigin`.
- Tests: the page answers, the sidebar links it, the pattern section holds a masked input for
  each field, a post of the pattern form returns what each field received, and the standalone
  page carries none of the shell.
- README: the "Input masks" section with what this story introduces: loading IMask and the
  form's media, `PatternMaskInput` and the blocks with every option, what the form receives, a
  page without IMask, a display character, what is not supported. The widgets and the script
  appear in the public surface.
- The sentence in ADR 0014 and ADR 0041, the CHANGELOG entry and the glossary terms. `CONTEXT.md`
  lists "block" under Avoid for a layout object, and the two entries are reconciled. The README
  and the glossary never call `DynamicMaskInput` a "choice", which is already a term for a size,
  colour or variant.

---

## US2 — A developer restricts what can be typed with a regular expression (P2)

Issue: #153. Delivers FR-008.

### T004 — The regular expression widget

**Files**: `tests/test_widgets.py`, `tests/test_imask_e2e.py`,
`tests/test_demo.py`, `mvp_forms/widgets.py`, `mvp_forms/static/mvp_forms/imask.js`,
`demo/views.py`, `README.md`

- `RegexMaskInput(mask, attrs=None, *, flags=None)`: the attribute holds the source and the
  flags. An empty or non-text `mask` and a flag JavaScript does not have are refused. Python
  never compiles the expression.
- In Chrome: a character that stops the value matching is not accepted, and a flag reaches
  IMask.
- The demo's regular expression section is back, and the README documents the widget with the
  caution about partial values.

---

## US3 — A developer formats a number as it is typed (P2)

Issue: #154. Delivers FR-009, FR-010, FR-018 to FR-020; SC-003.

### T005 — The number widget

**Files**: `tests/test_widgets.py`, `tests/test_imask_e2e.py`,
`tests/test_demo.py`, `mvp_forms/widgets.py`, `mvp_forms/static/mvp_forms/imask.js`,
`demo/forms.py`, `demo/views.py`, `README.md`

Research R5.

- Every option in the plan's table reaches the attribute, with `min_value` and `max_value`
  written as IMask's `min` and `max`. Each takes an `int`, a `float` or a `Decimal` and is written
  as a JSON number. What the plan lists as refused is refused, including
  `NumberMaskInput(thousands_separator=",")` with no `radix`, which names `thousands_separator`.
- `inputmode` is `decimal`, or `numeric` when `scale` is zero, and a developer's own is kept.
- `value_from_datadict`: a `DecimalField` and an `IntegerField` receive the plain number for each
  pair of separators, including IMask's defaults when none is stated, an empty value stays
  empty, and a negative number keeps its sign.
- `format_value`: an initial `Decimal`, an initial string and a bound value are each written with
  the widget's decimal mark and no thousands separator, with localisation on and off.
- In Chrome: a typed number gains its separators, an initial value is shown with them, and the
  page's post returns the plain number. The script has no branch for numbers beyond naming
  `Number`.
- The demo's number section is back with `min_value` and `max_value`. The README documents the
  widget and the caution about a page without IMask.

---

## US5 — A developer offers several masks and lets the best fit apply (P3)

Issue: #156. Delivers FR-011, FR-012.

### T006 — The widget that chooses between masks

**Files**: `tests/test_widgets.py`, `tests/test_imask_e2e.py`,
`tests/test_demo.py`, `mvp_forms/widgets.py`, `mvp_forms/static/mvp_forms/imask.js`,
`demo/views.py`, `README.md`

- `DynamicMaskInput(masks, attrs=None)`: the attribute holds each mask's options in order. An
  empty list and an item that is not one of the other three widgets are refused. The field
  receives the submitted text unchanged, including where a mask in the list is a number.
- In Chrome: with two patterns of different lengths, the mask in place changes as more is typed,
  and a list holding a pattern with a display character submits what was typed.
- The demo's section is back, and the README documents the widget.

---

## US4 — A developer uses a masked field in a formset, a modal and content loaded later (P2)

Issue: #155. Delivers FR-025; SC-007.

### T007 — Inputs added after the page loads

**Files**: `tests/test_imask_e2e.py`, `tests/test_pack/test_masked_inputs.py`,
`tests/test_demo.py`, `tests/templates/tests/`, `mvp_forms/static/mvp_forms/imask.js`,
`README.md`

Research R8.

- A formset's empty form carries the same attribute as its other forms.
- In Chrome: an input inserted by a script is masked; a node inserted with a masked input inside
  it is masked; an input moved within the page keeps one mask; a masked input in a `Modal` works
  once the dialog is open; a disabled and a read-only masked input show their value under the
  mask and keep their state.
- The red step removes the observer.
- The demo's formset, modal, states and size sections are tested for a masked input each. The
  README says inputs added later are masked, and names htmx 2 where it names htmx.

---

## US6 — A developer adds an option that needs JavaScript (P3)

Issue: #157. Delivers FR-027.

### T008 — The event

**Files**: `tests/test_imask_e2e.py`, `mvp_forms/static/mvp_forms/imask.js`, `README.md`

- In Chrome: a listener on the document receives `mvp-forms:imask` from each masked input, with
  the IMask instance in `detail.mask`; an input added later sends it too; options updated on the
  instance from the listener apply to what is typed next.
- The red step removes the dispatch.
- The README documents the event with one example that sets an option the widgets do not carry.
