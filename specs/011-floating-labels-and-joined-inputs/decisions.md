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

## D11. The floating label is spelt `label="floating"`

**Chosen:** `Choice(label="floating")` and `FormChoices(label="floating")`. `None` is the
ordinary label and undoes the form's statement for one field. The class is held in
`Modifiers.labels`, written out as a literal.

**Rejected:** a boolean, `floating=True`. Every other kind of choice is a name from a table with
`None` as the ordinary drawing and `INHERIT` as the default, and `Choice.over` merges them all
the same way. A boolean would be the one kind with three states spelt `True`, `False` and
`INHERIT`. A name also leaves room for another label daisyUI may add.

**Why defensible:** the spec says an unknown value for the label raises "as it does for an
unknown size", which presumes a set of names.

**ADR:** docs/adr/0033-a-floating-label-is-a-kind-of-choice.md

## D12. A floating label stated around a button raises

**Chosen:** `Choice(Submit(...), label="floating")` raises `InvalidChoice` with nothing allowed,
as a drawing around a button does.

**Why:** a `Choice` in a layout is checked against everything it holds (ADR 0020, FS-008 D15).
Passing a button over would make the label the one kind that a `Choice` in a layout does not
check.

**Revisit if:** developers wrap whole sections, button bar included, to float their labels, and
the error turns out to be in the way.

**ADR:** none. It applies an existing rule to the new kind.

## D13. A member is drawn by django-crispy-forms' own `Field` with a template of the pack's

**Chosen:** `Join` builds a `Field` for each member, gives it the member template, and renders
it through `render_field`, inside the accumulated `Choice` when the member is wrapped in one.

**Rejected:**

- Signalling a member through the template context and letting `daisyui/field.html` draw it.
  The join has to keep hidden inputs out of its children, so it must draw members one by one
  and know which is which. A context flag draws them as one string.
- Calling the widget directly from `Join.render`. It would copy what `render_field` does:
  recording the field as rendered, applying a `Field`'s attributes, and reporting a name the
  form lacks.

**ADR:** none of its own. It belongs in the record for the joined group.

## D14. The developer's id, class and attributes go on the join element

**Chosen:** on the `<div class="join">`, and not on the fieldset around it.

**Why:** `join-vertical` only works on the element that carries `join`, and the spec's
assumptions say that is how a developer stacks a group. `FieldWithButtons` already puts them
there (ADR 0026).

**ADR:** none of its own. It belongs in the record for the joined group.

## D15. The group's label is escaped

**Chosen:** `Join(label=...)` is text and is escaped.

**Why:** ADR 0025 draws a developer's text as markup only where django-crispy-forms documents it
as markup. `Join` is this package's own, so nothing documents it that way. Escaped text can also
serve as the fieldset's `aria-label` when the helper turns labels off.

**ADR:** none. ADR 0025 already decides it.

## D16. An input member fills the group and a select member is as wide as its options

**Chosen:** a member drawn as an input takes `flex-1` and one drawn as a select takes `w-auto`,
in place of `w-full`. A width the developer wrote on the member is kept and the pack adds
neither. `w-auto` is added to the class test by name.

**Why:** research R6. Equal shares is what a `Row` of columns already gives.

**Revisit if:** #16 or #18 rules on which layout utilities the pack may write.

**ADR:** docs/adr/0034-fields-are-joined-by-a-layout-object-of-the-packs.md

## D17. Help text and errors move to a template of their own

**Chosen:** `daisyui/field_messages.html` draws a field's help text and error element.
`daisyui/field_body.html` includes it, and so does the joined group, once per member.

**Why:** FS-001 left them inline "until a second template needs them". The joined group is that
template, and two copies of the ids ADR 0005 fixes would drift.

**ADR:** none. ADR 0029 already makes every template public, and the README's list records it.

## D18. A joined group's members are checked when drawn, and the error is `InvalidMember`

**Chosen:** a new error, `InvalidMember(ValueError)`, carrying `member`: the field's name, or the
class name of a layout object the group cannot hold.

**Rejected:** reusing `InvalidChoice`. It carries a kind, a value and the names allowed, none of
which a field that cannot be joined has.

**ADR:** none of its own. It belongs in the record for the joined group.

## D19. The demo's standalone pages are one per page

**Chosen:** `/floating-labels/standalone/` and `/joined-groups/standalone/`.

**Why:** each story then adds its own pages and no story edits another's template. FR-028 asks
that both be shown on a page that loads only the CDN install, and does not ask for one page.

**ADR:** none. Local to the demo project.

## D20. The design review's findings, and what was done with each

One reviewer, three lenses, verdict approve. Nothing was critical or high.

- **DR-001 (medium):** the templates of the joined group were added one task before a state drew
  them, which the replacement check refuses. The state moves to the task that adds the
  templates.
- **DR-002 (medium):** a name the form lacks would have raised out of the joined group where
  django-crispy-forms only logs it. The plan leaves such a name to django-crispy-forms and a
  test covers it.
- **DR-003 (low):** the research said daisyUI sizes a floating label's text for inputs only. It
  sizes it for selects and textareas too, so the README says nothing about a limit.
- **DR-004 (low):** the demo shows a read-only member as well as a disabled and a hidden one.
- **DR-005 (low):** the demo shows a joined group at every colour and in the variant.
- **DR-006 (low):** a field disabled only by a disabled fieldset around it is not detected. The
  tag cannot see the layout around a field. The README says to undo the floating label there.

Watch items carried into the briefs: a textarea inside `PrependedText` has no attached text and
so floats; the README's example of a joined group matches the one the test draws; the docstrings
say which `join` and which `label` they mean; the report pastes the command and result of the
comparison for SC-003.

**ADR:** none. It records a review, and each remedy is in the plan or the tasks.

## D21. A rating and a range take no floating label and cannot be joined

**Chosen:** a field drawn as a rating or as a range is not an input, a textarea or a select as
the pack draws them. The form's floating label passes it over, a floating label stated on it
raises `InvalidChoice` naming the field, and as a member of a joined group it raises
`InvalidMember` naming the field.

**Why:** rating and range inputs arrived on the main branch while this feature was being built.
A rating is a group of radio inputs and a range is a slider, and daisyUI documents neither
inside a floating label or a join. FR-003 and FR-013 already limit both parts to an input, a
textarea and a select, so this is the specification applied to two drawings it could not have
named.

**ADR:** none. It follows from the two records this feature writes.

## D22. A group's members are a small named type

**Chosen:** `Join.members()` returns a list of `Member`, a frozen dataclass holding the field's
`name`, the `attrs` of the `Field` that held it and the `Choice` around it.

**Why:** the plan said one entry per name with the attributes and the choice. A named type reads
better than a tuple of three, and the glossary already has the term.

**ADR:** none. It is a detail of the layout object, covered by its record.

## D23. One import line changed in the suite's shared forms

**Chosen:** `tests/forms.py` imports `Field` beside `Layout`, for the joined forms the suite now
draws. No existing form and no existing assertion changed.

**ADR:** none. Local to the tests.
