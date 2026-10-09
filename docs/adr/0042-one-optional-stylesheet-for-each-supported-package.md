# ADR 0042 — One optional stylesheet for each supported package, loaded by the host project

**Status:** accepted

## Decision

Where a supported third-party package builds its controls in the browser, under class names of
its own, the package ships one stylesheet for that package's controls. The first is
`mvp_forms/static/mvp_forms/tomselect.css`, for django-tomselect.

- The host project loads it. No pack template, no template tag and no widget's media names it.
- It applies only to that package's controls. For `tomselect.css` that is a Tom Select control,
  its dropdown, the element django-tomselect announces a choice in, and a box that holds an open
  control and would otherwise cut its dropdown off. A page with no control is drawn as before.
- It names no colour of its own. Every colour is one of the theme's variables, alone or mixed.
- Each supported package has a file of its own. There is never one stylesheet for several.
- The pack's own templates still define no class and need no stylesheet.

The control's outer box is not restyled. The pack writes daisyUI's `select` class, with the
stated size, colour and variant, on the select element, and Tom Select copies those classes to
the wrapper it builds. The stylesheet fits Tom Select's parts inside that box and draws the
dropdown as daisyUI draws the options of its own select.

Every selector inside a control starts with `:root`, so the rules win over Tom Select's own
stylesheet whichever of the two a page loads first.

## Why

A control built by script has no template the pack could put daisyUI classes on, so "the pack
ships no stylesheet" (ADR 0003, Article XIV before its amendment) left such a control in its
vendor's look, and every project that used one wrote the same stylesheet.

A stylesheet the widget loaded through its media would arrive on pages whose owner never chose
it. One stylesheet for every supported package would grow with each package and be paid for by
projects that use none of them. Replacing Tom Select's stylesheet outright would mean carrying
its layout rules as well as its colours, and following them from release to release.

Reusing daisyUI's `select` on the wrapper keeps the size, colour, variant, focus and error states
in daisyUI's hands, which is what Article XIV asks for wherever daisyUI has a component.

ADR 0034 rests on the pack shipping no stylesheet. It still holds for what the pack's own
templates draw. This file corrects nothing daisyUI draws: it draws what daisyUI does not.

## Revisit if

daisyUI ships a component for a searchable select, or Tom Select gains a way to take class names
for every part it builds, so that the control could be drawn with daisyUI's classes alone.
