"""Inks, pairings and measurements: what a person has to make out, and where."""

from dataclasses import dataclass

from tests.legibility.colours import Colour
from tests.legibility.themes import Theme


@dataclass(frozen=True)
class Ink:
    """A colour stated in a theme's own names, so it means the same under every theme.

    An ink is a named colour, or one built from others with `faded`, `mixed` and `over`.
    Inks are frozen and compare by value.

    Args:
        name: The theme colour's name without the `--color-` prefix, such as
            `base-content`. Empty for an ink built from others.
        base: The ink an ink built from others starts from.
        other: The ink a mixed ink is mixed with.
        share: The share of the base kept by a faded ink, or mixed in by a mixed one.
        surface: The ink a see-through ink is laid over.
    """

    name: str = ""
    base: "Ink | None" = None
    other: "Ink | None" = None
    share: float = 1.0
    surface: "Ink | None" = None

    def faded(self, share: float) -> "Ink":
        """Keep a share of this ink's opacity.

        Args:
            share: The share to keep, 0 to 1.

        Returns:
            The ink at that alpha. Fading a faded ink multiplies the shares.
        """
        if self.base and not (self.other or self.surface):
            return Ink(base=self.base, share=round(self.share * share, 6))
        return Ink(base=self, share=round(share, 6))

    def mixed(self, other: "Ink", share: float) -> "Ink":
        """Mix this ink with another in OKLab.

        Args:
            other: The ink that makes up the rest.
            share: How much of this ink, 0 to 1.

        Returns:
            The mixed ink.
        """
        return Ink(base=self, other=other, share=round(share, 6))

    def over(self, surface: "Ink") -> "Ink":
        """Lay a see-through ink on a surface, which makes it opaque.

        Args:
            surface: The opaque ink behind this one.

        Returns:
            The composited ink.
        """
        return Ink(base=self, surface=surface)

    def resolve(self, theme: Theme) -> Colour:
        """Find the colour this ink means under a theme.

        Args:
            theme: The theme to resolve against.

        Returns:
            The colour.

        Raises:
            KeyError: The ink names a colour the theme does not have.
        """
        if self.base is None:
            return theme.colours[self.name]
        base = self.base.resolve(theme)
        if self.surface is not None:
            return base.over(self.surface.resolve(theme))
        if self.other is not None:
            return base.mixed(self.other.resolve(theme), self.share)
        return base.faded(self.share)

    @property
    def words(self) -> str:
        """Describe the ink for a reader of the README.

        Returns:
            Text built from names and shares, such as `` `base-content` at 60% ``.
        """
        if self.base is None:
            return f"`{self.name}`"
        if self.surface is not None:
            return f"{self.base.words} over {self.surface.words}"
        if self.other is not None:
            return f"{self.percent} {self.base.words} in {self.other.words}"
        return f"{self.base.words} at {self.percent}"

    @property
    def percent(self) -> str:
        """Write the share as a percentage.

        Returns:
            The share, rounded, with its percent sign.
        """
        return f"{round(self.share * 100)}%"


@dataclass(frozen=True)
class Pairing:
    """One thing a person has to make out, with the surface directly behind it.

    Args:
        part: One of `text`, `placeholder`, `border`, `mark` and `button text`.
        ink: The colour of the part.
        surface: The colour behind it.
        figure: The least contrast ratio the standard asks for.
    """

    part: str
    ink: Ink
    surface: Ink
    figure: float

    figures = {
        "text": 4.5,
        "placeholder": 4.5,
        "button text": 4.5,
        "border": 3.0,
        "mark": 3.0,
    }

    @classmethod
    def of(cls, part: str, ink: Ink, surface: Ink) -> "Pairing":
        """Build a pairing with the figure its part is held to.

        Args:
            part: One of `text`, `placeholder`, `border`, `mark` and `button text`.
            ink: The colour of the part.
            surface: The colour behind it.

        Returns:
            The pairing.

        Raises:
            ValueError: The part is not one of the five.
        """
        if part not in cls.figures:
            raise ValueError(f"not a part a person has to make out: {part!r}")
        return cls(part, ink, surface, cls.figures[part])

    @property
    def name(self) -> str:
        """Name the pairing by what is drawn and on what.

        Returns:
            The part, the ink's words and the surface's words.
        """
        return f"{self.part}, {self.ink.words} on {self.surface.words}"

    def ratio(self, theme: Theme) -> float:
        """Calculate the contrast ratio under a theme.

        Args:
            theme: The theme to calculate under.

        Returns:
            WCAG's ratio, from 1 to 21.
        """
        return self.ink.resolve(theme).contrast(self.surface.resolve(theme))

    def meets(self, theme: Theme) -> bool:
        """Tell whether the pairing reaches its figure under a theme.

        Args:
            theme: The theme to calculate under.

        Returns:
            Whether the ratio is at least the figure.
        """
        return self.ratio(theme) >= self.figure


@dataclass(frozen=True)
class Element:
    """The element a measurement came from.

    Args:
        tag: The tag name.
        id: The element's id, or empty.
        kind: What the element is, such as `input`, `checkbox` or `btn`.
    """

    tag: str
    id: str
    kind: str


@dataclass(frozen=True)
class Measurement:
    """A pairing read from one element of one drawn form state.

    Args:
        form_state: The name of the drawn state.
        element: The element it came from.
        pairing: What has to be made out.
        held: Whether it must meet its figure. False for the dimmed content of a
            disabled control, which is measured and reported only.
        own: Whether the ink is one the pack chose itself and a class could change,
            as against a control's own drawing, a placeholder or the developer's choice.
    """

    form_state: str
    element: Element
    pairing: Pairing
    held: bool
    own: bool
