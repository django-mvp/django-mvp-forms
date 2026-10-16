# Research: Latitude, longitude and point fields

Read against main at `cb1b4f5` (2026-10-15). Nothing was delivered between the specification and
this research.

## The maintainer's planning notes

### 1. A point field for GeoDjango without depending on GeoDjango

**Adopted.** Django's own source settles that this works with nothing imported. A geometry
attribute on a model is a `SpatialProxy`, and its `__set__` lets through `None`, a `str` or a
`memoryview` as they are ("Set geometries with None, WKT, HEX, or WKB",
`django/contrib/gis/db/models/proxy.py`). `GeometryField.get_prep_value` then builds a
`GEOSGeometry` from the text when the model is saved (`django/contrib/gis/db/models/fields.py`),
and `GEOSGeometry` reads EWKT, so `SRID=4326;POINT(<x> <y>)` keeps its spatial reference. A model
form reaches the same proxy through `construct_instance` → `save_form_data` → `setattr`. The
first read of the attribute builds a GEOS geometry from the text and keeps it
(`django/contrib/gis/db/models/proxy.py`), so a form drawn again from that instance is handed a
point object. FR-022 covers both.

The field reads an existing point by duck typing: `x`, `y`, `srid`, and `z`, which a GEOS `Point`
returns as `None` when the point has no height. It never imports anything from
`django.contrib.gis`.

### 2. Proving a real `PointField` takes the text

**Not adopted as a GeoDjango test.** Neither this machine nor the CI images have GEOS or GDAL.
Importing `django.contrib.gis.geos` here fails with "Could not find the GDAL library". A test that
skips without them would never run anywhere, so it would prove nothing while looking like proof,
and a CI job that installs GDAL is the dependency the maintainer asked us not to take on. Instead:

- the tests assert the exact text the field produces, including the longitude-first order and a
  spatial reference prefix GEOS reads;
- the README cites GeoDjango's documentation for assigning WKT to a geometry field.

Reading GeoDjango's own code from a test was also tried and ruled out: even
`django.contrib.gis.db.models.proxy` refuses to import without GDAL. What the field relies on is
two documented behaviours of GeoDjango. Neither has changed since Django 1.x.

**ADR:** none. This is local to this feature's tests.

### 3. One of the existing IMask widgets

**Adopted, with one addition.** `NumberMaskInput` already does nearly everything the coordinate
inputs need. IMask 7.6.1 (the version the suite pins) was driven from Node against the options the
field would write (`scale=6, radix=".", thousandsSeparator="", min=-90, max=90`):

| Typed | Held |
|---|---|
| `95` | `9` |
| `-91` | `-9` |
| `90.5` | `90.` |
| `89.1234567` | `89.123456` |
| `12.34.5` | `12.345` |
| `abc` | empty |
| `9-0` | `90` |

So IMask refuses a digit past either bound, a seventh decimal place, a second decimal mark,
letters, and a minus sign anywhere but the start. **The gap:** with narrowed bounds that do not
include zero, IMask does not refuse a value below the lower bound while it is being typed. With
`min=40, max=60` it holds `35`, because it only checks the lower bound when it commits or
autofixes. That fails US-4 scenario 4 and FR-029.

The answer is a widget built on `NumberMaskInput` with its own kind, `coordinate`. The script
builds the same `Number` mask for it and adds one check: a value is refused when nothing that can
still be typed after it could fall inside the bounds. This is the reach check the partial date
mask already uses (`reach()` in `imask.js`), applied to a number. `NumberMaskInput` and its
`number` kind are left as they are, because FS-015's specification says IMask either refuses an
out-of-range number or corrects it, and some projects rely on that.

`autofix` was considered and rejected. It corrects the value when the input loses focus, so a
person who typed `35` would submit `40`, a value they never typed. IMask's `min` and `max` do the
same without `autofix`: the mask clamps to them on every commit, when it attaches and on every
blur. So the bounds go to the script's own check only, never to IMask.

## What already exists

| Piece | Where the search stopped |
|---|---|
| Parsing, `Decimal` cleaning, empty → `None`, no localisation, decimal-places check, min/max validators with replaceable messages | **Django:** `forms.DecimalField`. Its `min_value` and `max_value` validators carry codes `min_value` and `max_value` with `%(limit_value)s`, and `decimal_places` adds `DecimalValidator` with code `max_decimal_places`. A field's `error_messages` replace a validator's message by code (`Field.run_validators`). The latitude and longitude fields subclass it |
| Refusing exponent form (`5e1`) | **New code.** `DecimalField` accepts it, so a few lines in `to_python` |
| `-0` → `0` | **New code**, one line |
| The masked input | **This repo:** `NumberMaskInput`, subclassed as `CoordinateMaskInput` with kind `coordinate` (note 3) |
| The reach check while typing | **This repo:** the pattern of `reach()` in `mvp_forms/static/mvp_forms/imask.js`. **New code** for the number form of it |
| The field telling its widget its options | **This repo:** `PartialDateField.get_bound_field` sets them on the widget it is given. Same pattern |
| Two values as one field, `required` versus a half missing | **Django:** `forms.MultiValueField(require_all_fields=False)` with each subfield required. An empty pair cleans through `compress([])`, and a required empty pair gets `required`. A missing half gets a bare message with no error code, so `PointField.clean` raises `incomplete` itself |
| Two inputs as one widget | **Django:** `forms.MultiWidget`, with `decompress` written for points, WKT text and pairs (**new code**) |
| Drawing a multi-widget as a fieldset with a legend, one help text and one set of errors, size, colour and variant on each part | **This repo:** the pack already does this for every `MultiWidget` (`frame.html` `is_group`, `daisyui.py` `decorate_part`). Nothing to add |
| A visible name on each part | **This repo:** the partial date widget's typed year has a placeholder and an `aria-label` and sits in a daisyUI `join` (`mvp_forms/widgets/partial_date.html`). The point widget does the same with "Latitude" and "Longitude" |
| Reading WKT text for an initial value | **New code.** A regular expression for `[SRID=n;]POINT(x y)`. `POINT Z` and a third number are refused. GEOS is not available (note 2) |
| Writing the WKT text | **New code**, one format string |
| Errors that name the half | **Django**, by message: each subfield's own default messages name "latitude" or "longitude", so a `MultiValueField` that collects them names the half for free |
| Demo page, formset and modal | **This repo:** `demo/partial_date_forms.py` and `demo/partial_date_views.py` and their template, as a model |
| End-to-end tests | **This repo:** `tests/test_imask_e2e.py` and its `masked_page` fixture, IMask 7.6.1 from `tests/data` |

## Settled for the plan

- **Option names** follow Django and the partial date field: `min_value`, `max_value` and
  `decimal_places` on the latitude and longitude fields, and `min_latitude`, `max_latitude`,
  `min_longitude`, `max_longitude` and `decimal_places` on the point field.
- **Errors** carry codes. The latitude and longitude fields use `invalid`, `min_value`,
  `max_value`, `max_decimal_places` and `required`. The point field adds `incomplete`, with one
  message for each half, and `required` on the whole. Every message is wrapped in `gettext_lazy`, and the English
  catalogue gains them (Article VIII).
- **A point that cannot be shown** raises `ValueError` from the widget's `decompress`, which runs
  when the form is drawn and when `has_changed` compares. The message names the spatial reference,
  or says the point has a height.
- **No GEOS anywhere in the tests** (note 2).
- **The sketch gate is `none`**, as recorded. The point widget copies the partial date widget's
  drawing and adds no new design.
