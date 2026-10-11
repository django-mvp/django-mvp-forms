# ADR 0055 — One stylesheet draws Tom Select controls, from django-tomselect or from the package's own widgets

**Status:** accepted, supersedes [ADR 0042](0042-one-optional-stylesheet-for-each-supported-package.md)

## Decision

`mvp_forms/static/mvp_forms/tomselect.css` draws every Tom Select control: one django-tomselect
builds, and one started on a select that `TomSelect` or `TomSelectMultiple` drew. The package's
own widgets get no stylesheet of their own.

Everything else ADR 0042 decided still holds:

- The host project loads the stylesheet. No pack template, no template tag and no widget's
  media names it.
- It applies only to Tom Select controls, their dropdown, the element django-tomselect
  announces a choice in, and a box that holds an open control and would otherwise cut its
  dropdown off. A page with no control is drawn as before.
- It names no colour of its own. Every colour is one of the theme's variables, alone or mixed.
- A supported package whose controls are built in the browser has a file of its own. There is
  never one stylesheet for several packages.
- The pack's own templates still define no class and need no stylesheet.
- The control's outer box is not restyled. The pack writes daisyUI's `select` class, with the
  stated size, colour and variant, on the select element, and Tom Select copies those classes
  to the wrapper it builds.
- Every selector inside a control starts with `html:root`, so the rules win over Tom Select's
  own stylesheet whichever of the two a page loads first.

## Why

ADR 0042 said the file applies only to django-tomselect's controls. Its rules were written
against the parts Tom Select builds, and the package's own widgets start Tom Select on an
ordinary select, so they build the same parts. A second file would repeat every rule and the two
would drift apart. A page that used both kinds of control would load both.

What ADR 0042 protected is unchanged. A project loads one file when it uses a Tom Select
control and none when it does not.

One file is also what makes the two kinds of control look the same on a page, which is the
reason for offering the widgets beside django-tomselect's fields.

Article XIV of the constitution was amended to allow this before the widgets were built.

## Revisit if

daisyUI ships a component for a searchable select, or Tom Select gains a way to take class names
for every part it builds, so that the control could be drawn with daisyUI's classes alone.
