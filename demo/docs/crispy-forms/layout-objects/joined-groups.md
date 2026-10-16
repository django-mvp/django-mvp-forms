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

A member must be an input or a select. Anything else in the group, such as a
`Div`, raises `InvalidMember` when the form is drawn.
