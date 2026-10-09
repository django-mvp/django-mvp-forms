"""The suite's urlconf: the demo project's routes plus any test-only route."""

from django.contrib.auth.models import Group
from django.urls import path
from django_tomselect.autocompletes import AutocompleteModelView

from demo.urls import urlpatterns as demo_urlpatterns


class GroupAutocomplete(AutocompleteModelView):
    """Groups, for the django-tomselect widgets that read a model."""

    model = Group
    search_lookups = ["name__icontains"]
    value_fields = ["id", "name"]
    skip_authorization = True


urlpatterns = [
    *demo_urlpatterns,
    path("autocomplete/groups/", GroupAutocomplete.as_view(), name="ac-groups"),
]
