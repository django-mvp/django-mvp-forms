# Coordinate fields

`LatitudeField` and `LongitudeField` take a position in decimal degrees and
clean it to a `Decimal`. Their input refuses what the field would refuse as it
is typed: a value past 90 or 180, a decimal place too many, a second full stop
or a letter. `PointField` is the two together, and cleans the pair to WKT text
that a GeoDjango `PointField` takes.

```{live-example} /examples/coordinate-fields/
:title: Defaults, a narrowed range and a point

../../examples/custom_fields/coordinate_fields.py
```

| Option | What it does |
| --- | --- |
| `min_value`, `max_value` | The narrowest range accepted, inside -90 to 90 or -180 to 180. |
| `decimal_places` | The most decimal places accepted. Six by default. |

The input is masked with IMask, which the host project loads.
