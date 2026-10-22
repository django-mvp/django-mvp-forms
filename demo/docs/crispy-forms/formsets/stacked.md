# Stacked

With no template named on the helper, each form of the formset is drawn under
the last, as a panel, the way a `Fieldset` is drawn. The management form and
each form's delete checkbox are drawn for you.

```{live-example} /examples/formset-stacked/
:title: The lines of an order

../../../examples/formsets/stacked.py
../../../templates/demo/examples/formset.html
```

## A legend for each form

State a legend on the helper with `StackedForms`, set through `FormChoices`.
The legend is a template. It can use `number`, the form's place in the
formset counting from one, and `form`, the form itself.

```python
from mvp_forms.choices import FormChoices, StackedForms

helper.daisyui = FormChoices(forms=StackedForms(legend="Team member"))
```

```{live-example} /examples/formset-titled/
:title: Every form under the same legend

../../../examples/formsets/collapsible.py
```

## Collapsible forms

`collapsible=True` lets a person open and close each form by its legend, as a
collapsible fieldset is opened. `open=True` draws them open at first, and
without it they start closed. A form holding an error is drawn open, with a
mark beside its legend, whatever `open` says.

A legend taken from a value of the form names each one. Give a default for
the empty form at the end, which has no value yet.

```python
StackedForms(legend='{{ form.name.value|default:"New member" }}', collapsible=True)
```

```{live-example} /examples/formset-collapsible/
:title: Each member closed, under its own name

../../../examples/formsets/collapsible.py
```

Numbered by position, and open at first:

```python
StackedForms(legend="Member {{ number }}", collapsible=True, open=True)
```

```{live-example} /examples/formset-collapsible-numbered/
:title: Each member open, numbered

../../../examples/formsets/collapsible.py
```

Sent back with a mistyped email. The second member opens to show it.

```{live-example} /examples/formset-collapsible-error/
:title: A closed form drawn open to show its error

../../../examples/formsets/collapsible.py
```
