# Research: Characters left under a text field

Written at specification. The investigation for planning is added below when the feature is built.

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
