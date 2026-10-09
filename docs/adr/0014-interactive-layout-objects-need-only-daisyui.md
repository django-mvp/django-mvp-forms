# ADR 0014 — Interactive layout objects need only daisyUI

**Status:** accepted, amended by [ADR 0041](0041-a-policy-that-forbids-inline-handlers-is-the-host-projects-to-open.md): issue #47 is answered, and a Content Security Policy that forbids inline script no longer reopens this record

## Decision

A layout object that opens, closes or hides part of a form works on a page that loads daisyUI and
nothing else. The pack ships no script file. Each one uses the mechanism the browser already has:

- A tab is a radio input directly before its content, which daisyUI shows when the radio is
  checked.
- An accordion group is a `details` element, drawn with the `open` attribute when it starts open.
  The groups share no `name`, so each opens and closes on its own.
- A modal is a `dialog` element, drawn with the `open` attribute when it starts open. A host
  project opens it by its id.

A control the pack draws for these never joins the form's data and never submits the form. A
tab's radio carries `form=""`, which leaves it with no form owner. Buttons are `type="button"`.

An inline handler is written only where neither HTML nor daisyUI has a script-free mechanism.
There are two: the modal's close button calls `close()` on its dialog, and the alert's dismiss
button removes the alert.

## Why

A script file the host project must load would break the promise that daisyUI alone is enough,
as surely as a stylesheet would. An extra key in the submitted data is harmless on a post but
ends up in the query string of a search or filter form and can collide with a field name.

The accordion groups share no name because the browser keeps only the first open group of a
named set. django-crispy-forms can mark two groups open, one the developer chose and the one
holding an error, and the browser would close the second.

daisyUI closes a modal with a second form, which cannot sit inside the form the modal belongs
to. Its checkbox modal needs no script, but its close control is a label the keyboard cannot
reach. daisyUI has nothing for dismissing an alert. The `commandfor` and `command` attributes
would close a dialog with no script, but browsers gained them only recently, and a modal drawn
open for an error has no other way to close.

## Revisit if

The maintainer rules that the pack must work under a Content Security Policy that forbids inline
script (issue #47), or `commandfor` is supported by every browser daisyUI supports.
