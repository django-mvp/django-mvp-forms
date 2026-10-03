# ADR 0029 — Every template the pack distributes is public, with the names it reads

**Status:** accepted

## Decision

Every template under `mvp_forms/templates/daisyui/` is public API under Article XI. There are no
private templates. For each one the pack promises three things: its path, what it is asked to
draw, and the names it is handed.

The README's section "Replacing one template" lists them in one table. A template the package
distributes is on the list, and a feature that adds a template adds its row in the same pull
request.

**What "handed" means.** The names the pack's own template reads from outside itself. A value
Django or django-crispy-forms supplies, such as `field`, `form` or `widget`, is promised by its
name. `drawn` and `table` are the pack's own objects, so each part of them that a template reads
is promised too, one level down, as `drawn.is_group`. A property of `FieldInput` or
`FormsetTable` that a pack template reads is therefore public in the same sense as a path.

**How a replacement is found.** By Django's template loading and nothing else. The pack has no
setting, registry or hook for it. Templates outside `daisyui/widgets/` are found through
`TEMPLATES`. Those under it are loaded by the form renderer (ADR 0012), which with Django's
default renderer looks only in installed apps. Every pack template that draws another names it
by its listed path, in an `{% include %}` or in `FieldInput.templates`, so that a replacement of
the inner one is used.

**The check.** `tests/test_pack/test_template_list.py` reads the README's table and the package
and fails on a distributed template that is not listed, a listed path that is not distributed, a
name a template reads that its row leaves out, and a route listed wrongly. It refuses a template
that uses a tag it cannot read, so that a new tag is taught to the check before it is used.
`tests/test_pack/test_replacements.py` replaces every distributed template in turn with a copy
of itself and requires every form in the suite's list of states to come out the same.

**Changing a listed template.** A path, or a name a template is handed, changes only through one
minor version in which the old one still works. A release that moves a template or stops using
one:

1. adds the old path to `WITHDRAWN` in `mvp_forms/deprecation.py`, with the path that replaces
   it or `None`;
2. changes the place the template is drawn from to ask first for the host project's template at
   the old path: `{% daisyui_host_template "daisyui/old.html" as name %}` followed by
   `{% if name %}{% include name %}{% endif %}` in a template, or `host_template` with the form
   renderer's `get_template` in `FieldInput`;
3. keeps the old path's row in the README's table, saying what replaces it;
4. says what changed and what replaces it in the CHANGELOG.

The release after that removes all four. The pack no longer ships the old path, so a template
found there is the host project's: it is drawn, and a `DeprecationWarning` names the old path
and its replacement. A project with nothing there is not warned.

A release that renames a name a template is handed supplies both names for that version. There
is no warning for it.

The markup and the class names inside a template are not part of this and change freely.

## Why

A host project can put a file at any pack template's path whether or not the pack calls that
path public, because that is how Django finds templates. A template left off the list would
still be replaced by somebody and would then break without notice, which is what the list exists
to end.

A path alone is not enough. A replacement is a copy of the pack's template with edits, and it
reads what the original read. Django draws an unknown name as nothing and raises no error, so a
renamed name breaks a replacement silently. Promising everything a template can reach would
freeze far more of the pack's Python than any template uses. "Whatever the pack's own template
reads" has a clear edge and can be checked by a test.

A setting that maps a pack template to a replacement would be a second mechanism beside the one
every Django developer already knows.

For a moved template, three other ways were weighed. A check when the project starts does not
run under a production server. A template left at the old path that forwards to the new one
cannot tell a replacement from itself, so it cannot warn only the projects that have one.
Sending every `{% include %}` through the tag now would add a lookup to every draw for a table
with nothing in it. Asking at the one place that moved costs one lookup, which Django's cached
loader remembers when it misses.

The pack cannot see what a replacement reads, so it cannot warn about a renamed name without
warning every project.

## Revisit if

The pack's templates gain named blocks, which would make each block name part of this surface.
django-crispy-forms renames one of the paths it chooses, such as `%s/layout/div.html`, which the
pack cannot intercept from a template. Or the pack's template tags, which a copied template
calls, are ruled public or private.
