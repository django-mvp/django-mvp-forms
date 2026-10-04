# ADR 0036 — A floating label is a kind of choice, and a disabled field keeps its ordinary label

**Status:** accepted

## Decision

A floating label is the fifth kind of choice, beside size, colour, variant and drawing. It is
stated as `label="floating"` on `FormChoices` for a whole form and on `Choice` for one field, and
`None` is the ordinary label. `Modifiers.labels` holds the one name and its class as a literal.
It follows the order every choice follows: a `Choice` in the layout, then the field's entry by
name, then the form's.

A field takes a floating label when the pack draws it as one input, one textarea or one select.
It does not when it is a group, a multi-widget field, a rating or a range, when it has attached
text or joined buttons, when it is drawn inline, and when it is a member of a joined group.
Stated for the form, the choice passes such a field over. Stated for that field, or around a
button, it raises `InvalidChoice` with `kind="label"` and nothing allowed.

The label is one `<label class="floating-label">` holding a `<span>` with the label and the
required marker, then the input. The frame draws no other label for the field. An input or a
textarea with no placeholder of its own is given the label's text as its placeholder.

Three cases draw the ordinary label, or none, and raise nothing:

- a disabled field, whether by the form field, by `UneditableField` or by the widget's own
  attribute, keeps the ordinary label;
- with the helper's labels off no label is drawn and the input is named by `aria-label`;
- a field with no label text is drawn as any field with none.

## Why

It is a statement about how one field is drawn, which ADR 0019 says is an argument of `Choice`
and never a second layout object. A form drawn with no layout can then float its labels, and a
dense form can state it once.

It is a name and not a boolean so that it merges, inherits and is undone the way the other four
kinds are, and so that an unknown value is refused the way an unknown size is.

daisyUI shows a floating label at the input's edge only when the input has focus or is not
showing a placeholder. An input with no placeholder therefore never shows the label inside
itself, so the label's text is offered as the placeholder, which is the rule `InlineField`
already follows.

daisyUI makes the floating label transparent when the input inside it is disabled. A disabled
field with a value would then show no label and no placeholder. The pack defines no class of its
own (ADR 0003), so it cannot undo that, and the field falls back to the ordinary label. Raising
was rejected, because a field is often disabled at run time for one person and not another.

Attached text is itself a label that wraps the input (ADR 0026), and a join needs the input as
its direct child. daisyUI documents a floating label in neither, and the README says stock
markup wins.

The pack cannot see a `disabled` attribute on a fieldset around a field. The README says to undo
the floating label on the fields of such a fieldset.

## Revisit if

daisyUI shows a floating label on a disabled input, documents a floating label inside a join or
beside attached text, or adds a second kind of label.
