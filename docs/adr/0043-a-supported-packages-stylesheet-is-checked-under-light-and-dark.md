# ADR 0043 — A supported package's stylesheet is checked for legibility under light and dark

**Status:** accepted, extends [ADR 0033](0033-legibility-is-calculated-from-the-themes-published-colours.md)

## Decision

The text a supported package's stylesheet colours is held to the standard of ADR 0033 under
daisyUI's `light` and `dark` themes, and under no other.

The test reads each ink and the surface it sits on from the stylesheet itself, through a named
table of selector, declaration and surface, and resolves the theme's variables, `color-mix` and
opacity with the arithmetic under `tests/legibility/`. Text is held to 4.5 to 1, and a part of a
control that shows what it is or what state it is in to 3 to 1.

A pairing that is daisyUI's own, such as a placeholder, is the exception ADR 0034 already
describes. The dimmed content of a disabled control is measured and not held.

There is no test that a state has a rule. The states are shown on the demo page.

## Why

The stylesheet names no colour of its own (ADR 0042), so under any other theme it draws what that
theme's variables give a stock control. A shortfall there is the theme's, and ADR 0034 says how
one of those is handled. Checking thirty-five themes would list the same exceptions again for a
feature that serves an aspirational goal.

Reading the pairings from the file means a change to the stylesheet is measured, and a rule the
table reads a colour from cannot be removed without the test failing. A test that each state has
a selector could only fail when someone removed the rule on purpose.

## Revisit if

A supported package's stylesheet comes to name a colour that is not one of the theme's variables.
