# Decisions: django-tomselect support

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The package ships a stylesheet, and the developer loads it

**What was ambiguous:** Article XIV says the pack ships no stylesheet and defines no class. Tom
Select builds its control in the browser under class names of its own, so there is no template of
the pack's to put daisyUI classes on.

**Chosen:** the package ships `tomselect.css`, for django-tomselect's controls only. The developer
adds it to their pages. The pack and the widget never load it. Each third-party package supported
later gets a stylesheet of its own, never a shared one. This is the maintainer's ruling, given
when the feature was agreed.

**Why:** a stylesheet the widget loaded would arrive on pages whose owner never chose it, and one
shared stylesheet would grow with every package supported and be paid for by projects that use
none of them. Article XIV is amended and not waived: the pack's own templates still define no
class and need no stylesheet.

**ADR:** docs/adr/0042-one-optional-stylesheet-for-each-supported-package.md

## D2. Legibility is checked under `light` and `dark` only

**Chosen:** the stylesheet's pairings are held to FS-012's contrast standard under daisyUI's
`light` and `dark` themes. The check over every shipped theme is not extended to it. This is the
maintainer's ruling.

**Why:** the stylesheet names no colour of its own (FR-004), so under any other theme it draws
what that theme's variables give a stock control. A shortfall there is the theme's, and ADR 0034
already says how one of those is handled.

**ADR:** docs/adr/0043-a-supported-packages-stylesheet-is-checked-under-light-and-dark.md

## D3. Grouping is added here, though it is behaviour and not look

**What was ambiguous:** django-tomselect draws a group heading but has no setting that tells Tom
Select which group an option fetched from the server belongs to. Supplying one goes beyond
drawing.

**Chosen:** this package supplies it, as part of its support for django-tomselect. The maintainer
asked for grouping by name and confirmed that it must work without a template of the developer's.

**Why:** every project that needs groups carries the same small template today. The way it is
supplied is for the plan. Whatever the plan chooses must touch django-tomselect only through
places it offers for the purpose, and is retired if django-tomselect gains a setting of its own.

**ADR:** docs/adr/0044-grouping-is-added-by-extending-django-tomselects-template.md

## D4. Attached text, joined buttons and joined groups are left as they are

**Chosen:** this feature does not say what the pack draws when a django-tomselect control is put
inside a layout object that attaches text or joins fields. The README says these are not
supported.

**Why:** the maintainer ruled them out of this feature. Fixing a behaviour for them now would be
specifying something nobody has asked for.

**ADR:** none. Nothing is decided here beyond leaving the pack as it is.

## D5. The supported django-tomselect releases sit outside the support window

**What was ambiguous:** FS-013 declares the versions of Django, django-crispy-forms and daisyUI
the package supports and promises a period for each new release. Nothing said whether a supported
third-party package joins that declaration.

**Chosen:** it does not. The README names the django-tomselect releases the support is tested
against, with no period promised.

**Why:** G12 is aspirational and the package is complete without it. A promise to follow another
optional package's releases within a fixed time would make the window depend on something most
host projects do not install.

**ADR:** none. The README's statement is the record.

## D6. Two plugins are covered, and the rest wait for a request

**Chosen:** the support covers the clear button and the remove button. The dropdown header, the
dropdown footer, the search input inside the dropdown and checkboxes beside the options are not
covered. This is the maintainer's ruling, given when he approved the specification.

**Why:** the first two stories cannot be delivered without those two. Every other plugin is
styled when a project needs it, which is how the package takes on fields and widgets in general
(Article XV).

**ADR:** none. The README's list of covered plugins is the record.

## D7. The stylesheet may reach a box that holds an open control

**What was ambiguous:** FR-003 first said every rule applies only inside a control or its
dropdown. The approved sketch needs three rules that do not: one hides django-tomselect's status
element, and two let a modal box and a table's scroller overflow while a dropdown in them is open.

**Chosen:** FR-003 names those three. A page with no control is still drawn exactly as before.

**Why:** the maintainer approved the screens that need them, and SC-004 is the promise the
requirement exists to keep.

**ADR:** none. The scope test's list of exceptions is the record.

## D8. Article XIV is amended in its own pull request

**Chosen:** the amendment FR-006 asks for is made in a pull request of its own, which merges
before this one. The README sentences and the decision records change here.

**Why:** the constitution says a rule is changed in its own pull request and then the work is
done.

**ADR:** none. The constitution's own footer records the amendment.

## D9. Nothing in the suite runs a browser

**Chosen:** the suite holds the pack's markup, the stylesheet's structure and its contrast. What
a browser does with the rules was measured once during the sketch and is walked by the maintainer
at review.

**Why:** the repository has no browser tests and its workflow installs none. Adding one for a
feature that serves an aspirational goal would cost every later change a slower suite.

**ADR:** none. Local to this feature.

## D10. htmx start-up is django-tomselect's setting, set once

**Chosen:** the README tells a host project that swaps forms in with htmx to set `use_htmx` in
django-tomselect's default configuration. The package changes nothing to make it automatic.

**Why:** it is what django-tomselect provides for the purpose, and FR-026 allows what
django-tomselect already asks for.

**ADR:** none. The README's section is the record.

## D11. Three behaviours of django-tomselect are recorded and left alone

**Chosen:** typed text staying in a multiple control after a pick, the message an empty required
control gives, and the Tab key stopping inside an open dropdown are each an issue in this
repository. Nothing here patches them.

**Why:** the specification's assumptions say this package does not patch django-tomselect's
scripts.

**ADR:** none. The three issues are the record.

## D12. No test that a state has a rule

**Chosen:** the suite does not hold a table of states and the selectors that draw them. The design
review found that such a test can fail only when someone removes a rule on purpose, which the
testing standard calls a change detector.

**Why:** the states are on the demo page and are walked at review. The legibility test still
fails when a rule it reads a colour from goes.

**ADR:** none. Local to this feature's tests.

## D13. FR-004's radius and border width are the frame's

**Chosen:** "every colour, radius, border width and field size from the theme" is read as the
frame of the control, of a tag and of the dropdown. The loading ring and the dropdown's spinner
are shapes with a stroke of their own. The test holds colour only.

**Why:** a ring's stroke is not a border the theme sizes. The maintainer approved both on screen.

**ADR:** none. A reading of one requirement, local to this feature's test.

## D14. A field with no help text is described by an element that is not there

**Chosen:** recorded, not fixed. django-tomselect writes `aria-describedby` naming a help-text
element whether or not the field has help text. The pack's own value wins on a field in error.
It joins the behaviours of D11 as an issue in this repository.

**Why:** the attribute is django-tomselect's to write.

**ADR:** none. The behaviour is django-tomselect's, and the issue is the record.

## D15. A floating label is left as it is, like attached text

**What was found:** the specification said a floating label stated for the form is passed over
for these controls. The pack floats a label on any select, and it cannot tell a django-tomselect
select from another without either importing django-tomselect or changing the rule for every
widget that names a template of its own.

**Chosen:** the edge case is brought into line with D4. A floating label is not supported for
these controls, the README says so, and the pack draws what it drew before.

**Why:** the maintainer ruled floating labels out of this feature. A pack-wide change to which
widgets float would reach projects that have nothing to do with django-tomselect.

**ADR:** none. The README's list of what is not supported is the record.
