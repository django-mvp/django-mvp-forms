# Table

Name `daisyui/table_inline_formset.html` as the helper's `template` and the
same formset is drawn as a table: one row for each form, one column for each
field, with the labels as the column headings.

Send the form empty. An error sits in the row and cell it belongs to.

```{live-example} /examples/formset-table/
:title: The lines of an order as a table

../../../examples/formsets/table.py
```
