"""The country widgets, the autocomplete view and the configuration of the module."""

import importlib
import json
import re
import sys

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.test import RequestFactory, override_settings
from django_countries import Countries, countries
from django_countries.fields import Country, CountryField
from django_tomselect.app_settings import TomSelectConfig
from django_tomselect.forms import TomSelectChoiceField, TomSelectMultipleChoiceField

import mvp_forms
from mvp_forms import countries as countries_module
from mvp_forms.countries import (
    FLAGGED,
    CountryAutocomplete,
    CountrySelect,
    CountrySelectMultiple,
    country_config,
    grouped_at_break,
)
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
        assert json.loads(select["data-tom-select"])["lockOptgroupOrder"] is True
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
        assert CountrySelect().media.render_js() == TomSelect().media.render_js()
        assert (
            CountrySelectMultiple().media.render_css()
            == TomSelectMultiple().media.render_css()
        )


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

        assert form.has_error("country", "invalid_choice")


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


def ask(view=CountryAutocomplete, **query):
    """Return the JSON the autocomplete view answers to a request."""
    request = RequestFactory().get("/countries/", query)
    response = view.as_view()(request)
    assert response.status_code == 200
    return json.loads(response.content)


class TestCountryAutocomplete:
    def test_it_answers_a_page_of_twenty_and_says_more_follow(self):
        answer = ask()

        assert len(answer["results"]) == 20
        assert answer["has_more"] is True
        assert answer["page"] == 1

    def test_a_later_page_continues_where_the_page_before_stopped(self):
        every = []
        for page in range(1, 20):
            answer = ask(p=page)
            every.extend(result["value"] for result in answer["results"])
            if not answer["has_more"]:
                break

        assert every == [code for code, _name in countries]

    def test_each_result_holds_the_code_the_name_and_the_address_of_the_flag(self):
        answer = ask(q="zealand")

        assert answer["results"] == [
            {
                "value": "NZ",
                "label": "New Zealand",
                "flag": Country(code="NZ").flag,
            }
        ]

    @pytest.mark.parametrize("text", ["zeal", "ZEAL", "nz", "Nz"])
    def test_a_search_matches_the_name_or_the_code_whatever_the_case(self, text):
        values = [result["value"] for result in ask(q=text)["results"]]

        assert "NZ" in values

    def test_a_search_matching_nothing_answers_no_result(self):
        answer = ask(q="qqqq")

        assert answer["results"] == []
        assert answer["has_more"] is False

    def test_the_results_keep_the_order_of_django_countries(self):
        values = [result["value"] for result in ask()["results"]]

        assert values == [code for code, _name in list(countries)[:20]]

    def test_the_flag_follows_the_countries_it_answers_from(self):
        class Custom(Countries):
            override = {"NZ": {"name": "New Zealand", "flag_url": "custom/{code}.png"}}

        class Answering(CountryAutocomplete):
            countries = Custom()

        results = ask(Answering, q="zealand")["results"]

        assert results[0]["flag"] == Country(code="NZ", custom_countries=Custom()).flag
        assert results[0]["flag"].endswith("custom/nz.png")


class TestCountryConfig:
    def test_it_is_a_django_tomselect_configuration_for_the_url(self):
        config = country_config("ac-countries")

        assert isinstance(config, TomSelectConfig)
        assert config.url == "ac-countries"
        assert config.value_field == "value"
        assert config.label_field == "label"

    def test_a_search_starts_with_no_typing_unless_the_project_says_otherwise(self):
        assert country_config("ac").minimum_query_length == 0
        assert country_config("ac", minimum_query_length=2).minimum_query_length == 2

    def test_any_setting_of_the_configuration_passes_through(self):
        config = country_config("ac", placeholder="Pick one", max_items=4)

        assert config.placeholder == "Pick one"
        assert config.max_items == 4

    def test_the_templates_are_given_as_quoted_strings_and_attrs_are_kept(self):
        config = country_config("ac", attrs={"class": "mine"})

        assert config.attrs["class"] == "mine"
        assert json.loads(config.attrs["data_template_option"]) == FLAGGED % "label"
        assert json.loads(config.attrs["data_template_item"]) == FLAGGED % "label"

    def test_the_dictionary_of_attrs_a_project_passes_is_left_as_it_was(self):
        attrs = {"class": "mine"}

        country_config("ac", attrs=attrs)

        assert attrs == {"class": "mine"}

    def test_a_form_with_the_fields_it_configures_cleans_to_the_codes(self):
        class Form(forms.Form):
            one = TomSelectChoiceField(config=country_config("ac-flagged-countries"))
            several = TomSelectMultipleChoiceField(
                config=country_config("ac-flagged-countries")
            )

        form = Form({"one": "NZ", "several": ["NZ", "DE"]})

        assert form.is_valid()
        assert form.cleaned_data["one"] == "NZ"
        assert form.cleaned_data["several"] == ["NZ", "DE"]

    def test_the_templates_reach_the_script_as_django_tomselect_writes_it(self):
        """A canary: the day django-tomselect quotes a template itself, this fails."""
        field = TomSelectChoiceField(config=country_config("ac-flagged-countries"))
        script = str(field.widget.render("country", None))

        templates = re.findall(r"var template = (.*);", script)

        assert templates
        assert all(template == json.dumps(FLAGGED % "label") for template in templates)


class GermanSpeakingFirst(Countries):
    first = ["DE", "AT", "CH"]
    first_break = "Other"


class FirstWithoutBreak(Countries):
    first = ["DE", "AT"]


class FirstRepeated(Countries):
    first = ["DE", "AT"]
    first_repeat = True


class FirstRepeatedWithBreak(Countries):
    first = ["DE", "AT"]
    first_break = "Other"
    first_repeat = True


@pytest.fixture
def fresh_countries():
    """Clear django-countries' cache of its list before and after a test."""
    countries.__dict__.pop("countries", None)
    yield
    countries.__dict__.pop("countries", None)


def field_of(countries_class, widget):
    """Return the form field a CountryField of the countries gives the widget."""
    multiple = widget.allow_multiple_selected
    return CountryField(countries=countries_class, multiple=multiple).formfield()


def top_level(select):
    """Return the values of the options outside every group, in order."""
    return [child["value"] for child in select.find_all("option", recursive=False)]


def groups_of(select):
    """Return each option group of the select as its heading and its values."""
    return [
        (group["label"], [option["value"] for option in group.find_all("option")])
        for group in select.find_all("optgroup")
    ]


class TestCountriesFirstInTheWidgets:
    def test_the_countries_first_are_listed_ahead_of_all_the_others_outside_a_group(
        self,
    ):
        select = draw(
            CountrySelect(), field=field_of(GermanSpeakingFirst, CountrySelect)
        )

        assert top_level(select) == ["", "DE", "AT", "CH"]

    def test_every_other_country_is_in_one_group_headed_by_the_break(self):
        select = draw(
            CountrySelect(), field=field_of(GermanSpeakingFirst, CountrySelect)
        )

        [(heading, values)] = groups_of(select)

        assert heading == "Other"
        assert len(values) == 246
        assert "DE" not in values
        assert "NZ" in values

    def test_the_break_is_never_a_value_a_person_can_choose(self):
        select = draw(
            CountrySelect(), field=field_of(GermanSpeakingFirst, CountrySelect)
        )

        assert options_of(select).count("") == 1
        assert not any(option.text == "Other" for option in select.find_all("option"))

    def test_a_multiple_control_has_no_empty_option_and_the_same_groups(self):
        widget = CountrySelectMultiple
        select = draw(widget(), field=field_of(GermanSpeakingFirst, widget))

        assert top_level(select) == ["DE", "AT", "CH"]
        assert [heading for heading, _values in groups_of(select)] == ["Other"]

    def test_without_a_break_the_countries_first_sit_at_the_top_in_no_group(self):
        select = draw(CountrySelect(), field=field_of(FirstWithoutBreak, CountrySelect))

        assert top_level(select)[:3] == ["", "DE", "AT"]
        assert groups_of(select) == []
        assert options_of(select).count("DE") == 1

    @pytest.mark.parametrize("countries_class", [FirstRepeated, FirstRepeatedWithBreak])
    @pytest.mark.parametrize("widget", WIDGETS)
    def test_each_country_is_listed_once_whatever_first_repeat_says(
        self, countries_class, widget
    ):
        select = draw(widget(), field=field_of(countries_class, widget))

        values = [value for value in options_of(select) if value]

        assert len(values) == len(set(values)) == 249

    def test_a_value_chosen_among_the_countries_first_is_shown_chosen(self):
        select = draw(
            CountrySelect(), "AT", field=field_of(GermanSpeakingFirst, CountrySelect)
        )

        assert [o["value"] for o in select.find_all("option", selected=True)] == ["AT"]

    def test_the_stock_select_is_drawn_as_it_was(self):
        field = field_of(GermanSpeakingFirst, forms.Select)
        field.widget.choices = field.choices

        select = BeautifulSoup(
            field.widget.render("country", None), "html.parser"
        ).select_one("select")

        assert select.find("option", value="").text == "Other"
        assert select.find("optgroup") is None

    @pytest.mark.usefixtures("fresh_countries")
    @override_settings(COUNTRIES_FIRST=["NZ", "AU"], COUNTRIES_FIRST_BREAK="Rest")
    def test_django_countries_settings_take_effect_with_no_setting_of_the_packages(
        self,
    ):
        select = draw(CountrySelect(), field=CountryField().formfield())

        assert top_level(select) == ["", "NZ", "AU"]
        assert [heading for heading, _values in groups_of(select)] == ["Rest"]


class TestGroupedAtBreak:
    def test_choices_with_no_break_come_back_as_they_are(self):
        choices = [("DE", "Germany"), ("AT", "Austria")]

        assert grouped_at_break(choices) == choices

    def test_a_leading_empty_choice_is_not_a_break(self):
        choices = [("", "---"), ("DE", "Germany")]

        assert grouped_at_break(choices) == choices

    def test_a_country_listed_twice_is_kept_where_it_first_comes(self):
        choices = [("DE", "Germany"), ("AT", "Austria"), ("DE", "Germany")]

        assert grouped_at_break(choices) == choices[:2]


class TestCountriesFirstInTheView:
    def test_the_countries_first_come_first_with_no_group(self):
        class Answering(CountryAutocomplete):
            countries = GermanSpeakingFirst()

        results = ask(Answering)["results"]

        assert [result["value"] for result in results[:3]] == ["DE", "AT", "CH"]
        assert not any("optgroup" in result for result in results[:3])

    def test_every_other_result_names_the_break_as_its_group(self):
        class Answering(CountryAutocomplete):
            countries = GermanSpeakingFirst()

        results = ask(Answering, q="zealand")["results"]

        assert [result["optgroup"] for result in results] == ["Other"]

    def test_a_search_lists_the_matches_among_the_countries_first_above_the_rest(self):
        class Answering(CountryAutocomplete):
            countries = GermanSpeakingFirst()

        results = ask(Answering, q="a")["results"]
        groups = [result.get("optgroup") for result in results]

        assert groups.index("Other") > groups.index(None)
        assert groups == sorted(groups, key=lambda group: group is not None)

    def test_the_break_is_not_a_result(self):
        class Answering(CountryAutocomplete):
            countries = GermanSpeakingFirst()

        results = ask(Answering, q="other")["results"]

        assert all(result["value"] for result in results)

    @pytest.mark.parametrize("countries_class", [FirstRepeated, FirstRepeatedWithBreak])
    def test_each_country_is_answered_once_whatever_first_repeat_says(
        self, countries_class
    ):
        class Answering(CountryAutocomplete):
            countries = countries_class()

        values = []
        for page in range(1, 20):
            answer = ask(Answering, p=page)
            values.extend(result["value"] for result in answer["results"])
            if not answer["has_more"]:
                break

        assert len(values) == len(set(values)) == 249

    @pytest.mark.usefixtures("fresh_countries")
    @override_settings(COUNTRIES_FIRST=["NZ"], COUNTRIES_FIRST_BREAK="Rest")
    def test_django_countries_settings_take_effect_with_no_setting_of_the_packages(
        self,
    ):
        results = ask()["results"]

        assert results[0]["value"] == "NZ"
        assert results[1]["optgroup"] == "Rest"
