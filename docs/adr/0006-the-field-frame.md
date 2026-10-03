# ADR 0006 — One field frame, and what it reads from the context

**Status:** accepted, amended by [ADR 0011](0011-a-group-is-framed-as-a-fieldset.md): a group is framed as a `fieldset`, and a single checkbox sits inside its label; and by [ADR 0017](0017-a-choice-is-stated-on-the-helper-and-by-one-layout-object.md): the pack's tags also read `daisyui` and `daisyui_choice`

## Decision

`daisyui/field.html` is the frame around every field: the label, the required marker, the input,
the help text and the errors. Every input the pack draws, in this feature or a later one, sits
inside it.

It is given `field` and reads four optional names from the context: `form_show_labels`,
`form_show_errors`, `label_class` and `field_class`. Its outer element is always a `div`.

- A switch counts as off only when it is exactly `False`. A name missing from the context means
  on, so a template that includes the frame directly still gets a label and errors.
- The frame reads no other unqualified name. In particular it takes no element name and no
  wrapper class from the context.
- Help text and errors are written inside the frame. They are split into templates of their own
  by the first feature that needs to include them from somewhere else.

## Why

django-crispy-forms renders the field template with a copy of the host page's whole context when
a form is drawn through `{% crispy %}`. Any bare name the frame reads is one the page can set by
accident, and a name used as an element name would turn a page variable into markup. Other packs
read `tag` this way. This one does not.

django-crispy-forms always supplies the four names the frame does read, so the page cannot
override them.

One frame means later features get the same label, marker, help text and error handling without
redefining any of it, and a field whose widget the pack does not cover yet is still drawn
completely.

## Revisit if

A layout object needs the frame drawn as another element or with an extra class. That feature
passes the value by a route that does not read a bare page variable.
