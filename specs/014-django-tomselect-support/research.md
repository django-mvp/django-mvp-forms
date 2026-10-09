# Research: django-tomselect support

Done after the maintainer approved the sketch, against `main` at `0b7d859`. There are no planning
notes for this feature. Each line of `sketch.md` under "What the screens need" and "What the sketch
faked" is answered here by number.

## R1. What the pack already does for a django-tomselect select

`FieldInput` gives a widget that names a template of its own the pack's class and nothing else
(ADR 0012). For a django-tomselect widget that is `select`, the size, colour and variant modifiers
stated for the form or the field, `select-error` on a field in error, and `w-full`. Measured on the
sketch: `class="select w-full select-error"` on a bound form with the field missing.

Tom Select copies the classes of the element it replaces to its wrapper and to its dropdown. The
wrapper is therefore a daisyUI select with no code of ours: FR-010 and FR-011 need no change under
`mvp_forms/`, only tests that hold the markup. Disabled is the one state that does not arrive this
way, because daisyUI keys it on the `disabled` attribute and Tom Select writes a class.

## R2. Where the stylesheet lives and how it is loaded (needs 1 and 2)

`mvp_forms/static/mvp_forms/tomselect.css`. The wheel is built from the `mvp_forms` package
directory, so the file ships with no change to `pyproject.toml`. A host project links it with
`{% static 'mvp_forms/tomselect.css' %}`.

django-tomselect's widgets name Tom Select's stylesheet and its own in their form media, and
django-crispy-forms writes a form's media beside the form. Our file is in the page's head, so
theirs usually arrives later. Every selector inside a control starts with `:root`, which adds one pseudo-class of
specificity and makes the result independent of order. Six selectors needed one more class to win
a tie. django-tomselect and Tom Select mark some declarations `!important`: the clear button's colour
and opacity, and the margin of the input inside a control. Ours are important only where theirs
are.

The alternative, telling a developer to stop django-tomselect loading its stylesheets, would need a
setting django-tomselect does not have.

## R3. What the stylesheet has to undo (needs 3, 4, 11, 12)

Found by measuring the sketch in a browser:

- daisyUI's `.select` has `overflow: hidden`. The dropdown is inside the wrapper and was cut off.
- Tom Select's `.ts-wrapper` has `min-height: 36px`, which made the two smallest sizes taller than
  a stock select.
- Every wrapper is positioned, so a wrapper later in the page was drawn over an open dropdown.
  The open wrapper is given a `z-index`.
- Tom Select marks a fetching wrapper with the class `loading`. daisyUI's `loading` replaces the
  element with a spinner drawn as a mask. django-tomselect has a `loading_class` setting, but using
  it would be something a developer has to set, so the stylesheet undoes the mask on a wrapper
  instead and draws a small ring.
- django-tomselect hides its status element with `visually-hidden`, a Bootstrap class.

## R4. Grouping (need 5)

django-tomselect's `tomselect.html` has a `tomselect_render` block inside the Tom Select
configuration object. A template of the same name that extends it and adds `optgroupField` and
`optionGroupRegister` ahead of `{{ block.super }}` makes Tom Select group any option that carries
an `optgroup` key. Django's template loaders skip the origin already used, so the same name can
extend itself across application directories.

- The template is found ahead of django-tomselect's only when `mvp_forms` is listed before
  `django_tomselect` in `INSTALLED_APPS`. The other way round nothing breaks and nothing is
  grouped. The README has to state the order.
- A project that already has its own `django_tomselect/tomselect.html` keeps working where its
  template is found ahead of ours and extends the same name: in an application listed before
  `mvp_forms`, or in `DIRS` when the project's form renderer reads its templates setting.
- A developer names the group by returning `optgroup` on each result: from `hook_prepare_results`
  on a model view, from `get_iterable` on a view that answers from a list. That is the one
  documented place FR-020 asks for.
- An option with no `optgroup`, and every option of a control that names none, is listed as
  before: `optionGroupRegister` returns nothing for an empty value.
- django-tomselect never writes unselected options into the page, so "options that come with the
  page" are the chosen ones. They are in the control, not in the dropdown, unless the developer
  sets `hide_selected=False`. Whether a chosen option then appears under its group depends on
  django-tomselect sending the key with the selected values, which the build checks and reports.

Three checks the repository runs today name this file: no pack template may name a template that
is not under `daisyui/`, every distributed template is in the README's list, and every
distributed template can be replaced. Each is narrowed to the template pack's own directory and
gains its own statement for a supported package's directory. Rejected: a widget subclass (FR-009
forbids one), a script (the package ships none), and telling the developer to write the template
(FR-020).

## R5. htmx (need 6)

django-tomselect's inline script starts a control on `DOMContentLoaded` unless the field's
configuration has `use_htmx=True`, in which case it starts at once. After an htmx swap the first
never fires. `TOMSELECT = {"DEFAULT_CONFIG": {"use_htmx": True}}` in settings sets it for every
control and has no effect on a full page load other than starting the control sooner. Measured:
with it, a form fetched twice into the same target ends with one control for each field, and a
page reached by boosted navigation starts all of its controls. This is "what django-tomselect
already asks for" in FR-026, and the README says so.

## R6. Modal and table (need 7)

The dropdown is inside the wrapper, so in a `<dialog>` it is in the top layer with the modal.
daisyUI's `.modal-box` and the pack's `overflow-x-auto` around a table formset both scroll what
leaves them. `:has(.ts-wrapper.dropdown-active)` on each lets the box overflow while a dropdown in
it is open. `:has()` is in every browser daisyUI 5 supports. Moving the dropdown to `<body>` was
rejected: it would sit under the dialog.

## R7. What can be tested here, and what cannot

The suite renders templates in Python and has no browser. It can hold:

- the markup the pack writes on each of the four widgets, in each state, size, colour and variant
- the stylesheet as text: where each rule applies, that it names no colour, and that each state
  the specification lists has a rule
- contrast under `light` and `dark`, by reading the stylesheet's own declarations and resolving
  them with the colour arithmetic FS-012 added under `tests/legibility/`
- that the grouping template adds its two settings and changes nothing else
- that no module imports django-tomselect, and that the pack draws without it
- the demo pages as rendered

It cannot hold what a browser does with those rules: that a dropdown is on top, is not cut off in
a modal, or that a control starts after a swap. Those were measured once in a headless browser
during the sketch, by hit-testing every point of each open dropdown, and are laid out for the
maintainer to walk. Adding a browser to the suite and to CI for this feature is not proposed.

## R8. Versions

django-tomselect 2026.6.2 is the release installed. It declares Django up to 6.0. On Django 6.1
its controls work, and its `tomselect_media` template tag writes nothing and logs an error,
because form media holds objects where it expects strings. A host project on 6.1 loads its files through form media, which
django-crispy-forms writes, or links them by path. The README names the release tested and says
this.

## R9. What stays django-tomselect's

Seen in the browser and not changed: typed text staying in a multiple control after a pick, the
message a required single control gives when empty, and the Tab key stopping inside an open
dropdown. Each is recorded as an issue in this repository.

## R10. The constitution

The constitution says a rule is changed in its own pull request, before the work that depends on
it. Article XIV is therefore amended in a pull request of its own, and this feature merges after
it.
