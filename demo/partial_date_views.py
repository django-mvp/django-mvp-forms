"""The demo's partial date page."""

from crispy_forms.helper import FormHelper
from mvp.views import MVPTemplateView

from demo.partial_date_forms import (
    MaskedPartialDateForm,
    MaskedStatesForm,
    PartialDateModalForm,
    PartialDateSizesForm,
    PlainPartialDateForm,
    SampleFormSet,
    SelectPartialDateForm,
    SelectStatesForm,
    ThreePartPartialDateForm,
    ThreePartStatesForm,
)


class PartialDatesView(MVPTemplateView):
    """The partial date field with each widget, inside the application shell."""

    template_name = "demo/partial_dates.html"
    page_title = "Partial dates"
    page_subtitle = "A date known to the year, the month or the day"
    breadcrumbs = [{"text": "Partial dates"}]

    widgets = [
        (
            "masked",
            "One masked input",
            "PartialDateMaskInput. Type digits and the hyphens are placed for "
            "you. Stop after the year or the month, or go on to the day. A "
            "month above 12 and a day the month does not have are not accepted. "
            "The page loads IMask for it.",
            MaskedPartialDateForm,
        ),
        (
            "parts",
            "Year, month and day",
            "PartialDateInput. Enter a year, then choose a month and a day if "
            "they are known. The days on offer follow the month and the year. "
            "It needs no IMask.",
            ThreePartPartialDateForm,
        ),
        (
            "select",
            "Year, month and day, all chosen",
            "PartialDateSelect. The same three parts with the year as a select. "
            "The years on offer run from the field's earliest date to its "
            "latest, and reach a hundred years back from this year where one "
            "is not stated.",
            SelectPartialDateForm,
        ),
        (
            "plain",
            "No widget named",
            "The field alone, drawn as a text input with no script. The same "
            "rules are applied when the form is sent.",
            PlainPartialDateForm,
        ),
    ]

    def get_context_data(self, **kwargs):
        """Add a group for each widget, then the states, sizes and places."""
        posted = kwargs.pop("posted", None)
        groups = []
        for prefix, name, text, form_class in self.widgets:
            form = form_class(prefix=prefix)
            received = None
            if posted is not None and f"{prefix}-submit" in posted:
                form = form_class(posted, prefix=prefix)
                if form.is_valid():
                    received = [
                        (form[field].label, value)
                        for field, value in form.cleaned_data.items()
                    ]
            groups.append(
                {
                    "id": prefix,
                    "name": name,
                    "text": text,
                    "form": form,
                    "received": received,
                }
            )
        lines_helper = FormHelper()
        lines_helper.form_tag = False
        lines_helper.template = "daisyui/table_inline_formset.html"
        kwargs.update(
            groups=groups,
            states=[
                ("One masked input", MaskedStatesForm(prefix="masked-states")),
                ("Year, month and day", ThreePartStatesForm(prefix="parts-states")),
                (
                    "Year, month and day, all chosen",
                    SelectStatesForm(prefix="select-states"),
                ),
            ],
            sizes_form=PartialDateSizesForm(prefix="sizes"),
            lines=SampleFormSet(prefix="samples"),
            lines_helper=lines_helper,
            modal_form=PartialDateModalForm(prefix="dates"),
        )
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        """Draw the page again with what the posted form's fields received."""
        return self.render_to_response(self.get_context_data(posted=request.POST))
