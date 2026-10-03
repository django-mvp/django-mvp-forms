import pytest

from tests.legibility.exceptions import KnownExceptions
from tests.legibility.pairings import Element, Ink, Measurement, Pairing
from tests.legibility.themes import Themes

CONTENT = Ink("base-content")
BASE = Ink("base-100")
THEMES = Themes.shipped()[:4]
NAMES = {theme.name for theme in THEMES}


def measurement(kind, pairing, held=True, state="a state"):
    return Measurement(state, Element(kind, "", (), kind), pairing, held, False)


FAILS = Pairing.of("border", CONTENT.faded(0.2), BASE)
PASSES = Pairing.of("text", CONTENT, BASE)
OTHER_FAILS = Pairing.of("placeholder", CONTENT.faded(0.2), BASE)


def wrapped(table):
    return f"before\n{KnownExceptions.START}\n{table}\n{KnownExceptions.END}\nafter"


class TestKnownExceptions:
    def test_a_measurement_that_falls_short_is_found_with_its_themes(self):
        found = KnownExceptions.found([measurement("input", FAILS)], THEMES)

        assert found == {FAILS.name: NAMES}

    def test_a_measurement_that_passes_is_not_found(self):
        assert KnownExceptions.found([measurement("p", PASSES)], THEMES) == {}

    def test_a_measurement_that_is_not_held_is_not_found(self):
        found = KnownExceptions.found([measurement("input", FAILS, held=False)], THEMES)

        assert found == {}

    def test_a_pairing_held_anywhere_is_found(self):
        measurements = [
            measurement("input", FAILS, held=False),
            measurement("select", FAILS, held=True),
        ]

        assert FAILS.name in KnownExceptions.found(measurements, THEMES)

    def test_the_table_has_a_row_for_each_pairing_that_falls_short(self):
        measurements = [
            measurement("input", FAILS),
            measurement("select", FAILS),
            measurement("p", PASSES),
            measurement("input", OTHER_FAILS),
        ]

        table = KnownExceptions.table(measurements, THEMES)
        rows = table.splitlines()[2:]

        assert len(rows) == 2
        assert PASSES.name not in table

    def test_the_rows_are_sorted_by_pairing(self):
        measurements = [
            measurement("input", OTHER_FAILS),
            measurement("input", FAILS),
        ]

        rows = KnownExceptions.table(measurements, THEMES).splitlines()[2:]

        assert rows == sorted(rows)

    def test_a_row_says_what_it_is_seen_on_by_kind(self):
        measurements = [
            measurement("select", FAILS, state="one"),
            measurement("input", FAILS, state="two"),
            measurement("input", FAILS, state="three"),
        ]

        row = KnownExceptions.table(measurements, THEMES).splitlines()[2]
        cells = [cell.strip() for cell in row.strip("|").split("|")]

        assert cells[1] == "input, select"
        assert "one" not in row

    def test_published_reads_back_what_the_table_wrote(self):
        measurements = [measurement("input", FAILS), measurement("input", OTHER_FAILS)]
        table = KnownExceptions.table(measurements, THEMES)

        published = KnownExceptions.published(wrapped(table))

        assert published == KnownExceptions.found(measurements, THEMES)

    def test_published_reads_only_between_the_markers(self):
        outside = "| Pairing | Seen on | Themes |\n| --- | --- | --- |\n| x | y | z |"
        table = KnownExceptions.table([measurement("input", FAILS)], THEMES)

        published = KnownExceptions.published(f"{outside}\n{wrapped(table)}")

        assert set(published) == {FAILS.name}

    def test_published_with_no_rows_is_empty(self):
        table = KnownExceptions.table([], THEMES)

        assert KnownExceptions.published(wrapped(table)) == {}

    def test_published_refuses_text_with_no_markers(self):
        with pytest.raises(ValueError, match="known-exceptions"):
            KnownExceptions.published("no table here")

    def test_unlisted_gives_what_was_found_and_not_published(self):
        found = {"a": {"x", "y"}, "b": {"z"}}
        published = {"a": {"x"}}

        assert KnownExceptions.unlisted(found, published) == {"a": {"y"}, "b": {"z"}}

    def test_stale_gives_what_was_published_and_not_found(self):
        found = {"a": {"x"}}
        published = {"a": {"x", "y"}, "b": {"z"}}

        assert KnownExceptions.stale(found, published) == {"a": {"y"}, "b": {"z"}}

    def test_nothing_differs_when_found_equals_published(self):
        both = {"a": {"x"}}

        assert KnownExceptions.unlisted(both, both) == {}
        assert KnownExceptions.stale(both, both) == {}

    def test_dimmed_gives_the_ratio_under_each_theme_of_what_is_not_held(self):
        measurements = [
            measurement("input", FAILS, held=False),
            measurement("input", PASSES, held=True),
        ]

        dimmed = KnownExceptions.dimmed(measurements, THEMES)

        assert set(dimmed) == {FAILS.name}
        assert set(dimmed[FAILS.name]) == NAMES
        assert all(ratio >= 1 for ratio in dimmed[FAILS.name].values())
