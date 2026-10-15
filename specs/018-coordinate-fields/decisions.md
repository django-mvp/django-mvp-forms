# Decisions: Latitude, longitude and point fields

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying.

## D1. The point field cleans to WKT text, not a pair of numbers

The maintainer's choice, put to him with both options. A GeoDjango model's geometry attribute
takes a string and turns it into a geometry when the model is saved, so text with the spatial
reference in front drops straight onto a `PointField` with nothing imported. A pair of `Decimal`s
would have been neater for a project without GeoDjango, but would leave every GeoDjango user to
write the conversion the field exists to save them.

**ADR:** none — the field's contract, stated in the spec and the README; no other part of the package builds on it.

## D2. The name `PointField`

The maintainer's choice over `CoordinatesField`. GeoDjango's form module has a field of the same
name, so a form importing both renames one on import, and a developer expecting GeoDjango's field
should know this one cleans to text rather than a GEOS point. The README says both plainly. A
model's `PointField` takes either, so neither difference affects saving.

**ADR:** none — the field's name and what it returns are public surface, stated in the README, not an architectural choice.

## D3. Empty cleans to `None`

Django's `DecimalField` cleans an empty value to `None`, and the latitude and longitude fields
follow it. The point field does too rather than cleaning to empty text like a `CharField`, because
a nullable `PointField` takes `None`, while empty text reaches GEOS on save and fails there.

**ADR:** none — follows Django's own `DecimalField`, nothing downstream inherits it.

## D4. A point that cannot be shown is the developer's error

A point stored in another spatial reference holds numbers that are not degrees. The choices were to
show them anyway, to convert them, or to refuse. Showing them puts wrong values in front of a
person, who might save them. Converting needs GDAL, which is the dependency the feature exists to
avoid. A person cannot fix the cause, and Django has no way to put an error on an initial value,
so the field raises when the form is drawn. The developer sees it the first time they open the
form, and the message says what to do. A point with a height is refused for the same reason: the
form has no input for it and saving would drop it.

**ADR:** none — local to this field's starting values and stated in the README.

## D5. A half-filled point is always an error

A not-required point field with one half filled could have been cleaned to `None`, as if left
empty. That would throw away what the person typed without telling them, so it is an error that
names the missing half.

**ADR:** none — local to this field's cleaning.

## D6. No range across the antimeridian

Every other field in the package refuses a lower bound above its upper bound when the form class is
defined. Reading that as "wraps round the antimeridian" for a longitude alone would make one field
behave unlike the rest, and would make a typo silently valid. Nothing in the request needs it.

**ADR:** none — the package's existing rule for bounds, applied unchanged.

## D7. Design review, 2026-10-15

- **IMask is never handed the bounds.** It clamps to `min` and `max` on every commit, so a stored or half-typed value outside them would be changed and posted. The `coordinate` kind checks the bounds in its own `validate`, and an input drawn holding a value the mask would cut waits unmasked, as a partial date does (ADR 0050).
- **No `inputmode` on the coordinate input.** The decimal keypad on a phone has no minus key.
- **`PointField.clean` raises `incomplete` itself**, with one message per half in its own `error_messages`, because `MultiValueField` gives a missing half no error code.
- **`to_python` reads numbers as numbers**, so a float near zero written in exponent form is not refused.
- **`CoordinateMaskInput` carries class defaults** (ADR 0049).
- **A lone `-` posts what IMask commits**, `-0`, which cleans to `0`. Kept as IMask's number rule, stated in the README and pinned by a browser test, rather than adding a special case to the script.
- Watch items for the implementers: bound errors are asserted by `params["limit_value"]` as well as by code. The reviewer suggested an ADR for the `coordinate` kind's own check in `data-imask`; it is written with T004, where the check is finished.

**ADR:** docs/adr/0056-the-coordinate-mask-checks-its-own-bounds.md
