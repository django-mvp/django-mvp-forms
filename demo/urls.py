"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import (
    LayoutObjectsView,
    OverviewView,
    StandaloneLayoutObjectsView,
    StandaloneTextInputsView,
    TextInputsView,
)

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("text-inputs/", TextInputsView.as_view(), name="text-inputs"),
    path(
        "text-inputs/standalone/",
        StandaloneTextInputsView.as_view(),
        name="text-inputs-standalone",
    ),
    path("layout-objects/", LayoutObjectsView.as_view(), name="layout-objects"),
    path(
        "layout-objects/standalone/",
        StandaloneLayoutObjectsView.as_view(),
        name="layout-objects-standalone",
    ),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
