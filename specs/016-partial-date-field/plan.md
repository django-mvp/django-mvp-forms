# Implementation Plan: Partial date field

**Branch**: `016-partial-date-field` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

One field, `PartialDateField`, in `mvp_forms/fields.py`, and three widgets in
`mvp_forms/widgets.py`: `PartialDateMaskInput`, `PartialDateInput` and `PartialDateSelect`. The
field owns every rule and every option. Each widget keeps a person from breaking those rules in
the browser, through `mvp_forms/imask.js` for the masked input and a new script,
`mvp_forms/partial-date.js`, for the other two. The approved prototype is on the branch. Its demo
page is kept as approved. The field, the widgets and the scripts behind it are rebuilt test-first.

## Technical context

- Python 3.12 to 3.14, Django 5.2 to 6.1, django-crispy-forms 2.7. No new dependency.
- IMask 7 for the masked widget only, loaded by the host project. The copy under `tests/data/`
  serves the browser tests.
- No models, migrations, views or URLs in the package.

## Constitution check

| Article | How the plan meets it |
|---|---|
| I, test first | Every task writes its tests first and sees them fail with the prototype's code for that part removed |
| II and III, least machinery | One field class, three widget classes of which one subclasses another to replace one part. No registry, no settings, no dataclass, no shared script |
| VIII | Error messages and part names are translatable, and the English catalogue is regenerated |
| X | The rules are methods of the field. The scripts are each one function scope |
| XI, public surface | The field, its five options and error codes, the three widgets, the template path, the script path and the `data-partial-date` attributes are public from this release and listed in the README |
| XII, scope | A field and widgets only |
| XIII | The new template is a plain Django template. The modules import Django and the standard library |
| XIV | daisyUI's `join`, `join-item`, `input` and `select`, and Tailwind width utilities. No stylesheet |
| XV | Classes, template, tests and README entries arrive in this pull request |

## The field

`PartialDateField(forms.CharField)`, with keyword-only options before `CharField`'s own:

| Option | Takes | Default |
|---|---|---|
| `coarsest` | `"year"`, `"month"` or `"day"` | `"year"` |
| `resolution` | `"year"`, `"month"` or `"day"`: the finest precision accepted | `"day"` |
| `min_value` | a partial date as text, or a `datetime.date` | none |
| `max_value` | the same | none |

Raised with `ValueError` when the form class is defined, naming the option: a precision that is
not one of the three, a `resolution` coarser than `coarsest`, a limit that is not a partial date,
and a `min_value` later than `max_value`.

Methods:

- `to_python(value)`: empty gives `""`. Otherwise `parse`, then the precision checks, then the
  limits.
- `parse(value)`: the calendar rules, returning padded ISO text. A trailing hyphen is dropped.
  A value cut off inside a part cannot be told from a one-digit part for a month or day, so
  `2021-0` fails as a month of zero and `202` fails as a year.
- `span(value)`: the first and last day a partial date could be, as two `(year, month, day)`
  tuples. A value is inside the limits when its last day is not before the first day of
  `min_value` and its first day is not after the last day of `max_value`.
- `prepare_value(value)`: a `datetime.date` becomes ISO text.
- `get_bound_field(form, field_name)`: sets `resolution`, `min_value` and `max_value` on
  `self.widget`, then returns `super()`'s (research R3).

Error codes, each raised with `code` and each replaceable through `error_messages`: `invalid`,
`year`, `month`, `day`, `no_year`, `no_month`, `needs_month`, `needs_day`, `too_fine_month`,
`too_fine_day`, `min_value`, `max_value`. The last two carry the limit as `params`.

The default widget is `CharField`'s `TextInput`.

## The widgets

All three take `attrs` only, and carry class attributes `resolution = "day"`, `min_value = None`
and `max_value = None` that the field overwrites on the instance.

**`PartialDateMaskInput(MaskInput)`**: `kind = "partial-date"`, `inputmode="numeric"` unless the
developer's `attrs` state one. `mask_options` returns the kind, the resolution, and `min` and
`max` where stated.

**`PartialDateInput(forms.MultiWidget)`**: parts named `year`, `month` and `day`, so the
submitted names end `_year`, `_month` and `_day`. The year is a text input holding four digits,
the month a select of the twelve names, the day a select of 1 to 31. Each part carries
`join-item`, a width utility, an `aria-label` and `data-partial-date-part`. The first option of
each select is empty and names the part.

- `year_part()` returns the year's widget. It is the one method the subclass replaces.
- `decompress` splits ISO text or a `datetime.date`.
- `value_from_datadict` joins the parts with hyphens and drops empty parts from the right, so a
  day with no month arrives as `2021--14` and the field refuses it.
- `get_context` drops the parts beyond the resolution, removes `required` from every part but
  the year, and adds `min_value` and `max_value` for the template.
- Template `mvp_forms/widgets/partial_date.html`: one element classed `join` with
  `data-partial-date`, and `data-partial-date-min` and `data-partial-date-max` where stated,
  around the parts.
- Media: `mvp_forms/partial-date.js`.

**`PartialDateSelect(PartialDateInput)`**: `year_part()` returns a select. `get_context` lists
its years first: from the year of `max_value` down to the year of `min_value`. With no
`max_value` the list starts at this year, or a hundred years after `min_value`'s year when that
is in the future. With no `min_value` it reaches a hundred years back from where it starts. A
held year that is not on the list is put first.

## The scripts

**`imask.js`** gains the `partial-date` kind. Its options for IMask: the pattern for the
resolution (`Y`, `Y-M` or `Y-M-D`), three plain `IMask.MaskedRange` blocks, `prepare` for the
padding (research R1), and `validate`, which works out the lowest and highest date the typed
text could still become and refuses the keystroke when that reach holds no date the calendar and
the limits allow. Before a partial date mask is created the value is tried, and a value the mask
would change is left alone until the person's edit makes one it takes (research R2). Everything
ADR 0045 says of the script still holds: one flag on `window`, inputs added later, no input
masked twice, nothing done without IMask.

**`partial-date.js`** is new and needs no IMask. One function scope, guarded by a flag on
`window`. For each `[data-partial-date]` element, when the page loads, when one is added, and on
every `input` and `change` inside one:

- the month can be chosen only under a whole four-digit year that holds an allowed day
- the months offered are those with an allowed day in that year
- the day can be chosen only under a chosen month, and the days offered are the allowed days of
  that month in that year
- options that cannot be chosen leave the list (research R4)
- a month or day the change has made impossible is cleared, never moved
- when a group is first met, a part that holds a value is left as it was sent, enabled, with its
  option kept

No inline script, no inline handler, no `eval`, no network.

## The tests

- `tests/test_fields.py`, new, mirroring `mvp_forms/fields.py`: one class, `TestPartialDateField`,
  split further only if it passes 300 lines. Errors are asserted by code.
- `tests/test_widgets.py`: a class for each of the three widgets.
- `tests/test_pack/test_partial_dates.py`, new: each widget drawn through the pack, with a size
  and a colour, in error, in a formset's empty form, and through Django's own rendering.
- `tests/test_imask_e2e.py`: a class for the partial date mask.
- `tests/test_partial_date_e2e.py`, new, marked `e2e`, declared in `non-mirror-paths`.
- `tests/test_pack/test_independence.py`: the static directory holds the stylesheet and two
  scripts. `tests/test_pack/test_template_list.py` passes once the README lists the template.
- `tests/test_demo.py`: the page and its standalone version answer, each widget's section is
  present, and a post returns what each field received.

No test asserts wording, a class used for looks, or a width. Browser tests assert what this
package's scripts do.

## The demo

The page approved in the sketch is kept: its sections, order, help text and fields. Three things
change, each shown at the walkthrough:

- help text that says `finest=` says `resolution=`
- the masked input's "a day the month does not have" row shows `2021-02-30` whole (FR-042)
- the forms no longer tell their widgets by hand, since the field does it

A standalone page without django-mvp is added, as every other demo page has.

## Documentation

- README: a section "Partial dates" under the public surface, after "Input masks". The field's
  values, options and error codes land with US1, each widget with its story, the precision
  options with US4 and the limits with US5. The template joins the template list in US3.
- FS-015's `spec.md`, ADR 0047 and the README's "Input masks" section stop saying there is no
  date widget (research R10), in US2.
- `CONTEXT.md`: partial date, precision, and the sense of part, in US1.
- CHANGELOG: one entry under Added, grown story by story.
- Decision records at convergence: the package's first field and where validation lives, the
  field telling its widget through `get_bound_field`, and a second script that needs no IMask.

## Story order

US1 → US2 → US3 → US4 → US5, sequential, in the feature worktree.

## What this plan does not do

- No model field, no storage, no dependency on a partial date package.
- No calendar to pick from, no other order of parts, no other separator.
- No change to the four mask widgets of FS-015, to the pack's templates, to `CONSTITUTION.md` or
  to anything under `.github/`.
- No feedback in the browser for a typed year outside the limits beyond the closed month
  (research R5).
- No test of IMask's own masking rules.
