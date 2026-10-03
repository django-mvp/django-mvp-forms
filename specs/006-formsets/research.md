# Research: formsets drawn stacked or as a table

Read against `origin/main` at `23d5139` (FS-001, FS-002 and FS-003 merged) and the packages the
project resolves: django-crispy-forms 2.7 and Django 6.1.1, under
`.venv/lib/python3.13/site-packages/`. Paths below that start `crispy_forms/` or `django/` are in
that directory.

The specification directory has no `planning-notes.md` and the feature had no prototype, so there
is nothing from either to answer.

## R1. What django-crispy-forms asks the pack for

A formset reaches the pack two ways.

- **`{% crispy formset %}`**, with or without a helper. `BasicNode.get_render`
  (`crispy_forms/templatetags/crispy_forms_tags.py:76`) sees a `BaseFormSet`, builds the context
  under `formset_*` names (`formset_tag`, `formset_method`, `formset_action`,
  `formset_error_title`, line 147) and puts the formset in the context as `formset`.
  `CrispyFormNode.render` (line 203) then draws `helper.template` when the helper names one, and
  `<pack>/whole_uni_formset.html` when it does not. A formset with no `helper` attribute gets a
  bare `FormHelper()` (line 100), so it takes the same default.
- **`{{ formset|crispy }}`**. `as_crispy_form`
  (`crispy_forms/templatetags/crispy_forms_filters.py:28`) draws `<pack>/uni_formset.html` with
  `formset`, `field_template`, `form_show_errors`, `form_show_labels`, `label_class` and
  `field_class` and nothing else. There is no helper, so no form element, no buttons and no
  choice of template.

`{{ formset|as_crispy_errors }}` (same file, line 62) draws `<pack>/errors_formset.html` with
`formset` alone.

Today `{% crispy formset %}` raises `TemplateDoesNotExist: daisyui/whole_uni_formset.html`. The
pack has none of the three templates.

So the pack owes django-crispy-forms three templates by name: `whole_uni_formset.html`,
`uni_formset.html` and `errors_formset.html`. The table is a fourth, reached only through
`helper.template`.

## R2. Choosing the layout

`FormHelper.template` (`crispy_forms/helper.py:200`) is the setting the specification means: it
is documented as the template a form or formset is drawn with, and django-crispy-forms' own packs
publish `<pack>/table_inline_formset.html` to be named there. The pack follows the same name, so a
developer moving from another pack changes the prefix and nothing else:

```python
helper.template = "daisyui/table_inline_formset.html"
```

Leaving `template` unset draws stacked. No setting, tag argument or helper subclass is added.

The helper is the formset's: django-crispy-forms reads `formset.helper`, or the second argument of
the tag.

## R3. A layout on the helper

When the helper has a layout, `get_render` (line 124) sets `helper.render_hidden_fields = True`,
then for each form renders the layout and stores the markup on the form as `form.form_html`. The
pack's `display_form.html` already draws `form.form_html` when it is there and the plain field
loop when it is not, so the stacked template includes `display_form.html` once per form and the
layout is applied to each in turn with no more work.

Two consequences, both django-crispy-forms' documented behaviour:

- A layout draws only the fields it names, plus hidden ones. A delete or order input is drawn in
  a laid-out formset only when the layout names `DELETE` or `ORDER`. The README says so.
- The table never reads `form.form_html`, so a layout is not applied there (specification,
  clarification 4).

## R4. The management form and hidden fields

`{{ formset.management_form }}` draws four hidden inputs and nothing else (checked by drawing one:
`TOTAL_FORMS`, `INITIAL_FORMS`, `MIN_NUM_FORMS`, `MAX_NUM_FORMS`). It is drawn once, ahead of the
forms, in both layouts.

A form's hidden fields are drawn by `field.html`, which draws a hidden field as its input alone.
In the stacked layout they come out of the form's own field loop. In the table they have no
column, so they are drawn inside the row's first cell, which keeps them inside the row they
belong to and inside valid table markup.

A model formset's primary key and an inline formset's foreign key are hidden fields like any
other. The suite can build both without a model of its own: `django.contrib.auth` and
`django.contrib.contenttypes` are installed, so `modelformset_factory(Group, ...)` and
`inlineformset_factory(ContentType, Permission, ...)` are real ones.

## R5. Naming an input whose label is a column heading

`field.html` already does this when the form draws no labels. Drawn with `form_show_labels=False`
(checked by drawing a formset's form that way):

- an input gets `aria-label` holding its label's text, and keeps `aria-describedby` naming its
  help text, which `field_body.html` still draws beside it with the matching id;
- a radio group, a checkbox group and a date's selects keep their `<fieldset>`, which gets the
  `aria-label`;
- a single checkbox, which is what a delete input is, is drawn bare with `aria-label`;
- an invalid input is described by its error element, drawn in the same cell.

So each table cell includes the helper's field template with `form_show_labels=False`. The table
needs no naming mechanism of its own, and help text sits in the cell because the input's
description has to point at something on the page.

The column heading is a `<th scope="col">` holding the field's label and the pack's required
marker.

## R6. Columns, and rows that line up

Django gives every form of a formset the same fields with one exception: with
`can_delete_extra=False`, forms beyond the initial ones have no `DELETE` field (checked: an
initial form has `name, kind, ref, DELETE`, an extra one `name, kind, ref`). A template loop over
each form's visible fields would then draw rows of different lengths.

Initial forms come first in a formset, so the first form is always one that has the delete field
when any form does. The columns are therefore the first form's visible fields, in its own order,
and each row draws, for each column, that form's field of the same name or an empty cell when the
form has none. Looking a field up by name is not something a Django template can do, so this is a
small class in `mvp_forms/templatetags/daisyui.py` beside `FieldInput`, handed to the template by
a tag.

A formset with no forms draws no table: the management form, any formset-wide error, and the
helper's buttons. Whether an empty table should show its headings is one of the appearance points
the specification leaves to the build, and a table with headings and no rows would have to take
them from `formset.empty_form`, which the pack otherwise never touches.

A formset whose forms have only hidden fields has no columns. Each row still gets one cell to
hold them.

## R7. Where each error goes

- **A field's error**: `field_body.html`, unchanged, in the form's container or the row's cell.
- **A form-wide error**, stacked: `display_form.html` already includes `errors.html`, which draws
  `form.get_context.errors`: the form's non-field errors and its hidden fields' errors (FS-002).
  It lands inside the form's container with no new work.
- **A form-wide error**, table: decisions D5 left a cell or a row of its own to planning. A row of
  its own would break the one promise the specification makes about the table's structure, one
  body row per form, exactly when a script reading the rows needs it most. So the errors are drawn
  inside the row, in its first cell ahead of the field, in an element with an id built from the
  form's prefix, and the `<tr>` names that element with `aria-describedby`. The same list is used
  as stacked, so a hidden field's error lands there too.
- **A formset-wide error**: `formset.non_form_errors`, drawn once in `errors_formset.html` ahead
  of the forms, in the same `role="alert"` element the pack uses for a form's own, with
  `formset_error_title` when the helper sets one. Django reports a formset below its minimum,
  above its maximum or with a damaged management form through the same list.

`non_form_errors` on an unbound formset is empty and draws nothing. Every message goes through
the template layer and is escaped there. With `form_show_errors` off, no error of any kind is
drawn, as for a single form.

The row's error element takes its id from `form.prefix`, as `<prefix>_errors`. Field ids start
`id_` and frames start `div_id_` (ADR 0005), so it cannot collide with either.

## R8. Media

`uni_form.html` draws `form.media` when the helper's `include_media` is on. Included once per
form, that would repeat every script and stylesheet for every form. The formset templates draw
`formset.media` once and include each form with `include_media` off.

## R9. The delete and order inputs

`DELETE` is a `BooleanField` with a `CheckboxInput` and `ORDER` an `IntegerField` with a
`NumberInput` (`django/forms/formsets.py`, `add_fields`). Both are ordinary fields of the form, so
the pack already draws them as `checkbox` and `input`, and as visible fields they get a column and
a heading in the table. The work in this feature is the equal-length rows of R6 and the tests that
Django reads them back.

## R10. Classes

| Class | Where | Kind |
|---|---|---|
| `table` | the table | daisyUI component |
| `alert alert-error alert-soft` | formset-wide errors | daisyUI, already used by `errors.html` |
| `text-error` | a row's form-wide errors | daisyUI colour utility, already used for field errors |
| `divider` | between stacked forms | daisyUI component |
| `overflow-x-auto` | the element around the table | Tailwind layout utility; daisyUI's own table documentation wraps a table this way and has no component for it |

`overflow-x-auto` is added to `LAYOUT_UTILITIES` in `tests/test_pack/test_independence.py` by
name. The others are already in `tests/data/daisyui-classes.txt`.

## R11. The demo project

Earlier features each added a page inside the django-mvp shell and a standalone twin styled by
daisyUI's CDN build alone. This feature adds two such pairs, one per layout. Each page draws one
formset to submit and the same formset already bound to data that fails all three ways, so the
errors can be seen without typing. Deletion and ordering are on. The demo views bind the posted
formset and draw it again. They save nothing.

## R12. Text the pack adds

None. Headings are the fields' labels, `Delete` and `Order` are Django's, and error text is the
form's.

## R13. New dependencies

None.
