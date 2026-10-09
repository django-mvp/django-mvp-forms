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

Decided while building, and the maintainer's to change:

- One page for the whole feature, in the order: one field of each kind to try, pattern options,
  number options, states, size and colour, a formset, a modal, the event.
- Each field's help text states its mask, so the page explains itself without a second column.
- The first form is the only one that submits. It shows the text submitted beside the value the
  field received, since that difference is the point of the number widget.
- The sidebar entry sits above "Themes" and uses the `bi-123` icon.
