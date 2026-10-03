from pathlib import Path

import pytest

from tests.legibility.colours import Colour
from tests.legibility.themes import Themes

DATA = Path(__file__).parent.parent / "data"
THEMES_CSS = (DATA / "daisyui-themes.css").read_text()
CLASSES_TXT = (DATA / "daisyui-classes.txt").read_text()

COLOURS = {
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

RULE = (
    ":root:has(input.theme-controller[value=twilight]:checked),[data-theme=twilight]"
    "{{color-scheme:dark;--color-base-100:oklch(10% 0 0);{colours}}}"
)


def twilight(extra=""):
    colours = "".join(
        f"--color-{name}:oklch(50% 0 0);" for name in sorted(COLOURS - {"base-100"})
    )
    return RULE.format(colours=colours) + extra


class TestThemes:
    def test_thirty_five_themes_are_shipped(self):
        assert len(Themes.shipped()) == 35

    def test_each_theme_has_a_scheme_and_all_twenty_colours(self):
        for theme in Themes.shipped():
            assert theme.scheme in {"light", "dark"}, theme.name
            assert set(theme.colours) == COLOURS, theme.name
            assert all(isinstance(c, Colour) for c in theme.colours.values())

    def test_both_schemes_are_shipped(self):
        schemes = {theme.scheme for theme in Themes.shipped()}

        assert schemes == {"light", "dark"}

    def test_theme_names_are_unique(self):
        names = [theme.name for theme in Themes.shipped()]

        assert len(set(names)) == len(names)

    def test_a_theme_is_found_by_name(self):
        assert Themes.named("retro").name == "retro"

    def test_an_unknown_name_is_refused(self):
        with pytest.raises(KeyError):
            Themes.named("no-such-theme")

    def test_a_rule_without_a_theme_selector_is_not_a_theme(self):
        text = ":root{color-scheme:light;--color-base-100:oklch(100% 0 0)}" + twilight()

        assert [theme.name for theme in Themes.read(text)] == ["twilight"]

    def test_a_banner_comment_is_not_part_of_a_selector(self):
        text = "/*! daisyUI 9.9.9 - MIT License */ " + twilight()

        assert [theme.name for theme in Themes.read(text)] == ["twilight"]

    def test_a_theme_added_to_a_copy_of_the_text_is_returned(self):
        names = [theme.name for theme in Themes.read(THEMES_CSS + twilight())]

        assert len(names) == 36
        assert names[-1] == "twilight"

    def test_a_theme_missing_a_colour_is_refused(self):
        text = twilight().replace("--color-error:oklch(50% 0 0);", "")

        with pytest.raises(ValueError, match="error"):
            Themes.read(text)

    def test_a_theme_with_no_scheme_is_refused(self):
        with pytest.raises(ValueError):
            Themes.read(twilight().replace("color-scheme:dark;", ""))

    def test_the_version_is_read_from_the_banner(self):
        assert Themes.version("/*! 🌼 daisyUI 1.2.3 - MIT License */ x") == "1.2.3"

    def test_text_with_no_version_is_refused(self):
        with pytest.raises(ValueError):
            Themes.version(":root{}")

    def test_the_themes_and_the_class_list_are_the_same_version(self):
        assert Themes.version(THEMES_CSS) == Themes.version(CLASSES_TXT)

    def test_the_pinned_file_is_the_one_read(self):
        assert Themes.read(THEMES_CSS) == Themes.shipped()
