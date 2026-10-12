"""The forms the counted multiple select page draws.

Two drawings of one control: a multiple select that shows how many options are
chosen, not the options themselves, and marks each chosen option in its list.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from demo.forms import ChosenForm
from mvp_forms.widgets import TomSelectMultiple

DISCIPLINES = [
    "Geology", "Glaciology", "Petrology", "Seismology", "Tectonics", "Volcanology",
]  # fmt: skip

COUNTRY_NAMES = [str(name) for code, name in countries]

DATASETS = [
    "My extremely long option text possibly derived from the name of a django "
    "model instance",
    "Some other lengthy text from another record in the database",
    "Here we are again with more text",
    "These options are starting to get so long that they begin to wrap onto a new line",
    "Heat flow measurements from the continental margins, compiled 1990 to 2020",
    "Short one",
    "Borehole temperature logs with their corrections and the method each used",
    "Thermal conductivity of sedimentary rocks, measured on core samples",
]


class CountedCheckboxSelect(forms.CheckboxSelectMultiple):
    """Checkboxes in a list that opens under a button showing how many are ticked.

    It needs no script. The list is a popover, and the count is a CSS counter.
    """

    template_name = "demo/widgets/counted_select.html"


def named(names):
    """Pair each name with itself, as choices."""
    return [(name, name) for name in names]


def plain_field(label, names, **kwargs):
    """Build the control that needs no script."""
    return forms.MultipleChoiceField(
        label=label, choices=named(names), widget=CountedCheckboxSelect, **kwargs
    )


class CountedTomSelect(TomSelectMultiple):
    """The package's multiple widget, with a tick on each option and a search box.

    ``TomSelectMultiple`` has no setting for either plugin, so they are named here.
    """

    def control_settings(self):
        """Add Tom Select's two plugins to the settings that were stated."""
        settings = super().control_settings()
        settings.setdefault("plugins", []).extend(
            ["checkbox_options", "dropdown_input"]
        )
        return settings


def tomselect_field(label, names, **kwargs):
    """Build the Tom Select control: ticked options, a search box in the list."""
    return forms.MultipleChoiceField(
        label=label,
        choices=named(names),
        widget=CountedTomSelect(placeholder=_("Search"), clear_button=True),
        **kwargs,
    )


class PostedForm(forms.Form):
    """A form with a submit button named by its prefix."""

    def __init__(self, *args, **kwargs):
        """Build the helper and the button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class PlainCountedForm(PostedForm):
    """The three lists, each drawn with no script."""

    disciplines = plain_field(
        _("Disciplines"),
        DISCIPLINES,
        initial=["Geology", "Volcanology"],
        help_text=_("A few short options."),
    )
    countries = plain_field(
        _("Countries"),
        COUNTRY_NAMES,
        required=False,
        help_text=_("Every country. There is no search."),
    )
    datasets = plain_field(
        _("Datasets"),
        DATASETS,
        required=False,
        initial=DATASETS[:4],
        help_text=_("Options with long text."),
    )


class TomSelectCountedForm(PostedForm):
    """The same three lists, each drawn by the package's Tom Select widget."""

    disciplines = tomselect_field(
        _("Disciplines"),
        DISCIPLINES,
        initial=["Geology", "Volcanology"],
        help_text=_("A few short options."),
    )
    countries = tomselect_field(
        _("Countries"),
        COUNTRY_NAMES,
        required=False,
        help_text=_("Every country. Type to search."),
    )
    datasets = tomselect_field(
        _("Datasets"),
        DATASETS,
        required=False,
        initial=DATASETS[:4],
        help_text=_("Options with long text."),
    )


class PlainStateForm(ChosenForm):
    """The control that needs no script, in one state.

    Args:
        state: ``"empty"``, ``"one"``, ``"error"`` or ``"disabled"``.
    """

    disciplines = plain_field(_("Disciplines"), DISCIPLINES)

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        set_state(self, state)


class TomSelectStateForm(ChosenForm):
    """The Tom Select control, in one state.

    Args:
        state: ``"empty"``, ``"one"``, ``"error"`` or ``"disabled"``.
    """

    disciplines = tomselect_field(_("Disciplines"), DISCIPLINES)

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        set_state(self, state)


def set_state(form, state):
    """Give a state form its values, and disable it when the state says so."""
    if state == "one":
        form.initial["disciplines"] = ["Petrology"]
    if state == "disabled":
        form.initial["disciplines"] = ["Geology", "Petrology", "Tectonics"]
        form.fields["disciplines"].disabled = True
    if state != "error":
        form.fields["disciplines"].required = False
