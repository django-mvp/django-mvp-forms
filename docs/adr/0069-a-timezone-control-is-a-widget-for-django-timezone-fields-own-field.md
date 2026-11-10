# ADR 0069 — A timezone control is a widget for django-timezone-field's own field

**Status:** accepted

## Decision

The package draws a timezone choice with one widget, `mvp_forms.widgets.TimeZoneSelect`, a
subclass of `TomSelect`. A form names it on django-timezone-field's `TimeZoneFormField`:

```python
timezone = TimeZoneFormField(widget=TimeZoneSelect)
```

The field keeps its choices, its validation and its cleaning. The widget changes only how the
options are drawn. It groups each choice by the part of its value before the first slash, puts
the regions in alphabetical order and lists a value with no slash, such as `UTC`, under
"Other", last. It keeps each option's label, leaves an empty choice first and outside every
group, and draws choices already in groups as they are.

No module of the package imports django-timezone-field, as [ADR 0053](0053-a-supported-packages-widget-keeps-its-own-layout.md)
has it for every supported package. The `timezone` extra names the release the widget is tested
against, so a project that wants the control depends on `django-mvp-forms[timezone]`.

## Why

Grouping is about how the options are drawn and not about which value is valid, and a widget is
how Django changes how a field is drawn. [ADR 0048](0048-a-field-owns-the-rule-and-every-option.md)
gives the rule to the field, and here the field is django-timezone-field's.

A field of the package's own, subclassing `TimeZoneFormField`, would have to import
django-timezone-field, so the package would need a module that fails without it. It would stand
between the developer and the field django-timezone-field documents, and a model's
`TimeZoneField` would still give a model form django-timezone-field's field, so the widget would
be needed there in any case.

Grouping the field's own choices, rather than a list the widget builds from `zoneinfo`, keeps
whatever the developer gave the field: a shorter list of timezones, or labels with each offset
from GMT.

## Revisit if

django-timezone-field groups its choices itself, or a second supported package needs a module
that imports it.
