"""The themes daisyUI ships, read from the stylesheet the suite pins."""

import functools
import re
from dataclasses import dataclass
from pathlib import Path

from tests.legibility.colours import Colour

THEMES_CSS = Path(__file__).parent.parent / "data" / "daisyui-themes.css"
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RULE = re.compile(r"(?P<selector>[^{}]+)\{(?P<body>[^{}]*)\}")
NAME = re.compile(r"\[data-theme=(?P<name>[\w-]+)\]")
SCHEME = re.compile(r"color-scheme:\s*(?P<scheme>light|dark)")
COLOUR = re.compile(r"--color-(?P<name>[\w-]+):\s*(?P<value>oklch\([^)]*\))")
VERSION = re.compile(r"daisyUI\s+(?P<version>\d+(?:\.\d+)+)")
COLOURS = frozenset(
    {
        "base-100",
        "base-200",
        "base-300",
        "base-content",
        *(
            f"{name}{suffix}"
            for name in (
                "neutral",
                "primary",
                "secondary",
                "accent",
                "info",
                "success",
                "warning",
                "error",
            )
            for suffix in ("", "-content")
        ),
    }
)


@dataclass(frozen=True)
class Theme:
    """One daisyUI theme.

    Args:
        name: The theme's name, as in `data-theme`.
        scheme: `"light"` or `"dark"`.
        colours: Each colour by daisyUI's name without the `--color-` prefix.
    """

    name: str
    scheme: str
    colours: dict[str, Colour]


class Themes:
    """The themes of a daisyUI stylesheet."""

    @classmethod
    def read(cls, text: str) -> tuple[Theme, ...]:
        """Read the themes of a stylesheet shaped like daisyUI's `themes.css`.

        A rule with no `[data-theme=...]` selector is not a theme.

        Args:
            text: The stylesheet.

        Returns:
            The themes, in the order the stylesheet gives them.

        Raises:
            ValueError: A theme states no colour scheme or lacks one of the colours.
        """
        themes = []
        for rule in RULE.finditer(COMMENT.sub("", text)):
            named = NAME.search(rule["selector"])
            if named is None:
                continue
            name = named["name"]
            scheme = SCHEME.search(rule["body"])
            if scheme is None:
                raise ValueError(f"theme {name} has no color-scheme")
            colours = {
                found["name"]: Colour.parse(found["value"])
                for found in COLOUR.finditer(rule["body"])
            }
            missing = COLOURS - set(colours)
            if missing:
                raise ValueError(f"theme {name} lacks {', '.join(sorted(missing))}")
            themes.append(Theme(name, scheme["scheme"], colours))
        return tuple(themes)

    @classmethod
    @functools.cache
    def shipped(cls) -> tuple[Theme, ...]:
        """Read the themes of the pinned stylesheet, `tests/data/daisyui-themes.css`.

        Returns:
            The shipped themes.
        """
        return cls.read(THEMES_CSS.read_text())

    @classmethod
    def named(cls, name: str) -> Theme:
        """Find a shipped theme by its name.

        Args:
            name: The theme's name.

        Returns:
            The theme.

        Raises:
            KeyError: No shipped theme has that name.
        """
        for theme in cls.shipped():
            if theme.name == name:
                return theme
        raise KeyError(name)

    @classmethod
    def version(cls, text: str) -> str:
        """Read the daisyUI version a file names in its first lines.

        Args:
            text: A stylesheet with daisyUI's banner, or the header of the class list.

        Returns:
            The version, such as `5.7.47`.

        Raises:
            ValueError: The text names no version.
        """
        found = VERSION.search(text)
        if found is None:
            raise ValueError("no daisyUI version in the text")
        return found["version"]
