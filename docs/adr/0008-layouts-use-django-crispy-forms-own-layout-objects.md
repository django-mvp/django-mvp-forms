# ADR 0008 — Layouts use django-crispy-forms' own layout objects

**Status:** accepted, amended by [ADR 0017](0017-a-choice-is-stated-on-the-helper-and-by-one-layout-object.md): the package defines one layout object, `Choice`

## Decision

A developer imports `Fieldset`, `Row`, `Submit` and every other layout object from
django-crispy-forms, from `crispy_forms.layout` or `crispy_forms.bootstrap` as its documentation
says. The pack supplies a template for each one at the path django-crispy-forms asks for,
`daisyui/layout/<name>.html`. The package defines no layout classes, no subclasses of them and no
wrappers around them.

The names each template reads are the ones django-crispy-forms sets for that template and no
others. Attributes are read from the template's own object, such as `div.flat_attrs`, and never
as a bare name.

Buttons added to a form helper with `add_input` are drawn by `daisyui/inputs.html`, which the form
wrapper includes after the fields. An input object is drawn with the same template as in a layout.
An object that draws itself, such as a `StrictButton`, is drawn by its own `render` through the
tag `daisyui_layout_object`. Hidden inputs are drawn outside the container that holds the buttons.

## Why

Article XIV says that where django-crispy-forms documents how a layout object behaves, the pack
matches it. A second set of classes would give every object two names and make the upstream
documentation wrong for this pack. crispy-tailwind ships its own `Submit`, `Reset` and `Button`
to change their default classes, and a layout written from the upstream documentation then gets
unstyled buttons. Here the same layout code draws correctly.

The cost is that the pack cannot change what an object's Python does. It draws `Hidden` without
the class and generated id upstream gives it, and it drops a few class names by name. See ADR
0010.

Most layout objects render their template with the whole page context, and django-crispy-forms
leaves the names it set for earlier objects in that context. A template that read a bare name
could pick up a page variable or a sibling's value. This is the rule ADR 0006 set for the field
frame.

## Revisit if

A later feature needs an argument the upstream classes cannot carry. Choosing a size, colour or
variant from Python is the likely one.
