# Implementation Plan: forms stay legible under every daisyUI theme

**Branch**: `012-legible-under-every-theme` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [research.md](research.md), [decisions.md](decisions.md)

## Summary

The test suite gains a check that draws every form state the pack has, reads from the markup
what daisyUI paints for each class, and calculates the contrast of every pairing under each of
the 35 themes in the pinned daisyUI version, from the colours daisyUI publishes for them.

Text the pack colours itself and that falls short is repaired by one class: help text, a single
checkbox's label, attached text, table headers, tabs and the error alert gain
`text-base-content`, and field errors, the required marker and a table row's errors lose
`text-error`. After that every piece of text the pack writes by its own choice passes under
every theme.

What is left is daisyUI's own drawing or the developer's stated choice: placeholders, the border
of an input, a colour chosen for a button. Those are published in a table in the README, and the
check holds that table in both directions. A demo page shows every form state with a theme
chooser.

Nothing under `mvp_forms/` changes except `class` attributes in templates. No dependency is
added and nothing under `.github/` changes.

## Technical Context

**Language/Version**: Python 3.12 and 3.13

**Primary Dependencies**: Django 5.2, 6.0, 6.1; django-crispy-forms. No new dependency.

**Storage**: none

**Testing**: pytest, pytest-django, BeautifulSoup, through the fixtures in `tests/conftest.py`

**Project Type**: Django package (a template pack)

**Constraints**: plain Django templates in the pack; daisyUI classes only, written out as
literals; no leading-underscore names; line length 88; no compatibility aliases; the check needs
no browser and no network.

**Scale/Scope**: seven pack templates change a class; one new helper package under `tests/`; one
data file; one demo page in two forms; one README section.

## Constitution Check

| Article | Holds because |
|---|---|
| I Testing | every task is test-first. Contrast is a computation from published values, which is what section 1 of the testing standard says gets a test. A class is asserted only where it is the daisyUI class this feature writes. No wording or appearance is asserted |
| II Simplicity | one reader, one table of what each class paints, the maths written once. No dependency, no browser, no new CI job |
| III Anti-abstraction | no base class and no registry. The reader is one class with one table |
| IV Integration-first | the check draws forms through `{{ form\|crispy }}` and `{% crispy form %}` and reads the markup a host project would get |
| V Security | nothing a person typed is read or written. The demo's chooser takes theme names from a fixed list |
| VI Documentation | README, CHANGELOG and CONTEXT change in the task that changes what they describe |
| VII Dependencies | none added (research R4) |
| VIII i18n | the pack adds no text |
| X Cohesion | colour maths on `Colour`; themes on `Themes`; reading on `Reader`; the published list on `KnownExceptions` |
| XI Compatibility | template paths, ids and structure are unchanged. Class names inside the markup are not part of the public API |
| XIII Plain templates | the templates that change stay plain; nothing under `mvp_forms/` imports django-mvp or uses Cotton |
| XIV Stock daisyUI | the one class added is in daisyUI's stylesheet. No control is repainted with a utility (research R6) |

No violation, so no complexity is tracked.

## Project Structure

```text
tests/data/daisyui-themes.css                 new: daisyUI's themes.css, verbatim
tests/data/daisyui-classes.txt                header gains the second download
tests/legibility/__init__.py                  new
tests/legibility/colours.py                   new: Colour
tests/legibility/themes.py                    new: Theme, Themes
tests/legibility/pairings.py                  new: Ink, Pairing, Measurement
tests/legibility/reader.py                    new: Reader, Uncovered
tests/legibility/catalogue.py                 new: Catalogue
tests/legibility/exceptions.py                new: KnownExceptions
tests/legibility/__main__.py                  new: the report
tests/test_legibility/                        new: tests of the helpers, one module each
tests/test_pack/test_legibility.py            new: the pack under every theme
tests/test_pack/test_independence.py          TestDistributedFiles gains one test
tests/test_demo.py                            the demo page
mvp_forms/templates/daisyui/field_body.html, required_marker.html, errors.html,
  errors_formset.html, table_inline_formset.html, layout/tab-pane.html,
  widgets/clearable_file_input.html, and any other template the check names
demo/forms.py, views.py, urls.py, menus.py
demo/templates/demo/themes.html, themes_standalone.html
README.md, CHANGELOG.md, CONTEXT.md, AGENTS.md
```

`tests/legibility/` is helper code for tests, like `tests/forms.py`. `tests/test_legibility/`
mirrors it module for module, as `tests/test_factories.py` mirrors `tests/factories.py` in the
testing standard.

## The helpers

### `Colour` (`tests/legibility/colours.py`)

A frozen dataclass: OKLab `lightness`, `a`, `b` and `alpha`.

- `Colour.parse(text)` reads `oklch(L% C H)` as daisyUI writes it, with or without the percent
  sign, and raises `ValueError` on anything else.
- `mixed(other, share)` is `color-mix(in oklab, self share, other)` for two opaque colours.
- `faded(share)` is the colour at that alpha, which is what mixing with `transparent` gives.
- `over(surface)` composites a see-through colour on an opaque one in sRGB and returns an opaque
  colour.
- `luminance()` converts to linear sRGB, clips each channel to 0..1 and applies WCAG's weights.
- `contrast(surface)` composites first when `self` is see-through and returns WCAG's ratio.

Tests hold it to the vectors in research R4 and to black on white being 21.

### `Theme`, `Themes` (`tests/legibility/themes.py`)

- `Theme`: `name`, `scheme` (`"light"` or `"dark"`) and `colours`, a dict from daisyUI's colour
  name without the `--color-` prefix to a `Colour`.
- `Themes.read(text)` parses a stylesheet in the shape of daisyUI's `themes.css` and returns its
  themes. A rule with no `[data-theme=...]` selector is not a theme.
- `Themes.shipped()` is `read` on `tests/data/daisyui-themes.css`, cached.
- `Themes.version(text)` reads the version from the banner.

Tests: 35 themes are read from the pinned file; each has a scheme and all twenty colours; the
version equals the one named in the header of `daisyui-classes.txt` (FR-015).

### `Ink`, `Pairing`, `Measurement` (`tests/legibility/pairings.py`)

An `Ink` is a colour stated in a theme's own names, so it means the same under every theme:

- `Ink(name)` is one of the theme's colours.
- `ink.faded(share)` is that ink at an alpha.
- `ink.mixed(other, share)` is the two mixed in OKLab.
- `ink.over(surface)` is a see-through ink already laid on a surface.
- `ink.resolve(theme)` gives the `Colour`.
- `ink.words` describes it for a reader of the README, built from the names and shares, such as
  `` `base-content` at 60% `` or `` 8% `error` in `base-100` ``.

Inks are frozen and compare by value.

A `Pairing` is `part`, `ink`, `surface` and `figure`. `part` is one of a closed set of words for
what a person has to make out: `"text"`, `"placeholder"`, `"border"`, `"mark"`, `"button text"`.
`figure` is 4.5 for text and 3.0 for a part of a control. `pairing.name` is built from the part
and the words of the ink and the surface. `pairing.ratio(theme)` and `pairing.meets(theme)` do
the calculation.

A `Measurement` is a `form_state` (the name of the drawn state), an `element` (the tag, id and
classes of the element it came from, for a failure message), a `pairing`, `held` (false for the
dimmed content of a disabled control, FR-004) and `own` (true when the ink is one the pack chose
itself and a class could change: text coloured by `label`, `text-error`, a table header, a tab,
or the pack's own alert; false for a control's drawing, a placeholder and anything the
developer's stated colour or variant decides).

### `Reader` (`tests/legibility/reader.py`)

`Reader(form_state, supplied=frozenset()).read(soup)` walks the markup top down and returns a
list of `Measurement`. It carries two values down the tree, the text ink and the surface, and
starts with `base-content` on `base-100`.

`Reader.paints` is the table in research R3 as data: every daisyUI class the pack writes, each
with what it does to the text ink, to the surface, and which control it is. A class in
`Reader.silent` paints nothing: the structural classes, the size modifiers and the layout
utilities. A class on an element that is in neither and not in `supplied` raises `Uncovered`,
which carries the class and the form state (FR-016).

- **Text.** An element with text of its own (a text node that is not whitespace) yields a text
  pairing of its ink on its surface. Text inside `select`, `textarea`, `option`, `script`,
  `style` and hidden inputs is not read that way.
- **Ink rules**, in order: `text-base-content` gives `base-content`; `text-error` gives `error`;
  `fieldset-legend` gives `base-content`; `label` gives the inherited ink at 60%; a `thead`
  inside a `table` gives `base-content` at 60%; an `alert` gives what research R3 says for its
  modifiers; otherwise the ink is inherited. A colour class beside a component class wins.
- **Surface rules**: `modal-box` gives `base-100`; `bg-base-200` gives `base-200`; an `alert`
  gives its fill; otherwise the surface is inherited.
- **Alerts.** The pack writes `alert` alone and `alert alert-error alert-soft`. An alert with any
  other colour modifier carries the developer's own class (spec, *Edge Cases*): its fill and
  text are not measured, and nothing inside it is.
- **Inputs** (`input`, `textarea`, `select`, `file-input`, on the element or on the `label` that
  wraps attached text): a `border` pairing of the border ink on the surface outside, unless the
  variant is ghost; a `text` pairing for the value on the fill; a `placeholder` pairing when the
  element has a placeholder; for a select, a `mark` pairing for its arrow; for a file input, a
  `button text` pairing for its button. A colour modifier, including the error modifier, sets
  the border ink.
- **Checkbox, radio, toggle**: measured both off and on, whatever the markup has, by the rows in
  research R3. Off yields a `border` pairing. On yields a `mark` pairing of the mark on its
  fill, and with a colour a `border` pairing of the fill on the surface.
- **Buttons** (`btn`, on a `button`, an `input` or an `a`): one `button text` pairing by colour
  and variant, as research R3 gives them.
- **Tabs**: a `text` pairing chosen and one not chosen, and a `mark` pairing for the bar.
- **Accordion**: a `mark` pairing for the arrow.
- **Disabled.** An element with `disabled` yields its pairings dimmed as research R3 says, with
  `held` false. Read-only changes nothing (ADR 0013).
- A hidden input yields nothing.

Tests draw small fragments and whole forms and assert the pairings read: by part, ink, surface,
`held` and `own`, never by a ratio. One test per rule above, and `Uncovered` for an unknown
class.

### `Catalogue` (`tests/legibility/catalogue.py`)

`Catalogue.states()` is every drawn state: each entry of `STATES` in
`tests/test_pack/test_independence.py` under its id, plus the sweep of FS-007's choices, which
draws `EveryInputForm` and a form with every kind of button once per colour, once per variant
and once per size. `Catalogue.measurements()` reads them all with `Reader` and caches the result.
It is the same under every theme, because the pack's output is.

### `KnownExceptions` (`tests/legibility/exceptions.py`)

- `KnownExceptions.found(measurements, themes)` gives the held measurements that fall short, as
  a mapping from pairing name to the set of theme names.
- `KnownExceptions.published(text)` parses the table between the two marker comments in the
  README and gives the same mapping. A row is the pairing's name, the form states it is seen in
  and the themes.
- `KnownExceptions.table(measurements, themes)` writes that table as markdown, sorted, for the
  report.
- `KnownExceptions.unlisted(found, published)` and `KnownExceptions.stale(found, published)` are
  the two differences.

### The report (`tests/legibility/__main__.py`)

`uv run python -m tests.legibility` prints the known-exceptions table as the README should hold
it, then every disabled control's dimmed pairings with their ratio under each theme (FR-004).
`uv run python -m tests.legibility --theme retro` prints every measurement under one theme.

## The check (`tests/test_pack/test_legibility.py`)

- `TestEveryTheme`, parametrised by theme: every held measurement meets its figure or is
  published for that theme. The failure lists each one as form state, theme, pairing, ratio and
  figure (FR-008, FR-012).
- `TestPublishedExceptions`: nothing is published that the check does not find (FR-009); the
  README's table equals `KnownExceptions.table(...)` row for row (FR-023); every published theme
  is a shipped one.
- `TestRepairs`: no measurement that is `own` falls short under any theme (SC-003, scenario 8).
- `TestCoverage`: every class in `Modifiers.tables`, `FieldInput.components` and
  `FieldInput.error_modifiers` is drawn by a state in the catalogue; every daisyUI class written
  as a literal in a pack template is in `Reader.paints` or `Reader.silent` (FR-016); every theme
  in the pinned file is checked (FR-005); every disabled control in the catalogue has its dimmed
  pairings measured under every theme and none of them is held (FR-004).
- `TestTheCheckCatches`: a fragment drawn with a class removed or changed falls short, and the
  failure names the form state, the theme and the pairing (US2 scenario 2); a list with an entry
  that now passes is reported stale (scenario 3); a theme added to a copy of the pinned text is
  read and checked (scenario 5); a class the reader does not know raises `Uncovered`
  (scenario 6).

`TestDistributedFiles` in `test_independence.py` gains one test: no pack template or module
names a theme, `data-theme` or `theme-controller` (FR-011).

FR-010 is held by the tests FS-001 to FS-008 already have, which this feature may change only by
the class names it repairs. FR-014 follows from the calculation having no input but the two
pinned files and the markup.

## The repairs

| Template | Change |
|---|---|
| `daisyui/field_body.html` | help text, the single checkbox's label and both attached-text spans: `label text-base-content`. The field error loses `text-error` and its `class` attribute |
| `daisyui/required_marker.html` | loses `text-error` and its `class` attribute |
| `daisyui/errors.html`, `daisyui/errors_formset.html` | `alert alert-error alert-soft text-base-content` |
| `daisyui/table_inline_formset.html` | `thead` gains `class="text-base-content"`. The row's errors lose `text-error` |
| `daisyui/layout/tab-pane.html` | the radio: `tab text-base-content` |
| `daisyui/widgets/clearable_file_input.html` | the clear checkbox's label: `label text-base-content` |
| any other template | wherever `TestRepairs` names a `label` or a `text-error` the list above missed |

Every change is to a `class` attribute. No element is added, removed or moved, and no id
changes (FR-010). Tests that assert one of these classes are updated to the new class and in no
other way.

An error is still told apart without its colour: the input carries its error modifier and
`aria-invalid`, the message sits under it and is tied to it, and the form-wide alert keeps its
tinted fill and border.

## The published list

The README gains a section, *Themes*, in the public surface. It says what is checked, the
standard, which themes, that a theme the host project writes is not measured, and that a
disabled control's own content is measured and not held. Then the table, between
`<!-- known-exceptions:start -->` and `<!-- known-exceptions:end -->`: one row per pairing that
falls short somewhere, with the form states it is seen in and the themes it falls short under.

## The demo project

One page, "Themes", in the shell (`themes`) and standalone (`themes-standalone`), built the way
the other pages are: a mixin that builds the forms, a view on `MVPTemplateView`, a view on
`TemplateView`, a Cotton template for the shell and a plain one for the standalone page, a route
each, one sidebar entry and one icon.

- The chooser is one radio per shipped theme with the class `theme-controller`, drawn from a
  list of names in `demo/forms.py`. Each page loads daisyUI's `themes.css` for the pinned version
  in its head. No script, no setting (research R2, R9).
- The page gathers the forms the demo already has for each form state, bound and unbound, and
  the colour, variant and size gallery of the choices page.

Tests in `tests/test_demo.py`: both pages answer; the shell page is in the sidebar; each page
has one chooser entry per theme in `Themes.shipped()`; the pairings `Reader` reads from each
page include every pairing in the catalogue (FR-020, FR-021); the standalone page loads neither
django-mvp's stylesheet nor a Cotton component.

## Story order

US1 → US2 → US3, sequential, in the feature worktree. US1 builds the helpers, makes the repairs
and publishes the list. US2 proves the check catches what it must and closes its coverage. US3
is the demo page and the rest of the documentation.

## Decision records

Written at convergence, with numbers read from `origin/main` at that moment.

- Legibility is calculated from the theme's published colours against WCAG 2.2 AA (D2, D5, D8,
  D13, D14, D17, D18).
- A shortfall in daisyUI's own drawing is published, never patched, and the README table is the
  list (D4, D16).
- Text the pack writes is drawn in the theme's content colour; a control is never repainted
  (D15).
