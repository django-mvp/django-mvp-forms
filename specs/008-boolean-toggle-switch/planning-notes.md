# Planning notes: Booleans drawn as a checkbox, toggle or switch

Rulings the maintainer gave when this repository was set up, on 2026-10-03. They bear on how the
feature is built, and they are stricter than the README where the two differ. The plan answers
each one by name.

The pack limits itself to daisyUI's standard classes and modifiers, so that a host page loading
daisyUI's full CDN build needs no build step. A host project with its own Tailwind build works out
that configuration itself.

Pack templates are plain Django templates. They never use django-cotton or daisy-cotton. Guidance
elsewhere to prefer Cotton components over `{% include %}` applies to the demo project's own pages
and not to anything this package distributes.

This package never depends on django-mvp at runtime and never imports from it.

The pack draws formsets handed to it. Adding and removing rows in the browser, form views and form
page templates belong to django-mvp.

There is no support for carrying layouts over from other packs.

Each feature adds its own demo page or pages to the demo project, and its own entry in the
README's public surface.
