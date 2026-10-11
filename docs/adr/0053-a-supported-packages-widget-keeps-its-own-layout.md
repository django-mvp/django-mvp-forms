# ADR 0053 — A supported package's widget keeps the layout its own package gives it

**Status:** accepted

## Decision

Where a supported package's widget arranges its own parts, and the package gives the developer a
documented way to change that arrangement, the pack does not rearrange them. It draws the parts it
has a daisyUI class for and the README shows the developer's route.

The first case is django-countries' `CountrySelectWidget`. The pack writes daisyUI's `select`
class on its select, with the size, colour, variant and error state, as for any select. The flag
image is placed by the widget's `layout` argument, which is django-countries' own. The README
gives the one `layout` that sits the flag beside the select, and the demo page uses it.

No module of the package recognises a supported package's class, by import or by name.

## Why

`CountrySelectWidget` writes its flag after its select. The field frame is a one-column grid
(ADR 0007), so with django-countries' own layout the flag sits on a line of its own
([issue #72](https://github.com/django-mvp/django-mvp-forms/issues/72)).

Having the pack put the two in a row was built and taken out. The widget draws itself from a
format string and has no template the pack could stand in for (ADR 0012), so the pack had to
recognise the class by its dotted name, since it may not import django-countries, compare the
widget's layout with a fresh instance's on every draw, and rewrite the string on a copy. It would
have stopped without a word if django-countries renamed the class or the attribute. And it left
the flag 3 pixels off centre, because the inline margin in django-countries' layout cannot be
undone by a class.

The `layout` argument does the whole job in one line of the developer's own code, centres the
flag, and is the route django-countries documents. A plain route a Django developer already has
is preferred to a mechanism of the pack's.

## Revisit if

A supported package's widget is drawn badly and its package gives the developer no way to change
it, or django-countries draws the widget from a template the pack could extend.
