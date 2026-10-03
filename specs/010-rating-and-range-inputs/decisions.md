# Decisions: Rating and range inputs

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below
was made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as follows. A developer says in Python, for one field at a time,
that a single-choice field is drawn as daisyUI's rating or that a number field is drawn as
daisyUI's range. A form that says nothing is drawn as before. A rating and a range keep the label,
required marker, help text, errors and disabled state of a normal field, submit the same data as
the field's ordinary drawing, and take the size and colour choices of FS-007. The feature serves
G9 and is one of the two slices of R7. Floating labels and joined inputs stay with #87.

**Why:** the issue is three sentences and the roadmap item is one, and neither conflicts with this
reading. Each gap it fills is recorded as its own decision below.

**ADR:** none. This is the record of how the specification was written, not a constraint on the
code.

## D2. A rating and a range are drawings, not widgets, fields or layout objects

**What was ambiguous:** the issue says "from Python" and G9 says "reachable from a layout".
Neither says what the developer writes.

**Chosen:** a rating and a range are two more drawings, stated the way FS-008 states a toggle: with
a `Choice` around the field in a layout, or by the field's name in `FormChoices(fields=...)`
(FR-001, FR-002). The glossary's entry for a drawing, which today says only a boolean field takes
one, is widened when the feature is built (FR-026).

**Rejected:**

- A `Rating` widget and a `Range` widget shipped by the package. Article XV says fields and
  widgets arrive when a real project needs one and never through the roadmap. A widget would also
  make the developer change their form's fields to change how they look, which is what G4 and G9
  exist to avoid.
- Two new layout objects, such as `Rating("score")`. ADR 0019 says the package defines one layout
  object, and that a later statement for one field is an argument of `Choice`. A layout object
  would also be unreachable for a form drawn without a layout.
- Detecting the component from the widget, so that a number input with `type="range"` becomes a
  daisyUI range with nothing stated. ADR 0002 says the pack never reads an input's type to decide
  how to draw.

**Why defensible:** it is the mechanism the pack already has for "draw this field another way",
it works with and without a layout, and it combines with size and colour on one statement, which
the issue asks for.

**ADR:** yes. A record that a drawing is no longer a boolean field's alone, and that each kind of
field has its own set of drawings. It amends ADR 0022.

## D3. A stated drawing may change the element drawn, and never what is submitted

**What was ambiguous:** ADR 0002 says the pack never changes an input's type. A range is an input
of type `range`, and a rating is a group of radio inputs even when the field's widget is a select.

**Chosen:** a rating may be stated for a field whose widget is a select or a radio group, and a
range for a field whose widget is a number input (FR-004, FR-005). The pack draws the element the
drawing needs. What the form submits, validates and cleans to is unchanged (FR-007, FR-012).

**Rejected:**

- Requiring `RadioSelect` for a rating and `NumberInput(attrs={"type": "range"})` for a range.
  A Django `ChoiceField` is a select unless told otherwise, so "draw a choice field as a rating"
  would need two changes in two places, one of them on the field. It would also split the
  statement between the widget and the `Choice`.
- Accepting any widget and trusting the developer. A rating of a multiple select or a range of a
  text input submits something the field cannot clean.

**Why defensible:** the reason behind ADR 0002 is that the input type decides what the browser
submits, and that a setting about appearance must not change it. A select and a radio group submit
the same value for the same choice, and a number input and a slider submit the same number. The
developer also asked for the drawing by name, which is the opening ADR 0002 itself leaves when it
says "unless the developer writes" otherwise.

**ADR:** yes. It amends ADR 0002: the pack sets a type only for a drawing the developer stated,
and only where the submitted value is the same.

## D4. A rating's colour is daisyUI's colour class on each star

**What was ambiguous:** the issue asks for "the same size and colour choices as every other
input". daisyUI's rating has size modifiers and no colour modifier.

**Chosen:** a rating takes the colour through daisyUI's colour classes on its stars, such as
`bg-primary`, which is how daisyUI's own documentation colours a rating (FR-018, FR-022). The
`Modifiers` colour table gains a row for the rating whose values are those classes, written out in
full. A range has `range-primary` and the rest and takes them like any input.

**Rejected:**

- No colour on a rating, with the form's colour passed over and a field's own colour raising. It
  keeps strictly to component modifiers, and it fails the issue's one explicit ask.
- An arbitrary Tailwind colour utility. ADR 0003 allows utilities for layout only.

**Why defensible:** the eight `bg-` classes for daisyUI's semantic colours are in daisyUI's CDN
stylesheet, and `tests/data/daisyui-classes.txt` lists them. So they pass the pack's own test of
what it may write, they follow the host project's theme, and they need no build step. daisyUI
wrote them for its own colours.

**For the build to check:** a rating in error has no error modifier of daisyUI's. FR-020 asks only
that the chosen colour is left out and that the group is marked invalid. Whether the stars also
take the error colour is for the plan.

**ADR:** yes. The first component whose colour is not a modifier of its own.

## D5. An empty choice clears the rating and is never a star

**What was ambiguous:** an optional choice field usually has an empty first choice. Drawn as a
star, a five-point scale would show six.

**Chosen:** a choice with an empty value is drawn as daisyUI's own means of clearing a rating, and
not as a star (FR-009). A field with no empty choice offers no way to clear it.

**Rejected:** dropping the empty choice. An optional rating could then never be undone once
picked, which a select and a radio group both allow.

**For the build to check:** daisyUI draws every star as filled when no input of the group is
checked. FR-008 requires a rating with no value to show no star as picked, including on a required
field with no empty choice. The plan has to find how to do that with stock daisyUI, and should not
assume the markup of the radio group is enough.

**ADR:** none. It is how one template treats one case.

## D6. A range takes its limits from the field and adds none

**What was ambiguous:** a slider needs a lowest value, a highest value and a step. The issue names
none.

**Chosen:** the limits are the ones Django already writes on the number input from the field's
`min_value`, `max_value` and `step_size`, plus any the developer set on the widget (FR-013). With
none, the browser's defaults for a slider apply. The pack does not refuse a range on a field with
no limits, and does not refuse one on an optional field, although a slider always submits a
number.

**Rejected:**

- Raising when the field declares no limits. The browser's defaults are a working slider, and the
  field still validates whatever arrives.
- Arguments for the limits on the drawing. The field already owns them, and a second place to
  state them could disagree with what the field validates.

**ADR:** none. It follows from ADR 0004: the pack adds its class and leaves the widget's own
attributes alone.

## D7. No value readout and no step marks on a range

**Chosen:** a range is the slider alone, with the field's frame around it. The specification
leaves out a number beside the slider and marks under it.

**Why:** daisyUI has no component for either. A live readout needs a script, and the pack ships
none. Whether it may is tied to #47. Step marks in daisyUI's documentation are plain elements laid
out with utilities, which ADR 0003 allows only for layout where daisyUI has nothing, and they
would need a decision of their own.

**Open with the maintainer:** #90 asks whether the pack should offer either.

**ADR:** none. It is a boundary of this feature.

## D8. Half stars, other shapes and a vertical range are left out

**Chosen:** the rating uses daisyUI's ordinary star with one input for each choice. Half stars,
which daisyUI draws with two inputs for each star, its other mask shapes, and its vertical range
are not part of this feature.

**Why:** the issue names "a star rating and a range slider" and nothing more. Each of the three
would need a further statement from the developer, and Article II says to build what is needed
now.

**Revisit if:** a project asks for one.

**ADR:** none.

## D9. No sketch before the build

**Chosen:** the feature is built without a sketch for the maintainer to look at first.

**Why:** it places two stock daisyUI components inside the field frame the pack already draws, and
adds one demo page of the kind every earlier feature added. Nothing in it needs a new design.

**ADR:** none.

## D10. Nothing under `.github/` changes

**Chosen:** the feature needs no workflow change. It adds no dependency and no supported version,
and the test matrix stays as it is.

**ADR:** none.

## D11. Which drawings a field takes is decided by its widget, in one table

**Decision:** `FieldInput` holds the drawings each kind of widget takes: the three of a boolean
field for a `CheckboxInput`, `rating` for a select or a radio group that holds one value, `range`
for a `NumberInput`, and none for anything else. A drawing stated for a field has to be among its
own, and the error carries them as the names allowed.

**Why:** FR-021 asks the error to say which drawings the field can take. Before this feature the
answer was all three or none, so the widget was checked first and the name second. With five
drawings over three kinds of field, one rule replaces the two checks.

**Revisit if:** a drawing applies to more than one kind of field.

**ADR:** docs/adr/0029-each-kind-of-field-has-its-own-drawings.md

## D12. A rating is drawn through a radio group made for the draw

**Decision:** a radio group stated as a rating is drawn through a shallow copy of its widget
that names the pack's rating template. A select stated as a rating is drawn through a
`RadioSelect` built for that draw from the select's attributes and choices. A number input stated
as a range is drawn through a shallow copy whose input type is `range`. The form's own widget is
never written to.

**Why:** a rating is radio inputs, and Django's `RadioSelect` already gives each option the
widget's attributes, an id of its own and `checked`. A `Select` gives its options none of them
and withholds `required` when its first choice has a value. Building a radio group from the
select reuses Django's behaviour in place of re-creating it on a copy of the select. Passing
`type` as an attribute to a number input would write the attribute twice.

**Rejected:** copying the select and overwriting the four class attributes that make it behave
as a radio group. It leaves `use_required_attribute` as the select's.

**Revisit if:** a project needs a select subclass's own `create_option` to reach a rating.

**ADR:** docs/adr/0030-a-stated-drawing-may-set-the-element-drawn.md

## D13. A rating with nothing picked needs no markup beyond daisyUI's

**Decision:** the pack writes daisyUI's ordinary rating markup and nothing more for a field with
no value. This settles the point D5 left for the build.

**Why:** in daisyUI 5 every star starts dimmed, and only a checked input and the ones before it
are raised (research R2). An unchecked group therefore shows no star as picked. The concern in D5
came from daisyUI 4, which dimmed the stars after the checked one.

**Revisit if:** daisyUI changes which stars it dims.

**ADR:** none — it is how stock daisyUI behaves, and the pack decides nothing.

## D14. A rating in error draws its stars in the error colour

**Decision:** a rating in error leaves the chosen colour out and writes `bg-error` on each star.
A range in error takes `range-error`. This settles the point D4 left for the plan.

**Why:** every other input the pack draws carries an error modifier of its component, and a
radio takes `radio-error`. A rating has no modifier of its own for a colour, so the error colour
is written the way its chosen colour is (D4). FR-020 then holds as it does elsewhere: the error
is the only colour the field shows.

**Revisit if:** daisyUI gives the rating an error modifier.

**ADR:** docs/adr/0031-a-ratings-colour-is-a-class-on-each-star.md

## D15. A star is named by its choice's label, and the pack adds no text

**Decision:** each star's `aria-label` is the label of its choice, and the clearing input's is
the label of the empty choice. The pack adds no word of its own for either drawing, so FR-024 is
met with nothing to translate.

**Why:** FR-011 asks for the choice's label. A word such as "Clear" for the empty choice would be
text the developer did not write, in place of the empty label they did.

**Revisit if:** the maintainer wants the clearing input named by the pack when the empty label is
Django's row of dashes.

**ADR:** none — local to this feature's one template.

## D16. A select drawn as a rating is described once, by its fieldset

**Decision:** the stars of a select drawn as a rating do not carry the `aria-describedby` Django
adds to a widget that is not a fieldset. The fieldset names the help text and the errors, as it
does for a radio group. One the developer set on the widget is kept.

**Why:** Django decides it from the form's own widget, which is still a select. Left alone, a
screen reader would read the help text on every star, and a select and a radio group stated as
the same rating would be drawn differently.

**Revisit if:** Django lets a caller say for one render whether the widget is a fieldset.

**ADR:** none — it follows ADR 0011, which frames a group as a fieldset that carries the
description.

## D17. The clearing input is drawn first, whatever its place among the choices

**Decision:** the input for an empty choice is drawn before the stars even when the field lists
the empty choice last. The stars keep the field's order.

**Why:** the design review found that daisyUI raises every star before the checked input. A
field with no value has its empty choice checked, so a clearing input drawn after the stars
would show them all as picked, against FR-008. FR-006 orders only the choices that have a value.

**Revisit if:** daisyUI changes which stars it raises.

**ADR:** none — local to the rating's template.

## D18. Design review: what was applied and what is carried

**Decision:** all six findings were applied to the plan and the tasks. None was declined.

- DR-001 (medium): the existing drawings demo page names its three drawings itself (plan, T001).
- DR-002 (medium): the clearing input is drawn first (D17, plan, T002).
- DR-003 (low): the one existing test that pins the drawings table is named as extended (T001,
  T004).
- DR-004 (low): a star's `aria-label` is the choice's label as plain text (plan, T001).
- DR-005 (low): empty means the empty string, and a choice with the value `0` is a star (plan,
  T002).
- DR-006 (low): a slider always submits a number, so an extra form of a formset that holds a
  range is always submitted as changed. The README says so (T004), and the question of whether
  the pack should do anything about it is filed for the maintainer.

**Why:** each was verified against the code or the stylesheet by the reviewer, and each remedy
is the edit the finding named.

**ADR:** none — a record of the review, not a constraint on the code.

## D19. The demo's posting range is an optional field with an initial value

**Decision:** the range of the demo page's form that posts is an optional `IntegerField` with an
initial value, and the form is renamed `RatingAndRangeForm`. The range states of the page are a
form of their own, `RangeStateForm`, built beside the rating states.

**Why:** a slider always submits a number, so "required" says nothing a person can act on, and an
initial value is where the slider rests when the page opens. An optional field also leaves the
page's rating tests, which post stars alone, unchanged.

**Revisit if:** the maintainer decides the pack should do something about a range in an optional
field (#116).

**ADR:** none — a choice about the demo page.

## D20. The choices demo page's test looks for a size on the element that holds a rating

**Decision:** the test of the size, colour and variant demo page that checks every kind of input
is drawn at a stated size also looks at `div` elements. Nothing else in it changed.

**Why:** the test builds its cases from the size table and looks for each size's class on an
input, a select or a textarea. A rating's size is daisyUI's modifier of the element that holds
the stars (D4), so no drawing of a rating could satisfy it. The test still fails if the page
stops drawing any kind of input at a stated size.

**Revisit if:** a later kind of input carries its size somewhere else again, at which point the
test should ask the pack where.

**ADR:** none — a change to one test of the demo project.
