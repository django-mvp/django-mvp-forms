# ADR 0010 — Class names written for other packs are dropped by name

**Status:** accepted

## Decision

The filter `daisyui_classes` in `mvp_forms/templatetags/daisyui.py` removes the names in
`UPSTREAM_ONLY_CLASSES` from a class string and removes repeats. The names are `btn-inverse`,
`ctrlHolder`, `blockLabel` and `error`. The templates for `Submit`, `Reset`, `Button` and
`MultiField` pass django-crispy-forms' class strings through it.

The buttons keep `btn`, and a `Submit` keeps `btn-primary`. django-crispy-forms writes both
itself and daisyUI defines both. The pack does not add them.

A `Hidden` is drawn with no `class` and no `id`. An id or any other attribute passed to it as a
keyword argument is kept.

A later feature whose layout object arrives with a class daisyUI does not define adds the name to
`UPSTREAM_ONLY_CLASSES`.

## Why

django-crispy-forms sets default classes in Python, written for Bootstrap and uni-form, and joins
the developer's `css_class` onto the same string. A template cannot tell the two apart, so the
only way to leave out a default is to name it. ADR 0008 rules out subclassing the layout objects
to change the defaults.

Three of the four buttons already come out as daisyUI buttons because Bootstrap and daisyUI share
the names `btn` and `btn-primary`. The button tests assert `btn`, so a release of
django-crispy-forms that changes its defaults fails them.

`MultiField` appends `error` to its own class each time it is drawn with a failing field, so the
same layout drawn twice carries the name twice. Dropping repeats covers that.

`Hidden` is given the class `hidden` and a generated id that is stored where a developer's own id
would be. The class does nothing on an input that is already hidden, and the two ids cannot be
told apart.

## Revisit if

django-crispy-forms separates its default classes from the developer's, or daisyUI starts
defining one of the dropped names.
