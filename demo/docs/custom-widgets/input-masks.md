# Input masks

A mask widget is a text input that only accepts what fits. Each one is a
`TextInput` with its options written on it, which
[IMask](https://imask.js.org/) reads in the browser. Your project loads IMask
itself, and the widget brings the small script that starts it.

Masking helps the person typing. It is not validation: the field still decides
what is accepted.

## A pattern

`PatternMaskInput` takes IMask's pattern text. `0` is a digit, `a` is a letter
and `*` is anything.

```{live-example} /examples/pattern-mask/
:title: Phone, postcode and licence key

../../examples/custom_widgets/pattern_mask.py
../../templates/demo/examples/masked_form.html
```

## A number

`NumberMaskInput` formats a number as it is typed and hands the field a plain
one, so a `DecimalField` cleans it without knowing a mask was there.

```{live-example} /examples/number-mask/
:title: An amount and a quantity

../../examples/custom_widgets/number_mask.py
```

## The other two

`RegexMaskInput` accepts a character only while the value still matches a
regular expression. `DynamicMaskInput` takes a list of masks and applies the one
that fits best.

:::{note}
Their examples are not written yet.
:::
