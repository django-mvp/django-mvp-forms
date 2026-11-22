# Planning notes: Characters left under a text field

Things to consider when this feature is planned. Each one is answered by name in `research.md`.

The design of the line is settled: hidden until a few characters are left, then a line under the
field saying how many, driven by `data-` attributes on the input and a script that listens on the
document, so it survives htmx swaps and rows added later. Eight characters left is the number it
was designed and tried with.

The package's Tom Select widgets (FS-017, `mvp_forms/static/mvp_forms/tomselect.js`) are the one
place the line has to reach inside a control a script builds. Tom Select gives its typing box the
select's `id` followed by `-ts-control`, and empties the box when a typed value is used, which
raises no `input` event. How the line attaches there, and how it behaves whichever of the two
scripts runs first, is for research.

The line is announced to screen readers politely, not on every keystroke.

How the line is turned on is open: a setting on the package's widgets, widgets of the package's
own for a text input and a textarea, or attributes a helper returns. Whatever is chosen has to put
the script in the form's media, as the README promises for every widget that needs one, and a
helper that returns attributes alone cannot.

A textarea's line breaks are counted as one by the browser and as two by Django's `max_length`
validation (checked, `research.md`). The line has to follow the field's count, so either the
script counts the breaks as the field will, or the field counts them as the browser does. Look at
how Django itself and other packages have handled this before choosing.

Translations need the plural forms of the language. A pair of "one" and "other" strings is wrong
in many languages. Writing the line's words for each count the line can show, or Django's
JavaScript catalogue, are two ways to look at.
