# Rating and range

A field that holds one choice can be drawn as a row of stars, one for each
choice, and a number field can be drawn as a slider. Ask for either with a
`Choice` and `drawing="rating"` or `drawing="range"`.

A star is a radio input, so the form receives the value of the choice picked,
just as it would from a select. A slider always sends a number.

Pick a star, move the slider and send the form. Clear `comfort` with the first
choice, "No answer", which is not drawn as a star.

```{live-example} /examples/rating-and-range/
:title: Two ratings and a range

../../../examples/special_fields/rating_and_range.py
```

`score` is a rating by its name in the helper's `FormChoices`, and `comfort` is
one in the layout. `volume` is a range in the layout, from 0 to 100 in steps of
5, with a colour of its own. Both kinds take the form's colour and size, and
neither has a variant.

| Drawing | Field | Limits |
| --- | --- | --- |
| `rating` | A `ChoiceField`, a `TypedChoiceField` or a `ModelChoiceField`, as a select or radio group | One star for each choice. An empty choice clears it. |
| `range` | An `IntegerField`, a `FloatField` or a `DecimalField` | `min_value`, `max_value` and `step_size`. |

Any other field raises `InvalidChoice` when the form is drawn.
