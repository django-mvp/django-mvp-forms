# Alert

`Alert` draws a daisyUI alert between fields. It comes from
`crispy_forms.bootstrap`. It has a dismiss button unless you pass
`dismiss=False`, and a daisyUI colour such as `alert-success` in `css_class`.

Dismiss the first alert, then send the form empty. The alerts are drawn again
with the page, because a dismissal is not remembered.

```{live-example} /examples/alert/
:title: A dismissible alert, a permanent one and a coloured one

../../../examples/layout_objects/alert.py
```
