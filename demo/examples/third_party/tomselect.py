"""django-tomselect's autocomplete fields, drawn by this package with nothing added."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_tomselect.app_settings import (
    PluginClearButton,
    PluginRemoveButton,
    TomSelectConfig,
)
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField


class TagsField(TomSelectMultipleChoiceField):
    """A multiple field that keeps a value typed in, which the list never held."""

    def clean(self, value):
        """Accept every value, since a tag can be new."""
        if self.required and not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )
        return list(value or [])


def single(url, placeholder):
    """Configure a control that holds one value and can be cleared."""
    return TomSelectConfig(
        url=url,
        value_field="value",
        label_field="label",
        placeholder=placeholder,
        minimum_query_length=0,
        plugin_clear_button=PluginClearButton(),
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


class ResearchForm(forms.Form):
    """One value, several values, tags that can be new, and grouped options."""

    country = TomSelectChoiceField(
        config=single("ac-countries", "Search for a country"),
        help_text="One value, fetched as you type.",
    )
    languages = TomSelectMultipleChoiceField(
        config=multiple("ac-languages", "Add a language"),
        help_text="Several values, each with a remove button.",
        required=False,
    )
    keywords = TagsField(
        config=multiple("ac-keywords", "Add a keyword", create=True),
        help_text="Type a keyword that is not listed to add it.",
        required=False,
    )
    rock = TomSelectChoiceField(
        config=single("ac-rocks", "Search for a rock"),
        help_text="Options are listed under the group each one names.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.include_media = False
        self.helper.add_input(Submit("submit", "Save"))
