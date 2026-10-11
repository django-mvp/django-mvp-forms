"""The forms the Tom Select widgets page draws."""

from crispy_forms.bootstrap import Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.forms import formset_factory
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

GROUPED_TOPICS = [
    (_("Rock"), [("geology", _("Geology")), ("petrology", _("Petrology"))]),
    (
        _("Movement"),
        [
            ("seismology", _("Seismology")),
            ("tectonics", _("Tectonics")),
            ("volcanology", _("Volcanology")),
        ],
    ),
    ("glaciology", _("Glaciology")),
]


class UnavailableTomSelectMultiple(TomSelectMultiple):
    """A multiple widget that draws the volcanology option as unavailable."""

    unavailable = "volcanology"

    def create_option(self, name, value, *args, **kwargs):
        """Draw the unavailable option with the ``disabled`` attribute."""
        option = super().create_option(name, value, *args, **kwargs)
        if value == self.unavailable:
            option["attrs"]["disabled"] = True
        return option


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


class TomSelectWidgetsGroupsForm(ChosenForm):
    """Both widgets over choices written in groups, and one option unavailable.

    The single widget lists the options under their headings. The multiple
    widget is a subclass that draws one option with the ``disabled`` attribute.
    """

    topic = forms.ChoiceField(
        label=_("TomSelect"),
        choices=[("", _("No topic")), *GROUPED_TOPICS],
        required=False,
        widget=TomSelect,
        help_text=_("Options under headings, with one left outside every group."),
    )
    topics = forms.MultipleChoiceField(
        label=_("TomSelectMultiple"),
        choices=GROUPED_TOPICS,
        required=False,
        widget=UnavailableTomSelectMultiple,
        help_text=_("Volcanology is listed and cannot be chosen."),
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


class TomSelectWidgetsLineForm(forms.Form):
    """One line of the formset: a sample, and the topics it belongs to."""

    name = forms.CharField(label=_("Sample"), required=False)
    topics = forms.MultipleChoiceField(
        label=_("Topics"),
        choices=TOPICS,
        required=False,
        widget=TomSelectMultiple(placeholder=_("Pick topics"), remove_button=True),
    )


TomSelectWidgetsLineFormSet = formset_factory(TomSelectWidgetsLineForm, extra=2)


class TomSelectWidgetsModalForm(forms.Form):
    """A form whose controls sit in a modal. The form must be given a prefix."""

    name = forms.CharField(label=_("Sample"), required=False)
    topic = topic_field(choices=OPTIONAL_TOPICS, required=False)
    topics = topics_field(required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            "name",
            Modal(
                "topic",
                "topics",
                css_id=self.dialog_id,
                title=_("Topics"),
                title_id=f"{self.prefix}-title",
            ),
        )

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the button that opens it."""
        return f"{self.prefix}-dialog"
