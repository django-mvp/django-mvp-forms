"""Widgets that put an IMask input mask on a text input.

Each widget writes its options on the input as JSON in ``data-imask``, and the
script named in its media hands them to IMask. The host project loads IMask.
"""

import json
from collections.abc import Mapping
from decimal import Decimal

from django import forms


class Check:
    """The tests an option must pass for the form class to be defined."""

    @staticmethod
    def text(option, value):
        """Refuse a value that is not text, or is empty.

        Args:
            option: The option's name, for the message.
            value: What was stated.

        Raises:
            ValueError: The value is not text, or is empty.
        """
        if not isinstance(value, str) or not value:
            raise ValueError(f"{option} must be text and not empty, not {value!r}.")

    @staticmethod
    def character(option, value):
        """Refuse a value that is not one character of text.

        Args:
            option: The option's name, for the message.
            value: What was stated.

        Raises:
            ValueError: The value is not text of one character.
        """
        if not isinstance(value, str) or len(value) != 1:
            raise ValueError(f"{option} must be one character, not {value!r}.")

    @staticmethod
    def of_type(option, value, kinds, wanted):
        """Refuse a value that is not an instance of one of the kinds.

        The error is a ``ValueError`` and not a ``TypeError``, so that every
        refusal of an option is one kind of error.

        Args:
            option: The option's name, for the message.
            value: What was stated.
            kinds: The class or classes the value must be an instance of.
            wanted: What the value should have been, for the message.

        Raises:
            ValueError: The value is not an instance of one of the kinds.
        """
        if not isinstance(value, kinds):
            raise ValueError(  # noqa: TRY004
                f"{option} must be {wanted}, not {value!r}."
            )

    @staticmethod
    def one_of(option, value, allowed):
        """Refuse a value that is not one of the values allowed.

        Booleans and other values are compared by type as well as by value, so
        ``1`` is not ``True``.

        Args:
            option: The option's name, for the message.
            value: What was stated.
            allowed: The values the option takes.

        Raises:
            ValueError: The value is not one of those allowed.
        """
        if not any(type(value) is type(each) and value == each for each in allowed):
            raise ValueError(f"{option} must be one of {allowed!r}, not {value!r}.")

    @staticmethod
    def whole_number(option, value):
        """Refuse a value that is not an ``int``, or is a boolean.

        Args:
            option: The option's name, for the message.
            value: What was stated.

        Raises:
            ValueError: The value is not a whole number.
        """
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(  # noqa: TRY004
                f"{option} must be a whole number, not {value!r}."
            )

    @staticmethod
    def separator(option, value):
        """Refuse a value that is not one character of text, or no character.

        Args:
            option: The option's name, for the message.
            value: What was stated.

        Raises:
            ValueError: The value is not text of at most one character.
        """
        if not isinstance(value, str) or len(value) > 1:
            raise ValueError(f"{option} must be one character or empty, not {value!r}.")

    @staticmethod
    def number(option, value):
        """Refuse a value that is not a finite ``int``, ``float`` or ``Decimal``.

        Args:
            option: The option's name, for the message.
            value: What was stated.

        Raises:
            ValueError: The value is not a number, or is not finite, which JSON
                cannot write.
        """
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float | Decimal)
            or not Decimal(value).is_finite()
        ):
            raise ValueError(
                f"{option} must be an int, a float or a Decimal, not {value!r}."
            )


class MaskBlock:
    """What the blocks of a pattern have in common: a kind and the options stated."""

    kind = ""

    def __init__(self, options):
        """Keep the options that were stated and drop the rest.

        Args:
            options: The block's options, by IMask's own names.
        """
        self.options = {
            name: value for name, value in options.items() if value is not None
        }

    def mask_options(self):
        """Return what the script reads: the kind of block and its options."""
        return {"kind": self.kind, **self.options}


class RangeBlock(MaskBlock):
    """A block that takes a whole number between two bounds."""

    kind = "range"

    def __init__(
        self, minimum, maximum, *, max_length=None, autofix=None, placeholder_char=None
    ):
        """State the bounds and how the block behaves.

        Args:
            minimum: The smallest number the block takes.
            maximum: The largest number the block takes.
            max_length: The number of digits the block holds.
            autofix: Correct a number outside the bounds to the nearest one.
            placeholder_char: The character shown in each open position.

        Raises:
            ValueError: A bound or the length is not a whole number, the minimum
                is above the maximum, or the placeholder character is not one
                character.
        """
        Check.whole_number("minimum", minimum)
        Check.whole_number("maximum", maximum)
        if max_length is not None:
            Check.whole_number("max_length", max_length)
        if minimum > maximum:
            raise ValueError(
                f"minimum must not be above maximum, not {minimum!r} and {maximum!r}."
            )
        if placeholder_char is not None:
            Check.character("placeholder_char", placeholder_char)
        super().__init__(
            {
                "from": minimum,
                "to": maximum,
                "maxLength": max_length,
                "autofix": autofix,
                "placeholderChar": placeholder_char,
            }
        )


class EnumBlock(MaskBlock):
    """A block that takes one of a list of values."""

    kind = "enum"

    def __init__(self, values, *, placeholder_char=None):
        """State the values the block takes.

        Args:
            values: The values, as text.
            placeholder_char: The character shown in each open position.

        Raises:
            ValueError: The values are not a list of text, there are none, or
                the placeholder character is not one character.
        """
        Check.of_type("values", values, list | tuple, "a list of text")
        if not values:
            raise ValueError("values must hold at least one value.")
        for each in values:
            Check.of_type("values", each, str, f"a list of text, not holding {each!r}")
        if placeholder_char is not None:
            Check.character("placeholder_char", placeholder_char)
        super().__init__({"enum": list(values), "placeholderChar": placeholder_char})


class PatternBlock(MaskBlock):
    """A block that is a pattern of its own, and may be repeated."""

    kind = "pattern"

    def __init__(self, mask, *, repeat=None, placeholder_char=None):
        """State the pattern and how often it is repeated.

        Args:
            mask: The pattern, in IMask's pattern text.
            repeat: How many times the pattern is repeated.
            placeholder_char: The character shown in each open position.

        Raises:
            ValueError: The pattern is empty or not text, or the placeholder
                character is not one character.
        """
        Check.text("mask", mask)
        if placeholder_char is not None:
            Check.character("placeholder_char", placeholder_char)
        super().__init__(
            {"mask": mask, "repeat": repeat, "placeholderChar": placeholder_char}
        )


class MaskInput(forms.TextInput):
    """A text input whose mask options are written on it for the script."""

    kind = ""

    class Media:
        js = ["mvp_forms/imask.js"]

    def __init__(self, attrs=None, **options):
        """Keep the options that were stated and drop the rest.

        Args:
            attrs: HTML attributes for the input.
            **options: The mask's options, by IMask's own names.
        """
        super().__init__(attrs)
        self.options = {
            name: value for name, value in options.items() if value is not None
        }

    def mask_options(self):
        """Return what the script reads: the kind of mask and its options."""
        return {"kind": self.kind, **self.options}

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add the options to the input's attributes."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-imask"] = json.dumps(self.mask_options())
        return attrs


class PatternMaskInput(MaskInput):
    """A mask written as IMask's pattern text."""

    kind = "pattern"
    built_in_definitions = ("0", "a", "*")

    def __init__(
        self,
        mask,
        attrs=None,
        *,
        definitions=None,
        blocks=None,
        lazy=None,
        placeholder_char=None,
        overwrite=None,
        eager=None,
        display_char=None,
    ):
        """State the pattern and its options.

        Args:
            mask: The pattern, in IMask's pattern text.
            attrs: HTML attributes for the input.
            definitions: A character and the regular expression it stands for,
                written in JavaScript's dialect.
            blocks: A name and the block it stands for, each a ``RangeBlock``,
                an ``EnumBlock`` or a ``PatternBlock``.
            lazy: ``False`` shows the placeholder always.
            placeholder_char: The character shown in each open position, or a
                mapping from a definition's character to the character shown
                for it.
            overwrite: ``True`` has typing replace what is there, and
                ``"shift"`` has it replace and shift the rest.
            eager: ``True`` fills fixed characters in ahead of the cursor, and
                ``"append"`` or ``"remove"`` does so in one direction only.
            display_char: The character shown in place of what was typed.

        Raises:
            ValueError: An option holds a value that cannot be right. The
                message names the option.
        """
        Check.text("mask", mask)
        if placeholder_char is not None and not isinstance(placeholder_char, Mapping):
            Check.character("placeholder_char", placeholder_char)
        if display_char is not None:
            Check.character("display_char", display_char)
        if overwrite is not None:
            Check.one_of("overwrite", overwrite, (True, False, "shift"))
        if eager is not None:
            Check.one_of("eager", eager, (True, False, "append", "remove"))
        super().__init__(
            attrs,
            mask=mask,
            definitions=self.write_definitions(definitions, placeholder_char),
            blocks=self.write_blocks(blocks),
            lazy=lazy,
            placeholderChar=(
                None if isinstance(placeholder_char, Mapping) else placeholder_char
            ),
            overwrite=overwrite,
            eager=eager,
            displayChar=display_char,
        )

    def write_definitions(self, definitions, placeholder_char):
        """Return the definitions as the script reads them.

        Args:
            definitions: The developer's definitions, or ``None``.
            placeholder_char: A mapping from a definition's character to the
                character shown for it, or anything else.

        Returns:
            A mapping from a character to its expression, or to an object with
            the expression and the placeholder character where one is stated,
            or ``None`` when no definition is.

        Raises:
            ValueError: A definition is not one character and text, or a
                placeholder character is stated for a character no definition
                has.
        """
        written = {}
        for char, source in (definitions or {}).items():
            Check.character("definitions", char)
            Check.of_type("definitions", source, str, "an expression as text")
            written[char] = source
        if isinstance(placeholder_char, Mapping):
            for char, shown in placeholder_char.items():
                if char not in written and char not in self.built_in_definitions:
                    raise ValueError(
                        f"placeholder_char names {char!r}, which is not a definition."
                    )
                Check.character("placeholder_char", shown)
                source = written.get(char)
                written[char] = {
                    **({"mask": source} if source is not None else {}),
                    "placeholderChar": shown,
                }
        return written or None

    def write_blocks(self, blocks):
        """Return the blocks as the script reads them.

        Args:
            blocks: A mapping from a name to a block, or ``None``.

        Returns:
            A mapping from a name to the block's options, or ``None``.

        Raises:
            ValueError: ``blocks`` is not a mapping, or holds a name that is not
                text or something that is not one of the three block classes.
        """
        if blocks is None:
            return None
        Check.of_type("blocks", blocks, Mapping, "a mapping from a name to a block")
        for name, block in blocks.items():
            Check.text("blocks", name)
            Check.of_type(
                "blocks",
                block,
                (RangeBlock, EnumBlock, PatternBlock),
                f"a RangeBlock, an EnumBlock or a PatternBlock, for {name!r}",
            )
        return {name: block.mask_options() for name, block in blocks.items()}


class RegexMaskInput(MaskInput):
    """A mask that accepts a character only while the value still matches."""

    kind = "regex"
    javascript_flags = "dgimsuvy"

    def __init__(self, mask, attrs=None, *, flags=None):
        """State the expression and its flags.

        Python never compiles the expression. IMask runs it in the browser, in
        JavaScript's dialect.

        Args:
            mask: The expression, as text, in JavaScript's dialect.
            attrs: HTML attributes for the input.
            flags: The expression's flags, such as ``"i"``.

        Raises:
            ValueError: The expression is empty or not text, or a flag is one
                JavaScript does not have. The message names the option.
        """
        Check.text("mask", mask)
        if flags is not None:
            Check.of_type("flags", flags, str, "text")
            for flag in flags:
                if flag not in self.javascript_flags:
                    raise ValueError(
                        f"flags holds {flag!r}, which is not one of "
                        f"{self.javascript_flags!r}."
                    )
        super().__init__(attrs, mask=mask, flags=flags)


class NumberMaskInput(MaskInput):
    """A mask that formats a number, and hands the field a plain one."""

    kind = "number"
    default_radix = ","

    def __init__(
        self,
        attrs=None,
        *,
        scale=None,
        thousands_separator=None,
        radix=None,
        map_to_radix=None,
        pad_fractional_zeros=None,
        normalize_zeros=None,
        min_value=None,
        max_value=None,
        autofix=None,
    ):
        """State how the number is shown and bounded.

        Where the thousands separator and the decimal mark are not stated they
        are IMask's own: no separator, and a comma.

        Args:
            attrs: HTML attributes for the input. An ``inputmode`` stated here
                replaces the one the widget chooses.
            scale: The number of decimal places.
            thousands_separator: The character between groups of three digits,
                or an empty string for none.
            radix: The decimal mark.
            map_to_radix: A list of other characters to read as the decimal
                mark.
            pad_fractional_zeros: Pad the decimal places with zeros.
            normalize_zeros: Trim needless zeros.
            min_value: The smallest value, an ``int``, a ``float`` or a
                ``Decimal``.
            max_value: The largest value, of the same kinds.
            autofix: Correct a value outside the bounds to the nearest one.

        Raises:
            ValueError: An option holds a value that cannot be right. The
                message names the option.
        """
        if scale is not None:
            Check.of_type("scale", scale, int, "a whole number")
            if scale < 0:
                raise ValueError(f"scale must not be negative, not {scale!r}.")
        if radix is not None:
            Check.character("radix", radix)
        if thousands_separator is not None:
            Check.separator("thousands_separator", thousands_separator)
            if thousands_separator == (radix or self.default_radix):
                raise ValueError(
                    "thousands_separator must not be the decimal mark, "
                    f"{radix or self.default_radix!r}."
                )
        if map_to_radix is not None:
            Check.of_type("map_to_radix", map_to_radix, list | tuple, "a list")
            for each in map_to_radix:
                Check.character("map_to_radix", each)
        for option, value in (("min_value", min_value), ("max_value", max_value)):
            if value is not None:
                Check.number(option, value)
        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValueError(
                "min_value must not be above max_value, "
                f"not {min_value!r} and {max_value!r}."
            )
        self.thousands_separator = thousands_separator or ""
        self.radix = radix or self.default_radix
        super().__init__(
            {"inputmode": "numeric" if scale == 0 else "decimal", **(attrs or {})},
            scale=scale,
            thousandsSeparator=thousands_separator,
            radix=radix,
            mapToRadix=None if map_to_radix is None else list(map_to_radix),
            padFractionalZeros=pad_fractional_zeros,
            normalizeZeros=normalize_zeros,
            min=self.write_bound(min_value),
            max=self.write_bound(max_value),
            autofix=autofix,
        )

    @staticmethod
    def write_bound(bound):
        """Return a bound as a number JSON can write.

        Args:
            bound: An ``int``, a ``float``, a ``Decimal`` or ``None``.

        Returns:
            The bound, with a ``Decimal`` as a ``float``.
        """
        return float(bound) if isinstance(bound, Decimal) else bound

    def value_from_datadict(self, data, files, name):
        """Return the number with no thousands separator and a full stop."""
        value = super().value_from_datadict(data, files, name)
        if not value or not isinstance(value, str):
            return value
        if self.thousands_separator:
            value = value.replace(self.thousands_separator, "")
        return value.replace(self.radix, ".")

    def format_value(self, value):
        """Write the number with the decimal mark and no thousands separator.

        The number is not localised, since the widget's own options say how it
        is written. IMask adds the separators, and without IMask the text reads
        back as the same number.
        """
        if value is None or value == "":
            return None
        if isinstance(value, Decimal | float):
            value = format(Decimal(str(value)), "f")
        return str(value).replace(".", self.radix)


class DynamicMaskInput(MaskInput):
    """A list of masks, from which IMask applies the one that fits best."""

    kind = "dynamic"

    def __init__(self, masks, attrs=None):
        """State the masks, in order.

        IMask applies the mask that takes the most of what has been typed, and
        the earlier one where two take the same. Only each mask's options are
        used. Its ``attrs`` and the way it writes a number are not.

        Args:
            masks: A list of ``PatternMaskInput``, ``RegexMaskInput`` and
                ``NumberMaskInput`` widgets.
            attrs: HTML attributes for the input.

        Raises:
            ValueError: The list is empty, is not a list, or holds something
                other than one of the three widgets. The message names the
                option.
        """
        Check.of_type("masks", masks, list | tuple, "a list of mask widgets")
        if not masks:
            raise ValueError("masks must hold at least one mask.")
        for each in masks:
            Check.of_type(
                "masks",
                each,
                (PatternMaskInput, RegexMaskInput, NumberMaskInput),
                "a PatternMaskInput, a RegexMaskInput or a NumberMaskInput, "
                f"for each mask in the list, not {each!r}",
            )
        super().__init__(attrs, mask=[each.mask_options() for each in masks])
