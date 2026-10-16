# django-tomselect

[django-tomselect](https://github.com/OmenApps/django-tomselect) draws a select
that fetches its options from a view as you type. The pack draws it as it draws a
stock select, with the size, colour and variant of the form, and nothing is added
to the field. The package's stylesheet `mvp_forms/tomselect.css` keeps the
dropdown from being cut off, and your page loads it with django-tomselect's own
files.

```{live-example} /examples/django-tomselect/
:title: One value, several values, tags and groups

../../examples/third_party/tomselect.py
../../templates/demo/examples/django_tomselect_form.html
```

Type in the country control to search the list. The keywords control offers to
add a keyword the list does not hold, which needs a field that accepts it:
django-tomselect's stock multiple field refuses a value outside its choices, so
`TagsField` here does not. Options that carry an `optgroup` key are listed under
that heading in the rock control, provided `mvp_forms` comes before
`django_tomselect` in `INSTALLED_APPS`.

The autocomplete views behind the controls answer from lists, so the example
needs no model.
