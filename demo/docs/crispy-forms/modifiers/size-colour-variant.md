# Size, colour and variant

daisyUI gives every input a size, a colour and a variant. State one for the
whole form in `FormChoices`, and every input that has it takes it. A `Choice`
for one field overrides the form.

All three examples draw the same five fields from `base.py`.

## Size

`xs`, `sm`, `md`, `lg` or `xl`. Buttons follow the form's size.

```{live-example} /examples/size/
:title: A small form with large notes

../../../examples/modifiers/size.py
../../../examples/modifiers/base.py
```

## Colour

`neutral`, `primary`, `secondary`, `accent`, `info`, `success`, `warning` or
`error`. Buttons take a colour of their own with `button_color`. `None` for one
field takes the form's colour off it.

```{live-example} /examples/colour/
:title: Primary inputs and a secondary button

../../../examples/modifiers/colour.py
../../../examples/modifiers/base.py
```

## Variant

Inputs have one variant, `ghost`. Buttons have `outline`, `soft`, `dash`,
`ghost` and `link`, stated with `button_variant`.

```{live-example} /examples/variant/
:title: Ghost inputs and an outline button

../../../examples/modifiers/variant.py
../../../examples/modifiers/base.py
```
