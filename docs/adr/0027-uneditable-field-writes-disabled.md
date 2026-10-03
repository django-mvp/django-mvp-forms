# ADR 0027 — UneditableField is the one case where the pack writes disabled

**Status:** accepted. Amends [ADR 0013](0013-disabled-and-read-only-are-drawn-from-the-attribute.md), which said the pack adds no attribute for the disabled state

## Decision

`UneditableField` draws its field with the `disabled` attribute, for that render only. The pack
passes the attribute to the widget when it draws it. The form field's `disabled` argument and
the widget's own attributes are not changed.

It adds no class. How a disabled input looks is still drawn from the attribute, as ADR 0013 has
it. Everywhere else the state comes from the form field.

The form field is not disabled, so the browser leaves the value out of the submission and Django
validates what is left. The README says a form that needs the value kept declares the field
disabled in the form class.

## Why

django-crispy-forms documents `UneditableField` as drawing a disabled field, and the layout
object has no other way to say so than its template.

Read-only was rejected. It means nothing on a select, a checkbox or a radio, so the result would
differ by widget. A read-only input also suggests the value is protected, when only a field
declared disabled in the form refuses a changed value.

Setting `disabled` on the form field from a template would change validation from inside
rendering, behind the developer's back.

## Revisit if

django-crispy-forms changes what it documents for `UneditableField`.
