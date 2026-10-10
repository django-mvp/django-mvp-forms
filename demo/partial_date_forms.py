"""The forms of the demo's partial date page."""

import datetime

from crispy_forms.bootstrap import Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _

from mvp_forms.choices import Choice
from mvp_forms.fields import PartialDateField
from mvp_forms.widgets import (
    PartialDateInput,
    PartialDateMaskInput,
    PartialDateSelect,
)


class PartialDateForm(forms.Form):
    """One field for each resolution option. It must be given a prefix.

    A subclass names the widget every field is drawn with.
    """

    widget: type[forms.Widget] = forms.TextInput

    any_resolution = PartialDateField(
        label=_("Collected"),
        help_text=_("PartialDateField(): a year, a year and month, or a full date."),
    )
    at_least_month = PartialDateField(
        label=_("Analysed"),
        help_text=_(
            'PartialDateField(min_resolution="month"): a year alone is refused.'
        ),
        min_resolution="month",
        required=False,
    )
    no_day = PartialDateField(
        label=_("Published"),
        help_text=_('PartialDateField(max_resolution="month"): no day can be entered.'),
        max_resolution="month",
        required=False,
    )
    year_only = PartialDateField(
        label=_("Founded"),
        help_text=_(
            'PartialDateField(max_resolution="year"): a year and nothing else.'
        ),
        max_resolution="year",
        required=False,
    )
    in_range = PartialDateField(
        label=_("Sampled"),
        help_text=_(
            'PartialDateField(min_value="1998-03-15", max_value=date.today()): '
            "nothing before 15 March 1998 and nothing after today."
        ),
        min_value="1998-03-15",
        max_value=datetime.date.today(),
        required=False,
    )
    in_range_no_day = PartialDateField(
        label=_("Reported"),
        help_text=_(
            'PartialDateField(min_value="1998-03", max_value="2004-09", '
            'max_resolution="month"): a range of months, with no day.'
        ),
        min_value="1998-03",
        max_value="2004-09",
        max_resolution="month",
        required=False,
    )

    def __init__(self, *args, posts=True, **kwargs):
        """Give every field the widget, and a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget = self.widget()
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))
        else:
            self.helper.form_tag = False


class MaskedPartialDateForm(PartialDateForm):
    """Every field drawn as one masked input."""

    widget = PartialDateMaskInput


class ThreePartPartialDateForm(PartialDateForm):
    """Every field drawn as a year, a month and a day."""

    widget = PartialDateInput


class SelectPartialDateForm(PartialDateForm):
    """Every field drawn as three selects."""

    widget = PartialDateSelect


class PlainPartialDateForm(forms.Form):
    """The field with no widget named. It must be given a prefix."""

    collected = PartialDateField(
        label=_("Collected"),
        help_text=_("A plain text input. Nothing is checked until the form is sent."),
    )

    def __init__(self, *args, **kwargs):
        """Build the helper, with a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class PartialDateStatesForm(forms.Form):
    """A partial date at each resolution, disabled, and in error.

    A subclass names the widget every field is drawn with.
    """

    widget: type[forms.Widget] = forms.TextInput
    sent_values = {
        "year": "1987",
        "month": "1987-06",
        "day": "1987-06-30",
        "impossible": "2021-02-30",
        "gap": "2021--14",
        "early": "1990-06",
    }

    year = PartialDateField(label=_("Known to the year"), required=False)
    month = PartialDateField(label=_("Known to the month"), required=False)
    day = PartialDateField(label=_("Known to the day"), required=False)
    disabled = PartialDateField(
        label=_("Disabled"), initial="1987-06", disabled=True, required=False
    )
    empty = PartialDateField(
        label=_("Required and sent empty"),
        help_text=_("The error is the field's own required message."),
    )
    impossible = PartialDateField(
        label=_("A day the month does not have"),
        help_text=_("Sent as 2021-02-30 from a page with no script."),
    )
    gap = PartialDateField(
        label=_("A day with no month"),
        help_text=_("Sent as a year and a day from a page with no script."),
    )
    early = PartialDateField(
        label=_("Earlier than the earliest date"),
        help_text=_(
            'min_value="1998-03-15", sent as 1990-06 from a page with no script.'
        ),
        min_value="1998-03-15",
    )

    def __init__(self, **kwargs):
        """Bind the form to its values and draw no form element or button."""
        prefix = kwargs["prefix"]
        widget = self.widget()
        sent = {}
        for name, value in self.sent_values.items():
            if isinstance(widget, forms.MultiWidget):
                parts = [*value.split("-"), "", ""][:3]
                for part, entered in zip(("year", "month", "day"), parts, strict=True):
                    sent[f"{prefix}-{name}_{part}"] = entered
            else:
                sent[f"{prefix}-{name}"] = value
        super().__init__(sent, **kwargs)
        for field in self.fields.values():
            field.widget = self.widget()
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class MaskedStatesForm(PartialDateStatesForm):
    """Each state drawn as one masked input."""

    widget = PartialDateMaskInput

    def __init__(self, **kwargs):
        """Leave out the state one input cannot be brought to."""
        super().__init__(**kwargs)
        del self.fields["gap"]
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class ThreePartStatesForm(PartialDateStatesForm):
    """Each state drawn as a year, a month and a day."""

    widget = PartialDateInput


class SelectStatesForm(PartialDateStatesForm):
    """Each state drawn as three selects."""

    widget = PartialDateSelect


class PartialDateSizesForm(forms.Form):
    """Each widget at each size, and with a colour."""

    masked_xs = PartialDateField(label=_("Extra small"), required=False)
    parts_xs = PartialDateField(label=_("Extra small"), required=False)
    select_xs = PartialDateField(label=_("Extra small"), required=False)
    masked_sm = PartialDateField(label=_("Small"), required=False)
    parts_sm = PartialDateField(label=_("Small"), required=False)
    select_sm = PartialDateField(label=_("Small"), required=False)
    masked_lg = PartialDateField(label=_("Large"), required=False)
    parts_lg = PartialDateField(label=_("Large"), required=False)
    select_lg = PartialDateField(label=_("Large"), required=False)
    masked_primary = PartialDateField(label=_("Primary"), required=False)
    parts_primary = PartialDateField(label=_("Primary"), required=False)
    select_primary = PartialDateField(label=_("Primary"), required=False)

    def __init__(self, *args, **kwargs):
        """Give each field its widget and state a choice for each."""
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widgets = {
                "masked": PartialDateMaskInput,
                "parts": PartialDateInput,
                "select": PartialDateSelect,
            }
            field.widget = widgets[name.split("_")[0]]()
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Choice("masked_xs", size="xs"),
            Choice("parts_xs", size="xs"),
            Choice("select_xs", size="xs"),
            Choice("masked_sm", size="sm"),
            Choice("parts_sm", size="sm"),
            Choice("select_sm", size="sm"),
            Choice("masked_lg", size="lg"),
            Choice("parts_lg", size="lg"),
            Choice("select_lg", size="lg"),
            Choice("masked_primary", color="primary"),
            Choice("parts_primary", color="primary"),
            Choice("select_primary", color="primary"),
        )


class SampleForm(forms.Form):
    """One sample: its name, and when it was collected and analysed."""

    name = forms.CharField(label=_("Sample"))
    collected = PartialDateField(label=_("Collected"), widget=PartialDateInput)
    analysed = PartialDateField(
        label=_("Analysed"), required=False, widget=PartialDateMaskInput
    )


SampleFormSet = formset_factory(SampleForm, extra=2)


class PartialDateModalForm(forms.Form):
    """A form whose partial dates sit in a modal. It must be given a prefix."""

    name = forms.CharField(label=_("Sample"), required=False)
    collected = PartialDateField(
        label=_("Collected"), required=False, widget=PartialDateInput
    )
    analysed = PartialDateField(
        label=_("Analysed"), required=False, widget=PartialDateMaskInput
    )

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "name",
            Modal(
                "collected",
                "analysed",
                css_id=self.dialog_id,
                title=_("Dates"),
                title_id=f"{self.prefix}-title",
            ),
        )

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the control that opens it."""
        return f"{self.prefix}-dialog"
