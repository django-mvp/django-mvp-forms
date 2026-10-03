# ADR 0034 — A shortfall in daisyUI's own drawing is published, never patched

**Status:** accepted

## Decision

Where something the pack draws falls short of the standard under a shipped theme and no stock
daisyUI class brings it up to it under every shipped theme, the pack adds nothing of its own. The
pairing is a known exception, listed in the README with the themes it falls short under.

The README's table is the list. The check reads it and fails in both directions: when something
falls short that is not listed, and when something listed now passes. A known exception is a
pairing and a theme. A pairing is named by what is drawn, in which of the theme's colours and on
which surface, so form states that draw the same thing share one row.

Nothing becomes a known exception without a person pasting it into the README.
`uv run python -m tests.legibility` prints the table as it should read.

## Why

The pack ships no stylesheet and defines no class (ADR 0003), so it cannot correct a theme. A
small stylesheet or an inline style would have to be loaded by a host project on the CDN
install. A colour chosen per theme would be per-theme work inside the pack and would name actual
colours. Waiting until every theme passes would make the pack's delivery depend on another
project. Saying nothing would leave a developer choosing a theme with no way to find out.

One list in the test suite and a copy in the README would need a test that they agree, and the
copy in the README is the one that goes stale.

## Revisit if

The list grows until it stops being useful to someone choosing a theme, or daisyUI changes how
it draws an input's border, which is the row that names every theme.
