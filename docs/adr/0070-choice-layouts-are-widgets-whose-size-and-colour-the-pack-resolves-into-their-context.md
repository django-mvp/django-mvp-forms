# ADR 0070 — Choice layouts are widgets whose size and colour the pack resolves into their context

**Status:** accepted, extends [ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md) and [ADR 0020](0020-choices-are-daisyuis-names-from-a-closed-table.md): the class test accepts, by name, the Tailwind state utilities that show a checked choice, which are listed with the layout utilities

## Decision

A choice field is drawn as a scale, pills, chips or cards by naming one of seven widgets in
`mvp_forms.widgets`: `ScaleSelect`, `PillSelect`, `PillSelectMultiple`, `ChipSelect`,
`ChipSelectMultiple`, `CardSelect` and `CardSelectMultiple`. They subclass `RadioSelect` and
`CheckboxSelectMultiple` and draw each choice with a template of the pack's own. Settings that
belong to one layout, such as the words at the ends of a scale, a card's icon and description
and the values that stay on show, are arguments of the widget. A drawing stated with `Choice`
takes none, so none of these layouts is a drawing.

Each widget names the component it is drawn as: `choice-button` for the scale, pills and chips,
and `choice-card` for cards. The `daisyui_field` tag reads that name before it matches the
widget's class, so a `RadioSelect` subclass is no longer drawn as a `radio`. The size and colour
come from two entries in each table of `Modifiers`, and the tag writes the classes onto each
option in the widget's own context. The form's size and colour and the field's own apply. A
variant stated for the form is passed over and one stated on the field raises `InvalidChoice`
with `kind="variant"`. A drawing stated for the field raises it with `kind="drawing"`. A card's
mark is the existing `radio` or `checkbox` entry, and the `choice-card` entry holds only the
colour of the card's edge and tint.

The colour of a checked choice is written with Tailwind's state utilities, such as
`checked:bg-primary` and `has-checked:border-primary`, because daisyUI has no modifier that
colours a checked button or a card. The class test splits each entry on whitespace and accepts a
name that is daisyUI's or one listed in `LAYOUT_UTILITIES`. Every utility the templates and the
tables write is listed there by name, so adding one is a reviewed change, and a class that is
neither daisyUI's nor listed still fails.

The chip and card widgets draw every choice in the same row or grid, mark the choices not on show
`data-choice-folded`, and draw after them a native `button` that is hidden in the markup. One
script, `mvp_forms/choice-fold.js`, is named in the media of those two widgets and nowhere else.
On load it hides the marked choices that are not chosen and shows the button. A press shows
the hidden choices in place, removes the button and moves the focus to the first choice shown. It
also acts on choices that arrive later, from a formset row or htmx. Without it every choice is
shown and the button stays hidden, so a page that loads no script still answers and submits the
form. The scale and the pills name no script.

## Why

The class a `radio` carries draws a native radio mark, which is wrong inside a button, and the
rating already resolves its own size and colour into its context for the same reason. One new entry in two
tables and a name read before the class match give these layouts the same route without
a second way to state a size or a colour.

Settings of a layout belong on a widget, which is where Django puts them. A drawing carries
none, and giving it a second way to take settings would have two homes for one kind of choice.

daisyUI's `btn` has colour modifiers for the unchecked button and none for a checked one, so the
checked state needs a state utility. Listing each by name keeps the class test's promise that no
class is written without review, and naming the state utilities beside the layout utilities
changes that list and not the test's rule.

The pack's promise is that its own templates need no script, and it holds because the choices
stay in the markup and a page without the script shows all of them. A script that only hides and
shows follows the widgets that already ship one, named in their media so that a project that uses
none of them never loads it. A button in the same row as the choices reads as one more choice,
where a disclosure drawn under them reads as a separate control and moves the choices a person
has already found when it opens.

## Revisit if

daisyUI adds a modifier that colours a checked button or card, which would replace the state
utilities. A browser fails to wrap or tick an input drawn as `btn` with an `aria-label`, which
would send the layouts back to a label that holds a hidden input.
