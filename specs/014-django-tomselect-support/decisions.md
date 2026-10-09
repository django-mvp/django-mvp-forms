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

**ADR:** yes. It changes what ADR 0003 and ADR 0034 rest on.

## D2. Legibility is checked under `light` and `dark` only

**Chosen:** the stylesheet's pairings are held to FS-012's contrast standard under daisyUI's
`light` and `dark` themes. The check over every shipped theme is not extended to it. This is the
maintainer's ruling.

**Why:** the stylesheet names no colour of its own (FR-004), so under any other theme it draws
what that theme's variables give a stock control. A shortfall there is the theme's, and ADR 0034
already says how one of those is handled.

**ADR:** yes, as an extension of ADR 0033.

## D3. Grouping is added here, though it is behaviour and not look

**What was ambiguous:** django-tomselect draws a group heading but has no setting that tells Tom
Select which group an option fetched from the server belongs to. Supplying one goes beyond
drawing.

**Chosen:** this package supplies it, as part of its support for django-tomselect. The maintainer
asked for grouping by name and confirmed that it must work without a template of the developer's.

**Why:** every project that needs groups carries the same small template today. The way it is
supplied is for the plan. Whatever the plan chooses must touch django-tomselect only through
places it offers for the purpose, and is retired if django-tomselect gains a setting of its own.

**ADR:** yes.

## D4. Attached text, joined buttons and joined groups are left as they are

**Chosen:** this feature does not say what the pack draws when a django-tomselect control is put
inside a layout object that attaches text or joins fields. The README says these are not
supported.

**Why:** the maintainer ruled them out of this feature. Fixing a behaviour for them now would be
specifying something nobody has asked for.

**ADR:** none.

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
