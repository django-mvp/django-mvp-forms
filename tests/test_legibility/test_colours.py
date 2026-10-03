import pytest

from tests.legibility.colours import Colour
from tests.legibility.themes import Themes

BLACK = Colour.parse("oklch(0% 0 0)")
WHITE = Colour.parse("oklch(100% 0 0)")

# sRGB of base-100, base-content, base-content at 60% and at 20% on base-100, and
# error; then the ratios on base-100 of base-content, at 60%, error and at 20%.
VECTORS = {
    "light": (
        (
            (255, 255, 255),
            (24, 24, 27),
            (116, 116, 118),
            (209, 209, 209),
            (255, 98, 125),
        ),
        (17.73, 4.64, 2.87, 1.53),
    ),
    "retro": (
        (
            (236, 227, 202),
            (121, 50, 5),
            (167, 121, 84),
            (213, 192, 163),
            (255, 98, 102),
        ),
        (7.22, 2.99, 2.28, 1.38),
    ),
    "dark": (
        ((29, 35, 42), (236, 249, 255), (153, 163, 178), (70, 78, 87), (255, 98, 125)),
        (14.75, 6.23, 5.52, 1.87),
    ),
    "cupcake": (
        (
            (250, 247, 245),
            (41, 19, 52),
            (125, 110, 129),
            (208, 201, 206),
            (254, 28, 85),
        ),
        (15.91, 4.45, 3.57, 1.52),
    ),
}


def measured(name):
    colours = Themes.named(name).colours
    surface = colours["base-100"]
    content = colours["base-content"]
    return (
        (
            surface,
            content,
            content.faded(0.6).over(surface),
            content.faded(0.2).over(surface),
            colours["error"],
        ),
        (
            content,
            content.faded(0.6),
            colours["error"],
            content.faded(0.2),
        ),
    )


class TestColour:
    def test_black_on_white_is_twenty_one(self):
        assert BLACK.contrast(WHITE) == pytest.approx(21)

    def test_a_colour_on_itself_is_one(self):
        colour = Themes.named("retro").colours["error"]

        assert colour.contrast(colour) == pytest.approx(1)

    @pytest.mark.parametrize("name", VECTORS)
    def test_the_srgb_values_match_the_reference(self, name):
        colours, _ = measured(name)
        expected, _ = VECTORS[name]

        for colour, vector in zip(colours, expected, strict=True):
            assert colour.srgb() == pytest.approx(vector, abs=1)

    @pytest.mark.parametrize("name", VECTORS)
    def test_the_ratios_match_the_reference(self, name):
        theme = Themes.named(name)
        surface = theme.colours["base-100"]
        _, inks = measured(name)
        _, expected = VECTORS[name]

        for ink, ratio in zip(inks, expected, strict=True):
            assert ink.contrast(surface) == pytest.approx(ratio, abs=0.005)

    def test_a_faded_colour_is_composited_on_the_surface(self):
        faded = BLACK.faded(0.5)

        assert faded.contrast(WHITE) == pytest.approx(faded.over(WHITE).contrast(WHITE))
        assert faded.over(WHITE).srgb() == pytest.approx((127.5, 127.5, 127.5), abs=1)

    def test_mixing_two_colours_is_a_straight_line_in_oklab(self):
        mixed = BLACK.mixed(WHITE, 0.25)

        assert mixed.lightness == pytest.approx(0.75)
        assert mixed.alpha == 1

    def test_fading_sets_the_alpha(self):
        assert WHITE.faded(0.4).alpha == pytest.approx(0.4)
        assert WHITE.faded(0.5).faded(0.5).alpha == pytest.approx(0.25)

    def test_a_channel_outside_the_gamut_is_clipped_before_luminance(self):
        outside = Colour.parse("oklch(70% 0.4 30)")

        assert 0 <= outside.luminance() <= 1

    @pytest.mark.parametrize(
        "text",
        ["rgb(0 0 0)", "#ffffff", "oklch(50%)", "oklch(a b c)", "", "oklab(1 0 0)"],
    )
    def test_text_that_is_not_oklch_is_refused(self, text):
        with pytest.raises(ValueError, match="oklch"):
            Colour.parse(text)

    def test_the_percent_sign_is_optional(self):
        assert Colour.parse("oklch(50% 0.1 90)") == Colour.parse("oklch(0.5 0.1 90)")

    def test_a_see_through_surface_is_refused(self):
        with pytest.raises(ValueError, match="opaque"):
            BLACK.contrast(WHITE.faded(0.5))
