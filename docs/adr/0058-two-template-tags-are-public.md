# ADR 0058 — `daisyui_field` and `daisyui_button` are public, and every other tag and filter is internal

**Status:** accepted, extends [ADR 0029](0029-every-pack-template-is-public.md)

## Decision

Of the tags and filters in `mvp_forms/templatetags/daisyui.py`, two are public API under Article
XI: `daisyui_field` and `daisyui_button`. For each, the pack promises:

- the tag's name, loaded with `{% load daisyui %}`;
- the argument it takes, and for `daisyui_field` the keyword options the pack's own templates pass
  it, such as `prepended=`, `appended=`, `join=`, `disabled=True`, `unlabelled=True`,
  `inline=True` and `member=True`;
- the parts of the result that the pack's own templates read: for `daisyui_field` the parts of
  `drawn` listed for `daisyui/frame.html` and `daisyui/field_body.html` in the README's template
  table, and for `daisyui_button` `drawn.css_class` and `drawn.flat_attrs`.

A release that renames either tag, or one of those options, keeps the old name working for one
minor version. The old name stays registered, does what the new one does and raises a
`DeprecationWarning` naming the new one. The CHANGELOG of that release says what replaces it, and
the release after removes the old name.

Every other tag and filter in `daisyui` is internal: `daisyui_button_size`, `daisyui_sized`,
`daisyui_host_template`, `daisyui_layout_object`, `daisyui_formset_table`, and the filters
`daisyui_classes`, `daisyui_shown`, `daisyui_date_part` and `daisyui_tab_group`. Any release may
rename, change or remove one, a patch release included. A replacement template that calls one may
need changing when the pack is upgraded.

The README says this beside its list of templates, in "The template tags a replacement calls".

## Why

A replacement is a copy of the pack's template with edits, so it calls whatever the pack's
template calls. Most of those calls are incidental to what a replacement changes, and a
replacement can leave them out or write the markup itself: a class list, the tab group's name,
the size written on a modal's close button.

`daisyui_field` and `daisyui_button` are different. They hand a template `drawn`, the pack's
drawing of a field or a button, and ADR 0029 already promises the parts of `drawn` a template
reads. A promise about `drawn.render` is empty if the tag that makes `drawn` can be renamed in a
patch release. Without these two a replacement of a field or a button template has to rebuild
the pack's drawing in its own Python, which is the work the template list exists to save.

Making every tag public would freeze helpers the pack added for its own templates and would
change for its own reasons, such as `daisyui_sized`, which exists only because
django-crispy-forms draws a `Modal` with no context. Making none public would leave the field
and button templates, the ones most often replaced, with nothing stable to start from.

A renamed tag fails loudly with `TemplateSyntaxError` when it is drawn, unlike a renamed handed
name, which Django draws as nothing. That is why the internal tags can change in any release: a
project finds out the first time its tests draw the form. The two public tags are kept stable
because a project should not have to rewrite its field template on a patch upgrade at all.

## Revisit if

Projects commonly replace a template that cannot be written without one of the internal tags,
such as `daisyui/table_inline_formset.html`, which is built on the `table` that
`daisyui_formset_table` hands it.
