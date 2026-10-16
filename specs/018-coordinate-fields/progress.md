
## 2026-10-15T10:34:21Z · orchestrator · PLAN

Specification approved; research, plan and tasks written. Four stories, five tasks, in the order US1, US2, US4, US3. No sketch.

## 2026-10-15T10:36:41Z · orchestrator · S3R

Design review not dispatched: sessions_spawn refuses every model (anthropic account unavailable; claude-cli model not allowed). Sam chose to restore the account; the run waits at DESIGN_REVIEW with the brief written.

## 2026-10-15T13:37:48Z · orchestrator · S3R

Resumed in a new session; branch brought up to date with origin/main and the build claim moved to this session. Design review still not dispatched: sessions_spawn refuses opus, sonnet and the default model again ("selected account or native runtime is unavailable"; claude-cli models not allowed). The run waits at DESIGN_REVIEW with the brief rebuilt at /tmp/fs018/brief.json.

## 2026-10-15 · orchestrator · S3R

Resumed in a fresh session outside the worktree; the build claim moved to it. Design reviewer dispatched on opus against commit 07626a1.

## 2026-10-15T14:33:29Z · Implementer US1 · T001

Did: LatitudeField and LongitudeField on a shared CoordinateField(DecimalField) in mvp_forms/fields.py: definition-time ValueErrors per option, to_python reading numbers as numbers and text by a plain-number pattern, -0 to 0, per-code messages. 170 new cases in tests/test_fields.py written first (red: ImportError), then probed by five mutations (abs, pattern, text branch, bound range, decimal_places), each failing 2 to 10 cases. README section "Coordinates", CHANGELOG, CONTEXT.md terms, English catalogue regenerated with makemessages from mvp_forms/.
Verified: uv run pytest tests/test_fields.py -k Coordinate (170 passed); uv run pre-commit run --all-files green; uv run pytest -n auto -q (6586 passed).
Next: T002, the masked input.
Watch: the default widget is still DecimalField NumberInput until T002, so the initial-display test asserts only value="51.5" in the drawn HTML.

## 2026-10-15T14:45:51Z · Implementer US2 · T002

Did: CoordinateMaskInput, default widget of both fields written in get_bound_field, coordinate kind in imask.js with its own validate and the takes/wait path, README, tests.
Verified: widget, pack and e2e tests green; the e2e module fails 13 of 18 against the previous script; pre-commit green.
Next: T003 demo page.
Watch: a lone minus commits as -0 in IMask 7.6.1 (pinned by a test).

## 2026-10-15T14:47:38Z · Implementer US2 · T003

Did: Coordinates demo page (defaults, initial value, bound form in error), route, menu entry after Counted multiple select, icon.
Verified: TestCoordinatesPage green; full suite 6650 passed; pre-commit green; dev server answers /coordinates/ with 200.
Next: US4 (T004).
Watch: none.

## 2026-10-15T14:55:20Z · Implementer US4 · T004

Did: tests for narrowed bounds (40..60, -60..-40) and decimal places in fields, widget JSON and the browser; ADR 0056; README, changelog, demo section. validate in imask.js needed no change.
Verified: uv run pytest -n auto --dist loadscope -q: 6682 passed. Mutation probes: number kind in build() fails 4 browser tests; dropping the bounds in the field fails 24 field/widget tests.
Next: US3.
Watch: the input-drawn-with-35 browser test passes under the number-kind mutation too, so it pins the posted value, not the kind.

## 2026-10-15T15:05:42Z · Implementer US3 · T005

Did: PointField (MultiValueField of a LatitudeField and a LongitudeField, incomplete raised by clean with incomplete_latitude/incomplete_longitude, compress to SRID=4326;POINT(lon lat)) and PointInput (MultiWidget of two CoordinateMaskInput parts, decompress for stand-in, WKT text and pair, ValueError for other SRID/height/non-point) with mvp_forms/widgets/point.html. Tests first (ImportError red): fields, widget, pack, browser, demo. Demo: point, formset of points, modal. README, CONTEXT, CHANGELOG, catalogue, template list row, template_surface route list extended.
Verified: uv run pytest -n auto -q: 6803 passed; pre-commit all hooks passed.
Next: none, last story.
Watch: tests/template_surface.py and tests/test_pack/test_template_surface.py needed PointInput.template_name added (outside the named file list).
