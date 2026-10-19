# Range inputs

`RangeInput`, `DateRangeInput` and `DateTimeRangeInput` draw a low and a high
end as one field: two inputs side by side under the field's label, each named
inside its frame. Either end can be left empty, so "at least 60" and "up to
2500" can both be written.

Give one to any field that takes a pair of values, such as a `MultiValueField`
of two number or date fields. The widget takes the pair, or a `slice` as
django-filter's range fields give it, and sends back two values for the field
to clean. The example below builds its own pair field in a few lines.

```{live-example} /examples/range-input/
:title: Depths, dates and times

../../examples/custom_widgets/range_input.py
```

The depth holds both ends and the heat flow only its low end. Send the form with
the measured dates empty to see the error on both ends, or put the low depth
above the high one. On a narrow screen the two ends stack.

## Joined in one row

`joined=True` draws the two ends as one daisyUI join. They share a border and
stay in one row at every width, where the separate ends stack on a narrow
screen.

```python
depth = DepthField(widget=RangeInput(joined=True))
```

```{live-example} /examples/range-input-joined/
:title: Joined ranges

../../examples/custom_widgets/range_input.py
```

## Size and colour

The ends take the form's size and colour, as every other input does.

```{live-example} /examples/range-input-small/
:title: Small ranges, one in the primary colour

../../examples/custom_widgets/range_input.py
```

## With no label above it

In a form that draws no labels, such as a row of filters above a list, the
field's label moves into the first frame and the names of the two ends become
the inputs' placeholders. See [Tom Select](tom-select.md)
for the whole row.
