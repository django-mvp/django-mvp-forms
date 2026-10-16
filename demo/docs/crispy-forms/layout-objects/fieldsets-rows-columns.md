# Fieldsets, rows and columns

`Fieldset`, `Row`, `Column` and `Div` group fields and set them out on the page.
`HTML` puts a piece of markup between them. All five come from
`crispy_forms.layout`, and the pack draws them as daisyUI.

Send the form empty. Every field is required, and each error is drawn inside the
container that holds its field.

```{live-example} /examples/fieldsets-rows-columns/
:title: A fieldset with a row, a note and a div

../../../examples/layout_objects/fieldsets_rows_columns.py
```

## Buttons

`Submit`, `Reset` and `Button` are inputs of type `submit`, `reset` and `button`.
`ButtonHolder` and `FormActions` keep them together. A `Row` can also hold field
names directly, without a `Column` around each.

Press "Start again" to put back what a field held when the page was drawn.

```{live-example} /examples/button-holder/
:title: Two fields in a row, then a button holder

../../../examples/layout_objects/buttons.py
```

`FormActions` is the same idea and also takes a plain `Button`.

```{live-example} /examples/form-actions/
:title: A submit, a reset and a plain button in form actions

../../../examples/layout_objects/buttons.py
```
