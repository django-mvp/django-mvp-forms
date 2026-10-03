# ADR 0015 — A tab's radio is drawn with its pane, and the holder names the group

**Status:** accepted

## Decision

`layout/div.html` draws a `Tab` through `layout/tab-pane.html`, which writes the tab's radio and
then its content. It tells a `Tab` from a `Div` by the `link_template` attribute, which only a
`Tab` has. `layout/tab-link.html` draws nothing.

The pane writes a fixed placeholder for the radio's group name. `layout/tab.html` passes the
drawn panes through the filter `daisyui_tab_group`, which replaces the placeholder with a random
name made for that one drawing. When none of the holder's radios is checked, the filter checks
the first.

## Why

daisyUI shows a tab's content with `.tab:checked + .tab-content`, so the radio has to sit
directly before its content. django-crispy-forms draws every pane, then every link, and hands the
holder's template two joined strings, so a radio drawn by the link template would be separated
from its pane.

Radios form a group by a shared name, and a pane's template is given nothing but its own `Tab`.
Only the holder's template can supply the name. A name built from ids would be the same for two
forms drawn from one form class, joining their tabs into one group. A random name keeps every
holder apart with nothing asked of the developer.

Drawing each pane a second time from the holder's template was ruled out because
django-crispy-forms reports a field drawn twice. Keeping each drawn pane on its `Tab` was ruled
out because layout objects are often shared between requests, and one request could read
another's fields. ADR 0008 rules out a subclass of `TabHolder`.

django-crispy-forms marks no tab active when the first `Tab` was given `active=` and no tab holds
an error. Every pane would then be hidden until a person picked one, so the filter opens the
first, which is the tab the library opens by default.

## Revisit if

django-crispy-forms gives a pane's template its holder, or daisyUI shows a tab's content without
needing the radio beside it.
