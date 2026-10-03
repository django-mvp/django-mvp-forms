# Research: Replace one template without forking the pack

Read against `origin/main` at `8622e54` (v0.1.0). Citations are to the packages as resolved in
this project's environment: Django 6.1.1 and django-crispy-forms 2.7, under `.venv/`.

## Planning notes, answered

Each of the maintainer's notes in `planning-notes.md`, in its own words.

- **"Pack templates are plain Django templates. They never use django-cotton or daisy-cotton."**
  Adopted. This feature changes no pack template and adds none.
- **"This package never depends on django-mvp at runtime and never imports from it."** Adopted.
  The one module added, `mvp_forms/deprecation.py`, imports from Django and the standard library.
- **"The class policy is ADR 0003."** Adopted, and untouched: no markup is added to the pack.
- **"Each feature adds its own demo page where it changes what a person sees, and its entry in
  the README's public surface."** Adopted for the README. No demo page: nothing a person sees
  changes (D10).
- **"Nothing under `.github/` is changed by a feature."** Adopted. The checks run in the existing
  suite.
- **"A document reads as its current state."** Adopted. The list and the CHANGELOG carry no
  revision notes. A path on its way out has a table of its own in the README, in plain words.
- **"There is no support for carrying layouts over from other packs."** Adopted. Nothing here
  touches it.

## R1. A replacement is already found, on two routes

Every pack template is loaded by its path, through one of two engines.

**The page route.** django-crispy-forms asks Django's template loading for
`"%s/<name>.html" % template_pack`:

- the form templates, through `get_template`: `uni_form.html` and `uni_formset.html`
  (`crispy_forms/templatetags/crispy_forms_filters.py:14-21`), `errors.html` and
  `errors_formset.html` (`:77-80`), `whole_uni_form.html` and `whole_uni_formset.html`
  (`crispy_forms/templatetags/crispy_forms_tags.py:188-195`), `field.html`
  (`crispy_forms/utils.py:24-26`);
- every layout object's template, through `render_to_string` on the name its class holds
  (`crispy_forms/layout.py:19-23` and each class's `template`, such as `layout.py:731`
  `"%s/layout/div.html"`; `crispy_forms/bootstrap.py:715` `"%s/layout/tab-link.html"`).

The pack's own templates draw one another with `{% include "daisyui/…" %}`, which resolves
through the engine of the template being drawn. `get_template` and `{% include %}` search the
engines in `TEMPLATES`: each engine's `DIRS` first, then the `templates` directory of every app in
`INSTALLED_APPS`, in order.

So a file at the same path in a `DIRS` directory, or in an app listed before `mvp_forms`, is
found first. Probed in this environment: a `daisyui/required_marker.html` in a `DIRS` directory
was drawn for both required fields of a form, with nothing else changed.

**The form renderer route.** The templates under `daisyui/widgets/` are named by
`FieldInput.templates` and `FieldInput.inline_templates`
(`mvp_forms/templatetags/daisyui.py:108-117`) and set on a copy of the widget (ADR 0012). Django
renders a widget through the form's renderer, not through `TEMPLATES`. The default renderer,
`django.forms.renderers.DjangoTemplates`, builds an engine of its own whose `DIRS` is Django's
built-in form templates and whose `APP_DIRS` is on (`django/forms/renderers.py:31-44`). It never
reads the project's `TEMPLATES`. The includes inside a widget template resolve through that same
engine.

So with the default renderer a replacement for a widget template is found only in the
`templates` directory of an app listed before `mvp_forms`. A project that keeps its replacement
in a `DIRS` directory needs `FORM_RENDERER = "django.forms.renderers.TemplatesSetting"`
(`renderers.py:70-78`, which calls `get_template`), and then `django.forms` in `INSTALLED_APPS`
so Django's own widget templates are still found. Probed both ways: with the default renderer a
`daisyui/widgets/group.html` in `DIRS` was not used, and with `TemplatesSetting` it was.

**Consequence.** The first story needs no change to the pack. Its work is the tests that hold
the behaviour in place for every template, and the edge cases around placement.

## R2. Which templates are on which route

The form renderer route is exactly the values of `FieldInput.templates` and
`FieldInput.inline_templates`, plus every template those include: `widgets/group.html`,
`widgets/inline_group.html`, `widgets/select_date.html`, `widgets/clearable_file_input.html`,
`widgets/group_options.html` and `widgets/attrs.html`. The other forty are on the page route.
No template is included from both routes. The check computes the route this way and does not
trust the directory name.

## R3. One template whose output the pack does not draw

`daisyui/layout/tab-link.html` is rendered by django-crispy-forms for every `Tab`
(`crispy_forms/bootstrap.py:723`) and the result is handed to `layout/tab.html` as `links`
(`bootstrap.py:782-786`). The pack's `tab.html` draws tabs as radios and does not draw `links`.
The file has to exist, or `render_to_string` raises. A replacement for it is rendered, and its
output shows only where a replacement for `layout/tab.html` draws `links`. The list says so.

## R4. Templates django-crispy-forms keeps in memory

Five templates are loaded through functions wrapped in `functools.lru_cache`: `field.html`
(`crispy_forms/utils.py:24`), `uni_form.html` and `uni_formset.html`
(`crispy_forms_filters.py:14,19`), `whole_uni_form.html` and `whole_uni_formset.html`
(`crispy_forms_tags.py:188,193`). Django's development server resets its own template loaders
when a template file changes (`django/template/autoreload.py:33-45`) but knows nothing of these
caches. A replacement for one of the five that is added or edited while the server runs is not
picked up until it restarts. The README says so. The test suite already clears them
(`tests/conftest.py`, `clear_crispy_template_caches`).

## R5. What a template is handed

"Handed" is read as D3 has it: the names the pack's own template reads from outside itself. They
are found by compiling the template and walking its nodes, which is exact where a regular
expression is not:

- a `{{ variable }}`, a tag argument and a filter argument are each a `FilterExpression` whose
  `var` is a `Variable` with `lookups`, or a literal with none
  (`django/template/base.py`, `Variable.__init__`);
- `{% for %}` binds its loop variables and `forloop` inside its body, `{% with %}` binds its
  names inside its body, and a tag used with `as name` binds `name` for what follows it. Those
  are the template's own and are not handed;
- `{% include … with name=value %}` reads `value` and binds nothing in the including template.

A name is its first lookup: `field.auto_id` is `field`. Two values are the pack's own objects,
`drawn` (a `FieldInput`, or a `DrawnButton` in the two button templates) and `table` (a
`FormsetTable`). For those the promise reaches the part read, as D3 says, so they are listed and
checked one level down: `drawn.is_group`, `table.rows`. Everything else belongs to Django or to
django-crispy-forms and is listed by its name alone.

`widget.removal_class` is the one part the pack adds to a value of Django's
(`FieldInput.removal_context`). It is named in the entry for `widgets/clearable_file_input.html`
in words.

## R6. Proving a replacement is handed the same

The same context reaches whichever template Django finds at the path, so a replacement that is a
copy of the pack's template with a marker added must draw what the pack draws, plus the marker.
That is a test that needs no knowledge of the names: for each distributed template, draw every
entry of `STATES` (`tests/test_pack/test_independence.py:389`) with the copy in place, strip the
marker, and compare with the output drawn with nothing replaced. The marker is compared as a
string, since `widgets/attrs.html` is included inside a tag where markup cannot go. Tab and
accordion ids are random and are normalised first, as FS-008's comparison did.

Each template must be reached by at least one state, or the comparison proves nothing for it.
`tab-link.html` is the exception (R3) and is tested with a replacement for `tab.html` beside it.

## R7. Changing a listed template later

Nothing is renamed in this release. What is built is the one thing a later release cannot do
without: a way to honour a replacement at a path the pack no longer ships, and to warn about it.

- A draw site that the pack controls is an `{% include %}` in a pack template or a name in
  `FieldInput.templates`. A release that moves a template changes that site to ask first whether
  the host project has a template at the old path.
- The pack no longer ships the old path, so a template found there is the host project's. Asking
  is one `get_template` on the engine that would draw it: the including template's engine in a
  template, the form's renderer in `FieldInput`. Django's cached loader remembers a miss, so a
  project with nothing there pays for one lookup.
- When one is found the pack draws it and raises a `DeprecationWarning` naming the old path and
  what replaces it. When none is found nothing is raised. This is FR-013 as written, and it
  covers a template the pack stops using as well as one it renames.
- The paths django-crispy-forms chooses (`"%s/layout/div.html"` and the rest) are not the pack's
  to rename. They change only if django-crispy-forms changes them.
- For a name a template is handed (FR-014) nothing can be built ahead: the release that renames
  one supplies both names for a minor version. D5 already rules out a warning for it.

The registry of withdrawn paths is empty in this release. It is also what the list check reads,
so a withdrawn path has to stay on the README's list for as long as it is honoured (FR-015).

## R8. What stays out

- Named blocks inside pack templates (D7, #91).
- A setting or a registry for replacements (D4).
- A demo page (D10).
- Whether the pack's template tags, which a copied template calls, are public in the same sense
  as the paths. A renamed tag fails loudly, with `TemplateSyntaxError`, which is not the quiet
  break the issue is about. Asked in #115.
