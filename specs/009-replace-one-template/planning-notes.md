# Planning notes: Replace one template without forking the pack

Rulings the maintainer gave for this repository on 2026-10-03. They bear on how the feature is
built, and they are stricter than the README where the two differ. The plan answers each one by
name.

Pack templates are plain Django templates. They never use django-cotton or daisy-cotton. Cotton is
for the demo project's own pages only. `{% include %}` is fine inside the pack.

This package never depends on django-mvp at runtime and never imports from it.

The class policy is ADR 0003: daisyUI component classes and modifiers for every input, button and
component, and plain Tailwind layout utilities only where daisyUI has no component for the job. The
package ships no stylesheet and defines no classes.

Each feature adds its own demo page where it changes what a person sees, and its entry in the
README's public surface.

Nothing under `.github/` is changed by a feature. A workflow change is a separate request to the
maintainer.

A document reads as its current state. The template list and the CHANGELOG carry no dated revision
notes and no strikethrough. A path that is on its way out is marked as such in plain words.

There is no support for carrying layouts over from other packs.
