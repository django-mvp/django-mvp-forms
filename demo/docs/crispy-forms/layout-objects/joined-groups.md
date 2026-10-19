# Joined groups

`Join` draws several fields as one daisyUI join under a single label, such as a
country code beside a number. It comes from `mvp_forms.layout`. A member keeps
its own help text and errors, and a `Field` gives a member attributes.

Pick a code, leave the number empty and send the form. The error is on the
number alone.

```{live-example} /examples/joined-groups/
:title: A phone number in two parts

../../../examples/layout_objects/joined_groups.py
```

## With a button

A group can hold buttons as well as fields, so a select, a text input and a
button make one search bar. The button takes the form's size, colour and
variant for buttons, here the primary colour, and is drawn as one piece with
the inputs.

Send the form with no words to see the error on the text input alone.

```{live-example} /examples/joined-search/
:title: A search bar

../../../examples/layout_objects/joined_search.py
```

A member must be an input or a select, and a button must be a `StrictButton`,
`Submit`, `Button` or `Reset`. Anything else in the group, such as a `Div`,
raises `InvalidMember` when the form is drawn.
