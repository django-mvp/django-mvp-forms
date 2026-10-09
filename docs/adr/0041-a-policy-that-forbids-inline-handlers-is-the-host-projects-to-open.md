# ADR 0041 — A policy that forbids inline handlers is the host project's to open

**Status:** accepted

## Decision

The pack does not have to work in full under a Content Security Policy that forbids inline event
handlers. Under such a policy the close button of a `Modal` and the dismiss button of an `Alert`
are drawn and do nothing, and everything else the pack draws works as it does anywhere.

The two inline handlers of ADR 0014 stay, and the pack still ships no script file. A host project
that keeps such a policy has two routes, both in the README: allow the two handlers by hash with
`'unsafe-hashes'`, or draw the buttons itself in its own copy of the template.

This answers issue #47.

## Why

The promise the pack makes is that a page loading daisyUI and nothing else is enough. Dismissing
an alert has no script-free mechanism in HTML or in daisyUI's CDN build, so meeting a strict
policy means either a script file the host project loads, which ends that promise for every
project to serve the few that set such a policy, or an alert that cannot be dismissed.

The cost to a strict host is small and was measured. With `script-src 'self' 'unsafe-hashes'`
and the SHA-256 hash of each handler's text, both buttons work and every other inline handler on
the page stays blocked, in Chromium 153 and Firefox 155. Safari was not run. A project that will
not add the hashes replaces one template (ADR 0029) and closes the modal with `commandfor`.

Moving the modal's own close button to `commandfor` was weighed and left. It would close a modal
under any policy, but a browser without the attribute would draw a button that does nothing on a
modal opened for a field error, which has no other way to close. That trades a limit a host
project chose for one a person using the form cannot see coming.

## Revisit if

`commandfor` is supported by every browser daisyUI supports, which lets the modal's close button
drop its handler, or HTML or daisyUI gains a way to remove an element on a click with no script.
