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
