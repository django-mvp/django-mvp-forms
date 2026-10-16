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
from demo.examples.layout_objects.tabs import ProfileForm
from demo.examples.modifiers.colour import ColouredForm
from demo.examples.modifiers.size import SmallForm
from demo.examples.modifiers.variant import GhostForm
from demo.examples.special_fields.checkbox_toggle_switch import NotificationsForm
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
    path("size/", ExampleView.as_view(form_class=SmallForm)),
    path("colour/", ExampleView.as_view(form_class=ColouredForm)),
    path("variant/", ExampleView.as_view(form_class=GhostForm)),
    path("tabs/", ExampleView.as_view(form_class=ProfileForm)),
    path(
        "formset-stacked/",
        FormsetExampleView.as_view(
            form_class=OrderLineFormSet, helper_class=OrderHelper
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
