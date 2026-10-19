# Tabs

`TabHolder` and `Tab` put groups of fields behind daisyUI tabs. The whole form
is still one form: every tab is posted together.

Send the form empty. The first tab has no required field, so the form comes
back with the second tab open, where the first error is. The second and third
tabs both hold an error, so both labels carry a dot in the error colour, and a screen reader
says the tab contains a field with an error.

```{live-example} /examples/tabs/
:title: A profile in three tabs

../../../examples/layout_objects/tabs.py
```

The same marks work for tabs and accordion groups in one form. This one arrives
as if it had been sent empty, with errors in two tabs and two groups.

```{live-example} /examples/marked-errors/
:title: Errors in two tabs and two groups

../../../examples/layout_objects/marked_errors.py
```
