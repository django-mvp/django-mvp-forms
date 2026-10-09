"""The mask widgets and the blocks a pattern names, as the form writes them."""

import json

import pytest
from bs4 import BeautifulSoup

from mvp_forms.widgets import EnumBlock, PatternBlock, PatternMaskInput, RangeBlock


def written(widget, value=None):
    """Return the options the widget writes on the input it draws."""
    drawn = BeautifulSoup(widget.render("field", value), "html.parser")
    return json.loads(drawn.input["data-imask"])


class TestPatternMaskInput:
    def test_a_pattern_alone_writes_its_kind_and_the_pattern(self):
        assert written(PatternMaskInput("000-000")) == {
            "kind": "pattern",
            "mask": "000-000",
        }

    @pytest.mark.parametrize(
        ("stated", "name", "value"),
        [
            ({"lazy": False}, "lazy", False),
            ({"placeholder_char": "#"}, "placeholderChar", "#"),
            ({"overwrite": True}, "overwrite", True),
            ({"overwrite": "shift"}, "overwrite", "shift"),
            ({"eager": True}, "eager", True),
            ({"eager": "remove"}, "eager", "remove"),
            ({"display_char": "•"}, "displayChar", "•"),
        ],
    )
    def test_a_stated_option_is_written_under_imasks_name_and_nothing_else(
        self, stated, name, value
    ):
        assert written(PatternMaskInput("0000", **stated)) == {
            "kind": "pattern",
            "mask": "0000",
            name: value,
        }

    def test_a_definition_is_written_as_its_expression(self):
        widget = PatternMaskInput("S-00", definitions={"S": "[1-6]"})

        assert written(widget)["definitions"] == {"S": "[1-6]"}

    def test_a_placeholder_character_for_each_definition_is_written_on_it(self):
        widget = PatternMaskInput(
            "S-00", definitions={"S": "[1-6]"}, placeholder_char={"S": "s", "0": "#"}
        )

        written_options = written(widget)

        assert "placeholderChar" not in written_options
        assert written_options["definitions"] == {
            "S": {"mask": "[1-6]", "placeholderChar": "s"},
            "0": {"placeholderChar": "#"},
        }

    def test_a_built_in_definition_the_developer_redefined_keeps_the_expression(self):
        widget = PatternMaskInput(
            "00", definitions={"0": "[0-1]"}, placeholder_char={"0": "#"}
        )

        assert written(widget)["definitions"] == {
            "0": {"mask": "[0-1]", "placeholderChar": "#"}
        }

    def test_each_kind_of_block_is_written_under_its_name(self):
        widget = PatternMaskInput(
            "d-Q-L",
            blocks={
                "d": RangeBlock(
                    1, 31, max_length=2, autofix=True, placeholder_char="d"
                ),
                "Q": EnumBlock(["HD", "TV"], placeholder_char="q"),
                "L": PatternBlock("aa", repeat=2, placeholder_char="a"),
            },
        )

        assert written(widget)["blocks"] == {
            "d": {
                "kind": "range",
                "from": 1,
                "to": 31,
                "maxLength": 2,
                "autofix": True,
                "placeholderChar": "d",
            },
            "Q": {"kind": "enum", "enum": ["HD", "TV"], "placeholderChar": "q"},
            "L": {"kind": "pattern", "mask": "aa", "repeat": 2, "placeholderChar": "a"},
        }

    def test_a_block_writes_only_the_options_stated(self):
        widget = PatternMaskInput(
            "dQL",
            blocks={
                "d": RangeBlock(1, 31),
                "Q": EnumBlock(["HD"]),
                "L": PatternBlock("aa"),
            },
        )

        assert written(widget)["blocks"] == {
            "d": {"kind": "range", "from": 1, "to": 31},
            "Q": {"kind": "enum", "enum": ["HD"]},
            "L": {"kind": "pattern", "mask": "aa"},
        }

    @pytest.mark.parametrize(
        ("pattern", "option"),
        [
            pytest.param({"mask": ""}, "mask", id="empty pattern"),
            pytest.param({"mask": 5}, "mask", id="pattern that is not text"),
            pytest.param(
                {"definitions": {"ab": "[0-9]"}},
                "definitions",
                id="definition of two characters",
            ),
            pytest.param(
                {"definitions": {"S": 5}}, "definitions", id="definition not text"
            ),
            pytest.param({"placeholder_char": "ab"}, "placeholder_char", id="two"),
            pytest.param({"placeholder_char": ""}, "placeholder_char", id="none"),
            pytest.param({"placeholder_char": 5}, "placeholder_char", id="number"),
            pytest.param(
                {"placeholder_char": {"S": "#"}},
                "placeholder_char",
                id="mapping from a character no definition has",
            ),
            pytest.param(
                {"placeholder_char": {"0": "##"}},
                "placeholder_char",
                id="mapping to two characters",
            ),
            pytest.param({"display_char": "ab"}, "display_char", id="display two"),
            pytest.param({"display_char": ""}, "display_char", id="display none"),
            pytest.param(
                {"blocks": {"d": {"kind": "range", "from": 1, "to": 31}}},
                "blocks",
                id="block that is a dictionary",
            ),
            pytest.param({"blocks": [RangeBlock(1, 2)]}, "blocks", id="not a mapping"),
            pytest.param({"overwrite": "yes"}, "overwrite", id="overwrite"),
            pytest.param({"eager": "yes"}, "eager", id="eager"),
        ],
    )
    def test_a_value_that_cannot_be_right_is_refused_naming_the_option(
        self, pattern, option
    ):
        with pytest.raises(ValueError, match=option):
            PatternMaskInput(**{"mask": "0000", **pattern})

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="scale"):
            PatternMaskInput("0000", scale=2)

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(PatternMaskInput("0000").media)

    def test_the_developers_attrs_are_kept(self):
        widget = PatternMaskInput("0000", attrs={"class": "wide", "placeholder": "pin"})

        drawn = BeautifulSoup(widget.render("field", None), "html.parser").input

        assert drawn["class"] == ["wide"]
        assert drawn["placeholder"] == "pin"
        assert drawn["type"] == "text"

    def test_a_pattern_holding_a_quote_or_an_angle_bracket_stays_in_its_attribute(
        self,
    ):
        pattern = 'a"b<script>c</script>d&e'

        html = PatternMaskInput(pattern).render("field", None)

        assert "<script>" not in html
        assert written(PatternMaskInput(pattern))["mask"] == pattern

    def test_a_value_is_drawn_unchanged(self):
        drawn = BeautifulSoup(
            PatternMaskInput("0000").render("field", "12"), "html.parser"
        ).input

        assert drawn["value"] == "12"

    def test_what_a_form_posts_reaches_the_field_as_it_was_typed(self):
        widget = PatternMaskInput("+{49} 000")

        assert (
            widget.value_from_datadict({"phone": "+49 123"}, {}, "phone") == "+49 123"
        )


class TestRangeBlock:
    def test_a_lower_bound_above_the_upper_is_refused_naming_it(self):
        with pytest.raises(ValueError, match="minimum"):
            RangeBlock(31, 1)

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="repeat"):
            RangeBlock(1, 31, repeat=2)

    def test_a_placeholder_character_of_two_characters_is_refused_naming_it(self):
        with pytest.raises(ValueError, match="placeholder_char"):
            RangeBlock(1, 31, placeholder_char="dd")


class TestEnumBlock:
    def test_an_empty_list_is_refused_naming_the_option(self):
        with pytest.raises(ValueError, match="values"):
            EnumBlock([])

    def test_a_placeholder_character_of_two_characters_is_refused_naming_it(self):
        with pytest.raises(ValueError, match="placeholder_char"):
            EnumBlock(["HD"], placeholder_char="hh")


class TestPatternBlock:
    @pytest.mark.parametrize("mask", ["", 5])
    def test_a_pattern_that_is_empty_or_not_text_is_refused_naming_it(self, mask):
        with pytest.raises(ValueError, match="mask"):
            PatternBlock(mask)

    def test_a_placeholder_character_of_two_characters_is_refused_naming_it(self):
        with pytest.raises(ValueError, match="placeholder_char"):
            PatternBlock("aa", placeholder_char="aa")
