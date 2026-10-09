# ADR 0044 — Options are grouped by a template that extends django-tomselect's

**Status:** accepted

## Decision

The package distributes `mvp_forms/templates/django_tomselect/tomselect.html`. It extends
django-tomselect's template of the same path and adds two settings to Tom Select's configuration,
so that an option that carries an `optgroup` key is listed under a heading of that name. An option
with no such key, and every option of a control whose view sends none, is listed as before.

A developer names the group by returning `optgroup` on each result of the autocomplete view.

The template is found ahead of django-tomselect's only when `mvp_forms` is listed before
`django_tomselect` in `INSTALLED_APPS`. Listed the other way round, nothing is grouped and
nothing breaks.

It is the one template the package distributes outside `daisyui/`. It is listed in the README in
a table of its own, it names only django-tomselect's template of the same path, and the checks
that hold every pack template to daisyUI and to replacement apply to `daisyui/` (ADR 0029). The
two tables together are compared with every template the package distributes.

## Why

django-tomselect draws a group heading and has no setting that tells Tom Select which group an
option fetched from the server belongs to. Every project that wanted groups carried the same
template. A widget subclass would make the package depend on django-tomselect. A script would be
the first the package ships. Telling the developer to write the template is what the feature set
out to end.

This is the one place the package adds to django-tomselect's behaviour and not only to its look.
It touches django-tomselect through a block its template offers for the purpose.

## Revisit if

django-tomselect gains a setting that names an option's group. This template is then removed in
favour of it.
