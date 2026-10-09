"""The mask widgets and the blocks a pattern names, as the form writes them."""

import datetime
import json
import re
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.utils import translation
from django.utils.dates import MONTHS

from mvp_forms.fields import PartialDateField
from mvp_forms.widgets import (
    DynamicMaskInput,
    EnumBlock,
    NumberMaskInput,
    PartialDateInput,
    PartialDateMaskInput,
    PartialDateSelect,
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

    @pytest.mark.parametrize(
        ("arguments", "option"),
        [
            pytest.param((None, 3), "minimum", id="no minimum"),
            pytest.param((1, "3"), "maximum", id="maximum as text"),
            pytest.param((Decimal(1), 3), "minimum", id="a Decimal"),
            pytest.param((True, 3), "minimum", id="a boolean"),
        ],
    )
    def test_a_bound_that_is_not_a_whole_number_is_refused_naming_it(
        self, arguments, option
    ):
        with pytest.raises(ValueError, match=option):
            RangeBlock(*arguments)

    def test_a_length_that_is_not_a_whole_number_is_refused_naming_it(self):
        with pytest.raises(ValueError, match="max_length"):
            RangeBlock(1, 31, max_length="2")


class TestEnumBlock:
    @pytest.mark.parametrize(
        "values",
        [pytest.param("HD", id="text"), pytest.param(["HD", 4], id="a number in it")],
    )
    def test_values_that_are_not_a_list_of_text_are_refused_naming_the_option(
        self, values
    ):
        with pytest.raises(ValueError, match="values"):
            EnumBlock(values)

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
            pytest.param({"map_to_radix": "."}, "map_to_radix", id="marks as text"),
            pytest.param(
                {"map_to_radix": ["..", ","]}, "map_to_radix", id="a mark of two"
            ),
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


class TestDynamicMaskInput:
    def test_each_masks_options_are_written_in_the_order_stated(self):
        widget = DynamicMaskInput(
            [PatternMaskInput("000-0000"), PatternMaskInput("(000) 000-0000")]
        )

        assert written(widget) == {
            "kind": "dynamic",
            "mask": [
                {"kind": "pattern", "mask": "000-0000"},
                {"kind": "pattern", "mask": "(000) 000-0000"},
            ],
        }

    def test_a_pattern_a_regular_expression_and_a_number_each_write_their_own(self):
        widget = DynamicMaskInput(
            [
                RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i"),
                NumberMaskInput(scale=0, max_value=999),
                PatternMaskInput(
                    "S-00", definitions={"S": "[1-6]"}, lazy=False, display_char="•"
                ),
            ]
        )

        assert written(widget)["mask"] == [
            {"kind": "regex", "mask": "^#[0-9a-f]{0,6}$", "flags": "i"},
            {"kind": "number", "scale": 0, "max": 999},
            {
                "kind": "pattern",
                "mask": "S-00",
                "definitions": {"S": "[1-6]"},
                "lazy": False,
                "displayChar": "•",
            },
        ]

    def test_a_tuple_of_masks_is_written_as_a_list(self):
        widget = DynamicMaskInput((PatternMaskInput("0"), PatternMaskInput("00")))

        assert written(widget)["mask"] == [
            {"kind": "pattern", "mask": "0"},
            {"kind": "pattern", "mask": "00"},
        ]

    @pytest.mark.parametrize(
        "masks",
        [
            pytest.param([], id="empty list"),
            pytest.param(PatternMaskInput("0"), id="a widget and not a list"),
            pytest.param("0000", id="text"),
            pytest.param(["0000"], id="a pattern as text"),
            pytest.param([RangeBlock(1, 2)], id="a block"),
            pytest.param([forms.TextInput()], id="a widget of Django's"),
            pytest.param(
                [PatternMaskInput("0"), DynamicMaskInput([PatternMaskInput("00")])],
                id="another list of masks",
            ),
            pytest.param([PatternMaskInput("0"), None], id="one that is not a widget"),
        ],
    )
    def test_a_list_that_cannot_be_right_is_refused_naming_the_option(self, masks):
        with pytest.raises(ValueError, match="masks"):
            DynamicMaskInput(masks)

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="lazy"):
            DynamicMaskInput([PatternMaskInput("0")], lazy=False)

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(
            DynamicMaskInput([PatternMaskInput("0")]).media
        )

    def test_the_developers_attrs_are_kept(self):
        widget = DynamicMaskInput(
            [PatternMaskInput("0")], attrs={"placeholder": "number"}
        )

        html = input_of(widget)

        assert html["placeholder"] == "number"
        assert html["type"] == "text"

    @pytest.mark.parametrize(
        "masks",
        [
            [PatternMaskInput("000-0000"), PatternMaskInput("(000) 000-0000")],
            [RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i")],
            [NumberMaskInput(thousands_separator=" ", radix=",")],
            [
                RegexMaskInput("^#[0-9a-f]{0,6}$", flags="i"),
                NumberMaskInput(scale=0, thousands_separator=".", radix=","),
            ],
        ],
        ids=["patterns", "regular expression", "number", "expression and number"],
    )
    def test_what_a_form_posts_reaches_the_field_as_it_was_typed(self, masks):
        widget = DynamicMaskInput(masks)

        received = widget.value_from_datadict({"n": "1 234,5"}, {}, "n")

        assert received == "1 234,5"

    def test_a_value_is_drawn_unchanged_whatever_the_masks_in_the_list(self):
        widget = DynamicMaskInput([NumberMaskInput(radix=",")])

        assert input_of(widget, "1234.5")["value"] == "1234.5"


class TestPartialDateMaskInput:
    def test_it_writes_its_kind_and_the_finest_precision_a_form_may_hold(self):
        assert written(PartialDateMaskInput()) == {
            "kind": "partial-date",
            "resolution": "day",
        }

    def test_it_asks_for_a_numeric_keypad(self):
        assert input_of(PartialDateMaskInput())["inputmode"] == "numeric"

    def test_an_inputmode_the_developer_states_is_kept(self):
        widget = PartialDateMaskInput(attrs={"inputmode": "text"})

        assert input_of(widget)["inputmode"] == "text"

    def test_the_developers_attrs_are_kept(self):
        widget = PartialDateMaskInput(attrs={"placeholder": "Born", "id": "born"})

        drawn = input_of(widget)

        assert drawn["placeholder"] == "Born"
        assert drawn["id"] == "born"
        assert drawn["type"] == "text"

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="resolution"):
            PartialDateMaskInput(resolution="month")

    @pytest.mark.parametrize("resolution", ["year", "month", "day"])
    def test_it_writes_the_resolution_the_field_tells_it(self, resolution):
        class Form(forms.Form):
            born = PartialDateField(
                resolution=resolution, widget=PartialDateMaskInput()
            )

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert json.loads(soup.input["data-imask"]) == {
            "kind": "partial-date",
            "resolution": resolution,
        }

    def test_it_keeps_a_resolution_of_day_on_a_field_that_is_not_a_partial_date_field(
        self,
    ):
        class Form(forms.Form):
            born = forms.CharField(widget=PartialDateMaskInput())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert json.loads(soup.input["data-imask"])["resolution"] == "day"

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(PartialDateMaskInput().media)

    def test_it_draws_and_submits_text_on_a_field_that_is_not_a_partial_date_field(
        self,
    ):
        class Form(forms.Form):
            born = forms.CharField(widget=PartialDateMaskInput())

        form = Form(data={"born": "2021-03"})

        assert form.is_valid()
        assert form.cleaned_data["born"] == "2021-03"
        assert BeautifulSoup(str(form["born"]), "html.parser").input["type"] == "text"


def drawn(widget, value=None, name="born"):
    """Return the parts of a three-part widget, by the name each part submits."""
    soup = BeautifulSoup(widget.render(name, value), "html.parser")
    return {
        part: soup.find(attrs={"name": f"{name}_{part}"})
        for part in ("year", "month", "day")
    }


def chosen(part):
    """Return the value of the option a select shows as chosen, or None."""
    option = part.find("option", selected=True)
    return option["value"] if option else None


def cleaned(widget, **sent):
    """Return the form a field with this widget reads from the parts, validated."""

    class Form(forms.Form):
        born = PartialDateField(required=False, widget=widget)

    form = Form({f"born_{part}": value for part, value in sent.items()})
    form.is_valid()
    return form


class ThreePartWidget:
    """What both three-part widgets do alike, run once for each of them."""

    widget = None

    def test_its_parts_submit_under_names_ending_year_month_and_day(self):
        parts = drawn(self.widget())

        assert all(parts.values())

    def test_an_option_it_does_not_have_is_refused(self):
        with pytest.raises(TypeError, match="resolution"):
            self.widget(resolution="month")

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/partial-date.js" in str(self.widget().media)

    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            ({"year": "2021", "month": "", "day": ""}, "2021"),
            ({"year": "2021", "month": "03", "day": ""}, "2021-03"),
            ({"year": "2021", "month": "03", "day": "14"}, "2021-03-14"),
            ({"year": "2021", "month": "3", "day": "4"}, "2021-03-04"),
            ({"year": "", "month": "", "day": ""}, ""),
        ],
        ids=["year", "year and month", "all three", "unpadded", "nothing"],
    )
    def test_the_parts_reach_the_field_as_one_padded_iso_text(self, sent, expected):
        form = cleaned(self.widget(), **sent)

        assert form.is_valid()
        assert form.cleaned_data["born"] == expected

    @pytest.mark.parametrize(
        ("sent", "code"),
        [
            ({"year": "2021", "month": "", "day": "14"}, "no_month"),
            ({"year": "", "month": "03", "day": ""}, "no_year"),
            ({"year": "", "month": "03", "day": "14"}, "no_year"),
        ],
    )
    def test_a_gap_reaches_the_field_and_is_refused(self, sent, code):
        form = cleaned(self.widget(), **sent)

        assert form.has_error("born", code=code)

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2021", ("2021", None, None)),
            ("2021-03", ("2021", "03", None)),
            ("2021-03-14", ("2021", "03", "14")),
            (datetime.date(2021, 3, 14), ("2021", "03", "14")),
            (None, (None, None, None)),
        ],
        ids=["year", "year and month", "text", "date", "nothing"],
    )
    def test_an_initial_value_fills_the_parts_it_has_and_leaves_the_rest(
        self, value, expected
    ):
        parts = drawn(self.widget(), value)

        year = parts["year"]
        shown = year.get("value") if year.name == "input" else chosen(year)
        assert (
            shown or None,
            chosen(parts["month"]) or None,
            chosen(parts["day"]) or None,
        ) == expected

    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            ({"year": "2021", "month": "02", "day": "30"}, ("2021", "02", "30")),
            ({"year": "2021", "month": "", "day": "14"}, ("2021", None, "14")),
            ({"year": "", "month": "03", "day": ""}, (None, "03", None)),
            ({"year": "2021", "month": "2", "day": "30"}, ("2021", "02", "30")),
        ],
        ids=[
            "30th of February",
            "day with no month",
            "month with no year",
            "unpadded parts",
        ],
    )
    def test_a_refused_submission_is_drawn_again_as_it_was_sent(self, sent, expected):
        form = cleaned(self.widget(), **sent)

        parts = drawn(self.widget(), form["born"].value())

        year = parts["year"]
        shown = year.get("value") if year.name == "input" else chosen(year)
        assert (
            shown or None,
            chosen(parts["month"]) or None,
            chosen(parts["day"]) or None,
        ) == expected

    def test_the_month_options_carry_the_names_of_the_active_language(self):
        widget = self.widget()

        with translation.override("de"):
            month = drawn(widget)["month"]
            names = {number: str(name) for number, name in MONTHS.items()}

        labels = {
            option["value"]: option.get_text()
            for option in month("option")
            if option["value"]
        }
        assert labels == {f"{number:02}": name for number, name in names.items()}
        assert names[1] != str(MONTHS[1])

    def test_the_developers_attrs_reach_every_part(self):
        widget = self.widget(attrs={"data-note": "kept", "title": "Born"})

        parts = drawn(widget)

        assert [part["data-note"] for part in parts.values()] == ["kept"] * 3
        assert [part["title"] for part in parts.values()] == ["Born"] * 3

    def test_each_part_says_which_part_it_is(self):
        parts = drawn(self.widget())

        assert {
            name: part["data-partial-date-part"] for name, part in parts.items()
        } == {
            "year": "year",
            "month": "month",
            "day": "day",
        }
        assert all(part["aria-label"] for part in parts.values())

    def test_the_parts_are_drawn_inside_one_element_that_marks_the_group(self):
        soup = BeautifulSoup(self.widget().render("born", None), "html.parser")

        group = soup.find(attrs={"data-partial-date": True})

        assert len(soup.find_all(attrs={"data-partial-date": True})) == 1
        assert len(group.find_all(attrs={"data-partial-date-part": True})) == 3

    @pytest.mark.parametrize(
        ("resolution", "expected"),
        [
            ("year", ["year"]),
            ("month", ["year", "month"]),
            ("day", ["year", "month", "day"]),
        ],
    )
    def test_it_draws_no_part_finer_than_the_resolution_the_field_tells_it(
        self, resolution, expected
    ):
        class Form(forms.Form):
            born = PartialDateField(resolution=resolution, widget=self.widget())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        parts = soup.find_all(attrs={"data-partial-date-part": True})
        assert [part["data-partial-date-part"] for part in parts] == expected

    def test_it_draws_every_part_on_a_field_that_is_not_a_partial_date_field(self):
        class Form(forms.Form):
            born = forms.CharField(widget=self.widget())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        parts = soup.find_all(attrs={"data-partial-date-part": True})
        assert [part["data-partial-date-part"] for part in parts] == [
            "year",
            "month",
            "day",
        ]

    def test_a_part_the_resolution_leaves_out_is_refused_if_it_is_sent_anyway(self):
        class Form(forms.Form):
            born = PartialDateField(resolution="month", widget=self.widget())

        form = Form({"born_year": "2021", "born_month": "03", "born_day": "14"})

        assert form.has_error("born", code="too_fine_day")

    def test_only_the_year_is_required(self):
        class Form(forms.Form):
            born = PartialDateField(widget=self.widget())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        required = {
            part: soup.find(attrs={"data-partial-date-part": part}).has_attr("required")
            for part in ("year", "month", "day")
        }
        assert required == {"year": True, "month": False, "day": False}


class TestPartialDateInput(ThreePartWidget):
    widget = PartialDateInput

    def test_the_year_is_a_text_input_of_four_digits(self):
        year = drawn(PartialDateInput())["year"]

        assert year.name == "input"
        assert year["type"] == "text"
        assert year["maxlength"] == "4"

    def test_the_month_and_the_day_are_selects_of_twelve_and_of_31(self):
        parts = drawn(PartialDateInput())

        months = [option["value"] for option in parts["month"]("option")]
        days = [option["value"] for option in parts["day"]("option")]
        assert months == ["", *(f"{number:02}" for number in range(1, 13))]
        assert days == ["", *(f"{number:02}" for number in range(1, 32))]


class TestPartialDateSelect(ThreePartWidget):
    widget = PartialDateSelect

    def years(self, value=None):
        year = drawn(PartialDateSelect(), value)["year"]
        return [option["value"] for option in year("option") if option["value"]]

    def test_the_year_is_a_select(self):
        assert drawn(PartialDateSelect())["year"].name == "select"

    def test_the_years_run_from_this_year_back_a_hundred_latest_first(self):
        this_year = datetime.date.today().year

        assert self.years() == [
            f"{year:04}" for year in range(this_year, this_year - 101, -1)
        ]

    def test_a_held_year_that_is_not_on_the_list_is_still_an_option(self):
        parts = drawn(PartialDateSelect(), "1850-03")

        assert "1850" in self.years("1850-03")
        assert chosen(parts["year"]) == "1850"

    def test_a_year_on_the_list_is_chosen(self):
        parts = drawn(PartialDateSelect(), "2020")

        assert chosen(parts["year"]) == "2020"
