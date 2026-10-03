# ADR 0005 — The ids around a field are Django's, and the pack corrects its attributes in three cases

**Status:** accepted

## Decision

The field frame writes two ids and invents no others for them:

- `<auto_id>_helptext` on the help text,
- `<auto_id>_error` on one element that holds every error message for the field.

Django writes `aria-describedby`, `aria-invalid`, `required` and `disabled` on the input. The pack
leaves them alone except in three cases:

1. **A helper turns errors off.** The description names the help text only, or is removed when
   there is none, because the error element is not drawn.
2. **A form sets `use_required_attribute = False`.** A required input carries
   `aria-required="true"`.
3. **A helper turns labels off.** The input carries `aria-label` holding the label's text.

None of the three is applied to a widget drawn as a group (`BoundField.use_fieldset`), and a
developer's own `aria-describedby` or `aria-label` on the widget is never replaced.

## Why

Django 5.2, 6.0 and 6.1 all put `aria-describedby` on the input themselves, and they name exactly
those two ids. A pack that writes one id per error message, as crispy-tailwind does, leaves the
input describing itself by an element that is not on the page. Following Django's ids means what
Django writes on the input and what the pack writes around it agree with no code.

The three corrections are the cases where they would otherwise disagree, or where turning off
something visible would take information away from assistive technology.

Django copies a grouped widget's attributes onto each of its options, so a label or a requirement
written there would be announced for every radio button. Django withholds its own description
from those widgets for the same reason.

## Revisit if

A supported Django version changes the ids it names, or starts writing any of the three
attributes itself.
