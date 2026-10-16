# Partial date widgets

A [`PartialDateField`](../custom-fields/partial-date-field.md) is drawn as a
text input unless you give it a widget. There are three, and each reads the
field's `min_resolution`, `max_resolution`, `min_value` and `max_value`, so the
form and the browser agree on what is allowed. The field still cleans the value
and does the checking.

## One masked input

`PartialDateMaskInput` is one text input that puts the hyphens in as you type.
It needs IMask on the page, as the [input masks](input-masks.md) do. Type
`2001-02-3` and watch the mask refuse a day the month cannot have, then send
the form empty to see the required field's error.

```{live-example} /examples/partial-date-mask/
:title: Three fields, one masked input each

../../examples/custom_widgets/partial_date_mask.py
../../templates/demo/examples/masked_form.html
```

## A year, a month and a day

`PartialDateInput` draws three parts that make one value. The year is typed, and
the month and day open only once the part before is filled. A field with
`max_resolution="month"` is drawn with no day.

```{live-example} /examples/partial-date-input/
:title: The same three fields, as three parts

../../examples/custom_widgets/partial_date_input.py
```

## Three selects

`PartialDateSelect` is the same, with the year chosen from a list. The list runs
from the year of `max_value` back to the year of `min_value`, so the range on the
last field below limits what can be picked.

```{live-example} /examples/partial-date-select/
:title: The same three fields, as three selects

../../examples/custom_widgets/partial_date_select.py
```

| Widget | Needs | Best for |
| --- | --- | --- |
| `PartialDateMaskInput` | IMask | Typing a whole date quickly. |
| `PartialDateInput` | Nothing | Typed parts, with no list of years to scroll. |
| `PartialDateSelect` | Nothing | A short range of years, or a touch screen. |
