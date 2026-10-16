# Inline field

`InlineField` draws a field with no visible label, for a form that sits in a
line such as a search bar. The label is not lost: it names the input for
assistive technology, and a text input shows it as its placeholder.

Send the form empty. The error and the help text still appear, and a field next
to the inline ones keeps its label.

```{live-example} /examples/inline-field/
:title: A search box and a checkbox without labels

../../../examples/modifiers/inline_field.py
```

A single checkbox keeps the label it sits in. A select is named by its
`aria-label` and gets no placeholder.
