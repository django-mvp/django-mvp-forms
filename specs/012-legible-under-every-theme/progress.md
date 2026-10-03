# Progress — 012 Forms stay legible under every daisyUI theme

## 2026-10-03T22:23:46Z · Implementer US1 · T001

Did: copied daisyUI 5.7.47 themes.css to tests/data/daisyui-themes.css (the end-of-file hook added one trailing newline) and added its refresh note to the classes header. Wrote Colour (parse, mixed, faded, over, luminance, contrast) and Theme/Themes under tests/legibility/. Compositing keeps channels unclipped until the end, as a browser does; clipping first gives dark's 60% base-content 170 in blue where the reference has 178.
Verified: uv run pytest tests/test_legibility (37 passed); forge verify once to learn the conformance rule: it asked for tests/test_legibility/ as a non-mirror path, added to pyproject.toml; all six steps passed after.
Next: T002 Ink, Pairing, Measurement, Reader, Catalogue.
Watch: the vectors in research R4 hold to one step in 255 and two places.

## 2026-10-03T22:33:15Z · Implementer US1 · T002

Did: Ink, Pairing, Element and Measurement (pairings.py); Reader with one paints table, a silent set and Uncovered (reader.py); Catalogue drawing the 73 listed states, the disabled and read-only forms, a disabled file input, a disabled toggle and switch, and the sweeps (157 states in all). Wrote the tests first and saw them fail on the missing modules.
Verified: uv run pytest tests/test_legibility (165 passed). Probed the reader tests by mutation (override, label share, held on a disabled button, radio own, soft fill, unchosen tab): each made one test fail. Read against the 35 themes, the own shortfalls match the brief: label 15, text-error 21, tab 33, error alert 23, plus the dismiss button's btn-ghost on coloured alerts and a radio ring inside label.
Next: T003, the check and the repairs.
Watch: a radio's ring and dot take the inherited text ink, so a label's 60% reaches them; the faded border of a radio is not own.
