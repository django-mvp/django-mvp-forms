# Characters left

`CharactersLeftInput` and `CharactersLeftTextarea` show how many characters a
person can still type, under the field, once only a few are left. The limit is
the field's `max_length`, which Django also writes on the control as
`maxlength`, so the browser stops the typing at the limit with or without the
line.

## Show the characters left under a field

1. Give the field a `max_length`.
2. Set the widget to `CharactersLeftInput`, or to `CharactersLeftTextarea` for
   a textarea.
3. Draw the form with the form's media on the page, which brings the widget's
   script.

```python
from django import forms

from mvp_forms.widgets import CharactersLeftInput


class TitleForm(forms.Form):
    title = forms.CharField(max_length=40, widget=CharactersLeftInput)
```

Type in the field below. Nothing shows until 8 characters or fewer are left,
and the line counts down from there and back up as you delete.

```{live-example} /examples/characters-left/
:title: A text input with a limit

../../examples/custom_widgets/characters_left.py
```

## Show the line sooner

`show_from` is the number of characters left at which the line appears. Without
it the line appears at 8, the value of `CHARACTERS_LEFT_FROM`. A textarea
counts a line break as one character, as the browser does.

```{live-example} /examples/characters-left-textarea/
:title: A textarea, and an input whose line appears at 20

../../examples/custom_widgets/characters_left.py
```

## Add rows to a formset

A row added in the browser has its line with no script of yours. Adding the row
is the page's own work, and this page does it with a few lines of its own.

```{live-example} /examples/characters-left-formset/
:title: Notes, with rows you can add

../../examples/custom_widgets/characters_left.py
```

## Show a value that is over the limit

A value saved before the limit was lowered is drawn whole, and the line says by
how many characters it is over. The field's validation refuses the value until
it is shortened.

```{live-example} /examples/characters-left-over/
:title: A saved title over its limit

../../examples/custom_widgets/characters_left.py
```
