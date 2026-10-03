# Planning notes: Rating and range inputs

Rulings the maintainer gave for this repository on 2026-10-03. They bear on how the feature is
built. The plan answers each one by name.

Every input, button and component is drawn with daisyUI's component classes and modifiers. A plain
Tailwind utility is used only for layout, and only where daisyUI has no component for the job. The
package ships no stylesheet and defines no classes. A host page on daisyUI's documented CDN
install needs no build step.

Pack templates are plain Django templates. They never use django-cotton or daisy-cotton, which are
for the demo project's own pages only. `{% include %}` is fine inside the pack.

This package never depends on django-mvp at runtime and never imports from it.

Size, colour and variant are stated through `FormChoices` on `helper.daisyui` and the `Choice`
layout object. A new kind of input takes them by adding its rows to `Modifiers`.

There is no support for carrying layouts over from other packs. Fields and widgets beyond the
roadmap arrive as a project needs them, and not through this feature.

Each feature adds its own demo page or pages where it changes what a person sees, and its own
entry in the README's public surface.

Nothing under `.github/` is changed by this work.
