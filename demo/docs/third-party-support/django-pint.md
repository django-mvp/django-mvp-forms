# django-pint

[django-pint](https://github.com/CarliJoy/django-pint) stores a physical
quantity, a number with its unit, and converts between units for you. Its form
fields, `QuantityFormField`, `IntegerQuantityFormField` and
`DecimalQuantityFormField`, draw the number and the unit with one widget,
`QuantityWidget`, which is a `MultiWidget` of a number input and a select. The
pack draws them with nothing added: there is no widget to swap and no setting to
change.

## The number and its unit, joined

The number and the unit read as one value, so the pack draws them as one
daisyUI `join`. The number fills the row and the unit select is as wide as its
longest unit. A size, a colour, a variant and an error reach both parts.

The form arrives already sent: the weight is required and was left empty, the
depth has a value and the dose is optional.
Send it again with a weight in pounds and the form accepts it. django-pint
converts it to the field's base unit when it cleans.

```{live-example} /examples/pint/
:title: A required weight, a depth with a value and an optional dose

../../examples/third_party/pint.py
```

```{live-example} /examples/pint-disabled/
:title: A disabled weight

../../examples/third_party/pint.py
```

A disabled quantity field cannot be sent. Django cleans a disabled field from
its initial value, and django-pint's field cannot clean a quantity it was given
as one, so the form fails with "Enter a number." Send this form to see it.

```{live-example} /examples/pint-sizes/
:title: The five sizes

../../examples/third_party/pint.py
```

## Naming the unit

Each part of a multi-widget is named by the field's label, so a screen reader
reads the number and the unit both as "Weight". django-crispy-forms'
`MultiWidgetField` gives each part its own attributes, which is how a form names
the unit.

```{live-example} /examples/pint-named-unit/
:title: A weight whose unit is named

../../examples/third_party/pint.py
```

## Before: each part on its own line

How the pack drew the same forms before the parts were joined, for comparison.
The number and the unit each fill the row, one above the other, and the unit
select is as wide as the number.

```{live-example} /examples/pint-today/
:title: The same form, unjoined

../../examples/third_party/pint.py
```

```{live-example} /examples/pint-today-disabled/
:title: A disabled weight, unjoined

../../examples/third_party/pint.py
```

```{live-example} /examples/pint-today-sizes/
:title: The five sizes, unjoined

../../examples/third_party/pint.py
```
