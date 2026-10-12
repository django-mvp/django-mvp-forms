# django-countries

[django-countries](https://github.com/SmileyChris/django-countries) gives a
model a country field. Its form fields are ordinary selects, so the pack draws
them with nothing added: there is no widget to swap and no setting to change.

```{live-example} /examples/countries/
:title: One country, several, and one with its flag

../../examples/third_party/countries.py
```

The flag is django-countries' own `CountrySelectWidget`. Its `layout` argument
decides where the flag sits, and the one used here puts it beside the select.
