# Research: forms stay legible under every daisyUI theme

Done on 2026-10-03 against `origin/main` at `8622e54`, after FS-001 to FS-008 merged and v0.1.0
was released. FS-009, FS-010, FS-011 and FS-013 are being built at the same time and are not on
main.

## Planning notes, answered

Each of the maintainer's notes in `planning-notes.md`, under its own words.

- **"Every input, button and component is built from daisyUI's component classes and modifiers
  ... The package ships no stylesheet and defines no classes."** Adopted. The feature adds one
  class to pack templates, `text-base-content`, which is in daisyUI's CDN stylesheet
  (`tests/data/daisyui-classes.txt:2717`), and removes `text-error` from three places. It adds no
  stylesheet, no class of the pack's own and no inline style (R6).
- **"Pack templates are plain Django templates."** Adopted. The templates that change stay plain,
  and each change is to a `class` attribute only.
- **"This package never depends on django-mvp at runtime and never imports from it."** Adopted.
  Nothing under `mvp_forms/` gains an import. The check lives under `tests/`.
- **"Size, colour and variant are stated through `FormChoices` ... A new kind of input takes them
  by adding its rows to `Modifiers`."** Adopted, and relied on: the check draws every row of
  `Modifiers.tables` and fails when a row names a class it cannot read (R5).
- **"There is no support for carrying layouts over from other packs."** Adopted. Nothing here
  reads a class written for another pack.
- **"A feature adds its own demo page where it changes what a person sees, and its entry in the
  README's public surface."** Adopted. One page in two forms, in the shell and standalone, and a
  README section on themes.
- **"Nothing under `.github/` is changed by this work."** Adopted, and nothing needs to be: the
  check is plain pytest and runs in the jobs the repository already has (R8).
- **"A decision that is durable, architectural and non-obvious is recorded under `docs/adr/`."**
  Adopted. Three are expected (plan, *Decision records*).

## R1. What the delivered features left in place

- Every state the pack draws is already gathered in one list:
  `tests/test_pack/test_independence.py:389`, `STATES`, 80 entries, each a template source, a
  form builder and the classes the form itself supplied. `TestEmittedClasses` draws each one and
  holds every class written to `tests/data/daisyui-classes.txt`.
- The class list is every class selector in daisyUI 5.7.47's CDN stylesheet
  (`tests/data/daisyui-classes.txt:1-3`). The header names the version and how to refresh it.
- Colour, variant and size classes come from one literal table, `Modifiers.tables`
  (`mvp_forms/choices.py:70-241`): 113 classes.
- Across `STATES` the pack writes 69 daisyUI classes. The ones that paint something are `input`,
  `textarea`, `select`, `file-input`, `checkbox`, `radio`, `toggle`, `btn`, `label`,
  `fieldset-legend`, `text-error`, `alert`, `tab`, `table`, `collapse-arrow`, `modal-box`,
  `bg-base-200`, `link`, `divider`, and their modifiers.
- Text the pack colours itself today: help text, the label of a single checkbox, the label of
  the clear checkbox and attached text are `label` (`daisyui/field_body.html`,
  `daisyui/widgets/clearable_file_input.html`); field errors, the required marker and a table
  row's errors are `text-error` (`daisyui/field_body.html`, `daisyui/required_marker.html`,
  `daisyui/table_inline_formset.html`); form-wide and formset-wide errors are
  `alert alert-error alert-soft` (`daisyui/errors.html`, `daisyui/errors_formset.html`).

## R2. The themes and where their colours are published

daisyUI 5.7.47 ships 35 themes. `daisyui.css` carries only `light` and `dark`; all 35 are in
`https://cdn.jsdelivr.net/npm/daisyui@5.7.47/themes.css` (38 kB), one rule per theme:

```css
:root:has(input.theme-controller[value=retro]:checked),[data-theme=retro]{color-scheme:light;
--color-base-100:oklch(91.637% .034 90.515);--color-base-200:...;--color-base-content:...;
--color-primary:...;--color-primary-content:...; ... --color-error-content:...;--radius-...}
```

Each theme states `color-scheme` (22 light, 13 dark) and twenty colours: `base-100`, `base-200`,
`base-300`, `base-content`, and a colour and its `-content` for `neutral`, `primary`,
`secondary`, `accent`, `info`, `success`, `warning` and `error`. Every colour is written as
`oklch(L% C H)`.

**Decision**: the file is kept verbatim as `tests/data/daisyui-themes.css`. Its first line is
daisyUI's own banner, `/*! 🌼 daisyUI 5.7.47 - MIT License */`, so a test can hold its version to
the one in the header of `daisyui-classes.txt` (FR-015). The refresh note in that header gains the
second download.

The same rule gives the demo its theme chooser with no script: a radio input with the class
`theme-controller` and a theme's name as its value puts the whole page under that theme while it
is checked. Its selector is more specific than `[data-theme=...]`, so it wins over a theme the
shell set on the root element.

## R3. How daisyUI 5.7.47 colours each thing the pack writes

Read from `https://cdn.jsdelivr.net/npm/daisyui@5.7.47/daisyui.css` with nested rules flattened.
`content` below is `base-content`. "N% of X" is `color-mix(in oklab, X N%, transparent)`.
"Surface" is whatever is behind the element.

| Class | What it paints |
|---|---|
| `fieldset-legend` | text `content` |
| `label` | text 60% of the inherited text colour |
| `text-error` | text `error` |
| `text-base-content` | text `content`. It is in the stylesheet's utilities layer and wins over every component rule below |
| `link` | text inherited |
| `input`, `textarea`, `select` | fill `base-100`; border 20% of `content`; text inherited; placeholder 50% of the text colour. A `select` draws its arrow in the text colour |
| `file-input` | fill `base-100`; border 20% of `content`; its button has fill `base-200` and text `content` |
| `{input,textarea,select,file-input}-{colour}` | border in that colour. A `file-input`'s button takes the colour as its fill and the colour's `-content` as its text |
| `{input,textarea,select,file-input}-ghost` | no fill and no border |
| those four, `disabled` | fill and border `base-200`; text 40% of `content` (20% on a file input); placeholder 20% |
| `checkbox` | border 20% of `content`; ticked: no fill, mark `content` |
| `checkbox-{colour}` | border in the colour; ticked: fill in the colour, mark in its `-content` |
| `radio` | border 20% of the inherited text colour; chosen: fill `base-100`, ring and dot in the text colour |
| `radio-{colour}` | border, ring and dot in the colour |
| `toggle` | off: border and knob 50% of `content`, no fill; on: fill `base-100`, border and knob `content` |
| `toggle-{colour}` | on: border and knob in the colour. Off is unchanged |
| `checkbox`, `radio` disabled | the whole control at 20% opacity; a `toggle` at 30% |
| `btn` | fill `base-200`; text `content` |
| `btn-{colour}` | fill in the colour; text in its `-content` |
| `btn-outline`, `btn-dash`, `btn-ghost` | no fill; text in the colour, or `content` when none is stated |
| `btn-soft` | text in the colour (or `content`); fill is 8% of that mixed into `base-100`. With `btn-neutral` the fill is `color-mix(in oklab, neutral 8%, neutral-content 80%)`, which is 88% opaque |
| `btn-link` | no fill; text in the colour, or `primary` when none is stated |
| `alert` | fill `base-200`; text `content` |
| `alert-soft` with `alert-error` | text `error`; fill is 8% of `error` mixed into `base-100` |
| `alert-{colour}` alone | fill in the colour; text in its `-content` |
| `tab` | text inherited when chosen, 50% of `content` when not; `tabs-border` draws a bar under the chosen tab in its text colour |
| `table` | header text 60% of `content`; cells inherited |
| `collapse-arrow` | an arrow in the inherited text colour |
| `bg-base-200` | fill `base-200` |
| `modal-box` | fill `base-100` |
| `divider` | a line, 10% of `content`. Decoration: nothing has to be made out |
| `fieldset`, `join`, `join-item`, `tabs`, `tabs-border`, `tab-content`, `collapse`, `collapse-title`, `collapse-content`, `modal`, `modal-action`, every size modifier | no colour |

No size the pack writes makes text large in WCAG's sense (24px, or 18.66px bold). The largest is
`btn-xl` at 22px and weight 600. So the figure for large text applies to nothing the pack draws
today (FR-003 is met by there being none).

**Checked in a browser.** A page on the CDN install with one of each element above was opened
and its computed colours read under `light`, `retro`, `dark` and `cupcake`. They match the table,
and the colours calculated in R4 match what the browser paints to within one step in 255. The
same page confirmed that `text-base-content` beside `label`, on a `tab`, on a `thead` and on an
`alert-soft` gives `content` in every case.

## R4. The calculation

WCAG's contrast ratio is `(L1 + 0.05) / (L2 + 0.05)` on relative luminance in sRGB. From a
theme's `oklch()` values that takes: OKLCH to OKLab, mixing in OKLab (with `transparent` this
only sets the alpha), compositing a see-through colour over its surface in sRGB, OKLab to linear
sRGB, clipping to the sRGB gamut as browsers do, and the luminance weights. About sixty lines.

**Decision**: the maths is written in the test suite. `coloraide` does all of it and was used to
check the numbers, but adding it would be a development dependency pinned in this package alone,
which Article VII rules out (development tooling comes from the shared bundle), and it would put
`pyproject.toml` and `uv.lock` in the path of four sibling branches. Sixty lines of published
formulas, held by fixed vectors, cost less.

Reference vectors, from `coloraide` and confirmed in the browser (sRGB 0 to 255, and ratios on
`base-100`):

| Theme | `base-100` | `content` | 60% content | 20% content | `error` | content | 60% | error | 20% |
|---|---|---|---|---|---|---|---|---|---|
| light | 255,255,255 | 24,24,27 | 116,116,118 | 209,209,209 | 255,98,125 | 17.73 | 4.64 | 2.87 | 1.53 |
| retro | 236,227,202 | 121,50,5 | 167,121,84 | 213,192,163 | 255,98,102 | 7.22 | 2.99 | 2.28 | 1.38 |
| dark | 29,35,42 | 236,249,255 | 153,163,178 | 70,78,87 | 255,98,125 | 14.75 | 6.23 | 5.52 | 1.87 |
| cupcake | 250,247,245 | 41,19,52 | 125,110,129 | 208,201,206 | 254,28,85 | 15.91 | 4.45 | 3.57 | 1.52 |

It is deterministic: no clock, no network, no randomness, and arithmetic that gives the same
result on every supported Python (FR-014).

## R5. Reading what the pack drew

The check has to follow the markup, or it would measure a list somebody wrote and not the pack.
So it reads each drawn form the way a browser's cascade would, with two inherited values: the
text colour and the surface. Each element's classes change one or both by the table in R3. An
element holding text of its own yields a text pairing. A control yields the pairings for its
boundary and for each state a person can put it in: a checkbox is measured both ticked and not,
a tab both chosen and not, whatever the markup happened to have.

A daisyUI class the reader has no entry for is an error naming the class. That is FR-016: a new
kind of input, or a new class in a template, fails the suite until the reader is taught what it
paints. A static scan of the class literals in the pack's templates and tables holds the same
line for a template no drawn state reaches.

`STATES` gives the form states of FS-001 to FS-006 and FS-008. FS-007's colours and variants are
swept: one drawing of `EveryInputForm` and the buttons per colour, per variant and per size, so
every row of `Modifiers.tables` is drawn at least once.

## R6. What falls short, and what repairs it

The prototype measured 94 pairings under each theme: 1,298 shortfalls out of 3,290.

| What | Shortfalls | Repair |
|---|---|---|
| Text `content` on `base-100` or `base-200` | none | |
| `label` text (60%): help text, a single checkbox's label, attached text | 15 themes on the page, 18 in an accordion group | `text-base-content` beside `label` passes under all 35 |
| Table header (60%) | 15 | `text-base-content` on the `thead` |
| A tab not chosen (50%) | 33 | `text-base-content` on the tab |
| `text-error` on the page: field errors, required marker, a table row's errors | 21 | drop `text-error`; the text is then `content` |
| Text in the soft error alert | 23 | `text-base-content` on the alert. `content` on the tinted fill passes under all 35 |
| Placeholder (50%) | 33 | none. No class reaches a placeholder |
| Border of an input, select, textarea, file input, checkbox or radio (20%) | 35 | none (below) |
| A toggle turned off (50%) | 9 | none |
| Border of an invalid input (`error`) | 13 | none. It is the same class the developer's `error` colour writes |
| A chosen colour as a border, ring, knob or fill, per colour | 11 to 20 | none: the class is the choice |
| A chosen colour as button text (outline, dash, ghost, link, soft), per colour | 16 to 23 | none |
| Button text on a chosen colour's fill, per colour | 2 to 10 | none |

90% of `content` passes everywhere and 80% does not (two themes fall short in an accordion
group), so there is no muted grade worth keeping: the repair is `content` in full.

**No modifier repairs a control's border.** Each colour modifier fails under 11 to 20 themes.
`border-base-content` is in the stylesheet and would pass, but it repaints daisyUI's own
component with a utility, which Article XIV rules out ("uses it rather than assembling a
look-alike from utilities"), and it would make the pack's inputs look unlike every other input on
a daisyUI site. A colour modifier is also a choice FS-007 gives to the developer, and the pack
states none of its own (ADR 0021).

## R7. The published list

After the repairs about 40 pairings still fall short somewhere, around 600 pairing-and-theme
combinations. A pairing is named by what is drawn, in which colour and on which surface, so many
form states share one row: a `primary` border is the same pairing on an input, a select and a
checkbox. The README carries one table row per pairing with the themes it falls short under.

**Decision**: the README table is the list. The check parses it and compares it with what it
measured, both ways, so there is no second copy to drift (FR-023). A command prints the table as
the check would write it, for pasting, so a person adds an exception and the suite never does.

## R8. Continuous integration

The check is ordinary pytest under `tests/`, needs no browser and no network, and adds no
dependency. It runs in the existing test job across the Python and Django matrix. Nothing under
`.github/` changes (FR-013).

## R9. The demo's theme chooser

`demo/` runs on django-mvp's shell, whose stylesheet is prebuilt. The page loads
`daisyui@5.7.47/themes.css` from the CDN in its own head so all 35 themes exist on it, and draws
one `theme-controller` radio per theme. The standalone page does the same on daisyUI's CDN
install. Both need no script and edit no setting (FR-020, FR-021).
