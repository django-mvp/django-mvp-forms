"""django-pint's own quantity fields, drawn by this package with nothing added."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, MultiWidgetField, Submit
from django import forms
from quantityfield.fields import (
    DecimalQuantityFormField,
    IntegerQuantityFormField,
    QuantityFormField,
)
from quantityfield.units import ureg

from mvp_forms.choices import Choice, FormChoices

MASS = ["kilogram", "gram", "pound"]
LENGTH = ["metre", "centimetre", "kilometre"]

# What the page sends on arrival, so every state shows without a click: a
# value with its unit, a required field left empty, and an optional one.
SENT = {
    "weight_0": "",
    "weight_1": "kilogram",
    "depth_0": "1250",
    "depth_1": "metre",
    "dose_0": "",
    "dose_1": "gram",
}


class QuantitiesForm(forms.Form):
    """A required weight, a depth with a value and an optional dose."""

    weight = QuantityFormField(
        base_units="kilogram", unit_choices=MASS, help_text="Dry weight"
    )
    depth = IntegerQuantityFormField(base_units="metre", unit_choices=LENGTH)
    dose = DecimalQuantityFormField(
        base_units="gram",
        unit_choices=["gram", "kilogram"],
        max_digits=8,
        decimal_places=3,
        required=False,
        help_text="Leave empty if none was given",
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))


class DisabledForm(forms.Form):
    """A weight that is shown and cannot be changed."""

    container = QuantityFormField(
        base_units="kilogram",
        unit_choices=MASS,
        disabled=True,
        initial=ureg.Quantity(0.35, "kilogram"),
        help_text="Weighed once, at the start",
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", "Save"))


class SizedForm(forms.Form):
    """One length in each of daisyUI's five sizes."""

    extra_small = QuantityFormField(base_units="metre", unit_choices=LENGTH)
    small = QuantityFormField(base_units="metre", unit_choices=LENGTH)
    medium = QuantityFormField(base_units="metre", unit_choices=LENGTH)
    large = QuantityFormField(base_units="metre", unit_choices=LENGTH)
    extra_large = QuantityFormField(base_units="metre", unit_choices=LENGTH)

    def __init__(self, *args, **kwargs):
        """Give each field its size."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            fields={
                "extra_small": Choice(size="xs"),
                "small": Choice(size="sm"),
                "medium": Choice(size="md"),
                "large": Choice(size="lg"),
                "extra_large": Choice(size="xl"),
            },
        )
        self.helper.add_input(Submit("submit", "Save"))


class NamedUnitForm(forms.Form):
    """A weight whose unit is named for a screen reader."""

    weight = QuantityFormField(
        base_units="kilogram", unit_choices=MASS, help_text="Dry weight"
    )

    def __init__(self, *args, **kwargs):
        """Name each part of the weight."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            MultiWidgetField(
                "weight",
                attrs=({"aria-label": "Weight"}, {"aria-label": "Weight unit"}),
            ),
        )
        self.helper.add_input(Submit("submit", "Save"))
