# Partial date field

`PartialDateField` is for a date that may be known only to the year or the
month: a sample collected "in June 2019", a paper published "in 2004". It cleans
to ISO text, `2019`, `2019-06` or `2019-06-14`, so you can keep it in a
`CharField` and it still sorts in date order.

```{live-example} /examples/partial-date-field/
:title: Four fields, four rules

../../examples/custom_fields/partial_date_field.py
```

| Option | What it does |
| --- | --- |
| `min_resolution` | The least that must be given: `year` (the default), `month` or `day`. |
| `max_resolution` | The most that may be given: `year`, `month` or `day` (the default). |
| `min_value`, `max_value` | The earliest and latest date accepted, as a partial date or a Python `date`. |

The field is drawn here with a plain text input. The
[partial date widgets](../custom-widgets/partial-date-widgets.md) give it a
masked input, three boxes or three selects.
