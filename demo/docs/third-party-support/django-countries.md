# django-countries

[django-countries](https://github.com/SmileyChris/django-countries) gives a
model a country field. Its form field is an ordinary select, which the pack
draws as it draws any other. A list of some 250 countries is easier to use with
a search box, so `mvp_forms.countries` has controls that search the list and
show each country with its flag.

## Countries that come with the form

`CountrySelect` and `CountrySelectMultiple` are the pack's Tom Select widgets
with a flag beside each country, in the list and in each chosen value. They
take every setting `TomSelect` and `TomSelectMultiple` take, so a multiple one
can have a remove button on each country, or be counted. Every country is
written into the page with the form.

```{live-example} /examples/countries/
:title: A stock select, one country searched, several, and several counted

../../examples/third_party/countries.py
```

## Countries fetched as you type

`CountryAutocomplete` is a django-tomselect view that answers with every country
django-countries lists, each with its code, its name and its flag. Give it a
URL, and `country_config` configures a django-tomselect field to fetch from it
with the same flag in every option. The page holds none of the list until a
person opens the control.

```python
from django.urls import path
from mvp_forms.countries import CountryAutocomplete

urlpatterns = [
    path("countries/", CountryAutocomplete.as_view(), name="countries"),
]
```

```{live-example} /examples/countries/fetched/
:title: One country and several, fetched as you type

../../examples/third_party/countries.py
../../templates/demo/examples/django_tomselect_form.html
```

The flag is the image django-countries serves for each country. Neither way
needs a stylesheet of its own.
