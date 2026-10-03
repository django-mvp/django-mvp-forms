# ADR 0018 — Choices are daisyUI's own names, from a closed table written out in full

**Status:** accepted

## Decision

A size, a colour and a variant are written with daisyUI's names: `xs` to `xl`, the eight semantic
colours, `ghost` for inputs, and `outline`, `dash`, `soft`, `ghost` and `link` for buttons. The
keyword for a colour is `color`, as daisyUI and CSS spell it.

`Modifiers` in `mvp_forms/choices.py` holds the class each name means for each kind of input and
for buttons. Every class is written out as a literal string. None is built from a prefix and a
name.

A name outside the table raises `InvalidChoice` when the form is drawn. It is never written to
the page as a class. The error carries what was stated, the names allowed and the field or button
it was stated on.

A choice stated for a whole form that one kind of input has no modifier for, such as `ghost` on a
checkbox, is passed over for that kind. The same choice stated on that one field raises.

A later feature that draws a new kind of input adds a row to each table. When daisyUI adds or
removes a name, the tables follow it and `tests/data/daisyui-classes.txt` is refreshed.

## Why

The pack is limited to classes that daisyUI's CDN build defines, so that a host page needs no
build step. A name passed through unchecked would produce a class the build does not define, and
the form would look unchanged with no error anywhere.

A host project that builds its own stylesheet has Tailwind scan the installed package, and
Tailwind only finds a class that appears whole in a file. A class assembled at run time would be
missing from that build.

A form-wide choice has to be usable on a form that mixes kinds of input, so an inapplicable one
cannot be an error there. On one named field it can never apply, so it is a mistake.

Names are checked when the form is drawn and not when the statement is constructed, because a
`Choice` in `FormChoices(fields=...)` is built before it knows which field it is for, and the
error has to name the field.

## Revisit if

Host projects with custom daisyUI colours need to name them from Python.
