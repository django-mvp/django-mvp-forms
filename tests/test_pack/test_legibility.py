"""The pack under every shipped theme: each form state a person can read."""

import re
from collections import defaultdict
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from tests.legibility.catalogue import Catalogue
from tests.legibility.exceptions import KnownExceptions
from tests.legibility.reader import Reader, Uncovered
from tests.legibility.themes import COLOURS, THEMES_CSS, Themes

ROOT = Path(__file__).parent.parent.parent
README = ROOT / "README.md"
TEMPLATES = ROOT / "mvp_forms" / "templates"
TAGS = re.compile(r"\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}", re.DOTALL)
CLASS_ATTRIBUTE = re.compile(r'\bclass="([^"]*)"')
THEMES = Themes.shipped()


def published():
    return KnownExceptions.published(README.read_text())


class TestEveryTheme:
    @pytest.mark.parametrize("theme", THEMES, ids=lambda theme: theme.name)
    def test_every_held_pairing_meets_its_figure_or_is_published(self, theme):
        failures = KnownExceptions.failures(
            Catalogue.measurements(), theme, published()
        )

        assert not failures, failures


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


class TestTheCheckCatches:
    @pytest.fixture
    def help_text_without_its_ink(self):
        state = next(s for s in Catalogue.states() if s.name == "help text")
        fragment = BeautifulSoup(
            str(state.soup.select_one("p[id$=_helptext]")), "html.parser"
        )
        fragment.p["class"].remove("text-base-content")
        return Reader("help text without its ink").read(fragment)

    @pytest.fixture
    def with_an_added_theme(self):
        colours = "".join(f"--color-{name}:oklch(90% 0 0);" for name in sorted(COLOURS))
        added = f"[data-theme=added]{{color-scheme:light;{colours}}}"
        return Themes.read(THEMES_CSS.read_text() + added)

    def test_help_text_that_lost_its_ink_falls_short_under_a_theme(
        self, help_text_without_its_ink
    ):
        short = [
            theme
            for theme in THEMES
            if any(
                m.held and not m.pairing.meets(theme) for m in help_text_without_its_ink
            )
        ]

        assert short

    def test_the_failure_names_the_state_the_theme_and_the_pairing(
        self, help_text_without_its_ink
    ):
        theme = next(
            theme
            for theme in THEMES
            if any(not m.pairing.meets(theme) for m in help_text_without_its_ink)
        )
        measurement = next(
            m for m in help_text_without_its_ink if not m.pairing.meets(theme)
        )

        failures = KnownExceptions.failures(help_text_without_its_ink, theme, {})

        assert measurement.form_state in failures
        assert theme.name in failures
        assert measurement.pairing.name in failures

    def test_a_published_entry_that_now_passes_is_reported_stale(self):
        theme = THEMES[0]
        passing = next(
            m.pairing
            for m in Catalogue.measurements()
            if m.held and m.pairing.meets(theme)
        )
        found = KnownExceptions.found(Catalogue.measurements(), THEMES)

        stale = KnownExceptions.stale(found, {passing.name: {theme.name}})

        assert stale == {passing.name: {theme.name}}

    def test_a_shortfall_missing_from_the_list_is_reported_unlisted(self):
        found = KnownExceptions.found(Catalogue.measurements(), THEMES)
        name, themes = next(iter(sorted(published().items())))
        dropped = sorted(themes)[0]
        listed = {**published(), name: themes - {dropped}}

        unlisted = KnownExceptions.unlisted(found, listed)

        assert unlisted == {name: {dropped}}

    def test_a_theme_added_to_the_pinned_text_is_among_the_themes(
        self, with_an_added_theme
    ):
        assert [theme.name for theme in with_an_added_theme] == [
            *(theme.name for theme in THEMES),
            "added",
        ]

    def test_the_shortfalls_under_an_added_theme_are_found(self, with_an_added_theme):
        added = with_an_added_theme[-1]

        found = KnownExceptions.found(Catalogue.measurements(), with_an_added_theme)
        failures = KnownExceptions.failures(
            Catalogue.measurements(), added, published()
        )

        assert any(added.name in themes for themes in found.values())
        assert added.name in failures

    def test_a_class_the_reader_has_no_row_for_raises_uncovered(self):
        soup = BeautifulSoup('<div class="badge">Seen</div>', "html.parser")

        with pytest.raises(Uncovered) as raised:
            Reader("a badge").read(soup)

        assert raised.value.class_name == "badge"
        assert raised.value.form_state == "a badge"


class TestCoverage:
    def test_every_daisyui_class_a_template_writes_is_drawn_by_a_state(
        self, daisyui_classes
    ):
        written = set()
        for path in TEMPLATES.rglob("*.html"):
            for attribute in CLASS_ATTRIBUTE.findall(TAGS.sub(" ", path.read_text())):
                written |= set(attribute.split())
        drawn = {
            name
            for state in Catalogue.states()
            for tag in state.soup.find_all(class_=True)
            for name in tag["class"]
        }

        assert written & daisyui_classes
        assert (written & daisyui_classes) - drawn == set()

    def test_every_disabled_control_has_dimmed_pairings_under_every_theme(self):
        measured = defaultdict(list)
        for m in Catalogue.measurements():
            measured[(m.form_state, m.element.tag, m.element.id)].append(m)
        disabled = [
            (state.name, tag.name, tag.get("id", ""))
            for state in Catalogue.states()
            for tag in state.soup.find_all(attrs={"disabled": True})
        ]

        assert disabled
        for key in disabled:
            assert measured[key], key
            assert not any(m.held for m in measured[key]), key
            assert all(
                1 <= m.pairing.ratio(theme) <= 21
                for m in measured[key]
                for theme in THEMES
            ), key

    def test_the_report_gives_each_dimmed_pairing_a_ratio_under_every_theme(self):
        dimmed = KnownExceptions.dimmed(Catalogue.measurements(), THEMES)

        assert dimmed
        assert all(
            set(ratios) == {t.name for t in THEMES} for ratios in dimmed.values()
        )
