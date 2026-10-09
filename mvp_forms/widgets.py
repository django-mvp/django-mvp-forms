"""Widgets that put an IMask input mask on a text input.

Each widget writes its options on the input as JSON in ``data-imask``, and the
script named in its media hands them to IMask. The host project loads IMask.
"""

import json

from django import forms


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
            definitions: A character and the regular expression it stands for.
            blocks: A name and the block it stands for, each a dict with a
                ``kind`` of ``range``, ``enum``, ``pattern`` or ``repeat``.
            lazy: ``False`` shows the placeholder always.
            placeholder_char: The character shown in each open position.
            overwrite: Typing replaces what is there.
            eager: Fixed characters are filled in ahead of the cursor.
            display_char: The character shown in place of what was typed.
        """
        super().__init__(
            attrs,
            mask=mask,
            definitions=definitions,
            blocks=blocks,
            lazy=lazy,
            placeholderChar=placeholder_char,
            overwrite=overwrite,
            eager=eager,
            displayChar=display_char,
        )


class RegexMaskInput(MaskInput):
    """A mask that accepts only what a JavaScript regular expression matches."""

    kind = "regex"

    def __init__(self, mask, attrs=None, *, flags=None):
        """State the expression and its flags.

        Args:
            mask: The expression, in JavaScript's dialect.
            attrs: HTML attributes for the input.
            flags: The expression's flags, such as ``"i"``.
        """
        super().__init__(attrs, mask=mask, flags=flags)


class NumberMaskInput(MaskInput):
    """A mask that formats a number, and hands the field a plain one."""

    kind = "number"

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
        min=None,
        max=None,
        autofix=None,
    ):
        """State how the number is shown and bounded.

        Args:
            attrs: HTML attributes for the input.
            scale: The number of decimal places.
            thousands_separator: The character between groups of three digits.
            radix: The decimal mark.
            map_to_radix: Other characters read as the decimal mark.
            pad_fractional_zeros: Pad the decimal places with zeros.
            normalize_zeros: Trim needless zeros.
            min: The smallest value.
            max: The largest value.
            autofix: Correct a value outside the bounds to the nearest one.
        """
        keypad = "numeric" if scale == 0 else "decimal"
        super().__init__(
            {"inputmode": keypad, **(attrs or {})},
            scale=scale,
            thousandsSeparator=thousands_separator,
            radix=radix,
            mapToRadix=map_to_radix,
            padFractionalZeros=pad_fractional_zeros,
            normalizeZeros=normalize_zeros,
            min=min,
            max=max,
            autofix=autofix,
        )

    def value_from_datadict(self, data, files, name):
        """Return the number with no thousands separator and a full stop."""
        value = super().value_from_datadict(data, files, name)
        if not value:
            return value
        separator = self.options.get("thousandsSeparator", "")
        if separator:
            value = value.replace(separator, "")
        return value.replace(self.options.get("radix", ","), ".")


class DynamicMaskInput(MaskInput):
    """A list of masks, from which IMask applies the best fit."""

    kind = "dynamic"

    def __init__(self, masks, attrs=None):
        """State the masks, in order.

        Args:
            masks: Mask widgets, each with its own options.
            attrs: HTML attributes for the input.
        """
        super().__init__(attrs, mask=[mask.mask_options() for mask in masks])
