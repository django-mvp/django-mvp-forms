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

| Option | Widget | What it does |
| --- | --- | --- |
| `placeholder` | Both | Text shown while nothing is chosen. |
| `clear_button` | Both | `True` adds a button that clears the control. |
| `remove_button` | `TomSelectMultiple` | `True` adds a button to each chosen value. |
| `max_items` | `TomSelectMultiple` | The most values that can be chosen. |

The page loads Tom Select's complete build and the package's stylesheet
`mvp_forms/tomselect.css`. The widget brings its own small script with the
form's media.
