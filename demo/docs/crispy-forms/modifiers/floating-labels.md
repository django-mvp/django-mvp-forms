# Floating labels

A floating label sits inside the input while it is empty, then moves to the
border once the input is focused or holds a value. State it with
`label="floating"`, in `FormChoices` for the whole form or in a `Choice` for one
field.

## For the form

Focus a field to see its label move. While a required field is empty, its
required marker follows the label's text in the placeholder, and it moves to the
label when the label floats. Send the form empty to see the errors, which sit
below the fields as they do with ordinary labels.

```{live-example} /examples/floating-labels/
:title: A sign-in form with floating labels

../../../examples/modifiers/floating_labels.py
```

`notes` has `Choice(label=None)`, which takes the form's statement off that field
and gives it its ordinary label. The checkbox is passed over without an error.

## For one field

In a layout, wrap the field in a `Choice`.

```{live-example} /examples/floating-field/
:title: One floating label and one ordinary label

../../../examples/modifiers/floating_field.py
```

A floating label is for an input, a textarea or a select. The form's statement
is passed over for any other field, such as a checkbox, a radio group, a rating
or a field with attached text. The same statement on one of those fields raises
`InvalidChoice`. A disabled field keeps its ordinary label.
