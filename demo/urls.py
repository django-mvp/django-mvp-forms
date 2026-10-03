"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import (
    AccordionView,
    AlertView,
    AttachedTextView,
    ChoiceInputsView,
    ChoicesView,
    ContainersStandaloneView,
    DecoratedFieldsStandaloneView,
    FieldWithButtonsView,
    InlineChoicesView,
    InlineFieldView,
    LayoutObjectsView,
    ModalView,
    OverviewView,
    StackedFormsetView,
    StandaloneChoiceInputsView,
    StandaloneChoicesView,
    StandaloneLayoutObjectsView,
    StandaloneStackedFormsetView,
    StandaloneTableFormsetView,
    StandaloneTextInputsView,
    TableFormsetView,
    TabsView,
    TextInputsView,
    UneditableFieldView,
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
    path("attached-text/", AttachedTextView.as_view(), name="attached-text"),
    path("inline-choices/", InlineChoicesView.as_view(), name="inline-choices"),
    path(
        "field-with-buttons/", FieldWithButtonsView.as_view(), name="field-with-buttons"
    ),
    path("uneditable-field/", UneditableFieldView.as_view(), name="uneditable-field"),
    path("inline-field/", InlineFieldView.as_view(), name="inline-field"),
    path(
        "decorated-fields/standalone/",
        DecoratedFieldsStandaloneView.as_view(),
        name="decorated-fields-standalone",
    ),
    path("choices/", ChoicesView.as_view(), name="choices"),
    path(
        "choices/standalone/",
        StandaloneChoicesView.as_view(),
        name="choices-standalone",
    ),
    path("formset-stacked/", StackedFormsetView.as_view(), name="formset-stacked"),
    path(
        "formset-stacked/standalone/",
        StandaloneStackedFormsetView.as_view(),
        name="formset-stacked-standalone",
    ),
    path("formset-table/", TableFormsetView.as_view(), name="formset-table"),
    path(
        "formset-table/standalone/",
        StandaloneTableFormsetView.as_view(),
        name="formset-table-standalone",
    ),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
