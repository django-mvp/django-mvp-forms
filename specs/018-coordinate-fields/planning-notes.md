# Planning notes: Latitude, longitude and point fields

Suggestions from the maintainer on how this might be built, in his words where he gave them.
Research answers each one by name: adopted or not adopted, and why.

## 1. A point field for GeoDjango without depending on GeoDjango

"It might be nice to have a combined "CoordinatesField" which combines both into a single field.
The idea would be that I could use it for a GeoDjango PointField. However, I do not want to add
geodjango as a dependency to ensure it works. If we could create it without doing that, it might
be cool."

He then chose WKT text as what the field hands back, and asked for it to be named `PointField`
"to match expectations".

## 2. Proving a real `PointField` takes the text

Raised while grilling and left for planning: the tests can check the text the field produces and
read back a stand-in object with `x`, `y` and `srid`, but they can only save to a real GeoDjango
`PointField` where GEOS is installed, which is a system library and not a Python package. Decide
whether the suite proves the round trip against GeoDjango (for example, a test that runs only where
GEOS is present, or a CI job that installs it) or relies on GeoDjango's documented acceptance of
WKT text, keeping in mind that the maintainer does not want GeoDjango as a dependency.

## 3. One of the existing IMask widgets

"The fields will utilize one of our IMask widgets to control what the user types."
