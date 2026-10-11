# ADR 0052 — django-countries' flag widget is drawn in a row with its flag

**Status:** accepted

## Decision

A field whose widget is django-countries' `CountrySelectWidget`, or a subclass of it, is drawn
from a copy of the widget whose layout is wrapped in `<div class="flex items-center gap-2">`. The
select and the flag are then side by side inside the field frame, and the select takes the width
the flag leaves.

- The widget is recognised by the dotted name of its class,
  `django_countries.widgets.CountrySelectWidget`, read from the classes the widget inherits from.
  No module of the package imports django-countries.
- The row is written only while the widget holds django-countries' own layout. A widget given a
  `layout` of the developer's is drawn as written.
- The row is written only for a field that stands alone in its frame. A field with attached text,
  joined buttons or a floating label, and a member of a `Join`, is drawn as it was.
- The field's own widget is never changed (ADR 0004). The copy lasts for one render.
- `items-center` is named in `LAYOUT_UTILITIES` in `tests/test_pack/test_independence.py`, as
  ADR 0003 asks. `flex` and `gap-2` were there already.

The flag image, its `id`, its inline `style` and the `onchange` handler on the select are
django-countries' own and are left as they are. django-countries is a development dependency,
for the tests and the demo page, and never a runtime one.

## Why

The field frame is a one-column grid (ADR 0007), and `CountrySelectWidget` writes its flag as a
second element after the select, so the flag fell onto a row of its own under a full-width
select. It read as a stray image and not as part of the control
([issue #72](https://github.com/django-mvp/django-mvp-forms/issues/72)).

The widget draws itself in `render()` from a format string, `layout`, and has no template the
pack could stand in for (ADR 0012). The string is the one place the select and the flag can be
given a shared parent, so the copy's string is wrapped. Three other routes were weighed:

- A branch in `daisyui/field_body.html` would add a name to what that template is handed, which
  is public (ADR 0029), for the sake of one widget of one package.
- Importing the class to test for it would make django-countries something the package reaches
  for, and a project without it would need the import guarded.
- Replacing the layout with one of the pack's own would centre the flag exactly, by leaving out
  django-countries' inline margin. It would also restate the image's `id` and class, which the
  widget's handler depends on, and have to follow them from release to release.

A layout the developer wrote is left alone for the reason a widget that names its own template
is: the developer has said how it is drawn. Wrapping it would also change it, because a block
element written around the select would become a flex item and lose its width.

`flex`, `items-center` and `gap-2` are in Tailwind's browser build and in the stylesheet
django-mvp ships, which is the ground ADR 0009 chose its utilities on. Without `items-center` a
flex row stretches the image to the height of the select.

No stylesheet is involved. ADR 0042 allows one only for controls built in the browser, and this
one is drawn on the server.

Measured in Chromium against the demo page, inside the django-mvp shell and on daisyUI's CDN
build: the flag sits to the right of the select on the same row at 1280 and at 390 pixels, the
page does not scroll sideways, and the flag's middle is 3 pixels below the select's. That offset
is django-countries' inline `margin: 6px 4px 0`, which no class can undo without `!important`.

## Revisit if

django-countries draws the widget from a template, drops the inline margin, or renames the class
or its `layout`. Or a second supported package needs its widget recognised by name, which is
when this becomes a table and not one name.
