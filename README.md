# django-mvp-forms

A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects.

> **Status: pre-release.** The template pack draws text-like fields, choices, booleans, file inputs and hidden inputs, every layout object django-crispy-forms ships, including the nine that decorate a field and `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, and formsets drawn stacked or as a table, and it draws the select controls of django-tomselect. Nothing is published to PyPI. The versions of Django, django-crispy-forms and daisyUI it supports are in [Supported versions](https://github.com/django-mvp/django-mvp-forms#supported-versions).

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

Widgets from popular third-party Django packages may get templates here so they sit properly in a daisyUI form. Which packages are supported is the maintainers' call, and none of them becomes a dependency. A supported package whose controls are built by script, as django-tomselect's are, may also get one optional stylesheet that the host project loads. The pack's own templates define no class and need no stylesheet, and there is never one stylesheet for several packages. The package also ships one script, for its input mask widgets, which a form names in its media. A project that uses none of those widgets never loads it, and the pack's own templates need no script.

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

The host project supplies daisyUI itself. The pack's templates are markup and need no stylesheet of ours; the package's one stylesheet, for django-tomselect's controls, is optional and is described under [django-tomselect](https://github.com/django-mvp/django-mvp-forms#django-tomselect). Pages that draw these forms must load daisyUI 5, from the minor release named in [Supported versions](https://github.com/django-mvp/django-mvp-forms#supported-versions) upward. Its CDN build needs no build step, so daisyUI's own CDN install in the page's `<head>` is enough:

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

A host project with its own Tailwind build has to make that build produce the classes the pack writes. Tailwind only generates a class it finds in the files it scans, so point it at the whole installed `mvp_forms` package: the classes are written in its templates and in its template tags.

## Supported versions

<!-- support-window -->
| | Supported |
|---|---|
| Django | 5.2, 6.0, 6.1 |
| django-crispy-forms | 2.7 |
| daisyUI | 5.0 to 5.7 |
| Python | 3.12, 3.13, 3.14 |

Each django-crispy-forms release works with the Django series on its row:

| django-crispy-forms | Django |
|---|---|
| 2.7 | 5.2, 6.0, 6.1 |
<!-- /support-window -->

A version is named the way a project chooses it: a release series for Django, a feature release for django-crispy-forms, and a major version with a minimum minor release for daisyUI. The newest patch release of each named version is the one meant. The Python versions are the ones the test suite runs on.

Django is supported for every release series the Django project still supports with mainstream or security fixes. django-crispy-forms is supported for every feature release of its current major series from the minimum named above. daisyUI is supported for its current major version from the minimum named above. The test suite checks the pack against the two ends of the daisyUI range named above, and does not check the releases between them one by one. A daisyUI version below the minimum is outside the window, whether it comes from the CDN or from a Tailwind build of your own.

A Django or django-crispy-forms release newer than any named above installs, because the package sets no upper limit on either. It is not vouched for until this section names it.

### How soon a new release is supported

Within thirty days of its final release, a new Django release series, a new django-crispy-forms feature release in its current major series and a new daisyUI minor release in its current major version are each either supported by a release of this package or listed here as not supported, with a link to the [issue](https://github.com/django-mvp/django-mvp-forms/issues) that tracks it. A pre-release is not covered. Python versions carry no period: this section follows what the suite runs on.

A new major version of django-crispy-forms or daisyUI has no period. It is supported only from the release of this package that names it.

A page that loads `daisyui@5` from the CDN receives a new daisyUI minor release as soon as daisyUI publishes it, before this section names it. For up to thirty days that release is neither checked nor named. After that this section either names it or says it is not supported and links the issue.

### How a version leaves

- A Django series leaves when the Django project ends its support for it.
- A django-crispy-forms release leaves when the minimum is raised. The minimum is raised only when the release no longer supports any Django series in the window, or when the pack needs something a later release provides.
- The daisyUI minimum is raised only when the pack needs a class that a later minor release provides. A daisyUI major version leaves only when this package's own major version changes.

Dropping a version is not a breaking change. It ships in a minor or major release of this package and never in a patch release. The changelog names each version a release drops.

### Versions that have left

No version has left the window. When one does, it is listed below with the last release of this package that supported it. An installer in a project still on a dropped Django or django-crispy-forms version selects that last release by itself, because every later release requires a newer version. That last release is not fixed further: a defect found in it later gets no new release.

<!-- dropped-versions -->
<!-- /dropped-versions -->

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

The pack draws radio and checkbox groups, a date's selects and a clearable file input from templates of its own, which the form renderer loads, and which a host project replaces in a way of its own (see [Replacing one template](#replacing-one-template)). A widget subclass that names a template of its own is drawn by that template, with the daisyUI class only.

The label is tied to the input, and a required field's label carries a marker that assistive technology skips. The input announces itself as required, as invalid when it has errors, and by its help text and error messages as its description. Label, help text and errors are escaped unless you mark them safe. Help text, the label of a single checkbox, the label of each option in a radio or checkbox group and the label of a file input's removal checkbox wrap onto as many lines as they need, so a long one never makes the form wider than a narrow page. Their input stays centred beside the lines, as daisyUI draws it. Text attached to an input stays on one line. Every id the pack writes is built from the form's `auto_id`, so forms with different prefixes never share one, and a form with `auto_id=False` gets none.

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

The layout objects of django-crispy-forms are drawn as daisyUI too, so a form with a `Layout` needs nothing more than the pack selected. Import them from django-crispy-forms as its documentation says. This package adds two of its own, `Choice` (see "One field's own choice") and `Join` (see "Joined groups"). `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`, all from `crispy_forms.bootstrap`, are supported along with the structural and button objects below:

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
- The close button takes the size stated for the form, `FormChoices(size="sm")`, so it matches the form's other buttons, and the size of a `Choice` around the `Modal` wins over the form's. It takes the size alone: `button_color` and `button_variant` do not reach it, and neither do the colour and variant of a `Choice`, because the button belongs to the modal and is not one you placed. With no size stated it carries none.
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
- The dismiss button is small, `btn-sm`, until a size is stated. It then takes the size stated for the form, or the size of a `Choice` around the `Alert`, which wins. `Choice(Alert(...), size=None)` draws it small again. Like a modal's close button it takes the size alone, never `button_color`, `button_variant` or the colour and variant of a `Choice`.
- `block=True` is accepted and changes nothing, because daisyUI has no counterpart to the Bootstrap class it adds. `alert-block` is never drawn.
- The content is trusted. It is written into the page as markup, as django-crispy-forms documents, so a tag in it is a tag in the page, and a context value in it is not filled in. Anything a person typed must be escaped before it is put there, for example with `django.utils.html.escape` or `format_html`.

Two of the buttons above run a line of script written on the button itself, in its `onclick` attribute: the close button of a `Modal` and the dismiss button of an `Alert`. Neither HTML nor daisyUI has another way to do either job that works in every browser daisyUI supports. A page served with a Content Security Policy that forbids inline event handlers, such as `script-src 'self'` with nothing more, draws both buttons and neither does anything:

- Tabs and an accordion use no script and work under any policy, as does everything else the pack draws.
- A modal your page opened as a modal is still closed with the Escape key. A modal drawn open because a field in it has an error has no other way to close, and an alert stays where it is.
- Both buttons work when the policy allows inline event handlers, with `script-src-attr 'unsafe-inline'` or with `'unsafe-inline'` in `script-src`. To allow these two handlers and no other, add `'unsafe-hashes'` and the SHA-256 hash of each handler's text to either directive. The text is the value of `onclick` in `daisyui/layout/modal.html` and in `daisyui/layout/alert.html`, and the hash has to be worked out again if a release changes that text.
- A project that keeps its policy strict can draw the buttons its own way (see [Replacing one template](https://github.com/django-mvp/django-mvp-forms#replacing-one-template)). A close button written as `<button type="button" class="btn daisyui-size" commandfor="{{ modal.css_id }}" command="close">` in your own `daisyui/layout/modal.html` closes the dialog with no script, in a browser that has the `command` and `commandfor` attributes. Chrome, Firefox and Safari all gained them during 2025, and an older browser draws a button that does nothing. `Alert(..., dismiss=False)` draws an alert with no button.
- The button in the example above that opens the modal is an inline handler too. Under such a policy write it as `<button type="button" commandfor="name-modal" command="show-modal">Edit name</button>`, or open the modal from a script file of your own.

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
- `wrapper_class` works on any field, not only on these three: it is added to the class of the frame's outer element, whether that is a `<div>` or a `<fieldset>`. `Field("name", wrapper_class="wide")` draws `class="fieldset wide"`. The one place it does not reach is a `Field` given as the first item of `FieldWithButtons`, because django-crispy-forms passes on only that `Field`'s attributes.

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

#### Joined groups

`Join` comes from `mvp_forms.layout`, and is the package's own, not django-crispy-forms'. It draws several fields as one daisyUI join under one label, such as a country code and a phone number:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from mvp_forms.layout import Join


class ContactForm(forms.Form):
    name = forms.CharField()
    country_code = forms.ChoiceField(choices=[("+49", "+49"), ("+44", "+44")])
    number = forms.CharField(help_text="Digits only")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            "name",
            Join("country_code", Field("number", autocomplete="tel"), label="Phone"),
        )
```

- A group holds field names, `Field` objects and `Choice` objects, in the order they are drawn. A `Field` gives its attributes and its `css_class` to the input of each name it holds, and a `Choice` states its size, colour and variant for the names it holds. A member has no frame of its own, so a `Field` given a `wrapper_class` or a `template` raises `InvalidMember` with `Field` as `member`. Anything else in a group raises `InvalidMember` too, when the form is drawn, with the class name as `member`: a `Div`, a `PrependedText`, an `InlineField`, a button, another `Join`, and a subclass of `Field` such as `MultiWidgetField`.
- A member is an input or a select drawn on its own. A checkbox, a toggle, a radio group, a checkbox group, a textarea, a file input, a multi-widget field, a date drawn as three selects, a rating, a range and a field whose widget the pack does not draw as an input raise `InvalidMember` with the field's name as `member`. A hidden field is accepted.
- The group is one `<fieldset>`. Its `label` is the `<legend>`, as escaped text, with the required marker when any member is required, and a group with no label has no legend. A member draws no label of its own: its input is named by an `aria-label` that is its own field's label, and an `aria-label` you wrote on the widget or on the `Field` is kept. With the helper's `form_show_labels` off the legend is not drawn and the fieldset takes the group's label as its `aria-label`.
- Each member keeps its own help text and errors. They are drawn after the join, inside the fieldset, once for each member, with the ids Django gives them, `<id>_helptext` and `<id>_error`. A member's input is described by its own help text and errors only, and only the member that failed is `aria-invalid`.
- The inputs are the direct children of the one element that carries `join`, in the order the group holds them. A hidden member is drawn as its hidden input after that element, inside the fieldset, because daisyUI squares the first and last child of a join whatever they are. A disabled member stays in its place disabled, and a read-only member keeps its attribute.
- The `css_id`, `css_class` and attributes you give `Join` are on the element that carries `join`, so `Join("width", "height", css_class="join-vertical")` stacks the inputs. A class written for another template pack is dropped. A name the form lacks is left to django-crispy-forms: it logs it, or raises when `CRISPY_FAIL_SILENTLY` is `False`, and draws nothing for it.
- `Join.members()` returns what a group holds as a list of `Member`, one for each field name in order, each with its `name`, the `attrs` of the `Field` that held it and the `choice` around it. It raises `InvalidMember` for a layout object the group cannot hold, so a layout can be checked without drawing a form.
- A group that holds no field draws nothing, and a group whose members are all hidden draws their hidden inputs alone.
- The join fills its width. An input takes the room the others leave and a select takes its own width. A width class of your own on a widget or a `Field`, such as `w-24`, is kept and the pack adds none.
- A floating label never applies to a member. The form's `label="floating"` passes it over, and the same statement on a member raises `InvalidChoice` with `kind="label"`.
- Size, colour and variant apply to each member as they do on any field, in the order under "One field's own choice". A `Choice` around the group states them for every member. A `Choice` around one member, or an entry for it in `FormChoices(fields=...)`, wins for that member, and the form's statement applies to every member the others leave alone. A member's own size wins for that member, and the group enforces no one size. A member in error carries its error modifier and no colour modifier, and the other members keep the colour.
- A form with no `Join` is drawn as before, and the form posts and cleans to the same data joined and not joined. In a formset drawn stacked every form draws the group. A formset drawn as a table shows each field as a column, so it draws no join and raises nothing.

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

- `fields` gives one field a `Choice` of its own, by the field's name. Each of size, colour and variant that the `Choice` states wins over the form's for that field, and each it leaves out, which is `INHERIT` and the default, falls back to the form's. A `Choice` also states a drawing, which the form has no statement of: see "Checkbox, toggle and switch" and "Rating and range" below. `None` is the pack's ordinary drawing, so `Choice(color=None)` undoes the form's colour for that field, as `notes` does above. `INHERIT` is the one value of the type `Inherit`.
- Every input of a field takes the choices: each option of a radio or checkbox group, each select of a date, and the removal checkbox of a file field that holds a file, which takes the size and the colour.
- A choice that one kind of input has no modifier for is passed over for that kind. `variant="ghost"` leaves a checkbox, a toggle and a radio as they are and draws the text input beside them in ghost.
- A name that is not in the lists above raises `InvalidChoice`, a `ValueError`, when the form is drawn. It carries the `kind`, the `value` and the names `allowed`.
- A field in error keeps its error modifier and is drawn without the chosen colour, so the error is the only colour it shows. Its size and variant still apply.
- Hidden inputs, labels, help text, error text and the `required`, `disabled` and `readonly` attributes are never changed, and classes you put on a widget are kept.
- The size reaches every button too, as `btn-sm` and the like. A colour or a variant for the form's buttons is stated apart from the inputs', as `button_color` and `button_variant`, so `color` and `variant` reach no button and the two never touch. Buttons are described below. The size also reaches the two buttons the pack draws itself, the close button of a `Modal` and the dismiss button of an `Alert`.

### One field's own choice

One field can state a size, a colour or a variant of its own, and a drawing as well. A floating label is stated the same way: see "Floating labels" below. There are two ways, and they combine.

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

Here `search` is large and keeps the form's colour, `name` and `city` keep the form's size and lose its colour, and `notes` takes the form's choices. A `Choice` may hold a `Row`, a `Fieldset` or any other layout object, and a `Choice` inside a `Choice` is merged over the outer one, each of its five kinds on its own, so the inner one wins for what it states. You can also wrap fields already in a layout, with `helper["search"].wrap(Choice, size="lg")`.

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
- The close button of a `Modal` and the dismiss button of an `Alert` are drawn by the pack and belong to their containers. They take the form's `size`, or the size of a `Choice` around the container, and nothing else: `button_color`, `button_variant` and a `Choice`'s colour and variant pass them by, and a `Choice` around the container is never checked against them.
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
- A boolean field takes these three drawings. A field that holds one choice takes the rating of "Rating and range" below, a number field takes the range there, and nothing else takes a drawing: a null-boolean select, a checkbox group, a text input or anything else that is neither a `CheckboxInput` nor one of those, and neither does a button.
- A hidden boolean field is a hidden input whatever is stated for it.
- A toggle and a switch take the form's size and colour, and the field's own, like any input: `toggle-sm` and `toggle-primary` for a toggle or a switch, where a checkbox takes `checkbox-sm` and `checkbox-primary`. They have no variant. A variant stated for the form is passed over for them and one stated on the field itself raises `InvalidChoice`, as for a checkbox. A field in error keeps `toggle-error` and is drawn without the colour.

For a boolean field, a name that is not one of the three raises `InvalidChoice` with `kind="drawing"`, naming the field as `target`, with `checkbox`, `toggle` and `switch` as the names `allowed`. One of the three, `checkbox` included, stated for a field that is not a boolean field raises the same error, and `allowed` holds the drawings that field takes: `rating` for a field that holds one choice, `range` for a number field and nothing for any other. One stated around a button raises it too, with nothing allowed. A `Choice` that holds fields states its drawing for each of them, so `Choice(Row("name", "agree"), drawing="toggle")` raises for a text input `name`. `None` and `INHERIT` state nothing and never raise. A drawing stated by name in `FormChoices(fields=...)` is checked when its field is drawn, so one for a field the layout leaves out is never looked at.

### Rating and range

A field that holds one choice can be drawn as daisyUI's rating, with one star for each choice, and a number field can be drawn as daisyUI's range, a slider. A rating is for a field whose widget is a `Select` or a `RadioSelect`, or a subclass of either that still uses Django's own templates, such as a `ChoiceField`, a `TypedChoiceField` or a `ModelChoiceField`. A range is for a field whose widget is a `NumberInput` or a subclass of one, which is what an `IntegerField`, a `FloatField` and a `DecimalField` have unless they are localised. State either as any drawing is stated, with `drawing="rating"` or `drawing="range"` in a `Choice`, in a layout or by the field's name:

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from mvp_forms.choices import Choice, FormChoices

STARS = [(count, f"{count} stars") for count in range(1, 6)]


class ReviewForm(forms.Form):
    score = forms.ChoiceField(choices=STARS)
    comfort = forms.ChoiceField(choices=[("", "No answer"), *STARS], required=False)
    volume = forms.IntegerField(min_value=0, max_value=100, step_size=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            size="sm", color="primary", fields={"score": Choice(drawing="rating")}
        )
        self.helper.layout = Layout(
            "score",
            Choice("comfort", drawing="rating"),
            Choice("volume", drawing="range", color="accent"),
        )
```

Here `score` is a rating by its name in `FormChoices`, `comfort` is a rating in the layout and `volume` is a range in the layout, from 0 to 100 in steps of 5. The form states a small size and the primary colour, so both ratings and the range are small, the ratings are primary, and `volume` states the accent colour of its own. The form posts and cleans exactly as it does with a select, because only the way the choices are drawn changes: a person picks a star and the form receives the value of that choice, and the field and its widget are not changed.

- Each choice that has a value is one `<input type="radio">` with the field's name, in the field's order, inside an element with the class `rating`. daisyUI draws every child of a rating as a star, so a star has no `<label>` around it. It is named by an `aria-label` that holds its choice's label as plain text, unless the widget already gives the input one. The pack adds no text of its own.
- A choice whose value is the empty string is not a star. It is the way to clear the rating, drawn first, whatever its place among the choices, as the input daisyUI hides with `rating-hidden`, so that an optional field can be submitted empty and cleans to its empty value. A choice whose value is `0` is a star. A field with no empty choice offers no way to clear it.
- A bound or initial value is drawn as the star picked, and a field that holds no value is drawn with no star picked. Choices in named groups are stars in the field's order and the group names are not drawn. A field with no choices is drawn with its frame and no star. A model choice field has its empty label as the way to clear.
- A select and a radio group with the same choices are drawn as the same inputs. A select is drawn through a radio group that is made for the draw from its attributes and choices, and a radio group is drawn through a copy of itself.
- A rating keeps what a radio group has. The stars are one group in a `<fieldset>` named by a `<legend>` that holds the field's label and the required marker, and by an `aria-label` on the fieldset when the form draws no labels. The help text and the errors are drawn and describe the fieldset, each star of a field in error is `aria-invalid`, and every star of a disabled field is disabled. A field in error draws its stars in the error colour, `bg-error`. A class or an attribute you set on the widget is on every input of the rating, the one that clears included.
- A rating and a range take the form's size and colour, and the field's own, like any input, and have no variant. A variant stated for the form is passed over for them and one stated on the field itself raises `InvalidChoice`. A range takes `range-sm` and `range-primary` and the like on its input. A rating's size is on the element with the class `rating`, the group of stars, as `rating-sm`, and its colour is on each star, as daisyUI's background colour class `bg-primary`, and never on the input that clears it. A field in error keeps its error modifier and is drawn without the chosen colour: a rating's stars carry `bg-error`, a range carries `range-error`, and the size still applies.
- A rating is drawn the same through `{{ form|crispy }}` and `{% crispy form %}`, in a formset stacked or as a table, and inside a `Row`, a `Fieldset`, a `Tab` or an `AccordionGroup`. `InlineRadios` around a rating draws the rating, and a layout object that attaches text to an input leaves it as it is. A hidden field is a hidden input whatever is stated for it. The pack adds no script.

A range is one `<input type="range">` with the field's name and id and the class `range`. It is drawn through a copy of the field's widget with its type changed, by Django's own input template, so what is submitted, validated and cleaned is what a number input gives, and the field and its widget are not changed.

- A range's lowest value, highest value and step are the ones Django already writes on the field's widget: `min`, `max` and `step` from `min_value`, `max_value` and `step_size`, and the `step` a `FloatField` or a `DecimalField` gets when none is declared. The pack adds none and refuses nothing for a field that has no limits, so an `IntegerField` that declares none is drawn with none, and the slider takes the browser's own: 0 to 100 in steps of 1.
- A bound or initial value is the input's `value`. A range keeps what a number input has: the label is tied to it, the help text and the errors are drawn and describe it, a field in error is `aria-invalid` and carries `range-error`, a required field carries the required marker, a disabled field is disabled, and with labels off it is named by an `aria-label`. A class or an attribute you set on the widget is kept, and a range fills its field unless a class you set holds a width.
- A range is drawn the same through `{{ form|crispy }}` and `{% crispy form %}`, in a formset stacked or as a table, and inside a `Row`, a `Fieldset`, a `Tab` or an `AccordionGroup`. A layout object that attaches text to an input, such as `PrependedText`, draws the range with no attached text. A hidden field is a hidden input whatever is stated for it. The pack adds no script, so a person moves the slider and the value reaches the server.
- A slider always submits a number. An optional number field drawn as a range is therefore never submitted empty, however far the person has moved it. Leave a field a person may skip as a number input.
- In a formset, an extra form nobody touched still submits its slider's position, and Django compares that with the field's initial value. A field with no `initial` has nothing to match, so the form counts as changed and is validated as a filled-in form. Give the field an `initial` the slider can rest on, one within its limits and on its step: the slider is drawn there, an untouched form submits that value, and Django passes the form over as unchanged. The pack does not refuse a range whose field has no `initial`.

A field that cannot be drawn as a rating or a range raises `InvalidChoice` with `kind="drawing"` when the form is drawn, naming the field as `target`. For a rating that is a multiple select, a checkbox group, a null-boolean select, a text input, a number input, a boolean field, and a select or a radio group whose widget names a template of its own, because the pack cannot draw a rating through a template it does not own. For a range it is a field whose widget is not a number input, which includes a localised `IntegerField`, `FloatField` or `DecimalField`, whose widget is a text input, and a rating or one of a boolean field's drawings stated for a number field. The names `allowed` are the field's own: `rating` for a field that holds one choice, `range` for a number field, the three drawings of a boolean field for a checkbox, and none for the others.

### Floating labels

A floating label is daisyUI's own: the label sits inside the field and takes the place of its placeholder while the field is empty, then moves to the field's edge once it is focused or holds a value. State it once for the form, or for one field, the same two ways as a size or a colour. You write no template and no class. The statement is `label="floating"`, in `FormChoices` for the form and in `Choice` for a field:

```python
from crispy_forms.helper import FormHelper
from django import forms
from mvp_forms.choices import Choice, FormChoices


class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput, help_text="At least eight characters"
    )
    country = forms.ChoiceField(choices=[("de", "Germany"), ("uk", "United Kingdom")])
    notes = forms.CharField(widget=forms.Textarea, required=False)
    remember = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            label="floating", fields={"notes": Choice(label=None)}
        )
```

Here `email`, `password` and `country` have a floating label, `notes` has its ordinary label, and `remember` is drawn as it is without the statement. It takes effect with `{{ form|crispy }}` and with `{% crispy form %}`, whether or not the form has a layout, and in each form of a formset drawn stacked. In a layout, wrap the field in a `Choice`: `Choice("email", label="floating")`.

The label is drawn once, in a `<label class="floating-label">` that holds the input and is tied to it by `for`. The required marker is inside it. The help text and the errors are drawn as they are for any field, with the input's `aria-describedby` and `aria-invalid` unchanged, and the form posts and cleans to the same data as with ordinary labels. Size, colour and variant apply as they do on any field: the form's, an entry in `FormChoices(fields=...)` and a `Choice` in a layout, the layout winning over the entry and the entry over the form's, as under "One field's own choice". A floating field takes the same modifier it takes with an ordinary label, and one in error carries its error modifier and no colour.

- A floating label is for an input, a textarea or a select drawn on its own. The form's statement is passed over, with no error, for every other field: a checkbox, a toggle, a radio group, a checkbox group, a file input, a rating, a range, a multi-widget field, a date drawn as three selects, and a field drawn with attached text on an input or a select, with buttons joined to it, or with no visible label by `InlineField`, and a member of a joined group. A textarea inside a `PrependedText` has no attached text to draw, so it floats.
- The same statement made for one of those fields, by name or in a layout, raises `InvalidChoice` with `kind="label"`, nothing allowed and the field as `target`. A `Choice` around a `FieldWithButtons` is stated for its buttons too, and they are drawn first, so there the `target` is the first button. A name other than `floating` raises it too, with `floating` as the name allowed. `None` undoes the form's statement for a field and never raises.
- An empty field with no placeholder of your own is given its label's text as its placeholder, which is how daisyUI shows the label in place. A select has none. A placeholder you set on the widget is kept.
- A disabled field is drawn with its ordinary label, so a person can still see what it is, and is never an error. The field is disabled when its form field has `disabled=True`, when its widget has a `disabled` attribute, or when it is drawn with a `disabled` option. A field disabled only by a `<fieldset disabled>` around it is not detected, so give it `Choice(label=None)`. A read-only field floats.
- With `form_show_labels` off no label is drawn, so nothing floats and the input is named by an `aria-label`. A field with no label text is drawn as any field with none is. A formset drawn as a table shows each label as its column heading, so nothing floats there and nothing raises.
- The label is escaped as every label is. In the placeholder it is plain text.

### What is refused and what is passed over

A name daisyUI does not have is refused when the form is drawn, never written as a class that does nothing. It raises `InvalidChoice`, a `ValueError` carrying `kind` (`"size"`, `"color"`, `"variant"`, `"drawing"` or `"label"`), the `value` you stated and the names `allowed`. It is raised for a choice stated for the form's inputs, for its buttons (`button_color` and `button_variant`), on one field by name, on one field with a `Choice` in a layout, and on one button. When it was stated on a field or a button, `target` names it: the field's name, or a button's name, or the content of a `StrictButton`. For a choice stated for the form, `target` is `None`. What is stated for the form is checked whenever a form is drawn, so `{{ form|crispy }}`, which draws no button, still reports a mistake in `button_color`.

A choice stated for the form that a kind of input has no modifier for is passed over, with no error: `variant="ghost"` leaves a checkbox, a toggle, a radio group and a checkbox group as they are and the rest take it. The same choice stated on one of those fields raises, and so does any choice stated on a field whose widget the pack does not draw as an input of its own, because you asked for it by name.

A floating label stated for the form is passed over for every field that cannot take one, listed under "Floating labels", with no error. Stated on one of them it raises `InvalidChoice` with `kind="label"`, the field as `target` and nothing allowed, and so does one stated around a button. A name other than `floating` raises it with `floating` allowed.

A `Join` that holds a layout object it cannot join, or a field it cannot draw as an input or a select, raises `InvalidMember`, from `mvp_forms.layout`, when the form is drawn. It is a `ValueError` carrying `member`: the layout object's class name, or the field's name. Nothing is passed over, because a field is named in the group on purpose. See "Joined groups".

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

### Replacing one template

A host project replaces one template of the pack by putting a file at the same path where Django finds it first. The replacement stands in for that template wherever the pack draws it, in every form of the project, and every other template stays the pack's. It needs nothing but the file: no setting of the pack's, no Python and no change to a form. A replacement is a whole template, since the pack's templates have no blocks to override, and it is the host project's own: the pack adds nothing to it and does not check it. A layout object's own `template=`, a helper's `field_template` and a helper's `template` still win for the form that sets them.

A replacement is found by one of two routes, and the last column of the list below says which:

- The templates outside `daisyui/widgets/` and `mvp_forms/widgets/` are found through `TEMPLATES`. Put the replacement in a directory listed in `DIRS`, or in the `templates` directory of an app listed in `INSTALLED_APPS` before `mvp_forms`.
- The templates under `daisyui/widgets/` and `mvp_forms/widgets/` are loaded by the form renderer, and Django's default renderer does not read `TEMPLATES`. It looks in Django's own form templates and then in the `templates` directory of each installed app, in order, so with the default renderer a replacement is found only in an app listed before `mvp_forms`. A project that keeps it in a `DIRS` directory sets `FORM_RENDERER = "django.forms.renderers.TemplatesSetting"` and adds `"django.forms"` to `INSTALLED_APPS`, so Django's own widget templates are still found.

An app listed after `mvp_forms` is never used. Once django-crispy-forms has loaded `daisyui/field.html`, `daisyui/uni_form.html`, `daisyui/uni_formset.html`, `daisyui/whole_uni_form.html` or `daisyui/whole_uni_formset.html` it keeps it in memory, so restart the development server after you add or edit a replacement for one of those five.

#### A required marker of your own

The pack draws a required field's marker with `daisyui/required_marker.html`, a star that assistive technology skips. To draw an abbreviation with a translated title instead, put this file at `daisyui/required_marker.html` in a directory listed in your `TEMPLATES` setting's `DIRS`:

```django
{% load i18n %}{% if field.field.required %} <abbr title="{% translate "required" %}">*</abbr>{% endif %}
```

Every required field in the project now carries that marker, in its label, in a group's legend and in a table's column heading, and every other template is still the pack's. The template reads `field`, which is what its row in the list below says it is handed.

#### The templates

Each row is one template the pack distributes. `Draws` says what it draws. `Handed` lists the names the pack's own template reads from outside itself, which a replacement can read too: a value Django or django-crispy-forms supplies is listed by its name alone, and `drawn` and `table`, which the pack supplies, are listed one level down, by the part read, as `drawn.is_group`. A template that sets `drawn` or `table` itself is not handed it and lists none, and `daisyui/frame.html` and `daisyui/field_body.html` are handed `drawn` by whichever template includes them. `Found by` is the route above.

The pack's own template tags also read the page's context, which no template shows. For example `daisyui_field` reads `form_show_labels`, `form_show_errors` and `wrapper_class`, and `daisyui_layout_object` reads `form` and `template_pack`. A replacement that calls a tag gets what the pack's template gets. The list covers what is written in a template and not what the tags read.

Two tags carry the form's size to the buttons the pack draws inside a container. `{% daisyui_button_size "btn-sm" %}` writes the class of the size stated for the form, or by a `Choice` around the layout object, and the class it is given when none is stated. django-crispy-forms draws a `Modal` with no context, so no tag in `daisyui/layout/modal.html` can read the form's size: the template writes the class `daisyui-size` on its close button, a `Choice` around the modal replaces it with its own size, and `{% daisyui_sized form.form_html %}` in `daisyui/display_form.html` replaces what is left with the form's, or removes it. A replacement for `daisyui/display_form.html` that draws `{{ form.form_html }}` without that tag leaves `daisyui-size` on the button, where it does nothing, and a replacement for `daisyui/layout/modal.html` that leaves the class out draws a close button that keeps one size. Both are `mvp_forms.choices.write_size` at work, which you do not call.

| Template | Draws | Handed | Found by |
|---|---|---|---|
| `daisyui/whole_uni_form.html` | The whole form that `{% crispy form %}` draws: the `<form>` element when the helper asks for one, a CSRF token for a post, the fields and the helper's buttons. | `csrf_token`, `disable_csrf`, `flat_attrs`, `form`, `form_method`, `form_tag` | `TEMPLATES` |
| `daisyui/display_form.html` | The form's media, its form-wide errors and then its fields, or the form's own `form_html` in their place when it has one, drawn through `{% daisyui_sized %}`, which writes the form's size on the close button of each `Modal` in it. | `form`, `form_show_errors`, `include_media` | `TEMPLATES` |
| `daisyui/uni_form.html` | The form's media, its form-wide errors and each of its fields with no `<form>` element around them, which is what the `crispy` filter asks for when it is given a form. | `field_template`, `form`, `form_show_errors`, `include_media` | `TEMPLATES` |
| `daisyui/errors.html` | The errors of the form as a whole in one alert under the helper's error title, and nothing for a form that has none. | `form`, `form_error_title` | `TEMPLATES` |
| `daisyui/inputs.html` | The helper's buttons and inputs, with the hidden inputs first and the rest in a row. | `inputs` | `TEMPLATES` |
| `daisyui/field.html` | One field: the pack draws the field's widget and the frame puts it in place. | `field` | `TEMPLATES` |
| `daisyui/frame.html` | The frame around a field's widget: a daisyUI fieldset holding the label, or the legend of a group, with the required marker, and then the field's body, and a hidden field is its input alone. | `drawn.group_description`, `drawn.is_floating`, `drawn.is_group`, `drawn.is_single_checkbox`, `drawn.label_text`, `drawn.show_labels`, `drawn.wrapper_class`, `field`, `label_class` | `TEMPLATES` |
| `daisyui/field_body.html` | What sits inside the frame: the widget, which may be a single checkbox in its own label, have text attached, have buttons joined to it or sit in a floating label, then the field's help text and its errors, which `daisyui/field_messages.html` draws. | `buttons`, `drawn.appended`, `drawn.attached_class`, `drawn.has_attached_text`, `drawn.is_floating`, `drawn.is_joined`, `drawn.is_single_checkbox`, `drawn.join`, `drawn.prepended`, `drawn.render`, `drawn.show_labels`, `field`, `field_class`, `label_class` | `TEMPLATES` |
| `daisyui/field_messages.html` | A field's help text, with the id that the input's description names, and its errors in one element with an id of its own, unless the form turns errors off. A joined group draws it once for each of its members. | `field`, `form_show_errors` | `TEMPLATES` |
| `daisyui/required_marker.html` | The marker a required field's label and a required column's heading carry, and nothing for an optional field. | `field` | `TEMPLATES` |
| `daisyui/multifield.html` | A field inside a `MultiField`, drawn as any field is: it reads nothing itself and passes `field` on to `daisyui/field.html`. | `field` | `TEMPLATES` |
| `daisyui/layout/fieldset.html` | A `Fieldset`: a daisyUI fieldset with its legend, holding its fields. | `fields`, `fieldset`, `legend` | `TEMPLATES` |
| `daisyui/layout/div.html` | A `Div`: a `<div>` holding its fields, or the pane of a tab when it is one. | `div`, `fields` | `TEMPLATES` |
| `daisyui/layout/row.html` | A `Row`: a `<div>` that lays its fields out along a row. | `div`, `fields` | `TEMPLATES` |
| `daisyui/layout/column.html` | A `Column`: a `<div>` that takes an equal share of its row and holds its fields. | `div`, `fields` | `TEMPLATES` |
| `daisyui/layout/tab.html` | A `TabHolder`: a `<div>` holding the tabs it is given, whose radio inputs share one group name. | `content`, `tabs` | `TEMPLATES` |
| `daisyui/layout/tab-pane.html` | One `Tab`: a radio input that names and selects it, and its pane holding its fields. | `div`, `fields` | `TEMPLATES` |
| `daisyui/layout/tab-link.html` | Nothing: django-crispy-forms renders it for every tab and hands the result to `daisyui/layout/tab.html` as `links`, which the pack's `tab.html` does not draw, so a replacement shows only beside a replacement of `tab.html` that draws `links`. |  | `TEMPLATES` |
| `daisyui/accordion.html` | An `Accordion`: a `<div>` stacking its groups. | `accordion`, `content` | `TEMPLATES` |
| `daisyui/accordion-group.html` | An `AccordionGroup`: a collapsible `<details>` with its name as the summary, holding its fields. | `div`, `fields` | `TEMPLATES` |
| `daisyui/layout/modal.html` | A `Modal`: a `<dialog>` with its title, its fields and a button that closes it, open when a field in it fails. The button carries the class `daisyui-size` where its size goes, which whatever draws around the modal replaces. | `fields`, `modal` | `TEMPLATES` |
| `daisyui/layout/alert.html` | An `Alert`: its content in an element with `role="alert"`, and a button that dismisses it when it can be dismissed, sized by `{% daisyui_button_size %}`. | `alert`, `content`, `dismiss` | `TEMPLATES` |
| `daisyui/layout/multifield.html` | A `MultiField`: a fieldset with its label as the legend, holding its fields. | `fields_output`, `multifield` | `TEMPLATES` |
| `daisyui/layout/buttonholder.html` | A `ButtonHolder`: a row holding its buttons. | `buttonholder`, `fields_output` | `TEMPLATES` |
| `daisyui/layout/formactions.html` | `FormActions`: a row holding its buttons. | `fields_output`, `formactions` | `TEMPLATES` |
| `daisyui/layout/button.html` | A `StrictButton`: a `<button>` element holding its content. | `button` | `TEMPLATES` |
| `daisyui/layout/baseinput.html` | A `Submit`, `Button`, `Reset` or `Hidden`: one `<input>` with the type, name and value the layout object gives it. | `input` | `TEMPLATES` |
| `daisyui/layout/prepended_appended_text.html` | A `PrependedText`, `AppendedText` or `PrependedAppendedText`: a field with text before or after its input, in the field's frame. | `crispy_appended_text`, `crispy_prepended_text`, `field` | `TEMPLATES` |
| `daisyui/layout/field_with_buttons.html` | A `FieldWithButtons`: a field's input joined to its buttons, in the field's frame. | `div`, `field` | `TEMPLATES` |
| `daisyui/layout/join.html` | A `Join`: a fieldset with the group's label as its legend, the visible members as the children of one element that carries `join`, the hidden members after it and the help text and errors of each member. | `form_show_labels`, `hidden`, `inputs`, `join`, `label_class`, `members`, `required` | `TEMPLATES` |
| `daisyui/layout/join_member.html` | One member of a `Join`: a field drawn as an input or a select of the join, or as its hidden input when it is hidden. | `field` | `TEMPLATES` |
| `daisyui/layout/inline_field.html` | An `InlineField`: a field with no visible label, named by an `aria-label`, in the field's frame. | `field` | `TEMPLATES` |
| `daisyui/layout/uneditable_input.html` | An `UneditableField`: a field's input disabled and showing the field's value, in the field's frame. | `field` | `TEMPLATES` |
| `daisyui/layout/radioselect_inline.html` | An `InlineRadios`: a radio group with its options along a line, in the field's frame. | `field` | `TEMPLATES` |
| `daisyui/layout/checkboxselectmultiple_inline.html` | An `InlineCheckboxes`: a checkbox group with its options along a line, in the field's frame. | `field` | `TEMPLATES` |
| `daisyui/whole_uni_formset.html` | The whole formset that `{% crispy formset %}` draws: the `<form>` element when the helper asks for one, a CSRF token for a post, the forms and the helper's buttons. | `csrf_token`, `disable_csrf`, `flat_attrs`, `formset`, `formset_method`, `formset_tag` | `TEMPLATES` |
| `daisyui/uni_formset.html` | The formset's media, its management form, its formset-wide errors and its forms one after another with a divider between them, which is what the `crispy` filter asks for when it is given a formset. | `form_show_errors`, `formset`, `include_media` | `TEMPLATES` |
| `daisyui/errors_formset.html` | The errors of the formset as a whole in one alert under the helper's formset error title, and nothing for a formset that has none. | `formset`, `formset_error_title` | `TEMPLATES` |
| `daisyui/table_inline_formset.html` | A formset as one table with a row for each form and a column for each visible field, chosen by setting the helper's `template`. | `csrf_token`, `disable_csrf`, `field_template`, `flat_attrs`, `form_show_errors`, `formset`, `formset_method`, `formset_tag`, `include_media` | `TEMPLATES` |
| `daisyui/widgets/group.html` | A radio group or a checkbox group with its options one under another. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/inline_group.html` | A radio group or a checkbox group with its options along a line, wrapping onto the next line. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/group_options.html` | The options of a radio group or a checkbox group, each an input in a label of its own, under a nested fieldset where the choices have group names, which the two group templates include. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/rating.html` | A field drawn as a rating: the element that holds the stars and one radio input for each choice, where `widget` also holds `rating_class`, the classes of that element, and `inputs`, the choices in the order they are drawn, the one that clears the rating first. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/select_date.html` | A date drawn by `SelectDateWidget`: a select for each part of the date, side by side. | `widget` | `FORM_RENDERER` |
| `mvp_forms/widgets/partial_date.html` | A partial date drawn by `PartialDateInput` or `PartialDateSelect`: one element that holds a year, a month and a day side by side, each a part of one field. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/clearable_file_input.html` | A clearable file input: the link to the file held, a removal checkbox when the field is optional, and the file input, where `widget` also holds `removal_class`, which the pack adds for the removal checkbox's size and colour. | `widget` | `FORM_RENDERER` |
| `daisyui/widgets/attrs.html` | The attributes of a widget or of one of its options, written inside the tag that includes it. | `widget` | `FORM_RENDERER` |

#### A supported package's templates

A template under `django_tomselect/` is a template of django-tomselect that the pack extends. It is not a replacement for one of the pack's own, and it has no `Handed` column because it reads nothing of its own: it extends django-tomselect's template of the same path and adds to a block of it.

| Template | Draws | Found by |
|---|---|---|
| `django_tomselect/tomselect.html` | django-tomselect's own template with one block added: an option that carries an `optgroup` key is listed under a heading of that name. | Application directories: list `mvp_forms` before `django_tomselect` in `INSTALLED_APPS`, since the first app that has the template supplies it and the other is never used. |

#### When a listed template changes

A listed path, and the names a template is handed, change only through one minor version in which the old one still works. For that version a replacement at the old path is still drawn, and it raises a `DeprecationWarning` naming the old path and what replaces it. A project with nothing at the old path sees no warning. Python shows a `DeprecationWarning` under a test runner, or when you run with `python -W default`, as it does Django's own, so run your tests to find a replacement that needs moving. A name a template is handed that is renamed or withdrawn keeps its value under the old name for that version. The CHANGELOG entry of that release says what changed and what replaces it. The pack records the paths it has moved away from in `mvp_forms.deprecation.WITHDRAWN` and asks `mvp_forms.deprecation.host_template` whether your project has a template at one, so you call neither.

A path on its way out stays a row of the table for as long as it is honoured, with what replaces it said in its `Draws` cell. The paths django-crispy-forms itself chooses, such as `daisyui/field.html`, change only if django-crispy-forms changes them.

The markup and the class names inside a template of the pack are not part of this promise and can change in any release. A replacement that copied the old markup keeps drawing it until its owner updates it.

### django-tomselect

The pack draws the select widgets of [django-tomselect](https://github.com/OmenApps/django-tomselect) so that they sit in a daisyUI form as a stock select does. It covers the single and the multiple widget, over a model and over a list of choices: `TomSelectModelWidget`, `TomSelectModelMultipleWidget`, `TomSelectIterablesWidget` and `TomSelectIterablesMultipleWidget`, which `TomSelectModelChoiceField`, `TomSelectModelMultipleChoiceField`, `TomSelectChoiceField` and `TomSelectMultipleChoiceField` build. django-tomselect is not a dependency of the package and no module of the package imports it, so a project without it is drawn as before.

`{{ form|crispy }}` and `{% crispy form %}` write nothing new for these widgets. They write daisyUI's `select` class on the `<select>` with `w-full`, the size, the colour and the variant stated for the form or for the field, and `select-error` in place of the colour on a field in error, exactly as for a stock select. A disabled field carries the `disabled` attribute and its label is tied to the select. Tom Select copies the classes of the element it replaces to the wrapper it builds, so the wrapper is a daisyUI select, and the dropdown sits inside it and takes its size from it. The package ships one stylesheet, `mvp_forms/tomselect.css`, that fits Tom Select's own parts, its tags, its dropdown and its clear button, inside them. Every colour, radius and size in it comes from the daisyUI theme, so a control follows the theme as a stock select does, and the stylesheet styles nothing outside a control. The pack never writes a link to the stylesheet. Load it yourself, once.

#### What to install and load

1. Install django-tomselect and set it up as its documentation says. A model-backed widget reads the current request, so `django_tomselect.middleware.TomSelectMiddleware` is in `MIDDLEWARE`.
2. List `mvp_forms` in `INSTALLED_APPS`, as above, so that Django's static files finder serves `mvp_forms/tomselect.css`.
3. On every page that draws a django-tomselect select, load django-tomselect's two stylesheets, `mvp_forms/tomselect.css` and django-tomselect's script:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'django_tomselect/vendor/tom-select/css/tom-select.default.css' %}" />
<link rel="stylesheet" href="{% static 'django_tomselect/css/django-tomselect.css' %}" />
<link rel="stylesheet" href="{% static 'mvp_forms/tomselect.css' %}" />
<script src="{% static 'django_tomselect/js/django-tomselect.min.js' %}"></script>
```

The stylesheets can be loaded in either order. django-tomselect's also arrive with a form's media, which `{% crispy form %}` writes beside the form, after anything in the page's head, and `mvp_forms/tomselect.css` is written to win either way. Without `mvp_forms/tomselect.css` the control still works and is drawn by django-tomselect alone, but daisyUI hides whatever overflows a select, so the dropdown, which Tom Select builds inside the wrapper, is cut off. A page that loads the stylesheet and draws no django-tomselect select is drawn as before.

On Django 6.1, django-tomselect's `{% tomselect_media %}` tag writes no links and logs an error, because form media holds objects where it expects strings. Load the files by path, as above, or through form media, which `{% crispy form %}` writes beside the form. The controls work on Django 6.1 when their files are loaded.

The package also distributes one template of its own for django-tomselect, `django_tomselect/tomselect.html`, which extends django-tomselect's template of the same path. It is listed with the other templates, under [a supported package's templates](https://github.com/django-mvp/django-mvp-forms#a-supported-packages-templates), and Django finds it ahead of django-tomselect's own only when `mvp_forms` is listed before `django_tomselect` in `INSTALLED_APPS`.

#### One look

The look that is supported is django-tomselect's `default`, which is what its `css_framework` setting holds unless you change it. The Bootstrap 4 and Bootstrap 5 looks are not supported: leave `DEFAULT_CSS_FRAMEWORK` out of the `TOMSELECT` setting or set it to `default`.

#### Size, colour, variant and state

A control takes the size, the colour and the variant stated for the form or for the field by the rules of [Size, colour and variant](https://github.com/django-mvp/django-mvp-forms#size-colour-and-variant), with the names a stock select takes. State them as for any other field:

```python
from crispy_forms.helper import FormHelper
from django import forms
from django_tomselect.app_settings import PluginClearButton, TomSelectConfig
from django_tomselect.forms import TomSelectChoiceField

from mvp_forms.choices import FormChoices


class TripForm(forms.Form):
    country = TomSelectChoiceField(
        config=TomSelectConfig(
            url="country-autocomplete",
            value_field="value",
            label_field="label",
            plugin_clear_button=PluginClearButton(),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(size="sm", color="primary")
```

A control is drawn at rest, focused, in error, disabled and open. A control in error is drawn with the error state and none of the colour stated. The label, the required marker, the help text and the errors are tied to the select as they are to a stock select.

#### Plugins

The clear button, `PluginClearButton`, and the remove button on each tag of a multiple control, `PluginRemoveButton`, are drawn. Another plugin works and keeps django-tomselect's own look. Support for another is added when a project asks for it.

#### Tagging

Tagging is a multiple control that offers to add what was typed. Each value is a tag with a remove button, and when the typed text matches no option the dropdown begins with a line to add it, set apart from the options below by a rule. Turn it on with `create=True` in the `TomSelectConfig` of a multiple control that has `PluginRemoveButton`, and the stylesheet draws the tags, the tag the keyboard is on and the line that offers to add a value.

The pack draws the control and nothing more. Saving a new value is yours: django-tomselect posts it as it posts any other, and what your view does with it is up to you. The field has to accept it first, and django-tomselect's stock fields do not. `TomSelectMultipleChoiceField` and `TomSelectModelMultipleChoiceField` reject a value that is not among their choices, so a form with a new tag comes back in error. Write a field of your own that accepts any value, as the demo's `TagsField` does:

```python
from django import forms
from django_tomselect.app_settings import PluginRemoveButton, TomSelectConfig
from django_tomselect.forms import TomSelectMultipleChoiceField


class TagsField(TomSelectMultipleChoiceField):
    def clean(self, value):
        if self.required and not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )
        return list(value or [])


class ArticleForm(forms.Form):
    keywords = TagsField(
        config=TomSelectConfig(
            url="keyword-autocomplete",
            value_field="value",
            label_field="label",
            create=True,
            plugin_remove_button=PluginRemoveButton(),
        ),
        required=False,
    )
```

`cleaned_data["keywords"]` is then a list of strings, whether or not each is among the options, and your view decides which of them to save.

#### Grouping

An option can be listed under a heading. Give the option an `optgroup` key whose value is the heading, and every option that carries the same value is listed under it. An option with no `optgroup` key, or an empty one, is listed with no heading. django-tomselect draws the headings and has no setting that names an option's group, so the pack's `django_tomselect/tomselect.html` tells Tom Select to read the group from `optgroup`. You write no template.

A value the control already holds when the page is drawn is added by django-tomselect with its value and label only. If you keep chosen options in the dropdown with `hide_selected=False`, that one is listed with no heading until it is fetched again.

This works only when `mvp_forms` is listed before `django_tomselect` in `INSTALLED_APPS`, because Django uses the first template of a name that it finds. With the order reversed the control is still drawn, with its options in one flat list.

A view names the group on each result. A view over a list of choices does it in `get_iterable`; a view over a model does it in `hook_prepare_results`, from a field it asked for in `value_fields`:

```python
from django_tomselect.autocompletes import (
    AutocompleteIterablesView,
    AutocompleteModelView,
)

from shop.models import Product

ROCKS = {"Igneous": ["Basalt", "Granite"], "Sedimentary": ["Chalk", "Shale"]}


class RockAutocomplete(AutocompleteIterablesView):
    iterable = True

    def get_iterable(self):
        return [
            {"value": rock, "label": rock, "optgroup": group}
            for group, rocks in ROCKS.items()
            for rock in rocks
        ]


class ProductAutocomplete(AutocompleteModelView):
    model = Product
    search_lookups = ["name__icontains"]
    value_fields = ["id", "name", "category__name"]

    def hook_prepare_results(self, results):
        for result in results:
            result["optgroup"] = result.pop("category__name")
        return results
```

A project that has a `django_tomselect/tomselect.html` of its own keeps the grouping by extending the template of the same name: `{% extends "django_tomselect/tomselect.html" %}`. Django resolves that to the next template of that name, which is the pack's, and the pack's extends django-tomselect's.

#### In a modal and in a table

A control works inside a `Modal` layout object and inside a formset drawn as a table with no change to either. The stylesheet does two things for them. An open control is lifted above the controls after it, and the two boxes that would otherwise cut off its dropdown, daisyUI's modal box and the scroller around a table, show what overflows them for as long as a dropdown inside is open. A modal or a table that has been scrolled loses its scroll position while that lasts, because a box that shows its overflow does not scroll. Give a form in a modal a prefix, so that the ids and the button names inside it do not repeat those of the page. The formset's own prefix keeps the controls of each row apart.

#### Loaded by htmx

A form that htmx swaps into the page has its controls started as it arrives, provided `use_htmx` is on. Turn it on once, for every control, in the `TOMSELECT` setting:

```python
TOMSELECT = {"DEFAULT_CONFIG": {"use_htmx": True}}
```

Without it a control's script starts the control when the document finishes loading, and a swapped-in form is not a document load. The package changes nothing to make this automatic. Give each form you fetch a prefix of its own, such as one that counts the fetches, so that a second copy swapped in beside or over the first does not repeat its ids. The stylesheet needs nothing more, since it is already loaded by the page that fetches. A page reached by htmx navigation starts its controls in the same way.

#### What is not supported

- django-tomselect's token widget, `TomSelectTokenWidget`, which the stylesheet does not style.
- django-tomselect's Bootstrap looks.
- A floating label, text attached to a control, buttons joined to it and a joined group that holds it. The pack does not change what it draws when one is asked for.

#### The release tested

The support is tested against django-tomselect 2026.6.2, which the development dependencies name as the least release. That release declares Django up to 6.0, and its controls work on Django 6.1, apart from the `{% tomselect_media %}` tag above. Which releases of django-tomselect are supported is stated here and is not part of the [support window](https://github.com/django-mvp/django-mvp-forms#supported-versions), whose periods apply to Django, django-crispy-forms and daisyUI.

### Input masks

A mask is a rule [IMask](https://imask.js.org/) applies to a text input as a person types: it decides what can be typed and how it is shown. The package gives a developer a widget to name on a field, and one script that hands what the widget wrote to IMask. The widgets add nothing to validation, so a field cleans and validates exactly as it did.

This is the public surface:

- `mvp_forms.widgets.PatternMaskInput`, with the three blocks it takes, `RangeBlock`, `EnumBlock` and `PatternBlock`, from the same module
- `mvp_forms.widgets.RegexMaskInput`
- `mvp_forms.widgets.NumberMaskInput`
- `mvp_forms.widgets.DynamicMaskInput`
- the attribute `data-imask`, which holds a widget's options as JSON on its `<input>`
- the script `mvp_forms/imask.js`, which each widget names in its media
- the event `mvp-forms:imask`, which the script sends from each input once its mask is applied, with the IMask instance in `event.detail.mask`

The widgets are written for IMask 7, and the package's tests run against 7.6.1. IMask is not a dependency of the package and the package does not distribute it.

#### What to load

Two things have to be on a page that draws a masked field: IMask, and the form's media, which names the script.

```django
<script src="https://cdn.jsdelivr.net/npm/imask@7.6.1/dist/imask.min.js"
        integrity="sha384-UO8YwPv//GjwHj93ZlwXcDNjv3BSxdBFUB2jtiOuL3d/a0kS9E8sYvHjTBkQI8u8"
        crossorigin="anonymous"></script>
{{ form.media }}
```

- `{% crispy form %}` writes the form's media inside the form, so the page template writes only IMask. A page with several forms drawn this way holds the script once for each of them, and the script acts once however often it is included.
- `{{ form|crispy }}`, `{{ field|as_crispy_field }}` and Django's own form rendering write no media. Render `{{ form.media }}` in the page template, or load `{% static 'mvp_forms/imask.js' %}` yourself.
- The script waits for the document to finish loading before it looks for IMask, so it may be written before or after IMask, as long as IMask is loaded by the time the document has finished loading. An IMask loaded later than that, with `async` for example, is not found for the inputs already on the page. A project that bundles IMask exposes it as `window.IMask`, the name IMask publishes, and the widgets work as they do with the copy from a CDN.
- The script is a file and the widgets write no inline script and no inline handler. A page whose Content Security Policy allows scripts from its own origin and from the origin serving IMask, and forbids inline script, masks every field.
- A project that uses none of these widgets never loads the script. The pack's own templates still need no script.

A page that does not load IMask draws every masked field as an ordinary text input. Nothing is masked, no error is raised in the browser, and the form submits.

#### `PatternMaskInput`

The pattern is written as [IMask's pattern text](https://imask.js.org/guide.html#masked-pattern), unchanged. In it `0` stands for a digit, `a` for a letter and `*` for any character, a part in square brackets is optional, and every other character is fixed.

```python
from django import forms

from mvp_forms.widgets import PatternMaskInput


class BookingForm(forms.Form):
    phone = forms.CharField(widget=PatternMaskInput("+{49} 000 0000000"))
    reference = forms.CharField(
        widget=PatternMaskInput(
            "aa-0000", lazy=False, placeholder_char={"0": "#", "a": "a"}
        )
    )
```

`PatternMaskInput(mask, attrs=None, *, definitions=None, blocks=None, lazy=None, placeholder_char=None, overwrite=None, eager=None, display_char=None)`. Every option is written on the input under IMask's own name, and an option you do not state is not written, so IMask's default applies.

| Option | IMask's name | What it does |
|---|---|---|
| `definitions` | `definitions` | A mapping from one character to the regular expression it stands for, written as text in JavaScript's dialect: `{"S": "[1-6]"}` |
| `blocks` | `blocks` | A mapping from a name used in the pattern to a block, described below |
| `lazy` | `lazy` | `False` shows the whole pattern, with its placeholder, before anything is typed. A field nothing was typed into submits nothing, and a field partly filled in submits what is shown, placeholder characters included |
| `placeholder_char` | `placeholderChar` | One character shown in each open position, or a mapping from a definition's character to the character shown for it: `{"0": "#", "a": "a"}` |
| `overwrite` | `overwrite` | `True` has what is typed replace what is there, and `"shift"` has it replace and shift the rest |
| `eager` | `eager` | `True` writes the fixed characters ahead of the cursor, `"append"` and `"remove"` do so in one direction only |
| `display_char` | `displayChar` | The character shown in place of what was typed, for a PIN |

A mapping for `placeholder_char` may name `0`, `a`, `*` and any definition you state. For one of IMask's three own definitions the script reads the expression from IMask, so the package holds no copy of it.

A value that cannot be right raises `ValueError` when the form class is defined, and its message names the option: an empty or non-text pattern, a definition that is not one character and text, a placeholder or display character that is not one character, a block that is not one of the three classes, and an `overwrite` or `eager` that is not one of the values above. An option the widget does not have is Python's own `TypeError`.

Your own `attrs` are kept. A pattern holding a quote or an angle bracket is escaped as any attribute value is.

#### Blocks

A block is a named part of a pattern with a rule of its own. Name it in `blocks` and write its name in the pattern.

```python
from mvp_forms.widgets import EnumBlock, PatternBlock, PatternMaskInput, RangeBlock

date = PatternMaskInput(
    "d{.}`m{.}`Y",
    lazy=False,
    overwrite=True,
    blocks={
        "d": RangeBlock(1, 31, max_length=2, placeholder_char="d"),
        "m": RangeBlock(1, 12, max_length=2, placeholder_char="m"),
        "Y": RangeBlock(1900, 2100, placeholder_char="y"),
    },
)
resolution = PatternMaskInput("Q", blocks={"Q": EnumBlock(["HD", "TV", "VR"])})
serial = PatternMaskInput("N", blocks={"N": PatternBlock("0", repeat=4)})
```

| Block | What it takes |
|---|---|
| `RangeBlock(minimum, maximum, *, max_length=None, autofix=None, placeholder_char=None)` | A whole number between the bounds. `max_length` is the number of digits, and `autofix=True` corrects a number outside the bounds to the nearest one. A bound or a `max_length` that is not a whole number, and a minimum above the maximum, raise `ValueError` |
| `EnumBlock(values, *, placeholder_char=None)` | One of a list of values. An empty list, and anything that is not a list of text, raise `ValueError` |
| `PatternBlock(mask, *, repeat=None, placeholder_char=None)` | A pattern of its own, repeated `repeat` times when that is stated |

A date is masked with a pattern whose day, month and year are ranges, and Django's `DateField` reads the result through `input_formats`.

#### `RegexMaskInput`

A [regular expression mask](https://imask.js.org/guide.html#masked-base) accepts a character only while the whole value still matches the expression. Use it where a field has no fixed shape but a limited alphabet: digits only, letters and hyphens, a hexadecimal colour.

```python
from django import forms

from mvp_forms.widgets import RegexMaskInput


class AccountForm(forms.Form):
    customer_number = forms.CharField(widget=RegexMaskInput(r"^\d{0,8}$"))
    colour = forms.CharField(widget=RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i"))
```

`RegexMaskInput(mask, attrs=None, *, flags=None)`. `mask` is the expression as text, and `flags` is its flags as text, such as `"i"` for a match that ignores case. Both are written on the input and IMask runs them in the browser, so the expression is written in JavaScript's dialect and Python never compiles it. A difference between the two dialects, such as `(?<name>...)` for a named group, is yours to mind.

An empty or non-text `mask`, which includes a compiled Python pattern, and a flag JavaScript does not have (`d`, `g`, `i`, `m`, `s`, `u`, `v` and `y` are the ones it has) raise `ValueError` when the form class is defined, and the message names the option.

IMask tests the value after every keystroke, so the expression has to accept every partial value on the way to a whole one. An expression that matches only a finished value, such as `^\d{5}$`, accepts no first character and the field cannot be typed into. Write `^\d{0,5}$` instead, and let the field's own validation decide that five digits were required.

#### `NumberMaskInput`

A [number mask](https://imask.js.org/guide.html#masked-number) writes the separators as a number is typed: `1 234 567,5` appears as `1234567,5` is keyed in. The field receives the plain number, so a `DecimalField` or an `IntegerField` needs no cleaning code.

```python
from django import forms

from mvp_forms.widgets import NumberMaskInput


class InvoiceForm(forms.Form):
    amount = forms.DecimalField(
        widget=NumberMaskInput(scale=2, thousands_separator=" ", radix=",")
    )
    quantity = forms.IntegerField(
        widget=NumberMaskInput(scale=0, min_value=0, max_value=100, autofix=True)
    )
```

`NumberMaskInput(attrs=None, *, scale=None, thousands_separator=None, radix=None, map_to_radix=None, pad_fractional_zeros=None, normalize_zeros=None, min_value=None, max_value=None, autofix=None)`. An option you do not state is not written, so IMask's default applies: two decimal places, no thousands separator and a comma as the decimal mark.

| Option | IMask's name | What it does |
|---|---|---|
| `scale` | `scale` | The number of decimal places. `0` takes whole numbers only |
| `thousands_separator` | `thousandsSeparator` | The character between groups of three digits, or `""` for none |
| `radix` | `radix` | The decimal mark, one character |
| `map_to_radix` | `mapToRadix` | A list of other characters to read as the decimal mark |
| `pad_fractional_zeros` | `padFractionalZeros` | `True` pads the decimal places with zeros |
| `normalize_zeros` | `normalizeZeros` | `False` keeps needless zeros |
| `min_value` | `min` | The smallest value, an `int`, a `float` or a `Decimal`, written as a JSON number |
| `max_value` | `max` | The largest value, of the same kinds |
| `autofix` | `autofix` | `True` corrects a value outside the bounds to the nearest one |

A value that cannot be right raises `ValueError` when the form class is defined, and its message names the option: a negative `scale`, a `thousands_separator` or `radix` that is more than one character, a `thousands_separator` that is the decimal mark (a comma when you state no `radix`, so `NumberMaskInput(thousands_separator=",")` is refused until you state `radix="."`), a `map_to_radix` that is not a list of single characters, a `min_value` or `max_value` that is not a finite number, and a `min_value` above the `max_value`.

The input is a text input, since IMask masks no other type, and it asks a touch device for a decimal keypad, or a numeric one when `scale=0`. An `inputmode` in your `attrs` replaces that.

The widget reads and writes the number by one rule, with IMask on the page or not:

- A submitted value has its thousands separator removed and its decimal mark written as a full stop, so `1 234 567,5` reaches the field as `1234567.5`, a negative keeps its sign, and an empty value stays empty.
- A value the form is drawn with, a `Decimal`, a number or a plain string such as `"1234.5"`, is written with the widget's decimal mark and no thousands separator: `1234,5`. IMask adds the separators when it applies the mask, and without IMask the same text reads back as the same number. The widget does not localise the value, whatever the field's `localize` says, because its own options say how the number is written.

A page that does not load IMask shows the number as the widget wrote it, with no separators, and the field still reads what is typed by the rule above. A person who types `1234.56` where the decimal mark is a comma and the thousands separator a full stop therefore submits `123456`, since the full stop is dropped as a separator. The field's own validation is what catches a number that is not what was meant.

#### `DynamicMaskInput`

A [dynamic mask](https://imask.js.org/guide.html#masked-dynamic) is a list of masks. As a person types, IMask applies the mask from the list that takes the most of what has been typed, and the earlier one where two take the same. Use it where one field takes values of more than one shape: a phone number of two lengths, a card number of two.

```python
from django import forms

from mvp_forms.widgets import DynamicMaskInput, PatternMaskInput


class ContactForm(forms.Form):
    phone = forms.CharField(
        widget=DynamicMaskInput(
            [PatternMaskInput("000-0000"), PatternMaskInput("(000) 000-0000")]
        )
    )
```

`DynamicMaskInput(masks, attrs=None)`. `masks` is a list of `PatternMaskInput`, `RegexMaskInput` and `NumberMaskInput` widgets, in the order IMask tries them, and each is written with its own options. Only a widget's options are used: its `attrs` are not, and the way a `NumberMaskInput` reads and writes a number is not. The widget takes no options of its own, since which mask applies is IMask's decision.

An empty list, a value that is not a list, and an item that is not one of the three widgets (another `DynamicMaskInput` included) raise `ValueError` when the form class is defined, and the message names `masks`.

The field receives the submitted text unchanged, as it does from a pattern or a regular expression, including where a mask in the list is a number. A list that holds a pattern with a `display_char` shows that character and submits what was typed.

#### Inputs added later

The script applies a mask to each masked input on the page when it loads, and then watches the document for inputs added afterwards. A formset row added by a script, a form that htmx 2 swaps into the page and a node your own script inserts all get their mask with no script of yours, and so does a field in a `Modal`, which is masked before the dialog is opened. Each input has one mask: an input moved within the page keeps its mask, and a page that includes the script more than once masks each input once.

A formset's `empty_form`, the template a script clones to add a row, is drawn through the same widget, so it carries the same `data-imask` as the rows beside it.

A disabled or a read-only masked input shows its value under the mask and stays disabled or read-only. A disabled input adds no entry to the form's data, as for any input.

#### The event

An option that is a JavaScript function, or any other option the widgets do not carry, is set in a few lines of your own script. The script sends the event `mvp-forms:imask` from each input once its mask is applied. The event bubbles, so a listener on the document hears every input, including one added after the page loaded, and `event.detail.mask` is the [IMask instance](https://imask.js.org/guide.html). Change an option on it with `updateOptions` and it applies to what is typed next.

```js
document.addEventListener("mvp-forms:imask", (event) => {
  if (event.target.id !== "id_reference") return;
  event.detail.mask.updateOptions({
    prepareChar: (char) => char.toUpperCase(),
  });
});
```

Register the listener before the script runs, so that it hears the inputs that are already on the page: write it in a script that comes before the form's media. Where the page's Content Security Policy forbids inline script, the listener goes in a file or carries a nonce, like any other script.

#### What the form receives

A pattern, a regular expression or a list of masks hands the field the text as the person saw it, fixed characters included, and the field cleans it as it would any text. A number mask hands it the plain number, as described above. A pattern submitted half filled in reaches the field half filled in, with its placeholder characters where `lazy=False` shows them, and whether that is acceptable is the field's validation to decide: add a validator to a field that must match a shape. A pattern nothing was typed into submits nothing, whatever placeholder it shows, so a required field left untouched is still reported as empty.

A field with a `display_char` shows that character, and the form receives what was typed. In these two cases, a display character and an untouched placeholder, the script sets the field's entry in the form's data when the form's data is read, which covers a native submit and a script that builds a `FormData` from the form, as htmx 2 does. Every other masked input is submitted by the browser as it shows. So is any masked input whose value was changed without typing, by a reset button or by a script that assigns to it: the form receives what the input then shows. A masked input that has been removed from its form, is disabled by itself or by a `<fieldset>`, or has no name adds no entry.

Options IMask refuses, such as a regular expression JavaScript cannot compile, leave that one input unmasked and are reported in the browser's console. Every other input on the page is masked as usual.

#### What is not supported

An option whose value is a JavaScript function cannot be written in Python and is not supported: function masks, `prepare`, `prepareChar`, `commit`, `validate`, `dispatch`, `format` and `parse`. IMask's date mask needs two of them for any format but its default, so none of the four widgets is a date widget: a date is a pattern of range blocks, and a partial date has a widget of its own, [`PartialDateMaskInput`](https://github.com/django-mvp/django-mvp-forms#partial-dates). There are no widgets for one particular format, such as a phone number or an IBAN, because the pattern differs by country and each is one line with `PatternMaskInput`. IMask's pipes, which format a value with no input, are not covered.

### Partial dates

A partial date is a date known to the year, to the month or to the day: a letter dated 1894, a sample collected in March 2021, a birth on 14 March 2021. `PartialDateField` takes one from a form, checks it against the calendar and hands the form `cleaned_data` ISO text.

This is the public surface:

- `mvp_forms.fields.PartialDateField`
- `mvp_forms.widgets.PartialDateMaskInput`
- `mvp_forms.widgets.PartialDateInput`
- `mvp_forms.widgets.PartialDateSelect`
- the template `mvp_forms/widgets/partial_date.html` and the script `mvp_forms/partial-date.js`

#### The field

```python
from django import forms

from mvp_forms.fields import PartialDateField


class SampleForm(forms.Form):
    collected = PartialDateField(required=False)
```

The field takes `CharField`'s own arguments, and `required`, `disabled`, `validators`, `error_messages`, `label`, `help_text` and `initial` behave as they do there. With no widget named it is drawn as a text input, in the pack's `input` class with the size, colour and variant stated for the form, and its form's media names no script.

| Entered | `cleaned_data` |
|---|---|
| `2021` | `"2021"` |
| `2021-03` | `"2021-03"` |
| `2021-3` | `"2021-03"` |
| `2021-03-14` | `"2021-03-14"` |
| `2021-3-4` | `"2021-03-04"` |
| `2021-` | `"2021"` |
| nothing, or only space | `""` |

A value is a year of four digits, then a month, then a day, each part joined to the last by a hyphen. A month or a day of one digit is padded to two. Space around the value is dropped, and so is one trailing hyphen. A part is only ever left out from the right: a month with no year and a day with no month are refused. Every part is made of the digits 0 to 9, so a year written in the digits of another script is refused. A date has to exist: `2023-02-29` is refused and `2024-02-29` is not, and the Gregorian rules apply to every year from 0001.

The field returns text, as a `CharField` does, and never a `datetime.date`, since a year alone is no date. A `datetime.date` given as the field's `initial` is shown as its ISO text, and so is the date of a `datetime.datetime`, with no time. A model's `CharField` with `max_length=10` takes the value as it is, and so does a model field of your own that stores a partial date. How a project stores it is the project's.

#### Error codes

Every error is raised with a `code`, so a test or a form's `has_error` can name it, and each message can be replaced through `error_messages`:

| Code | The value |
|---|---|
| `required` | is empty on a required field |
| `invalid` | is not a date written with hyphens: it holds anything but the digits 0 to 9 and hyphens, has more than three parts, an empty part at its end, or more than one trailing hyphen |
| `year` | has a year of fewer or more than four digits, or the year `0000` |
| `month` | has a month above 12, or a month of `0` or `00` |
| `day` | has a day the month does not have, including 29 February in a year that is not a leap year, or a day of `0` or `00` |
| `no_year` | has a month or a day and no year |
| `no_month` | has a day and no month |
| `needs_month` | is a year alone, on a field whose `min_resolution` is `"month"` |
| `needs_day` | is a year alone or a year and a month, on a field whose `min_resolution` is `"day"` |
| `month_not_allowed` | has a month or a day, on a field whose `max_resolution` is `"year"` |
| `day_not_allowed` | has a day, on a field whose `max_resolution` is `"month"` |
| `min_value` | is before the field's `min_value`. The limit is in the error's `params` as `limit` |
| `max_value` | is after the field's `max_value`. The limit is in the error's `params` as `limit` |

A value cut off inside a part cannot be told from a part of one digit, so `2021-0` is a month of zero and `202` is a year of three digits.

#### How much of a date must be given

`min_resolution` is the lowest resolution a field accepts and `max_resolution` is the highest. Each is one of `"year"`, `"month"` or `"day"`. With nothing stated a field accepts all three, as `min_resolution="year"` and `max_resolution="day"`.

```python
class SampleForm(forms.Form):
    analysed = PartialDateField(min_resolution="month")  # a year alone is refused
    published = PartialDateField(max_resolution="month")  # a day is refused
    founded = PartialDateField(max_resolution="year")  # a year and nothing else
```

The field refuses a value lower than `min_resolution` or higher than `max_resolution` with the code that names what is missing or not allowed, `needs_month`, `needs_day`, `month_not_allowed` or `day_not_allowed`. A value that is not a date is refused with its own code first, whatever the resolutions.

A resolution that is not one of the three, and a `max_resolution` lower than `min_resolution`, raise `ValueError` when the form class is defined. The message names the option at fault, and both options when the `max_resolution` is lower than the `min_resolution`.

Every widget follows the `max_resolution`, and you state it nowhere but on the field, so changing a widget is changing one name:

- `PartialDateMaskInput` writes the resolution in its `data-imask`, so at `"month"` the input takes a year and a month and no day, and at `"year"` it takes the year alone.
- `PartialDateInput` and `PartialDateSelect` draw no part higher than the maximum resolution: at `"month"` a year and a month, at `"year"` the year alone. A day sent to a field of that resolution anyway is refused with `day_not_allowed`.
- A widget on a field that is not a `PartialDateField` has no maximum resolution stated and keeps `"day"`: the masked input takes a full date and the other two draw all three parts.

The field tells its widget the first time its form reads the field, so a widget your form's `__init__` puts in its place is told as well, and two forms of one class never share a widget.

```python
class SampleForm(forms.Form):
    published = PartialDateField(max_resolution="month")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published"].widget = PartialDateSelect()
```

A widget is swapped before the form is first drawn or validated, since a form keeps the bound field it first made.

`min_resolution` is checked by the field alone. A three-part widget still draws every part up to the maximum resolution, and a masked input still takes a year alone, so a value of too low a resolution comes back from the field with `needs_month` or `needs_day`.

#### The earliest and latest date

`min_value` is the earliest date a field accepts and `max_value` the latest. Each takes a partial date as text, in any of the three resolutions, or a `datetime.date`. With neither stated the field accepts any date.

```python
import datetime


class SampleForm(forms.Form):
    letter = PartialDateField(min_value="1850", max_value="1899")
    sample = PartialDateField(min_value="1998-03-15", max_value="2004-09")
    filed = PartialDateField(min_value=datetime.date(2010, 1, 1))
```

A value outside the limits is refused with the code `min_value` or `max_value`, and the limit, padded to ISO text, is in the error's `params` as `limit`. A value that is not a date is refused with its own code first, and a value higher or lower than the field allows is refused for its resolution before the limits are looked at.

A partial value is inside the limits when any day it could be is. The comparison is of the first and last day each value covers:

- A value is refused by `min_value` when its last possible day is before the first day of `min_value`.
- A value is refused by `max_value` when its first possible day is after the last day of `max_value`.
- A limit given to the year or to the month stands for the whole of it. As an earliest date `1998-03` means 1 March 1998, and as a latest date it means 31 March 1998.

With `min_value="1998-03-15"`, `1998`, `1998-03` and `1998-03-15` are accepted, because each of them holds a day on or after the 15th of March, and `1997`, `1998-02` and `1998-03-14` are refused. With `max_value="1998-03-15"` the same three are accepted and `1999`, `1998-04` and `1998-03-16` are refused.

A limit that is not a partial date, and a `min_value` later than the `max_value`, raise `ValueError` when the form class is defined. The message names the option at fault, and both options when the earliest date is the later one.

A limit is fixed when the form class is defined, and a class body runs once, when the module is imported. A limit that follows today's date, such as a sample that cannot be dated in the future, is given by declaring the field in the form's `__init__`, which runs for every form:

```python
class SampleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["collected"] = PartialDateField(
            max_value=datetime.date.today(), required=False
        )
```

Every widget is told the limits by the field, as it is told the resolution, and you state them nowhere else:

- `PartialDateMaskInput` writes `min` and `max` in its `data-imask`, as padded ISO text, for each limit the field states and for no other.
- `PartialDateInput` and `PartialDateSelect` write `data-partial-date-min` and `data-partial-date-max` on the element that holds the parts, again for each limit stated and for no other.
- `PartialDateSelect` lists the years from the year of `max_value` back to the year of `min_value`, latest first. With no `max_value` the list starts this year, or a hundred years on from the year of `min_value` when that year is still to come. With no `min_value` it reaches a hundred years back from where it starts. A year the form already holds that is outside the limits is still put first, so a refused date is drawn as it was sent.
- A widget on a field that is not a `PartialDateField` is told no limits and writes none.

A date outside the limits that was sent is drawn again as it was sent, in every widget, with the field's error.

How a person is kept inside the limits depends on the widget:

- `PartialDateMaskInput` refuses the digit that would leave no date inside the limits, as [What the mask does](#what-the-mask-does) describes.
- `PartialDateInput` and `PartialDateSelect` offer only the months and days inside the limits, as [What the script does](#what-the-script-does) describes.
- With `PartialDateInput` the year is typed, and a text input has no minimum. A typed year outside the limits keeps the month closed, and the field's error says which limit was crossed once the form is sent. Nothing else in the browser says so. `PartialDateSelect` offers only the years inside the limits, so a person cannot choose one outside them.

#### The masked input

`PartialDateMaskInput` draws one text input and has IMask put the hyphens in as a person types.

```python
from mvp_forms.widgets import PartialDateMaskInput


class SampleForm(forms.Form):
    collected = PartialDateField(
        required=False,
        widget=PartialDateMaskInput(attrs={"placeholder": "2021-03-14"}),
    )
```

`PartialDateMaskInput(attrs=None)` takes HTML attributes and nothing else. Every option is a keyword of the field. The input is drawn with the field's name and id, with `inputmode="numeric"` so a touch device offers a numeric keypad unless your `attrs` state an `inputmode`, and with every other attribute you gave kept. Its `data-imask` holds `{"kind": "partial-date", "resolution": "day"}`, with the field's `max_resolution` in place of `"day"` when the field states one, and `min` and `max` when the field states a limit. It carries a `placeholder` of `YYYY-MM-DD`, `YYYY-MM` or `YYYY` for the field's `max_resolution`, unless your `attrs` state one. In the pack it is an `input`, takes the size, colour and variant stated for the form, and is drawn the same way through Django's own rendering.

The page has to load what a page loads for any mask widget: IMask and the form's media, which names `mvp_forms/imask.js`. [What to load](https://github.com/django-mvp/django-mvp-forms#what-to-load) says how, and how a page's Content Security Policy and a project's bundler are met.

A page that does not load IMask draws the input as an ordinary text input. Nothing is masked, no error is raised in the browser, and the form submits what was typed to the field, which checks it as it does any value.

The widget on a field that is not a `PartialDateField` is a text input that submits what was typed.

##### What the mask does

The year is four digits, then a hyphen, a month and a hyphen, a day, and the hyphens are placed as the digits are typed.

- While the input has focus its open positions are shown in place: `YYYY-MM-DD` when it is empty, `19YY-MM-DD` after `19`, and `1998-0M-DD` after `19980`. A field whose `max_resolution` is `"month"` shows `YYYY-MM` and one whose `max_resolution` is `"year"` shows `YYYY`. The caret waits at the first open position. When focus leaves, the input holds the partial date alone, `1998-03`, and an empty input is empty. The form is sent the same text whether or not the input has focus at that moment: `199803` typed and Enter pressed submits `1998-03`.
- A digit that would make the month `00` or above 12 is not accepted. A digit that would make a day the typed month does not have is not accepted, and February takes the 29th only in a leap year. A change to the year or the month that would leave the day with no date is not accepted either: the input keeps the date it held.
- With limits stated, a digit is also refused when no date inside the limits could follow from what has been typed. With `min_value="1998-03-15"` and `max_value="2004-09"`, `1997` keeps `199`, `19980314` keeps `1998-03-1`, `19980315` is taken whole, and `200410` keeps `2004-0`. The mask works out the first and the last day the typed text could still become, the way the field does, so a year or a month alone is taken while a date inside the limits remains.
- A first digit that can only be the whole month, 2 to 9, or the whole day, 4 to 9, is padded with a zero as it is typed: `202145` gives `2021-04-05`. A pasted date is padded in the same way: `2021-3-4` gives `2021-03-04`.
- Typing writes over the positions it reaches and moves nothing. With `2020-12-25` in the input, `1999` typed with the caret at the start gives `1999-12-25`, and so does selecting the year and typing `1999`. Selecting the month and typing `03` gives `2020-03-25`, and selecting everything and typing `19980304` gives `1998-03-04`. A digit that is refused for the month, the day or the limits is refused when it is typed over a digit too.
- A change inside a value never alters a part you did not touch. Delete deletes the digit after the caret and Backspace the one before it, and the digit is not taken out of its part: deleting the `1` of the month in `2020-12-25` gives `2020-02-25`, and typing `1` writes it back. A deletion that would move a digit of another part into its place is not applied, and the input keeps the value it held, and the selection with it. Backspace or Delete inside the year of `2020-12-25`, and Delete between the digits of the month, leave `2020-12-25`. A digit is corrected by typing over it.
- Pasted text that is longer than one character and holds anything but digits and hyphens, such as `14.03.2021`, is not taken: nothing of it is inserted.
- A person may stop after the year or after the month. `2021` and `2021-03` are submitted as they stand, and the field accepts them.
- A value the form was drawn with is shown under the mask, `2021-03` as `2021-03`. A value the mask would cut, such as `2021-02-30`, or `1997-03-14` where the earliest date is `1998-03-15`, held in a form's `initial` or in a bound form that failed, is shown whole so that the person sees what was sent. The mask is put on the input once the person has changed it to a value the mask takes.

The mask refuses the digits a calendar cannot have and nothing more. The field is what checks the value.

The padding is done by a subclass of IMask's range block that overrides `_appendCharRaw`, a method that IMask's guide does not document, because the two options the guide does document for changing typed text lose the rest of a value that is changed in the middle. The widget is tested against IMask 7.6.1, and a newer release needs the browser tests run against it before it is relied on.

#### The year, the month and the day

`PartialDateInput` draws a year, a month and a day as three parts that make one value, and `PartialDateSelect` is the same with the year chosen from a list.

```python
from mvp_forms.widgets import PartialDateInput, PartialDateSelect


class SampleForm(forms.Form):
    collected = PartialDateField(required=False, widget=PartialDateInput())
    born = PartialDateField(required=False, widget=PartialDateSelect())
```

Both take `attrs` and nothing else, and every option is a keyword of the field. The attributes you give reach every part. The parts are one joined group in a single element that carries `data-partial-date`:

- The year is a text input of four digits with a numeric keypad, or, in `PartialDateSelect`, a select of years.
- The month is a select of the twelve months, named in the active language.
- The day is a select of 1 to 31.

Each part carries an `aria-label` that says which part it is and `data-partial-date-part` set to `year`, `month` or `day`. The parts submit under the field's name followed by `_year`, `_month` and `_day`, so a field named `collected` is posted as `collected_year`, `collected_month` and `collected_day`. In the pack the parts are drawn in one fieldset whose legend is the label, with one help text and one set of errors, and each part takes the size, colour and variant stated for the form. Only the year carries `required`, because a month and a day may be left out. Through Django's own rendering the same three controls are drawn.

The widget joins the parts with hyphens and leaves out the empty ones from the right, so the field receives `2021`, `2021-03` or `2021-03-14`. A day with no month and a month with no year reach the field and are refused with `no_month` and `no_year`. A part holding a hyphen is not joined to the others: the form is refused with `invalid`. A form drawn again after a refused submission shows each part as it was sent, including `2021-02-30`, a day with no month and a part holding a hyphen. An `initial` value, as text or as a `datetime.date`, fills the parts it has and leaves the rest empty.

`PartialDateSelect` lists the years from this year back a hundred years, latest first, or the years between the field's limits when it states them. The list stops at the year `0001`. A year the form already holds that is not on the list is still an option, so a stored `1850` is shown and not lost.

The widgets name `mvp_forms/partial-date.js` in the form's media. The script needs no IMask, and a page that loads the form's media is all it asks for.

##### What the script does

The script keeps the three parts in step with the calendar as the person fills them in.

- No month can be chosen until the year has four digits, and no day can be chosen until a month is chosen. The parts that cannot be used yet are disabled, and so are not submitted.
- The days on offer are the days the chosen month has in the entered year, and February offers the 29th only in a leap year. A day the month does not have is not in the list at all, so nothing greyed out is left to puzzle over.
- The limits narrow the same lists. Under a year the limits leave no date in, no month can be chosen. In the first year only the months from the earliest date on are offered, and in the last year only the months up to the latest. The days of a month the limit falls in are cut the same way: with an earliest date of `1998-03-15`, March 1998 offers the 15th onward.
- A month or a day the change has made impossible is cleared and never moved to another one. A chosen 31st is cleared when the month becomes February, and a chosen 29th of February is cleared when the year stops being a leap year. A day the new month still has is kept. A month the new year puts outside the limits, such as February when the year changes to the earliest one, is cleared, and so is a day a limit now rules out.
- A form drawn holding a value that is not a date, such as `2021-02-30`, a day with no month, or a date outside the limits, shows what was sent until the person changes a part. The person sees what the field refused, and the first change puts the parts back in step.
- A group added to the page later, such as the extra form of a formset, behaves in the same way, and a page that holds the form's media several times has the script act once. Add a row from the formset's empty form, held in a `<template>` with `__prefix__` replaced by the form count, and never clone a row in use: a clone of a row whose month was cut down to February offers only the days February has, because the script takes the options a select holds when it first meets it for its full list.

The script writes no inline script and no inline handler, and it makes no request. It holds on to the full list of a part's options the first time it meets it, and puts back into the select only those that can be chosen.

A page that does not load the script draws the same three parts with every option: twelve months and the days 1 to 31, each part enabled. The form submits, and the field refuses a combination that is not a date, so a day with no month comes back as `no_month` and a date such as `2021-02-30` as `day`.

### Themes

The pack names only daisyUI's semantic colours, so a form follows whichever theme the host project chooses, and the pack sets none. Under each of the 35 themes built into daisyUI 5.7.47, light and dark, every piece of text the pack colours by its own choice can be read: labels, legends, help text, attached text, table headers, tabs and the alert that holds a form's errors. What is left is daisyUI's own drawing of a control, or a colour you chose for it.

The test suite draws every form state the pack has and calculates the contrast of each piece of text, and of each part of a control that shows what it is and what state it is in, against the surface directly behind it, from the colours daisyUI publishes for each theme. The standard is [WCAG 2.2](https://www.w3.org/TR/WCAG22/) level AA: 4.5 to 1 for text, and 3 to 1 for the part of a control that shows what it is or its state. Those parts are the border of an input, a select, a textarea and a file input, the border of a checkbox or radio that is off, a toggle that is off, the mark and fill of each when on, a rating's stars, lit and unlit, a range's track and thumb, the arrow of a select and of an accordion group, and the bar under the chosen tab. A button is held by its text alone. A field drawn with the ghost variant has no border by daisyUI's design, so none is measured for it.

An error message is drawn in the text colour, not in daisyUI's error colour, which falls short against the page under many themes. An invalid input is marked by its border, which takes the error colour, and the errors of a form as a whole are gathered in an alert at the top of it. The border of an invalid input is measured like any other and appears in the list below where it falls short.

A disabled control is dimmed by daisyUI. Its own content, such as its text, border and mark, is measured and reported, and is never held to the standard. Its label and help text are held. daisyUI does not dim a disabled rating, but its stars are measured and not held in the same way.

A theme your project writes or alters is not measured: the suite reads the themes of the pinned daisyUI version and no others. The pack's own text is drawn in the theme's `base-content` on `base-100` and `base-200`, and in the error alert on its tinted fill, so a theme whose `base-content` reaches 4.5 to 1 on both reads the same. The borders, marks and buttons that take a colour of the theme, and a colour or variant you state with `FormChoices` or `Choice`, depend on that theme's own colours, and the list below shows which of daisyUI's colours fall short on `base-100` under the shipped themes.

Where daisyUI's own drawing, or a colour you chose for a control, falls short under a theme, no stock daisyUI class repairs it and the pack adds no style of its own. Each such pairing is listed here with the themes it falls short under, and the test suite fails when this list and what it measures differ.

<!-- known-exceptions:start -->
| Pairing | Seen on | Themes |
| --- | --- | --- |
| border, `accent` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `accent` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `accent` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | light, cupcake, emerald, retro, cyberpunk, valentine, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, acid, lemonade, coffee, nord, abyss |
| border, `base-content` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `base-content` at 20% on `base-100` | checkbox, file-input, input, radio, rating, select, textarea | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `base-content` at 20% on `base-200` | input | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `base-content` at 50% on `base-100` | toggle | emerald, retro, valentine, luxury, coffee, winter, nord, caramellatte, silk |
| border, `error` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `error` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `error` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | light, bumblebee, corporate, retro, cyberpunk, garden, lofi, pastel, business, lemonade, winter, caramellatte, silk |
| border, `error` on `base-200` | input | light, bumblebee, emerald, corporate, retro, cyberpunk, garden, lofi, pastel, fantasy, business, lemonade, winter, caramellatte, silk |
| border, `info` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `info` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `info` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | light, cupcake, bumblebee, emerald, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, black, cmyk, autumn, lemonade, winter, nord, silk |
| border, `neutral` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `neutral` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `neutral` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | dark, synthwave, halloween, forest, aqua, wireframe, black, luxury, dracula, business, night, coffee, dim, sunset, abyss |
| border, `primary` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `primary` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `primary` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | cupcake, bumblebee, emerald, retro, cyberpunk, pastel, wireframe, black, cmyk, business, acid |
| border, `secondary` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `secondary` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `secondary` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | cupcake, bumblebee, retro, cyberpunk, halloween, aqua, pastel, wireframe, black, luxury, acid, lemonade, coffee, nord |
| border, `success` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `success` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `success` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | light, cupcake, bumblebee, cyberpunk, valentine, garden, lofi, pastel, acid, lemonade, winter, nord, silk |
| border, `warning` at 10% on `base-100` | range | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `warning` at 20% on `base-100` | rating | light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
| border, `warning` on `base-100` | checkbox, file-input, input, radio, select, textarea, toggle | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, lofi, pastel, fantasy, cmyk, autumn, acid, lemonade, winter, nord, caramellatte, silk |
| button text, `accent-content` on `accent` | btn, file-input | corporate, retro, garden, pastel |
| button text, `accent` on 8% `accent` in `base-100` | btn | light, cupcake, emerald, corporate, retro, cyberpunk, valentine, garden, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, acid, lemonade, coffee, winter, nord, abyss |
| button text, `accent` on `base-100` | btn | light, cupcake, emerald, corporate, retro, cyberpunk, valentine, garden, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, acid, lemonade, coffee, winter, nord, abyss |
| button text, `error-content` on `error` | btn, file-input | cupcake, bumblebee, retro, valentine, pastel, autumn, business, caramellatte, abyss, silk |
| button text, `error` on 8% `error` in `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, dracula, cmyk, autumn, business, acid, lemonade, winter, nord, caramellatte, silk |
| button text, `error` on `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, cmyk, business, acid, lemonade, winter, nord, caramellatte, silk |
| button text, `info-content` on `info` | btn, file-input | bumblebee, corporate, retro, halloween, aqua, pastel |
| button text, `info` on 8% `info` in `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, halloween, garden, aqua, lofi, pastel, fantasy, black, cmyk, autumn, business, acid, lemonade, winter, nord, silk |
| button text, `info` on `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, halloween, garden, aqua, lofi, pastel, fantasy, black, cmyk, autumn, acid, lemonade, winter, nord, silk |
| button text, `neutral-content` on `neutral` | btn, file-input | pastel, autumn |
| button text, `neutral` on 9% `neutral` in `neutral-content` at 88% over `base-100` | btn | synthwave, pastel, autumn, sunset, caramellatte |
| button text, `neutral` on `base-100` | btn | dark, synthwave, halloween, forest, aqua, wireframe, black, luxury, dracula, autumn, business, night, coffee, dim, sunset, abyss |
| button text, `primary-content` on `primary` | btn, file-input | dark, corporate, valentine, garden, winter |
| button text, `primary` on 8% `primary` in `base-100` | btn | dark, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, pastel, wireframe, black, cmyk, business, acid, lemonade, winter, nord |
| button text, `primary` on `base-100` | btn | dark, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, pastel, wireframe, black, cmyk, business, acid, lemonade, nord |
| button text, `secondary-content` on `secondary` | btn, file-input | light, dark, bumblebee, emerald, valentine, aqua, pastel, fantasy |
| button text, `secondary` on 8% `secondary` in `base-100` | btn | light, dark, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, halloween, aqua, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, business, acid, lemonade, coffee, nord |
| button text, `secondary` on `base-100` | btn | light, dark, cupcake, bumblebee, emerald, retro, cyberpunk, valentine, halloween, aqua, pastel, wireframe, black, luxury, cmyk, autumn, acid, lemonade, coffee, nord |
| button text, `success-content` on `success` | btn, file-input | corporate, pastel, black |
| button text, `success` on 8% `success` in `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, black, autumn, acid, lemonade, winter, nord, silk |
| button text, `success` on `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, black, autumn, acid, lemonade, winter, nord, silk |
| button text, `warning-content` on `warning` | btn, file-input | retro, pastel |
| button text, `warning` on 8% `warning` in `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, cmyk, autumn, acid, lemonade, winter, nord, caramellatte, silk |
| button text, `warning` on `base-100` | btn | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, cmyk, autumn, acid, lemonade, winter, nord, caramellatte, silk |
| mark, `accent` on `base-100` | radio, range, rating, toggle | light, cupcake, emerald, retro, cyberpunk, valentine, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, acid, lemonade, coffee, nord, abyss |
| mark, `error` on `base-100` | radio, range, rating, toggle | light, bumblebee, corporate, retro, cyberpunk, garden, lofi, pastel, business, lemonade, winter, caramellatte, silk |
| mark, `info` on `base-100` | radio, range, rating, toggle | light, cupcake, bumblebee, emerald, cyberpunk, valentine, garden, aqua, lofi, pastel, fantasy, black, cmyk, autumn, lemonade, winter, nord, silk |
| mark, `neutral` on `base-100` | radio, range, rating, toggle | dark, synthwave, halloween, forest, aqua, wireframe, black, luxury, dracula, business, night, coffee, dim, sunset, abyss |
| mark, `primary` on `base-100` | radio, range, rating, toggle | cupcake, bumblebee, emerald, retro, cyberpunk, pastel, wireframe, black, cmyk, business, acid |
| mark, `secondary` on `base-100` | radio, range, rating, toggle | cupcake, bumblebee, retro, cyberpunk, halloween, aqua, pastel, wireframe, black, luxury, acid, lemonade, coffee, nord |
| mark, `success` on `base-100` | radio, range, rating, toggle | light, cupcake, bumblebee, cyberpunk, valentine, garden, lofi, pastel, acid, lemonade, winter, nord, silk |
| mark, `warning` on `base-100` | radio, range, rating, toggle | light, cupcake, bumblebee, emerald, corporate, retro, cyberpunk, valentine, garden, lofi, pastel, fantasy, cmyk, autumn, acid, lemonade, winter, nord, caramellatte, silk |
| placeholder, `base-content` at 50% on `base-100` | input, textarea | light, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk |
<!-- known-exceptions:end -->

To see where the pack stands, run `uv run python -m tests.legibility`: it prints this table as the check would write it, then the ratio of each disabled control's dimmed parts under every theme. When the check fails, repair the markup with a stock daisyUI class that passes under every theme, or, where no such class exists, paste the report's table between the two markers above.

The demo project draws every form state the check covers on one page, `/themes/`, reached from its sidebar, with a chooser of the 35 themes: check one and the page is drawn under it. `/themes/standalone/` is the same page as a host project with neither django-mvp nor Cotton would have it. Both load daisyUI's [`themes.css`](https://daisyui.com/docs/themes/) for the pinned version from a CDN, because django-mvp's prebuilt stylesheet and daisyUI's main CDN file carry only a few themes.

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

### Changing the support window

The versions this package supports are declared in
[support-window.toml](https://github.com/django-mvp/django-mvp-forms/blob/main/support-window.toml).
The tables in
[Supported versions](https://github.com/django-mvp/django-mvp-forms#supported-versions), the
table of versions that have left, the package metadata, the lockfile, the installed versions, the
versions the test workflow runs on, the release headings of the changelog and the daisyUI class
lists are checked against that file on every test run, so a change to one that the others do not
follow fails the suite.

To add a version, change these together:

1. Add the version to `support-window.toml`. A django-crispy-forms release also gets a line under
   `[django-crispy-forms.pairs]` naming the Django series it supports.
2. Add it to the two tables in "Supported versions".
3. For a Django series or a Python version, add its trove classifier to `pyproject.toml`. The
   requirements there say `>=` the oldest named version and nothing else. Add it as well to
   `django-versions` or `python-versions` in `.github/workflows/tests.yml`, which passes both
   lists to the shared tests workflow so that its defaults are never the versions run.
4. For a daisyUI version that becomes the minimum or the newest, write its class list with
   `uv run python support_window.py classes 5.8`. It finds the newest patch release of that minor
   version, reads the stylesheet daisyUI publishes for it and writes
   `tests/data/daisyui-classes-5.8.txt`. It uses the network. Delete the list of a version that is
   no longer one end of the range. Every test that compares the pack's classes with daisyUI's runs
   once for each list. When the newest version changes, also replace `tests/data/daisyui-themes.css`
   with the `themes.css` of the same patch release, which the legibility check reads. A test fails
   until that file and the newest class list name the same version.
5. Run the suite on the new pair, as below.

To take a version out, change these together:

1. Remove it from `versions` in `support-window.toml`, or for daisyUI raise `minimum`. Add a
   `[[dropped]]` table for it with its `package`, its `version` and the `last-release`, the last
   release of this package that supported it. The file has a commented example. A django-crispy-forms
   release also loses its line under `[django-crispy-forms.pairs]`, and a dropped Django series
   comes out of every line that lists it.
2. Remove it from the two tables in "Supported versions" and add a row to the table of versions
   that have left, between the `dropped-versions` comments, as `| package | version | last release |`
   under a header row. When the first version leaves, remove the sentence "No version has left
   the window." from "Versions that have left", as the first row goes into the table.
3. For a Django or django-crispy-forms version, raise the minimum in the dependencies of
   `pyproject.toml`, so that an installer in a project still on the dropped version selects the
   last release that supported it. For a Django series, also remove its trove classifier and take
   it out of `django-versions` in `.github/workflows/tests.yml`.
4. Write the CHANGELOG entry under Removed, naming each version dropped and the last release that
   supported it.

A Python version is taken out by removing it from `python` in the declaration, from the table,
from its classifier and from `python-versions` in `.github/workflows/tests.yml`, and it gets no
`[[dropped]]` entry.

The suite names a version that is both in the window and dropped, a version between `first`, the
oldest this package ever supported, and the newest named that is neither, a last release that the
changelog has no heading for, a row of the table that the declaration does not match, and a
requirement that still admits a dropped version. A drop ships in a minor or major release and
never in a patch release, and one release may drop several versions. No check enforces the kind
of release, because the version number is raised after the change merges.

`uv run python support_window.py test 5.2 2.7` runs the whole suite on Django 5.2 and
django-crispy-forms 2.7. The two versions are laid over the project's environment for that one
command, so your own environment is left as it was. Arguments after the pair go to pytest instead
of the default of running in parallel. The header of every test run names the Django and
django-crispy-forms it ran on, and a run that finds other versions than the ones it was asked for
stops before the first test with a usage error. A pair the window does not offer runs nothing and
exits with a failing status.

`uv run python support_window.py releases` asks the package index for Django and
django-crispy-forms and the npm registry for daisyUI, and says whether a final release exists that
the window does not name. It prints one line for each Django series, django-crispy-forms feature
release and daisyUI minor release newer than the newest the window names, with the day it was
first released. Its exit status is:

- `0` when nothing is outstanding.
- `1` when at least one such release is missing from the window.
- `2` when a source could not be reached, its answer could not be read, or it does not list the
  newest version the window names. The output names the package it could not find out about and
  does not say the window is current.

A new major version of django-crispy-forms or daisyUI is printed and does not change the status.
Every newer Django series counts, including a new major version. Pre-releases are ignored. The
command uses the network and the test suite never runs it. It is run by hand, because running it
on a schedule needs a workflow, which is tracked in
[issue 127](https://github.com/django-mvp/django-mvp-forms/issues/127).

The test workflow runs every Django series and Python version named in the window, and the suite
fails when the lists in `.github/workflows/tests.yml` differ from the declaration. It runs
django-crispy-forms only at the release in `uv.lock`, which is the one release named today. Running
a second named release needs the shared tests workflow to take the versions of another package,
which is tracked in
[issue 126](https://github.com/django-mvp/django-mvp-forms/issues/126).

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

One more page draws the size, colour and variant of a form's inputs and buttons. It holds a small form for each size and for each colour, each with one input and one button; a form holding every kind of input at one size; a form of inputs in the ghost variant and a button bar with one button in each variant; and a form that states choices and overrides them for one field in its layout, for one field by name, for one field that drops the colour, and for one button. It also holds a small and a large form with an alert and a modal in each, whose dismiss and close buttons take the form's size. The forms are built from the tables of `Modifiers`, so the page follows them, and none of them posts anywhere.

- `/choices/` is the page inside the django-mvp shell, reached from its sidebar as "Size, colour and variant".
- `/choices/standalone/` is the same page styled by daisyUI's CDN build alone.

One more page draws a boolean field as a checkbox, a toggle and a switch. It holds one form with three boolean fields, drawn those three ways: the first states nothing, the second is a toggle by its name in `FormChoices`, and the third is a switch in the layout. Turning some on and submitting the form draws the page again with each field as it was posted and the values the form cleaned to. Nothing is saved. The page also draws each of the three in each state (off, on, with help text, required and in error, and disabled), at every size and in every colour a toggle has, and in a form whose size and colour one field overrides.

- `/drawings/` is the page inside the django-mvp shell, reached from its sidebar as "Checkbox, toggle and switch".
- `/drawings/standalone/` is the same page styled by daisyUI's CDN build alone.

One more page draws a single-choice field as a rating and a number field as a range. It holds one form with two ratings and a range: a required rating stated by its name in `FormChoices`, an optional one stated in the layout, whose empty choice clears it, and a range with limits and a step. Picking stars, moving the slider and submitting the form draws the page again with each field as it was posted and the values the form cleaned to. Nothing is saved. The page also draws a rating and a range each with help text, in error and disabled.

- `/rating-and-range/` is the page inside the django-mvp shell, reached from its sidebar as "Rating and range".
- `/rating-and-range/standalone/` is the same page styled by daisyUI's CDN build alone.

Both pages end the form to submit in a `FormActions` holding a `Submit`, a `Reset`, a `Button` and a `StrictButton`, and add a form whose buttons were added to its helper and a small layout that puts two fields straight in a `Row` above a `ButtonHolder`. The form to submit also places an `HTML` note inside its fieldset, groups two fields in a `MultiField`, and carries a `Hidden` input.

One more page draws fields with a floating label. It holds a form to submit with an input, a textarea and a select that float, a field that undoes the form's statement and a checkbox the statement passes over. Submitting it with no name comes back with the error, and submitting it with one shows the values the form cleaned to. Nothing is saved. The page also draws a form that already fails, with a required field and its help text, a disabled field and a read-only field, and a form drawn with no layout that floats one field by name. It also draws a floating form at each size, one at each colour and one in the variant.

- `/floating-labels/` is the page inside the django-mvp shell, reached from its sidebar as "Floating labels".
- `/floating-labels/standalone/` is the same page styled by daisyUI's CDN build alone.

One more page draws fields joined into one group. It holds a form to submit with a country code and a number under one label. Submitting it with no number comes back with the number's error, and submitting it with one shows the values the form cleaned to. Nothing is saved. The page also draws a group that already fails in one member, a group with help text on a member, a group with a disabled member, a read-only member and a hidden member, a group with no label, and a group of one. It also draws a group at each size, one at each colour and one in the variant, a coloured group with one member in error, and a group inside a `Choice` that states a size and a colour.

- `/joined-groups/` is the page inside the django-mvp shell, reached from its sidebar as "Joined groups".
- `/joined-groups/standalone/` is the same page styled by daisyUI's CDN build alone.

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

One more page draws django-tomselect's controls. Its sidebar entry is in a group of its own, apart from the standard pages. The page holds a form to submit with a text input and a stock select beside a single control, a multiple control, a tagging control and a control whose options are listed under groups. Submitting it with no country comes back with the country's error, and submitting it with one shows the values the form cleaned to. Nothing is saved. The page also draws a stock select, a single control and a tagging control in a state each (holding a value, in error and disabled), and the same three controls at each size, at each colour and in the variant. It ends with controls in a modal and in a formset drawn as a table, a form that htmx fetches and a link to a second page that htmx navigation loads. The autocomplete views behind the controls answer from lists kept in the demo, so the page needs no data.

- `/tomselect/` is the page inside the django-mvp shell, reached from its sidebar under "Third-party widgets" as "django-tomselect".
- `/tomselect/standalone/` is the same page styled by daisyUI's CDN build alone, with django-tomselect's files and `mvp_forms/tomselect.css`.

Every page inside the shell links `mvp_forms/tomselect.css`, because the demo's base template does.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-forms/blob/main/LICENSE).
