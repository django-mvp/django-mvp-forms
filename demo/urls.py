"""URL routes for the demo project."""

from django.urls import include, path
from mvp.mounted import mount

from demo.autocompletes import (
    CountryAutocomplete,
    KeywordAutocomplete,
    LanguageAutocomplete,
    RockAutocomplete,
)
from demo.mounted import docs

urlpatterns = [
    # The pages the documentation shows in a frame as live examples.
    path("examples/", include("demo.examples.urls")),
    path("autocomplete/countries/", CountryAutocomplete.as_view(), name="ac-countries"),
    path(
        "autocomplete/languages/", LanguageAutocomplete.as_view(), name="ac-languages"
    ),
    path("autocomplete/keywords/", KeywordAutocomplete.as_view(), name="ac-keywords"),
    path("autocomplete/rocks/", RockAutocomplete.as_view(), name="ac-rocks"),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
    # The pages themselves, written in Markdown under demo/docs. They are the
    # site's main app, so their contents are the sidebar on every page. Mounted
    # last: the app answers every address nothing above it claims.
    mount("", docs, main=True),
]
