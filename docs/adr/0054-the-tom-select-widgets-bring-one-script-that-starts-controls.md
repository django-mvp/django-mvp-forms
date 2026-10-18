# ADR 0054 — The Tom Select widgets bring one script, and it starts the controls

**Status:** accepted

## Decision

`TomSelect` and `TomSelectMultiple` in `mvp_forms.widgets` draw Django's own select and write
their settings on it as JSON in `data-tom-select`. They name one script,
`mvp_forms/tomselect.js`, in their media. Nothing else in the package loads it, and the pack's
own templates still need no script.

The host project loads Tom Select. The script uses whatever the page provides as
`window.TomSelect`, which django-tomselect's own script also sets, and does nothing on a page
without it.

The script follows [ADR 0045](0045-mask-widgets-bring-one-script-that-acts-once.md): it is a
file, it sets a flag on `window` so that only its first copy acts, and it waits for the document
to finish loading. Beyond that it:

- starts a control only on a `select[data-tom-select]` that has none, so a stock select and a
  select django-tomselect drew are left alone
- reads `placeholder`, `maxItems` and `plugins` from the attribute and passes those to Tom
  Select with `maxOptions: null`, and passes nothing else
- copies the select's `aria-describedby` to the input Tom Select builds
- watches the document for added elements and starts a control on any marked select among them
- destroys the control of a marked select that is out of the page once a batch of changes has
  been made, so a select moved within the page keeps its control
- copies `data-none-text` and `data-count-text` from the select to the box that holds the chosen
  values, for a counted control ([ADR 0057](0057-a-counted-control-is-one-setting-drawn-by-the-tom-select-stylesheet.md))
- sends `mvp-forms:tomselect` from the select, with the instance in `event.detail.tomselect`

It is tested in Chrome, as [ADR 0046](0046-the-mask-script-is-tested-in-a-browser.md) decided
for the mask script, against a copy of Tom Select kept under `tests/data/`.

## Why

django-tomselect's fields load their options from a view. A project that wanted the same control
over a short list known when the form is built had to write an endpoint for each field. Django
already writes such a field's options into the page, and Tom Select reads them from the select,
so a widget needs only to mark the select and a script to start the control.

Distributing Tom Select would mean following its releases, and a project that uses
django-tomselect would load it twice.

Tom Select offers at most 50 options unless told otherwise. A field with more could not show
them all, so the limit is removed.

Tom Select hides the select and gives focus to an input of its own, which carries the label and
not the description. The pack ties help text and errors to a field through `aria-describedby`,
so without the copy assistive technology would stop announcing them.

Passing the whole attribute to Tom Select would make every one of its settings reachable from
markup, including the ones it reads as HTML. The widgets write three settings, so the script
reads three. A developer who needs another takes the instance from the event.

Projects built on this package add formset rows in the browser and load forms with htmx. A
control that started only on selects present when the page loaded would be missing in most of
the places it is used. django-mvp inserts a row from an empty form kept in a `<template>`, whose
content the script never sees, so the inserted select arrives unstarted and the watcher finds
it.

Tom Select adds listeners to the document and the window for each control and removes them only
in `destroy()`. A page that swaps a form out with htmx would keep the listeners of every control
it had shown. A move within the page is a removal and an insertion in the same batch, so the
script asks whether the select is still in the page once the batch is read, rather than treating
every removal as the end of the control.

## Revisit if

Tom Select stops reading options, groups or the `disabled` attribute from a select, or
django-tomselect stops exposing Tom Select to the page, which would have a page that uses both
load it twice.
