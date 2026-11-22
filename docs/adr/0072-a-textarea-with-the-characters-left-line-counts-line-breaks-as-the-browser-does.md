# ADR 0072 — A textarea with the characters-left line counts line breaks as the browser does

**Status:** accepted

## Decision

`CharactersLeftTextarea.value_from_datadict` returns the submitted text through Django's
`normalize_newlines`, so every `\r\n` and `\r` is read as `\n`. The field then counts a line break
as one character, as the browser's `maxlength` does, and a text the line says fits is accepted
when it is submitted.

The text is stored with `\n` line breaks. A value saved earlier with `\r\n` reads as changed on
its form until it is saved once.

## Why

A browser counts a line break in a textarea as one character and submits it as two. A
`CharField(max_length=5)` then refuses `ab`, a line break and `cd`, which the browser's `maxlength`
allowed. A line saying none are left before an error on submit would be worse than no line.

Counting each break as two in the script would let the browser take a text the line then calls
over the limit, and would leave every other reader of the field with the mismatch. Reading the
breaks as one on the way in makes the browser, the line and the field agree.

## Revisit if

Django's `CharField` counts a line break as the browser does, or the browser's `maxlength` counts
a submitted line break as two.
