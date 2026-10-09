# Sketch: django-tomselect support

A prototype of the screens, built before the feature is planned. Nothing here is tested, and the
code behind the screens is rebuilt when the feature is built. What the maintainer approves is how
the controls look and behave on the demo pages.

## What exists

- The pack already writes daisyUI's `select` class on a django-tomselect select, with the size,
  colour, variant and error modifiers stated for the form or the field, because a widget that
  names a template of its own gets the pack's classes and nothing else (ADR 0012).
- Tom Select copies the classes of the select to the wrapper it builds, and to its dropdown. The
  wrapper is therefore a daisyUI select before any stylesheet of ours is loaded: border, height,
  radius, caret, focus ring, colour, variant and size all arrive from daisyUI.
- django-tomselect ships Tom Select's default stylesheet and a small one of its own. Both name
  colours of their own, and its own marks two of them `!important`.
- django-tomselect draws group headings, and nothing in it says which group an option fetched
  from the server belongs to. Its widget template has blocks made for extending.
- django-tomselect starts a control when the page has finished loading, unless the field's
  configuration, or the project's default configuration, sets `use_htmx`. With it set, a control
  starts as soon as its markup arrives.
- The demo has no models. django-tomselect has an autocomplete view that answers from a list,
  so the demo page needs none.
- daisyUI draws the options of its own select as a padded panel with rounded options. That is
  the model the dropdown follows.

## What the screens need from the code

1. `tomselect.css` among the package's static files, loaded by the host project after daisyUI.
2. The stylesheet has to win over Tom Select's stylesheet whichever is loaded first.
3. The wrapper must stop clipping what leaves it, or the dropdown is cut off: daisyUI's select
   hides its overflow.
4. Tom Select marks a wrapper that is fetching with the class `loading`, which daisyUI draws as
   a spinner in place of the element. The control needs that undone and a sign of its own.
5. An option that carries an `optgroup` key is listed under a heading of that name. The sketch
   does this in a template of the package's that extends django-tomselect's. How a developer
   names the group, and where the package hooks in, are for the plan.
6. A control in content htmx swaps in needs `use_htmx` set. The demo sets it once, in the
   project's default configuration. The README has to say so.
7. An open dropdown has to leave daisyUI's modal box and the scroller around a table formset.
   The sketch lets both overflow while a dropdown inside them is open.
8. The demo needs django-tomselect installed, its middleware and context processor, four
   autocomplete routes, and its stylesheets and script in the base template.
9. The sidebar needs a group for third-party widgets.
10. A field that accepts a value typed in needs a field class that does not reject it. The demo
    has one. Whether the README shows one is for the plan.

## What the sketch faked

- The four autocomplete views answer from lists in `demo/autocompletes.py`. No model is involved,
  so the model-backed widgets are not on the page.
- Nothing is saved. The form to submit shows what it cleaned to.
- The demo's tagging field accepts any value. A real project validates and stores new values in
  its own view.
- The template list in the README, the CHANGELOG, the glossary, Article XIV and the decision
  records are untouched. So are the tests, some of which will fail on the new template and
  static file until the build accounts for them.
- django-tomselect's `tomselect_media` template tag raises on Django 6.1, so the demo's base
  template links django-tomselect's three files by path.
- Legibility under `light` and `dark` was calculated once by hand for the tag, the tag's remove
  button, an option, the active option and a group heading. There is no check in the suite.

## What was ruled by eye

Decisions with no right answer, made so there was something to look at. Each is the
maintainer's to change.

- A control that holds several values has no caret.
- Tags are neutral: the theme's second base colour with a border in the third, whatever colour
  the control states. The tag the keyboard is on takes the theme's neutral colour.
- The tag's remove button is separated from the text by a line and darkens under the pointer.
- The clear button appears only while the control holds a value and is under the pointer or
  focused.
- The dropdown is a rounded panel a short gap below the control, with a soft shadow, as wide as
  the control.
- The part of an option that matches what was typed is bold and underlined, with no background.
- Group headings are smaller, semibold and slightly muted, and groups are separated by a line.
- The offer to add a value sits under a line at the end of the options.
- While options are fetched, a small ring turns beside the caret.
- At the two smallest sizes a control holding tags is a few pixels taller than a stock select,
  because django-tomselect keeps each remove button at least 24 pixels square.
