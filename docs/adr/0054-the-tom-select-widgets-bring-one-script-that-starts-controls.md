# ADR 0054 — The Tom Select widgets bring Tom Select and one script that starts the controls

**Status:** accepted

## Decision

`TomSelect` and `TomSelectMultiple` in `mvp_forms.widgets` draw Django's own select and write
their settings on it as JSON in `data-tom-select`. They name one script of the package's own,
`mvp_forms/tomselect.js`, in their media. Nothing else in the package loads it, and the pack's
own templates still need no script.

The package ships Tom Select ([#240](https://github.com/django-mvp/django-mvp-forms/issues/240)).
A pinned copy of Tom Select's complete build and its stylesheet, with Tom Select's licence, sits
under `mvp_forms/static/mvp_forms/vendor/tom-select/`. The widgets' media names the copy before
`mvp_forms/tomselect.js`, and Tom Select's stylesheet before the package's, so a page that
renders the form's media needs nothing else. The copy is the complete build because it is the
one that registers every plugin the widgets name: `clear_button`, `remove_button`,
`checkbox_options` and `dropdown_input`.

The copy is wrapped so that it runs only when the page has no `window.TomSelect` yet. The script
uses whatever the page holds as `window.TomSelect` once the document has loaded, which may be
the package's copy, one the page loaded itself or django-tomselect's, and does nothing on a page
with none.

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
for the mask script, against the copy the package ships, and against an older copy kept under
`tests/data/` for a page that loads its own Tom Select.

## Why

django-tomselect's fields load their options from a view. A project that wanted the same control
over a short list known when the form is built had to write an endpoint for each field. Django
already writes such a field's options into the page, and Tom Select reads them from the select,
so a widget needs only to mark the select and a script to start the control.

django-mvp depends on this package and every other asset a django-mvp page needs arrives with
the packages it installs. A widget whose control works only after the project finds, pins and
loads a library is the one exception, and a page that forgot it showed a plain select with no
error. Shipping the library costs following Tom Select's releases, which is a version bump of
two static files.

django-tomselect's script carries its own Tom Select and defines plugins of its own on it,
`dropdown_footer` among them, before setting `window.TomSelect`. A stock copy loaded after it
would replace that class, and every django-tomselect control started afterwards would fail for a
missing plugin. The guard keeps whichever copy arrived first. When django-tomselect's script
comes after the package's copy, it replaces it before any control has started, which is
harmless.

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

Tom Select stops reading options, groups or the `disabled` attribute from a select, or Tom
Select gains a way to load a second copy without replacing the first, which would make the
guard unnecessary.
