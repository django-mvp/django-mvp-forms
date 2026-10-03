# django-mvp-forms

Domain vocabulary for django-mvp-forms, a daisyUI template pack for
django-crispy-forms with form fields and widgets for django-mvp projects.

The terms below are the ones to use in issues, commits and tests.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the stylesheet, the
theme, the base template, the views and the URLs. This package renders into it
and decides none of those. A host project may or may not use django-mvp.
_Avoid_: consumer, client, downstream, user (a user is a person using the host
project, not the project itself).

**Template pack**:
The set of templates django-crispy-forms selects by name through
`CRISPY_TEMPLATE_PACK`, one template per thing it can draw. This package ships
one, and it emits daisyUI markup. "The pack" on its own always means this one.
_Avoid_: theme, skin, style.

**Layout object**:
A django-crispy-forms Python class placed in a form's `Layout` to say how part
of the form is arranged: `Fieldset`, `Row`, `Div`, `Submit` and the rest. Each
is drawn by a template in the pack. A pack is complete when every layout object
crispy-forms documents has one.
_Avoid_: component, block, element.

**Formset**:
A Django formset: several forms of one kind, handed to the pack as a whole with
`{% crispy formset %}` or `{{ formset|crispy }}`, together with its management
form. A model formset and an inline formset are formsets. Drawing one is this
package's; handling one (the view, saving it, adding and removing rows in the
browser) is django-mvp's.
_Avoid_: form set, form list.

**Stacked layout**:
The way the pack draws a formset when nothing else is chosen: every form one
after another, each in a container of its own and drawn exactly as a single
form is.
_Avoid_: list layout, vertical layout.

**Table layout**:
The way the pack draws a formset when the helper chooses it: one table, a row
per form and a column per visible field.
_Avoid_: grid, inline layout.

**Field**:
A Django form field class. It owns validation and cleaning, and names the
widget that draws it. Never a model field, which this package does not ship.
_Avoid_: input (that is the HTML element a widget emits).

**Widget**:
A Django form widget: the class and template that draw one field's input.
_Avoid_: component, control. Not django-mvp's navbar widgets, which are
unrelated.

**Theme**:
A daisyUI colour scheme, chosen by the host project. The pack reads the theme's
colours through daisyUI's classes and never sets or ships one.
_Avoid_: using "theme" for the template pack.

**Size**:
One of the sizes daisyUI defines for inputs and buttons, written with daisyUI's
own name for it: `xs`, `sm`, `md`, `lg` or `xl`.
_Avoid_: scale, dimension.

**Colour**:
One of daisyUI's semantic colour names, such as `primary` or `error`. The host
project's theme decides what each name looks like, and the pack never names an
actual colour. The keyword is spelt `color`, as daisyUI spells it.
_Avoid_: theme, palette.

**Variant**:
One of the alternatives daisyUI offers for the same input or button, which its
own documentation calls a style. Inputs have one, `ghost`. Buttons
have several.
_Avoid_: style, look.

**Choice**:
A size, a colour, a variant or a drawing stated in Python, for a form, for one
field or for one button. The four are independent of each other. A drawing is
stated for one boolean field at a time and never for a form.
_Avoid_: option, setting, modifier (a modifier is the daisyUI class a choice
means).

**Drawing**:
How a boolean field is drawn: `checkbox`, `toggle` or `switch`. A toggle and a
switch are both daisyUI's toggle, and a switch also tells assistive technology
it is a switch. A field that states none is drawn as a checkbox.
_Avoid_: style, look, type (an input's type is the HTML attribute).

**Boolean field**:
A field whose widget is a Django `CheckboxInput`, or a subclass of one, such as
a `BooleanField`. It is the only kind of field that takes a drawing. A
null-boolean select and a checkbox group are not boolean fields.
_Avoid_: checkbox field, switch field.

## Terms deliberately not used

**Component**:
In django-mvp this means a django-cotton component placed with a `<c-...>` tag.
This package ships none, and its templates must not use any, so calling a
widget or a layout object a component implies a dependency that is ruled out.

**Form view**:
A real thing, but django-mvp's. An issue here that needs this word is probably
filed against the wrong repository. The same line runs through formsets: this
package draws one, and the view that handles it, the saving, and adding and
removing rows in the browser stay with django-mvp.
