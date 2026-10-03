# ADR 0017 — A formset's layout is chosen with the helper's template

**Status:** accepted

## Decision

The pack draws a formset stacked unless the formset's helper names another template. The table
is chosen with `helper.template = "daisyui/table_inline_formset.html"`. The pack adds no setting,
no template tag argument and no helper class for it.

The formset templates carry the names django-crispy-forms asks a pack for:
`daisyui/whole_uni_formset.html` for `{% crispy formset %}`, `daisyui/uni_formset.html` for
`{{ formset|crispy }}` and `daisyui/errors_formset.html` for `{{ formset|as_crispy_errors }}`.
The table carries the name other packs written for django-crispy-forms give theirs. All four
paths are public surface.

## Why

django-crispy-forms already has a setting for the template a form or a formset is drawn with,
and packs written for it publish a table under this name to be chosen there. A developer coming
from one of them changes the pack's prefix and nothing else. The README makes matching
django-crispy-forms' documented behaviour the rule over inventing a new one, and a second way to
choose a layout would have to be kept in step with the first.

Stacked is the default because it is what django-crispy-forms draws when nothing is chosen, and
it is the only layout that can be drawn through `{{ formset|crispy }}`, which has no helper.

## Revisit if

django-crispy-forms adds a setting of its own for a formset's layout, or a third layout is
wanted that a template name cannot express.
