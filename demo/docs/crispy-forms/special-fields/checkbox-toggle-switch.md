# Checkbox, toggle and switch

A `BooleanField` is a checkbox unless you say otherwise. Ask for `toggle` or
`switch` with a `Choice`, either by the field's name in the helper's
`FormChoices` or around the field in the layout. Both do the same thing.

```{live-example} /examples/checkbox-toggle-switch/
:title: One kind of field, three drawings

../../../examples/special_fields/checkbox_toggle_switch.py
```

| Drawing | What it is |
| --- | --- |
| `checkbox` | daisyUI's `checkbox`. The default. |
| `toggle` | daisyUI's `toggle`, with its label beside it. |
| `switch` | A `toggle` with its label first and the control at the far end of the row. |

All three post the same value, and a required one fails the same way.
