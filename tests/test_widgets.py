"""The mask widgets and the blocks a pattern names, as the form writes them."""

import json
import re
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.utils import translation

from mvp_forms.widgets import (
    EnumBlock,
    NumberMaskInput,
    PatternBlock,
    PatternMaskInput,
    RangeBlock,
    RegexMaskInput,
)


def input_of(widget, value=None):
    """Return the input the widget draws."""
    return BeautifulSoup(widget.render("field", value), "html.parser").input


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


class TestRegexMaskInput:
    def test_an_expression_alone_writes_its_kind_and_the_source(self):
        assert written(RegexMaskInput(r"^\d{0,8}$")) == {
            "kind": "regex",
            "mask": r"^\d{0,8}$",
        }

    def test_the_flags_are_written_beside_the_source(self):
        assert written(RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i")) == {
            "kind": "regex",
            "mask": "^#[0-9a-f]{0,6}$",
            "flags": "i",
        }

    @pytest.mark.parametrize("flags", ["dgimsuy", "v", ""])
    def test_each_flag_javascript_has_is_accepted(self, flags):
        assert written(RegexMaskInput("^a*$", flags=flags))["flags"] == flags

    @pytest.mark.parametrize(
        ("regex", "option"),
        [
            pytest.param({"mask": ""}, "mask", id="empty expression"),
            pytest.param({"mask": 5}, "mask", id="expression that is not text"),
            pytest.param(
                {"mask": re.compile("^a*$")}, "mask", id="compiled python pattern"
            ),
            pytest.param({"mask": "^a*$", "flags": "x"}, "flags", id="unknown flag"),
            pytest.param({"mask": "^a*$", "flags": "iL"}, "flags", id="one in two"),
            pytest.param({"mask": "^a*$", "flags": 5}, "flags", id="flags a number"),
        ],
    )
    def test_a_value_that_cannot_be_right_is_refused_naming_the_option(
        self, regex, option
    ):
        with pytest.raises(ValueError, match=option):
            RegexMaskInput(**regex)

    def test_an_expression_python_would_refuse_is_written_unchanged(self):
        source = r"^(?<letter>\p{L})*$"

        assert written(RegexMaskInput(source, flags="u"))["mask"] == source

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="lazy"):
            RegexMaskInput("^a*$", lazy=False)

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(RegexMaskInput("^a*$").media)

    def test_the_developers_attrs_are_kept(self):
        widget = RegexMaskInput("^a*$", attrs={"placeholder": "name"})

        drawn = BeautifulSoup(widget.render("field", None), "html.parser").input

        assert drawn["placeholder"] == "name"
        assert drawn["type"] == "text"

    def test_what_a_form_posts_reaches_the_field_as_it_was_typed(self):
        widget = RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i")

        assert widget.value_from_datadict({"colour": "#A0b"}, {}, "colour") == "#A0b"


class TestNumberMaskInput:
    def test_a_number_alone_writes_only_its_kind(self):
        assert written(NumberMaskInput()) == {"kind": "number"}

    @pytest.mark.parametrize(
        ("stated", "name", "value"),
        [
            ({"scale": 0}, "scale", 0),
            ({"scale": 3}, "scale", 3),
            ({"thousands_separator": " "}, "thousandsSeparator", " "),
            ({"thousands_separator": ""}, "thousandsSeparator", ""),
            ({"radix": "."}, "radix", "."),
            ({"map_to_radix": [",", "."]}, "mapToRadix", [",", "."]),
            ({"pad_fractional_zeros": True}, "padFractionalZeros", True),
            ({"normalize_zeros": False}, "normalizeZeros", False),
            ({"autofix": True}, "autofix", True),
        ],
    )
    def test_a_stated_option_is_written_under_imasks_name_and_nothing_else(
        self, stated, name, value
    ):
        assert written(NumberMaskInput(**stated)) == {"kind": "number", name: value}

    @pytest.mark.parametrize(
        "bound", [5, -2.5, Decimal("10"), Decimal("0.25"), 0], ids=repr
    )
    @pytest.mark.parametrize("option", ["min_value", "max_value"])
    def test_a_bound_is_written_as_a_json_number_under_imasks_name(self, option, bound):
        name = option.removesuffix("_value")

        options = written(NumberMaskInput(**{option: bound}))

        assert options == {"kind": "number", name: float(bound)}
        assert type(options[name]) in (int, float)

    def test_every_option_is_written_at_once(self):
        widget = NumberMaskInput(
            scale=2,
            thousands_separator=".",
            radix=",",
            map_to_radix=["."],
            pad_fractional_zeros=True,
            normalize_zeros=False,
            min_value=0,
            max_value=Decimal("99.5"),
            autofix=True,
        )

        assert written(widget) == {
            "kind": "number",
            "scale": 2,
            "thousandsSeparator": ".",
            "radix": ",",
            "mapToRadix": ["."],
            "padFractionalZeros": True,
            "normalizeZeros": False,
            "min": 0,
            "max": 99.5,
            "autofix": True,
        }

    @pytest.mark.parametrize(
        ("number", "option"),
        [
            pytest.param({"scale": -1}, "scale", id="negative scale"),
            pytest.param({"scale": "2"}, "scale", id="scale not a number"),
            pytest.param({"scale": 1.5}, "scale", id="scale not whole"),
            pytest.param(
                {"thousands_separator": "  "}, "thousands_separator", id="two spaces"
            ),
            pytest.param({"thousands_separator": 5}, "thousands_separator", id="digit"),
            pytest.param({"radix": ",,"}, "radix", id="radix of two characters"),
            pytest.param({"radix": ""}, "radix", id="radix of none"),
            pytest.param(
                {"thousands_separator": ","},
                "thousands_separator",
                id="separator is the default decimal mark",
            ),
            pytest.param(
                {"thousands_separator": ".", "radix": "."},
                "thousands_separator",
                id="separator is the stated decimal mark",
            ),
            pytest.param({"min_value": "5"}, "min_value", id="bound as text"),
            pytest.param({"max_value": "5"}, "max_value", id="upper bound as text"),
            pytest.param({"min_value": True}, "min_value", id="bound a boolean"),
            pytest.param({"max_value": float("nan")}, "max_value", id="not a number"),
            pytest.param({"max_value": float("inf")}, "max_value", id="infinite"),
            pytest.param(
                {"min_value": 10, "max_value": 5}, "min_value", id="bounds reversed"
            ),
            pytest.param(
                {"min_value": Decimal("1.5"), "max_value": 1},
                "min_value",
                id="decimal bound above the other",
            ),
        ],
    )
    def test_a_value_that_cannot_be_right_is_refused_naming_the_option(
        self, number, option
    ):
        with pytest.raises(ValueError, match=option):
            NumberMaskInput(**number)

    @pytest.mark.parametrize(
        "number",
        [
            {"thousands_separator": "."},
            {"thousands_separator": ",", "radix": "."},
            {"thousands_separator": ""},
            {"min_value": 5, "max_value": 5},
        ],
    )
    def test_a_value_that_can_be_right_is_accepted(self, number):
        NumberMaskInput(**number)

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="mask"):
            NumberMaskInput(mask="000")

    def test_imasks_own_names_for_a_bound_are_not_options(self):
        with pytest.raises(TypeError, match="min"):
            NumberMaskInput(min=0)

    def test_it_asks_a_touch_device_for_a_decimal_keypad(self):
        assert input_of(NumberMaskInput(scale=2))["inputmode"] == "decimal"
        assert input_of(NumberMaskInput())["inputmode"] == "decimal"

    def test_it_asks_for_a_numeric_keypad_where_there_are_no_decimal_places(self):
        assert input_of(NumberMaskInput(scale=0))["inputmode"] == "numeric"

    def test_an_inputmode_the_developer_states_is_kept(self):
        widget = NumberMaskInput(scale=0, attrs={"inputmode": "tel"})

        assert input_of(widget)["inputmode"] == "tel"

    def test_it_stays_a_text_input_with_the_developers_attrs(self):
        html = input_of(NumberMaskInput(attrs={"placeholder": "0,00"}))

        assert html["type"] == "text"
        assert html["placeholder"] == "0,00"

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(NumberMaskInput().media)


class TestWhatTheNumberFieldReceives:
    @pytest.mark.parametrize(
        ("options", "typed", "number"),
        [
            pytest.param(
                {"thousands_separator": " ", "radix": ","},
                "1 234 567,5",
                Decimal("1234567.5"),
                id="space and comma",
            ),
            pytest.param(
                {"thousands_separator": ".", "radix": ","},
                "1.234.567,5",
                Decimal("1234567.5"),
                id="full stop and comma",
            ),
            pytest.param(
                {"thousands_separator": ",", "radix": "."},
                "1,234,567.5",
                Decimal("1234567.5"),
                id="comma and full stop",
            ),
            pytest.param(
                {"thousands_separator": "'", "radix": "."},
                "1'234'567.5",
                Decimal("1234567.5"),
                id="apostrophe and full stop",
            ),
            pytest.param({}, "1234567,5", Decimal("1234567.5"), id="imasks defaults"),
            pytest.param(
                {"thousands_separator": " ", "radix": ","},
                "-1 234,5",
                Decimal("-1234.5"),
                id="negative",
            ),
            pytest.param(
                {"thousands_separator": " ", "radix": ","},
                "1 234",
                Decimal("1234"),
                id="no decimal places",
            ),
        ],
    )
    def test_a_decimal_field_receives_the_plain_number(self, options, typed, number):
        field = forms.DecimalField(widget=NumberMaskInput(**options))

        received = field.widget.value_from_datadict({"n": typed}, {}, "n")

        assert field.clean(received) == number

    def test_an_integer_field_receives_the_plain_number(self):
        field = forms.IntegerField(
            widget=NumberMaskInput(scale=0, thousands_separator=" ", radix=",")
        )

        received = field.widget.value_from_datadict({"n": "-12 345"}, {}, "n")

        assert field.clean(received) == -12345

    @pytest.mark.parametrize("typed", ["", None])
    def test_an_empty_value_stays_empty(self, typed):
        widget = NumberMaskInput(thousands_separator=" ", radix=",")

        received = widget.value_from_datadict({"n": typed}, {}, "n")

        assert received == typed

    def test_a_field_that_is_not_there_is_not_there(self):
        widget = NumberMaskInput(thousands_separator=" ", radix=",")

        assert widget.value_from_datadict({}, {}, "n") is None

    def test_a_number_that_is_not_text_is_left_as_it_was(self):
        widget = NumberMaskInput(thousands_separator=" ", radix=",")

        assert widget.value_from_datadict({"n": 5}, {}, "n") == 5

    def test_a_full_stop_typed_where_the_separator_is_a_full_stop_is_dropped(self):
        widget = NumberMaskInput(thousands_separator=".", radix=",")

        assert widget.value_from_datadict({"n": "1234.56"}, {}, "n") == "123456"


class TestHowTheNumberFieldIsDrawn:
    @pytest.mark.parametrize(
        ("options", "value", "shown"),
        [
            pytest.param({"radix": ","}, Decimal("1234.5"), "1234,5", id="decimal"),
            pytest.param({"radix": ","}, "1234.5", "1234,5", id="text"),
            pytest.param({"radix": ","}, 1234.5, "1234,5", id="float"),
            pytest.param({"radix": ","}, 1234, "1234", id="int"),
            pytest.param({}, Decimal("1234.5"), "1234,5", id="imasks default mark"),
            pytest.param({"radix": "."}, Decimal("1234.5"), "1234.5", id="full stop"),
            pytest.param(
                {"radix": ",", "thousands_separator": "."},
                Decimal("1234567.5"),
                "1234567,5",
                id="separator stated and not written",
            ),
            pytest.param({"radix": ","}, Decimal("1E+3"), "1000", id="exponent"),
            pytest.param({"radix": ","}, Decimal("-0.50"), "-0,50", id="negative"),
        ],
    )
    @pytest.mark.parametrize("localised", [False, True], ids=["plain", "localised"])
    def test_a_value_is_written_with_the_decimal_mark_and_no_separator(
        self, options, value, shown, localised
    ):
        widget = NumberMaskInput(**options)
        widget.is_localized = localised

        with translation.override("de"):
            html = input_of(widget, value)

        assert html["value"] == shown

    @pytest.mark.parametrize("value", [None, ""])
    def test_an_empty_value_writes_no_value(self, value):
        html = input_of(NumberMaskInput(radix=","), value)

        assert "value" not in html.attrs

    @pytest.mark.parametrize(
        "options",
        [
            {"thousands_separator": " ", "radix": ","},
            {"thousands_separator": ".", "radix": ","},
            {"thousands_separator": ",", "radix": "."},
            {},
        ],
    )
    def test_what_is_drawn_reaches_the_field_as_the_same_number_without_imask(
        self, options
    ):
        field = forms.DecimalField(widget=NumberMaskInput(**options))
        html = input_of(field.widget, Decimal("1234.5"))

        received = field.widget.value_from_datadict({"n": html["value"]}, {}, "n")

        assert field.clean(received) == Decimal("1234.5")
