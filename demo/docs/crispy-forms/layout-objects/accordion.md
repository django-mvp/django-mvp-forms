# Accordion

`Accordion` and `AccordionGroup` stack groups of fields that open and close.
They are the browser's own `<details>`, so they need no script. Both come from
`crispy_forms.bootstrap`.

Send the form empty. Only the last group has a required field, so it opens.

```{live-example} /examples/accordion/
:title: Three groups, the last with the error

../../../examples/layout_objects/accordion.py
```

`active` states which group starts open, whatever its place in the stack. Here
the first group is closed and the second open.

```{live-example} /examples/accordion-chosen/
:title: A group opened by choice

../../../examples/layout_objects/accordion.py
```
