# Decisions: Choice widgets drawn as a scale, pills, chips or cards

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
reading of the feature was taken from issue #250 and resolved without a round of questions, so
every decision below is self-resolved and the maintainer's to overturn when he reviews the
specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. It is a feature

**Chosen:** a new feature with a specification of its own. After it, a developer can draw a choice field as a scale, pills,
chips or cards by naming a widget, and a person filling in a form can answer by tapping large
choices and unfold the ones not on show. No spec describes either.

**ADR:** none

## D2. Seven widgets, not drawings

**Chosen:** `ScaleSelect`, `PillSelect`, `PillSelectMultiple`, `ChipSelect`,
`ChipSelectMultiple`, `CardSelect` and `CardSelectMultiple`, subclasses of `RadioSelect` and
`CheckboxSelectMultiple`.

**Why:** the issue asks for widgets. Each layout has settings of its own, and a drawing stated with
`Choice` carries none, so a drawing would need a second way to state them. Naming the classes after
Django's `*Select` widgets and the package's `TomSelect` keeps one naming pattern across the
package. A scale is a single-choice question by nature, so it has no multiple form.

**ADR:** none — widgets beside Django's own are the package's ordinary shape

## D3. Pills and chips are separate widgets

**Chosen:** two widgets, as the issue lists them. A pill is for a short set of short labels, laid
out in a row that wraps. A chip is a larger target that shows a long label in full and can fold
the rarely used choices away.

**Why:** they answer different questions. Merging them would give the pill a fold it never needs
and the chip a size setting to make it a pill.

**ADR:** none

## D4. A single choice is cleared by the field's own empty choice

**Chosen:** a choice whose value is the empty string is drawn after the others as the way to say
"none", on every single-choice widget. No hidden input and no second-tap script.

**Why:** it is how the pack's rating already clears (FS-010), it is how Django already writes an
optional choice, it is visible and reachable by keyboard, and it needs no script. A second tap
that clears is invisible to a person who does not know it is there, and needs a script on every
widget that offers it.

**ADR:** none — it follows the rating's rule

## D5. The fold is by named values, and a chosen choice is never folded

**Chosen:** a developer names the values that stay on show, when the widget is made or on the
form's copy of it in `__init__`. Every chosen choice is on show as well. A value the field does
not offer is passed over.

**Why:** the choices that matter usually depend on the person (the ones they use most), which is
known only when the form is built. A count would fold by position, which says nothing about which
choices matter. Model choices change with the data, so an unknown value is not an error.

**ADR:** none

## D6. Only the fold needs a script, and it is an addition

**Chosen:** one script, named in the media of the chip and card widgets, which keeps a choice
chosen inside the fold on show when the fold closes and keeps the count true. Without it the fold
is a native disclosure that opens and closes, and every choice is reachable.

**Why:** the pack's promise is that its own templates need no script. The input mask, partial
date, Tom Select and image widgets already ship one each, named in their media, so a project that
uses none of them never loads one. Following the same rule keeps the scale and pills script-free.

**ADR:** expected — a short record that the chip and card widgets bring one script, beside the
existing records for the other widget scripts

## D7. A card's icon is markup the developer gives

**Chosen:** markup per choice value, drawn as given when marked safe and escaped otherwise.

**Why:** the package depends on no icon set, and must work in any daisyUI project (G6). Markup
lets a project use whatever icons it already draws.

**ADR:** none

## D8. Group names are not drawn

**Chosen:** choices in named groups are drawn in the field's order with no headings, as a rating
draws them.

**Why:** grouping and folding are two ways of organising a long list, and drawing both inside one
fold would make a person open a fold to scan headings. A developer who needs headings uses the
pack's checkbox or radio group.

**ADR:** none

## D9. Size and colour, no variant, no drawing

**Chosen:** the widgets take the form's and the field's size and colour. A variant stated for the
form is passed over; one stated on the field raises `InvalidChoice`. A drawing stated for the field
raises `InvalidChoice`.

**Why:** the size and colour of any form component can be set from Python (G4). A variant would
change how an unchosen choice looks, and the layouts depend on chosen and unchosen choices being
told apart at a glance, so it is left out as it is for the rating. A drawing would replace the
widget the developer chose.

**ADR:** none — it follows the rating's rule

## D10. The look is the agreed one, within daisyUI's markup

**Chosen:** the build keeps to the look already agreed for the four layouts, described in
`planning-notes.md`, using daisyUI's classes and Tailwind's utilities only.

**Why:** the README's scope rules out a stylesheet of the pack's own, and stock daisyUI markup wins
over custom styling when the two conflict.

**ADR:** none

## D11. Out of scope

Reordering choices in the browser, folding by count, a second tap that clears, hiding the other
choices once one is chosen (daisyUI's filter does that, and a question needs its choices in view),
an icon set, and icons on pills, chips or the scale. Each can be a request of its own if a project
needs it.

## D12. The widgets name their own component and the tag resolves from it

**Chosen:** each widget carries the name of the component it is drawn as (`choice-button` for the
scale, pills and chips, `choice-card` for cards). The tag reads that name before it matches the
widget's class, so a subclass of `RadioSelect` is no longer a `radio`. Size and colour come from
two new entries in the existing tables, and the resolved classes are written onto each option in
the widget's own context.

**Why:** the class match would give these inputs the `radio` class and the modifiers of a radio,
which draws a native radio mark inside a button. The rating already resolves into its context for
the same reason.

**ADR:** docs/adr/ — written in T005, graduated at convergence

## D13. The fold is a native details element

**Chosen:** one `details` with a `summary` for every chip and card widget, single or multiple. The
script only moves a chosen choice out of a closed fold and rewrites the count.

**Why:** the disclosure, its keyboard operation and its open state for assistive technology come
from the browser, and without the script every folded choice is still reachable (FR-018).

**ADR:** none — local to this feature, nothing downstream inherits it

## D14. A choice is named by its label through `aria-label`

**Chosen:** the scale, pills and chips draw each choice as an input drawn as `btn`, named by an
`aria-label` holding the label as plain text, as daisyUI documents a join of radio buttons.

**Why:** it is daisyUI's own markup and needs no wrapper. If a browser fails to wrap or tick a label
drawn this way, the build falls back to a `label` holding a hidden input and records it here.

**ADR:** none — local to this feature, nothing downstream inherits it

## D15. Design review corrections

The scale's end words name the first and last inputs through `aria-labelledby`, since `aria-label` is the visible text of an input drawn as `btn`. The colour entries for the two components are Tailwind state utilities, so the class test accepts names in `LAYOUT_UTILITIES`, and the decision record extends ADRs 0003 and 0020. A card's mark takes the existing `radio` or `checkbox` tables. The widget writes its own `aria-label`. The `fixed_size` entries and the inline-layout contingency are dropped. Quiet text starts at `text-base-content/90`.

**ADR:** none — recorded in the feature's decision record
