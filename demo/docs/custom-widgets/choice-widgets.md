# Choice widgets

A select hides its choices behind a tap, and a column of small radios is a poor
target for a finger. Seven widgets draw a choice field with large choices
instead: `ScaleSelect` as one row of segments, `PillSelect` and
`PillSelectMultiple` as rounded toggles, `ChipSelect` and `ChipSelectMultiple`
as large toggles that show a long label in full, and `CardSelect` and
`CardSelectMultiple` as cards with an icon and a description.

Name one on a `ChoiceField` or a `MultipleChoiceField`. The field cleans exactly
as it does with a radio or checkbox group, and no template, stylesheet or script
of yours is needed.

```python
from django import forms

from mvp_forms.widgets import PillSelect, ScaleSelect


class SurveyForm(forms.Form):
    recommend = forms.ChoiceField(
        choices=[(score, str(score)) for score in range(11)],
        widget=ScaleSelect(low="Not at all likely", high="Extremely likely"),
    )
    colour = forms.ChoiceField(
        choices=[("red", "Red"), ("green", "Green"), ("blue", "Blue")],
        widget=PillSelect,
    )
```

## A scale

`ScaleSelect` suits an ordered set of up to eleven short choices. `low` and
`high` put words under the first and the last segment, and a screen reader reads
them with the choice. A choice whose value is the empty string is not a segment.
It is drawn after the row as the way to clear the field.

```{live-example} /examples/choice-scale/
:title: A scale, with and without words at its ends

../../examples/custom_widgets/choice_widgets.py
```

## Pills

`PillSelect` and `PillSelectMultiple` suit a short set of short labels. A chosen
pill of a multiple field shows a tick. The empty choice of a single field is
drawn last, and a multiple field draws it as any other.

```{live-example} /examples/choice-pills/
:title: Pills for one choice and for several

../../examples/custom_widgets/choice_widgets.py
```

## Chips and a fold

`ChipSelect` and `ChipSelectMultiple` suit long labels, which a chip shows in
full. `show` names the values that stay on show. The rest sit in a fold that
says how many choices it holds, and `fold_label` gives the fold your own words.
A chosen choice is never folded.

```python
interests = forms.MultipleChoiceField(
    choices=INTERESTS,
    widget=ChipSelectMultiple(show=["cycling", "cooking", "gardening"]),
)
```

```{live-example} /examples/choice-chips/
:title: Chips with a fold and a choice that clears

../../examples/custom_widgets/choice_widgets.py
```

### A fold for the person using the form

Which choices matter often depends on who is filling in the form. Set `show` on
the form's own copy of the widget in `__init__`. Another form made from the same
class is not affected.

```python
class InterestsForm(forms.Form):
    interests = forms.MultipleChoiceField(
        choices=INTERESTS, widget=ChipSelectMultiple, required=False
    )

    def __init__(self, *args, usual=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interests"].widget.show = set(usual)
```

```{live-example} /examples/choice-fold-in-init/
:title: A fold set in the form's __init__

../../examples/custom_widgets/choice_widgets.py
```

## Cards

`CardSelect` and `CardSelectMultiple` draw each choice as a card. `descriptions`,
`icons` and `meta` are mappings from a choice's value to the softer text under
the label, the icon's markup and the short line above the label. Each is
optional for every choice. An icon is drawn as the markup you give, so mark it
safe, and the package names no icon set. A description is escaped. `columns` is
the number of cards across on a wide screen, 1, 2 or 3, and one card sits across
on a narrow screen.

```{live-example} /examples/choice-cards/
:title: Cards in three, two and one column

../../examples/custom_widgets/choice_widgets.py
```

Cards take a fold and a clearing choice as chips do.

```{live-example} /examples/choice-cards-folded/
:title: Cards with a fold and a choice that clears

../../examples/custom_widgets/choice_widgets.py
```

## A field in error and a disabled field

Each widget is a group with a legend, the help text and the errors. A field in
error is drawn in the error colour, and every choice of a disabled field is
disabled.

```{live-example} /examples/choice-states/
:title: A field in error and disabled fields

../../examples/custom_widgets/choice_widgets.py
```

## Size and colour

The widgets take the form's size and colour, and a field's own, as every input
does. They take no variant.

```{live-example} /examples/choice-small/
:title: Small, in the accent colour, with the plan in the secondary colour

../../examples/custom_widgets/choice_widgets.py
```

## In a formset

Each row of a formset has a fold of its own. Keep the empty form in a
`<template>` element and make a row from it, never by copying a row that is
already on the page.

```{live-example} /examples/choice-formset/
:title: A formset whose rows can be added

../../examples/custom_widgets/choice_widgets.py
```
