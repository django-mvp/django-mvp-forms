# Attached text and buttons

Text or a button is attached to the edge of an input with a `Join` of one field,
from `mvp_forms.layout`. Put `HTML` before the field, after it or on both sides
for a currency or a unit, and a button after it for a search box. The field
keeps its own label, help text and errors, as it has anywhere else.

## Text before and after

The text is rendered as `HTML` is anywhere else, markup and the form's context
included, so escape anything a person typed before you put it in.

Send the form empty to see all three fields in error with the text still
attached, then enter some numbers.

```{live-example} /examples/attached-text/
:title: A price, a weight and a budget

../../../examples/modifiers/attached_text.py
```

## Buttons

A button goes in the group in its place, as a `StrictButton`, `Submit`, `Button`
or `Reset`, and is drawn as one piece with the input.

Send an empty search to see the error, then type something.

```{live-example} /examples/field-with-buttons/
:title: A search box with a button

../../../examples/modifiers/field_with_buttons.py
```

The input, the text and the buttons take the form's size. A `Choice` around the
`Join` states a size for all of them at once.

## Before this

`PrependedText`, `AppendedText`, `PrependedAppendedText` and `FieldWithButtons`
from django-crispy-forms are deprecated. They are still drawn in this version,
with a `DeprecationWarning`, and stop being drawn in the next minor version.
`PrependedText("amount", "$")` becomes `Join(HTML("$"), "amount")`, and
`FieldWithButtons("query", StrictButton("Go"))` becomes
`Join("query", StrictButton("Go"))`.
