# Accordion

`Accordion` and `AccordionGroup` stack groups of fields that open and close.
They are the browser's own `<details>`, so they need no script. Both come from
`crispy_forms.bootstrap`.

Send the form empty. The second and third groups have required fields, so the
second opens. Both headings carry a dot in the error colour, and a screen reader says the group
contains a field with an error.

```{live-example} /examples/accordion/
:title: Three groups, two with an error

../../../examples/layout_objects/accordion.py
```

`active` states which group starts open, whatever its place in the stack. Here
the first group is closed and the second open.

```{live-example} /examples/accordion-chosen/
:title: A group opened by choice

../../../examples/layout_objects/accordion.py
```
