# Implementation Plan: Latitude, longitude and point fields

**Branch**: `018-coordinate-fields` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

Three fields in `mvp_forms/fields.py`: `LatitudeField` and `LongitudeField`, which subclass
Django's `DecimalField`, and `PointField`, a `MultiValueField` built from one of each. Two widgets
in `mvp_forms/widgets.py`: `CoordinateMaskInput`, a `NumberMaskInput` with a kind of its own, and
`PointInput`, a `MultiWidget` of two of them. `mvp_forms/imask.js` gains the `coordinate` kind,
which is the number mask plus a check that refuses a value no further typing could bring inside
the bounds. Every option is stated on the field, and the field tells its widget, as the partial
date field does.

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7. No new dependency.
- IMask 7 for the masked inputs, loaded by the host project. The copy under `tests/data/` serves
  the browser tests.
- No GeoDjango, GEOS or GDAL, at runtime or in the tests (research, note 2).
- No models, migrations, views or URLs in the package.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, test first | Every task writes its tests first and sees them fail before the code is written |
| II and III, least machinery | One shared base for the two single fields, which differ by one number and their messages. One widget subclass, one multi-widget. No registry, no settings |
| VIII | Every error message and part name is wrapped in `gettext_lazy`, and the English catalogue is regenerated |
| X | The bounds rule lives on the field. The widget only carries what the field tells it |
| XI, public surface | The three fields, their options and error codes, the two widgets, the `coordinate` kind in `data-imask`, and the template path are public from this release and listed in the README |
| XII, scope | Form fields and widgets only. `PointField` is a form field, not a model field |
| XIII | The new template is a plain Django template. The modules import Django and the standard library |
| XIV | daisyUI's `join`, `join-item` and `input`. No stylesheet |
| XV | Classes, template, tests and README entries arrive in this pull request |

## The latitude and longitude fields

`CoordinateField(forms.DecimalField)` holds everything the two share. It is not exported in the
README's public surface. A subclass states `limit` (90 or 180) and its default messages.

| Option | Takes | Default |
|---|---|---|
| `min_value` | `int`, `float` or `Decimal`, at least `-limit` | `-limit` |
| `max_value` | the same, at most `limit` | `limit` |
| `decimal_places` | a whole number of at least zero | `6` |

Everything else is `DecimalField`'s, passed through. `max_digits` stays `None`.

- **At definition**, `__init__` refuses a bound that is not a finite number, a bound outside
  `±limit`, a `min_value` above `max_value`, and a `decimal_places` that is not a whole number of
  at least zero (a `bool` is not one). Each `ValueError` names the option. This reuses
  `Check.number` and `Check.whole_number` from `mvp_forms/widgets.py`.
- **`to_python`** strips the value. It refuses anything that does not match
  `[+-]?(\d+(\.\d*)?|\.\d+)` with code `invalid`, which rules out exponent form, `inf`, `nan` and
  a comma, and then hands the value to `DecimalField.to_python`. A `Decimal` equal to zero is
  returned as `abs(value)` so `-0` becomes `0`. Empty is `None`.
- **Validation** is `DecimalField`'s: `MinValueValidator`, `MaxValueValidator` and
  `DecimalValidator(None, decimal_places)`, with codes `min_value`, `max_value` and
  `max_decimal_places`. The subclass's `default_error_messages` replace their messages so they say
  "latitude" or "longitude" and keep `%(limit_value)s` or `%(max)s`. That is how an error inside a
  point names the half (FR-015).
- **Messages**: `invalid` ("Enter a latitude in decimal degrees."), `min_value`, `max_value` and
  `max_decimal_places`. The wording is not tested, only the codes.
- **Widget**: the default is `CoordinateMaskInput`. In `get_bound_field`, as `PartialDateField`
  does, the field writes its bounds and decimal places onto the widget when the widget is a
  `CoordinateMaskInput`. A widget the developer named that is not one is left alone.
- `widget_attrs` from `DecimalField` adds `step`, `min` and `max` only to a `NumberInput`, so
  nothing reaches the text input. Check this with a test.

## The masked input

`CoordinateMaskInput(NumberMaskInput)`, `kind = "coordinate"`, taking only `attrs`. It sets
`radix="."`, `thousands_separator=""` and `scale`, `min_value` and `max_value` from the attributes
the field writes. `mask_options()` is built when the widget is drawn, not in `__init__`, so a field
that changes them in `get_bound_field` is followed. `value_from_datadict` and `format_value` are
`NumberMaskInput`'s, which with a full stop and no separator pass the text through.

In `imask.js`, `build()` gains:

```js
if (kind === "coordinate") return coordinate(rest);
```

`coordinate(options)` returns `{ mask: Number, ...options, validate }`, where `validate` takes the
value as typed and refuses it when nothing that can still be typed after it lies in
`[min, max]`. An empty value, or a lone `-` while `min < 0`, is always accepted. For an unsigned
prefix `p` with no decimal mark, the values it can still become are `p` itself and every
`[p·10ᵏ, (p+1)·10ᵏ)` for k ≥ 1. The check stops once `p·10ᵏ` exceeds `max(|min|, |max|)`. With a
decimal mark and `f` fractional digits, the value is fixed to within `10⁻ᶠ`. The sign mirrors the
interval. The function sits beside `reach()` and follows its comments. Nothing in the `number`
kind changes.

## The point field

`PointField(forms.MultiValueField)`:

| Option | Default |
|---|---|
| `min_latitude`, `max_latitude` | `-90`, `90` |
| `min_longitude`, `max_longitude` | `-180`, `180` |
| `decimal_places` | `6`, shared by both halves |

- `__init__` builds `LatitudeField(min_value=…, max_value=…, decimal_places=…, required=True)`
  and the same for longitude, so their definition-time checks apply and their `ValueError` names
  the option. The point field catches each one and raises it again with its own option name
  (`min_latitude`, and so on). It calls `super().__init__(fields, require_all_fields=False,
  **kwargs)` with `widget=PointInput` unless one is named.
- Each half's `incomplete` message is set to "Enter a latitude." or "Enter a longitude.", so
  `MultiValueField` names the missing half (FR-020).
- `compress([])` returns `None`. `compress([lat, lon])` returns
  `f"SRID=4326;POINT({lon:f} {lat:f})"`.
- `has_changed` is `MultiValueField`'s. It works because `decompress` returns `Decimal`s, built
  from `str(float)` for a GEOS point, so `51.5074` compares equal to `Decimal("51.5074")`.
- `get_bound_field` writes each half's bounds and the decimal places onto the two parts of a
  `PointInput`.

## The point widget

`PointInput(forms.MultiWidget)`, `template_name = "mvp_forms/widgets/point.html"`, with two
`CoordinateMaskInput` parts. Each part has a translatable `placeholder` and `aria-label`
("Latitude" and "Longitude") and the class `join-item`, as the partial date's typed year has.

`decompress(value)` returns `[latitude, longitude]` as `Decimal`s, or `[None, None]` for an empty
value:

- an object with `x` and `y`: `srid` must be `None` or `4326` and `z` must be absent or `None`.
  Otherwise it raises `ValueError` naming the spatial reference or the height;
- `str`: `^\s*(SRID=(\d+);)?\s*POINT\s*\(\s*(num)\s+(num)\s*\)\s*$`, case-insensitive. The same
  spatial reference rule applies. `POINT Z`, `POINT EMPTY`, a third number or anything else raises
  `ValueError` saying the text is not a two-dimensional WKT point;
- a list or tuple of two: `(latitude, longitude)`, in that order.

The template copies `partial_date.html`: a `join` holding the parts.

The pack needs no change. A `MultiWidget` field is drawn as a fieldset with a legend, its parts
take the stated size, colour and variant through `decorate_part`, and an `aria-label` the part
already has is kept.

## The tests

| File | What it covers |
|---|---|
| `tests/test_fields.py` | Cleaning, every error code, options and their `ValueError`s for all three fields, `decompress`, `has_changed`, empty and required |
| `tests/test_widgets.py` | `CoordinateMaskInput`'s `data-imask` JSON follows the field, `PointInput` media and parts |
| `tests/test_pack/test_coordinates.py` (new) | Drawing through the pack: a text input with no `step`, `min` or `max`. A point is a fieldset with two named inputs, size, colour and variant on both, and the error state |
| `tests/test_coordinates_e2e.py` (new) | Typing in a browser: the bounds, the decimal places, the minus sign, a narrowed range whose lower bound is above zero, a page without IMask, an input added later, the point's two inputs |
| `tests/test_demo.py` | The new demo page answers and holds each field |

The field tests never import `django.contrib.gis`. A small stand-in class with `x`, `y`, `srid`
and `z` plays the GEOS point.

## The demo

A page "Coordinates" in the Forms section: each field with its defaults, a latitude and longitude
narrowed to one country, a point with an initial value, a bound form in error, a formset of points
whose rows can be added, and a point field in a modal. It is modelled on the partial date page.

## Documentation

- README: a section "Coordinates" after "Partial dates", covering the three fields, their options
  and error codes, what the page loads, a page without IMask, and declaring `PointField` on a
  model form for a GeoDjango `PointField`, with the note that GeoDjango's form field of the same
  name cleans to a GEOS point. The public surface list gains the fields and the widgets, and the
  template list gains `mvp_forms/widgets/point.html`.
- `CHANGELOG.md` under `[Unreleased]`.
- `CONTEXT.md`: decimal degrees, WGS84 bounds, coordinate fields and WKT text.
- The English catalogue regenerated.

## Story order

**US1 → US2 → US4 → US3, sequential, in the feature worktree.** US4's options live in the single
fields, and the point field builds on them, so US4 comes before US3 despite its priority.

## What this plan does not do

- Change `NumberMaskInput` or the `number` kind.
- Touch the pack's templates or `daisyui.py`.
- Import anything from `django.contrib.gis`.
