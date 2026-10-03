# ADR 0003 — daisyUI classes for every component, Tailwind utilities for layout only

**Status:** accepted

## Decision

Every input, button and component the pack draws is built from daisyUI's component classes and
their modifiers. A plain Tailwind utility is allowed only for layout, and only where daisyUI has
no component for the job, such as putting columns side by side. The package ships no stylesheet
and defines no class of its own.

A test compares every class the pack writes with the class names in daisyUI's published CDN
stylesheet, kept in `tests/data/daisyui-classes.txt`. A feature that needs a layout utility adds
it to that test by name, so each one is a visible, reviewed exception.

The first such utility is `w-full`. See ADR 0007.

## Why

The pack has to work on a page that has no build step. daisyUI's documented CDN install is its
stylesheet plus Tailwind's browser build, which generates utilities in the page as it finds them.
So both kinds of class work there, and a host project needs nothing else.

Restricting components to daisyUI's own classes keeps the pack looking like the rest of a daisyUI
site under every theme. A look-alike assembled from utilities would drift from the theme the host
project chose.

A stricter rule was considered first: only classes found in the CDN stylesheet, with no Tailwind
utility at all. It cannot lay out a row of columns, because daisyUI has no grid component.

A host project with its own Tailwind build has to make that build scan the package's templates.
The README says so.

## Revisit if

daisyUI stops documenting Tailwind's browser build as part of its CDN install, or gains layout
components that make the utilities unnecessary.
