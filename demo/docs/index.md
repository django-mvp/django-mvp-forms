# Overview

MVP Forms is a daisyUI template pack for django-crispy-forms, with a few form
fields and widgets of its own. Name the pack in your settings and every form
you already have comes out as daisyUI components, with no template to write.

```python
CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]
CRISPY_TEMPLATE_PACK = "daisyui"
```

Each page here shows one thing. The form on the left is running: fill it in and
send it. The code on the right is the file that makes it, read from this
project, so what you see is what you would write. Switch the theme in the top
bar and every example follows.

## Where to look

**Crispy forms** is what the pack does for forms and layouts you write with
django-crispy-forms.

- [Standard fields](crispy-forms/standard-fields.md) is every field Django
  ships, on one plain form.
- [Special fields](crispy-forms/special-fields/index.md) are fields drawn as
  something a plain form cannot give you, such as a toggle or a rating.
- [Modifiers](crispy-forms/modifiers/index.md) change a field that already
  exists: its size, its colour, its state.
- [Layout objects](crispy-forms/layout-objects/index.md) arrange fields, or put
  something between them that is not a field.
- [Formsets](crispy-forms/formsets/index.md) draw many forms at once.

**Custom fields** and **Custom widgets** are the form fields and widgets the
package ships. **Third-party support** shows popular Django packages drawn by
the pack.

```{toctree}
:caption: Crispy forms
:hidden:

crispy-forms/standard-fields
crispy-forms/special-fields/index
crispy-forms/modifiers/index
crispy-forms/layout-objects/index
crispy-forms/formsets/index
```

```{toctree}
:caption: Custom fields
:hidden:

custom-fields/partial-date-field
custom-fields/coordinate-fields
```

```{toctree}
:caption: Custom widgets
:hidden:

custom-widgets/partial-date-widgets
custom-widgets/input-masks
custom-widgets/tom-select
custom-widgets/image-input
```

```{toctree}
:caption: Third-party support
:hidden:

third-party-support/django-tomselect
third-party-support/django-countries
```
