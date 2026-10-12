# Decisions: Tom Select widgets for choice fields

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer confirmed the reading of the feature on 2026-10-11. Everything below that he did not
rule on directly is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. Two widgets, and no field

**Chosen:** `TomSelect` and `TomSelectMultiple`, widgets a developer names on any choice field.

**Why:** the feature changes how a choice is made in the browser and nothing about what a valid
choice is. Django's own choice fields already hold that rule, so a field of the package's would
duplicate them. Two widgets follow Django's `Select` and `SelectMultiple`, whose places they take.

**Confirmed by the maintainer.**

**ADR:** none — two widgets beside Django's own is the ordinary shape, nobody would ask why

## D2. The host project loads Tom Select

**Chosen:** the package ships the widgets and one script. Tom Select comes from the page.

**Why:** the mask widgets already work this way with IMask (ADR 0045), and a package that
distributed Tom Select would have to follow its releases. django-tomselect's script puts Tom
Select on the page under the name Tom Select publishes, so a project that uses both loads it
once.

**Confirmed by the maintainer** as to who loads it. That django-tomselect's copy can serve both
was checked against django-tomselect 2026.6.2 and is to be proved again at planning. If a later
release stops exposing it, such a page loads Tom Select a second time and FR-017's second sentence
is withdrawn.

**ADR:** docs/adr/0054-the-tom-select-widgets-bring-one-script-that-starts-controls.md

## D3. Four settings from Python

**Chosen:** a placeholder, a clear button, a remove button on each chosen value, and the largest
number of values. Everything else is reached through the event.

**Why:** these are plain data and are what a short list needs. Carrying every Tom Select setting
would mean following its API, and many settings are functions that cannot be written in Python.

**Confirmed by the maintainer.**

**ADR:** docs/adr/0054-the-tom-select-widgets-bring-one-script-that-starts-controls.md

## D4. One stylesheet for Tom Select controls from either source

**Chosen:** these widgets are drawn by `mvp_forms/tomselect.css`. The package ships no second
stylesheet.

**Why:** the stylesheet's rules are written against Tom Select's own parts. A second file would
repeat them and the two would drift, and a page using both kinds of control would load both. ADR
0042 says each supported package has a stylesheet of its own and that this one applies only to
django-tomselect's controls. Its purpose, that a project pays only for what it uses, still holds:
a project using either kind of control loads one file. A new record supersedes it to say so.

**Confirmed by the maintainer.**

**ADR:** docs/adr/0055-one-stylesheet-draws-tom-select-controls-from-either-source.md

## D5. The script starts controls added later

**Chosen:** a select added to the page after it has loaded gets a control with no script from the
developer, including a formset row copied from the empty form.

**Why:** the mask script already does this for masked inputs (ADR 0045), and a developer who has
both kinds of widget in one formset should not have to start one of them by hand. The reading put
to the maintainer said the script would give django-mvp a way to start a control. Starting it
without being asked covers that case and every other script that adds a row.

**Self-resolved.** It does more than the reading said and asks less of django-mvp.

**ADR:** docs/adr/0054-the-tom-select-widgets-bring-one-script-that-starts-controls.md

## D6. No way to mark an option unavailable from Python

**Chosen:** the control respects the `disabled` attribute on an option and the widgets add no
argument for writing it.

**Why:** Django's choice fields have no such argument either. A developer writes the attribute
from a subclass, as for a stock select. Inventing an argument here would give these two widgets a
feature Django's own select widgets lack.

**Self-resolved.** The reading suggested unavailable options could show greyed out, which this
delivers.

**ADR:** none — the widgets add nothing here, so there is nothing to explain later

## D7. No sketch

**Chosen:** the feature goes to planning without a prototype.

**Why:** the control's look was drawn and approved for django-tomselect in FS-014, and FR-013
requires these controls to match it. The demo page is new but shows nothing that has not been
seen.

**Confirmed by the maintainer.**

**ADR:** none — local to this feature's process

## D8. Design review, before any code

One reviewer read the plan through three lenses. Verdict: changes requested. Every finding was
applied to `plan.md`, `tasks.md` and `research.md`.

- **ARCH-001 (high).** The plan amended Article XIV inside this pull request. The constitution
  says a rule is changed in a pull request of its own, before the work it affects. The amendment
  was taken out of the plan and opened as its own pull request, which merges first.
- **SPEC-001 (medium).** The module's text check refuses a lazy translation. The placeholder
  accepts one and it is turned into text when the widget is drawn.
- **SPEC-002 (medium).** Tom Select does not carry `aria-describedby` to the input that takes
  focus. The script copies it.
- **SEC-001 (low).** The script passes Tom Select only the three settings it knows from the
  attribute.
- **ARCH-002 (low).** The browser tests for groups and unavailable options were cut to two.
- **SPEC-003, SPEC-004 (low).** A missing glossary term and a clearer README sentence about the
  empty form.

**ADR:** none — a record of a review, nothing downstream inherits it.
