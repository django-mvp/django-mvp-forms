"""The forms the Tom Select widgets page draws."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_tomselect.forms import TomSelectMultipleChoiceField

from demo.forms import ChosenForm
from demo.tomselect_forms import multiple
from mvp_forms.choices import FormChoices
from mvp_forms.widgets import TomSelectMultiple

TOPICS = [
    ("geology", _("Geology")),
    ("glaciology", _("Glaciology")),
    ("petrology", _("Petrology")),
    ("seismology", _("Seismology")),
    ("tectonics", _("Tectonics")),
    ("volcanology", _("Volcanology")),
]


def topics_field(**kwargs):
    """Build the field the page is about: several values from a fixed list."""
    kwargs.setdefault("label", _("Topics"))
    return forms.MultipleChoiceField(choices=TOPICS, widget=TomSelectMultiple, **kwargs)


class TomSelectWidgetsForm(forms.Form):
    """The field beside a text input, which can be posted."""

    name = forms.CharField(label=_("Name"), required=False)
    topics = topics_field(
        help_text=_("Several values from a list written into the page.")
    )

    def __init__(self, *args, **kwargs):
        """Build the helper and a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class TomSelectWidgetsStateForm(ChosenForm):
    """The field in one state.

    Args:
        state: ``"filled"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with nothing posted, so the required field fails.
    """

    topics = topics_field()

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        if state in ("filled", "disabled"):
            self.initial.update(topics=["geology", "volcanology"])
        for field in self.fields.values():
            field.disabled = state == "disabled"


class TomSelectWidgetsChosenForm(ChosenForm):
    """The field under a size or a colour stated for the form.

    Args:
        size: The size the form states, or None.
        color: The colour the form states, or None.
    """

    topics = topics_field(required=False)

    def __init__(self, *args, size=None, color=None, **kwargs):
        """State the size and the colour for the form."""
        stated = {
            key: value for key, value in {"size": size, "color": color}.items() if value
        }
        super().__init__(*args, choices=FormChoices(**stated), **kwargs)
        self.helper.include_media = False
        self.initial.update(topics=["petrology", "tectonics"])


class TomSelectWidgetsComparisonForm(ChosenForm):
    """A stock multiple select, this package's widget and a django-tomselect control.

    The three are given the same list, and the form must be given a prefix.
    """

    stock = forms.MultipleChoiceField(
        label=_("A stock multiple select"), choices=TOPICS, required=False
    )
    widget = topics_field(label=_("TomSelectMultiple"), required=False)
    django = TomSelectMultipleChoiceField(
        label=_("A django-tomselect control"),
        config=multiple("ac-languages", _("Add a language")),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Hold the same values in the two selects that share a list."""
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        self.initial.update(
            stock=["geology", "volcanology"], widget=["geology", "volcanology"]
        )
