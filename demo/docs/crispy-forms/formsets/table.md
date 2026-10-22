# Table

Name `daisyui/table_inline_formset.html` as the helper's `template` and the
same formset is drawn as a table: one row for each form, one column for each
field, with the labels as the column headings. The table is drawn in a panel,
the way a `Fieldset` is drawn.

Send the form empty. An error sits in the row and cell it belongs to.

```{live-example} /examples/formset-table/
:title: The lines of an order as a table

../../../examples/formsets/table.py
```

## A legend for the table

State a legend on the helper with `TablePanel`, set through `FormChoices`. The
legend is a template, and it can use `formset`.

```python
from mvp_forms.choices import FormChoices, TablePanel

helper.daisyui = FormChoices(table=TablePanel(legend="Order lines"))
```

```{live-example} /examples/formset-table-titled/
:title: The table under a legend

../../../examples/formsets/table.py
```

## A collapsible table

Every form stays one row, so it is the whole table that opens and closes, by
its legend. `open=True` draws it open at first, and without it the table
starts closed. A table holding an error in any row is drawn open, with a mark
beside its legend, whatever `open` says.

```python
TablePanel(
    legend="Order lines ({{ formset.initial_form_count }})",
    collapsible=True,
)
```

```{live-example} /examples/formset-table-collapsible/
:title: The table closed, with how many lines it holds

../../../examples/formsets/table.py
```

Sent back with no quantity on the second line. The table opens to show it.

```{live-example} /examples/formset-table-collapsible-error/
:title: A closed table drawn open to show its error

../../../examples/formsets/table.py
```
