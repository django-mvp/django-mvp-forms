"""The forms of the demo's coordinates page."""

from decimal import Decimal

from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from mvp_forms.fields import LatitudeField, LongitudeField


class CoordinateForm(forms.Form):
    """A latitude and a longitude at their defaults. It must be given a prefix."""

    latitude = LatitudeField(
        label=_("Latitude"),
        help_text=_("LatitudeField(): from -90 to 90, up to six decimal places."),
    )
    longitude = LongitudeField(
        label=_("Longitude"),
        help_text=_("LongitudeField(): from -180 to 180, up to six decimal places."),
    )

    def __init__(self, *args, **kwargs):
        """Draw the two fields without a form tag of their own."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class InitialCoordinateForm(CoordinateForm):
    """The same two fields, drawn holding a place."""

    def __init__(self, *args, **kwargs):
        """Start the fields at the Greenwich meridian's neighbour, London."""
        kwargs.setdefault(
            "initial", {"latitude": Decimal("51.5074"), "longitude": -0.1278}
        )
        super().__init__(*args, **kwargs)


class BoundCoordinateForm(CoordinateForm):
    """The same two fields, sent with a latitude past 90 and too many places."""

    def __init__(self, *args, **kwargs):
        """Bind the form to a post that the fields refuse."""
        super().__init__(
            {"latitude": "95", "longitude": "-0.12775812"}, *args, **kwargs
        )
        self.is_valid()
