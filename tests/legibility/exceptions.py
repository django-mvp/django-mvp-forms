"""The known exceptions: what falls short under a theme, and the list that says so."""

from collections.abc import Iterable, Mapping

from tests.legibility.pairings import Measurement
from tests.legibility.themes import Theme


class KnownExceptions:
    """The pairings that fall short of the standard under a shipped theme.

    The README's table is the one list. These methods find what the check measures,
    read what the README publishes and say how the two differ.
    """

    START = "<!-- known-exceptions:start -->"
    END = "<!-- known-exceptions:end -->"
    HEADER = ("Pairing", "Seen on", "Themes")

    @classmethod
    def found(
        cls, measurements: Iterable[Measurement], themes: Iterable[Theme]
    ) -> dict[str, set[str]]:
        """Find the held pairings that fall short, and under which themes.

        Args:
            measurements: What the reader read.
            themes: The themes to calculate under.

        Returns:
            The themes that each pairing falls short under, by the pairing's name.
        """
        held = {m.pairing for m in measurements if m.held}
        found: dict[str, set[str]] = {}
        for pairing in held:
            short = {t.name for t in themes if not pairing.meets(t)}
            if short:
                found[pairing.name] = short
        return found

    @classmethod
    def published(cls, text: str) -> dict[str, set[str]]:
        """Read the table between the two markers.

        Args:
            text: The README.

        Returns:
            The themes that each pairing is published under, by the pairing's name.
            What a row is seen on is not compared.

        Raises:
            ValueError: The text lacks the two markers.
        """
        if cls.START not in text or cls.END not in text:
            raise ValueError("the text lacks the known-exceptions markers")
        between = text.split(cls.START, 1)[1].split(cls.END, 1)[0]
        rows = [line for line in between.splitlines() if line.startswith("|")]
        published: dict[str, set[str]] = {}
        for row in rows[2:]:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            published[cells[0]] = {name for name in cells[2].split(", ") if name}
        return published

    @classmethod
    def table(cls, measurements: Iterable[Measurement], themes: Iterable[Theme]) -> str:
        """Write the published table as the check would find it.

        Args:
            measurements: What the reader read.
            themes: The themes to calculate under.

        Returns:
            A markdown table with a row for each pairing that falls short, sorted.
        """
        measurements = list(measurements)
        found = cls.found(measurements, themes)
        order = [t.name for t in themes]
        lines = [
            "| " + " | ".join(cls.HEADER) + " |",
            "| " + " | ".join("---" for _ in cls.HEADER) + " |",
        ]
        for name in sorted(found):
            kinds = {
                m.element.kind
                for m in measurements
                if m.held and m.pairing.name == name
            }
            shown = [theme for theme in order if theme in found[name]]
            lines.append(
                f"| {name} | {', '.join(sorted(kinds))} | {', '.join(shown)} |"
            )
        return "\n".join(lines)

    @classmethod
    def unlisted(
        cls, found: Mapping[str, set[str]], published: Mapping[str, set[str]]
    ) -> dict[str, set[str]]:
        """Find what the check finds and the README does not publish.

        Args:
            found: What the check measured.
            published: What the README lists.

        Returns:
            The themes found and not published, by pairing name.
        """
        return cls.difference(found, published)

    @classmethod
    def stale(
        cls, found: Mapping[str, set[str]], published: Mapping[str, set[str]]
    ) -> dict[str, set[str]]:
        """Find what the README publishes and the check no longer finds.

        Args:
            found: What the check measured.
            published: What the README lists.

        Returns:
            The themes published and not found, by pairing name.
        """
        return cls.difference(published, found)

    @classmethod
    def difference(
        cls, first: Mapping[str, set[str]], second: Mapping[str, set[str]]
    ) -> dict[str, set[str]]:
        """Subtract one mapping of pairings to themes from another.

        Args:
            first: The mapping to take from.
            second: The mapping to take away.

        Returns:
            What is in the first and not in the second, leaving out empty entries.
        """
        left = {
            name: themes - second.get(name, set()) for name, themes in first.items()
        }
        return {name: themes for name, themes in left.items() if themes}

    @classmethod
    def dimmed(
        cls, measurements: Iterable[Measurement], themes: Iterable[Theme]
    ) -> dict[str, dict[str, float]]:
        """Give the ratio of each pairing that is measured and not held.

        Args:
            measurements: What the reader read.
            themes: The themes to calculate under.

        Returns:
            Each theme's ratio, by theme name, for each such pairing's name.
        """
        measurements = list(measurements)
        held = {m.pairing for m in measurements if m.held}
        loose = {m.pairing for m in measurements if not m.held} - held
        return {
            pairing.name: {theme.name: pairing.ratio(theme) for theme in themes}
            for pairing in sorted(loose, key=lambda p: p.name)
        }
