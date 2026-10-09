# Decisions: Partial date field

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer confirmed the reading of the feature on 2026-10-09. Everything below that he did not
rule on directly is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. A field, with two widgets beside it

**Chosen:** one form field that owns the rule for what a partial date is, and two widgets a
developer may name on it. With no widget named the field uses a plain text input.

**Why:** the rule has to hold on the server whichever widget drew the input, and whether or not a
script ran. A widget cannot own it, because a widget does not validate. Keeping the default a
plain text input means a form can use the field with no script at all, and the masked widget
stays a choice the developer makes knowing the page must load IMask.

**Confirmed by the maintainer** as to the field and the two widgets. The plain default is
self-resolved.

**ADR:** expected. It is the package's first field and sets where validation lives.

## D2. The masked date input does not reopen FS-015

**Chosen:** a fifth mask widget with a fixed shape and no mask option. The calendar rules are in
the package's script.

**Why:** FS-015 left out a date widget because IMask's date mask needs functions a developer
cannot write in Python. That reason is about a developer's options. Here the developer states
none, so nothing has to cross from Python to JavaScript but the finest precision. The four
existing widgets are untouched and still take plain data only.

**Self-resolved.** The maintainer asked for the behaviour: no month over 12, days that follow
the month.

**ADR:** expected, amending ADR 0047 or standing beside it.

## D3. One-digit months and days are accepted and padded

**Chosen:** `2021-3-4` cleans to `2021-03-04`. A year must have four digits.

**Why:** on a page without the script a person types into a plain box and has no mask to pad for
them. The value is unambiguous, so refusing it is strictness with no benefit. A short year is
ambiguous and is refused. The maintainer's requirement is on what comes back, which is always
padded ISO text.

**Self-resolved.**

**ADR:** none. It is local to this field's parsing.

## D4. A trailing hyphen is ignored

**Chosen:** `2021-` is read as `2021`.

**Why:** a mask that places separators for the person can leave one at the end when they stop
after the year. Treating that as an error would punish the person for what the input did.

**Self-resolved.**

**ADR:** none. It is local to this field's parsing.

## D5. A day that stops existing is cleared

**Chosen:** in the three-part widget, changing the month or year so the chosen day has no date
clears the day.

**Why:** the alternative is to move it to the last day of the new month, and then the form
submits a date nobody chose. For a scientific record a missing day is honest and a moved one is
not.

**Self-resolved.**

**ADR:** none. It is one behaviour of one widget.

## D6. Precision is stated on the field, and the widgets follow it

**Chosen:** the coarsest and finest precision are options of the field. Each widget reads the
finest from the field it is on.

**Why:** the limit is a rule about the data, so it belongs with validation. Stating it again on
the widget would let the two disagree.

**Confirmed by the maintainer** as to a minimum precision and turning off the day. Where the
options live is self-resolved.

**ADR:** none expected, unless the plan finds the field has to configure its widget in a way the
package has not done before.

## D7. The three-part widget brings its own small script and does not need IMask

**Chosen:** a second script, named in the form's media, for the days that follow the month.

**Why:** the behaviour has nothing to do with masking, and a project that wants only this widget
should not have to load IMask for it. It ships the way the mask script does, so the pack's own
templates still need none.

**Self-resolved.**

**ADR:** expected, beside ADR 0045.
