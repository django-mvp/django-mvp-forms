"""Widgets for IMask input masks and for Tom Select controls.

Each mask widget writes its options on the input as JSON in ``data-imask``, and
the script named in its media hands them to IMask. A Tom Select widget writes its
settings on the select as JSON in ``data-tom-select``, and its script starts a
Tom Select control. The host project loads IMask and Tom Select.
"""

import datetime
import json
import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation

from django import forms
from django.utils.dates import MONTHS
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _


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


class CoordinateMaskInput(NumberMaskInput):
    """A decimal degree, typed with a full stop and an optional minus sign.

    The latitude and longitude fields state the number of decimal places and the
    bounds on the widget they are given. The bounds are checked by the script
    and never handed to IMask, which would change a value outside them.
    """

    kind = "coordinate"
    scale = 6
    min_value = None
    max_value = None

    def __init__(self, attrs=None):
        """Draw no ``inputmode``, unless ``attrs`` states one.

        The decimal keypad of a phone has no minus key, and offers a comma where
        the language's decimal mark is a comma.

        Args:
            attrs: HTML attributes for the input.
        """
        super().__init__(attrs, radix=".", thousands_separator="")
        if "inputmode" not in (attrs or {}):
            del self.attrs["inputmode"]

    def mask_options(self):
        """Return the kind of mask, its decimal places and the field's bounds."""
        bounds = {
            "min": self.write_bound(self.min_value),
            "max": self.write_bound(self.max_value),
        }
        return {
            "kind": self.kind,
            "scale": self.scale,
            **self.options,
            **{name: bound for name, bound in bounds.items() if bound is not None},
        }


class PointInput(forms.MultiWidget):
    """A latitude and a longitude as two masked inputs that make one point.

    Each input is drawn inside its own daisyUI ``input`` frame, a ``<label>``
    that shows the half's name before it. The point field states each half's
    bounds and the decimal places on the parts it is given.
    """

    template_name = "mvp_forms/widgets/point.html"
    number = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?"
    well_known_text = re.compile(
        rf"\s*(?:SRID\s*=\s*(\d+)\s*;\s*)?POINT\s*\(\s*({number})\s+({number})\s*\)\s*",
        re.IGNORECASE,
    )

    def __init__(self, attrs=None):
        """Build the latitude and the longitude parts.

        Args:
            attrs: HTML attributes for both parts.
        """
        parts = [
            CoordinateMaskInput({"aria-label": _("Latitude")}),
            CoordinateMaskInput({"aria-label": _("Longitude")}),
        ]
        super().__init__(parts, attrs)

    def get_context(self, name, value, attrs):
        """Move each part's classes onto the frame drawn around it.

        The frame is the daisyUI ``input``, so the size, colour, variant and
        error state the pack gives a part belong on it, not on the input inside.
        """
        context = super().get_context(name, value, attrs)
        for part in context["widget"]["subwidgets"]:
            part["frame_class"] = part["attrs"].pop("class", "")
            part["frame_name"] = part["attrs"].get("aria-label", "")
        return context

    def decompress(self, value):
        """Split a point into its latitude and longitude.

        Args:
            value: An object with ``x`` and ``y`` such as a GEOS point, WKT
                text, or a pair of ``(latitude, longitude)``.

        Returns:
            The latitude and the longitude as ``Decimal`` numbers, or two
            ``None`` for an empty value.

        Raises:
            ValueError: The point is in a spatial reference other than 4326, has
                a height, or is not a two-dimensional point.
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return [None, None]
        if isinstance(value, str):
            found = self.well_known_text.fullmatch(value)
            if not found:
                raise ValueError(
                    f"{value!r} is not a two-dimensional WKT point, such as "
                    "'SRID=4326;POINT(-0.1278 51.5074)'."
                )
            srid, longitude, latitude = found.groups()
            self.check_srid(int(srid) if srid else None)
        elif isinstance(value, list | tuple):
            if len(value) != 2:
                raise ValueError(
                    f"A pair holds a latitude and a longitude, not {value!r}."
                )
            latitude, longitude = value
        elif hasattr(value, "x") and hasattr(value, "y"):
            self.check_srid(getattr(value, "srid", None))
            if getattr(value, "z", None) is not None:
                raise ValueError(
                    "The point has a height, which the form has no input for."
                )
            latitude, longitude = value.y, value.x
        else:
            raise ValueError(f"{value!r} is not a point.")
        try:
            return [Decimal(str(latitude)), Decimal(str(longitude))]
        except InvalidOperation:
            raise ValueError(
                f"A point holds a latitude and a longitude, not {value!r}."
            ) from None

    @staticmethod
    def check_srid(srid):
        """Refuse a spatial reference whose numbers are not degrees of WGS84.

        Args:
            srid: The point's spatial reference identifier, or ``None``.

        Raises:
            ValueError: The identifier is neither ``None`` nor 4326.
        """
        if srid not in (None, 4326):
            raise ValueError(
                f"The point is in spatial reference {srid}, which is not "
                "latitude and longitude in degrees. Convert it to 4326 first."
            )


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


SHAPES = {"year": "YYYY", "month": "YYYY-MM", "day": "YYYY-MM-DD"}


class PartialDateMaskInput(MaskInput):
    """One text input masked as a year, a year and month, or a full date.

    The partial date field states its max_resolution and the earliest and
    latest dates on the widget it is given.
    """

    kind = "partial-date"
    max_resolution = "day"
    min_value = None
    max_value = None

    def __init__(self, attrs=None):
        """Ask a touch device for a numeric keypad.

        Args:
            attrs: HTML attributes for the input.
        """
        super().__init__({"inputmode": "numeric", **(attrs or {})})

    def mask_options(self):
        """Return the kind of mask and what the field accepts."""
        limits = {"min": self.min_value, "max": self.max_value}
        return {
            "kind": self.kind,
            "resolution": self.max_resolution,
            **{name: value for name, value in limits.items() if value},
        }

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Show the shape of the date the field accepts, unless attrs state one."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.setdefault("placeholder", SHAPES[self.max_resolution])
        return attrs


class PartialDateInput(forms.MultiWidget):
    """A year, a month and a day as three parts that make one ISO value.

    The year is typed. The partial date field states its max_resolution and
    the earliest and latest dates on the widget it is given.
    """

    template_name = "mvp_forms/widgets/partial_date.html"
    max_resolution = "day"
    min_value = None
    max_value = None

    class Media:
        js = ["mvp_forms/partial-date.js"]

    def __init__(self, attrs=None):
        """Build the parts.

        Args:
            attrs: HTML attributes for every part.
        """
        parts = {
            "year": self.year_part(),
            "month": forms.Select(
                {
                    "class": "join-item w-auto",
                    "aria-label": _("Month"),
                    "data-partial-date-part": "month",
                },
                choices=[
                    ("", _("Month")),
                    *((f"{number:02}", name) for number, name in MONTHS.items()),
                ],
            ),
            "day": forms.Select(
                {
                    "class": "join-item w-auto",
                    "aria-label": _("Day"),
                    "data-partial-date-part": "day",
                },
                choices=[
                    ("", _("Day")),
                    *((f"{number:02}", str(number)) for number in range(1, 32)),
                ],
            ),
        }
        super().__init__(parts, attrs)

    def year_part(self):
        """Return the part the year is entered in."""
        return forms.TextInput(
            {
                "class": "join-item w-24",
                "inputmode": "numeric",
                "maxlength": 4,
                "pattern": "[0-9]{4}",
                "placeholder": _("Year"),
                "aria-label": _("Year"),
                "data-partial-date-part": "year",
            }
        )

    def decompress(self, value):
        """Split ISO text, a Python date or the date of a datetime into its parts."""
        if not value:
            return ["", "", ""]
        if isinstance(value, datetime.datetime):
            value = value.date()
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        year, *rest = [*str(value).split("-"), "", ""][:3]
        return [year, *(part.zfill(2) if part else "" for part in rest)]

    def value_from_datadict(self, data, files, name):
        """Join what the parts hold, dropping empty parts from the right.

        A part holding a hyphen would be read as two, so the parts are returned
        as sent and the field refuses them.
        """
        parts = super().value_from_datadict(data, files, name)
        if any("-" in (part or "") for part in parts):
            return parts
        return "-".join((part or "").strip() for part in parts).rstrip("-")

    def get_context(self, name, value, attrs):
        """Draw the parts down to the max_resolution, with only the year required."""
        context = super().get_context(name, value, attrs)
        widget = context["widget"]
        names = ("year", "month", "day")
        widget["subwidgets"] = widget["subwidgets"][
            : names.index(self.max_resolution) + 1
        ]
        for part in widget["subwidgets"][1:]:
            part["attrs"].pop("required", None)
        widget["min_value"] = self.min_value
        widget["max_value"] = self.max_value
        return context


class PartialDateSelect(PartialDateInput):
    """A year, a month and a day as three selects that make one ISO value.

    The years on offer run from the field's earliest date to its latest. Where
    one is not stated, they reach a hundred years back from this year.
    """

    def year_part(self):
        """Return a select, whose years are listed when it is drawn."""
        return forms.Select(
            {
                "class": "join-item w-auto",
                "aria-label": _("Year"),
                "data-partial-date-part": "year",
            }
        )

    def years(self, held):
        """Return the years on offer, latest first, with the one held."""
        today = datetime.date.today().year
        last = int(self.max_value[:4]) if self.max_value else None
        first = int(self.min_value[:4]) if self.min_value else None
        if last is None:
            last = today if first is None or first <= today else first + 100
        if first is None:
            first = max(last - 100, 1)
        years = [f"{year:04}" for year in range(last, first - 1, -1)]
        if held and held not in years:
            years.insert(0, held)
        return years

    def get_context(self, name, value, attrs):
        """List the years before the parts are drawn."""
        held = value[0] if isinstance(value, list) else self.decompress(value)[0]
        self.widgets[0].choices = [
            ("", _("Year")),
            *((year, year) for year in self.years(held)),
        ]
        return super().get_context(name, value, attrs)


class TomSelect(forms.Select):
    """A single select the script turns into a Tom Select control.

    The select is drawn as Django draws it, holding every choice of its field.
    The attribute ``data-tom-select`` marks it for the script named in the
    media, and holds the settings stated as JSON.
    """

    class Media:
        js = ["mvp_forms/tomselect.js"]

    def __init__(self, attrs=None, choices=(), *, placeholder=None, clear_button=None):
        """Keep the settings that were stated.

        Args:
            attrs: HTML attributes for the select.
            choices: The choices to draw as options.
            placeholder: Text shown while the control holds no value. A lazy
                translation is read when the select is drawn.
            clear_button: ``True`` to add a button that empties the control.

        Raises:
            ValueError: A setting holds a value that cannot be right. The
                message names the setting.
        """
        if placeholder is not None and not isinstance(placeholder, Promise):
            Check.text("placeholder", placeholder)
        if clear_button is not None:
            Check.one_of("clear_button", clear_button, (True, False))
        super().__init__(attrs, choices)
        self.placeholder = placeholder
        self.clear_button = clear_button

    def control_settings(self):
        """Return the settings that were stated, under Tom Select's own names."""
        settings = {}
        if self.placeholder is not None:
            settings["placeholder"] = str(self.placeholder)
        if self.clear_button:
            settings["plugins"] = ["clear_button"]
        return settings

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add the settings to the select's attributes."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-tom-select"] = json.dumps(self.control_settings())
        return attrs


class TomSelectMultiple(TomSelect, forms.SelectMultiple):
    """A multiple select the script turns into a Tom Select control.

    It takes what ``TomSelect`` takes, and a button on each chosen value, the
    largest number of values that may be chosen, and a counted control: one that
    shows how many values are chosen in place of the values themselves, ticks
    each chosen option in its list and has its search box in the list.
    """

    def __init__(
        self,
        attrs=None,
        choices=(),
        *,
        placeholder=None,
        clear_button=None,
        remove_button=None,
        max_items=None,
        counted=None,
        none_text=None,
        count_text=None,
    ):
        """Keep the settings that were stated.

        Args:
            attrs: HTML attributes for the select.
            choices: The choices to draw as options.
            placeholder: Text shown while the control holds no value. A lazy
                translation is read when the select is drawn.
            clear_button: ``True`` to add a button that empties the control.
            remove_button: ``True`` to add a button to each chosen value.
            max_items: The largest number of values that may be chosen, a whole
                number above zero. ``1`` makes Tom Select draw the control as a
                single one, while the field still receives a list.
            counted: ``True`` to show a count in place of the chosen values.
            none_text: What a counted control shows while it holds no value.
            count_text: What a counted control shows after the number of values
                it holds.

        Raises:
            ValueError: A setting holds a value that cannot be right. The
                message names the setting.
        """
        if remove_button is not None:
            Check.one_of("remove_button", remove_button, (True, False))
        if max_items is not None:
            Check.whole_number("max_items", max_items)
            if max_items < 1:
                raise ValueError(f"max_items must be above zero, not {max_items!r}.")
        if counted is not None:
            Check.one_of("counted", counted, (True, False))
        if counted and remove_button:
            raise ValueError(
                "remove_button has no effect on a counted control, whose chosen "
                "values are not shown."
            )
        for option, text in (("none_text", none_text), ("count_text", count_text)):
            if text is None:
                continue
            if not counted:
                raise ValueError(f"{option} is used only with counted=True.")
            if not isinstance(text, Promise):
                Check.text(option, text)
        super().__init__(
            attrs, choices, placeholder=placeholder, clear_button=clear_button
        )
        self.remove_button = remove_button
        self.max_items = max_items
        self.counted = counted
        self.none_text = _("Nothing selected") if none_text is None else none_text
        self.count_text = _("selected") if count_text is None else count_text

    def control_settings(self):
        """Return the settings that were stated, under Tom Select's own names."""
        settings = super().control_settings()
        if self.remove_button:
            settings.setdefault("plugins", []).append("remove_button")
        if self.max_items is not None:
            settings["maxItems"] = self.max_items
        if self.counted:
            settings.setdefault("plugins", []).extend(
                ["checkbox_options", "dropdown_input"]
            )
        return settings

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add the words of a counted control, which the stylesheet draws."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        if self.counted:
            attrs["data-none-text"] = str(self.none_text)
            attrs["data-count-text"] = str(self.count_text)
        return attrs


class ImageInput(forms.ClearableFileInput):
    """A file input for an image that shows the image it holds.

    The stored image is drawn as a thumbnail, and a newly chosen file takes its
    place before the form is sent. Removing the stored image stays a checkbox,
    as it is for any clearable file.
    """

    template_name = "mvp_forms/widgets/image.html"
    clear_checkbox_label = _("Remove image")
    initial_text = _("Current image")

    class Media:
        js = ["mvp_forms/image-input.js"]

    def __init__(
        self,
        attrs=None,
        *,
        aspect_ratio=None,
        show_input=True,
        show_file_name=False,
        horizontal=False,
        align="middle",
        height=6,
    ):
        """Set how the image is shown.

        Args:
            attrs: The file input's attributes.
            aspect_ratio: The thumbnail's width over its height, such as ``1``,
                ``2`` or ``16 / 9``. The image fills a thumbnail of that shape.
                Without one the thumbnail is square and the image is shown
                whole inside it.
            show_input: ``False`` to leave out the file input, so that the
                thumbnail itself opens the file picker.
            show_file_name: ``True`` to name the stored file beside the image,
                as a link to it.
            horizontal: ``True`` to set the thumbnail beside the rest, where
                there is room, rather than above it.
            align: Where the rest sits beside a horizontal thumbnail:
                ``"top"``, ``"middle"`` or ``"bottom"``.
            height: The thumbnail's height in rem. Its width follows from the
                aspect ratio.

        Raises:
            ValueError: An option holds a value it cannot take.
        """
        if aspect_ratio is not None:
            Check.of_type("aspect_ratio", aspect_ratio, (int, float), "a number")
            if isinstance(aspect_ratio, bool) or aspect_ratio <= 0:
                raise ValueError(
                    f"aspect_ratio must be a number above zero, not {aspect_ratio!r}."
                )
        for option, value in (
            ("show_input", show_input),
            ("show_file_name", show_file_name),
            ("horizontal", horizontal),
        ):
            Check.one_of(option, value, (True, False))
        Check.one_of("align", align, ("top", "middle", "bottom"))
        Check.of_type("height", height, (int, float), "a number")
        if isinstance(height, bool) or height <= 0:
            raise ValueError(f"height must be a number above zero, not {height!r}.")
        super().__init__(attrs)
        self.align = align
        self.height = height
        self.aspect_ratio = aspect_ratio
        self.show_input = show_input
        self.show_file_name = show_file_name
        self.horizontal = horizontal

    def get_context(self, name, value, attrs):
        """Add the options and the stored file's name without its folders."""
        context = super().get_context(name, value, attrs)
        widget = context["widget"]
        widget["aspect_ratio"] = self.aspect_ratio
        widget["show_input"] = self.show_input
        widget["show_file_name"] = self.show_file_name
        widget["horizontal"] = self.horizontal
        widget["align"] = self.align
        widget["height"] = self.height
        widget["ratio"] = self.aspect_ratio or 1
        widget["invalid"] = widget["attrs"].get("aria-invalid") == "true"
        if widget["is_initial"]:
            widget["file_name"] = str(value.name).rsplit("/", 1)[-1]
        return context
