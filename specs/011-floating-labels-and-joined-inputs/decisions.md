# Decisions: Floating labels and joined inputs

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below
was made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as two parts. First, a developer states in Python that a field is
drawn with daisyUI's floating label, once for a form or for one field, in the place where a size,
a colour and a variant are stated. The label stays tied to the input, and the required marker,
help text and errors are kept. Second, a developer names several fields in a layout to be drawn as
one daisyUI join under one label, such as a country code beside a phone number. Each joined field
stays a field of its own, with its own accessible name, help text, errors and cleaned value. Both
parts take the size, colour and variant choices of FS-007. A form that states neither is drawn as
before. The feature serves G9 and is one of two slices of R7. Rating and range inputs are #86.

**Why:** the issue is one paragraph and the roadmap item one sentence, and neither conflicts with
this reading. Each gap it fills is recorded as its own decision below.

**ADR:** none. This is the record of how the specification was written, not a constraint on the
code.

## D2. A floating label is a choice, stated for a form and for one field

**Chosen:** a floating label is stated where FS-007's choices are stated and follows their order:
the field's own statement wins over the form's, and a field can undo the form's (FR-001, FR-002).

**Rejected:**

- A layout object of its own that wraps a field. ADR 0019 says a later statement about one field
  is added to the existing statement and no second layout object is defined for it. A wrapper
  would also leave a form drawn without a layout unable to float a label.
- Per field only, as FS-008 did for a drawing. A drawing is rarely right for every boolean field
  of a form. A floating label is a decision about a form's density and is usually wanted on all
  of its fields, which is the "dense forms" the issue names.
- For the form only. One field with a long label, or one the developer wants to stand out, has to
  be able to opt out.

**Why defensible:** it reuses the one mechanism the pack already has, costs a developer nothing to
learn, and reaches both drawing paths.

**ADR:** expected, at build. It adds a fifth kind of choice, and a kind that is neither a class
from the `Modifiers` table nor limited to boolean fields. The record should say how it sits beside
ADRs 0019 to 0022.

## D3. Which fields take a floating label, and what happens to the rest

**Chosen:** a field the pack draws as a daisyUI input, textarea or select (FR-003). Stated for the
form, the choice passes every other field over. Stated on one such field by name, it raises
(FR-011).

**Why:** daisyUI 5's floating label is a wrapping label holding a span and the input. Its rules
react to an `input` or a `textarea` showing its placeholder, and a select inside it shows the
label at its edge at all times. A checkbox, a radio or checkbox group and a toggle have their
label beside them. A file input, a multi-widget field and a date drawn as three selects have no
single box for the label to sit on.

Passing over for the form and raising for one named field is the rule ADR 0020 already set for a
choice that an input has no modifier for. A form-wide choice has to be usable on a form that
mixes kinds of field, and a choice on one named field that can never apply is a mistake.

**ADR:** none of its own. It belongs in the record D2 expects.

## D4. An empty field shows the label's text, and a disabled field keeps its ordinary label

**Chosen:** with no placeholder of the developer's own, an empty floating-label field shows the
label's text (FR-006). A placeholder the developer set is kept. A disabled field for which a
floating label is stated is drawn with the ordinary label (FR-007).

**Why:** this follows from what daisyUI 5 does, read from its stylesheet:

- while an input or textarea shows its placeholder, the floating label is transparent, and the
  placeholder is what a person sees;
- when the field has focus or a value, the placeholder fades and the label is shown at the edge;
- an input with no placeholder attribute never counts as showing one, so its label sits at the
  edge at all times;
- when the input is disabled, the label is transparent in every state.

The issue describes a label that "sits inside the input and moves up when it has a value". The
only way stock daisyUI gives that is a placeholder holding the label's text. `InlineField` already
offers the label as a placeholder and keeps one the developer set, so the same rule is used here.

The last point is the one that needs a requirement. A disabled field with a value would show no
label and no placeholder, so a person could not tell what it is. The pack cannot fix that with a
class of its own (Article XIV), so the field falls back to the ordinary label.

**Rejected:** raising when a floating label is stated on a disabled field. A field is often
disabled at run time, for one person and not another, and an error for that would be hostile.

**ADR:** expected, at build, as part of the record D2 expects. The fallback for a disabled field
is not something a reader would guess.

## D5. A floating label does not combine with another decoration

**Chosen:** a field with attached text, with buttons joined to it, drawn inline or drawn as a
member of a joined group does not take a floating label. The form's statement passes it over, and
a statement on that field raises (FR-010, FR-011).

**Why:** attached text is itself a wrapping label that holds the input (ADR 0026), and a floating
label is another. Two wrappers on one input is markup daisyUI does not document. An inline field
has no visible label by definition. Inside a join, the floating wrapper would be the joined child
in place of the input, which daisyUI does not document either. Article XIV says stock markup wins.

**Revisit if:** daisyUI documents a floating label inside a join or beside attached text.

**ADR:** none of its own. It belongs in the record D2 expects.

## D6. Joining is a layout object the package defines

**Chosen:** several fields are joined by naming them together in the form's layout (FR-012). The
specification does not name the class.

**Rejected:**

- An argument on the existing per-field statement. Joining is a statement about several fields at
  once, in an order, with a label of its own. ADR 0019 reserved that statement for one field or
  one button.
- Reusing a layout object django-crispy-forms ships. `MultiField` is already drawn as a fieldset
  of whole fields, each in its own frame, and `Div` with a class of `join` would put every field's
  frame, label and errors inside the join. `FieldWithButtons` takes one field. None of them can
  mean "these inputs, joined" without changing what it draws today.
- A widget. A `MultiWidget` joins the parts of one field. The issue asks to join several fields,
  each validated and cleaned on its own.

**Why defensible:** the request cannot be met without something in the layout that names several
fields. Stating it there keeps it out of the form class and beside the other arrangement
decisions.

**ADR:** expected, at build. ADR 0008 says the package defines no layout classes and ADR 0019
made one exception. This is a second, and the record should say why it does not subclass or
shadow an upstream object.

## D7. One label for the group, and each member keeps the rest

**Chosen:** the group has one visible label, given by the developer, and is framed as the pack
frames any group of inputs (FR-014). Each input is named by its own field's label for assistive
technology (FR-015). Each member's help text and errors are drawn once with the group and tied to
that member's input (FR-016). The group's label carries the required marker when any member is
required (FR-017).

**Rejected:**

- Drawing every member's label above its input. The inputs are joined edge to edge, and separate
  labels above them is the row of columns the pack already draws.
- Taking the group's label from the first member. A country code and a phone number are together
  "Phone", which is neither field's label.
- One shared set of errors with no tie to an input. ADR 0005 keeps Django's ids, and Django
  writes each input's description itself. Tying every error to its own input costs nothing and
  tells a person which part is wrong.

**Why defensible:** it is what ADR 0011 and ADR 0027 already do for a group and for the parts of
a multi-widget field: one legend, and a name on each part.

**ADR:** expected, at build, in the record D6 expects.

## D8. A joined group holds inputs and selects, and no buttons

**Chosen:** a member is a field the pack draws as a daisyUI input or select (FR-013). Anything
else raises (FR-021). Buttons are not accepted.

**Why:** these are the two kinds ADR 0026 already joins. A textarea, a file input, a checkbox and
a group of options are not shown joined in daisyUI's documentation. Raising, where
`PrependedText` draws the field undecorated, is deliberate: a decoration on one field can be
dropped and leave a usable field, and a group whose member cannot be joined has no sensible
drawing left.

Buttons are left out because the issue asks to join fields, and `FieldWithButtons` exists for a
field with buttons. A group of fields ending in a button is a likely later ask, and daisyUI's own
first example of a join is one. It is filed as #94 for the maintainer.

**ADR:** none. It is a boundary of this feature.

## D9. Sizes inside a joined group follow FS-007, and one size is not enforced

**Chosen:** each member takes the choices in force for it under FS-007 (FR-023). A size stated
for the form or around the group reaches every member. A member's own size still wins for that
member.

**Rejected:** forcing one size on a group, or raising when members differ. ADR 0026 says a joined
group takes one size, and #15 is open on exactly how far that goes for attached text and buttons.
This specification is told not to settle #15, so it keeps FS-007's order and names the issue.

**ADR:** none. It follows FS-007 as built.

## D10. No sketch before the build

**Chosen:** the feature is built without a prototype stage.

**Why:** both parts are stock daisyUI components placed in a form by a statement in Python. The
only pages added are demo pages that list states, which follow the pattern of the existing ones.

**ADR:** none.
