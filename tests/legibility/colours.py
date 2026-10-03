"""The colour maths: daisyUI's OKLCH values in, WCAG 2.2 contrast ratios out."""

import math
import re
from dataclasses import dataclass, replace

OKLCH = re.compile(
    r"oklch\(\s*(?P<lightness>\d*\.?\d+)(?P<percent>%?)\s+(?P<chroma>\d*\.?\d+)"
    r"\s+(?P<hue>\d*\.?\d+)(?:deg)?\s*\)"
)


@dataclass(frozen=True)
class Colour:
    """A colour in OKLab with an alpha, which is what daisyUI's values are mixed in.

    Args:
        lightness: OKLab lightness, 0 to 1.
        a: OKLab green-red axis.
        b: OKLab blue-yellow axis.
        alpha: Opacity, 0 to 1.
    """

    lightness: float
    a: float
    b: float
    alpha: float = 1.0

    # Bjorn Ottosson's published OKLab matrices.
    LMS_FROM_OKLAB = (
        (1.0, 0.3963377774, 0.2158037573),
        (1.0, -0.1055613458, -0.0638541728),
        (1.0, -0.0894841775, -1.2914855480),
    )
    RGB_FROM_LMS = (
        (4.0767416621, -3.3077115913, 0.2309699292),
        (-1.2684380046, 2.6097574011, -0.3413193965),
        (-0.0041960863, -0.7034186147, 1.7076147010),
    )
    LMS_FROM_RGB = (
        (0.4122214708, 0.5363325363, 0.0514459929),
        (0.2119034982, 0.6806995451, 0.1073969566),
        (0.0883024619, 0.2817188376, 0.6299787005),
    )
    OKLAB_FROM_LMS = (
        (0.2104542553, 0.7936177850, -0.0040720468),
        (1.9779984951, -2.4285922050, 0.4505937099),
        (0.0259040371, 0.7827717662, -0.8086757660),
    )
    WEIGHTS = (0.2126, 0.7152, 0.0722)

    @classmethod
    def parse(cls, text: str) -> "Colour":
        """Read a colour written as daisyUI writes it, `oklch(L% C H)`.

        Args:
            text: The CSS value. The percent sign on the lightness is optional; without
                it the lightness is a fraction of one.

        Returns:
            The colour, opaque.

        Raises:
            ValueError: The text is not an `oklch(...)` value.
        """
        found = OKLCH.fullmatch(text.strip())
        if found is None:
            raise ValueError(f"not an oklch() colour: {text!r}")
        lightness = float(found["lightness"])
        if found["percent"]:
            lightness /= 100
        hue = math.radians(float(found["hue"]))
        chroma = float(found["chroma"])
        return cls(lightness, chroma * math.cos(hue), chroma * math.sin(hue))

    @classmethod
    def from_rgb(cls, red: float, green: float, blue: float) -> "Colour":
        """Build an opaque colour from gamma-encoded sRGB channels.

        Args:
            red: Red, 0 to 1.
            green: Green, 0 to 1.
            blue: Blue, 0 to 1.

        Returns:
            The same colour in OKLab.
        """
        linear = [cls.decode(channel) for channel in (red, green, blue)]
        lms = [
            sum(w * c for w, c in zip(row, linear, strict=True))
            for row in cls.LMS_FROM_RGB
        ]
        root = [math.cbrt(value) for value in lms]
        lightness, a, b = (
            sum(w * c for w, c in zip(row, root, strict=True))
            for row in cls.OKLAB_FROM_LMS
        )
        return cls(lightness, a, b)

    @staticmethod
    def decode(channel: float) -> float:
        """Turn a gamma-encoded sRGB channel into a linear one.

        Args:
            channel: The encoded channel, 0 to 1.

        Returns:
            The linear channel.
        """
        if abs(channel) <= 0.04045:
            return channel / 12.92
        return math.copysign(((abs(channel) + 0.055) / 1.055) ** 2.4, channel)

    @staticmethod
    def encode(channel: float) -> float:
        """Turn a linear sRGB channel into a gamma-encoded one.

        Args:
            channel: The linear channel, 0 to 1.

        Returns:
            The encoded channel.
        """
        if abs(channel) <= 0.0031308:
            return channel * 12.92
        return math.copysign(1.055 * abs(channel) ** (1 / 2.4) - 0.055, channel)

    def linear(self, clip: bool = True) -> tuple[float, float, float]:
        """Convert to linear sRGB.

        Args:
            clip: Clip each channel to the gamut, as browsers do when they paint.

        Returns:
            Red, green and blue, each from 0 to 1 when clipped.
        """
        lms = [
            (self.lightness + row[1] * self.a + row[2] * self.b) ** 3
            for row in self.LMS_FROM_OKLAB
        ]
        red, green, blue = (
            sum(w * c for w, c in zip(row, lms, strict=True))
            for row in self.RGB_FROM_LMS
        )
        if clip:
            return (
                min(max(red, 0.0), 1.0),
                min(max(green, 0.0), 1.0),
                min(max(blue, 0.0), 1.0),
            )
        return red, green, blue

    def rgb(self, clip: bool = True) -> tuple[float, float, float]:
        """Convert to gamma-encoded sRGB.

        Args:
            clip: Clip each channel to the gamut before encoding it.

        Returns:
            Red, green and blue, each from 0 to 1 when clipped.
        """
        red, green, blue = (self.encode(channel) for channel in self.linear(clip))
        return red, green, blue

    def srgb(self) -> tuple[int, int, int]:
        """Convert to the 0 to 255 values a browser paints.

        Returns:
            Red, green and blue, rounded.
        """
        red, green, blue = (round(channel * 255) for channel in self.rgb())
        return red, green, blue

    def mixed(self, other: "Colour", share: float) -> "Colour":
        """Mix with another colour in OKLab, as `color-mix(in oklab, ...)` does.

        Args:
            other: The colour that makes up the rest.
            share: How much of this colour, 0 to 1. The other gets what is left.

        Returns:
            The mixed colour.
        """
        rest = 1 - share
        return Colour(
            self.lightness * share + other.lightness * rest,
            self.a * share + other.a * rest,
            self.b * share + other.b * rest,
            self.alpha * share + other.alpha * rest,
        )

    def faded(self, share: float) -> "Colour":
        """Keep a share of the opacity, which is what mixing with `transparent` does.

        Args:
            share: The share of the opacity to keep, 0 to 1.

        Returns:
            The same colour, more see-through.
        """
        return replace(self, alpha=self.alpha * share)

    def over(self, surface: "Colour") -> "Colour":
        """Lay this colour on an opaque one, compositing in gamma-encoded sRGB.

        Args:
            surface: The colour behind this one. Must be opaque.

        Returns:
            The opaque colour that results.

        Raises:
            ValueError: The surface is itself see-through.
        """
        if surface.alpha < 1:
            raise ValueError("a see-through colour needs an opaque surface")
        # A browser composites before it clips, so a value outside the gamut counts.
        front = self.rgb(clip=False)
        back = surface.rgb()
        red, green, blue = (
            f * self.alpha + b * (1 - self.alpha)
            for f, b in zip(front, back, strict=True)
        )
        return Colour.from_rgb(red, green, blue)

    def luminance(self) -> float:
        """Calculate WCAG's relative luminance, ignoring any alpha.

        Returns:
            The luminance, 0 to 1.
        """
        return sum(w * c for w, c in zip(self.WEIGHTS, self.linear(), strict=True))

    def contrast(self, surface: "Colour") -> float:
        """Calculate WCAG's contrast ratio against the surface behind this colour.

        Args:
            surface: The opaque colour behind this one.

        Returns:
            The ratio, from 1 to 21. A see-through colour is composited on the surface
            first.

        Raises:
            ValueError: The surface is see-through.
        """
        if surface.alpha < 1:
            raise ValueError("the surface must be opaque")
        front = self.over(surface) if self.alpha < 1 else self
        lighter, darker = sorted((front.luminance(), surface.luminance()), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)
