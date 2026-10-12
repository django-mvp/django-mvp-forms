"""The Tom Select widgets, drawn as the pack draws a select and through each renderer."""

import json
import re
from pathlib import Path

import pytest

from mvp_forms.choices import FormChoices
from tests.forms import (
    StockMultipleForm,
    StockSingleForm,
    TomSelectMultipleForm,
    TomSelectSettingsForm,
    TomSelectSettingsFormSet,
    TomSelectSingleForm,
)

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.fruit|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]
WHOLE_FORM = [*FORM_WIDE, SOURCES[3]]


README = Path(__file__).parents[2] / "README.md"


def selected_values(select):
    return [option["value"] for option in select.find_all("option", selected=True)]


def option_values(select):
    return [option["value"] for option in select.find_all("option")]


class TestTomSelectMultiple:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_attribute_is_drawn_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=TomSelectMultipleForm())

        drawn = soup.find(id="id_fruit")

        assert json.loads(drawn["data-tom-select"]) == {}

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_select_holds_every_choice_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=TomSelectMultipleForm())

        drawn = soup.find(id="id_fruit")

        assert drawn.has_attr("multiple")
        assert option_values(drawn) == ["a", "b"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_is_drawn_as_a_daisyui_select(self, draw, source):
        soup = draw(source, form=TomSelectMultipleForm())

        drawn = soup.find(id="id_fruit")

        assert drawn.name == "select"
        assert {"select", "w-full"} <= set(drawn["class"])

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "select-lg"),
            ("color", "primary", "select-primary"),
            ("variant", "ghost", "select-ghost"),
        ],
    )
    def test_it_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = TomSelectMultipleForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_fruit")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_a_field_in_error_is_marked_and_described_by_its_error(self, draw, source):
        soup = draw(source, form=TomSelectMultipleForm({}))

        drawn = soup.find(id="id_fruit")

        assert "select-error" in drawn["class"]
        assert drawn["aria-invalid"] == "true"
        assert "id_fruit_error" in drawn["aria-describedby"].split()

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_a_disabled_field_is_drawn_disabled(self, draw, source):
        soup = draw(source, form=TomSelectMultipleForm())

        assert soup.find(id="id_off").has_attr("disabled")

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_label_and_help_text_are_tied_to_the_select(self, draw, source):
        soup = draw(source, form=TomSelectMultipleForm())

        drawn = soup.find(id="id_fruit")

        assert soup.find("label", attrs={"for": "id_fruit"}) is not None
        described = drawn["aria-describedby"].split()
        assert "id_fruit_helptext" in described
        assert all(soup.find(id=name) is not None for name in described)

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_initial_and_submitted_values_are_drawn_as_chosen(self, draw, source):
        initial = draw(source, form=TomSelectMultipleForm(initial={"fruit": ["a"]}))
        submitted = draw(source, form=TomSelectMultipleForm({"fruit": ["a", "b"]}))

        assert selected_values(initial.find(id="id_fruit")) == ["a"]
        assert selected_values(submitted.find(id="id_fruit")) == ["a", "b"]

    @pytest.mark.parametrize("source", WHOLE_FORM)
    def test_the_developers_attrs_are_kept(self, draw, source):
        soup = draw(source, form=TomSelectMultipleForm())

        drawn = soup.find(id="id_own")

        assert drawn["data-role"] == "picker"
        assert "mine" in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_stock_select_is_beside_the_attribute(self, draw, source):
        tom = draw(source, form=TomSelectMultipleForm())
        stock = draw(source, form=StockMultipleForm())

        for each in tom.find_all("select", attrs={"data-tom-select": True}):
            del each["data-tom-select"]
        for each in tom.find_all("script"):
            each.decompose()

        def lines(soup):
            return [line for line in str(soup).splitlines() if line.strip()]

        assert lines(tom) == lines(stock)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_without_the_widgets_is_drawn_with_no_attribute(self, draw, source):
        soup = draw(source, form=StockMultipleForm())

        assert soup.find_all(attrs={"data-tom-select": True}) == []

    def test_the_form_media_names_the_script_once(self):
        assert TomSelectMultipleForm().media._js == ["mvp_forms/tomselect.js"]

    def test_the_media_of_a_form_without_the_widgets_names_no_script(self):
        assert StockMultipleForm().media._js == []


class TestTomSelect:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_attribute_is_drawn_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=TomSelectSingleForm())

        drawn = soup.find(id="id_fruit")

        assert json.loads(drawn["data-tom-select"]) == {}

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_select_holds_every_choice_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=TomSelectSingleForm())

        drawn = soup.find(id="id_fruit")

        assert not drawn.has_attr("multiple")
        assert option_values(drawn) == ["a", "b"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_is_drawn_as_a_daisyui_select(self, draw, source):
        soup = draw(source, form=TomSelectSingleForm())

        drawn = soup.find(id="id_fruit")

        assert drawn.name == "select"
        assert {"select", "w-full"} <= set(drawn["class"])

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "select-lg"),
            ("color", "primary", "select-primary"),
            ("variant", "ghost", "select-ghost"),
        ],
    )
    def test_it_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = TomSelectSingleForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_fruit")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_a_field_in_error_is_marked_and_described_by_its_error(self, draw, source):
        soup = draw(source, form=TomSelectSingleForm({}))

        drawn = soup.find(id="id_fruit")

        assert "select-error" in drawn["class"]
        assert drawn["aria-invalid"] == "true"
        assert "id_fruit_error" in drawn["aria-describedby"].split()

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_a_disabled_field_is_drawn_disabled(self, draw, source):
        soup = draw(source, form=TomSelectSingleForm())

        assert soup.find(id="id_off").has_attr("disabled")

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_label_and_help_text_are_tied_to_the_select(self, draw, source):
        soup = draw(source, form=TomSelectSingleForm())

        drawn = soup.find(id="id_fruit")

        assert soup.find("label", attrs={"for": "id_fruit"}) is not None
        described = drawn["aria-describedby"].split()
        assert "id_fruit_helptext" in described
        assert all(soup.find(id=name) is not None for name in described)

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_initial_and_submitted_values_are_drawn_as_chosen(self, draw, source):
        initial = draw(source, form=TomSelectSingleForm(initial={"fruit": "a"}))
        submitted = draw(source, form=TomSelectSingleForm({"fruit": "b"}))

        assert selected_values(initial.find(id="id_fruit")) == ["a"]
        assert selected_values(submitted.find(id="id_fruit")) == ["b"]

    @pytest.mark.parametrize("source", WHOLE_FORM)
    def test_the_developers_attrs_are_kept(self, draw, source):
        soup = draw(source, form=TomSelectSingleForm())

        drawn = soup.find(id="id_own")

        assert drawn["data-role"] == "picker"
        assert "mine" in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_stock_select_is_beside_the_attribute(self, draw, source):
        tom = draw(source, form=TomSelectSingleForm())
        stock = draw(source, form=StockSingleForm())

        for each in tom.find_all("select", attrs={"data-tom-select": True}):
            del each["data-tom-select"]
        for each in tom.find_all("script"):
            each.decompose()

        def lines(soup):
            return [line for line in str(soup).splitlines() if line.strip()]

        assert lines(tom) == lines(stock)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_without_the_widgets_is_drawn_with_no_attribute(self, draw, source):
        soup = draw(source, form=StockSingleForm())

        assert soup.find_all(attrs={"data-tom-select": True}) == []

    def test_the_form_media_names_the_script_once(self):
        assert TomSelectSingleForm().media._js == ["mvp_forms/tomselect.js"]

    def test_the_media_of_a_form_without_the_widgets_names_no_script(self):
        assert StockSingleForm().media._js == []

    def test_the_readmes_example_draws_a_single_select_beside_the_multiple_one(
        self, draw
    ):
        section = re.search(
            r"^### Tom Select widgets$(.*?)^### ", README.read_text(), re.M | re.S
        ).group(1)
        source = re.search(r"```python\n(.*?)```", section, re.S).group(1)
        names = {}

        exec(source, names)  # noqa: S102
        soup = draw("{{ form.as_div }}", form=names["ArticleForm"]())

        drawn = soup.find("select", id="id_section", attrs={"data-tom-select": True})
        assert drawn is not None
        assert not drawn.has_attr("multiple")


class TestTheSettings:
    TOPIC = {"placeholder": "Pick one", "plugins": ["clear_button"]}
    TOPICS = {
        "placeholder": "Pick some",
        "maxItems": 2,
        "plugins": ["clear_button", "remove_button"],
    }

    @pytest.mark.parametrize("source", [*SOURCES[:2], SOURCES[3]])
    def test_each_field_carries_its_settings_whichever_way_the_form_is_rendered(
        self, draw, source
    ):
        soup = draw(source, form=TomSelectSettingsForm())

        drawn = {
            name: json.loads(soup.find(id=f"id_{name}")["data-tom-select"])
            for name in ("topic", "topics")
        }

        assert drawn == {"topic": self.TOPIC, "topics": self.TOPICS}

    def test_a_field_is_drawn_with_its_settings_through_as_crispy_field(self, draw):
        form = TomSelectSettingsForm()

        soup = draw("{{ form.topics|as_crispy_field }}", form=form)

        drawn = json.loads(soup.find(id="id_topics")["data-tom-select"])
        assert drawn == self.TOPICS

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_carries_the_same_settings(self, draw, source):
        formset = TomSelectSettingsFormSet()

        row = draw(source, form=formset.forms[0])
        template = draw(source, form=formset.empty_form)

        def settings(soup, name):
            drawn = soup.find("select", id=re.compile(f"id_.*{name}$"))
            return json.loads(drawn["data-tom-select"])

        assert settings(template, "topics") == settings(row, "topics") == self.TOPICS
        assert settings(template, "topic") == settings(row, "topic") == self.TOPIC


class TestTheReadmesExample:
    def test_the_form_it_gives_draws_the_widgets_select(self, draw):
        section = re.search(
            r"^### Tom Select widgets$(.*?)^### ", README.read_text(), re.M | re.S
        ).group(1)
        source = re.search(r"```python\n(.*?)```", section, re.S).group(1)
        names = {}

        exec(source, names)  # noqa: S102
        soup = draw("{{ form.as_div }}", form=names["ArticleForm"]())

        drawn = soup.find("select", attrs={"data-tom-select": True})
        assert drawn is not None
        assert drawn.has_attr("multiple")


class TestTheReadmesGroupsExample:
    def test_the_form_it_gives_draws_groups_and_one_disabled_option(self, draw):
        section = re.search(
            r"^#### Groups and unavailable options$(.*?)^#",
            README.read_text(),
            re.M | re.S,
        ).group(1)
        source = re.search(r"```python\n(.*?)```", section, re.S).group(1)
        names = {}

        exec(source, names)  # noqa: S102
        soup = draw("{{ form.as_div }}", form=names["OfficesForm"]())

        drawn = soup.find("select", id="id_offices")
        assert [group["label"] for group in drawn.find_all("optgroup")] == [
            "Germany",
            "France",
        ]
        assert [o["value"] for o in drawn.find_all("option", disabled=True)] == ["lyon"]
