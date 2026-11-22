# Research: Characters left under a text field

Written at specification and extended when the feature was built, against `origin/main` on
2026-11-22.

## Assumptions checked

Checked on 2026-11-22 against `origin/main`, Django 6.1.3.

- **Django writes `max_length` on a text input and a textarea.** A `CharField(max_length=20)` draws
  `<input type="text" ... maxlength="20">`, and with `widget=forms.Textarea` draws
  `<textarea ... maxlength="200">`. The limit the line follows is already on the input.
- **Failed: a textarea's line breaks are counted twice on submit.** A form with
  `CharField(max_length=5, widget=forms.Textarea)` sent `ab\r\ncd`, which is how a browser submits
  the five characters `ab`, a line break and `cd` that its `maxlength` allowed, is refused with
  "Ensure this value has at most 5 characters (it has 6)." This is why FR-009 is a requirement and
  not an assumption: the build has to reconcile the two counts.

## Planning notes, answered

- **The design of the line** (hidden until a few are left, driven by `data-` attributes, a
  listener on the document, eight as the number): **adopted**. Eight is the package's number.
  The attributes sit on the input, and `data-characters-left-from` is the marker the script
  finds it by.
- **Tom Select controls left alone**: **adopted**. The script only acts on an input that carries
  the marker, and a Tom Select control's typing box never does, so there is no code for the
  case. A test puts both in one field.
- **Announced politely, not on every keystroke**: **adopted**. The line the eye reads is hidden
  from assistive technology, and a second, visually hidden status region beside it is written
  only at the three moments of FR-011.
- **How the line is turned on**: **adopted: widgets of the package's own** for a text input and a
  textarea, `CharactersLeftInput` and `CharactersLeftTextarea`, sharing a mixin. Django's
  `TextInput` and `Textarea` are not the package's to change, and a helper that returns
  attributes cannot put the script in the form's media, which the README promises for every
  widget that needs one.
- **A textarea's line breaks**: **adopted: the field counts as the browser does.** The textarea
  widget turns `\r\n` and `\r` in the submitted text into `\n` before the field sees it. Django's
  own `Textarea` leaves the breaks as submitted, so a field's `max_length` and a browser's
  `maxlength` disagree (checked above). The other way, a script counting each break as two,
  would let the browser take a text that the line then calls over the limit, and would leave
  every other reader of the field with the mismatch. Normalising on the way in makes the
  browser, the line and the field agree, and the text is stored with `\n`.
- **Translations**: **adopted: the words are written for every count the line can show.** The
  widget writes the line's words for each count from none up to the number from which the line
  appears, through `ngettext` in the language the page is drawn in, so the plural forms are the
  catalogue's own. Django's JavaScript catalogue was not adopted: it needs a view and a URL, and
  the package adds neither (FR-020). The over-the-limit words are one phrase that carries the
  number and no counted noun (`Over the limit by 3`), so they need no plural form and no table.

## What already exists

- The text input and the textarea are drawn by the pack from `forms.TextInput` and
  `forms.Textarea` (`FieldInput.components`, `mvp_forms/templatetags/daisyui.py`), and a subclass
  of either is drawn the same way. **This repo**, nothing to add to the pack.
- Attributes on a widget reach every renderer: `MaskInput.build_attrs` writes `data-imask`, and
  the pack's `widgets/attrs.html` draws every attribute. **This repo**, the same shape.
- Media on a widget through a nested `Media` class: `MaskInput`, `ImageInput`. **This repo.**
- Option checks that raise `ValueError` naming the option: `Check` in `mvp_forms/widgets.py`.
  **This repo.**
- Plural forms in a translated string: `django.utils.translation.ngettext`. **Django.**
- A status region read politely: `role="status"`. **The browser.**
- The visually hidden class: `sr-only`, a Tailwind utility the pack already writes
  (`layout/fieldset.html`). **Tailwind.**
- Following content added later: a `MutationObserver` on the document. **The browser.**
- Line break normalisation: `django.utils.text.normalize_newlines`. **Django.**
- Counting as the browser's limit counts: `input.value.length`. **The browser.**
- The line itself, its script and its attributes. **New code**, because no maintained package
  offers a count line drawn in daisyUI markup.
