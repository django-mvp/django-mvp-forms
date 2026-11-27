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
