"""The demo's coordinates page."""

from crispy_forms.helper import FormHelper
from mvp.views import MVPTemplateView

from demo.coordinate_forms import (
    BoundCoordinateForm,
    CoordinateForm,
    InitialCoordinateForm,
    NarrowedCoordinateForm,
    PointForm,
    PointModalForm,
    SiteFormSet,
)


class CoordinatesView(MVPTemplateView):
    """The latitude and longitude fields at their defaults, with a value and in error."""

    template_name = "demo/coordinates.html"
    page_title = "Coordinates"
    page_subtitle = "A latitude and a longitude in decimal degrees"
    breadcrumbs = [{"text": "Coordinates"}]

    def get_context_data(self, **kwargs):
        """Add one form for each state of the two fields."""
        # The row "Add a site" copies: the formset's empty form, drawn alone.
        line = SiteFormSet(prefix="sites")
        line.forms = [line.empty_form]
        lines_helper = FormHelper()
        lines_helper.form_tag = False
        lines_helper.template = "daisyui/table_inline_formset.html"
        kwargs.update(
            lines=SiteFormSet(prefix="sites"),
            line=line,
            lines_helper=lines_helper,
            modal_form=PointModalForm(prefix="site"),
            sections=[
                (
                    "defaults",
                    "At their defaults",
                    "Type past 90 or 180, a seventh decimal place, a second full "
                    "stop or a letter and the input refuses it. The page loads "
                    "IMask for it.",
                    CoordinateForm(prefix="defaults"),
                ),
                (
                    "initial",
                    "With an initial value",
                    "The value is drawn with a full stop, whatever the language.",
                    InitialCoordinateForm(prefix="initial"),
                ),
                (
                    "narrowed",
                    "Narrowed to one country",
                    "Latitude 47.27 to 55.06 and longitude 5.87 to 15.04, to two "
                    "decimal places. A digit that no value in the range could "
                    "follow is refused.",
                    NarrowedCoordinateForm(prefix="narrowed"),
                ),
                (
                    "point",
                    "A point",
                    "PointField, drawn as a latitude and a longitude side by "
                    "side, each masked to its own range. The form cleans the "
                    "pair to WKT text that a GeoDjango PointField takes.",
                    PointForm(prefix="point"),
                ),
                (
                    "error",
                    "Sent and refused",
                    "A latitude past 90 and a longitude with eight decimal places, "
                    "as a form that was sent without IMask would hold them.",
                    BoundCoordinateForm(prefix="error"),
                ),
            ],
        )
        return super().get_context_data(**kwargs)
