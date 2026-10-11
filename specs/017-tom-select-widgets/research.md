# Research: Tom Select widgets for choice fields

Read against `main` at `11c7f66` on 2026-10-12. The specification has no planning notes and the
feature has no sketch, so everything here is what the plan needs settled.

## R1. How the pack draws a subclass of `Select`

`mvp_forms/templatetags/daisyui.py` maps `forms.Select` to the `select` component and finds a
widget's component through its classes, so a subclass of `Select` or `SelectMultiple` is drawn
with `select`, `w-full`, the stated size, colour and variant, and `select-error` on a field in
error. The pack needs no change for the two widgets to be drawn as its own.

## R2. Tom Select builds the control the stylesheet already styles

The stylesheets django-tomselect 2026.6.2 carries are Tom Select 2.5.2's. Tom Select copies the classes of
the select it replaces to the wrapper it builds, and does not copy them to the dropdown
(`copyClassesToDropdown` is off by default). Every selector in `mvp_forms/tomselect.css` is
written against `.ts-wrapper`, `.ts-control` and `.ts-dropdown`, with three named exceptions, and
none names anything django-tomselect adds except the element it announces a choice in. A control
started on a plain select therefore meets the same rules. The stylesheet already has rules for
the clear button, the remove button, group headings, an option with `aria-disabled`, and a modal
or scrolling box that holds an open control.

## R3. What Tom Select does with a select element on its own

- It reads the options, their groups and their `disabled` attribute from the select. An option
  group becomes a heading and a disabled option is listed with `aria-disabled` and cannot be
  chosen.
- It offers at most 50 options by default (`maxOptions: 50`). The script sets it to `null`, or a
  field with more options than that could not show them all (FR-005).
- With `allowEmptyOption` off, which is the default, an option with an empty value is not listed
  and its text becomes the placeholder when none is stated. Django's empty choice on an optional
  single select is that option, so the field can be emptied and reads `---------` while empty.
- It moves the label's `for` to the control's own input and names the control with the label.
- It escapes an option's label in its default drawing.
- It takes `maxItems` from the select: one for a single select and no limit for a multiple one.
- It sets `select.tomselect` to the instance, which is how the script knows a select is started.
- `clear_button` and `remove_button` are plugins. The complete build of Tom Select and
  django-tomselect's bundle both carry them. Tom Select's base build does not.

## R4. django-tomselect's script puts Tom Select on the page

`django_tomselect/js/django-tomselect.min.js` assigns `window.TomSelect`. A page that loads it
has a Tom Select with both plugins, so the package's script needs nothing else there. This is
proved by a browser test against the installed django-tomselect, and the README names the
release it was proved on.

## R5. How rows are added to a formset

django-mvp's `formset.js` keeps the empty form in a `<template>`, replaces `__prefix__` in its
markup and inserts the result. A template's content is inert, so a script looking for selects
never finds the one inside it, and the inserted row holds a select no control was started on.
Watching for added nodes is enough. A script that copies a row whose control has started copies
Tom Select's wrapper with it. That is not supported, and the README says to copy the empty form.

## R6. How the script is tested

ADR 0046 holds: the script is tested in Chrome through Playwright, marked `e2e`, with the library
served from a copy under `tests/data/` by answering the page's request. Tom Select 2.5.2's
complete build is 51 kB and is added there as `tom-select-2.5.2.complete.min.js`. It is not part
of the wheel or the sdist. The tests assert what this package's script does and never Tom
Select's own behaviour beyond what shows the settings arrived.

## R7. The constitution and ADR 0042

Article XIV allows one optional stylesheet for a supported package, which "styles that package's
controls and nothing else". The maintainer approved drawing these widgets with the same file.
The controls it styles are Tom Select's in both cases. The constitution is amended in a pull
request of its own and never in the middle of the work it affects, so the one sentence saying
the package's own Tom Select widgets are drawn by the stylesheet shipped for django-tomselect
goes to the maintainer separately and merges before this feature. ADR 0042 is rewritten here to
match. No second stylesheet exists and no project pays for a file
it does not use, which is what the article protects.

## R8. Guards already in the suite that this feature meets

- `tests/test_pack/test_independence.py` fails if a module of the package imports
  django-tomselect.
- `tests/test_pack/test_independence.py` lists the package's static files.
- `tests/test_pack/test_documented_examples.py` runs the README's examples.
- `tests/tomselect_stylesheet.py` and the legibility tests read `mvp_forms/tomselect.css`.

## R9. No new dependency

Tom Select is not a Python package and is loaded by the host project. django-tomselect stays a
development dependency for the demo and the tests.
