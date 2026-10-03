# Planning notes: text inputs drawn as daisyUI

Notes for whoever plans and builds this feature. They say things about how, which the specification does not. Each one is to be answered by name in the plan.

## From the maintainer, 2026-10-03

These were given when the repository was set up. They are paraphrased, not quoted.

The pack limits itself to daisyUI's standard classes and modifiers, so that a host page loading daisyUI's full CDN build needs no build step. A host project with its own Tailwind build works that out itself.

Pack templates are plain Django templates and never use django-cotton or daisy-cotton. A preference for Cotton components over `{% include %}` applies to the demo project's own pages only, never to anything the package distributes.

The package never depends on django-mvp at runtime and never imports from it.

No support for carrying layouts over from other packs. Goal G10 is rejected.

Each feature adds its own demo page or pages and its own README public-surface entry.

## From writing the specification

The demo project currently selects the `tailwind` pack and installs `crispy_tailwind`. FR-031 has it use this pack instead. django-mvp's own pages in the shell, such as sign-in, draw forms too, so check what they look like once the setting changes and before #6 lands.

Django 5.0 and later put `aria-describedby` and `aria-invalid` on the widget themselves, and the ids they point at follow a fixed pattern. FR-018 exists so the pack's ids match that pattern and are not invented. Check each supported Django version, because what is emitted for errors differs between them.

FR-026 needs something to compare against. A list of the classes in daisyUI's CDN stylesheet has to come from somewhere a test can read without the network.

Features #6 and #7 are specified at the same time as this one and will draw through the field frame. Keep the frame's template paths and context stable once they are chosen, and say what they are in the plan so those builds can rely on them.
