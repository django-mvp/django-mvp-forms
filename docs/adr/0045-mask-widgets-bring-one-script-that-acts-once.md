# ADR 0045 — The mask widgets bring one script, and it acts once

**Status:** accepted, narrows [ADR 0014](0014-interactive-layout-objects-need-only-daisyui.md) and [ADR 0041](0041-a-policy-that-forbids-inline-handlers-is-the-host-projects-to-open.md)

## Decision

The package ships one script, `mvp_forms/imask.js`. The widgets in `mvp_forms.widgets` name it in
their media, and nothing else in the package loads it. The pack's own templates still need no
script.

The script is a file. The widgets write no inline script and no inline event handler: their
options travel on the input as JSON in `data-imask`.

The script sets a flag on `window` the first time it runs and returns at once on every later run.
It waits for the document to finish loading before it looks for IMask, applies a mask to each
`input[data-imask]`, and watches for inputs added afterwards.

When a form's data is collected, the script changes a masked input's entry in two cases only.
A field with a display character hands the form what was typed. A placeholder nothing was typed
into hands the form an empty value. In every other case, and whenever the mask is out of step
with what the input shows, the browser's own entry stands.

## Why

ADR 0014 and ADR 0041 protect one promise: a page that loads daisyUI and nothing else draws every
form the pack can draw. A developer names one of these widgets on a field on purpose, and Django's
media is the ordinary way for a widget to bring its script. A project that uses none never loads
it, so the promise stands.

A file needs no exception under a Content Security Policy that forbids inline script, which is
the limit ADR 0041 had to accept for two buttons.

django-crispy-forms writes a form's media inside every form drawn with `{% crispy %}`. A page with
eight forms holds the script tag eight times. Without the flag, each copy gave every input a mask
of its own. Most masks survive that, and a pattern with a display character accepts nothing. The
script tag also sits inside the form, usually ahead of the tag that loads IMask, which is why the
script waits for the document.

IMask writes a display character into the input, so the browser would submit the dots of a PIN
field and not the digits. The script compares the mask's value with what the input shows
and does not ask whether the mask has a display character, because a pattern inside
`DynamicMaskInput` hides its display character from the outer mask.

IMask also writes an always-visible placeholder into the input. Submitted as it stands, an
untouched required field would pass and an optional one would store the placeholder.

A reset button, or a script that assigns to the input, changes what the input shows without
telling IMask. The mask's value is then stale, so the script touches nothing unless the two
agree.

## Revisit if

django-crispy-forms stops writing media inside the form, which would let the flag go, or IMask
gains a way to keep the typed value in the input's own value while showing a display character.
