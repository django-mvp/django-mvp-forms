# Planning notes: Forms stay legible under every daisyUI theme

Rulings the maintainer gave for this repository on 2026-10-03. They bear on how the feature is
built. The plan answers each one by name.

Every input, button and component is built from daisyUI's component classes and modifiers. Plain
Tailwind layout utilities are used only where daisyUI has no component for the job (ADR 0003). The
package ships no stylesheet and defines no classes. A host page on daisyUI's documented CDN
install needs no build step.

Pack templates are plain Django templates. They never use django-cotton or daisy-cotton. Cotton is
for the demo project's own pages only. `{% include %}` is fine inside the pack.

This package never depends on django-mvp at runtime and never imports from it.

Size, colour and variant are stated through `FormChoices` on `helper.daisyui` and the `Choice`
layout object (ADRs 0019 to 0022). A new kind of input takes them by adding its rows to
`Modifiers`.

There is no support for carrying layouts over from other packs.

A feature adds its own demo page where it changes what a person sees, and its entry in the
README's public surface.

Nothing under `.github/` is changed by this work. If the check turns out to need a workflow
change, such as another entry in the test matrix, everything else is built and the workflow part
is filed as a separate request for the maintainer.

A decision that is durable, architectural and non-obvious is recorded under `docs/adr/` as well as
in `decisions.md`.
