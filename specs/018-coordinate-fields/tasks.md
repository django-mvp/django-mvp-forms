# Tasks — 018 Latitude, longitude and point fields

**Branch**: `018-coordinate-fields` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I: the tests are written and seen to
fail for the right reason, then the code is written. A task is done when its tests pass, the tree
is green and the work is committed. Documentation lands in the task that introduces what it
describes.

No test asserts wording, a colour, a width or a class used only for looks. A field test asserts
the cleaned value or the error's code. A widget test asserts the `data-imask` JSON, the parts
drawn, the media and what the field receives. A browser test asserts what this package's script
does and the options IMask was handed, and asserts IMask's own number rules only where they make a
scenario of the spec true.

Code standards for every task: no leading-underscore names; line length 88; docstrings per
`docs/contributing/standards/code-documentation.md`; no docstrings on tests; test structure per
`docs/contributing/standards/testing.md`. `mvp_forms/fields.py` and `mvp_forms/widgets.py` import
Django and the standard library only, and nothing anywhere imports `django.contrib.gis`.
`CONSTITUTION.md` and everything under `.github/` do not change. A document reads as current
state. README links are absolute. Every `ValueError` names the option at fault, and every
`ValidationError` is raised with a `code`.

## Order

**US1 → US2 → US4 → US3, sequential, in the feature worktree.**

---

## US1 — A developer adds a latitude or a longitude field to a form (P1)

Issue: #194. Delivers FR-001 to FR-009, FR-031, FR-033, FR-035; SC-001.

### T001 — The two fields and their rules

**Files**: `tests/test_fields.py`, `mvp_forms/fields.py`,
`mvp_forms/locale/en/LC_MESSAGES/django.po`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`

Plan, *The latitude and longitude fields*.

- `LatitudeField` cleans `-90` to `90` and `LongitudeField` cleans `-180` to `180` to a
  `Decimal`. Both ends are accepted, and a value past either is refused with `min_value` or
  `max_value`. Nothing is wrapped.
- More than six decimal places is refused with `max_decimal_places`, and the value is not
  rounded.
- Refused with `invalid`: text that is not a number, `51,5`, `5e1`, `1E2`, `inf`, `nan`, `-`
  and `.`. Accepted: `+51.5`, `.5`, `90.`, and a value with space around it. `-0` cleans to `0`.
- Empty is `None` when not required, and `required` when required.
- `initial` as a `Decimal`, a `float` or a `str` is shown with a full stop. Check that nothing is
  localised under a language whose decimal mark is a comma.
- A developer's own `error_messages` replace each code's message. `disabled` and `validators`
  behave as on a `DecimalField`.
- The default widget is `CoordinateMaskInput` once T002 exists. Until then the field uses
  `DecimalField`'s, and this task asserts nothing about widgets.
- README: the section "Coordinates" opens with the two fields: what they accept and return, and
  their error codes. The public surface gains both. CHANGELOG entry. `CONTEXT.md` gains *decimal
  degrees*, *WGS84 bounds* and *coordinate fields*. The catalogue is regenerated.

---

## US2 — A person types a coordinate into a masked input (P1)

Issue: #195. Delivers FR-010 to FR-013, FR-030, FR-032, FR-034; SC-002, SC-003, SC-005.

### T002 — The masked input and the `coordinate` kind

**Files**: `tests/test_widgets.py`, `tests/test_pack/test_coordinates.py` (new),
`tests/test_coordinates_e2e.py` (new), `mvp_forms/widgets.py`, `mvp_forms/fields.py`,
`mvp_forms/static/mvp_forms/imask.js`, `README.md`, `pyproject.toml` (the e2e file list)

Plan, *The masked input*.

- `CoordinateMaskInput` writes `{"kind": "coordinate", "scale": 6, "radix": ".",
  "thousandsSeparator": "", "min": -90, "max": 90}` for a latitude field with no options, and
  `±180` for a longitude. The field writes them in `get_bound_field`. Two forms of the same class
  each draw their own field's values.
- A widget the developer named that is not a `CoordinateMaskInput` is left as it is.
- Through the pack, the input is a text input with no `step`, `min` or `max` attribute, and takes
  a stated size, colour and variant. Its form's media names `mvp_forms/imask.js`.
- A form with no coordinate field names no script it did not name before.
- `imask.js` builds the `coordinate` kind as the number mask plus `validate` (plan). This task
  writes the whole check, but only the WGS84 bounds are exercised in the browser here.
- Browser, with IMask 7.6.1 and the form's media: typing past ±90 or ±180 is refused, a seventh
  decimal place is refused, a minus sign is taken only at the start, a second full stop is
  refused, letters are refused, and a posted value reaches `cleaned_data` as the `Decimal` typed.
  Without IMask the input is a plain text input, no error is raised, and an out-of-range value is
  refused by the field. An input added after the page loaded is masked once.
- README: the masked input, what the page must load, and what happens without IMask.
  `CoordinateMaskInput` in the public surface, and the `coordinate` kind beside the other
  `data-imask` kinds.

### T003 — The demo page

**Files**: `demo/coordinate_forms.py` (new), `demo/coordinate_views.py` (new),
`demo/templates/demo/coordinates.html` (new), `demo/urls.py`, `demo/menus.py`,
`tests/test_demo.py`

Plan, *The demo*. The page "Coordinates" with a latitude and a longitude field at their defaults,
the two with an initial value, and a bound form in error. The point field, the formset and the
modal sections come with T005. `tests/test_demo.py` asserts the page answers and holds each field
by id.

---

## US4 — A developer narrows the bounds or sets the precision (P3)

Issue: #197. Delivers FR-026 to FR-029.

### T004 — Narrower bounds and the number of decimal places

**Files**: `tests/test_fields.py`, `tests/test_widgets.py`, `tests/test_coordinates_e2e.py`,
`mvp_forms/fields.py`, `mvp_forms/static/mvp_forms/imask.js`, `README.md`,
`demo/coordinate_forms.py`

- `min_value`, `max_value` and `decimal_places` are enforced, and the widget's JSON follows them.
  `decimal_places=0` takes whole numbers only.
- `ValueError` naming the option at definition: a bound past `±limit`, a bound that is not a
  finite number (including `bool`, `nan`, `inf` and text), `min_value` above `max_value`, and a
  `decimal_places` that is negative, not an `int`, or a `bool`. Equal bounds are allowed.
- Browser: with `min_value=40, max_value=60`, typing `3` is refused, and `4`, `45` and `45.5` are
  taken. With `min_value=-60, max_value=-40` the same holds mirrored. With `decimal_places=2` a
  third decimal place is refused. These fail before the `validate` in `imask.js` is right, and
  the `40` to `60` case fails with the `number` kind (show this by the test's first run).
- README: the options and the errors they raise. The demo's narrowed pair.

---

## US3 — A developer saves a point from a form to a GeoDjango `PointField` (P2)

Issue: #196. Delivers FR-014 to FR-025; SC-004, SC-006.

### T005 — The point field, its widget and its template

**Files**: `tests/test_fields.py`, `tests/test_widgets.py`, `tests/test_pack/test_coordinates.py`,
`tests/test_coordinates_e2e.py`, `tests/test_demo.py`, `mvp_forms/fields.py`,
`mvp_forms/widgets.py`, `mvp_forms/templates/mvp_forms/widgets/point.html` (new),
`mvp_forms/locale/en/LC_MESSAGES/django.po`, `README.md`, `CONTEXT.md`, `demo/coordinate_forms.py`,
`demo/templates/demo/coordinates.html`, `tests/test_pack/test_independence.py` and the README's
template list, if they enumerate templates

Plan, *The point field* and *The point widget*.

- Cleans to `SRID=4326;POINT(<longitude> <latitude>)`, longitude first, each number as typed in
  plain decimal notation. Both empty: `None` when not required, `required` when required. One
  half empty: an error with code `incomplete` on the field, whichever half, required or not. A
  half out of bounds or not a number: that half's code. The message for each names the half.
  Assert by codes, and once each that the two halves' messages differ.
- Options `min_latitude`, `max_latitude`, `min_longitude`, `max_longitude` and `decimal_places`
  are enforced, and a bad one raises `ValueError` naming the point field's option.
- `decompress`: a stand-in with `x`, `y`, `srid=4326` or `srid=None` and `z=None`; `POINT(x y)`
  and `SRID=4326;POINT(x y)` text, in any case and spacing; a `(latitude, longitude)` tuple or
  list; `None` and empty text. `ValueError` when drawn: `srid=3857`, `z=12.0`,
  `SRID=3857;POINT(...)`, `POINT Z (1 2 3)`, `POINT EMPTY`, `LINESTRING(...)`.
- `has_changed` is `False` for a form posted with the coordinates of its initial point (a float
  stand-in, WKT text and a tuple), and `True` when either half moved.
- Through the pack: one fieldset whose legend is the label, one help text and one error list, two
  text inputs each with its own `aria-label` and the mask's `data-imask` for its half, both taking
  a stated size, colour and variant, and `aria-invalid` on both when the field is in error.
- Browser: each input is masked to its own half's bounds, and a posted pair reaches
  `cleaned_data` as the WKT text.
- Demo: the point field with an initial value, a formset of points whose rows can be added, and
  a point in a modal. `tests/test_demo.py` covers the new sections.
- README: `PointField` and `PointInput`, the starting values it reads, the error raised for a
  point it cannot show, declaring it on a model form for a GeoDjango `PointField` with a short
  example, and the note that GeoDjango's own form `PointField` cleans to a GEOS point. Template
  list: `mvp_forms/widgets/point.html`. `CONTEXT.md` gains *WKT text*.
