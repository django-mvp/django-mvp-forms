# Progress — 012 Forms stay legible under every daisyUI theme

## 2026-10-03T22:23:46Z · Implementer US1 · T001

Did: copied daisyUI 5.7.47 themes.css to tests/data/daisyui-themes.css (the end-of-file hook added one trailing newline) and added its refresh note to the classes header. Wrote Colour (parse, mixed, faded, over, luminance, contrast) and Theme/Themes under tests/legibility/. Compositing keeps channels unclipped until the end, as a browser does; clipping first gives dark's 60% base-content 170 in blue where the reference has 178.
Verified: uv run pytest tests/test_legibility (37 passed); forge verify once to learn the conformance rule: it asked for tests/test_legibility/ as a non-mirror path, added to pyproject.toml; all six steps passed after.
Next: T002 Ink, Pairing, Measurement, Reader, Catalogue.
Watch: the vectors in research R4 hold to one step in 255 and two places.
