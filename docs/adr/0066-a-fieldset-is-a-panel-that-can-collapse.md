# ADR 0066 — A fieldset is a panel, and the package's own Fieldset can collapse

**Status:** accepted. Extends [ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md): the panel's colours and the collapsible fieldset's parts are Tailwind utilities, named in the class test

## Decision

Every `Fieldset` is drawn as the panel daisyUI's fieldset documentation shows: `bg-base-200
border-base-300 rounded-box border p-4`, without the `w-xs` that only sizes the documentation's
preview, and with `mb-4` so that panels one after another do not touch.

`mvp_forms.layout.Fieldset` subclasses django-crispy-forms' `Fieldset` and adds three keyword
arguments, taken off before django-crispy-forms writes the rest as attributes:

- `description`, help text drawn before the first field and named by the fieldset's
  `aria-describedby`
- `collapsible`, which makes the legend open and close the fieldset
- `state`, `"open"` or `"closed"`, closed when not given

A collapsible fieldset is drawn with a visually hidden checkbox before its legend, labelled by the
legend. Open, the legend sits on the border. Closed, the legend is floated, which takes it off the
border and into the panel as a title, and the fields are hidden. A drawn minus or plus beside the
legend, sized to the legend's capital letters, shows the way it will go. All of it is done with
Tailwind utilities on the fieldset's parts, `peer-checked:` among them. A fieldset holding a field in
error is drawn open, with the error mark an accordion group carries.

## Why

daisyUI styles a `fieldset` hardly at all, so a group's start and end were not visible (#226). The
panel is daisyUI's own documented composition, and every class in it is one daisyUI defines or a
theme colour, so it follows the theme.

Collapsing follows the Django admin's fieldsets, which developers already know. daisyUI's `collapse`
on a `<details>` element was tried first. It needs no utilities, but a `<summary>` cannot be a
fieldset's legend, so an open fieldset could not keep its legend on the border, which was the look
chosen. Only a `<legend>` can sit on a fieldset's border, and it has to be the fieldset's own child,
so the control is a checkbox beside it. A stylesheet of the package's own would also have done it,
and the constitution allows one only for a supported package's controls.

The cost is in what assistive technology announces. A checkbox is read as checked or not checked,
where a `<summary>` is read as expanded or collapsed. The checkbox is labelled by the legend and
reachable and operable from the keyboard, so nothing is out of reach, but the words are less exact.

The ids start with the fieldset's `css_id` or its legend made into a slug, as django-crispy-forms
names an accordion group, and with the form's prefix, because the forms of a formset draw the same
layout.

## Revisit if

daisyUI gains a fieldset that collapses, or browsers let a `<summary>` act as a fieldset's legend.
