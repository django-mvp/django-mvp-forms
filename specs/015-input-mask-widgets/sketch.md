# Sketch: Input mask widgets for IMask

The prototype is the demo page "Input masks". It was built to be looked at and typed into. Nothing
behind it is tested, and the code behind the page is the plan's to keep or rebuild.

## What exists

- The pack draws any `forms.TextInput` subclass as a daisyUI `input`, and applies the size, colour
  and variant stated on the helper or by a `Choice` in the layout. A widget that subclasses
  `TextInput` needs nothing more to be drawn as one of the pack's own.
- The package has no `widgets` module and no static files. This is the first of each.
- The demo's pages extend django-mvp's `page_view.html`, whose base template has an `extra_js`
  block. Nothing in the demo renders a form's media today.
- The demo's formsets have no control that adds a row. Adding rows is django-mvp's, and the demo
  does not use it.
- `Modal` draws a `<dialog>` that is in the page from the start, so its inputs exist when the page
  loads.

## What the screens need from the code

- Four widgets a form names on a field, each drawing a text input that carries its options.
- A number widget whose submitted value reaches a `DecimalField` or `IntegerField` as a plain
  number, and whose initial value is shown with the stated separators.
- One script, named in the widgets' media, that applies IMask to each such input, to inputs added
  later, and never twice to the same one.
- An event from each input once its mask is in place, carrying the IMask instance.
- A page template that loads IMask and then renders the form's media.
- The script acts once however many times a page includes it. django-crispy-forms writes a form's
  media inside each form it draws, so a page with eight forms holds the script eight times. The
  first prototype applied a mask once for each copy, and a field with a display character then
  accepted nothing. The specification's edge case that says Django's media loads the script once
  is wrong for forms drawn with `{% crispy %}` and is to be corrected when the feature is planned.
- A page drawn with `{% crispy %}` needs IMask and nothing else added, since the form brings the
  script. A page drawn with `|crispy` or Django's own rendering renders the form's media itself.
- A field with a display character submits what was typed. IMask puts the display characters in
  the input, so without help the form receives dots. The sketch sets the real value when the
  form's data is collected.
- A placeholder that says what each position takes. IMask has one placeholder character for a
  whole pattern, so the sketch splits a pattern into blocks to give letters and digits a
  character each. A developer should not have to write blocks for that.

## What the sketch faked

- The widgets take their options under provisional names (`PatternMaskInput`, `RegexMaskInput`,
  `NumberMaskInput`, `DynamicMaskInput`, and the event `mvp-forms:imask`). The plan chooses the
  names.
- The widgets check nothing. A wrong option, a missing pattern or a contradictory pair is accepted
  without an error.
- A pattern's blocks are written as plain dictionaries with IMask's own key names, and options are
  passed to IMask under its own names. The plan decides how a developer writes a block.
- The "Add a line" button is a script written into the demo page. It copies the last row and
  renumbers it.
- The demo page loads IMask from jsDelivr at `imask@7`, unpinned.
- The page's own listener and button script are inline, so the demo page itself would not pass a
  policy that forbids inline script. The package's script is a file.
- There is no standalone page without django-mvp, which every other demo page has.
- The table under "Try it" that shows what each field received is drawn with a bare daisyUI table
  in the page template.
- No README section, no decision record and no glossary terms.

## What was ruled by eye

Ruled by the maintainer on the first round:

- The page is grouped by widget. Each widget has a section of its own, named after the widget,
  with its own form and submit button. Sections that show a masked field in a state, at a size, in
  a formset and in a modal follow, and each says which widget and mask it uses.
- An always-visible placeholder uses characters that say what the position takes: `#` for a digit,
  `a` for a letter, and `d`, `m` and `y` for the parts of a date. A dot or an underscore for every
  position is not used.
- Every field that demonstrates a pattern or a regular expression states it in full in its help
  text, with the meaning of any definition or block. A number field states its options.

Ruled by the maintainer on the second round:

- The PIN field has to show a dot for each digit typed. It showed nothing.

Ruled by the maintainer on the third round, when he approved the sketch:

- Each widget's section links to the part of the IMask guide that documents its kind of mask.

Decided while building, and the maintainer's to change:

- Each widget's form shows the text submitted beside the value the field received.
- The sidebar entry sits above "Themes" and uses the `bi-123` icon.
