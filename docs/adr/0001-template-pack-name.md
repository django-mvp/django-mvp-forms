# ADR 0001 — The template pack is named `daisyui`

**Status:** accepted

## Decision

The pack is selected with `CRISPY_TEMPLATE_PACK = "daisyui"`, and its templates live under
`mvp_forms/templates/daisyui/`. The name is public interface from the first release.

## Why

django-crispy-forms packs are named after the CSS framework they emit: `bootstrap5`, `tailwind`,
`bulma`. A host project reads the setting and knows what markup it will get.

Two other names were weighed. `mvp_forms` would suggest the pack needs django-mvp, which it must
not. `daisyui5` would force a rename at every daisyUI major version, while the roadmap plans for
one pack tested across the daisyUI versions it supports.

crispy-daisyui uses the same name, so a project cannot install both. That pack is the one this
package replaces, so a project has no reason to.

## Revisit if

A daisyUI major version changes its markup so far that one set of templates cannot serve both the
old and the new version.
