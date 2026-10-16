"""The address of every live example. Each is a page of its own, without the shell."""

from django.urls import path

from demo.examples.custom_fields.coordinate_fields import SiteForm
from demo.examples.custom_fields.partial_date_field import SampleForm
from demo.examples.custom_widgets.dynamic_mask import PhoneForm
from demo.examples.custom_widgets.number_mask import InvoiceForm
from demo.examples.custom_widgets.partial_date_input import PartDatesForm
from demo.examples.custom_widgets.partial_date_mask import MaskedDatesForm
from demo.examples.custom_widgets.partial_date_select import SelectDatesForm
from demo.examples.custom_widgets.pattern_mask import ContactForm
from demo.examples.custom_widgets.regex_mask import AccountForm
from demo.examples.custom_widgets.tom_select import TopicsForm
from demo.examples.formsets.stacked import OrderHelper, OrderLineFormSet
from demo.examples.formsets.table import OrderHelper as TableOrderHelper
from demo.examples.formsets.table import OrderLineFormSet as TableOrderLineFormSet
from demo.examples.layout_objects.accordion import ChosenGroupForm
from demo.examples.layout_objects.accordion import ProfileForm as AccordionForm
from demo.examples.layout_objects.alert import NoticeForm
from demo.examples.layout_objects.buttons import ActionsForm, HolderForm
from demo.examples.layout_objects.fieldsets_rows_columns import DetailsForm
from demo.examples.layout_objects.joined_groups import PhoneForm
from demo.examples.layout_objects.modal import AddressForm as ModalForm
from demo.examples.layout_objects.multi_widget_field import EventForm
from demo.examples.layout_objects.tabs import ProfileForm
from demo.examples.modifiers.attached_text import PriceForm
from demo.examples.modifiers.colour import ColouredForm
from demo.examples.modifiers.field_with_buttons import SearchForm
from demo.examples.modifiers.floating_field import NameForm
from demo.examples.modifiers.floating_labels import SignInForm
from demo.examples.modifiers.inline_field import FilterForm
from demo.examples.modifiers.size import SmallForm
from demo.examples.modifiers.state import StateForm
from demo.examples.modifiers.uneditable_field import ProfileForm as UneditableForm
from demo.examples.modifiers.variant import GhostForm
from demo.examples.special_fields.checkbox_toggle_switch import NotificationsForm
from demo.examples.special_fields.inline_choices import SurveyForm
from demo.examples.special_fields.rating_and_range import ReviewForm
from demo.examples.standard_fields import StandardFieldsForm
from demo.examples.third_party.countries import AddressForm
from demo.examples.third_party.tomselect import ResearchForm
from demo.examples.views import ExampleView, FormsetExampleView

MASKED = "demo/examples/masked_form.html"
TOM_SELECT = "demo/examples/tom_select_form.html"
DJANGO_TOMSELECT = "demo/examples/django_tomselect_form.html"

urlpatterns = [
    path(
        "standard-fields/",
        ExampleView.as_view(
            form_class=StandardFieldsForm,
            template_name="demo/examples/plain_form.html",
        ),
    ),
    path(
        "checkbox-toggle-switch/",
        ExampleView.as_view(form_class=NotificationsForm),
    ),
    path("inline-choices/", ExampleView.as_view(form_class=SurveyForm)),
    path("rating-and-range/", ExampleView.as_view(form_class=ReviewForm)),
    path("attached-text/", ExampleView.as_view(form_class=PriceForm)),
    path("field-with-buttons/", ExampleView.as_view(form_class=SearchForm)),
    path("floating-labels/", ExampleView.as_view(form_class=SignInForm)),
    path("floating-field/", ExampleView.as_view(form_class=NameForm)),
    path("inline-field/", ExampleView.as_view(form_class=FilterForm)),
    path("state/", ExampleView.as_view(form_class=StateForm)),
    path("uneditable-field/", ExampleView.as_view(form_class=UneditableForm)),
    path("size/", ExampleView.as_view(form_class=SmallForm)),
    path("colour/", ExampleView.as_view(form_class=ColouredForm)),
    path("variant/", ExampleView.as_view(form_class=GhostForm)),
    path("tabs/", ExampleView.as_view(form_class=ProfileForm)),
    path("fieldsets-rows-columns/", ExampleView.as_view(form_class=DetailsForm)),
    path("button-holder/", ExampleView.as_view(form_class=HolderForm)),
    path("form-actions/", ExampleView.as_view(form_class=ActionsForm)),
    path("joined-groups/", ExampleView.as_view(form_class=PhoneForm)),
    path("multi-widget-field/", ExampleView.as_view(form_class=EventForm)),
    path("accordion/", ExampleView.as_view(form_class=AccordionForm)),
    path("accordion-chosen/", ExampleView.as_view(form_class=ChosenGroupForm)),
    path(
        "modal/",
        ExampleView.as_view(
            form_class=ModalForm, template_name="demo/examples/modal_form.html"
        ),
    ),
    path("alert/", ExampleView.as_view(form_class=NoticeForm)),
    path(
        "formset-stacked/",
        FormsetExampleView.as_view(
            form_class=OrderLineFormSet, helper_class=OrderHelper
        ),
    ),
    path(
        "formset-table/",
        FormsetExampleView.as_view(
            form_class=TableOrderLineFormSet, helper_class=TableOrderHelper
        ),
    ),
    path("partial-date-field/", ExampleView.as_view(form_class=SampleForm)),
    path(
        "coordinate-fields/",
        ExampleView.as_view(form_class=SiteForm, template_name=MASKED),
    ),
    path(
        "pattern-mask/",
        ExampleView.as_view(form_class=ContactForm, template_name=MASKED),
    ),
    path(
        "number-mask/",
        ExampleView.as_view(form_class=InvoiceForm, template_name=MASKED),
    ),
    path(
        "regex-mask/",
        ExampleView.as_view(form_class=AccountForm, template_name=MASKED),
    ),
    path(
        "dynamic-mask/",
        ExampleView.as_view(form_class=PhoneForm, template_name=MASKED),
    ),
    path(
        "partial-date-mask/",
        ExampleView.as_view(form_class=MaskedDatesForm, template_name=MASKED),
    ),
    path("partial-date-input/", ExampleView.as_view(form_class=PartDatesForm)),
    path("partial-date-select/", ExampleView.as_view(form_class=SelectDatesForm)),
    path(
        "tom-select/",
        ExampleView.as_view(form_class=TopicsForm, template_name=TOM_SELECT),
    ),
    path(
        "django-tomselect/",
        ExampleView.as_view(form_class=ResearchForm, template_name=DJANGO_TOMSELECT),
    ),
    path("countries/", ExampleView.as_view(form_class=AddressForm)),
]
