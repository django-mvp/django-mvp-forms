"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import (
    AccordionView,
    AlertView,
    ChoiceInputsView,
    ChoicesView,
    ContainersStandaloneView,
    LayoutObjectsView,
    ModalView,
    OverviewView,
    StandaloneChoiceInputsView,
    StandaloneChoicesView,
    StandaloneLayoutObjectsView,
    StandaloneTextInputsView,
    TabsView,
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
    path("choice-inputs/", ChoiceInputsView.as_view(), name="choice-inputs"),
    path(
        "choice-inputs/standalone/",
        StandaloneChoiceInputsView.as_view(),
        name="choice-inputs-standalone",
    ),
    path("layout-objects/", LayoutObjectsView.as_view(), name="layout-objects"),
    path(
        "layout-objects/standalone/",
        StandaloneLayoutObjectsView.as_view(),
        name="layout-objects-standalone",
    ),
    path("tabs/", TabsView.as_view(), name="tabs"),
    path("accordion/", AccordionView.as_view(), name="accordion"),
    path("modal/", ModalView.as_view(), name="modal"),
    path("alert/", AlertView.as_view(), name="alert"),
    path(
        "containers/standalone/",
        ContainersStandaloneView.as_view(),
        name="containers-standalone",
    ),
    path("choices/", ChoicesView.as_view(), name="choices"),
    path(
        "choices/standalone/",
        StandaloneChoicesView.as_view(),
        name="choices-standalone",
    ),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
