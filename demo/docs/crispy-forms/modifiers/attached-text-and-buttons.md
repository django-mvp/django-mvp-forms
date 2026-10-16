# Attached text and buttons

Some layout objects attach something to the edge of an input. `PrependedText`,
`AppendedText` and `PrependedAppendedText` put text before it, after it, or
both, such as a currency or a unit. `FieldWithButtons` joins buttons to it, such
as a search box with a button beside it.

## Text before and after

The text is markup, written into the page as it is, so escape anything a person
typed before you pass it in.

Send the form empty to see all three fields in error with the text still
attached, then enter some numbers.

```{live-example} /examples/attached-text/
:title: A price, a weight and a budget

../../../examples/modifiers/attached_text.py
```

## Buttons

`FieldWithButtons` takes the field first and then any number of buttons. Give
each button `join-item` so the borders where the parts meet are not doubled.

Send an empty search to see the error, then type something.

```{live-example} /examples/field-with-buttons/
:title: A search box with a button

../../../examples/modifiers/field_with_buttons.py
```

The input and the buttons share one size. State it for the whole form, or put a
`Choice` around the `FieldWithButtons`: a size stated for the field by name does
not reach its buttons.
