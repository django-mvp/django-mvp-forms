# django-timezone-field

[django-timezone-field](https://github.com/mfogel/django-timezone-field) stores
a timezone and gives a form a field to choose one, `TimeZoneFormField`. Drawn
as it comes, that field is a plain select of several hundred names.

Name the package's `TimeZoneSelect` as its widget and the field becomes a
[Tom Select](../custom-widgets/tom-select.md) control you can type into, with
the timezones listed under their regions. The field still chooses, validates
and cleans the value, so the form receives a timezone as it did.

```{live-example} /examples/timezone/
:title: A timezone, and one shown with its offset from GMT

../../examples/third_party/timezone.py
```

Type part of a city, such as "buenos", to find it under America. Names with no
region, such as UTC, are listed under Other, at the end. The second field shows
each timezone with its offset from GMT, as django-timezone-field's
`choices_display="WITH_GMT_OFFSET"` writes it, still under its region.

Install it with the extra that names the release the widget is tested against:

```bash
pip install "django-mvp-forms[timezone]"
```

`TimeZoneSelect` takes the settings `TomSelect` takes, such as `placeholder` and
`clear_button`. For a model's `TimeZoneField`, name the widget in the form's
`Meta.widgets`.
