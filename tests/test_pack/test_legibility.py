"""The pack under every shipped theme: each form state a person can read."""

from collections import defaultdict
from pathlib import Path

import pytest

from tests.legibility.catalogue import Catalogue
from tests.legibility.exceptions import KnownExceptions
from tests.legibility.themes import Themes

README = Path(__file__).parent.parent.parent / "README.md"
THEMES = Themes.shipped()


def published():
    return KnownExceptions.published(README.read_text())


class TestEveryTheme:
    @pytest.mark.parametrize("theme", THEMES, ids=lambda theme: theme.name)
    def test_every_held_pairing_meets_its_figure_or_is_published(self, theme):
        listed = published()
        failures = {
            (m.form_state, m.pairing.name): (m.pairing.ratio(theme), m.pairing.figure)
            for m in Catalogue.measurements()
            if m.held
            and not m.pairing.meets(theme)
            and theme.name not in listed.get(m.pairing.name, set())
        }

        assert not failures, "\n".join(
            f"{state} | {theme.name} | {name} | {ratio:.2f} < {figure}"
            for (state, name), (ratio, figure) in sorted(failures.items())
        )


class TestPublishedExceptions:
    def test_nothing_is_published_that_the_check_does_not_find(self):
        found = KnownExceptions.found(Catalogue.measurements(), THEMES)

        assert KnownExceptions.stale(found, published()) == {}

    def test_nothing_the_check_finds_is_missing_from_the_list(self):
        found = KnownExceptions.found(Catalogue.measurements(), THEMES)

        assert KnownExceptions.unlisted(found, published()) == {}

    def test_every_theme_the_list_names_is_a_shipped_theme(self):
        named = {name for themes in published().values() for name in themes}

        assert named <= {theme.name for theme in THEMES}


class TestRepairs:
    def test_no_text_the_pack_colours_falls_short_under_any_theme(self):
        short = defaultdict(set)
        for m in Catalogue.measurements():
            if m.held and m.own:
                for theme in THEMES:
                    if not m.pairing.meets(theme):
                        short[(m.element.kind, m.pairing.name)].add(theme.name)

        assert not short, "\n".join(
            f"{kind} | {name} | {len(themes)} themes"
            for (kind, name), themes in sorted(short.items())
        )
