# ADR 0019 — A choice is stated on the form helper, and by one layout object

**Status:** accepted, amended by [ADR 0037](0037-fields-are-joined-by-a-layout-object-of-the-packs.md): the package defines a second layout object, `Join`

## Decision

A form states its size, colour and variant once, as one attribute on its helper instance:
`helper.daisyui = FormChoices(...)`, with `FormChoices` from `mvp_forms.choices`.

One field or one button states its own with `Choice`, the one layout object this package defines.
`Choice("search", size="lg")` and `Choice(Submit("save", "Save"), color="accent")` draw what they
hold with that choice, at any depth, and an inner `Choice` wins over an outer one, each of the
three kinds on its own. Holding nothing, a `Choice` is the value in
`FormChoices(fields={"search": Choice(size="lg")})`, which is how a form drawn without a layout
singles out one field.

This amends [ADR 0008](0008-layouts-use-django-crispy-forms-own-layout-objects.md), which said
the package defines no layout classes. Its rule still holds for every object django-crispy-forms
ships: none is subclassed and none is wrapped by a class of the same name.

The pack's tags read two names from the template context, `daisyui` and `daisyui_choice`. They
are the stated exception to the rule in [ADR 0006](0006-the-field-frame.md) that the frame reads
no bare name. A value under either name that is not a `FormChoices` or a `Choice` is the host
page's own and is ignored.

A later feature that needs a statement for one field or one button adds an argument to `Choice`.
It does not add a second layout object and does not subclass an upstream one.

## Why

A button in a layout is drawn before the form is in the template context, and a page may call its
form anything, so an attribute on the form cannot reach it. django-crispy-forms does pass every
attribute set on a helper instance into that context, and documents this as the way to give a
template pack a setting of its own. It is the only home every drawing path can read. The crispy
filter never reads a helper, so there the pack reads the form's `helper` itself.

A plain attribute for each choice, such as `helper.size`, was rejected. A misspelt attribute name
would do nothing and report nothing. A constructor refuses a keyword it does not know.

`Field` and the button classes of django-crispy-forms turn every keyword argument into an HTML
attribute, so they cannot carry a choice. Subclassing each would add five names that shadow
upstream ones, which is what ADR 0008 ruled out. One wrapper adds one name and leaves every
upstream object as its documentation describes it.

The statement has to be set on the helper instance. django-crispy-forms copies instance
attributes into the context and not class attributes, so a class attribute on a helper subclass
would reach the inputs and not the buttons of a layout.

## Revisit if

django-crispy-forms stops passing a helper's own attributes into the context, or gives layout
objects a way to carry arguments that a template pack can read.
