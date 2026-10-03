# ADR 0021 — Size is stated once for a form; colour and variant are held for inputs and for buttons

**Status:** accepted

## Decision

`FormChoices(size=...)` reaches every input and every button the form draws. Colour and variant
are held twice: `color` and `variant` reach the inputs, and `button_color` and `button_variant`
reach the buttons. Neither pair reaches the other.

When two colour classes would land on one element, the pack writes one. A field drawn as in error
keeps its error modifier and is drawn without the chosen colour. A `Submit` given a colour is
drawn without the `btn-primary` django-crispy-forms writes by default. A class the developer
wrote by hand is always kept.

## Why

Size is the one choice that always wants to match across a form. Colour and variant do not. A
form with ghost inputs rarely wants ghost buttons, and a submit and a reset button drawn in the
colour of every input say nothing about which is which. The variants also differ: daisyUI gives
inputs one and buttons five, so a single statement could only name what they share.

Two colour modifiers on one element both set the same property, and which one shows depends on
the order of the rules in daisyUI's stylesheet. A person has to be able to tell which field is
wrong, and that should not rest on rule order.

## Revisit if

Real forms turn out to state the same colour and variant for inputs and buttons nearly every
time.
