# Tasks — 004 Layout objects that decorate a field

**Branch**: `004-field-decorating-layout-objects` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass,
the tree is green and the work is committed. Documentation for a layout object lands in the task
that adds it.

No test asserts wording, width, spacing, colour or which utility arranges anything. Elements are
found by id, by name, by role and by element type. A class is asserted only where it is a daisyUI
component or modifier (`input`, `select`, `label`, `join`, `join-item`, `checkbox`, `radio`, the
`-error` modifiers), which the testing standard counts as behaviour for a published pack ("Markup
that consumers depend on"). The inline arrangement is asserted by which widget template drew the
group, never by a utility class.

Code standards for every task: no leading-underscore names anywhere (methods, helpers, constants,
templates); line length 88; no compatibility aliases; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests. Pack templates are
plain Django templates: `{% include %}` is fine inside the pack, and django-cotton never appears
in anything under `mvp_forms/`. Cotton components are for the demo project's shell pages only.
Layout objects are imported from django-crispy-forms. The package adds none of its own. Nothing
under `.github/` is touched.

## Order

**US1 → US2 → US3 → US4 → US5 → US6, sequential, in the feature worktree** (plan, *Story order*).

---

## US1 — Text prepended or appended to an input (P1)

Issue: #59. Delivers FR-001 – FR-008, and for these three FR-023 – FR-028, FR-031; SC-001 – SC-004.

### T001 — `PrependedText`, `AppendedText` and `PrependedAppendedText`

**Files**: `mvp_forms/templates/daisyui/field.html`, `frame.html`, `field_body.html`,
`layout/prepended_appended_text.html`, `mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_pack/test_attached_text.py`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`

Plan, *One frame, told how the field is decorated*, *The frame takes a wrapper class* and
*Attached text*; research R1, R2, R5, R9.

- Move the frame to `frame.html`, with `field.html` reduced to the tag and the include. Give
  `daisyui_field` its keyword options and `FieldInput` the three keyword-only arguments this
  story needs: `wrapper_class`, `prepended` and `appended`. Each of the other four arrives in
  the task that gives it behaviour (`inline` in T003, `join` in T005, `disabled` in T007,
  `unlabelled` in T009). Split the classes into `own_classes` and `pack_classes`.
- Tests, `tests/test_pack/test_attached_text.py`, drawn through `{% crispy %}`:
  - prepended: one wrapper `label` carrying `input` holds a `span.label` before the input and
    none after, the input inside it carries no `input` class, and the frame holds one label for
    the field and one help text (US1.1); appended: the span is after (US1.2); both (US1.3); only
    one of the two set on `PrependedAppendedText`, and an empty string or None on either: one
    span, or none and no wrapper (US1.4, FR-002);
  - bound and failing: the wrapper carries `input-error`, the error element is in the frame, the
    input has `aria-invalid` and is described by the error element (US1.5);
  - the input is inside the wrapper `label`, so the text is part of its name (US1.6, FR-004);
  - on a select: the wrapper carries `select`, and `select-error` when failing (US1.7, FR-003);
  - the input's `name` and `value` equal the unwrapped field's, and the bound form's
    `cleaned_data` is the same with and without the layout object (US1.8, FR-006, SC-004);
  - text holding markup is drawn as an element (FR-007); a label, help text, error and value
    holding markup are escaped (FR-026);
  - `css_class` and an extra attribute reach the input, `wrapper_class` reaches the frame's
    outer element, `template=` draws a template of the developer's, and `input_size` and
    `active` raise nothing and add no class daisyUI lacks (FR-024, FR-027);
  - on a checkbox, a radio group, a date drawn as three selects, a textarea and a file input
    the field is drawn as it is undecorated, with its input, label and errors, and a hidden field is drawn as a hidden input alone (FR-025, Edge Cases);
  - `wrapper_class` on a plain `Field` reaches the frame, on a `div` frame and on a `fieldset`
    frame, and a field with none has no extra class.
- Tests, `tests/test_templatetags/test_daisyui.py`: `own_classes`, `pack_classes`,
  `has_attached_text` and `attached_class` for an input, a select and an unsuited widget; the
  bare input's class is its own classes, or absent; the tag passes its keyword options on and
  reads `wrapper_class` from the context.
- A state for attached text, unbound and failing, in `test_independence.py`'s `STATES`, and
  django-crispy-forms' docstring examples for the three in `test_documented_examples.py`.
- README: a section for the layout objects that decorate a field, opening with these three:
  where to import each from, what is drawn, that the text is markup and must be escaped first
  when built from anything a person typed (FR-008), that `input_size` does nothing yet, and
  that `wrapper_class` now works on any field. CHANGELOG entry, which also says that the frame
  now lives in `daisyui/frame.html`, so a host project that overrides `daisyui/field.html` to
  change the frame overrides `frame.html` instead.

### T002 — The attached-text demo page and the standalone page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/attached_text.html`, `demo/templates/demo/decorated_fields_standalone.html`,
`tests/test_demo.py`, `README.md`, `CHANGELOG.md`

Plan, *The demo project*.

- Route `attached-text` on the shell and route `decorated-fields-standalone`, each linking the
  other. A form to post that fails when submitted empty and one already failing, showing all
  three layout objects on an input and at least one on a select (US1.9).
- Tests: both pages answer; the menu holds the entry; each of the three is drawn valid and with
  an error (found by field id); posting empty comes back with errors; no id repeats on a page;
  the standalone page loads no django-mvp or Cotton asset, as the FS-005 standalone test checks.
- README's demo section lists the two routes. CHANGELOG entry.

---

## US2 — Checkboxes and radios in a line (P1)

Issue: #60. Delivers FR-009 – FR-011.

### T003 — `InlineRadios` and `InlineCheckboxes`

**Files**: `mvp_forms/templates/daisyui/widgets/group.html`, `widgets/group_options.html`,
`widgets/inline_group.html`, `layout/radioselect_inline.html`,
`layout/checkboxselectmultiple_inline.html`, `mvp_forms/templatetags/daisyui.py`,
`tests/forms.py`, `tests/test_pack/test_inline_groups.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Inline groups*; research R4.

- Tests, `tests/test_pack/test_inline_groups.py`:
  - every choice is a `radio` (or `checkbox`) input inside a `label` of its own tied by `for`
    (US2.1, US2.2); the group is drawn by the inline template and the stacked group by the
    stacked one, asserted through `FieldInput.template_name` (FR-009);
  - the frame is a `fieldset` with a `legend`, the required marker and the help text, described
    by help text and error (US2.3, US2.4, FR-010);
  - initial and submitted values check exactly those options (US2.5); `cleaned_data` equals the
    stacked group's for the same data (US2.6, FR-011);
  - disabled options are disabled (US2.7), with a disabled field and with a widget that disables
    one option;
  - choices with named groups are drawn under their names; a widget naming its own template or
    option template is drawn by it; `InlineRadios` on a field with no choices and on a text
    field draws the field (FR-025); `wrapper_class`, `css_class` and `template=` (FR-024).
- `FieldInput` gains `inline`. `test_daisyui.py`: `template_name` with and without `inline`. A state in `STATES`. Upstream's
  docstring examples for the two.
- README and CHANGELOG.

### T004 — The inline-choices demo page

**Files**: `demo/forms.py`, `demo/views.py`, `demo/urls.py`, `demo/menus.py`, `demo/settings.py`,
`demo/templates/demo/inline_choices.html`, `demo/templates/demo/decorated_fields_standalone.html`,
`tests/test_demo.py`, `README.md`, `CHANGELOG.md`

- Route `inline-choices`; both layout objects, to post and already failing (US2.8). The same
  forms on the standalone page. Tests as T002's, for this page.

---

## US3 — A field with buttons attached (P2)

Issue: #61. Delivers FR-012 – FR-014.

### T005 — `FieldWithButtons`

**Files**: `mvp_forms/templates/daisyui/field_body.html`, `layout/field_with_buttons.html`,
`mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_pack/test_field_with_buttons.py`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`

Plan, *Field with buttons*; research R3.

- Tests, `tests/test_pack/test_field_with_buttons.py`:
  - one `join` element holds the input and the button, the input first and carrying
    `join-item`, and the frame holds one label and one help text (US3.1); several buttons are
    all inside it in the order given (US3.2), for `StrictButton`, `Submit` and `Button`;
  - a `Field` as the first item passes its attributes and class to the input (US3.3, FR-013);
  - failing: the input has its error modifier and `aria-invalid`, the error element is in the
    frame and describes the input (US3.4);
  - a `Submit` in the group keeps its `name` and `value`, the same as the one drawn outside a
    group (US3.5);
  - no buttons: the group holds the input alone (Edge Cases); `css_id`, `css_class` and an
    extra attribute are on the `join` element, a class written for another pack is dropped, and
    `input_size` raises nothing and draws no class (FR-024, FR-027); `template=`;
  - a button whose content is a template variable holding `{{ … }}` is drawn once, escaped, and
    not evaluated (research R3);
  - on a select the group is drawn; on a checkbox and a radio group the field and the buttons
    are both drawn (FR-025); a hidden field is drawn alone.
- `FieldInput` gains `join`. `test_daisyui.py`: `is_joined`, and `join-item` in `pack_classes`
  only when joined and never on a group. A state in
  `STATES`. Upstream's docstring example.
- README (including that a button takes `css_class="join-item"` to close the doubled border)
  and CHANGELOG.

### T006 — The field-with-buttons demo page

**Files**: as T004, with `demo/templates/demo/field_with_buttons.html`

- Route `field-with-buttons`; a field with one button and one with several, to post and already
  failing (US3.6). The same forms on the standalone page. Tests as T002's, for this page.

---

## US4 — An uneditable field (P2)

Issue: #62. Delivers FR-015, FR-016.

### T007 — `UneditableField`

**Files**: `mvp_forms/templates/daisyui/layout/uneditable_input.html`,
`mvp_forms/templatetags/daisyui.py`, `tests/forms.py`,
`tests/test_pack/test_uneditable_field.py`, `tests/test_templatetags/test_daisyui.py`,
`tests/test_pack/test_independence.py`, `tests/test_pack/test_documented_examples.py`,
`README.md`, `CHANGELOG.md`

Plan, *Uneditable field*; research R1, R7.

- Tests, `tests/test_pack/test_uneditable_field.py`:
  - with an initial value the input shows it, is `disabled` and keeps its component class
    (US4.1); label and help text are drawn and tied (US4.2); with no value it is empty and
    disabled (US4.3);
  - a field declared `disabled=True` in the form keeps its initial value in `cleaned_data` when
    submitted without it (US4.4); a field not declared disabled and required fails with the
    `required` code when the value is left out, which is what the browser does (Edge Cases);
  - a value holding markup is escaped (US4.5);
  - a select, a single checkbox, every option of a radio group and a textarea are disabled;
  - `uneditable-input` is not drawn; the form's own widget is not changed to disabled by the
    pack; `css_class`, `wrapper_class` and `template=` (FR-024).
- `FieldInput` gains `disabled`. `uneditable-input` joins `UPSTREAM_ONLY_CLASSES`, as ADR 0010
  asks, and `own_classes` drops that one name. `test_daisyui.py`: `disabled` in `attrs`;
  `uneditable-input` absent from `own_classes`; a developer's own `active` class still on an
  input. A
  state in `STATES`. Upstream's docstring example.
- README, stating that the browser does not submit the value and that a form which needs it
  kept declares the field disabled (FR-016), and correcting the sentence under *Disabled and
  read-only fields* that says the pack adds no attribute for either state: `UneditableField` is
  the one case where it writes `disabled`. CHANGELOG.

### T008 — The uneditable-field demo page

**Files**: as T004, with `demo/templates/demo/uneditable_field.html`

- Route `uneditable-field`; an uneditable field beside an editable one (US4.6). The same form
  on the standalone page. Tests as T002's, without an error state.

---

## US5 — An inline field (P3)

Issue: #63. Delivers FR-017 – FR-020.

### T009 — `InlineField`

**Files**: `mvp_forms/templates/daisyui/layout/inline_field.html`,
`mvp_forms/templatetags/daisyui.py`, `tests/forms.py`, `tests/test_pack/test_inline_field.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Inline field* and the `unlabelled` rows under *One frame*; research R8.

- Tests, `tests/test_pack/test_inline_field.py`:
  - a text field has no `label` element in its frame and an `aria-label` equal to the field's
    label (US5.1); a placeholder equal to the label when the widget sets none (US5.2); the
    widget's own placeholder kept (US5.3); a widget's own `aria-label` kept;
  - a single checkbox keeps its `label` with the checkbox inside (US5.4, FR-020);
  - failing: the error element is drawn and describes the input, which has `aria-invalid` and
    its error modifier (US5.5); help text is drawn and describes the input (US5.6);
  - a label marked safe reaches the placeholder as text; a select and a radio group are drawn
    without a placeholder attribute, the group named by `aria-label` (FR-025);
  - a field beside it that is not inline keeps its label; `wrapper_class`, `css_class`,
    `template=` (FR-024); `cleaned_data` unchanged (SC-004).
- `FieldInput` gains `unlabelled`, and the frame and its body read `drawn.show_labels` where
  they read `form_show_labels != False`. `test_daisyui.py`: `show_labels` and the placeholder
  under `unlabelled`. A state in `STATES`.
  Upstream's docstring example.
- README and CHANGELOG.

### T010 — The inline-field demo page

**Files**: as T004, with `demo/templates/demo/inline_field.html`

- Route `inline-field`; a short form of inline fields, to post and already failing (US5.7).
  The same forms on the standalone page. Tests as T002's, for this page.

---

## US6 — Attributes for each part of a multi-widget field (P3)

Issue: #64. Delivers FR-021, FR-022.

### T011 — The parts of a multi-widget field, and `MultiWidgetField`

**Files**: `mvp_forms/templatetags/daisyui.py`, `mvp_forms/locale/en/LC_MESSAGES/django.po`,
`tests/forms.py`, `tests/test_pack/test_multi_widget.py`,
`tests/test_templatetags/test_daisyui.py`, `tests/test_pack/test_independence.py`,
`tests/test_pack/test_documented_examples.py`, `README.md`, `CHANGELOG.md`

Plan, *Multi-widget fields*; research R1, R6.

- Tests, `tests/test_pack/test_multi_widget.py`:
  - a sequence of attribute sets puts each on its own part (US6.1); a single set on every part
    (US6.2); fewer sets than parts leaves the rest without them and raises nothing (US6.4);
  - each part of a split date and time carries `input`, and `input-error` when the field fails;
    a class given to one part is kept beside the pack's; the frame is a `fieldset` with one
    `legend`, one help text and one error element, described by them (US6.3, FR-022);
  - each part has an `aria-label`, the two of a split date and time different from each other,
    and one given through `MultiWidgetField` is kept; the parts of another multi-widget are
    named by the field's label; a part made hidden through `MultiWidgetField` gets neither a
    class nor a name;
  - `cleaned_data` equals the undecorated field's (US6.5, SC-004);
  - the form's own widget and its parts carry no class or name of the pack's after drawing;
    drawing twice gives the same markup; a split date and time with no layout object is drawn
    the same way; a hidden split field is drawn as hidden inputs alone;
  - `MultiWidgetField` on a field with one widget draws the field (FR-025); `wrapper_class` and
    `template=` (FR-024).
- `test_daisyui.py`: the copy's parts and the untouched original. A state in `STATES`.
  Upstream's docstring example.
- `Date` and `Time` join the English catalogue (FR-029).
- README: `MultiWidgetField`, and the line about widgets drawn without a class updated for the
  split date and time. CHANGELOG.

### T012 — The multi-widget-field demo page

**Files**: as T004, with `demo/templates/demo/multi_widget_field.html`

- Route `multi-widget-field`; a split date and time with a different attribute on each part, to
  post and already failing (US6.6). The same forms on the standalone page. Tests as T002's, for
  this page.
