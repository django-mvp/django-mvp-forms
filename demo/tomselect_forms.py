"""The forms the django-tomselect page draws."""

from crispy_forms.bootstrap import Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django_tomselect.app_settings import (
    PluginClearButton,
    PluginRemoveButton,
    TomSelectConfig,
)
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField

from demo.forms import ChosenForm
from mvp_forms.choices import FormChoices

PLANS = [("", _("Pick a plan")), ("free", _("Free")), ("team", _("Team"))]


def single(url, placeholder, **kwargs):
    """Configure a control that holds one value and can be cleared."""
    return TomSelectConfig(
        url=url,
        value_field="value",
        label_field="label",
        placeholder=placeholder,
        minimum_query_length=0,
        plugin_clear_button=PluginClearButton(),
        **kwargs,
    )


def multiple(url, placeholder, **kwargs):
    """Configure a control that holds several values, each with a remove button."""
    return TomSelectConfig(
        url=url,
        value_field="value",
        label_field="label",
        placeholder=placeholder,
        minimum_query_length=0,
        plugin_remove_button=PluginRemoveButton(),
        **kwargs,
    )


class TagsField(TomSelectMultipleChoiceField):
    """A multiple field that keeps a value typed in, which the list never held."""

    def clean(self, value):
        """Accept every value, since a tag can be new."""
        if self.required and not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )
        return list(value or [])


def country_field(**kwargs):
    """Build the single control."""
    return TomSelectChoiceField(
        label=_("Country"),
        config=single("ac-countries", _("Search for a country")),
        **kwargs,
    )


def languages_field(**kwargs):
    """Build the multiple control."""
    return TomSelectMultipleChoiceField(
        label=_("Languages"),
        config=multiple("ac-languages", _("Add a language")),
        **kwargs,
    )


def keywords_field(**kwargs):
    """Build the tagging control."""
    return TagsField(
        label=_("Keywords"),
        config=multiple("ac-keywords", _("Add a keyword"), create=True),
        **kwargs,
    )


def rock_field(**kwargs):
    """Build the grouped control."""
    return TomSelectChoiceField(
        label=_("Rock"),
        config=single("ac-rocks", _("Search for a rock")),
        **kwargs,
    )


class TomSelectForm(forms.Form):
    """Every control beside a stock select and a text input, which can be posted."""

    name = forms.CharField(label=_("Name"), required=False)
    plan = forms.ChoiceField(label=_("Plan"), choices=PLANS, required=False)
    country = country_field(help_text=_("One value, fetched as you type."))
    languages = languages_field(
        required=False, help_text=_("Several values, each with a remove button.")
    )
    keywords = keywords_field(
        required=False,
        help_text=_("Tagging: type a keyword that is not listed to add it."),
    )
    rock = rock_field(
        required=False, help_text=_("Options listed under the group each names.")
    )

    def __init__(self, *args, **kwargs):
        """Build the helper and a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.include_media = False
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class TomSelectStateForm(ChosenForm):
    """A single and a tagging control, in one state.

    Args:
        state: ``"filled"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with nothing posted, so the required fields fail.
    """

    plan = forms.ChoiceField(label=_("Plan (a stock select)"), choices=PLANS)
    country = country_field()
    keywords = keywords_field()

    def __init__(self, *args, state, **kwargs):
        """Put the fields in their state."""
        if state == "error":
            args = args or ({},)
        super().__init__(*args, **kwargs)
        self.helper.include_media = False
        if state in ("filled", "disabled"):
            self.initial.update(
                plan="team", country="Germany", keywords=["petrology", "tectonics"]
            )
        for field in self.fields.values():
            field.disabled = state == "disabled"


class TomSelectTrioForm(ChosenForm):
    """A stock select, a single control and a tagging control under one statement.

    Args:
        size: The size the form states, or None.
        color: The colour the form states, or None.
        variant: The variant the form states, or None.
    """

    plan = forms.ChoiceField(label=_("Plan (a stock select)"), choices=PLANS)
    country = country_field(required=False)
    keywords = keywords_field(required=False)

    def __init__(self, *args, size=None, color=None, variant=None, **kwargs):
        """State the size, colour and variant for the form."""
        stated = {
            key: value
            for key, value in {"size": size, "color": color, "variant": variant}.items()
            if value
        }
        super().__init__(*args, choices=FormChoices(**stated), **kwargs)
        self.helper.include_media = False
        self.initial.update(country="Japan", keywords=["seismology", "volcanology"])


class TomSelectModalForm(forms.Form):
    """A form whose controls sit in a modal. The form must be given a prefix."""

    name = forms.CharField(label=_("Name"), required=False)
    country = country_field(required=False)
    rock = rock_field(required=False)
    keywords = keywords_field(required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.include_media = False
        self.helper.layout = Layout(
            "name",
            Modal(
                "country",
                "rock",
                "keywords",
                css_id=self.dialog_id,
                title=_("Where and what"),
                title_id=f"{self.prefix}-title",
            ),
        )
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the control that opens it."""
        return f"{self.prefix}-dialog"


class SampleForm(forms.Form):
    """One line of the table formset."""

    label = forms.CharField(label=_("Sample"), required=False)
    country = country_field(required=False)
    rock = rock_field(required=False)
    keywords = keywords_field(required=False)


SampleFormSet = formset_factory(SampleForm, extra=3)


class SampleTableHelper(FormHelper):
    """Draws the samples as a table, with no form element."""

    template = "daisyui/table_inline_formset.html"
    form_tag = False
    disable_csrf = True
    include_media = False


class FetchedForm(forms.Form):
    """The form htmx puts on the page after it has loaded."""

    country = country_field(required=False)
    keywords = keywords_field(required=False)

    def __init__(self, *args, **kwargs):
        """Draw the form with no form element."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = False
