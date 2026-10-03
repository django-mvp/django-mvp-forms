import pytest

from tests.legibility.pairings import Element, Ink, Measurement, Pairing
from tests.legibility.themes import Themes

CONTENT = Ink("base-content")
BASE = Ink("base-100")
LIGHT = Themes.named("light")


class TestInk:
    def test_an_ink_resolves_to_the_themes_colour(self):
        assert Ink("error").resolve(LIGHT) == LIGHT.colours["error"]

    def test_a_faded_ink_resolves_to_the_colour_at_that_alpha(self):
        resolved = CONTENT.faded(0.6).resolve(LIGHT)

        assert resolved == LIGHT.colours["base-content"].faded(0.6)

    def test_a_faded_ink_meets_the_reference_ratio_under_light(self):
        ratio = CONTENT.faded(0.6).resolve(LIGHT).contrast(BASE.resolve(LIGHT))

        assert ratio == pytest.approx(4.64, abs=0.005)

    def test_a_mixed_ink_resolves_to_the_two_mixed(self):
        resolved = Ink("error").mixed(BASE, 0.08).resolve(LIGHT)

        assert resolved == LIGHT.colours["error"].mixed(LIGHT.colours["base-100"], 0.08)

    def test_an_ink_laid_over_a_surface_is_opaque(self):
        resolved = CONTENT.faded(0.6).over(BASE).resolve(LIGHT)

        assert resolved.alpha == 1

    def test_fading_a_faded_ink_multiplies_the_shares(self):
        assert CONTENT.faded(0.6).faded(0.2) == CONTENT.faded(0.12)

    def test_two_inks_built_the_same_way_are_equal(self):
        assert Ink("error").faded(0.5) == Ink("error").faded(0.5)
        assert hash(Ink("error").faded(0.5)) == hash(Ink("error").faded(0.5))

    def test_inks_built_differently_are_not_equal(self):
        assert Ink("error") != Ink("success")
        assert Ink("error").faded(0.5) != Ink("error").faded(0.6)
        assert Ink("error").mixed(BASE, 0.08) != Ink("error").over(BASE)

    def test_the_words_state_the_shares_and_the_names(self):
        assert CONTENT.words == "`base-content`"
        assert CONTENT.faded(0.6).words == "`base-content` at 60%"
        assert Ink("error").mixed(BASE, 0.08).words == "8% `error` in `base-100`"
        assert CONTENT.faded(0.2).over(BASE).words == (
            "`base-content` at 20% over `base-100`"
        )

    def test_a_colour_the_theme_does_not_have_is_refused(self):
        with pytest.raises(KeyError):
            Ink("no-such-colour").resolve(LIGHT)


class TestPairing:
    def test_the_figure_is_four_and_a_half_for_text(self):
        for part in ("text", "placeholder", "button text"):
            assert Pairing.of(part, CONTENT, BASE).figure == 4.5

    def test_the_figure_is_three_for_a_part_of_a_control(self):
        for part in ("border", "mark"):
            assert Pairing.of(part, CONTENT, BASE).figure == 3.0

    def test_a_part_that_is_not_one_of_the_closed_set_is_refused(self):
        with pytest.raises(ValueError, match="part"):
            Pairing.of("colour", CONTENT, BASE)

    def test_the_name_is_the_same_for_the_same_part_ink_and_surface(self):
        first = Pairing.of("text", CONTENT.faded(0.6), BASE)
        second = Pairing.of("text", CONTENT.faded(0.6), BASE)

        assert first.name == second.name
        assert first == second

    def test_the_name_differs_when_any_of_the_three_differs(self):
        names = {
            Pairing.of("text", CONTENT, BASE).name,
            Pairing.of("border", CONTENT, BASE).name,
            Pairing.of("text", Ink("error"), BASE).name,
            Pairing.of("text", CONTENT, Ink("base-200")).name,
        }

        assert len(names) == 4

    def test_the_ratio_is_the_inks_contrast_on_the_surface(self):
        pairing = Pairing.of("text", CONTENT, BASE)

        assert pairing.ratio(LIGHT) == pytest.approx(17.73, abs=0.005)

    def test_it_meets_the_standard_when_the_ratio_reaches_the_figure(self):
        assert Pairing.of("text", CONTENT, BASE).meets(LIGHT)
        assert not Pairing.of("border", CONTENT.faded(0.2), BASE).meets(LIGHT)


class TestMeasurement:
    def test_an_element_names_its_tag_id_and_classes(self):
        element = Element("input", "id_name", ("input", "input-error"), "input")

        assert str(element) == "input#id_name.input.input-error"

    def test_an_element_with_neither_id_nor_classes_is_its_tag(self):
        assert str(Element("p", "", (), "p")) == "p"

    def test_a_measurement_holds_what_it_was_read_from(self):
        pairing = Pairing.of("text", CONTENT, BASE)
        element = Element("p", "", (), "p")

        measurement = Measurement("unbound", element, pairing, held=True, own=False)

        assert measurement.pairing is pairing
        assert measurement.form_state == "unbound"
