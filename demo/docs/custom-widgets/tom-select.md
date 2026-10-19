# Tom Select

`TomSelect` and `TomSelectMultiple` turn a Django choice field into a select you
can type into. The options are known when the form is built and are written into
the page, so there is no view to write. Use them for a list long enough to
search. For options fetched as you type, see
[django-tomselect](../third-party-support/django-tomselect.md).

Name the widget on the field. The field cleans and validates as it did.

```{live-example} /examples/tom-select/
:title: One value, several values and groups

../../examples/custom_widgets/tom_select.py
../../templates/demo/examples/tom_select_form.html
```

Send the form empty to see the required field in error, then pick a topic and
try the clear button. Choices written in groups, as Django writes them, are
listed under their headings.

The link under the form loads the page again through htmx, which swaps the new
page in rather than loading it. Each control is started once htmx has finished
the swap, so it looks and works as it does on a page loaded in full.

| Option | Widget | What it does |
| --- | --- | --- |
| `placeholder` | Both | Text shown while nothing is chosen. |
| `clear_button` | Both | `True` adds a button that clears the control. |
| `remove_button` | `TomSelectMultiple` | `True` adds a button to each chosen value. |
| `max_items` | `TomSelectMultiple` | The most values that can be chosen. |
| `counted` | `TomSelectMultiple` | `True` shows a count in place of the chosen values. |
| `none_text` | `TomSelectMultiple` | What a counted control shows while nothing is chosen. |
| `count_text` | `TomSelectMultiple` | What a counted control shows after the count. |

The page loads Tom Select's complete build and the package's stylesheet
`mvp_forms/tomselect.css`. The widget brings its own small script with the
form's media.

## A count in place of the chosen values

With `counted=True`, the control shows how many values are chosen rather than
listing them. Each chosen option has a tick in the list, and the search box sits
at the top of the list.

```{live-example} /examples/tom-select-counted/
:title: Counted controls

../../examples/custom_widgets/counted_select.py
../../templates/demo/examples/tom_select_form.html
```

Untick every discipline and send the form to see the field in error. Search the
countries in the list and pick a few, then clear them with the button. A screen
reader is told each chosen value by name. Backspace in an empty search box
removes the value chosen last, as it does in any Tom Select control.

## In a row of filters

In a form that draws no labels, with `form_show_labels = False`, a select shows
its label inside its frame, before the value. A counted control reads "Category"
and then "2 selected", so a row of them can still be told apart once something is
chosen. A Tom Select control, a counted one and a stock select are all drawn this
way. A text input has no frame to show it in, so give it a placeholder.

```{live-example} /examples/filter-toolbar/
:title: Filters above a list of sites

../../examples/custom_widgets/filter_toolbar.py
```

The same row with a value chosen in every filter:

```{live-example} /examples/filter-toolbar-chosen/
:title: Filters with values chosen

../../examples/custom_widgets/filter_toolbar.py
```

Pressing the label opens the control. A screen reader hears the field's label
as the control's name, chosen or not.
