# Tabs

`TabHolder` and `Tab` put groups of fields behind daisyUI tabs. The whole form
is still one form: every tab is posted together.

Send the form empty. The first tab has no required field, so the form comes
back with the second tab open, where the first error is.

```{live-example} /examples/tabs/
:title: A profile in three tabs

../../../examples/layout_objects/tabs.py
```
