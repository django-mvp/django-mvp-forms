# Standard fields

This is a plain Django form. It has no helper, no layout and no widget from this
package. Every field is drawn by the pack from the widget Django gave it.

Send it empty to see how each kind of field shows an error.

```{live-example} /examples/standard-fields/
:title: Every standard field

../../examples/standard_fields.py
../../templates/demo/examples/plain_form.html
```

## What each field becomes

| Django widget | daisyUI component |
| --- | --- |
| `TextInput`, `EmailInput`, `URLInput`, `NumberInput`, `PasswordInput`, `DateInput`, `TimeInput`, `SearchInput`, `TelInput`, `ColorInput` | `input` |
| `Textarea` | `textarea` |
| `Select`, `SelectMultiple`, `NullBooleanSelect`, `SelectDateWidget` | `select` |
| `RadioSelect` | a group of `radio` |
| `CheckboxInput` | `checkbox` |
| `CheckboxSelectMultiple` | a group of `checkbox` |
| `FileInput`, `ClearableFileInput` | `file-input` |

A label, help text, the required mark and errors are drawn the same way around
every one of them.
