"""The country widgets, the autocomplete view and the configuration of the module."""

import importlib
import json
import sys

import pytest
from bs4 import BeautifulSoup
from django import forms
from django_countries.fields import Country, CountryField

import mvp_forms
from mvp_forms import countries as countries_module
from mvp_forms.countries import CountrySelect, CountrySelectMultiple
from mvp_forms.widgets import TomSelect, TomSelectMultiple

WIDGETS = [CountrySelect, CountrySelectMultiple]


def draw(widget, value=None, field=None):
    """Return the select the widget draws for a country field."""
    field = field or CountryField(multiple=widget.allow_multiple_selected).formfield()
    widget.choices = field.choices
    html = widget.render("country", value)
    return BeautifulSoup(html, "html.parser").select_one("select")


def options_of(select):
    """Return the values of the options the select holds, groups included."""
    return [option["value"] for option in select.find_all("option")]


class TestCountrySelect:
    def test_it_is_a_tom_select(self):
        assert issubclass(CountrySelect, TomSelect)
        assert issubclass(CountrySelectMultiple, TomSelectMultiple)

    @pytest.mark.parametrize("widget", WIDGETS)
    def test_every_country_of_the_field_is_an_option(self, widget):
        field = CountryField(multiple=widget.allow_multiple_selected).formfield()

        select = draw(widget(), field=field)

        assert options_of(select) == [value for value, _name in field.choices]

    @pytest.mark.parametrize("widget", WIDGETS)
    def test_each_option_carries_the_address_of_its_countrys_flag(self, widget):
        select = draw(widget())

        flags = {
            option["value"]: option["data-flag"]
            for option in select.find_all("option")
            if option["value"]
        }

        assert len(flags) == 249
        assert flags["NZ"] == Country(code="NZ").flag

    def test_the_empty_choice_carries_no_flag(self):
        select = draw(CountrySelect(), field=CountryField(blank=True).formfield())

        empty = select.find("option", value="")

        assert not empty.has_attr("data-flag")

    @pytest.mark.parametrize("widget", WIDGETS)
    def test_it_states_a_template_for_an_option_and_a_chosen_value(self, widget):
        select = draw(widget())

        render = json.loads(select["data-tom-select"])["render"]

        assert set(render) == {"option", "item"}
        for template in render.values():
            assert "${data.flag}" in template
            assert "${data.text}" in template

    def test_a_value_is_shown_as_chosen(self):
        select = draw(CountrySelect(), "NZ")

        assert [o["value"] for o in select.find_all("option", selected=True)] == ["NZ"]

    def test_several_values_are_shown_as_chosen(self):
        select = draw(CountrySelectMultiple(), ["NZ", "DE"])

        chosen = [o["value"] for o in select.find_all("option", selected=True)]

        assert chosen == ["DE", "NZ"]

    def test_the_media_is_the_tom_select_media(self):
        assert CountrySelect().media._js == TomSelect().media._js
        assert CountrySelectMultiple().media._css == TomSelectMultiple().media._css


class TestTheEmptyChoice:
    def test_a_single_control_starts_on_an_empty_option_when_the_field_has_none(self):
        field = CountryField(default="NZ").formfield()

        select = draw(CountrySelect(), field=field)

        assert field.choices[0][0] != ""
        assert options_of(select)[0] == ""
        assert options_of(select).count("") == 1
        assert [o["value"] for o in select.find_all("option", selected=True)] == [""]

    def test_a_blank_choice_the_field_gives_is_not_drawn_twice(self):
        field = CountryField(blank=True).formfield()

        select = draw(CountrySelect(), field=field)

        assert options_of(select).count("") == 1

    def test_a_multiple_control_is_given_no_empty_option(self):
        select = draw(CountrySelectMultiple())

        assert "" not in options_of(select)

    def test_a_required_field_is_drawn_required(self):
        class Form(forms.Form):
            country = CountryField(default="NZ").formfield(widget=CountrySelect())

        select = BeautifulSoup(str(Form()["country"]), "html.parser").select_one(
            "select"
        )

        assert select.has_attr("required")


class TestTheSettingsAreTomSelects:
    def test_each_setting_reaches_the_control(self):
        select = draw(
            CountrySelectMultiple(
                placeholder="Add a country",
                clear_button=True,
                remove_button=True,
                max_items=3,
            )
        )

        settings = json.loads(select["data-tom-select"])

        assert settings["placeholder"] == "Add a country"
        assert settings["plugins"] == ["clear_button", "remove_button"]
        assert settings["maxItems"] == 3

    def test_a_counted_control_carries_what_tom_select_gives_it(self):
        select = draw(CountrySelectMultiple(counted=True))

        settings = json.loads(select["data-tom-select"])

        assert settings["plugins"] == ["checkbox_options", "dropdown_input"]
        assert select.has_attr("data-none-text")

    @pytest.mark.parametrize(
        ("widget", "parent", "options"),
        [
            (CountrySelect, TomSelect, {"placeholder": 3}),
            (CountrySelect, TomSelect, {"clear_button": "yes"}),
            (CountrySelectMultiple, TomSelectMultiple, {"max_items": 0}),
            (CountrySelectMultiple, TomSelectMultiple, {"max_items": "2"}),
            (
                CountrySelectMultiple,
                TomSelectMultiple,
                {"counted": True, "remove_button": True},
            ),
        ],
    )
    def test_a_setting_that_cannot_be_right_is_refused_as_tom_select_refuses_it(
        self, widget, parent, options
    ):
        with pytest.raises(ValueError) as refused_parent:
            parent(**options)

        with pytest.raises(ValueError) as refused:
            widget(**options)

        assert str(refused.value) == str(refused_parent.value)


class TestTheFieldItDraws:
    def test_the_form_cleans_to_the_code_as_the_stock_field_does(self):
        class Form(forms.Form):
            country = CountryField().formfield(widget=CountrySelect())

        form = Form({"country": "NZ"})

        assert form.is_valid()
        assert form.cleaned_data["country"] == "NZ"

    def test_a_multiple_form_cleans_to_the_list_of_codes(self):
        class Form(forms.Form):
            countries = CountryField(multiple=True).formfield(
                widget=CountrySelectMultiple()
            )

        form = Form({"countries": ["NZ", "DE"]})

        assert form.is_valid()
        assert form.cleaned_data["countries"] == ["NZ", "DE"]

    def test_a_code_django_countries_does_not_list_is_refused(self):
        class Form(forms.Form):
            country = CountryField().formfield(widget=CountrySelect())

        form = Form({"country": "XX"})

        assert form.errors["country"][0].startswith("Select a valid choice")


class TestWithoutDjangoTomselect:
    def test_the_widgets_import_and_the_view_and_configuration_are_absent(
        self, monkeypatch
    ):
        monkeypatch.setattr(mvp_forms, "countries", countries_module)
        monkeypatch.delitem(sys.modules, "mvp_forms.countries")
        monkeypatch.setitem(sys.modules, "django_tomselect", None)
        monkeypatch.setitem(sys.modules, "django_tomselect.app_settings", None)
        monkeypatch.setitem(sys.modules, "django_tomselect.autocompletes", None)

        module = importlib.import_module("mvp_forms.countries")

        assert hasattr(module, "CountrySelect")
        assert not hasattr(module, "CountryAutocomplete")
        assert not hasattr(module, "country_config")
