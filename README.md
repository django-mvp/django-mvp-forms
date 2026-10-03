# django-mvp-forms

A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects.

> **Status: pre-release.** The template pack draws text-like fields, choices, booleans, file inputs and hidden inputs, every layout object django-crispy-forms ships, including the nine that decorate a field and `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, and formsets drawn stacked or as a table. Nothing is published to PyPI.

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

Selected with the two settings above. Every field is drawn inside a daisyUI `fieldset`. A field of one input has a label and its input, except a single checkbox, whose label holds the checkbox and is tied to it by `for`. A field of several inputs that share one label, such as a radio group, a checkbox group or a date drawn as three selects, is drawn as a `<fieldset>` with a `<legend>`, which is described by the field's help text and errors, and which is named by an `aria-label` when the form draws no labels.

The pack draws radio and checkbox groups, a date's selects and a clearable file input from templates of its own, which the form renderer has to load. Django's default renderer and `TemplatesSetting` both do. A widget subclass that names a template of its own is drawn by that template, with the daisyUI class only.

The label is tied to the input, and a required field's label carries a marker that assistive technology skips. The input announces itself as required, as invalid when it has errors, and by its help text and error messages as its description. Label, help text and errors are escaped unless you mark them safe. Every id the pack writes is built from the form's `auto_id`, so forms with different prefixes never share one, and a form with `auto_id=False` gets none.

These inputs are drawn as daisyUI components, whichever way crispy-forms is asked to draw the form (`|crispy`, `{% crispy form %}` or `|as_crispy_field`):

- text, email, URL, number, password, date, time and date-time inputs, as `input`
- textareas, as `textarea`
- `Select`, `SelectMultiple` and `NullBooleanSelect`, and selects with named groups, as `select`, and the three selects of a date drawn by `SelectDateWidget`, each named by an `aria-label` of Year, Month or Day unless the widget carries an `aria-label` of its own. The part is read from the end of the select's name, so a subclass that renames `year_field`, `month_field` or `day_field` names its own selects
- `CheckboxInput`, as `checkbox`, inside its own label, with `checkbox-error` when invalid
- `RadioSelect`, as a group of `radio` inputs, and `CheckboxSelectMultiple`, as a group of `checkbox` inputs: each option is an input inside a label of its own, tied to it by `for`, with `radio-error` or `checkbox-error` when invalid. Choices with named groups sit under their name in a nested `<fieldset>`, and an attribute a widget sets on one option stays on that option. A required checkbox group does not mark its options `required`, since that would demand all of them
- `FileInput` and `ClearableFileInput`, as `file-input`, with `file-input-error` when invalid. A `ClearableFileInput` whose field holds a file shows a link to it, and, when the field is optional, a removal checkbox in a label of its own; a required field offers no removal and its input is not `required`, so it can be submitted without choosing another file. A widget that allows several files keeps `multiple`
- `HiddenInput` and `MultipleHiddenInput`, as `<input type="hidden">` and nothing around it, which is described below
- the parts of a `MultiWidget`, each as the component of its own kind, so a `SplitDateTimeField` is two `input` elements. A part that is hidden has no class

Each of them but the checkbox, the radio and the hidden input fills the width of its field. daisyUI gives inputs a fixed width and has no modifier for a full-width one, so the pack adds Tailwind's `w-full`. A width class of your own on the widget, such as `w-40`, replaces it. On a page with no Tailwind at all the class does nothing and the inputs keep daisyUI's width.

Errors that belong to the form as a whole are drawn once, in an element with `role="alert"` ahead of the fields. A form with none draws no such element, and `{{ form|as_crispy_errors }}` draws the same element on its own.

A hidden field is drawn as its `<input type="hidden">` alone, or one per value for a `MultipleHiddenInput`, with no frame, label, help text or error element. Nobody sees a hidden input, so an error on one joins the form-wide errors in that same element, worded by Django as `(Hidden field name) message` and escaped. With errors off it is not drawn.

With `{% crispy form %}` the pack follows these `FormHelper` settings:

- `form_tag`, `form_method`, `form_action`, `form_id`, `form_class` and `attrs` for the `<form>` element, which is `multipart` when the form needs it, and `disable_csrf` for its CSRF token, drawn for a post form
- `form_show_labels`: with labels off, each input is named by an `aria-label` holding the label's text, unless the widget sets its own
- `form_show_errors`: with errors off, no field error, no form-wide error and no error styling is drawn, and an input's description names only what is on the page
- `label_class` on each label, and `field_class` on an element wrapped around each input
- `form_error_title` inside the form-wide error element, and `include_media` for the form's media

`help_text_inline` and `error_text_inline` are ignored.

A class, placeholder, input type or row count you give a widget is kept. The pack never changes an input's type, so a date field is a text input unless its widget says otherwise. Fields with any other widget are still drawn in place, without a daisyUI class, except that the parts of a multi-widget are drawn as the inputs they are (see [A multi-widget field](#a-multi-widget-field)).

### Disabled and read-only fields

The pack adds no class for either state, and no attribute either, except in one case: `UneditableField` writes `disabled` (see [An uneditable field](#an-uneditable-field)). A field with `disabled=True` is drawn by Django with `disabled` on its input, on every option of a radio or checkbox group, and on the removal checkbox of a file field that holds a file, and daisyUI draws its disabled look from that attribute for every component the pack uses. A disabled field still shows its value, except a password input, which never draws one. The browser does not submit a disabled input, and Django takes the field's initial value instead.

Read-only is the browser's and exists only on text inputs and textareas. Set `readonly` on the widget, `forms.TextInput(attrs={"readonly": True})`, and it reaches the input unchanged, with the input's name and value, so the browser still submits it. The attribute does nothing on a select, a checkbox, a radio or a file input, and the pack does not try to make it: use `disabled` for those.

### Layout objects

The layout objects of django-crispy-forms are drawn as daisyUI too, so a form with a `Layout` needs nothing more than the pack selected. Import them from django-crispy-forms as its documentation says. This package adds no layout classes of its own. `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, all from `crispy_forms.bootstrap`, are supported along with the structural and button objects below:

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
- `Column` is a `<div>` that takes an equal share of its row. Outside a `Row` it carries the same two layout classes, which do nothing unless its parent is a flex container. A `Row` that holds fields directly draws them in order, without columns.
- `MultiField` is a daisyUI `fieldset` whose `<legend>` is the label you give it, holding its fields in order. Each field is still drawn in its own frame, with its own label, help text and errors, so an error sits beside the field it belongs to and not at the top of the group. The label is drawn as you write it, markup included. Unlike a `Fieldset` legend it is not rendered as a template, so it cannot read the page's context. `css_id`, `css_class`, `label_class` and attributes are kept on the group, and the class names django-crispy-forms writes for other template packs, listed under the buttons below, are not drawn.

Each of the five holds its fields and further layout objects in the order the layout gives, and can be nested to any depth. The `css_id`, `css_class` and attributes you give one are kept on its element, and your classes come after the pack's. Every field inside is still drawn with its own label, help text and errors. An empty container is drawn, and `template=` draws a container with a template of your own.

Tabs are daisyUI's `tabs`. `TabHolder` and `Tab` come from `crispy_forms.bootstrap`, where django-crispy-forms keeps them:

```python
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class AccountForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab("Name", "first_name", "last_name"),
                Tab("Contact", "email"),
            )
        )
```

- Each `Tab` is one daisyUI `tab` radio, named for assistive technology by the tab's name, followed by its `tab-content` element holding the tab's fields. The radios of one `TabHolder` form one group, so the Tab key reaches the tabs and the arrow keys move between them. No script is involved.
- Exactly one tab is open. It is the first tab that holds a field with an error, including a hidden field, and with no error it is the first tab, also when you gave the first `Tab` `active=True` or `active=False`. A form-wide error alone opens the first tab.
- A tab's radio carries `form=""`, so it belongs to no form and is never submitted: the browser submits only the form's own fields.
- Each holder has a group name of its own, so two holders in one form, a holder in each of two forms on a page and a holder inside a tab do not open each other's tabs. A `Tab` is drawn only inside a `TabHolder`: on its own it has no group and no tab is open.
- The `css_id`, `css_class` and attributes you give a `TabHolder` are kept on its element, and those you give a `Tab` on its `tab-content` element. A `Tab` takes its id from its name unless you give one. The name is escaped. `active` and `tab-pane`, which django-crispy-forms writes for other template packs, are not drawn.
- A browser will not submit a form whose empty required input is in a tab that is not open. Set `self.helper.attrs = {"novalidate": True}` to let the server answer and open the tab that holds the error.

An accordion is a stack of daisyUI `collapse` elements. `Accordion` and `AccordionGroup` come from `crispy_forms.bootstrap` too:

```python
from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup("Name", "first_name", "last_name"),
                AccordionGroup("Contact", "email", active=True),
            )
        )
```

- Each `AccordionGroup` is a `<details class="collapse">` holding a `<summary class="collapse-title">` with the group's name and a `collapse-content` element with the group's fields. `<details>` and `<summary>` are the browser's own disclosure, so the keyboard and assistive technology work with no script and the accordion draws no input or button of its own.
- Each group opens and closes on its own: opening one does not close another, and no group is given a `name`.
- Which groups are open is decided by django-crispy-forms. Unbound, the first group is open, unless you gave it `active=False`, and a later group you gave `active=True` is open as well. With an error, the first group that holds a field with an error, including a hidden field, is open. A form-wide error alone leaves the first group open.
- An `Accordion` inside a `Tab` that holds a field with an error opens the tab and the group.
- The `css_id`, `css_class` and attributes you give an `Accordion` are kept on its element, and those you give an `AccordionGroup` on its `<details>`. The group's name is escaped. An `Accordion` you give no id gets one from django-crispy-forms.
- A browser will not submit a form whose empty required input is in a group that is closed. Set `self.helper.attrs = {"novalidate": True}` to let the server answer and open the group that holds the error.

A modal is a daisyUI `modal`, drawn as a `<dialog>`. `Modal` comes from `crispy_forms.bootstrap` too:

```python
from crispy_forms.bootstrap import Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            "email",
            Modal(
                "first_name",
                "last_name",
                css_id="name-modal",
                title="Your name",
                title_id="name-modal-title",
            ),
        )
```

- The modal is a `<dialog class="modal">` with the `css_id` you give, holding a `modal-box` with the title, the fields and one close button. The dialog is where the layout puts it, inside the form element, so its fields are submitted with the rest of the form. Give two modals two ids and two `title_id` values: the title's id is built from `title_id`, so two modals left on the default share one title id and the second is named by the first one's title.
- The pack draws nothing that opens the modal. Your page does, by the modal's id. A button outside the dialog that calls `showModal()` on it is enough: `<button type="button" onclick="document.getElementById('name-modal').showModal()">Edit name</button>`. A `<dialog>` opened this way is shown above the page, can be closed with the Escape key and returns focus to the button.
- The close button is a `<button type="button">`, so it never submits the form, and closing the modal leaves what was typed in its fields as it was. The modal holds no submit button: submit with a button of the form.
- The title is an `<h3>` with the id `<title_id>-label`, and the dialog's `aria-labelledby` names it, so it is the dialog's accessible name. The title is escaped. `title_class` is added to the title, which the pack gives no class of its own, and `title_id` defaults to `modal_title_id`.
- The modal is drawn open when a field inside it has an error, including inside a `Tab` or an `AccordionGroup` in the modal, and then the tab and the group that hold the error are open too. It opens even when the helper's `form_show_errors` is off. A modal that holds only an `HTML` object never opens, and an error in a field outside it does not open it. A modal drawn open this way takes the keyboard focus when the page arrives and is closed with its close button. It was not opened with `showModal()`, so the Escape key does not close it and the page behind it can still be reached with the Tab key.
- The `css_class` and attributes you give a `Modal` are kept on its `<dialog>`. A `Modal` you give no id gets `modal_id` from django-crispy-forms, so give each its own.
- A browser will not submit a form whose empty required input is in a closed modal. Set `self.helper.attrs = {"novalidate": True}` to let the server answer and open the modal that holds the error.

An alert is a daisyUI `alert`. `Alert` comes from `crispy_forms.bootstrap` too:

```python
from crispy_forms.bootstrap import Alert
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            "first_name",
            Alert(
                "<strong>Check the spelling.</strong> Names are printed as written.",
                css_class="alert-warning",
                css_id="name-note",
            ),
            "last_name",
        )
```

- The alert is a `<div role="alert" class="alert">` where the layout puts it, holding its content in a `<span>`. It is drawn again when the form is bound, and two alerts in one form are each drawn.
- Colour it with a daisyUI modifier in `css_class`, as above: `alert-info`, `alert-success`, `alert-warning`, `alert-error`, `alert-soft`, `alert-outline` or `alert-dash`. The `css_id` and attributes you give are kept on the alert, and your classes come after the pack's.
- A dismiss button is drawn by default: a `<button type="button">` named by an `aria-label`, which removes the alert from the page. It never submits the form. A dismissal is not remembered, so the alert is back the next time the page is drawn. Pass `dismiss=False` to draw the alert with no button.
- `block=True` is accepted and changes nothing, because daisyUI has no counterpart to the Bootstrap class it adds. `alert-block` is never drawn.
- The content is trusted. It is written into the page as markup, as django-crispy-forms documents, so a tag in it is a tag in the page, and a context value in it is not filled in. Anything a person typed must be escaped before it is put there, for example with `django.utils.html.escape` or `format_html`.

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

- `Submit`, `Reset` and `Button` are `<input>` elements of type `submit`, `reset` and `button`, each carrying `btn` (a `Submit` also `btn-primary`). Their value can read the page's context, as in `Submit("save", "Save {{ user.username }}")`. Pass `disabled=True` to draw one disabled. Seven class names are never drawn, even when you give them yourself, because django-crispy-forms writes them for other template packs: `btn-inverse`, `ctrlHolder`, `blockLabel`, `error`, `tab-pane`, `active` and `alert-block`. Every one of them is dropped from the `css_class` of these buttons, of a `MultiField` (and its `label_class`), of a `Tab` and of an `Alert`, so a class of your own called `active` on any of them is not drawn either.
- `StrictButton` is a `<button>` of type `button` unless you give another `type=`. Its content may hold markup and context values; the values are escaped.
- `ButtonHolder` and `FormActions` hold buttons side by side in one container, wrapping on a narrow page. `ButtonHolder` accepts an id and classes; `FormActions` also keeps any other attributes.
- A button added to the form helper with `self.helper.add_input(Submit("save", "Save"))` is drawn after the fields, inside the form element, in a container of its own. It is the same element as the same button in a layout, with two limits that are django-crispy-forms' own: the value of a `Submit`, `Reset` or `Button` added this way is drawn as written and is not rendered as a template, and `template=` applies to a button in a layout only. A `StrictButton` added to the helper is drawn as it is in a layout. A `Hidden` added to the helper is drawn inside the form, outside the container of the buttons. With `form_tag` off, the buttons of a layout are still drawn.

Raw markup and hidden values go in a layout as they do in django-crispy-forms:

```python
from crispy_forms.layout import HTML, Hidden

Layout(
    "first_name",
    HTML("<p>Prepared for {{ user.username }}.</p>"),
    "last_name",
    Hidden("step", "details"),
)
```

- `HTML` is drawn where you put it, between fields or inside a `Fieldset`, `Column`, `ButtonHolder` or `FormActions`. Your markup is kept as written, and a context value in it, as in the example, is filled in with any markup in the value escaped.
- `Hidden` is an `<input type="hidden">` with the name and value you give, inside the form element. It carries no class and no id, so `css_id` and `css_class` do nothing on it. Pass `id=` or any other attribute as a keyword argument to add it.

### Layout objects that decorate a field

Some layout objects of django-crispy-forms draw one field with something added to it. The first three attach text to an input. `PrependedText`, `AppendedText` and `PrependedAppendedText` come from `crispy_forms.bootstrap`:

```python
from crispy_forms.bootstrap import AppendedText, PrependedAppendedText, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class PriceForm(forms.Form):
    amount = forms.CharField()
    weight = forms.CharField()
    budget = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            PrependedText("amount", "$"),
            AppendedText("weight", "kg"),
            PrependedAppendedText("budget", "$", ".00"),
        )
```

- The field is drawn in its usual frame, with its label, help text and errors, and its input sits in one daisyUI `input` wrapper, which is a `<label>`, beside a `<span class="label">` for each text that is set: before the input for the prepended text and after it for the appended one. The input inside has no `input` class of its own, because the wrapper has it. On a select the wrapper is `select` instead. Because the wrapper is a label, assistive technology announces the text as part of the field's name. That holds while the form draws labels: with `form_show_labels` off the input is named by an `aria-label` holding the field's label alone, which takes the place of every label, so put the unit in the field's label if it has to be announced.
- A text that is an empty string or `None` draws nothing, and a field with neither text is drawn as it is without the layout object. The error modifier, `input-error` or `select-error`, is on the wrapper, and the input is marked invalid as before.
- The text is markup. It is written into the page as it is, so `"<b>US</b>"` is drawn as a bold element and a currency symbol such as `&euro;` works. When you build it from anything a person typed, escape it first, for example with `django.utils.html.escape` or `format_html`. The label, the help text, the errors and the value stay escaped.
- On a checkbox, a radio group, a date drawn as three selects, a textarea or a file input there is nowhere to attach the text, so the field is drawn exactly as it is without the layout object. A hidden field is drawn as its hidden input alone.
- `css_class` and extra attributes go to the input, as they do for `Field`. `template=` draws your own template. `input_size` and `active` are accepted and do nothing.
- The wrapper takes the size of the field. With a size stated for the form, or with a `Choice` around the layout object, the size class (`input-lg`, or `select-lg` on a select) is on the wrapper and the input inside carries none, so the text and the input read as one control.
- `wrapper_class` now works on any field, not only on these three: it is added to the class of the frame's outer element, whether that is a `<div>` or a `<fieldset>`. `Field("name", wrapper_class="wide")` draws `class="fieldset wide"`. The one place it does not reach is a `Field` given as the first item of `FieldWithButtons`, because django-crispy-forms passes on only that `Field`'s attributes.

#### Choices in a line

`InlineRadios` and `InlineCheckboxes` come from `crispy_forms.bootstrap`. They draw a radio group or a checkbox group with its options along a line instead of one under another:

```python
from crispy_forms.bootstrap import InlineCheckboxes, InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class SurveyForm(forms.Form):
    size = forms.ChoiceField(
        choices=[("s", "Small"), ("m", "Medium"), ("l", "Large")],
        widget=forms.RadioSelect,
    )
    extras = forms.MultipleChoiceField(
        choices=[("a", "Ketchup"), ("b", "Mustard")],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(InlineRadios("size"), InlineCheckboxes("extras"))
```

- Each option is a `radio` or a `checkbox` input inside a `<label>` of its own, tied to it by `for`, exactly as in a group drawn without the layout object. The options sit in a `<div>` that lets them run along a line and wrap onto the next one when the group has many options or long labels.
- The frame is the group's usual one: a `<fieldset>` with a `<legend>`, the required marker, the help text and the errors, described by the help text and the error. Initial and submitted values check the same options, disabled options stay disabled, choices with named groups sit under their names, and `cleaned_data` is what the group without the layout object gives.
- A widget that names a template or an option template of its own is drawn by it. A field with no choices is drawn with its frame and no option, and a field that is not a group, such as a text field, is drawn as it is without the layout object.
- `css_class` and extra attributes go to every option, as they do for `Field`. `wrapper_class` reaches the frame's outer element and `template=` draws your own template.

#### A field with buttons

`FieldWithButtons` comes from `crispy_forms.bootstrap`. It draws one field with any number of buttons joined to it, such as a search box with a button beside it. The first item is the field, as a name or as a `Field`, and the rest are the buttons:

```python
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Field, Layout
from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            FieldWithButtons(
                Field("query", css_class="mine"),
                StrictButton("Go", type="submit", name="go"),
                Button("clear", "Clear"),
            ),
        )
```

- The field is drawn in its usual frame, with its label, help text and errors. Inside it one daisyUI `join` element holds the input, which carries `join-item`, and then every button in the order you gave them. The buttons are the ones `StrictButton`, `Submit` and `Button` draw anywhere else, and each is drawn once, so a `Submit` keeps its name and value and a button whose content holds markup or `{{ ... }}` from a value is escaped, never evaluated.
- With no buttons the group holds the input alone. A failing field has its error modifier on the input, which is marked invalid and described by the error element in the frame.
- A `Field` as the first item gives its class and attributes to the input. `css_id`, `css_class` and any other attribute go to the `join` element, and a class written for another template pack is dropped from it. `template=` draws your own template. `input_size` is accepted and does nothing.
- On a select the group is drawn as it is on an input. On a checkbox or a radio group both the field and the buttons are drawn, and no option of a group carries `join-item`. A hidden field is drawn as its hidden input alone.
- The input and the buttons take the same size. State it for the whole form, or put a `Choice` around the layout object: `Choice(FieldWithButtons("query", StrictButton("Go")), size="lg")` gives the input `input-lg` and the button `btn-lg`. A size stated for one field by name, `FormChoices(fields={"query": Choice(size="lg")})`, reaches the input and cannot reach its buttons, which django-crispy-forms draws before the field, so for a field with buttons state the size with `Choice` around the `FieldWithButtons` or for the whole form.
- Give a button `css_class="join-item"` to close the doubled border where the joined parts meet.
- A `Choice` around the layout object is stated for the input and for the buttons alike, so state only what both have. A size is safe. A variant that only buttons have, such as `outline`, raises `InvalidChoice` for the input.

#### An uneditable field

`UneditableField` comes from `crispy_forms.bootstrap`. It draws one field with its current value shown and the input disabled, such as an account number on a profile form:

```python
from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class ProfileForm(forms.Form):
    account = forms.CharField(initial="AC-1001", help_text="Issued once")
    reference = forms.CharField(initial="R-7", disabled=True)
    nickname = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            UneditableField("account"),
            UneditableField("reference"),
            "nickname",
        )
```

- The field is drawn in its usual frame, with its label, help text and errors, and its input keeps its component class (`input`, `select`, `textarea`, `checkbox`) and shows the field's value. A field with no value is drawn empty. The value is escaped, as it is for any field.
- The input carries the `disabled` attribute and no class for it: daisyUI draws the disabled look from the attribute. A select, a checkbox and a textarea are disabled the same way, and every option of a radio group or a checkbox group is. The form's own field and widget are not changed, so the same field drawn without the layout object is editable.
- **The browser does not submit a disabled input.** Wrapping a field in `UneditableField` does not make Django ignore what comes back, so a required field left out of the submitted data fails with the `required` code. A form that needs the value kept declares the field disabled in the form class, `forms.CharField(initial="R-7", disabled=True)` as `reference` does above, and Django then uses the initial value whatever is submitted.
- `uneditable-input`, the class django-crispy-forms writes for other template packs, is not drawn on an input a person can see. It is the only name dropped from an input's own classes, so a class of yours called `active` or `error` on an input is still drawn.
- `css_class` and extra attributes go to the input, as they do for `Field`. `wrapper_class` reaches the frame's outer element and `template=` draws your own template.

#### An inline field

`InlineField` comes from `crispy_forms.bootstrap`. It draws one field with no visible label, for a form that sits in a line such as a search bar. The input is named by an `aria-label` and the label is offered as its placeholder:

```python
from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label="Search", help_text="Names and numbers")
    remember = forms.BooleanField(label="Remember me", required=False)
    note = forms.CharField(label="Note", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            InlineField("query"),
            InlineField("remember"),
            "note",
        )
```

- The frame holds no `<label>` for the field. The input has an `aria-label` equal to the field's label, and on a text input or a textarea a `placeholder` equal to it as well. A placeholder or an `aria-label` that the widget sets is kept. A label marked safe reaches both as plain text.
- The help text and the error element are still drawn, still described by the input, and a failing input has `aria-invalid` and its error modifier.
- A single checkbox keeps its `<label>`, with the checkbox inside it. A select and a radio group get no placeholder; a select is named by an `aria-label` and a group by an `aria-label` on its fieldset, without a legend.
- A field beside it that is not inline keeps its label. `css_class` and extra attributes go to the input, `wrapper_class` reaches the frame's outer element and `template=` draws your own template.

#### A multi-widget field

`MultiWidgetField` comes from `crispy_forms.layout`, not `crispy_forms.bootstrap`. It draws a field whose widget is several widgets, such as a `SplitDateTimeField`, and lets you give each part attributes of its own:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, MultiWidgetField
from django import forms


class EventForm(forms.Form):
    starts = forms.SplitDateTimeField(label="Starts", help_text="Local time")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            MultiWidgetField(
                "starts",
                attrs=({"placeholder": "2026-10-03"}, {"class": "mine"}),
            ),
        )
```

- `attrs` is a sequence with one set of attributes for each part, in order, or one set that goes on every part. A sequence shorter than the parts leaves the last parts with none, and raises nothing. A part given `{"type": "hidden"}` is drawn as a hidden input.
- Each part is drawn as the daisyUI component of its kind: the two parts of a split date and time are `input`, with `input-error` when the field fails, and a class of your own on a part is kept beside it. A size, a colour and a variant stated for the form, or with a `Choice` around the layout object, reach every part as they reach any input, and a failing field's parts have the error modifier and not the colour.
- The frame is one `<fieldset>` with one `<legend>`, one help text and one error element, and the fieldset is described by the help text and the error. Each part has an `aria-label`: Date and Time for a split date and time, and the field's label for the parts of any other multi-widget. An `aria-label` you give a part is kept.
- A `SplitDateTimeField` with no layout object is drawn the same way. A split field whose widget is hidden is drawn as hidden inputs and nothing around them. On a field with one widget, `MultiWidgetField` draws the field with the attributes.
- The form's own widget and its parts are not changed: the classes and names are written on a copy for each render, so drawing a form twice gives the same markup. `wrapper_class` reaches the frame's outer element and `template=` draws your own template.
- Do not make a part of a `SplitDateTimeField` hidden: the hidden widget of that field is itself a multi-widget, and validating the form then fails. To hide the whole field, give it `widget=forms.SplitHiddenDateTimeWidget`.

### Size, colour and variant

State a size, a colour and a variant once, in Python, and the pack adds daisyUI's modifier for each to every input it draws for the form. You write no class on any widget. The statement is a `FormChoices`, set as the `daisyui` attribute of the form's helper:

```python
from crispy_forms.helper import FormHelper
from django import forms
from mvp_forms.choices import Choice, FormChoices


class SettingsForm(forms.Form):
    name = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea)
    newsletter = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm",
            color="primary",
            variant="ghost",
            fields={"notes": Choice(color=None)},
        )
```

It takes effect with `{{ form|crispy }}` and with `{% crispy form %}`, whether or not the form has a layout, and wherever a field sits in one. Set it on the helper's instance, as above, and not as a class attribute of a `FormHelper` subclass: django-crispy-forms passes a helper's instance attributes on to the templates and leaves its class attributes behind, so a class attribute would not reach everything the pack draws.

The names are daisyUI's own, and nothing else is accepted. For inputs:

- size: `xs`, `sm`, `md`, `lg`, `xl`
- colour: `neutral`, `primary`, `secondary`, `accent`, `info`, `success`, `warning`, `error`
- variant: `ghost`, for text-like inputs, textareas, selects and file inputs

For buttons, the same sizes and colours and these variants:

- variant: `outline`, `dash`, `soft`, `ghost`, `link`

The classes the names mean are written out in the tables of `Modifiers`, in `mvp_forms.choices`, one for sizes, one for colours and one for variants. The keyword is spelt `color`, as daisyUI spells it. The three are independent: changing one leaves the other two as they were. Every one is optional, and a form that states nothing is drawn exactly as it was before.

- `fields` gives one field a `Choice` of its own, by the field's name. Each of size, colour and variant that the `Choice` states wins over the form's for that field, and each it leaves out, which is `INHERIT` and the default, falls back to the form's. A `Choice` also states a drawing for a boolean field, which the form has no statement of: see "Checkbox, toggle and switch" below. `None` is the pack's ordinary drawing, so `Choice(color=None)` undoes the form's colour for that field, as `notes` does above. `INHERIT` is the one value of the type `Inherit`.
- Every input of a field takes the choices: each option of a radio or checkbox group, each select of a date, and the removal checkbox of a file field that holds a file, which takes the size and the colour.
- A choice that one kind of input has no modifier for is passed over for that kind. `variant="ghost"` leaves a checkbox, a toggle and a radio as they are and draws the text input beside them in ghost.
- A name that is not in the lists above raises `InvalidChoice`, a `ValueError`, when the form is drawn. It carries the `kind`, the `value` and the names `allowed`.
- A field in error keeps its error modifier and is drawn without the chosen colour, so the error is the only colour it shows. Its size and variant still apply.
- Hidden inputs, labels, help text, error text and the `required`, `disabled` and `readonly` attributes are never changed, and classes you put on a widget are kept.
- The size reaches every button too, as `btn-sm` and the like. A colour or a variant for the form's buttons is stated apart from the inputs', as `button_color` and `button_variant`, so `color` and `variant` reach no button and the two never touch. Buttons are described below.

### One field's own choice

One field can state a size, a colour or a variant of its own, and a boolean field a drawing as well. There are two ways, and they combine.

In a layout, wrap the field in a `Choice`. It draws what it holds, with its choice in force for everything inside it:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row
from django import forms
from mvp_forms.choices import Choice, FormChoices


class SearchForm(forms.Form):
    search = forms.CharField()
    name = forms.CharField()
    city = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(size="sm", color="primary")
        self.helper.layout = Layout(
            Choice("search", size="lg"),
            Choice(Row(Column("name"), Column("city")), color=None),
            "notes",
        )
```

Here `search` is large and keeps the form's colour, `name` and `city` keep the form's size and lose its colour, and `notes` takes the form's choices. A `Choice` may hold a `Row`, a `Fieldset` or any other layout object, and a `Choice` inside a `Choice` is merged over the outer one, each of its four kinds on its own, so the inner one wins for what it states. You can also wrap fields already in a layout, with `helper["search"].wrap(Choice, size="lg")`.

For a form drawn without a layout, name the field in `FormChoices`, as `notes` was in the section above: `FormChoices(fields={"search": Choice(size="lg")})`. It works with `{{ form|crispy }}` and with `{% crispy form %}`, and changes no other field.

When both are given for a field, the `Choice` in the layout wins over the one in `fields`, which wins over the form's, for each of size, colour and variant on its own, and the drawing is taken from the first of the two that states one. What a `Choice` leaves out is inherited, and `None` is the pack's ordinary drawing: `Choice("notes", color=None)` undoes the form's colour for that field and keeps its size. A size, colour or variant that the field's input has no modifier for raises `InvalidChoice` when the form is drawn, because you asked for it by name. The form's own statement is passed over for such an input.

### Buttons

A `Submit`, `Reset`, `Button` or `StrictButton` takes the form's `size`, `button_color` and `button_variant`, in a layout and when added with `helper.add_input`. The names are the sizes and colours listed above and the variants `outline`, `dash`, `soft`, `ghost` and `link`. A choice is stated for one button by wrapping it in a `Choice`, as below, and for every button in the form by `size`, `button_color` and `button_variant` of `FormChoices`.

```python
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Reset, Submit
from django import forms
from mvp_forms.choices import Choice, FormChoices


class ConfirmForm(forms.Form):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm", button_color="neutral", button_variant="outline"
        )
        self.helper.layout = Layout(
            "name",
            Submit("save", "Save"),
            Reset("clear", "Clear"),
            Choice(StrictButton("Delete", type="submit"), color="error"),
        )
```

Here every button is small and outlined, `Delete` is in the error colour and the others are neutral, and the text input is small. Wrap one button in a `Choice` to give it a choice of its own: what the `Choice` states wins over the form's, what it leaves out is inherited, and `None` is the ordinary drawing. A `Choice` takes the same `color` and `variant` for a button as for a field, and the form's `button_color` and `button_variant` are the ones it is merged over.

- A `Submit` is drawn `btn-primary` unless a colour is stated for it, by `button_color` or by a `Choice`. Then only the colour you stated is written. A `btn-primary` you pass as `css_class` is kept.
- Your `css_class`, `css_id` and attributes are kept on every button, and a `Hidden` is never changed.
- The statement reaches a button as the context name `daisyui`, which django-crispy-forms copies from the helper, so it works under whatever name the page gives its form, and with `{% crispy form %}`. Buttons are drawn only by the tag: `{{ form|crispy }}` draws no layout and no helper.

### Checkbox, toggle and switch

A boolean field, which is any field whose widget is a `CheckboxInput` or a subclass of one, such as a `BooleanField`, is drawn as a checkbox. To draw it another way, state a `drawing` in a `Choice`, in a layout or by the field's name, the same two ways as a size or a colour:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from mvp_forms.choices import Choice, FormChoices


class SettingsForm(forms.Form):
    remember = forms.BooleanField(required=False)
    notify = forms.BooleanField(required=False)
    publish = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm", fields={"notify": Choice(drawing="toggle")}
        )
        self.helper.layout = Layout(
            "remember",
            "notify",
            Choice("publish", drawing="switch", color="primary"),
        )
```

Here `remember` is a checkbox, `notify` is a toggle and `publish` is a switch in the primary colour, all small. The three drawings are:

- `"checkbox"`, daisyUI's checkbox. It is what a boolean field is drawn as when no drawing is stated, and stating it changes nothing.
- `"toggle"`, daisyUI's toggle: the same checkbox input with the class `toggle` in place of `checkbox`.
- `"switch"`, daisyUI's toggle again, with `role="switch"` on the input, so assistive technology announces a switch and not a checkbox. daisyUI has no separate switch, so a toggle and a switch look the same. The role replaces a `role` written on the widget's own attributes.

Each is still one `<input type="checkbox">` with the field's name, inside the label a checkbox sits in, so a form posts and cleans to `True` and `False` exactly as it does with checkboxes. The pack adds no script. A bound or initial `True` is drawn checked in every drawing, and a field in error keeps an error modifier of its own, `toggle-error`, as a checkbox keeps `checkbox-error`. A toggle and a switch are never widened. A toggle and a switch keep what a checkbox has: the label is tied to the input, the help text and the errors describe it, a required field carries the required marker, and a disabled field is disabled.

- The drawing is stated one field at a time. `FormChoices` has no `drawing` of its own, so a form cannot say that all its boolean fields are toggles. Name each one in `fields`, or wrap it in a `Choice`.
- A `Choice` in a layout wins over the one in `fields`, and a `Choice` that leaves the drawing out takes the one around it. `None` is the ordinary drawing, so `Choice("remember", drawing=None)` undoes a drawing stated around it.
- A field that states no drawing is drawn exactly as it was before, whatever the other fields of the form state.
- Only a boolean field takes a drawing. A field that is a null-boolean select, a checkbox group, a text input or anything else that is not a `CheckboxInput` does not, and neither does a button.
- A hidden boolean field is a hidden input whatever is stated for it.
- A toggle and a switch take the form's size and colour, and the field's own, like any input: `toggle-sm` and `toggle-primary` for a toggle or a switch, where a checkbox takes `checkbox-sm` and `checkbox-primary`. They have no variant. A variant stated for the form is passed over for them and one stated on the field itself raises `InvalidChoice`, as for a checkbox. A field in error keeps `toggle-error` and is drawn without the colour.

A name that is not one of the three raises `InvalidChoice` with `kind="drawing"`, naming the field as `target`, with `checkbox`, `toggle` and `switch` as the names `allowed`. A drawing of any name, `checkbox` included, stated for a field that is not a boolean field, or around a button, raises the same error with nothing allowed. A `Choice` that holds fields states its drawing for each of them, so `Choice(Row("name", "agree"), drawing="toggle")` raises for a text input `name`. `None` and `INHERIT` state nothing and never raise. A drawing stated by name in `FormChoices(fields=...)` is checked when its field is drawn, so one for a field the layout leaves out is never looked at.

### What is refused and what is passed over

A name daisyUI does not have is refused when the form is drawn, never written as a class that does nothing. It raises `InvalidChoice`, a `ValueError` carrying `kind` (`"size"`, `"color"`, `"variant"` or `"drawing"`), the `value` you stated and the names `allowed`. It is raised for a choice stated for the form's inputs, for its buttons (`button_color` and `button_variant`), on one field by name, on one field with a `Choice` in a layout, and on one button. When it was stated on a field or a button, `target` names it: the field's name, or a button's name, or the content of a `StrictButton`. For a choice stated for the form, `target` is `None`. What is stated for the form is checked whenever a form is drawn, so `{{ form|crispy }}`, which draws no button, still reports a mistake in `button_color`.

A choice stated for the form that a kind of input has no modifier for is passed over, with no error: `variant="ghost"` leaves a checkbox, a toggle, a radio group and a checkbox group as they are and the rest take it. The same choice stated on one of those fields raises, and so does any choice stated on a field whose widget the pack does not draw as an input of its own, because you asked for it by name.

A name in `FormChoices(fields=...)` that is not a field of the form raises `UnknownField`, a `KeyError` whose `names` lists them, when a field of the form is drawn.

A `Choice` in a layout is checked against each field and button it holds, as a choice stated on each of them. `Choice(Row("name", "agree"), variant="ghost")` raises for a checkbox `agree`, which has no ghost, and a `Choice` holding a field and a button needs a variant both have. Size and colour apply to every kind, so a `Choice` that states only those can hold anything.

The `daisyui` attribute of the helper a form carries as `form.helper` must be a `FormChoices`: anything else, `None` included, raises `TypeError` when a field of the form is drawn. Leave the attribute off to state nothing. A page variable that happens to be called `daisyui` and is not a `FormChoices` is ignored, and so is such a value on a helper handed to the tag on its own, as `{% crispy form helper %}`, where the pack cannot tell it from the page's. Keep the statement on the helper the form carries: with `{% crispy form helper %}` the inputs still read `form.helper`, and the buttons only the helper that draws them.
### Formsets

A formset is drawn when you hand it to the pack, as a form is, and it needs no work per form. A plain formset, a model formset and an inline formset are all drawn the same way:

```django
{% load crispy_forms_tags %}

{% crispy formset %}
```

`{% crispy formset %}` follows the formset's helper, which is the `FormHelper` you give `{% crispy formset helper %}` or the one on the formset. `{{ formset|crispy }}` draws the forms and the management form with no `<form>` element around them and no helper. With no choice made, the formset is drawn stacked: every form one after another.

What is drawn:

- the management form, once, as its four hidden inputs, ahead of the forms
- each form in a `<div>` of its own that holds that form's fields and no other form's, with a daisyUI `divider` between one form and the next
- every hidden field of every form, such as a model formset's primary key or an inline formset's foreign key, inside its form's `<div>`
- each form's fields as the pack draws them in a single form, with the same label, required marker, help text, errors and input
- one `<form>` element around the whole formset, never one per form, unless the helper's `form_tag` is off, and the CSRF token once for a post form
- through `{% crispy formset %}`, the formset's media once, unless `include_media` is off, and the helper's buttons once, after the last form. `{{ formset|crispy }}` draws neither, as for a single form

A helper's layout is applied to each form. A form drawn through a layout shows the fields the layout names and its hidden fields, so the `DELETE` and `ORDER` fields that Django adds to a formset are drawn only when the layout names them.

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

helper = FormHelper()
helper.layout = Layout("name", "quantity", "DELETE")
helper.add_input(Submit("save", "Save"))
```

A layout that names `DELETE` or `ORDER` needs every form to have that field. With `can_delete_extra=False` the extra forms have no `DELETE` field, and django-crispy-forms raises for a field a form does not have while `DEBUG` is on. Leave `DELETE` out of the layout for such a formset, or draw it as a table.

The two templates are `daisyui/whole_uni_formset.html`, which `{% crispy formset %}` asks for, and `daisyui/uni_formset.html`, which `{{ formset|crispy }}` asks for and the first includes.

#### As a table

To draw the same formset as a table, set the helper's template. Nothing else changes, and `{% crispy formset helper %}` stays as it is:

```python
helper = FormHelper()
helper.template = "daisyui/table_inline_formset.html"
```

What is drawn:

- one daisyUI `table`, with a row for each form and a column for each visible field, in the form's own order, inside an element with Tailwind's `overflow-x-auto` so a wide table scrolls instead of widening the page
- a heading for each visible field, holding its label and, for a required field, the required marker
- each input named by an `aria-label` equal to its label, and described by its help text when it has any. A radio or checkbox group keeps its `<fieldset>`, which carries the `aria-label`
- every hidden field in the first cell of its form's row, with no heading and no cell of its own
- the management form, the `<form>` element, the CSRF token, the media and the helper's buttons as in the stacked layout
- no table at all for a formset with no forms, though the management form is still drawn so the formset can be posted back

A helper's layout is not applied in a table: every visible field of the form gets a column. The columns are the first form's visible fields and every form is taken to have the same ones. A form that lacks one of them has an empty cell there.

#### Errors

Every error is drawn once, next to what it belongs to, in both layouts:

- a field's error under its input, which the input's `aria-describedby` names
- a form's own errors, its form-wide errors and those of its hidden fields, in the form's own container when stacked, and in the first cell of the form's row in a table. The row's `aria-describedby` names them, and a row with none carries no `aria-describedby`
- errors that belong to the formset as a whole, such as a minimum or maximum number of forms, once in an element with `role="alert"` ahead of the forms, outside every form's container and above the table

`formset_error_title` is drawn at the top of the formset-wide element when the helper sets it. A formset with no such error draws no such element, and with `form_show_errors` off none of the three kinds is drawn. `{{ formset|as_crispy_errors }}` draws the formset-wide errors on their own, through `daisyui/errors_formset.html`.

#### Delete and order inputs

When a formset has `can_delete` or `can_order` on, each form's delete input is drawn as the pack's checkbox and its order input as the pack's number input, the same as a boolean or an integer field in a single form. In the table each has a column of its own, with a heading and an `aria-label`. What a posted form reports in `deleted_forms` and `ordered_forms` is Django's, read from the inputs as drawn.

A form that has no delete field, such as an extra form of a formset with `can_delete_extra=False`, leaves that cell empty, so every row has as many cells as there are headings. A form that was marked for deletion and is drawn again after a failed post keeps its delete input ticked.

A form marked for deletion is left out of the formset's validation by Django, but it still holds its own field errors, and they are drawn with it when the page comes back.

The pack draws a formset and nothing around it. It draws no empty form to copy, adds no script, and has no view: adding and removing rows in the browser, handling the post and saving belong to django-mvp or to your own code.

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

The demo has two pairs of pages, and each pair draws the same forms. One pair
shows every text input kind in each of five states (empty, holding a value,
required, with help text, with an error), and a form to submit that comes back
with a field error and a form-wide error. The other shows every select, boolean,
radio and checkbox group, file and hidden input in those five states and a sixth,
disabled, with a text input drawn disabled and another read-only, and a multipart
form to submit that comes back with a field error. An uploaded file is checked and
dropped, and nothing is stored.

- `/text-inputs/` and `/choice-inputs/` are the pages inside the django-mvp shell,
  reached from its sidebar.
- `/text-inputs/standalone/` and `/choice-inputs/standalone/` are the same pages
  as a host project with neither django-mvp nor Cotton would have them, styled by
  daisyUI's CDN build alone.

Two more pages draw the layout objects, a form to submit and a form that already
fails, so an error inside a fieldset, a row and a column can be seen:

- `/layout-objects/` is the page inside the django-mvp shell, reached from its sidebar.
- `/layout-objects/standalone/` is the same page styled by daisyUI's CDN build alone.

One more page draws the size, colour and variant of a form's inputs and buttons. It holds a small form for each size and for each colour, each with one input and one button; a form holding every kind of input at one size; a form of inputs in the ghost variant and a button bar with one button in each variant; and a form that states choices and overrides them for one field in its layout, for one field by name, for one field that drops the colour, and for one button. The forms are built from the tables of `Modifiers`, so the page follows them, and none of them posts anywhere.

- `/choices/` is the page inside the django-mvp shell, reached from its sidebar as "Size, colour and variant".
- `/choices/standalone/` is the same page styled by daisyUI's CDN build alone.

One more page draws a boolean field as a checkbox, a toggle and a switch. It holds one form with three boolean fields, drawn those three ways: the first states nothing, the second is a toggle by its name in `FormChoices`, and the third is a switch in the layout. Turning some on and submitting the form draws the page again with each field as it was posted and the values the form cleaned to. Nothing is saved. The page also draws each of the three in each state (off, on, with help text, required and in error, and disabled), at every size and in every colour a toggle has, and in a form whose size and colour one field overrides.

- `/drawings/` is the page inside the django-mvp shell, reached from its sidebar as "Checkbox, toggle and switch".
- `/drawings/standalone/` is the same page styled by daisyUI's CDN build alone.

Both pages end the form to submit in a `FormActions` holding a `Submit`, a `Reset`, a `Button` and a `StrictButton`, and add a form whose buttons were added to its helper and a small layout that puts two fields straight in a `Row` above a `ButtonHolder`. The form to submit also places an `HTML` note inside its fieldset, groups two fields in a `MultiField`, and carries a `Hidden` input.

Five more pages draw the containers and the notice django-crispy-forms keeps in `crispy_forms.bootstrap`. Each of the first three holds a form to submit whose required field sits in a tab, a group or a modal that is not open, so submitting it empty comes back with the tab, group or modal that holds the error open:

- `/tabs/` is inside the django-mvp shell, reached from its sidebar. Its second form is already bound and fails in its third tab.
- `/accordion/` is inside the shell too. Its second form has one group the developer opened and one the developer closed.
- `/modal/` is inside the shell too. Its form holds the street and the city, both required, in a modal that a button on the page opens by the modal's id. Submitting the form empty comes back with the modal open and the errors inside it.
- `/alert/` is inside the shell too. Its form has three alerts ahead of its field: one with a dismiss control, one without, and one with a daisyUI colour. Submitting the form empty draws all three again.
- `/containers/standalone/` draws the forms of all four pages as a host project with neither django-mvp nor Cotton would have them, styled by daisyUI's CDN build alone. A post is bound to the form whose submit button it names.

Six more pages draw the layout objects that decorate a field. The first draws the three that attach text to an input. Its form has a text input with a prepended text, one with an appended text, one with both and a select with a prepended text, every field required, so submitting it empty comes back with an error in each frame. A second form on the page already fails. The second draws the two that put choices in a line, the third draws `FieldWithButtons`, the fourth draws `UneditableField`, the fifth draws `InlineField` and the sixth draws `MultiWidgetField`. The first three, the fifth and the sixth each have a form to submit and one that already fails; the fourth has one form to submit:

- `/attached-text/` is the page inside the django-mvp shell, reached from its sidebar.
- `/inline-choices/` is the page inside the shell, reached from its sidebar. The form to submit holds a required radio group and a required checkbox group, so submitting it empty comes back with an error in each frame.
- `/field-with-buttons/` is the page inside the shell, reached from its sidebar. The form to submit has a required field with one button and a required field with three, so submitting it empty comes back with an error in each frame.
- `/uneditable-field/` is the page inside the shell, reached from its sidebar. Its form holds an uneditable account, shown with its value and the `disabled` attribute, beside an editable nickname. The account is declared disabled in the form class, so submitting the form keeps its value and shows no error.
- `/inline-field/` is the page inside the shell, reached from its sidebar. The form to submit has a required email and a required city, each drawn with no label and named by its placeholder, and a checkbox that keeps its label, so submitting it empty comes back with an error in the frame of each of the two fields.
- `/multi-widget-field/` is the page inside the shell, reached from its sidebar. The form to submit has a required split date and time whose parts each have a placeholder of their own, and an optional one drawn with no layout object, so submitting it empty comes back with an error in the frame of the first.
- `/decorated-fields/standalone/` draws the forms of all six pages as a host project with neither django-mvp nor Cotton would have them, styled by daisyUI's CDN build alone.

Four more pages draw a formset of order lines, each with a delete input and an order input, and each drawn twice: a formset to submit and a formset that already fails, so all three kinds of error can be seen. A line with a quantity below one is a field error, a line whose total passes a limit is a form-wide error, and the same item on two lines is a formset-wide error. Posting the formset to submit with lines like those comes back with all three. Nothing is saved.

- `/formset-stacked/` and `/formset-table/` draw the formset stacked and as a table, inside the django-mvp shell, and are reached from its sidebar.
- `/formset-stacked/standalone/` and `/formset-table/standalone/` are the same pages styled by daisyUI's CDN build alone.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-forms/blob/main/LICENSE).
