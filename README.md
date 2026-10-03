# django-mvp-forms

A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects.

> **Status: pre-release.** The template pack draws text-like fields, choices, booleans, file inputs and hidden inputs, and the layout objects, with `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert` all supported. Nothing is published to PyPI.

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

A class, placeholder, input type or row count you give a widget is kept. The pack never changes an input's type, so a date field is a text input unless its widget says otherwise. Fields with any other widget are still drawn in place, without a daisyUI class.

### Disabled and read-only fields

The pack adds no class and no attribute for either state. A field with `disabled=True` is drawn by Django with `disabled` on its input, on every option of a radio or checkbox group, and on the removal checkbox of a file field that holds a file, and daisyUI draws its disabled look from that attribute for every component the pack uses. A disabled field still shows its value, except a password input, which never draws one. The browser does not submit a disabled input, and Django takes the field's initial value instead.

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

- `fields` gives one field a `Choice` of its own, by the field's name. Each of the three that the `Choice` states wins over the form's for that field, and each it leaves out, which is `INHERIT` and the default, falls back to the form's. `None` is the pack's ordinary drawing, so `Choice(color=None)` undoes the form's colour for that field, as `notes` does above. `INHERIT` is the one value of the type `Inherit`.
- Every input of a field takes the choices: each option of a radio or checkbox group, each select of a date, and the removal checkbox of a file field that holds a file, which takes the size and the colour.
- A choice that one kind of input has no modifier for is passed over for that kind. `variant="ghost"` leaves a checkbox and a radio as they are and draws the text input beside them in ghost.
- A name that is not in the lists above raises `InvalidChoice`, a `ValueError`, when the form is drawn. It carries the `kind`, the `value` and the names `allowed`.
- A field in error keeps its error modifier and is drawn without the chosen colour, so the error is the only colour it shows. Its size and variant still apply.
- Hidden inputs, labels, help text, error text and the `required`, `disabled` and `readonly` attributes are never changed, and classes you put on a widget are kept.
- The size reaches every button too, as `btn-sm` and the like. A colour or a variant for the form's buttons is stated apart from the inputs', as `button_color` and `button_variant`, so `color` and `variant` reach no button and the two never touch. Buttons are described below.

### One field's own choice

One field can state a size, a colour or a variant of its own. There are two ways, and they combine.

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

Here `search` is large and keeps the form's colour, `name` and `city` keep the form's size and lose its colour, and `notes` takes the form's choices. A `Choice` may hold a `Row`, a `Fieldset` or any other layout object, and a `Choice` inside a `Choice` is merged over the outer one, each of the three on its own, so the inner one wins for what it states. You can also wrap fields already in a layout, with `helper["search"].wrap(Choice, size="lg")`.

For a form drawn without a layout, name the field in `FormChoices`, as `notes` was in the section above: `FormChoices(fields={"search": Choice(size="lg")})`. It works with `{{ form|crispy }}` and with `{% crispy form %}`, and changes no other field.

When both are given for a field, the `Choice` in the layout wins over the one in `fields`, which wins over the form's, for each of the three on its own. What a `Choice` leaves out is inherited, and `None` is the pack's ordinary drawing: `Choice("notes", color=None)` undoes the form's colour for that field and keeps its size. A size, colour or variant that the field's input has no modifier for raises `InvalidChoice` when the form is drawn, because you asked for it by name. The form's own statement is passed over for such an input.

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

### What is refused and what is passed over

A name daisyUI does not have is refused when the form is drawn, never written as a class that does nothing. It raises `InvalidChoice`, a `ValueError` carrying `kind` (`"size"`, `"color"` or `"variant"`), the `value` you stated and the names `allowed`. It is raised for a choice stated for the form's inputs, for its buttons (`button_color` and `button_variant`), on one field by name, on one field with a `Choice` in a layout, and on one button. When it was stated on a field or a button, `target` names it: the field's name, or a button's name, or the content of a `StrictButton`. For a choice stated for the form, `target` is `None`. What is stated for the form is checked whenever a form is drawn, so `{{ form|crispy }}`, which draws no button, still reports a mistake in `button_color`.

A choice stated for the form that a kind of input has no modifier for is passed over, with no error: `variant="ghost"` leaves a checkbox, a radio group and a checkbox group as they are and the rest take it. The same choice stated on one of those fields raises, and so does any choice stated on a field whose widget the pack does not draw as an input of its own, because you asked for it by name.

A name in `FormChoices(fields=...)` that is not a field of the form raises `UnknownField`, a `KeyError` whose `names` lists them, when a field of the form is drawn.

A `Choice` in a layout is checked against each field and button it holds, as a choice stated on each of them. `Choice(Row("name", "agree"), variant="ghost")` raises for a checkbox `agree`, which has no ghost, and a `Choice` holding a field and a button needs a variant both have. Size and colour apply to every kind, so a `Choice` that states only those can hold anything.

The `daisyui` attribute of the helper a form carries as `form.helper` must be a `FormChoices`: anything else, `None` included, raises `TypeError` when a field of the form is drawn. Leave the attribute off to state nothing. A page variable that happens to be called `daisyui` and is not a `FormChoices` is ignored, and so is such a value on a helper handed to the tag on its own, as `{% crispy form helper %}`, where the pack cannot tell it from the page's. Keep the statement on the helper the form carries: with `{% crispy form helper %}` the inputs still read `form.helper`, and the buttons only the helper that draws them.

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

Both pages end the form to submit in a `FormActions` holding a `Submit`, a `Reset`, a `Button` and a `StrictButton`, and add a form whose buttons were added to its helper and a small layout that puts two fields straight in a `Row` above a `ButtonHolder`. The form to submit also places an `HTML` note inside its fieldset, groups two fields in a `MultiField`, and carries a `Hidden` input.

Five more pages draw the containers and the notice django-crispy-forms keeps in `crispy_forms.bootstrap`. Each of the first three holds a form to submit whose required field sits in a tab, a group or a modal that is not open, so submitting it empty comes back with the tab, group or modal that holds the error open:

- `/tabs/` is inside the django-mvp shell, reached from its sidebar. Its second form is already bound and fails in its third tab.
- `/accordion/` is inside the shell too. Its second form has one group the developer opened and one the developer closed.
- `/modal/` is inside the shell too. Its form holds the street and the city, both required, in a modal that a button on the page opens by the modal's id. Submitting the form empty comes back with the modal open and the errors inside it.
- `/alert/` is inside the shell too. Its form has three alerts ahead of its field: one with a dismiss control, one without, and one with a daisyUI colour. Submitting the form empty draws all three again.
- `/containers/standalone/` draws the forms of all four pages as a host project with neither django-mvp nor Cotton would have them, styled by daisyUI's CDN build alone. A post is bound to the form whose submit button it names.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-forms/blob/main/LICENSE).
