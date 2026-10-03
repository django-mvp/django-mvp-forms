# ADR 0024 — Text a developer writes in a layout is drawn as markup

**Status:** accepted

## Decision

The text given to `PrependedText`, `AppendedText` and `PrependedAppendedText` is drawn as
written, markup included. It is the only value these templates draw unescaped.

Everything that comes from the form or from a person using it is escaped by the template layer:
labels, choice labels, help text, errors and values.

The README says the text is markup, and that text built from anything a person typed must be
escaped first.

A later template that takes text written by the developer in a layout follows the same rule
when django-crispy-forms documents that text as markup, and says so in the README. Otherwise it
escapes.

## Why

django-crispy-forms documents that this text can be markup, and an icon in front of an input is
its commonest use after a currency sign. Escaping it would break layouts written from that
documentation.

The text is written in Python, in the layout, in the same place a developer writes an `HTML`
layout object. It sits on the trusted side of the boundary the constitution draws in Article V.
`Alert` already draws its content the same way.

## Revisit if

django-crispy-forms starts escaping this text itself, or gives a way to mark it safe.
