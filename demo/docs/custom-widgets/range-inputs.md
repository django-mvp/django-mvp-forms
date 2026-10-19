# Range inputs

`RangeInput`, `DateRangeInput` and `DateTimeRangeInput` draw a low and a high
end as one field: two inputs side by side under the field's label, each named
inside its frame. Either end can be left empty, so "at least 60" and "up to
2500" can both be written.

Give one to a field that takes a pair of values. With django-filter, pass it to a
range filter:

```python
import django_filters

from mvp_forms.widgets import DateRangeInput, RangeInput


class SiteFilter(django_filters.FilterSet):
    depth = django_filters.RangeFilter(widget=RangeInput())
    measured = django_filters.DateFromToRangeFilter(widget=DateRangeInput())
```

The widget takes a pair, or a `slice` as django-filter's range fields give it,
and sends back two values for the field to clean. In a plain form, use a
`MultiValueField` of two number or date fields, as the example below does.

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
depth = django_filters.RangeFilter(widget=RangeInput(joined=True))
```

```{live-example} /examples/range-input-joined/
:title: Joined ranges

../../examples/custom_widgets/range_input.py
```

## Compact

`compact=True` draws both ends in one input frame, with an en dash between them and
the ends' names as placeholders. `separator` changes the text between them, such
as `separator=_("to")`.

```python
depth = django_filters.RangeFilter(widget=RangeInput(compact=True))
measured = django_filters.DateFromToRangeFilter(
    widget=DateRangeInput(compact=True, separator=_("to"))
)
```

```{live-example} /examples/range-input-compact/
:title: Compact ranges

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
