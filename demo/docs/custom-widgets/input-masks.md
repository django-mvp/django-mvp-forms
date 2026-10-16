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

## A regular expression

`RegexMaskInput` accepts a character only while the whole value still matches
a regular expression. Use it where a field has a limited alphabet but no fixed
shape. IMask tests the value after every keystroke, so the expression has to
allow every partial value on the way: write `^\d{0,5}$`, not `^\d{5}$`, and let
the field decide that five digits were required. The expression is JavaScript's
dialect, and `flags` takes its flags as text.

```{live-example} /examples/regex-mask/
:title: Digits only and a hexadecimal colour

../../examples/custom_widgets/regex_mask.py
```

## Several masks

`DynamicMaskInput` takes a list of `PatternMaskInput`, `RegexMaskInput` and
`NumberMaskInput` widgets and applies the one that takes the most of what has
been typed. Use it for a value of more than one shape.

```{live-example} /examples/dynamic-mask/
:title: A phone number of seven or ten digits

../../examples/custom_widgets/dynamic_mask.py
```
