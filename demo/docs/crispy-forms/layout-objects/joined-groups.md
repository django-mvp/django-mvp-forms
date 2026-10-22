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

## With text between the fields

A measurement and its uncertainty are written with a `±` between them. Put
django-crispy-forms' own `HTML` in the group where the text goes. It is drawn
in its place in the join, framed like the inputs beside it, and takes the
form's size, colour and variant for inputs, or those of a `Choice` around it.
The text is rendered with the form's context, as `HTML` is anywhere else.

```{live-example} /examples/joined-text/
:title: A measurement with its uncertainty

../../../examples/layout_objects/joined_text.py
```

A member must be an input or a select, a button must be a `StrictButton`,
`Submit`, `Button` or `Reset`, and text must be `HTML`. Anything else in the
group, such as a `Div`, raises `InvalidMember` when the form is drawn. A
`Choice` around text that states a label or a drawing raises `InvalidChoice`.
