# ADR 0057 — A counted control is one setting of TomSelectMultiple, drawn by the Tom Select stylesheet

**Status:** accepted

## Decision

`TomSelectMultiple` takes `counted=True`, which draws a multiple control that shows how many
values it holds in place of a tag for each, ticks each chosen option in its dropdown and has its
search box at the top of the dropdown.

- The one setting turns on both of Tom Select's plugins, `checkbox_options` and
  `dropdown_input`. There is no setting for either plugin on its own.
- The two words the control shows, "Nothing selected" and "selected", are the widget's
  `none_text` and `count_text`. Their defaults are translated with the package's catalogue. The
  widget writes them on the select as `data-none-text` and `data-count-text`, and the script
  copies them to the box Tom Select builds to hold the chosen values.
- The rules that hide the tags, draw the count, draw the ticks and fit the search box are in
  `mvp_forms/tomselect.css`, under the terms of [ADR 0055](0055-one-stylesheet-draws-tom-select-controls-from-either-source.md):
  every colour from the daisyUI theme, every selector inside a control. The count is drawn only
  on a box that carries `data-count-text`, so a django-tomselect control that uses
  `checkbox_options` keeps its tags. The ticks and the search box are drawn on any control that
  uses the plugins.
- Backspace in an empty search box keeps Tom Select's default and removes the value chosen last.
- The single `TomSelect` widget has no counted setting and no search box in its dropdown.

## Why

The demo drew this control from a subclass naming the two plugins and a stylesheet of its own. A
developer who wanted it had to copy both.

A tick on each option with the tags still shown is a control someone might want too. Nobody
does yet, and Article XV of the constitution adds settings when a project needs them. One
setting is what the demo showed and what was asked for.

The words are in the page for each control, so a project translates them as it translates any
other string of the package, and a field states its own where "selected" reads wrongly. A CSS
custom property holding a string would have to be written by hand in a stylesheet of the
project's own for each language.

The tags of a counted control are out of sight, but the search box is in the dropdown, so the
dropdown is open whenever Backspace reaches it. The value it removes loses its tick in front of
the person, and the count drops by one. Changing the key would mean overriding a Tom Select
default for one kind of control only.

## Revisit if

A project needs ticks with the tags still shown, or a search box in the dropdown of a single
control. Either is then a setting of its own.
