# Planning notes: layout objects for structure and buttons

Rulings given when the specification was approved on 2026-10-03. They say how to build the feature, which `spec.md` deliberately does not. The plan for the build has to answer each note by name.

## Rows and columns may use Tailwind layout utilities

daisyUI has no grid component. Its documented CDN install loads Tailwind's browser build beside the stylesheet, and that provides layout utilities with no build step. So where daisyUI has no component for the job, which here means laying columns side by side, plain Tailwind layout utilities are allowed. Inputs, buttons and every other part that daisyUI does have a component for stay on daisyUI classes only. This is the working answer to issue #18, which stays open for the maintainer to confirm.

## StrictButton, Hidden and MultiField stay in this feature

All three are drawn here. If the specification for issue #8 also claims `StrictButton`, that specification drops it and this one keeps it.

## The pack is named daisyui

The template pack's name is `daisyui`, as FS-001 decided. Templates this feature adds live under that name, and the demo pages and README use it.
