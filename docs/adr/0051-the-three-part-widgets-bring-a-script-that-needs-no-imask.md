# ADR 0051 — The three-part partial date widgets bring a script that needs no IMask

**Status:** accepted

## Decision

`PartialDateInput` and `PartialDateSelect` name `mvp_forms/partial-date.js` in their media. It
depends on nothing, acts once however often a page includes it, and acts on groups added later,
as [ADR 0045](0045-mask-widgets-bring-one-script-that-acts-once.md) asks of the mask script.

The few lines that know the calendar, the length of a month and a partial date read as a number,
are in this script and in `mvp_forms/imask.js` both.

Options that cannot be chosen are taken out of a select and put back when they can be. They are
not hidden or disabled.

Without the script all three parts work, and the field validates what is sent.

## Why

A project that wants three selects should not have to load IMask for them. Neither script can
lean on the other, since a page may load only one, and a third shared script would be a file to
load for a dozen lines.

Safari ignores `hidden` on an `option`, so a hidden day would be shown greyed there.

It is tested in Chrome, as [ADR 0046](0046-the-mask-script-is-tested-in-a-browser.md) settles.

## Revisit if

A third script of the package needs the same calendar lines.
