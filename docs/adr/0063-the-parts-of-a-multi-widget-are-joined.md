# ADR 0063 — The parts of a multi-widget are joined

**Status:** accepted

## Decision

A multi-widget drawn through Django's own multi-widget template
(`django/forms/widgets/multiwidget.html`), whose visible parts are all drawn as an input or a
select, is drawn as one daisyUI join. The visible parts sit inside `<div class="join w-full">` and
any hidden parts follow it, outside the join. The pack writes the template for this,
`daisyui/widgets/joined_parts.html`, on a copy of the widget for each render.

Each joined part takes `join-item` and the width of a member of a `Join`: an input takes `flex-1`
and a select takes `w-auto`, in place of `w-full`. The size, colour, variant and error modifier
reach every part as before. A select's `step="any"` attribute is left alone.

A widget with a template of its own is not joined, and neither is one with a visible part that is
not an input or a select. That leaves the split date and time, the partial date, the point, the
range and the image input as they were.

Each part keeps the field's label as its `aria-label`. A developer names a part, such as the unit,
with `MultiWidgetField(..., attrs=({"aria-label": "Weight"}, {"aria-label": "Weight unit"}))`.

## Why

Django's stock multi-widget template writes its parts one after another, so the pack owns how they
are arranged. A number and its unit read as one value, and drawn as separate full-width controls
they read as two.

The join reuses the member widths of a `Join` (ADR 0037) and keeps one size across a joined group
(ADR 0026), so no new classes or rules are added.

The rule recognises no package's class (ADR 0053). It applies to every multi-widget that meets it,
and django-pint's `QuantityWidget` is the first case.

The unit part keeps the field's label (ADR 0027) because the pack cannot know that a part is a
unit without recognising the class. `MultiWidgetField` is the developer's route to a better name.

## Revisit if

django-pint lets a developer give each part of its widget its own attributes.
