"""Reads the stylesheet the pack ships for django-tomselect into rules."""

import re
from pathlib import Path
from typing import NamedTuple

import mvp_forms
from tests.legibility.pairings import Ink

STYLESHEET = Path(mvp_forms.__file__).parent / "static" / "mvp_forms" / "tomselect.css"
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
CONTROL = re.compile(r"(?:div)?\.ts-(?:wrapper|dropdown)(?![\w-])")
# The rules that reach outside a control, each matched whole after any `:root `.
NAMED_EXCEPTIONS = frozenset(
    {
        '[id$="_sr_status"].visually-hidden',
        ".modal-box:has(.ts-wrapper.dropdown-active)",
        ".overflow-x-auto:has(.ts-wrapper.dropdown-active)",
    }
)
COLOUR_FUNCTION = re.compile(
    r"(?<![\w-])(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color|light-dark)\("
)
HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}(?![\w-])")
CUSTOM_PROPERTY = re.compile(r"--[\w-]+")
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")
WORD = re.compile(r"[a-zA-Z][\w-]*")
NAMED_COLOURS = frozenset(
    re.findall(
        r"\w+",
        """
    aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond
    blue blueviolet brown burlywood cadetblue chartreuse chocolate coral
    cornflowerblue cornsilk crimson cyan darkblue darkcyan darkgoldenrod darkgray
    darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid
    darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey
    darkturquoise darkviolet deeppink deepskyblue dimgray dimgrey dodgerblue
    firebrick floralwhite forestgreen fuchsia gainsboro ghostwhite gold goldenrod
    gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
    lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
    lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon
    lightseagreen lightskyblue lightslategray lightslategrey lightsteelblue
    lightyellow lime limegreen linen magenta maroon mediumaquamarine mediumblue
    mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen
    mediumturquoise mediumvioletred midnightblue mintcream mistyrose moccasin
    navajowhite navy oldlace olive olivedrab orange orangered orchid palegoldenrod
    palegreen paleturquoise palevioletred papayawhip peachpuff peru pink plum
    powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon
    sandybrown seagreen seashell sienna silver skyblue slateblue slategray slategrey
    snow springgreen steelblue tan teal thistle tomato turquoise violet wheat white
    whitesmoke yellow yellowgreen
""",
    )
)
KEYFRAMES = "@keyframes"
THEME_COLOUR = re.compile(r"var\(--color-(?P<name>[\w-]+)\)")
COLOUR_MIX = re.compile(
    r"color-mix\(\s*in oklab,\s*(?P<first>.+?)\s+(?P<share>[\d.]+)%\s*,"
    r"\s*(?P<second>.+?)\s*\)"
)
SURROUNDING_INK = {"inherit", "currentcolor"}
OPENERS = {"(": ")", "[": "]"}
QUOTES = "\"'"


class UnreadRule(Exception):
    """The stylesheet holds an at-rule that ``Stylesheet`` cannot read.

    Teach ``Stylesheet.read_blocks`` the at-rule before the stylesheet uses it,
    so that a rule inside it cannot go unchecked.
    """


class Declaration(NamedTuple):
    """One property and its value.

    Args:
        name: The property's name.
        value: The value as written, with ``!important`` removed.
        important: Whether the value was marked ``!important``.
    """

    name: str
    value: str
    important: bool


class Rule(NamedTuple):
    """A selector list and the declarations it applies.

    Args:
        selectors: Each selector of the list, with its whitespace collapsed.
        declarations: The declarations, in the order written.
    """

    selectors: list[str]
    declarations: list[Declaration]


class Stylesheet:
    """The pack's stylesheet read into rules, with its comments removed.

    Args:
        text: The text of the stylesheet. By default, the file the pack ships.

    Attributes:
        rules: Every rule outside an ``@keyframes`` block, in order.
        keyframes: The frames of each ``@keyframes`` block, by its name.
    """

    def __init__(self, text: str | None = None) -> None:
        source = STYLESHEET.read_text() if text is None else text
        self.rules: list[Rule] = []
        self.keyframes: dict[str, list[Rule]] = {}
        for prelude, body in self.read_blocks(COMMENT.sub("", source)):
            if prelude.startswith(KEYFRAMES):
                name = prelude.removeprefix(KEYFRAMES).strip()
                self.keyframes[name] = [
                    self.read_rule(frame, contents)
                    for frame, contents in self.read_blocks(body)
                ]
            elif prelude.startswith("@"):
                raise UnreadRule(prelude)
            else:
                self.rules.append(self.read_rule(prelude, body))

    def selectors(self) -> list[str]:
        """Return every selector of every rule, one at a time.

        Returns:
            The selectors, in order, not counting the frames of ``@keyframes``.
        """
        return [selector for rule in self.rules for selector in rule.selectors]

    def declarations(self) -> list[Declaration]:
        """Return every declaration, including those inside ``@keyframes``.

        Returns:
            The declarations of every rule, then those of every frame.
        """
        frames = [frame for group in self.keyframes.values() for frame in group]
        return [
            declaration
            for rule in [*self.rules, *frames]
            for declaration in rule.declarations
        ]

    def outside_a_control(self) -> list[str]:
        """Return the selectors that begin outside a Tom Select control.

        A selector is inside a control when, after an optional ``:root``, it
        begins at ``.ts-wrapper``, ``.ts-dropdown`` or ``div.ts-dropdown``. The
        three rules that have to reach outside a control are matched whole.

        Returns:
            The selectors that are neither inside a control nor one of those
            three, in order.
        """
        outside = []
        for selector in self.selectors():
            start = selector.removeprefix(":root ")
            if start in NAMED_EXCEPTIONS or CONTROL.match(start):
                continue
            outside.append(selector)
        return outside

    def colours(self) -> list[Declaration]:
        """Return the declarations that name a colour of the stylesheet's own.

        A colour comes from the theme, as ``var(--color-...)`` alone or inside
        ``color-mix``. A hex colour, a colour function and a named colour do not,
        except ``transparent`` and ``currentColor``.

        Returns:
            The declarations whose value writes such a colour, in order.
        """
        found = []
        for declaration in self.declarations():
            value = CUSTOM_PROPERTY.sub("", QUOTED.sub("", declaration.value))
            words = {word.lower() for word in WORD.findall(value)}
            if (
                HEX_COLOUR.search(value)
                or COLOUR_FUNCTION.search(value)
                or words & NAMED_COLOURS
            ):
                found.append(declaration)
        return found

    def declared(self, selector: str, name: str) -> str:
        """Return the value a selector's rule gives a property.

        Args:
            selector: One selector of the rule, exactly as the stylesheet writes it.
            name: The property.

        Returns:
            The value of the last rule in the file that has the selector among its
            own and declares the property, without ``!important``.

        Raises:
            KeyError: No rule with the selector declares the property.
        """
        for rule in reversed(self.rules):
            if selector not in rule.selectors:
                continue
            for declaration in reversed(rule.declarations):
                if declaration.name == name:
                    return declaration.value
        raise KeyError(f"{selector} declares no {name}")

    def number(self, selector: str, name: str) -> float:
        """Return a property a selector's rule gives as a plain number.

        Args:
            selector: One selector of the rule, exactly as the stylesheet writes it.
            name: The property, such as ``opacity``.

        Returns:
            The number.

        Raises:
            KeyError: No rule with the selector declares the property.
        """
        return float(self.declared(selector, name))

    def ink(self, selector: str, name: str, inherited: Ink | None = None) -> Ink:
        """Return the theme colour a selector's rule gives a property.

        A colour is ``var(--color-...)``, or ``color-mix(in oklab, ...)`` of such
        colours and ``transparent``. A value that takes the colour of the
        surrounding text, whether ``inherit`` or a shorthand ending in
        ``currentColor``, is the ink the caller says is inherited.

        Args:
            selector: One selector of the rule, exactly as the stylesheet writes it.
            name: The property.
            inherited: The ink the surrounding text has, for a value that takes it.

        Returns:
            The ink, in the theme's own names.

        Raises:
            KeyError: No rule with the selector declares the property.
            ValueError: The value is not a colour taken from the theme, or takes
                the surrounding ink when none was given.
        """
        return self.read_ink(self.declared(selector, name), inherited)

    def read_ink(self, value: str, inherited: Ink | None) -> Ink:
        """Read one colour value into an ink.

        Args:
            value: The value as written.
            inherited: The ink the surrounding text has, if known.

        Returns:
            The ink.

        Raises:
            ValueError: The value is not a colour taken from the theme, or takes
                the surrounding ink when none was given.
        """
        text = value.strip()
        if text.split()[-1].lower() in SURROUNDING_INK:
            if inherited is None:
                raise ValueError(f"{value!r} takes the surrounding ink")
            return inherited
        if found := THEME_COLOUR.fullmatch(text):
            return Ink(found["name"])
        if found := COLOUR_MIX.fullmatch(text):
            first = self.read_ink(found["first"], inherited)
            share = float(found["share"]) / 100
            if found["second"] == "transparent":
                return first.faded(share)
            return first.mixed(self.read_ink(found["second"], inherited), share)
        raise ValueError(f"{value!r} is not a colour taken from the theme")

    def read_rule(self, prelude: str, body: str) -> Rule:
        """Read one rule from the text before its braces and the text inside them.

        Args:
            prelude: The selector list.
            body: The declarations.

        Returns:
            The rule.
        """
        declarations = []
        for text in self.split(body, ";"):
            if ":" not in text:
                continue
            name, value = text.split(":", 1)
            important = bool(re.search(r"!\s*important\s*$", value))
            value = re.sub(r"\s*!\s*important\s*$", "", value)
            declarations.append(Declaration(name.strip(), value.strip(), important))
        selectors = [
            re.sub(r"\s+", " ", selector.strip())
            for selector in self.split(prelude, ",")
        ]
        return Rule(selectors, declarations)

    def read_blocks(self, text: str) -> list[tuple[str, str]]:
        """Split text into the blocks that sit at its top level.

        Args:
            text: Stylesheet text without comments.

        Returns:
            The text before each block's opening brace and the text between its
            braces, in order.
        """
        blocks = []
        depth = 0
        quote = ""
        start = body_start = 0
        prelude = ""
        for index, char in enumerate(text):
            if quote:
                quote = "" if char == quote else quote
            elif char in QUOTES:
                quote = char
            elif char == "{":
                if depth == 0:
                    prelude = text[start:index].strip()
                    body_start = index + 1
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    blocks.append((prelude, text[body_start:index]))
                    start = index + 1
        return blocks

    def split(self, text: str, separator: str) -> list[str]:
        """Split text at a separator that is not inside brackets or quotes.

        Args:
            text: The text to split.
            separator: The one character to split at.

        Returns:
            The pieces, without the separator, in order.
        """
        pieces = []
        closers: list[str] = []
        quote = ""
        start = 0
        for index, char in enumerate(text):
            if quote:
                quote = "" if char == quote else quote
            elif char in QUOTES:
                quote = char
            elif char in OPENERS:
                closers.append(OPENERS[char])
            elif closers and char == closers[-1]:
                closers.pop()
            elif char == separator and not closers:
                pieces.append(text[start:index])
                start = index + 1
        pieces.append(text[start:])
        return pieces
