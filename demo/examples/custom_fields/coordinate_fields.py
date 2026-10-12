"""A latitude, a longitude and a point, in decimal degrees."""

from decimal import Decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from mvp_forms.fields import LatitudeField, LongitudeField, PointField


class SiteForm(forms.Form):
    """Each field at its defaults, then narrowed, then as a pair."""

    latitude = LatitudeField(
        help_text="From -90 to 90, up to six decimal places.",
    )
    longitude = LongitudeField(
        help_text="From -180 to 180, up to six decimal places.",
    )
    latitude_in_germany = LatitudeField(
        label="Latitude in Germany",
        min_value=Decimal("47.27"),
        max_value=Decimal("55.06"),
        decimal_places=2,
        help_text="47.27 to 55.06, two places. A digit no value could take is refused.",
        required=False,
    )
    place = PointField(
        initial="SRID=4326;POINT(-0.1278 51.5074)",
        help_text="Cleans to WKT text, longitude first, for a GeoDjango PointField.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))
