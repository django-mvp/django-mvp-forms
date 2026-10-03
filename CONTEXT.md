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

**Replacement**:
A template a host project provides at the path of one of the pack's templates,
which Django's template loading finds ahead of the pack's. It stands in for that
one template across the whole project, and every other template stays the
pack's. It needs no setting, no Python and no change to a form.
_Avoid_: override, fork, theme, skin.

**Template list**:
The README's record of every template the pack distributes: its path, what it
draws, the names it is handed and where a replacement is found. It is the
statement of what is public, and a test fails when it and the package differ.
_Avoid_: registry, manifest.

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
A size, a colour, a variant, a drawing or a label stated in Python, for a form,
for one field or for one button. The five are independent of each other. A
drawing is stated for one field at a time and never for a form. A label is
stated for a form or for one field and never for a button.
_Avoid_: option, setting, modifier (a modifier is the daisyUI class a choice
means).

**Drawing**:
How a field is drawn when its widget allows more than one way. A boolean field
takes `checkbox`, `toggle` or `switch`, a single-choice field takes `rating`
and a number field takes `range`. A toggle and a switch are both
daisyUI's toggle, and a switch also tells assistive technology it is a switch.
A field that states none is drawn as its widget is: a boolean field as a
checkbox, a single-choice field as a select or a radio group, a number field as
a number input. Any other field takes none.
_Avoid_: style, look, type (an input's type is the HTML attribute).

**Floating label**:
An input's label drawn as daisyUI's `floating-label`: its text is the empty
input's placeholder and moves to the field's edge once the field is focused or
holds a value. It is the one name of the label kind of choice, `"floating"`, and
only a lone input, textarea or select takes one.
_Avoid_: animated label, placeholder label.

**Joined group**:
Several fields a developer names in a layout with `Join`, drawn as one daisyUI
join under one label. It is the package's own layout object. Its inputs sit side
by side as the direct children of one element, in one fieldset whose legend is
the group's label, and only an input or a select can be one.
_Avoid_: input group (that is Bootstrap's name), compound field, field group.

**Member**:
One field of a joined group. It has no label of its own and is named by an
`aria-label` that is its field's label, and it keeps its own help text, errors
and place in the cleaned data. A hidden field named in a group is drawn beside
the join and is not a member.
_Avoid_: item, child, part (a part is one widget of a multi-widget field).

**Boolean field**:
A field whose widget is a Django `CheckboxInput`, or a subclass of one, such as
a `BooleanField`. It takes the drawings `checkbox`, `toggle` and `switch`. A
null-boolean select and a checkbox group are not boolean fields.
_Avoid_: checkbox field, switch field.

**Single-choice field**:
A field whose widget is a Django `Select` or `RadioSelect`, or a subclass of
either that still uses Django's own templates, and that holds one value, such as
a `ChoiceField` or a `ModelChoiceField`. It takes the drawing `rating`. A
multiple select, a checkbox group and a null-boolean select are not
single-choice fields.
_Avoid_: dropdown field, radio field.

**Rating**:
The drawing of a single-choice field as daisyUI's rating: one star for each
choice that has a value, drawn as bare radio inputs in the field's order. The
choice whose value is the empty string is not a star but the way to clear the
rating. A rating is a group, framed by a fieldset and a legend as a radio group
is.
_Avoid_: stars, star field.

**Number field**:
A field whose widget is a Django `NumberInput`, or a subclass of one, such as an
`IntegerField`, a `FloatField` or a `DecimalField`. It takes the drawing
`range`. A localised number field has a text input, so it is not a number field.
_Avoid_: numeric field, slider field.

**Range**:
The drawing of a number field as daisyUI's range: one input of type `range`,
drawn through a copy of the field's widget by Django's own input template. Its
lowest value, highest value and step are the ones Django already writes on the
widget. A range always submits a number, so an optional number field drawn as a
range is never submitted empty.
_Avoid_: slider field.

**Form state**:
One thing the pack draws, in one condition a person can meet it in: a text input
that is empty, filled, invalid, disabled or read-only, a help text, a field error,
a form-wide error, a required marker, a button, a tab that is selected or not, an
accordion group open or closed, and so on.
_Avoid_: case, scenario.

**Shipped theme**:
A theme built into the daisyUI version the test suite is pinned to, used as
daisyUI publishes it. Each one is either light or dark.
_Avoid_: using it for a theme a host project writes, which the suite never
measures.

**Pairing**:
One thing a person has to make out, together with the surface directly behind
it: a piece of text and its background, or the part of a control that shows what
it is and what state it is in and the surface around it.
_Avoid_: contrast pair, combination.

**Standard**:
The minimum contrast WCAG 2.2 sets at level AA: one figure for text, a lower one
for large text, and one for the parts of a control that identify it and show its
state. The pack draws no large text, so text is held to 4.5 to 1 and those parts
to 3 to 1.
_Avoid_: threshold, guideline.

**Known exception**:
A pairing that falls short of the standard under a named shipped theme, that no
stock daisyUI class would bring up to it, and that is published in the README.
The README's table is the only list, and the test suite compares it with what it
measures in both directions.
_Avoid_: bug, waiver, ignore list.

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
