# ADR 0024 — The frame takes a wrapper class from the context

**Status:** accepted. Amends [ADR 0006](0006-the-field-frame.md)

## Decision

`daisyui_field` reads `wrapper_class` from the template context and the frame writes it as a
class on its outer element, after `fieldset`. This is what django-crispy-forms documents for the
`wrapper_class` argument of `Field` and of the layout objects built on it.

The frame still reads no name that becomes an element or raw markup.

## Why

django-crispy-forms hands the value to the template as a bare context name and by no other
route. It flattens the context before the template sees it, the layout object is not in it, and
a `Field` adds the name only when it was given one. So the template cannot tell a layout's
`wrapper_class` from a page variable of the same name.

ADR 0006 refused bare names because of `tag`, which other packs use as an element name, so a
page variable could turn into markup. A class is written inside an attribute and escaped. The
worst a page variable called `wrapper_class` can do is add a class to every field's frame.

Refusing it would leave a documented argument of eight layout objects doing nothing.

## Revisit if

django-crispy-forms passes the layout object to the field template, which would give a route
that reads no bare name.
