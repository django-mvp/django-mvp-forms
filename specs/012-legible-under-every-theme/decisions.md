# Decisions: Forms stay legible under every daisyUI theme

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below was
made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as follows. Every form state the merged features draw is measured
for contrast under every theme built into the pinned daisyUI version. A state that falls short is
repaired by changing which stock daisyUI class the pack writes, where one passes. Where none does,
the shortfall is published as a known exception. The check stays in the test suite. A demo page
shows every state under a theme chosen on the page, and the README says what is promised. The host
project does nothing per theme. The feature serves G5 and is the whole of R8.

**Why:** the issue is one paragraph and the roadmap item is one sentence, and neither conflicts
with this reading. Each gap it fills is its own decision below.

**ADR:** none. This is the record of how the specification was written.

## D2. The standard is WCAG 2.2 level AA

**Chosen:** "fails contrast" means falling below the minimum contrast WCAG 2.2 sets at level AA,
for text, for large text and for the parts of a control that identify it and show its state
(FR-003).

**Rejected:**

- Level AAA. It is stricter than most projects are held to, and several daisyUI themes are
  designed below it on purpose. The list of known exceptions would swamp the README.
- A newer perceptual measure such as APCA. It is not a published standard yet, and a host project
  that has to show conformance is asked for WCAG.
- No figure, and a person's judgement. It cannot be tested, and it cannot be repeated when daisyUI
  changes a theme.

**Why defensible:** it is the standard a host project is most likely to be held to itself, and it
is a calculation, which the constitution's test rules need.

**ADR:** expected. It is the bar every later input and layout object is held to, and someone will
ask why this level.

## D3. The themes are those built into the daisyUI version the suite pins

**Chosen:** the check covers every theme in the daisyUI version the list of classes in
`tests/data/` is taken from, and is refreshed with it (FR-005, FR-015).

**Rejected:**

- A hand-written list of theme names. It would miss a theme daisyUI adds.
- Every daisyUI version the package supports. Which versions those are is #89, and that feature
  can widen the check when it lands.
- Custom themes. The pack cannot know them.

**ADR:** none. It follows the pin the suite already has.

## D4. A shortfall in daisyUI's own theme is published, never patched

**Chosen:** where no stock daisyUI class brings a pairing up to the standard under a theme, the
pack records a known exception and adds nothing of its own (FR-007). The check holds the list in
both directions: an unlisted shortfall fails, and so does a listed one that now passes (FR-008,
FR-009). The README carries the same list (FR-022, FR-023).

**Rejected:**

- Shipping a small stylesheet or inline styles to correct the theme. Article XIV and ADR 0003 say
  the pack ships no stylesheet and defines no class, and a host project on the CDN install would
  have to load something extra.
- Tailwind colour utilities chosen per theme. That is per-theme work inside the pack, it names
  actual colours, which `CONTEXT.md` says the pack never does, and it would drift from the host
  project's theme.
- Failing the feature until every theme passes. It would make the pack's delivery depend on
  changes in another project.
- Leaving shortfalls unrecorded. A developer choosing a theme should be able to find out.

**Why defensible:** it is the only reading that keeps the class rule and still tells the truth.
The issue says anything that fails "should be fixed"; the pack fixes what is in its power, and
names the rest precisely enough to be reported to daisyUI.

**Risk:** the list may be long. Error text in a theme's error colour and daisyUI's muted label
text are the likely places. If it is, the maintainer is told at the build with the numbers, and
the choice between living with it and loosening Article XIV is his.

**ADR:** expected. It settles what the pack does when daisyUI itself falls short, and it will come
up again with every new component.

## D5. A disabled control's own content is measured and not held to the figure

**Chosen:** the label, help text and surroundings of a disabled field meet the standard. The
dimmed content of the control is measured and reported for every theme and does not fail the
check (FR-004).

**Rejected:**

- Holding it to the standard. WCAG exempts disabled controls, daisyUI dims them from the
  `disabled` attribute (ADR 0013) and the pack adds no class for the state, so every theme would
  produce a known exception and the list would say nothing.
- Leaving it out. The issue names disabled fields, and a theme where a disabled value all but
  vanishes is worth seeing in a report.

**ADR:** none. It is a detail of the standard in D2 and can be noted there.

## D6. Pairings are measured on the page background and on surfaces the pack draws

**Chosen:** the surface behind a pairing is the theme's page background, or whatever the pack
itself draws there, such as an accordion group, a modal's box, an alert or a table (FR-002).

**Rejected:** measuring against every surface colour a theme has. The host project decides where a
form sits, and a form on a coloured card is the host project's to check.

**ADR:** none.

## D7. Colour and variant choices are form states

**Chosen:** every colour, variant and size FS-007 offers, on every input and button that takes
it, and every drawing from FS-008, is checked (FR-001).

**Why:** FS-007's specification says in its assumptions that it does not check any combination for
contrast and that this roadmap item does. Shortfalls here are almost certainly daisyUI's own and
fall under D4.

**ADR:** none.

## D8. The check is a calculation inside the existing test command

**Chosen:** whether a pairing passes is calculated from the theme's published colours, runs under
the documented test command, gives the same result every run, and needs nothing under `.github/`
(FR-012 to FR-014). How the calculation is done is left to planning.

**Rejected:**

- Judging pages by eye, or from pictures of them. It is not repeatable and proves nothing.
- A separate continuous-integration job. Nothing under `.github/` may change in this work. If
  planning finds the check cannot run inside the existing jobs, everything else is built and the
  workflow part is filed as a separate request for the maintainer.

**ADR:** expected, with D2, once planning has settled how the colours are read.

## D9. New inputs join the check when they are built

**Chosen:** the suite fails when a pack template draws something the check does not cover
(FR-016). Rating, range, floating labels and joined inputs (#86, #87) are specified alongside this
feature and do not depend on it, so whichever is built second adds those states.

**ADR:** none.

## D10. Focus, hover and pressed are not form states

**Chosen:** only states a form can be in at rest are checked. Focus rings, hover and the pressed
moment are daisyUI's, are the same for every component, and the pack writes nothing for them.

**Revisit if:** a host project reports a focus ring it cannot see under a shipped theme.

**ADR:** none.

## D11. Open questions on the tracker are measured as built

**Chosen:** #46, #70, #15 and #77 are not settled here. Each is measured as the pack draws it
today, and whatever they decide comes under the check through D9. #16 is not settled either: a fix
uses only what ADR 0003 already allows.

**ADR:** none.

## D12. No sketch before the build

**Chosen:** the feature goes to the build without a prototype. The demo page gathers forms the
demo project already shows and adds a theme chooser, and the README section is text.

**ADR:** none.

## D13. The contrast maths is written in the test suite

**Chosen:** the conversion from daisyUI's `oklch()` values to a WCAG contrast ratio is about
sixty lines under `tests/legibility/`, held by fixed vectors.

**Rejected:** `coloraide` as a development dependency. It does the same work and was used to
check the numbers. Article VII says development tooling comes from the shared bundle and is not
pinned package by package, and the change would sit in `pyproject.toml` and `uv.lock`, which four
sibling branches are also changing.

**Revisit if:** the shared bundle gains a colour library.

**ADR:** pending. Judged at convergence with D2 and D8.

## D14. The check reads the drawn markup through a table of what each class paints

**Chosen:** a reader walks each drawn form with the text colour and the surface inherited down
the tree, and one table says what each daisyUI class the pack writes does to them. A class with
no row is an error.

**Rejected:**

- A hand-written list of pairings. It would measure the list and not the pack, and a new template
  would never reach it.
- A headless browser reading computed styles. It needs a browser in continuous integration, which
  means a workflow change (FR-013), and D8 already settles on a calculation.
- Evaluating daisyUI's stylesheet itself. That is a CSS engine.

**Risk:** the table is a reading of daisyUI's stylesheet for one version. It was checked against
a browser for 5.7.47. When the pinned version moves, the rows are re-read with it.

**ADR:** pending. Judged at convergence with D2 and D8.

## D15. A repair changes the colour of text the pack writes, and never repaints a control

**Chosen:** a pairing is repaired when a stock daisyUI class brings it to the standard under
every shipped theme, which is the test acceptance scenario 8 of the first story sets. For text
that class is `text-base-content`, or dropping `text-error`. A control's border, fill and mark
are left as daisyUI's component and its modifiers draw them.

**Rejected:**

- `border-base-content` and the like on an input. It is in the stylesheet and it would pass, but
  it paints over daisyUI's component with a utility. Article XIV says the pack uses the component
  and does not assemble a look-alike, and ADR 0003 gives the reason: the pack should look like
  the rest of a daisyUI site.
- A colour modifier written by default, such as `input-neutral`. No colour passes under every
  theme (each fails under 11 to 20), and a colour is a choice FS-007 gives to the developer.
- Keeping error text in the theme's error colour. It falls short under 21 themes, and plain
  `base-content` passes under all 35. The error is still marked by the input's error modifier,
  by `aria-invalid`, by where the message sits and by the alert's tinted fill.
- A muted grade for help text. 90% passes everywhere and 80% does not, so nothing worth calling
  muted is left.

**Spec:** FR-006 said a class is written when it helps one theme and harms none. Read against a
colour modifier that would have the pack state a colour for the developer. FR-006 now carries
scenario 8's test, "under every shipped theme", and says a colour or variant modifier is the
developer's to state.

**ADR:** pending. Judged at convergence.

## D16. The README table is the list of known exceptions

**Chosen:** a known exception is a pairing and a theme. A pairing is named by what is drawn, in
which of the theme's colours and on which surface, so form states that draw the same thing share
one row. The check parses the README's table and compares it with what it measured, both ways.

**Rejected:** a list in the test suite and a copy in the README. Two lists need a test that they
agree, and the README copy is the one that goes stale.

**ADR:** pending. Judged at convergence with D4.

## D17. Nothing the pack draws is large text

**Chosen:** WCAG's lower figure for large text applies to text of 24px, or 18.66px when bold. The
largest text the pack writes is a `btn-xl` at 22px and weight 600, which is neither. Every piece
of text is held to 4.5.

**Revisit if:** a later size or component draws text at 24px or more.

**ADR:** none. It is a reading of the standard in D2 for the sizes daisyUI has today.

## D18. Which parts of a control are held to the figure

**Chosen:** the border of an input, a select, a textarea and a file input; the border of a
checkbox and a radio that is off; a toggle that is off; the mark and the fill of each when on;
the arrow of a select and of an accordion group; the bar under the chosen tab. Each is what tells
a person the control is there or what state it is in. A button is identified by its text, so its
text is held and its outline is not, which is WCAG's own reading of a button.

**ADR:** pending. Judged at convergence with D2.

## D19. An alert whose colour the developer chose is not measured

**Chosen:** the pack writes `alert` alone and `alert alert-error alert-soft`. An `Alert` layout
object given another colour class carries the developer's class, and the spec's edge cases leave
its fill and its text to the developer. The dismiss button inside it is the pack's, so its text
is measured on the alert's fill.

**ADR:** none. It follows the spec's edge case.

## D20. The pre-existing tests change only by the class repaired

**Chosen:** a test from FS-001 to FS-008 that asserts `text-error` or a bare `label` on a
repaired element has that class name updated. Nothing else in it changes. The markup of every
drawn state with its `class` attributes stripped is compared before and after, and is identical.

**ADR:** none. It is how this feature shows FR-010.

## D21. The design review's findings

One review of the plan before any code: approve, nothing critical or high. Four medium findings
and six low ones, all applied to the plan and the tasks.

- The scan of template classes now asks that each is drawn by a state, and not only known to the
  reader. What it still cannot catch is a new template that writes only classes another state
  already draws.
- The catalogue draws the disabled and read-only forms, a disabled file input, a disabled toggle
  and switch, a toggle in the sweep, and every button colour with every variant.
- The dismiss button the pack writes inside an alert is measured even when the developer
  coloured the alert.
- Attached text is read on its wrapper's fill. An input drawn with no daisyUI class yields its
  text and no border. A disabled button has a row.
- The published table is compared by pairing and themes only, and names what a pairing is seen
  on by the kind of element.
- The report loses its per-theme listing, and two assertions that could not fail are dropped.
- The demo page's test reads the element holding the forms. The radios override the shell's own
  chooser on that page.

**ADR:** none. It is the record of a review.

## D22. A see-through colour is composited before it is clipped to the gamut

**Decision:** `Colour.over` encodes the front colour to sRGB without clipping it, composites
on the surface, and leaves the clipping to `luminance` and `srgb`.

**Why:** daisyUI's `base-content` under the `dark` theme is outside the sRGB gamut in blue
(1.05 once encoded). Clipping first gives 170 for it at 60% on `base-100`; compositing first
gives 178, which is what research R4's vector and the browser give.

**Revisit if:** the vectors in research R4 are regenerated from a different engine.

## D23. A radio's ring and dot are the text ink, and only they are `own`

**Decision:** a radio's ring and dot are read in the inherited text ink, and are `own` when
that ink was chosen by the pack. Its faded border (20% of the ink) is not `own`.

**Why:** daisyUI draws a radio in the text colour it inherits, so a `label` around it at 60%
reaches the ring, and `text-base-content` on the label repairs it. The border at 20% falls
short whatever class the label carries, so it is a known exception and a repair cannot be asked
of it.

**Revisit if:** the pack draws a radio outside a label.

## D24. A measurement names its element by an `Element`, not a string

**Decision:** `Measurement.element` is an `Element` (tag, id, classes, kind) whose `str` is a
selector for a failure message, and whose `kind` is what the README's *Seen on* column lists.

**Why:** the table must say what a pairing is seen on by the kind of element, such as `input`
or `btn`, and never by a drawn state, and the reader is the one that knows the kind.

**Revisit if:** the table stops naming what a pairing is seen on.

## D25. The failure text is built by `KnownExceptions.failures`

**Decision:** the lines that `TestEveryTheme` shows when a held pairing falls short (form
state, theme, pairing, ratio and figure) are built by `KnownExceptions.failures(measurements,
theme, published)`. `TestEveryTheme` asserts that it is empty and `TestTheCheckCatches` asserts
that it names the state, the theme and the pairing of a help text that lost
`text-base-content`.

**Why:** a test that built its own copy of the message would pass while the real one lost a
field. The one method is the message a contributor reads.

**Revisit if:** the failure is reported another way than text.

## D26. The Themes page draws its forms apart, and four demo forms exist for it

**Decision:** every form on the Themes page is drawn with no form element and no token, so
nothing on it posts. `ReadOnlyKindsForm`, `AlertColoursForm`, `LockedKindsForm` and
`UneditableChoicesForm` are added to `demo/forms.py`; the forms the demo already had are not
changed.

**Why:** the catalogue holds pairings that no earlier demo form draws: a disabled input in each
variant, an invalid uneditable checkbox or radio, and an alert in each colour. The page test
reads the page against the catalogue and names what is missing, so these are what it took to
empty that list.

**Revisit if:** the catalogue gains a state the page does not draw; the test says which.
