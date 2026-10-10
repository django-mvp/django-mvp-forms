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

**ADR:** docs/adr/0048-a-field-owns-the-rule-and-every-option.md

## D2. The masked date input does not reopen FS-015

**Chosen:** a fifth mask widget with a fixed shape and no mask option. The calendar rules are in
the package's script.

**Why:** FS-015 left out a date widget because IMask's date mask needs functions a developer
cannot write in Python. That reason is about a developer's options. Here the developer states
none, so nothing has to cross from Python to JavaScript but the finest precision. The four
existing widgets are untouched and still take plain data only.

**Self-resolved.** The maintainer asked for the behaviour: no month over 12, days that follow
the month.

**ADR:** docs/adr/0050-the-partial-date-mask-has-a-rule-of-its-own.md

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

**ADR:** docs/adr/0048-a-field-owns-the-rule-and-every-option.md

## D7. The three-part widget brings its own small script and does not need IMask

**Chosen:** a second script, named in the form's media, for the days that follow the month.

**Why:** the behaviour has nothing to do with masking, and a project that wants only this widget
should not have to load IMask for it. It ships the way the mask script does, so the pack's own
templates still need none.

**Self-resolved.**

**ADR:** docs/adr/0051-the-three-part-widgets-bring-a-script-that-needs-no-imask.md

## D8. Every option on the field, and three widgets that take none

**Chosen:** `coarsest`, `resolution`, `min_value` and `max_value` are keywords of the field. The
widgets take `attrs` only. The year select is a third widget, `PartialDateSelect`, and not an
option of the three-part widget. This supersedes what D1, D2 and D6 say of two widgets and of the
finest precision being all that crosses to a script.

**Why:** the maintainer asked for one field with a swappable widget, so changing widget has to be
a change of one name.

**Ruled by the maintainer**, 2026-10-10, including the name `resolution`.

**ADR:** docs/adr/0048-a-field-owns-the-rule-and-every-option.md

## D9. The field tells its widget through `get_bound_field`

**Chosen:** the field sets `resolution`, `min_value` and `max_value` on its widget when a form
first reads the field. A widget is swapped before the form is first drawn or validated.

**Why:** a widget named in a form's `__init__` after the field was built would otherwise know
nothing. Research R3.

**Revisit if:** a project needs to swap a widget on a form that has already been validated.

**ADR:** docs/adr/0049-a-field-tells-its-widget-when-a-form-first-reads-it.md

## D10. A partial value is inside the limits when any day it could be is

**Chosen:** `1998` passes an earliest date of `1998-03-15`. `1998-02` does not.

**Why:** refusing `1998` would force a person who knows only the year to invent a month.

**Self-resolved**, shown to the maintainer with the prototype.

**ADR:** none — a rule of this one field, stated in the README.

## D11. The year list with an earliest date in the future

**Chosen:** with no latest date and an earliest date after this year, the list runs a hundred
years on from the earliest. FR-040 read to the letter ends the list at this year, which would
leave it empty.

**Self-resolved**, for the maintainer to overturn.

**ADR:** none — local to one widget's default.

## D12. The padding keeps IMask's range block subclass

**Chosen:** the month and day blocks subclass `IMask.MaskedRange` and override `_appendCharRaw`.

**Why:** IMask's published `prepare` and `prepareChar` options both lose part of the value when a
person changes the middle of a date. Research R1 has the cases.

**Revisit if:** IMask gains a published way to pad a range, or a new IMask version fails the
browser tests that pin this.

**ADR:** docs/adr/0050-the-partial-date-mask-has-a-rule-of-its-own.md

## D13. A masked input shows a refused value whole

**Chosen:** FR-042. The mask is held off an input whose value it would cut, until the person has
changed it to one the mask takes.

**Self-resolved** after the question was put to the maintainer twice and left open.

**ADR:** none — covered by the README and the browser test.

## D14. Design review

One reviewer, three lenses, one round: changes requested. Applied: the padding decision above
(high), the mid-value cases and the refused change in T003, ASCII digits only in T001, the month
names under another language in T004, a held value outside the limits in T008, the waiting input
recorded, and three README sentences. Carried as documentation: a limit is fixed when the form
class is defined. Whether a limit could be a callable is a question for the maintainer and is
not built.

**ADR:** none — a record of the review.

## D15. The template-list check learns the package's own widget template

**Decision:** `tests/template_surface.py` takes `mvp_forms/` beside `daisyui/` as a directory of
the package's templates, and counts `PartialDateInput.template_name` among those the form
renderer loads. Made directly at the end of US1, with no dispatch: three lines in a test helper
and one in its test.

**Why:** the check refused any distributed template outside `daisyui/` and
`django_tomselect/`, and this is the first widget of the package that names a template.

**ADR:** none — a test helper following the code.

## D16. The limits are tested on the existing browser pages

**Decision:** the two browser-test forms, `MaskedPageForm` and `PartialDatePageForm`, each gain
fields with limits of `1998-03-15` and `2004-09` (`born_limited`, `limited_typed`,
`limited_listed`), and the limits tests use those. No new page or route.

**Why:** the pages already answer a post, carry initial values and bound entries through the
query string, and give the formset's empty form. A second page would repeat all of that for
three fields. The new fields are optional, so no existing test's post or error expectations
change.

**Revisit if:** a limits test needs a form the existing pages cannot draw, such as a resolution
of month with limits and a formset of its own.

**ADR:** none — a test fixture.

## D17. A change inside a masked date is put back, and a value put back is not padded

**Decision:** for the partial date kind only, `imask.js` reads the text after the caret in a
capturing `input` listener, before IMask's own listener runs. When IMask's result no longer
ends with that text, the value and selection recorded at `beforeinput` are given back. The value
is given back with the padding of `prepare` switched off for that one assignment, recorded in a
`WeakSet` keyed by the Masked instance that `prepare` receives. The branch of `prepare` that
passed a tail on unchanged is removed.

**Why:** IMask drops a typed character when the digits after it no longer fit and re-flows the
rest through blocks that pad and refuse, so an edit in the middle turned one date into another
that exists. Put back through `prepare` as it stood, a held `2021-1` was padded to `2021-01`,
which changed a part the person had not touched. The tail branch is unreachable under the rule:
a tail is a whole date with a one-digit part only for an edit at position 0, and the result then
cannot end with the text the edit left after it, so the value is put back whether the tail was
padded or not. Probed with the branch restored: every browser case gave the same value.

**Revisit if:** a newer IMask changes the order of its `input` listener against a capturing one,
or the maintainer wants selecting a part and typing a new one to work in the middle of a value.

**ADR:** none — a script detail inside the mask the earlier decision already covers.

## D18. The demo pages draw the formset's empty form once, as a row, from the view

**Decision:** `PartialDatesMixin` puts a second `SampleFormSet` in the context as `line`, whose
only form is the formset's `empty_form`, and both demo templates draw it with the table helper
inside a `<template>`. "Add a sample" copies that template's row and replaces `__prefix__` with the
form count. `demo/partial_date_views.py` is the one file outside the task's list that changes.

**Why:** the table template lays out a formset's `forms`, and a template cannot hand it a single
form. Drawing the empty form through the same helper keeps the row's markup the same as the
rows already on the page, so what the page shows does not change, and a pristine row holds every
option, which the script takes for the full list.

**Revisit if:** the table helper learns to draw an empty form directly.

**ADR:** none — a demo page detail.

## D19. The options are `min_resolution` and `max_resolution`

**Decision:** the least and most of a date a field accepts are `min_resolution` and
`max_resolution`. The error codes for a part that is not allowed are `month_not_allowed` and
`day_not_allowed`. No older name is kept as an alias, since nothing has been released.

**Why:** the maintainer walked the pages and said coarsest and finest do not read as words about
dates. The pair sits beside `min_value` and `max_value`.

**Ruled by the maintainer**, 2026-10-10, as to the words. The pair of names and the two codes are
self-resolved from what he proposed.

**ADR:** docs/adr/0048-a-field-owns-the-rule-and-every-option.md

## D20. The masked input shows its open positions and is typed over in place

**Decision:** FR-043 to FR-045. While a person is in the input its open positions are shown as
`Y`, `M` and `D`. Typing writes over the position at the caret and moves nothing. A deletion that
would move a digit of another part is not applied. Outside the input it holds the partial date
alone. The put-back restores the mask's own state and not the text shown, the caret goes to the
first open position on focus, and the range an edit may touch is as long as what was written.

**Why:** the maintainer asked for the placeholders, and found that a digit deleted from the
middle of a date could not be typed back. Typing over in place answers both.

**Revisit if:** a project needs the letters of the open positions in another language.

**ADR:** docs/adr/0050-the-partial-date-mask-has-a-rule-of-its-own.md
