# django-mvp-forms

A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects.

> **Status: pre-release.** The template pack draws text-like fields so far, and nothing is published to PyPI.

## Why

[django-mvp](https://github.com/django-mvp/django-mvp) renders its pages with [daisyUI](https://daisyui.com), and its forms with [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms). That leaves a gap: a crispy template pack that produces daisyUI markup and covers everything crispy-forms can lay out.

Two packs exist. [crispy-tailwind](https://github.com/django-crispy-forms/crispy-tailwind) emits plain Tailwind utility classes, not daisyUI components, and has had no release since February 2024. [crispy-daisyui](https://github.com/fabge/crispy-daisyui) is a fork of it that its author describes as modified just enough for their own needs, with no test suite. Neither is a base we want django-mvp's form rendering to rest on, so this package provides a pack that is maintained alongside django-mvp and tested against the Django and daisyUI versions it supports.

## Scope & philosophy

The package covers how a form is drawn and what goes in it:

- a complete daisyUI template pack for django-crispy-forms, covering every layout object it ships
- formsets, drawn when one is handed to the pack
- form fields and widgets that have proved useful across django-mvp projects

It stays out of everything around the form. Form views, adding and removing formset rows, and form page templates belong to django-mvp. There are no models, no URLs and no migrations here.

The pack's templates are plain Django templates. They do not use [django-cotton](https://github.com/wrabit/django-cotton) or daisy-cotton, so the pack works in any daisyUI project, with or without django-mvp. For the same reason this package does not depend on django-mvp. The dependency runs the other way.

Fields and widgets are collected as real projects need them. They are not planned ahead and do not appear on the roadmap, so the set grows unevenly and that is intended. The package is complete without any of them, and each one has to fit the pack without changing what the pack promises.

Widgets from popular third-party Django packages may get templates here so they sit properly in a daisyUI form. Which packages are supported is the maintainers' call, and none of them becomes a dependency.

When two reasonable designs conflict, stock daisyUI markup wins over custom styling, and matching crispy-forms' documented behaviour wins over inventing a new one.

## Installation

Nothing is published to PyPI yet, so install it from GitHub:

```bash
pip install git+https://github.com/django-mvp/django-mvp-forms
```

Then add it to `INSTALLED_APPS` alongside crispy-forms:

```python
INSTALLED_APPS = [
    # ...
    "crispy_forms",
    "mvp_forms",
]
```

The host project supplies daisyUI itself. This package ships markup, not a stylesheet. Pages that draw these forms must load daisyUI 5. Its CDN build needs no build step, so daisyUI's own CDN install in the page's `<head>` is enough:

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

A host project with its own Tailwind build has to make that build produce the classes the pack writes. Tailwind only generates a class it finds in the files it scans, so point it at the whole installed `mvp_forms` package: the classes are written in its templates and in its template tags.

## Quickstart

Select the pack in your settings. Both settings are needed: crispy-forms refuses a pack that is not allowed.

```python
CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]
CRISPY_TEMPLATE_PACK = "daisyui"
```

Write a form as you always have, and a view that hands it to a template:

```python
from django import forms
from django.shortcuts import render


class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


def contact(request):
    form = ContactForm(request.POST or None)
    return render(request, "contact.html", {"form": form})
```

Draw it in a template of a page that loads daisyUI:

```django
{% load crispy_forms_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  </head>
  <body>
    <form method="post">
      {% csrf_token %}
      {{ form|crispy }}
      <button type="submit" class="btn btn-primary">Send</button>
    </form>
  </body>
</html>
```

## Public surface

### Template pack `daisyui`

Selected with the two settings above. Every field is drawn inside a daisyUI `fieldset` with a label and its input.

The label is tied to the input, and a required field's label carries a marker that assistive technology skips. The input announces itself as required, as invalid when it has errors, and by its help text and error messages as its description. Label, help text and errors are escaped unless you mark them safe. Every id the pack writes is built from the form's `auto_id`, so forms with different prefixes never share one, and a form with `auto_id=False` gets none.

These inputs are drawn as daisyUI components, whichever way crispy-forms is asked to draw the form (`|crispy`, `{% crispy form %}` or `|as_crispy_field`):

- text, email, URL, number, password, date, time and date-time inputs, as `input`
- textareas, as `textarea`

Each of them fills the width of its field. daisyUI gives inputs a fixed width and has no modifier for a full-width one, so the pack adds Tailwind's `w-full`, the one utility it writes. A width class of your own on the widget, such as `w-40`, replaces it. On a page with no Tailwind at all the class does nothing and the inputs keep daisyUI's width.

Errors that belong to the form as a whole are drawn once, in an element with `role="alert"` ahead of the fields. A form with none draws no such element, and `{{ form|as_crispy_errors }}` draws the same element on its own.

With `{% crispy form %}` the pack follows these `FormHelper` settings:

- `form_tag`, `form_method`, `form_action`, `form_id`, `form_class` and `attrs` for the `<form>` element, which is `multipart` when the form needs it, and `disable_csrf` for its CSRF token, drawn for a post form
- `form_show_labels`: with labels off, each input is named by an `aria-label` holding the label's text, unless the widget sets its own
- `form_show_errors`: with errors off, no field error, no form-wide error and no error styling is drawn, and an input's description names only what is on the page
- `label_class` on each label, and `field_class` on an element wrapped around each input
- `form_error_title` inside the form-wide error element, and `include_media` for the form's media

`help_text_inline` and `error_text_inline` are ignored.

A class, placeholder, input type or row count you give a widget is kept. The pack never changes an input's type, so a date field is a text input unless its widget says otherwise. Fields with any other widget are still drawn in place, without a daisyUI class.

### Layout objects

The layout objects of django-crispy-forms are drawn as daisyUI too, so a form with a `Layout` needs nothing more than the pack selected. Import them from django-crispy-forms as its documentation says. This package adds no layout classes of its own:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Layout, Row
from django import forms


class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "Data for {{ user.username }}",
                Row(Column("first_name"), Column("last_name")),
                Div("email", css_id="contact"),
                css_class="profile",
            )
        )
```

Build the layout in the form's `__init__`, as above, so each form has its own. django-crispy-forms stores some rendered values back on its layout objects, so one shared between forms or kept on a class is drawn wrongly the second time.

- `Fieldset` is a daisyUI `fieldset` and its legend is a `fieldset-legend`. An empty legend draws no `<legend>`. The legend is rendered as a template against the page's context, as in the example, and markup in a context value is escaped.
- `Div` is a plain `<div>` around its fields.
- `Row` is a `<div>` that sets its columns side by side on a wide page and stacks them on a narrow one. It uses Tailwind layout utilities, because daisyUI has no component for a row.
- `Column` is a `<div>` that takes an equal share of its row. Outside a `Row` it is a plain `<div>`. A `Row` that holds fields directly draws them in order, without columns.

Each of them holds its fields and further layout objects in the order the layout gives, and can be nested to any depth. The `css_id`, `css_class` and attributes you give one are kept on its element, and your classes come after the pack's. Every field inside is still drawn with its own label, help text and errors. An empty container is drawn, and `template=` draws a container with a template of your own.

Buttons are drawn as daisyUI buttons. `FormActions` and `StrictButton` come from `crispy_forms.bootstrap`, where django-crispy-forms keeps them:

```python
from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.layout import Button, ButtonHolder, Reset, Submit

FormActions(
    Submit("save", "Save"),
    Reset("clear", "Clear"),
    Button("help", "Help"),
    StrictButton("Save for {{ user.username }}", type="submit", css_class="btn-accent"),
)
```

- `Submit`, `Reset` and `Button` are `<input>` elements of type `submit`, `reset` and `button`, each carrying `btn` (a `Submit` also `btn-primary`). Their value can read the page's context, as in `Submit("save", "Save {{ user.username }}")`. Pass `disabled=True` to draw one disabled.
- `StrictButton` is a `<button>` of type `button` unless you give another `type=`. Its content may hold markup and context values; the values are escaped.
- `ButtonHolder` and `FormActions` hold buttons side by side in one container, wrapping on a narrow page. `ButtonHolder` accepts an id and classes; `FormActions` also keeps any other attributes.
- A button added to the form helper with `self.helper.add_input(Submit("save", "Save"))` is drawn after the fields, inside the form element, in a container of its own. It is the same element as the same button in a layout. With `form_tag` off, the buttons of a layout are still drawn.

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-forms/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-forms/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

The demo has two pages that draw the same forms: every text input kind in each of
five states (empty, holding a value, required, with help text, with an error),
and a form to submit that comes back with a field error and a form-wide error.

- `/text-inputs/` is the page inside the django-mvp shell, reached from its sidebar.
- `/text-inputs/standalone/` is the same page as a host project with neither
  django-mvp nor Cotton would have it, styled by daisyUI's CDN build alone.

Two more pages draw the layout objects, a form to submit and a form that already
fails, so an error inside a fieldset, a row and a column can be seen:

- `/layout-objects/` is the page inside the django-mvp shell, reached from its sidebar.
- `/layout-objects/standalone/` is the same page styled by daisyUI's CDN build alone.

Both pages end the form to submit in a `FormActions` holding a `Submit`, a `Reset`, a `Button` and a `StrictButton`, and add a form whose buttons were added to its helper and a small layout that puts two fields straight in a `Row` above a `ButtonHolder`.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-forms/blob/main/LICENSE).
