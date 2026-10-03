# Decisions: Booleans drawn as a checkbox, toggle or switch

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below was
made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as follows. A developer says in Python, for one boolean field at a
time, whether it is drawn as a checkbox, a toggle or a switch. Checkbox is the default, so nothing
changes for a form that says nothing. A toggle or a switch keeps the label, required marker, help
text, errors and disabled state of a checkbox, submits the same data, and takes the size and colour
choices FS-007 introduces. The feature serves G4, sits in R5, and depends on #11. Everything about
sizes, colours and variants themselves stays with #11, and the checkbox itself stays with #6.

**Why:** the issue is one sentence and the roadmap deliverable is one line, and neither conflicts
with this reading. Each gap it fills is recorded as its own decision below.

**ADR:** none. This is the record of how the specification was written, not a constraint on the
code.

## D2. A switch is a toggle that assistive technology announces as a switch

**Chosen:** a toggle and a switch are both built from daisyUI's toggle. They differ in what a
screen reader says: a toggle is a checkbox that is checked or not, and a switch is a switch that is
on or off (FR-004, FR-005).

**Rejected:**

- Treating the two words as one drawing with two names. The issue, the roadmap and G4 all list
  them separately, so the maintainer means two things.
- Giving the switch a look of its own. daisyUI has a checkbox and a toggle and nothing else for a
  boolean. A third look would need classes the pack defines itself, which Article XIV rules out,
  and it would not work on the CDN build without a stylesheet from the pack.
- Setting them apart by where the label sits, with a switch laid out as a settings row. That is
  appearance. It cannot be stated as a requirement or tested, and it would leave the two
  indistinguishable to anyone not looking at the page.

**Why defensible:** it is the only difference between the two that is behaviour, that needs
nothing beyond stock daisyUI, and that matters to someone. An on/off setting that takes effect as
a state reads more naturally as a switch to a screen-reader user, and a field that records consent
or agreement reads more naturally as a checkbox. The developer knows which one a field is.

**Open with the maintainer:** #17 asks whether this is the distinction he had in mind. If he
answers differently, FR-004 and FR-005 change and nothing else in the specification does.

**ADR:** expected. It is durable, it shapes the public surface, and a reader of the code will ask
why two options draw the same component. To be written when the feature is built.

## D3. Checkbox is the default and existing forms do not change

**Chosen:** a boolean field with no drawing chosen is the checkbox FS-002 draws (FR-002).

**Rejected:** making the toggle the default for the pack. R1 promises that a plain Django form
looks right with no per-form work, and a checkbox is what Django and every other pack draw for a
boolean. Changing it would also alter forms that never asked for this feature.

**ADR:** none. It follows from R1 and nobody would expect otherwise.

## D4. The drawing is chosen per field only

**Chosen:** there is no way to set the drawing once for a whole form (FR-001).

**Rejected:** a form-wide drawing beside FS-007's form-wide size and colour. The issue and the
roadmap both say "chosen per field". Unlike a size, a drawing is rarely right for every boolean in
a form: a settings form may want toggles while its "I agree to the terms" field wants a checkbox.
Article II says to build what is needed now.

**Revisit if:** forms with many toggles make the repetition a nuisance in a real project.

**ADR:** none. It is a boundary of this feature, not a constraint on later ones.

## D5. Only a field drawn by Django's single checkbox is a boolean field

**Chosen:** the choice applies to a field whose widget is Django's single checkbox or a subclass
of it (FR-003). A null-boolean field, which is a select with three states, and a checkbox group
are outside it.

**Why:** a toggle has two states, so it cannot stand in for a three-state select. A checkbox group
is a multiple-choice field that FS-002 owns, and drawing its options as toggles is a separate
want nobody has asked for.

**ADR:** none. Local to this feature.

## D6. A choice the pack cannot honour raises an error

**Chosen:** an unknown drawing name, or a toggle or switch on a field that is not a boolean field,
raises an error naming the field (FR-012).

**Rejected:** drawing the default and carrying on. The repository's own notes on the demo project
describe how costly quiet failures are there: a missing component, an unknown class and an
unresolved menu entry all draw nothing and raise nothing. A misspelt drawing name that silently
gives a checkbox would be the same trap in the pack itself.

**ADR:** none here. If FS-007 settles how the pack treats a mistaken size or colour, this follows
the same rule and that record covers both.

## D7. The drawing is chosen where FS-007's per-field choices are made

**Chosen:** the specification does not invent a place for the choice. It goes wherever FS-007
puts a field's own size and colour, and is honoured wherever those are (FR-006).

**Why:** a developer should set a field's drawing, size and colour in one statement. Two
mechanisms for per-field choices in one pack would need a justification under Article III, and
there is none. FS-007 is being specified at the same time, so this specification names the
dependency and leaves the mechanism to it.

**ADR:** none from this feature. The mechanism is FS-007's decision to record.

## D8. A variant does to a toggle whatever it does to a checkbox

**Chosen:** the issue asks for "size and colour" and leaves out variant. This specification says
only that a toggle or a switch treats a variant as a checkbox does under FS-007.

**Why:** daisyUI's checkbox and toggle have sizes and colours and no variants such as ghost. Whether
a form-wide variant is ignored by inputs that have none is a question about every such input, so it
is FS-007's to answer once.

**ADR:** none. Nothing is decided here.

## D9. No sketch before the build

**Chosen:** the feature is built without a prototype stage.

**Why:** it places stock daisyUI components in a form and adds one page to the demo project. There
is no new page design and no flow to judge.

**ADR:** none.

## D10. The drawing is a fourth argument of `Choice`, and the form's statement has none

**Decision:** `Choice(drawing="toggle")`, beside `size`, `color` and `variant`. It is stated in a
layout or by name in `FormChoices(fields=...)`, and merged the way the other three are.
`FormChoices` gains no `drawing`.

**Why:** ADR 0019 already rules that a later feature needing a statement for one field adds an
argument to `Choice`. FR-006 asks for the same place and manner as a field's size and colour, and
FR-001 and D4 keep the drawing per field.

**Revisit if:** a form-wide drawing is asked for (D4).

**ADR:** none — ADR 0019 already states the rule this follows, and the missing form-wide drawing
is a boundary of this feature that D4 records.

## D11. A mistaken drawing raises `InvalidChoice` with the kind `drawing`

**Decision:** an unknown name raises `InvalidChoice` with the three names as `allowed`. Any
drawing stated on a field whose widget is not Django's single checkbox raises it with nothing
allowed, `checkbox` included. `None` and `INHERIT` state nothing and never raise.

**Why:** D6 said this would follow FS-007's rule once it existed. ADR 0020 is that rule: a choice
stated on one field that its input cannot take is a mistake. A second error class for one more
kind would be a second mechanism for the same thing.

**Revisit if:** developers need to tell a mistaken drawing from a mistaken size without reading
`kind`.

**ADR:** none — ADR 0020 covers it; the drawing is one more kind under the same rule.

## D12. A toggle is a component of its own in the tables, not a modifier of the checkbox

**Decision:** a field drawn as a toggle or a switch has the component `toggle`, with its own rows
for size and colour and its own error modifier. It is still counted as a single checkbox by the
frame, so the label is drawn the same way.

**Why:** daisyUI's toggle replaces the `checkbox` class and has modifiers of its own
(`toggle-sm`, `toggle-primary`). Writing `checkbox toggle` or `checkbox-sm` on a toggle would
mix two components on one input. ADR 0020 says a new kind of input adds a row.

**Revisit if:** daisyUI folds the toggle into the checkbox.

**ADR:** none — it applies ADR 0020's "a new kind of input adds a row" and is sealed inside
`Modifiers` and `FieldInput`.

## D13. No template in the pack changes

**Decision:** the frame, the label and the widget templates are untouched. The drawing changes
only the class and, for a switch, the role that `FieldInput` hands to the widget for one render.

**Why:** everything FR-009 lists is drawn by the frame around the input and does not depend on
the component. Keeping it there is what makes "keeps everything a checkbox has" true by
construction, not by a second copy of the markup.

**Revisit if:** a drawing needs the label arranged differently.

**ADR:** none — local to this feature; it follows ADR 0004 and ADR 0006 and adds no rule.

## D14. The pack adds no text for a toggle or a switch

**Decision:** neither drawing adds a word to the page, so FR-015 is met with nothing to translate
and no test is written for it.

**Why:** the on and off state is announced by assistive technology from the role and the checked
state. Visible "On" and "Off" words would be text the developer did not ask for.

**Revisit if:** a drawing gains visible state text.

**ADR:** none — nothing is decided that constrains later work.

## D15. A drawing stated around a button is refused

**Decision:** a `Choice` in a layout that states a drawing and holds a button raises
`InvalidChoice` with the kind `drawing`, nothing allowed and the button as `target`.

**Why:** the design review found that the plan passed it over in silence. SC-006 says every
choice the pack cannot honour is reported, and ADR 0020 already refuses a choice stated on one
thing that cannot take it.

**Revisit if:** wrapping a whole button bar and its fields in one `Choice` with a drawing turns
out to be something forms want.

**ADR:** none — ADR 0020's rule applied to one more kind.

## D16. What the design review found, and what was done

**Decision:** one reviewer read the plan through three lenses and approved it with one medium and
four low findings. All five were applied to the plan and the tasks before any code.

- DR-001 (medium): size and colour reach a toggle only in the third story, so the README example
  and the demo form state a drawing only until then. Applied to plan and T002, T003.
- DR-002 (low): the submission test builds its posted data from the drawn inputs. Applied to T002.
- DR-003 (low): a drawing around a button. Decided as D15, applied to plan, research and T001.
- DR-004 (low): CONTEXT's Choice and Variant entries are amended with the new term. Applied to T002.
- DR-005 (low): the widget is checked before the name, and the name against a tuple. Applied to
  plan and T001.

**Why:** each costs a sentence now and a rework later.

**ADR:** none — a record of the review, not a constraint on the code.
