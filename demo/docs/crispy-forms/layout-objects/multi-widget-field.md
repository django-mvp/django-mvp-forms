# Multi-widget field

`MultiWidgetField` draws a field whose widget is several widgets, such as a
`SplitDateTimeField`, and gives each part attributes of its own. It comes from
`crispy_forms.layout`. A split field with no layout object is drawn the same
way, without the attributes.

Look at the placeholders in the start's two inputs, then send the form empty.
The start is required and the end is not.

```{live-example} /examples/multi-widget-field/
:title: A start with a placeholder on each part

../../../examples/layout_objects/multi_widget_field.py
```
