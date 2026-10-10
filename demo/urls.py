"""URL routes for the demo project."""

from django.urls import include, path

from demo.autocompletes import (
    CountryAutocomplete,
    KeywordAutocomplete,
    LanguageAutocomplete,
    RockAutocomplete,
)
from demo.partial_date_views import PartialDatesView, StandalonePartialDatesView
from demo.tomselect_views import (
    StandaloneTomSelectView,
    TomSelectBoostedView,
    TomSelectFetchedView,
    TomSelectView,
)
from demo.views import (
    AccordionView,
    AlertView,
    AttachedTextView,
    ChoiceInputsView,
    ChoicesView,
    ContainersStandaloneView,
    DecoratedFieldsStandaloneView,
    DrawingsView,
    FieldWithButtonsView,
    FloatingLabelsView,
    InlineChoicesView,
    InlineFieldView,
    InputMasksView,
    JoinedGroupsView,
    LayoutObjectsView,
    ModalView,
    MultiWidgetFieldView,
    OverviewView,
    RatingAndRangeView,
    StackedFormsetView,
    StandaloneChoiceInputsView,
    StandaloneChoicesView,
    StandaloneDrawingsView,
    StandaloneFloatingLabelsView,
    StandaloneInputMasksView,
    StandaloneJoinedGroupsView,
    StandaloneLayoutObjectsView,
    StandaloneRatingAndRangeView,
    StandaloneStackedFormsetView,
    StandaloneTableFormsetView,
    StandaloneTextInputsView,
    StandaloneThemesView,
    TableFormsetView,
    TabsView,
    TextInputsView,
    ThemesView,
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
        "multi-widget-field/",
        MultiWidgetFieldView.as_view(),
        name="multi-widget-field",
    ),
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
    path("drawings/", DrawingsView.as_view(), name="drawings"),
    path(
        "drawings/standalone/",
        StandaloneDrawingsView.as_view(),
        name="drawings-standalone",
    ),
    path("rating-and-range/", RatingAndRangeView.as_view(), name="rating-and-range"),
    path(
        "rating-and-range/standalone/",
        StandaloneRatingAndRangeView.as_view(),
        name="rating-and-range-standalone",
    ),
    path("floating-labels/", FloatingLabelsView.as_view(), name="floating-labels"),
    path(
        "floating-labels/standalone/",
        StandaloneFloatingLabelsView.as_view(),
        name="floating-labels-standalone",
    ),
    path("joined-groups/", JoinedGroupsView.as_view(), name="joined-groups"),
    path(
        "joined-groups/standalone/",
        StandaloneJoinedGroupsView.as_view(),
        name="joined-groups-standalone",
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
    path("input-masks/", InputMasksView.as_view(), name="input-masks"),
    path("partial-dates/", PartialDatesView.as_view(), name="partial-dates"),
    path(
        "partial-dates/standalone/",
        StandalonePartialDatesView.as_view(),
        name="partial-dates-standalone",
    ),
    path(
        "input-masks/standalone/",
        StandaloneInputMasksView.as_view(),
        name="input-masks-standalone",
    ),
    path("themes/", ThemesView.as_view(), name="themes"),
    path(
        "themes/standalone/",
        StandaloneThemesView.as_view(),
        name="themes-standalone",
    ),
    path("tomselect/", TomSelectView.as_view(), name="tomselect"),
    path(
        "tomselect/standalone/",
        StandaloneTomSelectView.as_view(),
        name="tomselect-standalone",
    ),
    path(
        "tomselect/fetched/", TomSelectFetchedView.as_view(), name="tomselect-fetched"
    ),
    path(
        "tomselect/boosted/", TomSelectBoostedView.as_view(), name="tomselect-boosted"
    ),
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
]
