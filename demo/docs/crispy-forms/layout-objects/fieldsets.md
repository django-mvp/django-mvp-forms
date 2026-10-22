# Fieldsets

`Fieldset` gathers fields under a legend. The pack draws it as a daisyUI
`fieldset` with a `fieldset-legend`, set out as a panel. django-crispy-forms'
own `Fieldset` from `crispy_forms.layout` is drawn the same way. The one in
`mvp_forms.layout` also takes a `description`, help text drawn before the first
field.

Fieldsets one after another are spaced apart. A fieldset can hold another, and
one with an empty legend is drawn as a panel with no heading.

Send the form empty. The required fields are drawn in error inside the fieldset
that holds them.

```{live-example} /examples/fieldsets/
:title: Two fieldsets, one holding another, and one with no legend

../../../examples/layout_objects/fieldsets.py
```

## Collapsible fieldsets

Import `Fieldset` from `mvp_forms.layout` to make one collapsible. Its legend
becomes the control that opens and closes it. `state` says how it is first
drawn, `"open"` or `"closed"`, and a collapsible fieldset with no state starts
closed. A fieldset that holds a field in error is drawn open, with a mark beside
its legend, whatever its state.

```python
Fieldset("Contact", "name", "email", collapsible=True, state="open")
```

Send the form empty. The billing address starts closed, and opens to show the
fields in error.

```{live-example} /examples/collapsible-fieldsets/
:title: An open fieldset, a closed one, and one closed until it holds an error

../../../examples/layout_objects/collapsible_fieldsets.py
```
