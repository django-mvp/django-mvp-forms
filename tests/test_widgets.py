"""The mask and Tom Select widgets, and the blocks a pattern names, as written."""

import datetime
import json
import re
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup
from django import forms
from django.contrib.auth.models import Group
from django.http import QueryDict
from django.utils import translation
from django.utils.dates import MONTHS
from django.utils.translation import gettext_lazy

from mvp_forms.fields import LatitudeField, LongitudeField, PartialDateField, PointField
from mvp_forms.widgets import (
    CoordinateMaskInput,
    DynamicMaskInput,
    EnumBlock,
    NumberMaskInput,
    PartialDateInput,
    PartialDateMaskInput,
    PartialDateSelect,
    PatternBlock,
    PatternMaskInput,
    PointInput,
    RangeBlock,
    RegexMaskInput,
    TomSelect,
    TomSelectMultiple,
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
    def test_it_writes_its_kind_and_the_highest_resolution_a_form_may_hold(self):
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
        with pytest.raises(TypeError, match="max_resolution"):
            PartialDateMaskInput(max_resolution="month")

    @pytest.mark.parametrize(
        ("max_resolution", "shape"),
        [("year", "YYYY"), ("month", "YYYY-MM"), ("day", "YYYY-MM-DD")],
    )
    def test_it_shows_the_shape_of_the_date_its_field_accepts_as_a_placeholder(
        self, max_resolution, shape
    ):
        class Form(forms.Form):
            born = PartialDateField(
                max_resolution=max_resolution, widget=PartialDateMaskInput()
            )

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert soup.input["placeholder"] == shape

    def test_a_field_that_is_not_a_partial_date_field_shows_a_full_date_placeholder(
        self,
    ):
        class Form(forms.Form):
            born = forms.CharField(widget=PartialDateMaskInput())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert soup.input["placeholder"] == "YYYY-MM-DD"

    def test_a_placeholder_the_developer_states_is_kept_at_every_resolution(self):
        class Form(forms.Form):
            born = PartialDateField(
                max_resolution="month",
                widget=PartialDateMaskInput(attrs={"placeholder": "Born"}),
            )

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert soup.input["placeholder"] == "Born"

    @pytest.mark.parametrize("resolution", ["year", "month", "day"])
    def test_it_writes_the_max_resolution_the_field_tells_it(self, resolution):
        class Form(forms.Form):
            born = PartialDateField(
                max_resolution=resolution, widget=PartialDateMaskInput()
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

    @pytest.mark.parametrize(
        ("limits", "expected"),
        [
            ({"min_value": "1998-03-15"}, {"min": "1998-03-15"}),
            ({"max_value": "2004-09"}, {"max": "2004-09"}),
            (
                {"min_value": "1998-03-15", "max_value": "2004-09"},
                {"min": "1998-03-15", "max": "2004-09"},
            ),
            ({"min_value": datetime.date(1998, 3, 5)}, {"min": "1998-03-05"}),
            ({"max_value": "2004-9"}, {"max": "2004-09"}),
            ({}, {}),
        ],
        ids=["earliest", "latest", "both", "a Python date", "padded", "neither"],
    )
    def test_it_writes_the_limits_the_field_tells_it_where_they_are_stated(
        self, limits, expected
    ):
        class Form(forms.Form):
            born = PartialDateField(widget=PartialDateMaskInput(), **limits)

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert json.loads(soup.input["data-imask"]) == {
            "kind": "partial-date",
            "resolution": "day",
            **expected,
        }

    def test_it_writes_no_limit_on_a_field_that_is_not_a_partial_date_field(self):
        class Form(forms.Form):
            born = forms.CharField(widget=PartialDateMaskInput())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        assert set(json.loads(soup.input["data-imask"])) == {"kind", "resolution"}

    @pytest.mark.parametrize("sent", ["1997-03-14", "2004-10", "1997"])
    def test_a_refused_date_outside_the_limits_is_drawn_as_it_was_sent(self, sent):
        class Form(forms.Form):
            born = PartialDateField(
                min_value="1998-03-15",
                max_value="2004-09",
                widget=PartialDateMaskInput(),
            )

        form = Form({"born": sent})
        soup = BeautifulSoup(str(form["born"]), "html.parser")

        assert not form.is_valid()
        assert soup.input["value"] == sent

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


class TestCoordinateMaskInput:
    def test_a_latitude_field_with_no_options_writes_the_bounds_of_a_latitude(self):
        class Form(forms.Form):
            where = LatitudeField()

        soup = BeautifulSoup(str(Form()["where"]), "html.parser")

        assert json.loads(soup.input["data-imask"]) == {
            "kind": "coordinate",
            "scale": 6,
            "radix": ".",
            "thousandsSeparator": "",
            "min": -90,
            "max": 90,
        }

    def test_a_longitude_field_with_no_options_writes_the_bounds_of_a_longitude(self):
        class Form(forms.Form):
            where = LongitudeField()

        soup = BeautifulSoup(str(Form()["where"]), "html.parser")

        options = json.loads(soup.input["data-imask"])

        assert (options["min"], options["max"]) == (-180, 180)

    def test_two_forms_of_one_class_each_draw_their_own_fields_values(self):
        class Form(forms.Form):
            where = LatitudeField()

        first, second = Form(), Form()
        first.fields["where"].min_value = Decimal(-10)
        second.fields["where"].min_value = Decimal(-20)

        drawn_first = BeautifulSoup(str(first["where"]), "html.parser").input
        drawn_second = BeautifulSoup(str(second["where"]), "html.parser").input

        assert json.loads(drawn_first["data-imask"])["min"] == -10
        assert json.loads(drawn_second["data-imask"])["min"] == -20

    def test_the_narrowed_bounds_and_decimal_places_are_written(self):
        class Form(forms.Form):
            north = LatitudeField(min_value=40, max_value=60, decimal_places=2)
            south = LatitudeField(min_value=Decimal("-60.5"), max_value=-40)
            whole = LongitudeField(decimal_places=0)

        form = Form()
        north, south, whole = (
            json.loads(
                BeautifulSoup(str(form[name]), "html.parser").input["data-imask"]
            )
            for name in ("north", "south", "whole")
        )

        assert (north["min"], north["max"], north["scale"]) == (40, 60, 2)
        assert (south["min"], south["max"], south["scale"]) == (-60.5, -40, 6)
        assert (whole["min"], whole["max"], whole["scale"]) == (-180, 180, 0)

    def test_it_is_the_default_widget_of_both_fields(self):
        assert isinstance(LatitudeField().widget, CoordinateMaskInput)
        assert isinstance(LongitudeField().widget, CoordinateMaskInput)

    def test_a_widget_the_developer_named_is_left_as_it_is(self):
        class Form(forms.Form):
            where = LatitudeField(widget=forms.TextInput)

        soup = BeautifulSoup(str(Form()["where"]), "html.parser")

        assert not soup.input.has_attr("data-imask")

    def test_on_a_field_that_is_not_a_coordinate_field_it_draws_with_no_bounds(self):
        class Form(forms.Form):
            where = forms.CharField(widget=CoordinateMaskInput())

        soup = BeautifulSoup(str(Form()["where"]), "html.parser")

        assert json.loads(soup.input["data-imask"]) == {
            "kind": "coordinate",
            "scale": 6,
            "radix": ".",
            "thousandsSeparator": "",
        }

    def test_it_draws_no_inputmode(self):
        assert not input_of(CoordinateMaskInput()).has_attr("inputmode")

    def test_an_inputmode_the_developer_states_is_kept(self):
        widget = CoordinateMaskInput(attrs={"inputmode": "text"})

        assert input_of(widget)["inputmode"] == "text"

    def test_the_input_is_a_text_input_with_no_step_min_or_max(self):
        class Form(forms.Form):
            where = LatitudeField()

        drawn_input = BeautifulSoup(str(Form()["where"]), "html.parser").input

        assert drawn_input["type"] == "text"
        for name in ("step", "min", "max"):
            assert not drawn_input.has_attr(name)

    def test_its_form_names_the_script_that_applies_the_mask(self):
        class Form(forms.Form):
            where = LatitudeField()

        assert "mvp_forms/imask.js" in str(Form().media)

    def test_a_form_with_no_coordinate_field_names_no_script_it_did_not_name(self):
        class Form(forms.Form):
            name = forms.CharField()

        assert "imask.js" not in str(Form().media)

    @pytest.mark.parametrize("language", ["en", "de", "fr"])
    def test_an_initial_value_is_drawn_with_a_full_stop(self, language):
        class Form(forms.Form):
            where = LatitudeField(initial=Decimal("51.5"))

        with translation.override(language):
            soup = BeautifulSoup(str(Form()["where"]), "html.parser")

        assert soup.input["value"] == "51.5"


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
        with pytest.raises(TypeError, match="max_resolution"):
            self.widget(max_resolution="month")

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

    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            ({"year": "20-21", "month": "03", "day": "14"}, ("20-21", "03", "14")),
            ({"year": "2021-03", "month": "", "day": ""}, ("2021-03", None, None)),
        ],
        ids=["hyphen inside the year", "month written into the year"],
    )
    def test_a_part_holding_a_hyphen_is_refused_and_drawn_again_as_it_was_sent(
        self, sent, expected
    ):
        form = cleaned(self.widget(), **sent)

        parts = drawn(self.widget(), form["born"].value())

        year = parts["year"]
        shown = year.get("value") if year.name == "input" else chosen(year)
        assert form.has_error("born", code="invalid")
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
        names = [part["aria-label"] for part in parts.values()]
        assert all(names)
        assert len(set(names)) == len(names)

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
    def test_it_draws_no_part_higher_than_the_max_resolution_the_field_tells_it(
        self, resolution, expected
    ):
        class Form(forms.Form):
            born = PartialDateField(max_resolution=resolution, widget=self.widget())

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

    @pytest.mark.parametrize(
        ("limits", "expected"),
        [
            ({"min_value": "1998-03-15"}, {"min": "1998-03-15"}),
            ({"max_value": "2004-09"}, {"max": "2004-09"}),
            (
                {"min_value": "1998-03-15", "max_value": "2004-09"},
                {"min": "1998-03-15", "max": "2004-09"},
            ),
            ({"min_value": datetime.date(1998, 3, 5)}, {"min": "1998-03-05"}),
            ({}, {}),
        ],
        ids=["earliest", "latest", "both", "a Python date", "neither"],
    )
    def test_the_group_carries_the_limits_the_field_tells_it_where_they_are_stated(
        self, limits, expected
    ):
        class Form(forms.Form):
            born = PartialDateField(widget=self.widget(), **limits)

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        group = soup.find(attrs={"data-partial-date": True})
        assert {
            "min": group.get("data-partial-date-min"),
            "max": group.get("data-partial-date-max"),
        } == {"min": None, "max": None, **expected}

    def test_the_group_carries_no_limit_on_a_field_that_is_not_a_partial_date_field(
        self,
    ):
        class Form(forms.Form):
            born = forms.CharField(widget=self.widget())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        group = soup.find(attrs={"data-partial-date": True})
        assert not group.has_attr("data-partial-date-min")
        assert not group.has_attr("data-partial-date-max")

    @pytest.mark.parametrize(
        ("sent", "code"),
        [
            ({"year": "1997", "month": "03", "day": "14"}, "min_value"),
            ({"year": "1998", "month": "03", "day": "14"}, "min_value"),
            ({"year": "2004", "month": "10", "day": ""}, "max_value"),
            ({"year": "2005", "month": "", "day": ""}, "max_value"),
        ],
    )
    def test_a_refused_date_outside_the_limits_is_drawn_as_it_was_sent(
        self, sent, code
    ):
        widget = self.widget()

        class Form(forms.Form):
            born = PartialDateField(
                min_value="1998-03-15", max_value="2004-09", widget=widget
            )

        form = Form({f"born_{part}": value for part, value in sent.items()})
        parts = drawn(widget, form["born"].value())

        year = parts["year"]
        shown = year.get("value") if year.name == "input" else chosen(year)
        assert form.has_error("born", code=code)
        assert (
            shown or None,
            chosen(parts["month"]) or None,
            chosen(parts["day"]) or None,
        ) == tuple(value or None for value in sent.values())

    def test_a_datetime_is_split_by_its_date_alone(self):
        parts = drawn(self.widget(), datetime.datetime(2021, 3, 14, 10, 30, 5))

        year = parts["year"]
        shown = year.get("value") if year.name == "input" else chosen(year)
        assert (shown, chosen(parts["month"]), chosen(parts["day"])) == (
            "2021",
            "03",
            "14",
        )

    def test_a_part_the_max_resolution_leaves_out_is_refused_if_it_is_sent_anyway(self):
        class Form(forms.Form):
            born = PartialDateField(max_resolution="month", widget=self.widget())

        form = Form({"born_year": "2021", "born_month": "03", "born_day": "14"})

        assert form.has_error("born", code="day_not_allowed")

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

    def test_the_years_run_from_the_latest_limits_year_down_to_the_earliests(self):
        class Form(forms.Form):
            born = PartialDateField(
                min_value="1998-03-15", max_value="2004-09", widget=PartialDateSelect()
            )

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        years = soup.find(attrs={"data-partial-date-part": "year"})("option")
        assert [option["value"] for option in years if option["value"]] == [
            f"{year}" for year in range(2004, 1997, -1)
        ]

    def test_with_no_earliest_date_the_years_reach_a_hundred_back_from_the_latest(
        self,
    ):
        class Form(forms.Form):
            born = PartialDateField(max_value="2004-09", widget=PartialDateSelect())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        years = soup.find(attrs={"data-partial-date-part": "year"})("option")
        assert [option["value"] for option in years if option["value"]] == [
            f"{year}" for year in range(2004, 1903, -1)
        ]

    def test_with_a_latest_date_in_the_first_hundred_years_the_years_stop_at_0001(
        self,
    ):
        class Form(forms.Form):
            born = PartialDateField(max_value="0050", widget=PartialDateSelect())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        years = soup.find(attrs={"data-partial-date-part": "year"})("option")
        values = [option["value"] for option in years if option["value"]]
        assert values == [f"{year:04}" for year in range(50, 0, -1)]

    def test_with_no_latest_date_the_years_start_this_year(self):
        this_year = datetime.date.today().year

        class Form(forms.Form):
            born = PartialDateField(min_value="1998", widget=PartialDateSelect())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        years = soup.find(attrs={"data-partial-date-part": "year"})("option")
        assert [option["value"] for option in years if option["value"]] == [
            f"{year}" for year in range(this_year, 1997, -1)
        ]

    def test_with_no_latest_date_and_an_earliest_in_the_future_the_years_run_a_hundred_on(
        self,
    ):
        first = datetime.date.today().year + 5

        class Form(forms.Form):
            born = PartialDateField(min_value=f"{first}-06", widget=PartialDateSelect())

        soup = BeautifulSoup(str(Form()["born"]), "html.parser")

        years = soup.find(attrs={"data-partial-date-part": "year"})("option")
        assert [option["value"] for option in years if option["value"]] == [
            f"{year}" for year in range(first + 100, first - 1, -1)
        ]

    def test_a_held_year_outside_the_limits_is_put_first_and_chosen(self):
        class Form(forms.Form):
            born = PartialDateField(
                min_value="1998", max_value="2004", widget=PartialDateSelect()
            )

        form = Form({"born_year": "1990", "born_month": "03"})
        soup = BeautifulSoup(str(form["born"]), "html.parser")

        year = soup.find(attrs={"data-partial-date-part": "year"})
        values = [option["value"] for option in year("option") if option["value"]]
        assert values == ["1990", *(f"{n}" for n in range(2004, 1997, -1))]
        assert chosen(year) == "1990"


FRUIT = [("a", "Apple"), ("b", "Banana"), ("c", "Cherry")]


def select_of(widget, value=None):
    """Return the select the widget draws."""
    return BeautifulSoup(widget.render("field", value), "html.parser").select_one(
        "select"
    )


def selected_values(select):
    """Return the values of the options the select holds as chosen."""
    return [option["value"] for option in select.find_all("option", selected=True)]


class TestTomSelectMultiple:
    def test_it_draws_a_multiple_select_holding_every_choice(self):
        select = select_of(TomSelectMultiple(choices=FRUIT))

        assert select.has_attr("multiple")
        assert [each["value"] for each in select.find_all("option")] == ["a", "b", "c"]

    def test_it_writes_no_setting_when_none_is_stated(self):
        select = select_of(TomSelectMultiple(choices=FRUIT))

        assert json.loads(select["data-tom-select"]) == {}

    def test_its_media_names_the_script_and_no_stylesheet(self):
        media = TomSelectMultiple().media

        assert media._js == ["mvp_forms/tomselect.js"]
        assert media._css == {}

    def test_the_developers_attrs_are_kept_beside_the_attribute(self):
        widget = TomSelectMultiple(
            attrs={"class": "mine", "data-role": "picker"}, choices=FRUIT
        )

        select = select_of(widget)

        assert select["class"] == ["mine"]
        assert select["data-role"] == "picker"
        assert json.loads(select["data-tom-select"]) == {}

    def test_a_subclass_is_drawn_as_its_parent_is(self):
        class Teams(TomSelectMultiple):
            pass

        select = select_of(Teams(choices=FRUIT))

        assert json.loads(select["data-tom-select"]) == {}
        assert Teams().media._js == ["mvp_forms/tomselect.js"]

    def test_grouped_choices_are_drawn_as_option_groups(self):
        widget = TomSelectMultiple(
            choices=[("Fruit", FRUIT[:2]), ("Vegetable", [("d", "Dill")]), ("e", "Egg")]
        )

        select = select_of(widget)

        groups = {
            group["label"]: [each["value"] for each in group.find_all("option")]
            for group in select.find_all("optgroup")
        }
        assert groups == {"Fruit": ["a", "b"], "Vegetable": ["d"]}

    def test_initial_values_are_drawn_as_chosen(self):
        select = select_of(TomSelectMultiple(choices=FRUIT), ["a", "c"])

        assert selected_values(select) == ["a", "c"]


class TestWhatTheTomSelectMultipleFieldReceives:
    @staticmethod
    def fields(field_class, **kwargs):
        """Return the field with the stock widget and with the Tom Select one."""
        return (
            field_class(widget=forms.SelectMultiple, **kwargs),
            field_class(widget=TomSelectMultiple, **kwargs),
        )

    @staticmethod
    def received(field, entries):
        """Return what the field cleans the entries to, as its form would."""
        data = QueryDict(mutable=True)
        data.setlist("field", entries)
        return field.clean(field.widget.value_from_datadict(data, {}, "field"))

    @pytest.mark.parametrize(
        ("field_class", "kwargs", "entries"),
        [
            (forms.MultipleChoiceField, {"choices": FRUIT}, ["a", "c"]),
            (
                forms.TypedMultipleChoiceField,
                {"choices": [("1", "One"), ("2", "Two")], "coerce": int},
                ["1", "2"],
            ),
        ],
    )
    def test_a_field_cleans_what_it_cleans_from_a_stock_select(
        self, field_class, kwargs, entries
    ):
        stock, tom = self.fields(field_class, **kwargs)

        assert self.received(tom, entries) == self.received(stock, entries)

    @pytest.mark.django_db
    def test_a_model_field_cleans_to_the_same_objects(self):
        queryset = Group.objects.all()
        names = ["Editors", "Readers"]
        pks = [str(Group.objects.create(name=name).pk) for name in names]
        stock, tom = self.fields(forms.ModelMultipleChoiceField, queryset=queryset)

        assert list(self.received(tom, pks)) == list(self.received(stock, pks))
        assert len(self.received(tom, pks)) == 2

    @pytest.mark.parametrize(
        ("field_class", "kwargs"),
        [
            (forms.MultipleChoiceField, {"choices": FRUIT}),
            (
                forms.TypedMultipleChoiceField,
                {"choices": FRUIT, "coerce": str},
            ),
        ],
    )
    def test_a_value_not_among_the_choices_is_refused(self, field_class, kwargs):
        stock, tom = self.fields(field_class, **kwargs)

        with pytest.raises(forms.ValidationError) as refused:
            self.received(tom, ["nowhere"])

        with pytest.raises(forms.ValidationError) as refused_stock:
            self.received(stock, ["nowhere"])
        assert refused.value.code == refused_stock.value.code == "invalid_choice"

    @pytest.mark.django_db
    def test_a_model_value_not_among_the_choices_is_refused(self):
        stock, tom = self.fields(
            forms.ModelMultipleChoiceField, queryset=Group.objects.all()
        )

        with pytest.raises(forms.ValidationError) as refused:
            self.received(tom, ["999"])

        with pytest.raises(forms.ValidationError) as refused_stock:
            self.received(stock, ["999"])
        assert refused.value.code == refused_stock.value.code == "invalid_choice"


class TestTomSelect:
    def test_it_draws_a_single_select_holding_every_choice(self):
        select = select_of(TomSelect(choices=FRUIT))

        assert not select.has_attr("multiple")
        assert [each["value"] for each in select.find_all("option")] == ["a", "b", "c"]

    def test_it_writes_no_setting_when_none_is_stated(self):
        select = select_of(TomSelect(choices=FRUIT))

        assert json.loads(select["data-tom-select"]) == {}

    def test_its_media_names_the_script_and_no_stylesheet(self):
        media = TomSelect().media

        assert media._js == ["mvp_forms/tomselect.js"]
        assert media._css == {}

    def test_the_developers_attrs_are_kept_beside_the_attribute(self):
        widget = TomSelect(
            attrs={"class": "mine", "data-role": "picker"}, choices=FRUIT
        )

        select = select_of(widget)

        assert select["class"] == ["mine"]
        assert select["data-role"] == "picker"
        assert json.loads(select["data-tom-select"]) == {}

    def test_a_subclass_is_drawn_as_its_parent_is(self):
        class Teams(TomSelect):
            pass

        select = select_of(Teams(choices=FRUIT))

        assert json.loads(select["data-tom-select"]) == {}
        assert Teams().media._js == ["mvp_forms/tomselect.js"]

    def test_grouped_choices_are_drawn_as_option_groups(self):
        widget = TomSelect(
            choices=[("Fruit", FRUIT[:2]), ("Vegetable", [("d", "Dill")]), ("e", "Egg")]
        )

        select = select_of(widget)

        groups = {
            group["label"]: [each["value"] for each in group.find_all("option")]
            for group in select.find_all("optgroup")
        }
        assert groups == {"Fruit": ["a", "b"], "Vegetable": ["d"]}

    def test_the_initial_value_is_drawn_as_chosen(self):
        select = select_of(TomSelect(choices=FRUIT), "b")

        assert selected_values(select) == ["b"]

    def test_the_empty_choice_is_drawn_as_an_option(self):
        select = select_of(TomSelect(choices=[("", "None"), *FRUIT]))

        assert [each["value"] for each in select.find_all("option")] == [
            "",
            "a",
            "b",
            "c",
        ]


class TestWhatTheTomSelectFieldReceives:
    @staticmethod
    def fields(field_class, **kwargs):
        """Return the field with the stock widget and with the Tom Select one."""
        return (
            field_class(widget=forms.Select, **kwargs),
            field_class(widget=TomSelect, **kwargs),
        )

    @staticmethod
    def received(field, entry):
        """Return what the field cleans the entry to, as its form would."""
        data = QueryDict(mutable=True)
        data["field"] = entry
        return field.clean(field.widget.value_from_datadict(data, {}, "field"))

    @pytest.mark.parametrize(
        ("field_class", "kwargs", "entry"),
        [
            (forms.ChoiceField, {"choices": FRUIT}, "b"),
            (
                forms.TypedChoiceField,
                {"choices": [("1", "One"), ("2", "Two")], "coerce": int},
                "2",
            ),
            (
                forms.ChoiceField,
                {"choices": [("", "None"), *FRUIT], "required": False},
                "",
            ),
            (
                forms.TypedChoiceField,
                {
                    "choices": [("", "None"), ("1", "One")],
                    "coerce": int,
                    "required": False,
                    "empty_value": None,
                },
                "",
            ),
        ],
    )
    def test_a_field_cleans_what_it_cleans_from_a_stock_select(
        self, field_class, kwargs, entry
    ):
        stock, tom = self.fields(field_class, **kwargs)

        assert self.received(tom, entry) == self.received(stock, entry)

    @pytest.mark.django_db
    def test_a_model_field_cleans_to_the_same_object(self):
        pk = str(Group.objects.create(name="Editors").pk)
        stock, tom = self.fields(forms.ModelChoiceField, queryset=Group.objects.all())

        assert self.received(tom, pk) == self.received(stock, pk)
        assert self.received(tom, pk).name == "Editors"

    @pytest.mark.django_db
    def test_a_model_field_that_is_optional_cleans_the_empty_entry_to_none(self):
        stock, tom = self.fields(
            forms.ModelChoiceField, queryset=Group.objects.all(), required=False
        )

        assert self.received(tom, "") is None
        assert self.received(stock, "") is None

    @pytest.mark.parametrize(
        ("field_class", "kwargs"),
        [
            (forms.ChoiceField, {"choices": FRUIT}),
            (forms.TypedChoiceField, {"choices": FRUIT, "coerce": str}),
        ],
    )
    def test_a_value_not_among_the_choices_is_refused(self, field_class, kwargs):
        stock, tom = self.fields(field_class, **kwargs)

        with pytest.raises(forms.ValidationError) as refused:
            self.received(tom, "nowhere")

        with pytest.raises(forms.ValidationError) as refused_stock:
            self.received(stock, "nowhere")
        assert refused.value.code == refused_stock.value.code == "invalid_choice"

    @pytest.mark.django_db
    def test_a_model_value_not_among_the_choices_is_refused(self):
        stock, tom = self.fields(forms.ModelChoiceField, queryset=Group.objects.all())

        with pytest.raises(forms.ValidationError) as refused:
            self.received(tom, "999")

        with pytest.raises(forms.ValidationError) as refused_stock:
            self.received(stock, "999")
        assert refused.value.code == refused_stock.value.code == "invalid_choice"

    def test_a_required_field_refuses_the_empty_entry(self):
        stock, tom = self.fields(forms.ChoiceField, choices=[("", "None"), *FRUIT])

        with pytest.raises(forms.ValidationError) as refused:
            self.received(tom, "")

        with pytest.raises(forms.ValidationError) as refused_stock:
            self.received(stock, "")
        assert refused.value.code == refused_stock.value.code == "required"


def settings_of(widget):
    """Return the settings the widget writes on the select it draws."""
    return json.loads(select_of(widget)["data-tom-select"])


class TestTheSettingsOfBothWidgets:
    @pytest.fixture(params=[TomSelect, TomSelectMultiple])
    def widget_class(self, request):
        return request.param

    def test_a_placeholder_is_written_under_tom_selects_name(self, widget_class):
        widget = widget_class(choices=FRUIT, placeholder="Pick one")

        assert settings_of(widget) == {"placeholder": "Pick one"}

    def test_the_clear_button_is_written_as_a_plugin(self, widget_class):
        widget = widget_class(choices=FRUIT, clear_button=True)

        assert settings_of(widget) == {"plugins": ["clear_button"]}

    def test_a_clear_button_that_is_not_wanted_is_not_written(self, widget_class):
        widget = widget_class(choices=FRUIT, clear_button=False)

        assert settings_of(widget) == {}

    def test_no_setting_is_written_for_one_that_is_not_stated(self, widget_class):
        widget = widget_class(choices=FRUIT, placeholder="Pick one")

        assert "plugins" not in settings_of(widget)

    def test_the_settings_are_written_beside_the_developers_attrs(self, widget_class):
        widget = widget_class(
            attrs={"class": "mine"}, choices=FRUIT, placeholder="Pick one"
        )

        select = select_of(widget)

        assert select["class"] == ["mine"]
        assert json.loads(select["data-tom-select"]) == {"placeholder": "Pick one"}

    def test_the_settings_are_taken_by_name_only(self, widget_class):
        with pytest.raises(TypeError):
            widget_class(None, FRUIT, "Pick one")

    def test_a_lazy_placeholder_is_written_in_the_language_active_when_drawn(
        self, widget_class
    ):
        lazy = gettext_lazy("This field is required.")
        widget = widget_class(choices=FRUIT, placeholder=lazy)

        with translation.override("en"):
            english = settings_of(widget)["placeholder"]
            in_english = str(lazy)
        with translation.override("de"):
            german = settings_of(widget)["placeholder"]
            in_german = str(lazy)

        assert in_english != in_german
        assert (english, german) == (in_english, in_german)

    @pytest.mark.parametrize("value", ["", 3, b"bytes", ["a"]])
    def test_a_placeholder_that_is_not_text_or_is_empty_is_refused(
        self, widget_class, value
    ):
        with pytest.raises(ValueError, match="placeholder"):
            widget_class(placeholder=value)

    @pytest.mark.parametrize("value", [1, 0, "yes"])
    def test_a_clear_button_that_is_not_true_or_false_is_refused(
        self, widget_class, value
    ):
        with pytest.raises(ValueError, match="clear_button"):
            widget_class(clear_button=value)


class TestTheSettingsOfTomSelectMultiple:
    def test_the_remove_button_is_written_as_a_plugin(self):
        widget = TomSelectMultiple(choices=FRUIT, remove_button=True)

        assert settings_of(widget) == {"plugins": ["remove_button"]}

    def test_both_buttons_are_written_as_plugins(self):
        widget = TomSelectMultiple(choices=FRUIT, clear_button=True, remove_button=True)

        assert settings_of(widget) == {"plugins": ["clear_button", "remove_button"]}

    def test_the_largest_number_of_values_is_written_as_max_items(self):
        widget = TomSelectMultiple(choices=FRUIT, max_items=3)

        assert settings_of(widget) == {"maxItems": 3}

    def test_every_setting_is_written_together(self):
        widget = TomSelectMultiple(
            choices=FRUIT,
            placeholder="Pick some",
            clear_button=True,
            remove_button=True,
            max_items=2,
        )

        assert settings_of(widget) == {
            "placeholder": "Pick some",
            "maxItems": 2,
            "plugins": ["clear_button", "remove_button"],
        }

    @pytest.mark.parametrize("value", [1, 0, "yes"])
    def test_a_remove_button_that_is_not_true_or_false_is_refused(self, value):
        with pytest.raises(ValueError, match="remove_button"):
            TomSelectMultiple(remove_button=value)

    @pytest.mark.parametrize("value", [True, False, 2.0, "2", 0, -1])
    def test_a_largest_number_that_is_not_a_whole_number_above_zero_is_refused(
        self, value
    ):
        with pytest.raises(ValueError, match="max_items"):
            TomSelectMultiple(max_items=value)

    def test_a_largest_number_of_one_is_accepted_and_the_field_still_gets_a_list(
        self,
    ):
        field = forms.MultipleChoiceField(
            choices=FRUIT, widget=TomSelectMultiple(max_items=1)
        )
        data = QueryDict(mutable=True)
        data.setlist("field", ["b"])

        assert settings_of(field.widget) == {"maxItems": 1}
        assert field.clean(field.widget.value_from_datadict(data, {}, "field")) == ["b"]


class TestACountedTomSelectMultiple:
    def test_it_turns_on_the_checkbox_and_search_box_plugins(self):
        widget = TomSelectMultiple(choices=FRUIT, counted=True)

        assert settings_of(widget) == {
            "plugins": ["checkbox_options", "dropdown_input"]
        }

    def test_its_plugins_follow_the_clear_button(self):
        widget = TomSelectMultiple(choices=FRUIT, clear_button=True, counted=True)

        assert settings_of(widget)["plugins"] == [
            "clear_button",
            "checkbox_options",
            "dropdown_input",
        ]

    def test_it_writes_the_two_words_it_is_given_on_the_select(self):
        widget = TomSelectMultiple(
            choices=FRUIT, counted=True, none_text="None yet", count_text="chosen"
        )

        select = select_of(widget)

        assert (select["data-none-text"], select["data-count-text"]) == (
            "None yet",
            "chosen",
        )

    def test_it_writes_both_words_when_none_is_stated(self):
        select = select_of(TomSelectMultiple(choices=FRUIT, counted=True))

        assert select["data-none-text"]
        assert select["data-count-text"]

    def test_a_lazy_word_is_written_in_the_language_active_when_drawn(self):
        lazy = gettext_lazy("This field is required.")
        widget = TomSelectMultiple(choices=FRUIT, counted=True, count_text=lazy)

        with translation.override("en"):
            english = select_of(widget)["data-count-text"]
            in_english = str(lazy)
        with translation.override("de"):
            german = select_of(widget)["data-count-text"]
            in_german = str(lazy)

        assert in_english != in_german
        assert (english, german) == (in_english, in_german)

    @pytest.mark.parametrize("counted", [None, False])
    def test_a_widget_that_is_not_counted_writes_no_words(self, counted):
        select = select_of(TomSelectMultiple(choices=FRUIT, counted=counted))

        assert not select.has_attr("data-none-text")
        assert not select.has_attr("data-count-text")
        assert "plugins" not in json.loads(select["data-tom-select"])

    @pytest.mark.parametrize("value", [1, 0, "yes"])
    def test_counted_that_is_not_true_or_false_is_refused(self, value):
        with pytest.raises(ValueError, match="counted"):
            TomSelectMultiple(counted=value)

    @pytest.mark.parametrize("name", ["none_text", "count_text"])
    @pytest.mark.parametrize("value", ["", 3, ["a"]])
    def test_a_word_that_is_not_text_or_is_empty_is_refused(self, name, value):
        with pytest.raises(ValueError, match=name):
            TomSelectMultiple(counted=True, **{name: value})

    @pytest.mark.parametrize("name", ["none_text", "count_text"])
    def test_a_word_for_a_control_that_is_not_counted_is_refused(self, name):
        with pytest.raises(ValueError, match=name):
            TomSelectMultiple(**{name: "chosen"})

    def test_a_remove_button_on_a_counted_control_is_refused(self):
        with pytest.raises(ValueError, match="remove_button"):
            TomSelectMultiple(counted=True, remove_button=True)


class TestTheSettingsOfTomSelect:
    @pytest.mark.parametrize(
        "name", ["remove_button", "max_items", "counted", "none_text", "count_text"]
    )
    def test_a_setting_only_the_multiple_widget_has_is_refused(self, name):
        with pytest.raises(TypeError, match=name):
            TomSelect(**{name: True})


class Marker:
    """Plays the GEOS point a GeoDjango model holds."""

    def __init__(self, x, y, srid=4326, z=None):
        self.x = x
        self.y = y
        self.srid = srid
        self.z = z


class TestPointInput:
    @pytest.mark.parametrize(
        "value",
        [
            Marker(-0.1278, 51.5074),
            Marker(-0.1278, 51.5074, srid=None),
            "POINT(-0.1278 51.5074)",
            "SRID=4326;POINT(-0.1278 51.5074)",
            "srid=4326; point ( -0.1278   51.5074 )",
            (51.5074, -0.1278),
            [51.5074, -0.1278],
        ],
    )
    def test_decompress_reads_a_point_as_latitude_then_longitude(self, value):
        assert PointInput().decompress(value) == [
            Decimal("51.5074"),
            Decimal("-0.1278"),
        ]

    @pytest.mark.parametrize("value", [None, "", "  "])
    def test_decompress_reads_nothing_as_two_empty_halves(self, value):
        assert PointInput().decompress(value) == [None, None]

    def test_decompress_keeps_each_digit_a_float_is_written_with(self):
        assert PointInput().decompress(Marker(0.00005, 51.50740123)) == [
            Decimal("51.50740123"),
            Decimal("0.00005"),
        ]

    @pytest.mark.parametrize(
        ("value", "named"),
        [
            (Marker(1, 2, srid=3857), "3857"),
            ("SRID=3857;POINT(1 2)", "3857"),
            (Marker(1, 2, z=12.0), "height"),
            ("POINT Z (1 2 3)", "two-dimensional"),
            ("POINT(1 2 3)", "two-dimensional"),
            ("POINT EMPTY", "two-dimensional"),
            ("LINESTRING(1 2, 3 4)", "two-dimensional"),
            ("not a point", "two-dimensional"),
            ((1, 2, 3), "pair"),
            ((51.5, None), "latitude and a longitude"),
            (("51.5", ""), "latitude and a longitude"),
        ],
    )
    def test_decompress_refuses_a_point_the_form_cannot_show(self, value, named):
        with pytest.raises(ValueError, match=named):
            PointInput().decompress(value)

    def test_it_has_a_masked_part_for_each_half(self):
        widget = PointInput()

        assert [type(part) for part in widget.widgets] == [CoordinateMaskInput] * 2

    def test_it_names_the_script_in_its_media(self):
        assert "mvp_forms/imask.js" in str(PointInput().media)

    def test_the_parts_carry_a_label_for_a_screen_reader_each(self):
        class Form(forms.Form):
            place = PointField()

        soup = BeautifulSoup(str(Form()["place"]), "html.parser")
        latitude, longitude = soup.find_all("input")

        assert latitude["aria-label"] != longitude["aria-label"]
        assert latitude["name"] == "place_0"
        assert longitude["name"] == "place_1"

    def test_each_part_is_told_its_own_halfs_bounds_and_places(self):
        class Form(forms.Form):
            place = PointField(
                min_latitude=40,
                max_latitude=60,
                min_longitude=-10.5,
                max_longitude=10,
                decimal_places=2,
            )

        soup = BeautifulSoup(str(Form()["place"]), "html.parser")
        latitude, longitude = (
            json.loads(each["data-imask"]) for each in soup.find_all("input")
        )

        assert (latitude["min"], latitude["max"], latitude["scale"]) == (40, 60, 2)
        assert (longitude["min"], longitude["max"], longitude["scale"]) == (
            -10.5,
            10,
            2,
        )

    def test_the_parts_are_drawn_holding_the_initial_point(self):
        class Form(forms.Form):
            place = PointField()

        form = Form(initial={"place": Marker(-0.1278, 51.5074)})
        soup = BeautifulSoup(str(form["place"]), "html.parser")
        latitude, longitude = soup.find_all("input")

        assert latitude["value"] == "51.5074"
        assert longitude["value"] == "-0.1278"

    def test_a_point_it_cannot_show_raises_when_the_form_is_drawn(self):
        class Form(forms.Form):
            place = PointField()

        form = Form(initial={"place": Marker(1, 2, srid=3857)})

        with pytest.raises(ValueError, match="3857"):
            str(form["place"])
