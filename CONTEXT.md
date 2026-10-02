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

## Terms deliberately not used

**Component**:
In django-mvp this means a django-cotton component placed with a `<c-...>` tag.
This package ships none, and its templates must not use any, so calling a
widget or a layout object a component implies a dependency that is ruled out.

**Form view**, **formset**:
Real things, but django-mvp's. An issue here that needs one of these words is
probably filed against the wrong repository.
