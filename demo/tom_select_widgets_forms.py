"""The forms the Tom Select widgets page draws."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField

from demo.forms import ChosenForm
from demo.tomselect_forms import multiple, single
from mvp_forms.choices import FormChoices
from mvp_forms.widgets import TomSelect, TomSelectMultiple

TOPICS = [
    ("geology", _("Geology")),
    ("glaciology", _("Glaciology")),
    ("petrology", _("Petrology")),
    ("seismology", _("Seismology")),
    ("tectonics", _("Tectonics")),
    ("volcanology", _("Volcanology")),
]


OPTIONAL_TOPICS = [("", _("No topic")), *TOPICS]


def topics_field(**kwargs):
    """Build the field the page is about: several values from a fixed list."""
    kwargs.setdefault("label", _("Topics"))
    return forms.MultipleChoiceField(choices=TOPICS, widget=TomSelectMultiple, **kwargs)


def topic_field(**kwargs):
    """Build the single field: one value from the same list."""
    kwargs.setdefault("label", _("Topic"))
    kwargs.setdefault("choices", TOPICS)
    return forms.ChoiceField(widget=TomSelect, **kwargs)


class TomSelectWidgetsForm(forms.Form):
    """The two fields beside a text input, which can be posted."""

    name = forms.CharField(label=_("Name"), required=False)
    topic = topic_field(
        choices=OPTIONAL_TOPICS,
        required=False,
        help_text=_("One value from a list. Backspace returns it to no value."),
    )
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
    """The fields in one state.

    Args:
        state: ``"filled"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with nothing posted, so the required field fails.
    """

    topic = topic_field()
    topics = topics_field()

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        if state in ("filled", "disabled"):
            self.initial.update(topic="geology", topics=["geology", "volcanology"])
        for field in self.fields.values():
            field.disabled = state == "disabled"


class TomSelectWidgetsChosenForm(ChosenForm):
    """The fields under a size or a colour stated for the form.

    Args:
        size: The size the form states, or None.
        color: The colour the form states, or None.
    """

    topic = topic_field(required=False)
    topics = topics_field(required=False)

    def __init__(self, *args, size=None, color=None, **kwargs):
        """State the size and the colour for the form."""
        stated = {
            key: value for key, value in {"size": size, "color": color}.items() if value
        }
        super().__init__(*args, choices=FormChoices(**stated), **kwargs)
        self.helper.include_media = False
        self.initial.update(topic="petrology", topics=["petrology", "tectonics"])


class TomSelectWidgetsSettingsForm(ChosenForm):
    """Both widgets with every setting each of them takes.

    The single widget takes a placeholder and a clear button. The multiple widget
    adds a button on each chosen value and the largest number of values.
    """

    topic = forms.ChoiceField(
        label=_("TomSelect"),
        choices=OPTIONAL_TOPICS,
        required=False,
        widget=TomSelect(placeholder=_("Pick a topic"), clear_button=True),
        help_text=_("A placeholder while empty, and a button that clears it."),
    )
    topics = forms.MultipleChoiceField(
        label=_("TomSelectMultiple"),
        choices=TOPICS,
        required=False,
        widget=TomSelectMultiple(
            placeholder=_("Pick up to three topics"),
            clear_button=True,
            remove_button=True,
            max_items=3,
        ),
        help_text=_("A button on each value, and no more than three values."),
    )

    def __init__(self, *args, **kwargs):
        """Leave the media to the page."""
        super().__init__(*args, **kwargs)
        self.helper.include_media = False


class TomSelectWidgetsComparisonForm(ChosenForm):
    """A stock select, this package's widget and a django-tomselect control, twice.

    Each kind is drawn once for one value and once for several. The three of a
    kind are given the same list, and the form must be given a prefix.
    """

    stock_single = forms.ChoiceField(
        label=_("A stock single select"), choices=OPTIONAL_TOPICS, required=False
    )
    widget_single = topic_field(
        label=_("TomSelect"), choices=OPTIONAL_TOPICS, required=False
    )
    django_single = TomSelectChoiceField(
        label=_("A django-tomselect single control"),
        config=single("ac-languages", _("Pick a language")),
        required=False,
    )
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
        """Hold the same values in the selects that share a list."""
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        self.initial.update(
            stock_single="geology",
            widget_single="geology",
            stock=["geology", "volcanology"],
            widget=["geology", "volcanology"],
        )
