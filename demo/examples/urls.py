"""The address of every live example. Each is a page of its own, without the shell."""

from django.urls import path

from demo.examples.custom_fields.coordinate_fields import SiteForm
from demo.examples.custom_fields.partial_date_field import SampleForm
from demo.examples.custom_widgets.number_mask import InvoiceForm
from demo.examples.custom_widgets.pattern_mask import ContactForm
from demo.examples.formsets.stacked import OrderHelper, OrderLineFormSet
from demo.examples.layout_objects.tabs import ProfileForm
from demo.examples.modifiers.colour import ColouredForm
from demo.examples.modifiers.size import SmallForm
from demo.examples.modifiers.variant import GhostForm
from demo.examples.special_fields.checkbox_toggle_switch import NotificationsForm
from demo.examples.standard_fields import StandardFieldsForm
from demo.examples.third_party.countries import AddressForm
from demo.examples.views import ExampleView, FormsetExampleView

MASKED = "demo/examples/masked_form.html"

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
    path("countries/", ExampleView.as_view(form_class=AddressForm)),
]
