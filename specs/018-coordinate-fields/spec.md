# Feature Specification: Latitude, longitude and point fields

**Feature Branch**: `018-coordinate-fields`

**Created**: 2026-10-15

**Status**: Draft

**Serves**: G11 (the package offers its own fields and widgets, each looking native beside the
pack's own inputs)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #192

**Depends on**: nothing still to be delivered. It builds on the number mask widget and its script
(FS-015), and on the size, colour and variant choices of FS-007.

**Input**: Forms that record where something is, such as a sample site, a station or a find spot,
need a latitude and a longitude typed as numbers. A developer should be able to add a latitude
field, a longitude field, or one point field that takes both. Each is a coordinate in decimal
degrees, checked against the WGS84 bounds of ±90 for a latitude and ±180 for a longitude. The
inputs are masked so a person cannot type a value outside those bounds, and the field checks again
on the server. The point field hands back WKT text that a GeoDjango `PointField` model field
accepts as it is, without this package depending on GeoDjango.

## Clarifications

### Session 2026-10-15

The maintainer confirmed the reading of the feature before this was written: three fields, decimal
degrees only, the WGS84 bounds checked in the browser and again on the server, a point field that
cleans to WKT text for a GeoDjango `PointField`, and no dependency on GeoDjango. He chose WKT text
over a pair of numbers for the point field, and chose the name `PointField` over `CoordinatesField`
so it reads as what a GeoDjango developer expects. The coverage scan then found five ambiguities.
Each was resolved from that conversation, the goals, the constitution and the earlier fields'
specifications. Longer rationale is in `decisions.md`.

- **Q: What does a latitude or longitude field put in the cleaned data when it is left empty?**
  A: `None`, as Django's own number fields do. The point field cleans to `None` too, rather than
  empty text, because a nullable GeoDjango `PointField` takes `None` and cannot read empty text.
  Recorded as FR-004 and FR-019.

- **Q: A point is filled in by half: a latitude with no longitude. What happens?**
  A: The field reports an error that names the missing half, whether or not the field is required.
  A point with one coordinate is not a point, and saving nothing in its place would lose what the
  person typed without telling them. Recorded as FR-020.

- **Q: A form editing an existing record is handed a point stored in another spatial reference,
  such as Web Mercator. When is that refused, and how?**
  A: When the form is drawn, with an error that names the spatial reference it was given. The
  numbers of such a point are not degrees, so showing them would put wrong values in front of a
  person, and converting them would need GDAL. It is the developer's mistake, not the person's, so
  it is raised to the developer rather than shown on the form. A point with a height is refused in
  the same way, because saving the form would drop the height. Recorded as FR-024.

- **Q: Is the decimal mark a full stop in every language?**
  A: Yes. Coordinates are written with a full stop almost everywhere, including in languages whose
  numbers use a comma, and WKT text has to use one. The field does not localise the number.
  Recorded as FR-007.

- **Q: Can a developer narrow a longitude so that it crosses the antimeridian, such as 170 to
  -170 for the Pacific?**
  A: No. A lower bound above the upper bound is refused when the form class is defined, as it is
  for every other field in the package. A range across the antimeridian is listed under Out of
  scope. Recorded as FR-028.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer adds a latitude or a longitude field to a form (Priority: P1)

A developer has a value that is a latitude or a longitude. They add the matching field to a form.
Whatever a person submits, the form's cleaned data holds a number in decimal degrees inside the
WGS84 bounds, or the form reports an error on the field.

**Why this priority**: The fields are the feature. They own the rule for what a valid coordinate
is, and the masked input and the point field depend on them. With this story alone a developer
already has two working fields.

**Independent Test**: Define a form with one latitude field and one longitude field, submit it
with valid and invalid values, and read the cleaned data and the errors. No script and no other
story is needed.

**Acceptance Scenarios**:

1. **Given** a form with a latitude field, **When** it is submitted with a number from -90 to 90,
   **Then** the cleaned data holds that number as a `Decimal`.
2. **Given** a form with a longitude field, **When** it is submitted with a number from -180 to
   180, **Then** the cleaned data holds that number as a `Decimal`.
3. **Given** such a form, **When** it is submitted with a latitude of exactly -90 or 90, or a
   longitude of exactly -180 or 180, **Then** it is accepted.
4. **Given** such a form, **When** it is submitted with a latitude past ±90 or a longitude past
   ±180, **Then** the field reports an error that names the bound it crossed, and the value is not
   wrapped round to the other side.
5. **Given** such a form, **When** it is submitted with more decimal places than the field allows,
   **Then** the field reports an error and the value is not rounded.
6. **Given** such a form, **When** it is submitted with text that is not a number, or a number
   written with a comma as the decimal mark, **Then** the field reports an error.
7. **Given** a field that is not required, **When** it is submitted empty, **Then** the cleaned
   data holds `None` and the form is valid.
8. **Given** a required field, **When** it is submitted empty, **Then** the field reports that it
   is required.
9. **Given** a field whose initial value is a number, **When** the form is drawn, **Then** the
   input shows it in decimal degrees with a full stop as the decimal mark.

---

### User Story 2 - A person types a coordinate into a masked input (Priority: P1)

A person filling in a form meets an input for a latitude or a longitude. They type a number, with
a minus sign if they need one. They cannot type a value past the bounds, and they cannot type more
decimal places than the field allows.

**Why this priority**: The need behind the feature is that a wrong coordinate is stopped while the
person is typing it, before the form is sent. It shares the first priority because the fields
without it are no better than a number input.

**Independent Test**: Give a form a latitude and a longitude field, load IMask and the form's media
on a page, and type into each input in a browser.

**Acceptance Scenarios**:

1. **Given** a page that loads IMask and the form's media, **When** a person types into a latitude
   input a digit that would take the value past ±90, **Then** the digit is not accepted. A
   longitude input does the same at ±180.
2. **Given** such a page, **When** a person types a minus sign at the start of the input, **Then**
   it is accepted, and anywhere else it is not.
3. **Given** such a page, **When** a person types a full stop, **Then** it is taken as the decimal
   mark, and a second one is not accepted.
4. **Given** such a page, **When** a person types a digit past the number of decimal places the
   field allows, **Then** the digit is not accepted.
5. **Given** such a page, **When** a person types letters or other characters, **Then** they are
   not accepted.
6. **Given** a page that loads the form's media and not IMask, **When** a person types and
   submits, **Then** the input behaves as a plain text input, no error is raised in the browser,
   and the field validates what was sent.
7. **Given** a latitude or longitude field with no widget named, **When** its form is drawn through
   the pack, **Then** it is drawn as the pack draws any text input, taking the size, colour and
   variant stated for the form or the field.

---

### User Story 3 - A developer saves a point from a form to a GeoDjango `PointField` (Priority: P2)

A developer has a model with a GeoDjango `PointField` and wants people to type its coordinates
rather than click on a map. They declare the package's point field on the form. A person sees a
latitude and a longitude under one label. What the form hands back is WKT text that the model's
`PointField` takes as it is, and the package does not need GeoDjango installed to do any of it.

**Why this priority**: It is the case the maintainer has in mind for the fields, and it is what
lets a project with a spatial database use them without writing a conversion. It comes after the
two fields because it is built from them.

**Independent Test**: Define a form with a point field, submit it with valid and invalid pairs,
and read the cleaned data and the errors. Draw it with a stand-in object that has `x`, `y` and
`srid` as its initial value. None of this needs GeoDjango.

**Acceptance Scenarios**:

1. **Given** a form with a point field, **When** it is submitted with a latitude and a longitude
   inside the bounds, **Then** the cleaned data holds `SRID=4326;POINT(<longitude> <latitude>)`,
   with the longitude first.
2. **Given** such a form, **When** either half is outside its bounds or is not a number, **Then**
   the field reports an error that names the half and the bound it crossed.
3. **Given** such a form, **When** it is submitted with one half filled and the other empty,
   **Then** the field reports an error that names the missing half, whether or not the field is
   required.
4. **Given** a point field that is not required, **When** both halves are submitted empty,
   **Then** the cleaned data holds `None` and the form is valid.
5. **Given** a required point field, **When** both halves are submitted empty, **Then** the field
   reports that it is required.
6. **Given** a point field whose initial value is a GEOS point in WGS84, **When** the form is
   drawn, **Then** the latitude input shows the point's `y` and the longitude input shows its `x`.
7. **Given** a point field whose initial value is WKT text, or a pair of a latitude and a
   longitude, **When** the form is drawn, **Then** each input shows its half.
8. **Given** a point field whose initial value is a point in a spatial reference other than WGS84,
   or a point with a height, **When** the form is drawn, **Then** an error is raised to the
   developer that says why the point cannot be shown.
9. **Given** a form editing a point, **When** it is submitted with the same coordinates it was
   drawn with, **Then** the form reports that the field has not changed.
10. **Given** a page that loads IMask and the form's media, **When** a person types into either
    input, **Then** it is masked as a latitude or a longitude input is.
11. **Given** a point field, **When** its form is drawn through the pack, **Then** the two inputs
    are drawn in one fieldset whose legend is the field's label, with one help text and one set of
    errors, each input is named for assistive technology as the latitude or the longitude, and both
    take the size, colour and variant stated for the form or the field.

---

### User Story 4 - A developer narrows the bounds or sets the precision (Priority: P3)

A developer has coordinates that can only fall inside a known area, or that are only ever recorded
to a few decimal places. They state narrower bounds or a number of decimal places on the field.
The field enforces them and the masked input follows them.

**Why this priority**: The WGS84 bounds and six decimal places cover the common case. This narrows
the field for projects that need it.

**Independent Test**: Define fields with narrower bounds and with a different number of decimal
places, submit values on both sides of each, and define fields with options that cannot be right.

**Acceptance Scenarios**:

1. **Given** a latitude or longitude field with a narrower lower or upper bound, **When** it is
   submitted with a value outside it, **Then** the field reports an error that names the bound.
2. **Given** a point field with narrower bounds for either half, **When** it is submitted with a
   value outside them, **Then** the field reports an error that names the half and the bound.
3. **Given** a field with a number of decimal places stated, **When** it is submitted with more,
   **Then** the field reports an error. **When** it is drawn on a page that loads IMask, **Then**
   the input accepts no more.
4. **Given** a field with narrower bounds, **When** it is drawn on a page that loads IMask,
   **Then** the input refuses a digit that would take the value past them.
5. **Given** a field with a bound outside WGS84, a lower bound above its upper bound, or a number
   of decimal places that is not a whole number of at least zero, **When** the form class is
   defined, **Then** an error is raised that names the option.
6. **Given** a field with nothing stated, **When** it is submitted with up to six decimal places
   anywhere inside the WGS84 bounds, **Then** it is accepted.

---

### Edge Cases

- A value has a leading plus sign, such as `+51.5`. The field accepts it, as Django's number
  fields do. The mask need not let a person type one.
- A value is `-0`. It is accepted and cleaned to zero.
- A value has space around it. The space is dropped, as Django drops it for any number field.
- A value is written in exponent form, such as `5e1`. The field refuses it, because a coordinate
  is never written that way and the mask cannot produce one.
- A pasted value holds both coordinates, such as `51.5074, -0.1278`, or a hemisphere letter, such
  as `51.5074° N`. The mask takes what it can and the field validates what is sent. Accepting such
  text is out of scope.
- A developer gives the masked input of one of these fields to a field that is not one of them.
  The widget draws and submits text as it would, and whether that text is acceptable is that
  field's to decide.
- A developer sets `attrs` on a widget. They are kept. On the point field's widget they reach both
  inputs.
- The form is drawn with Django's own form rendering or another template pack. The inputs draw and
  are masked as usual, without the pack's drawing of the point field's fieldset.
- A page holds the form's media several times, once for each form. The script acts once.
- A host project's language is not English. The field's error messages follow the active language,
  where a translation exists. The decimal mark stays a full stop (FR-007).
- A point field's initial value is a GEOS point with no spatial reference set. It is read as WGS84,
  since that is what a point built from typed degrees is.
- A point field sits in a formset row added after the page loaded, or in a modal. Its inputs are
  masked there as anywhere.

### Out of scope

- A map to pick a point from. GeoDjango's own form field does that.
- Degrees, minutes and seconds, and hemisphere letters.
- Spatial references other than WGS84, and converting a point between them.
- Datums, projections and heights.
- A longitude range that crosses the antimeridian.
- Pasting a latitude and longitude together into one input.
- A model field, and storage of any kind. The point field hands back text, and the developer's
  model holds it.
- Any runtime dependency on GeoDjango, GEOS or GDAL. Whether the tests may use them is a planning
  question (`planning-notes.md`, note 2).
- A change to the mask widgets of FS-015.

## Requirements *(mandatory)*

### Functional Requirements

#### The latitude and longitude fields

- **FR-001**: The package MUST provide a latitude field and a longitude field: Django form fields
  a developer adds to a form.
- **FR-002**: The latitude field MUST accept a number from -90 to 90 inclusive and the longitude
  field a number from -180 to 180 inclusive, and each MUST refuse any other number with an error
  that names the bound it crossed. Neither MUST wrap a value round to the other side.
- **FR-003**: The cleaned value MUST be a `Decimal` in decimal degrees.
- **FR-004**: An empty submission to a field that is not required MUST clean to `None`.
- **FR-005**: Each field MUST accept up to six decimal places when nothing else is stated, and MUST
  refuse more with an error. It MUST NOT round.
- **FR-006**: Each field MUST refuse text that is not a number, and a number in exponent form.
- **FR-007**: Each field MUST read and show the decimal mark as a full stop in every language, and
  MUST NOT localise the number.
- **FR-008**: Each error a field reports MUST be translatable and MUST be replaceable by the
  developer as Django's field errors are.
- **FR-009**: Each field MUST behave as a Django form field does in every other respect:
  `required`, `label`, `help_text`, `validators`, `disabled` and `initial`.

#### The masked input

- **FR-010**: With no widget named, the latitude and longitude fields MUST use the package's number
  mask widget, set to the field's bounds and decimal places with a full stop as the decimal mark
  and no thousands separator. The developer states neither the bounds nor the decimal places twice.
- **FR-011**: On a page that loads IMask and the form's media, the input MUST accept digits, one
  minus sign at the start and one full stop, MUST refuse a digit that takes the value past the
  field's bounds, and MUST refuse a digit past the field's decimal places.
- **FR-012**: The input MUST work as the mask widgets of FS-015 do in every respect that spec
  settles: one script named in the form's media, no inline script, an input added later is masked,
  no input is masked twice, and a page without IMask gets a plain text input and no error.
- **FR-013**: The input MUST be drawn as the pack draws any text input, taking the size, colour
  and variant stated for the form or the field.

#### The point field

- **FR-014**: The package MUST provide a point field, named `PointField`: a Django form field that
  takes a latitude and a longitude together.
- **FR-015**: The point field MUST check each half as the latitude field and the longitude field
  check theirs, and each error MUST name the half it concerns.
- **FR-016**: The cleaned value MUST be the text `SRID=4326;POINT(<longitude> <latitude>)`, with
  the longitude first and each number written in plain decimal notation.
- **FR-017**: The cleaned value MUST be accepted as it is by a GeoDjango `PointField` model field,
  and the package MUST NOT import GeoDjango, GEOS or GDAL to produce it.
- **FR-018**: The point field MUST draw two masked inputs, one for the latitude and one for the
  longitude, each as FR-010 to FR-013 require.
- **FR-019**: When both halves are submitted empty, a point field that is not required MUST clean
  to `None`, and a required one MUST report that it is required.
- **FR-020**: When one half is submitted and the other is empty, the field MUST report an error
  that names the missing half, whether or not the field is required.
- **FR-021**: Through the pack, the two inputs MUST be drawn in one fieldset whose legend is the
  field's label, with one help text and one set of errors. Each input MUST carry a name for
  assistive technology that says whether it is the latitude or the longitude.
- **FR-022**: The point field MUST accept as its initial value an object with `x` and `y`
  attributes, such as a GEOS point, WKT text with or without a spatial reference, or a pair of a
  latitude and a longitude. It MUST read `x` as the longitude and `y` as the latitude.
- **FR-023**: An initial value with no spatial reference MUST be read as WGS84.
- **FR-024**: An initial value in a spatial reference other than WGS84, or a point with a height,
  MUST raise an error to the developer when the form is drawn, saying why the point cannot be
  shown.
- **FR-025**: A form submitted with the coordinates it was drawn with MUST report that the point
  field has not changed, whichever kind of initial value it was given.

#### Narrower bounds and precision

- **FR-026**: Each of the three fields MUST let a developer state narrower lower and upper bounds:
  one pair on the latitude and longitude fields, and one pair for each half on the point field.
  With nothing stated, the bounds are WGS84's.
- **FR-027**: Each of the three fields MUST let a developer state the number of decimal places it
  accepts. With nothing stated it is six.
- **FR-028**: A bound outside WGS84, a lower bound above its upper bound, or a number of decimal
  places that is not a whole number of at least zero MUST raise an error when the form class is
  defined, naming the option.
- **FR-029**: The masked inputs MUST follow the bounds and decimal places stated on the field.

#### Constraints the package keeps

- **FR-030**: The checks in the browser MUST never be the only check. Every rule a masked input
  enforces MUST also be enforced by the field.
- **FR-031**: The feature MUST add no model, model field, view, URL or migration, and no runtime
  dependency.
- **FR-032**: A form that uses none of the three fields MUST be drawn exactly as before and load no
  script it did not load before.

#### Shipping it

- **FR-033**: The README MUST gain a section on the three fields: the values accepted and
  returned, the bounds and decimal places, what the page needs to load, what happens on a page
  without IMask, and how the point field is declared on a form for a GeoDjango `PointField`. All
  three fields and any widget the feature adds MUST appear in the README's public surface, and any
  template the feature adds MUST appear in the template list.
- **FR-034**: The demo MUST gain a Coordinate fields page in its Custom fields group, with live
  examples of each field with its defaults, with narrower bounds, with an initial value, in an
  invalid state, in a formset whose rows can be added, and in a modal.
- **FR-035**: `CONTEXT.md` MUST gain the terms under Key Entities.

### Requirement coverage

| Story | Requirements |
|---|---|
| US1: A developer adds a latitude or a longitude field to a form | FR-001 to FR-009, FR-031, FR-033, FR-035 |
| US2: A person types a coordinate into a masked input | FR-010 to FR-013, FR-030, FR-032, FR-034 |
| US3: A developer saves a point from a form to a GeoDjango `PointField` | FR-014 to FR-025 |
| US4: A developer narrows the bounds or sets the precision | FR-026 to FR-029 |

### Key Entities

- **Decimal degrees**: a coordinate written as one signed number of degrees, such as `51.5074` or
  `-0.1278`. North and east are positive.
- **WGS84 bounds**: the range a coordinate can take on the WGS84 reference: -90 to 90 for a
  latitude and -180 to 180 for a longitude, each inclusive.
- **Coordinate fields**: the latitude field, the longitude field and the point field together.
- **WKT text**: the well-known text form of a geometry. The point field writes it with its
  spatial reference in front, as `SRID=4326;POINT(<longitude> <latitude>)`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every value a person can submit, a coordinate field accepts it exactly when it
  lies inside the field's bounds with no more than its decimal places, and every accepted value
  comes back in decimal degrees.
- **SC-002**: On a page with IMask and the form's media loaded, a person cannot bring any input to
  hold a value outside the field's bounds or with more than its decimal places.
- **SC-003**: With every script blocked, a form using any coordinate field can still be filled in
  and submitted, and a value outside the bounds is reported as an error on the field.
- **SC-004**: A developer with a GeoDjango `PointField` on their model saves a typed point by
  declaring one field on the form, with no conversion of their own, and the package installs
  nothing spatial.
- **SC-005**: A form that uses no coordinate field loads no script from this package that it did
  not load before.
- **SC-006**: The point field is announced by assistive technology as one named group holding a
  named latitude and a named longitude.

## Assumptions

- A host project that wants the masked inputs loads IMask itself, as it does for the mask widgets
  of FS-015.
- A developer using the point field with a GeoDjango `PointField` declares the field on their form,
  since a model form otherwise builds GeoDjango's own map field for it.
- GeoDjango converts a point saved as WGS84 text into the spatial reference of the model's field
  when the two differ, so a model in another reference still receives a correct point. Reading
  such a point back into the form is refused (FR-024).
- Six decimal places, about eleven centimetres at the equator, is precise enough for the data
  these fields are for unless the developer says otherwise.
