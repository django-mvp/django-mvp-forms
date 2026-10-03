# Tasks — 005 Tabs, accordion, modal and alert in a layout

**Branch**: `005-container-layout-objects` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a layout object lands in the task
that adds it.

No test asserts wording, width, spacing, colour or which utility arranges anything. Elements are
found by id, by name, by role and by element type. A class is asserted only where it is a daisyUI
component (`tabs`, `tab`, `tab-content`, `collapse`, `collapse-title`, `collapse-content`,
`modal`, `modal-box`, `alert`), which the testing standard counts as behaviour for a published
pack ("Markup that consumers depend on"). "Open" is asserted by the attribute the browser acts
on: `checked` on a tab's radio, `open` on a `details` or a `dialog`.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell pages only.
Layout objects are imported from django-crispy-forms. The package adds none of its own.

## Order

**US1 → US2 → US3 → US4, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Group parts of a form behind tabs (P1)

Issue: #66. Delivers FR-001 – FR-004, and for tabs FR-017 – FR-023; SC-001, SC-002, SC-004.

### T001 — `TabHolder` and `Tab`

**Files**: `mvp_forms/templates/daisyui/layout/tab.html`, `layout/tab-pane.html`,
`layout/tab-link.html`, `layout/div.html`, `mvp_forms/templatetags/daisyui.py`,
`tests/test_pack/test_tabs.py`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`

Plan, *Tabs* and *The three class names*; research R1 – R5, R10.

- The three templates and the branch in `div.html` as the plan has them. `daisyui_tab_group` and
  `TAB_GROUP_PLACEHOLDER`. `tab-pane` and `active` join `UPSTREAM_ONLY_CLASSES`.
- Tests, `tests/test_pack/test_tabs.py`:
  - one radio and one content element per `Tab`, each radio directly before its own content, and
    each content holding its own fields (US1.1);
  - unbound, exactly one radio is checked and it is the first (US1.2); with an error in the
    second tab the second is checked and the error element is inside its content (US1.3); with
    errors in the second and third, the second (US1.4); with the field nested in a `Row` or a
    `Fieldset` inside the tab (US1.5); with only a form-wide error, the first (US1.6);
  - two holders in one form, and one holder in each of two forms drawn on one page, have
    different group names, and the radios of one holder share one (US1.7, FR-020); a holder
    nested in a tab of another has a name of its own; no radio keeps the placeholder name;
  - no control the holder draws would be submitted or submits: every radio has `form=""`, and
    the named controls without it are the form's own fields (US1.8, FR-019);
  - a tab name holding markup is escaped in the radio's name for assistive technology, and a
    lazily translated name is drawn (FR-022); a single tab is drawn and checked; a tab holding
    only an `HTML` object is drawn and is not checked on account of an error elsewhere;
  - `css_id`, `css_class` and attributes on the holder and on a tab reach their elements, and
    neither `tab-pane` nor `active` is drawn (FR-017);
  - a plain `Div` is still drawn as FS-003 left it.
- Tests, `tests/test_templatetags/test_daisyui.py`: `daisyui_tab_group` replaces every
  placeholder with one name, gives two calls two names, and returns a safe string;
  `daisyui_classes` drops the two names.
- `test_independence.py`: a tabs state, unbound and bound. `test_documented_examples.py`: the
  `TabHolder` and `Tab` docstring examples.
- README, *Layout objects*: `TabHolder` and `Tab`, with an example, that the first tab holding an
  error opens, that a tab's radio is not submitted, and the two dropped names. CHANGELOG entry.

### T002 — The tabs demo page and the standalone page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/tabs.html`, `demo/templates/demo/containers_standalone.html`,
`tests/test_demo.py`, `CHANGELOG.md`

Plan, *The demo project*.

- The tabs page on the shell, with its menu entry and icon, and the standalone page holding the
  tabs forms. Each links to the other.
- Tests: both pages respond; the shell wraps the first and the sidebar links it; the standalone
  page carries daisyUI's CDN stylesheet and none of the shell's; a get has the first tab
  checked; an empty post comes back with the second tab checked and an error element inside it;
  the already failing form has its third tab checked; no id repeats on either page.

---

## US2 — Group parts of a form in an accordion (P1)

Issue: #67. Delivers FR-005 – FR-007, and for the accordion FR-017 – FR-023; SC-001, SC-002,
SC-004.

### T003 — `Accordion` and `AccordionGroup`

**Files**: `mvp_forms/templates/daisyui/accordion.html`, `accordion-group.html`,
`tests/test_pack/test_accordion.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Accordion*; research R1, R2, R6.

- The two templates as the plan has them.
- Tests, `tests/test_pack/test_accordion.py`:
  - one `details` per `AccordionGroup` inside the accordion's element, each with a `summary`
    and its own fields (US2.1);
  - unbound, the first group is open and the rest are closed; `active=True` on a later group
    opens it too; `active=False` on the first keeps it closed (US2.2, FR-007);
  - an error in a closed group opens it with the error element inside (US2.3); errors in two
    groups open the first of them (US2.4); an accordion inside a tab with an error in a group
    has both the tab checked and the group open (US2.5);
  - no `details` carries a `name`, and two accordions have different ids (US2.6, FR-020);
  - the accordion draws no input, select, textarea or button of its own (US2.7, FR-019);
  - a group name holding markup is escaped, and a lazily translated name is drawn; a single
    group is drawn open; a group holding only an `HTML` object is drawn;
  - `css_id`, `css_class` and attributes on the accordion and on a group reach their elements
    (FR-017).
- `test_independence.py`: an accordion state, unbound and bound.
  `test_documented_examples.py`: the `Accordion` and `AccordionGroup` docstring examples.
- README: `Accordion` and `AccordionGroup`, with an example, which groups start open, and that
  each group opens and closes on its own. CHANGELOG entry.

### T004 — The accordion demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/accordion.html`, `demo/templates/demo/containers_standalone.html`,
`tests/test_demo.py`, `CHANGELOG.md`

- The accordion page on the shell, and its forms added to the standalone page.
- Tests: the page responds, is wrapped and linked; a get has the first group open; an empty post
  comes back with the third group open and an error element inside it; the second form has the
  group the developer opened open and the one closed closed; no id repeats.

---

## US3 — Show part of a form in a modal (P2)

Issue: #68. Delivers FR-008 – FR-013, and for the modal FR-017 – FR-020, FR-022, FR-023;
SC-001, SC-002, SC-004.

### T005 — `Modal`

**Files**: `mvp_forms/templates/daisyui/layout/modal.html`,
`mvp_forms/templatetags/daisyui.py`, `tests/test_pack/test_modal.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Modal*; research R1, R7, R8.

- The template as the plan has it, and `daisyui_invalid`.
- Tests, `tests/test_pack/test_modal.py`:
  - a `dialog` with daisyUI's `modal` class and the developer's id, holding its fields inside a
    `modal-box`, with no `open` attribute (US3.1);
  - the title is drawn inside the dialog in an element whose id is the one the dialog's
    `aria-labelledby` names (US3.2, FR-009); a title holding markup is escaped (FR-022);
  - the dialog holds one button of type `button`, with text, and no element of type `submit`
    (US3.4, FR-010); nothing outside the dialog refers to its id (FR-011);
  - the modal's fields are inside the form element when the helper draws one (US3.5, FR-013);
  - bound with an error in a field of the modal, the dialog has `open` and the error element is
    inside it (US3.6); bound with an error only in a field outside the modal it does not; with
    `form_show_errors` off it still opens; a modal holding only an `HTML` object never opens;
  - a field with an error in a group in a tab in a modal has all three open;
  - two modals with two ids are both drawn, and an error in one opens only that one (FR-020);
  - `css_class`, `title_class`, `title_id` and extra attributes reach their elements (FR-017).
- Tests, `tests/test_templatetags/test_daisyui.py`: `daisyui_invalid` is true for drawn fields
  holding an invalid input and false otherwise, including for a field whose value is the text
  `aria-invalid="true"`.
- `test_independence.py`: a modal state, unbound and bound.
  `test_documented_examples.py`: the `Modal` docstring example.
- README: `Modal`, with an example, how a host project opens it by its id, that it is drawn open
  when a field inside it has an error, and that `title_class` styles the title. CHANGELOG entry.

### T006 — The modal demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/modal.html`, `demo/templates/demo/containers_standalone.html`,
`tests/test_demo.py`, `CHANGELOG.md`

- The modal page on the shell, with a control in the page that opens the modal by its id, and
  its form added to the standalone page.
- Tests: the page responds, is wrapped and linked; a get has the dialog closed; an empty post
  comes back with the dialog open and an error element inside it; the page holds a control
  outside the dialog that names the dialog's id (FR-024); no id repeats.

---

## US4 — Place a notice in a layout (P2)

Issue: #69. Delivers FR-014 – FR-016, and for the alert FR-017 – FR-020, FR-022; FR-024,
FR-025; SC-001, SC-003, SC-006.

### T007 — `Alert`

**Files**: `mvp_forms/templates/daisyui/layout/alert.html`,
`mvp_forms/templatetags/daisyui.py`, `tests/test_pack/test_alert.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Alert*; research R9, R10.

- The template as the plan has it. `alert-block` joins `UPSTREAM_ONLY_CLASSES`.
- Tests, `tests/test_pack/test_alert.py`:
  - an element with `role="alert"` and daisyUI's `alert` class, between the two fields it was
    placed between (US4.1);
  - dismissible by default: it holds one button of type `button` with an `aria-label`, and no
    element of type `submit` (US4.2, US4.3, FR-015); with `dismiss=False` it holds no button
    (US4.4);
  - content written with markup is drawn as markup (US4.5);
  - an extra class is on the alert (US4.6); `css_id` and attributes reach it; `block=True` draws
    and `alert-block` is not written (FR-017);
  - two alerts are both drawn, each with its own dismiss control (FR-020); a bound form draws
    the alert again.
- `test_independence.py`: an alert state. `test_documented_examples.py`: the `Alert` docstring
  example.
- README: `Alert`, with an example, how to colour it with a daisyUI modifier, that a dismissal is
  not remembered, and the note that alert content is trusted and anything a person typed must be
  escaped before it is put there (FR-016, FR-025). The sentence listing the six as supported.
  CHANGELOG entry.

### T008 — The alert demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/alert.html`, `demo/templates/demo/containers_standalone.html`,
`tests/test_demo.py`, `CHANGELOG.md`

- The alert page on the shell, and its form added to the standalone page.
- Tests: the page responds, is wrapped and linked; it holds a dismissible alert and one without
  a dismiss control; the standalone page holds all four layout objects; no id repeats on either.
