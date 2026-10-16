# State

A field can be disabled, read-only or uneditable. The pack adds no class for
any of them, because daisyUI draws each look from the attribute.

## Disabled, read-only, help and errors

A disabled field has `disabled=True` in the form. The browser does not submit
it, and Django takes the field's initial value instead. A read-only field is the
browser's own `readonly` on the widget: the input is still submitted, and the
attribute works on text inputs and textareas only. Use `disabled` for anything
else.

Send the form empty. `reference` and `account` keep their values, `email` fails
because it is required, and `nickname` has no error.

```{live-example} /examples/state/
:title: A disabled field, a read-only field, help text and an error

../../../examples/modifiers/state.py
```

## Uneditable

`UneditableField` shows a field's value with the input disabled, without
changing the field in the form. The browser does not submit a disabled input, so
a required field wrapped in it fails with `required`. To keep the value, declare
the field `disabled=True` in the form class, as `reference` is here.

Send the form. `account` fails, because it was not sent back. `reference` is
kept.

```{live-example} /examples/uneditable-field/
:title: Two uneditable fields

../../../examples/modifiers/uneditable_field.py
```
