# Decisions: Characters left under a text field

Rationale too long to inline in `spec.md`, and every place the issue was silent and a reading was
chosen. None of these was ruled on by the maintainer. Each is his to overturn when he reviews the
specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. It is a feature, with two stories

**Chosen:** a developer gains a way to show the characters left under a field, and a person
filling in a form gains a line that tells them. One story for each, since what a developer
configures and what a person then does are kept apart.

**Why:** work is a feature when someone gains a new way to do something. Both
do. Turning the line on for a Tom Select control, stating the number from which it appears, and
the line's behaviour in a formset or under a screen reader are settings and variants of those two
things, so they are scenarios rather than stories.

**Self-resolved.**

**ADR:** none

## D2. The line appears only near the limit

**Chosen:** the line is hidden until the characters left reach a number the package sets, and a
developer can state another number per field.

**Why:** a count that is always shown is noise on a field that is nowhere near its limit, and a
short name field would carry it from the first keystroke. The issue asks for a line "counting
down", which matters only once there is little left. A developer who wants it from the first
character states a number at least as large as the limit.

**Self-resolved.**

**ADR:** expected, together with D3, for the shape of the setting

## D3. The limit on a text field is `max_length` and nothing else

**Chosen:** a text input or a textarea takes its limit from the field's `max_length`. A limit
stated on one of them is refused.

**Why:** the issue says the line follows the field's own `max_length`. A second limit would let
the line and the browser promise more, or less, than the field accepts. Django already writes
`max_length` on the input as `maxlength`, so the line adds no limit of its own.

**Self-resolved.**

**ADR:** expected, with D2

## D4. No Tom Select control in this feature

**Chosen:** the line is not offered on the package's `TomSelect` and `TomSelectMultiple`, though the
issue names them. django-tomselect's controls are not covered either.

**Why:** on a Tom Select control the line matters only where a person can create an option by
typing it, as on a tags field that accepts new entries, and there its limit is the length of a new
option's text. Where creating is off, the typing box only searches and a count bounds nothing a
person keeps, so the line is not offered. The package's widgets let a person choose only among
the field's choices (FS-017), so creating is off on all of them. If a setting that lets a person
create an option is ever specified, the line comes with it, with that limit.

**Decided at the specification's review.** Replaces the first reading, which offered the line on
the package's widgets with a limit the developer stated.

**ADR:** none

## D5. Polite announcements at a few moments

**Chosen:** assistive technology hears the number when the line first appears, when the person
stops typing, and when none are left. Never for each key.

**Why:** a live region that changes on every keystroke interrupts a screen reader user with a
number each time they type, which WCAG's guidance on status messages (4.1.3) and the ARIA
authoring practices both warn against. The moments chosen are the ones that change what a person
would do next.

**Self-resolved.**

**ADR:** none — the spec's requirement says enough

## D6. The line follows the field's count, line breaks included

**Chosen:** a text the line says fits must be accepted by the field on submit.

**Why:** checked on Django 6.1 (`research.md`, Assumptions checked): a textarea limited to 5
characters takes `ab`, a line break and `cd` in the browser, which counts the break as one, and
submits it with the break as two characters, which the field refuses. A line that says "0 left"
before an error on submit would be worse than no line. How the two counts are reconciled is for
planning.

**Self-resolved.**

**ADR:** expected, since it touches what a field with the line accepts

## D7. A value over the limit is reported, not cut

**Chosen:** the line says the value is over and by how many characters. Nothing cuts it.

**Why:** a value drawn with the form can be longer than the limit, from data saved before the
limit was lowered or a script that set it. Cutting it silently loses the person's text. The
field's own validation already refuses it on submit, so the line only has to make that visible
before then.

**Self-resolved.**

**ADR:** none

## D8. No wording setting

**Chosen:** the line's words are the package's, translated with their plural forms. A developer
cannot state their own.

**Why:** there is no project need for other words yet (Article XV), and a project can still change
them through its own translation catalogue. Plural forms are required because a one-or-many pair
is wrong in many languages.

**Self-resolved.**

**ADR:** none

## D9. No masked inputs

**Chosen:** the line is not promised on the input mask widgets of FS-015.

**Why:** a mask already fixes what can be typed, often to a fixed length, so a count adds nothing
a person can act on. Promising it would make the line answer to every mask kind.

**Self-resolved.**

**ADR:** none

## D10. The line counts as the browser's limit counts

**Chosen:** the script counts UTF-16 code units (`input.value.length`), as the browser's
`maxlength` does, and not code points.

**Why:** found at the design review, checked in Chromium: with an emoji in the text the field
stops taking characters while a code-point count still says some are left, which is the silent
stop this feature exists to end. A code-unit count is never smaller than a code-point count, so a
text the line says fits is still accepted by the field's validation. Replaces the first reading
of D6's count for characters outside the Basic Multilingual Plane. A value drawn with such
characters can be within `max_length` by Django's count and over by the browser's, and the line
then says it is over while the field accepts it.

**Self-resolved at the design review.** Amends FR-009 and one edge case of the specification.

**ADR:** none — covered by the line-break ADR

## D11. Design-review findings carried into the plan

**Chosen:** the line records which input it serves, so two marked fields in one joined group each
keep their own line. The script opens with the once-only window flag the package's other scripts
use. The textarea normalises with Django's `normalize_newlines`. A value stored with CRLF reads as
changed until saved once, and the README says so, as it says a `show_from` near a long limit makes
the page heavier.

**Why:** design review findings DR-002 to DR-007.

**Self-resolved.**

**ADR:** none
