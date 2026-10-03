# Planning notes: tabs, accordion, modal and alert in a layout

Rulings given when the specification was approved on 2026-10-03. They say how to build the feature, which `spec.md` deliberately does not. The plan for the build has to answer each note by name.

## Script-free mechanisms first, an inline handler only where there is none

Build each of these from daisyUI's script-free mechanisms wherever one exists: radio-driven tabs, a radio or `details` accordion, and the `dialog` element closed by a form with the dialog method. Use an inline handler only where no script-free mechanism exists, and say so in the decision record written with the build. This is the working answer to issue #47, which stays open for the maintainer to confirm.

The notes for planning in `decisions.md` list the places already known to have no script-free answer: dismissing an alert, and closing a modal that sits inside the form it belongs to, where a second form cannot be nested.

## daisyUI classes for everything daisyUI has, Tailwind layout utilities for the rest

Use daisyUI's own classes for tabs, collapse, modal, alert and every other part daisyUI covers. Plain Tailwind layout utilities are allowed only where daisyUI has nothing for the job, because daisyUI's documented CDN install loads Tailwind's browser build beside the stylesheet. This is the working answer to issues #16 and #18.

## The pack is named daisyui

The template pack's name is `daisyui`, as FS-001 decided. Templates this feature adds live under that name, and the demo pages and README use it.

## Marking every tab or group with an error stays out

Issue #46 stays open. The build opens the first tab or group holding an error and marks nothing else.
