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

## Some countries first

django-countries can list some countries ahead of the rest, through `first`
and `first_break` on a `Countries` subclass given to the field, or the
`COUNTRIES_FIRST` and `COUNTRIES_FIRST_BREAK` settings for every field. The
country widgets keep those countries at the top and list the rest under a
heading of the break's text. Without `first_break` the countries first sit at
the top with no heading. A control lists each country once, so with
`first_repeat` the countries first are not listed again below.

```python
from django_countries import Countries


class GermanSpeakingFirst(Countries):
    first = ["DE", "AT", "CH"]
    first_break = "Other"
```

```{live-example} /examples/countries/first/
:title: Three countries first, in a stock select and in the country widgets

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

`CountryAutocomplete` answers from django-countries' own list. Give
`as_view()` a `countries` to answer from another, such as
`CountryAutocomplete.as_view(countries=GermanSpeakingFirst())`, and the
countries first come first in its results too, the rest under the break's
heading.

The flag is the image django-countries serves for each country. Neither way
needs a stylesheet of its own.
