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


class NarrowedCoordinateForm(CoordinateForm):
    """A latitude and a longitude narrowed to one country, with two places."""

    latitude = LatitudeField(
        label=_("Latitude"),
        min_value=Decimal("47.27"),
        max_value=Decimal("55.06"),
        decimal_places=2,
        help_text=_(
            "LatitudeField(min_value=47.27, max_value=55.06, decimal_places=2)"
        ),
    )
    longitude = LongitudeField(
        label=_("Longitude"),
        min_value=Decimal("5.87"),
        max_value=Decimal("15.04"),
        decimal_places=2,
        help_text=_(
            "LongitudeField(min_value=5.87, max_value=15.04, decimal_places=2)"
        ),
    )
