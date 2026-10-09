"""The stylesheet for django-tomselect stays inside its controls and takes its colours
from the theme."""

import pytest
from bs4 import BeautifulSoup

from tests.legibility.pairings import Ink, Pairing
from tests.legibility.reader import BASE_100, CONTENT, Reader
from tests.legibility.themes import Themes
from tests.tomselect_stylesheet import Stylesheet, UnreadRule

DROPDOWN = ":root div.ts-dropdown"
ACTIVE = ":root .ts-dropdown .active"
CHOSEN = ":root .ts-dropdown .option.selected"
NO_RESULTS = ":root .ts-dropdown .no-results"
NO_MORE_RESULTS = ":root .ts-dropdown .no-more-results"
LOADING_MORE_RESULTS = ":root .ts-dropdown .loading-more-results"
CLEAR = ":root .ts-wrapper.plugin-clear_button .clear-button"
CLEAR_SHOWN = (
    ":root .ts-wrapper.plugin-clear_button.has-items:not(.disabled):hover .clear-button"
)
LOADING = ":root .ts-wrapper.loading"
RING = ":root .ts-wrapper.loading::before"
PLACEHOLDER = ":root .ts-wrapper .ts-control > input::placeholder"
TAG = ":root .ts-wrapper.multi .ts-control > .item"
TAG_ACTIVE = ":root .ts-wrapper.multi .ts-control > .item.active"
TAG_REMOVE = ":root .ts-wrapper.plugin-remove_button .ts-control .item .remove"
DISABLED_TAG = ":root .ts-wrapper.multi.disabled .ts-control > .item"
GROUP_HEADING = ":root .ts-dropdown .optgroup-header"
DISABLED_WRAPPER = ":root .ts-wrapper.disabled"
DISABLED_OPTION = ":root .ts-dropdown [data-disabled]"
THEMES = [Themes.named("light"), Themes.named("dark")]
HELD = [
    "an option",
    "the active option",
    "a chosen option",
    "the line with no results",
    "the line with no more results",
    "the line loading more results",
    "the clear button",
    "the loading ring",
    "a tag",
    "the remove button of a tag",
    "the tag the keyboard is on",
    "the remove button of the tag the keyboard is on",
    "a group heading",
]
MEASURED = ["the disabled wrapper", "a disabled option", "a disabled tag"]

READ = """
/* A comment with { braces } and a colour: #fff; rgb(0, 0, 0) */
:root .ts-wrapper, :root .ts-dropdown:has(.a, .b) {
  color: var(--color-base-content) !important;
  content: "a;b";
  border: 2px solid currentColor;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
"""


class TestTheStylesheetReader:
    sheet = Stylesheet(READ)

    def test_a_selector_list_is_split_at_a_comma_outside_brackets(self):
        assert self.sheet.selectors() == [
            ":root .ts-wrapper",
            ":root .ts-dropdown:has(.a, .b)",
        ]

    def test_a_comment_is_removed_whatever_it_holds(self):
        assert len(self.sheet.rules) == 1
        assert self.sheet.colours() == []

    def test_a_declaration_is_its_name_its_value_and_whether_it_is_important(self):
        names = {
            declaration.name: (declaration.value, declaration.important)
            for declaration in self.sheet.rules[0].declarations
        }

        assert names == {
            "color": ("var(--color-base-content)", True),
            "content": ('"a;b"', False),
            "border": ("2px solid currentColor", False),
        }

    def test_the_frames_of_keyframes_are_kept_apart_from_the_rules(self):
        assert list(self.sheet.keyframes) == ["spin"]
        assert "transform" in {
            declaration.name for declaration in self.sheet.declarations()
        }
        assert "to" not in self.sheet.selectors()

    def test_an_at_rule_it_cannot_read_is_refused(self):
        with pytest.raises(UnreadRule):
            Stylesheet("@media print { .ts-wrapper { color: red; } }")

    def test_the_stylesheet_the_package_ships_is_read_by_default(self):
        assert Stylesheet().rules


class TestWhatTheStylesheetDeclares:
    sheet = Stylesheet(
        """
        .a { color: var(--color-base-content); opacity: 0.5; }
        .a, .b { color: color-mix(in oklab, var(--color-neutral) 30%, transparent); }
        .c { color: color-mix(in oklab, var(--color-error) 25%, var(--color-base-100)); }
        .d { color: inherit !important; border: 2px solid currentColor; }
        .e { color: red; }
        """
    )

    def test_the_last_rule_with_the_selector_that_declares_a_property_gives_it(self):
        assert self.sheet.declared(".a", "color").startswith("color-mix")
        assert self.sheet.declared(".a", "opacity") == "0.5"

    def test_a_property_no_rule_with_the_selector_declares_is_refused(self):
        with pytest.raises(KeyError):
            self.sheet.declared(".b", "opacity")

    def test_a_number_is_read_as_one(self):
        assert self.sheet.number(".a", "opacity") == 0.5

    def test_a_colour_mixed_with_transparent_is_the_ink_faded(self):
        assert self.sheet.ink(".b", "color") == Ink("neutral").faded(0.3)

    def test_a_colour_mixed_with_another_is_the_two_inks_mixed(self):
        assert self.sheet.ink(".c", "color") == Ink("error").mixed(
            Ink("base-100"), 0.25
        )

    @pytest.mark.parametrize("name", ["color", "border"])
    def test_a_value_that_takes_the_surrounding_ink_is_the_ink_it_is_given(self, name):
        assert self.sheet.ink(".d", name, inherited=Ink("base-content")) == Ink(
            "base-content"
        )

    @pytest.mark.parametrize("name", ["color", "border"])
    def test_a_value_that_takes_the_surrounding_ink_with_none_given_is_refused(
        self, name
    ):
        with pytest.raises(ValueError, match="surrounding"):
            self.sheet.ink(".d", name)

    def test_a_colour_that_is_not_the_themes_is_refused(self):
        with pytest.raises(ValueError, match="theme"):
            self.sheet.ink(".e", "color")


class TestTheScopeOfTheStylesheet:
    def test_every_selector_is_inside_a_control_or_a_named_exception(self):
        assert Stylesheet().outside_a_control() == []

    @pytest.mark.parametrize(
        "selector",
        [
            ".btn",
            ":root .btn",
            "body .ts-wrapper",
            ".modal-box",
            ".ts-wrapperish",
            ".modal-box:has(.ts-wrapper.dropdown-active) .btn",
            ".overflow-x-auto:has(.ts-wrapper)",
            '[id$="_sr_status"]',
        ],
    )
    def test_a_selector_outside_a_control_is_found(self, selector):
        sheet = Stylesheet(f"{selector} {{ margin: 0; }}")

        assert sheet.outside_a_control() == [selector]

    @pytest.mark.parametrize(
        "selector",
        [
            ".ts-wrapper",
            ":root .ts-wrapper.multi .ts-control > .item",
            ":root div.ts-dropdown",
            ".ts-dropdown .option",
            ':root [id$="_sr_status"].visually-hidden',
            ".modal-box:has(.ts-wrapper.dropdown-active)",
            ".overflow-x-auto:has(.ts-wrapper.dropdown-active)",
        ],
    )
    def test_a_selector_in_a_control_or_a_named_exception_is_not_found(self, selector):
        sheet = Stylesheet(f"{selector} {{ margin: 0; }}")

        assert sheet.outside_a_control() == []

    def test_one_selector_outside_a_control_in_a_list_is_found(self):
        sheet = Stylesheet(".ts-wrapper, .btn { margin: 0; }")

        assert sheet.outside_a_control() == [".btn"]


class TestTheColoursOfTheStylesheet:
    def test_no_declaration_names_a_colour_of_its_own(self):
        assert Stylesheet().colours() == []

    @pytest.mark.parametrize(
        "value",
        [
            "#fff",
            "#1a2b3c",
            "#1a2b3c80",
            "rgb(0 0 0)",
            "rgba(0, 0, 0, 0.5)",
            "hsl(10 20% 30%)",
            "oklch(60% 0.1 200)",
            "oklab(60% 0.1 0.1)",
            "color(display-p3 1 0 0)",
            "light-dark(white, black)",
            "red",
            "1px solid Tomato",
            "color-mix(in oklab, rebeccapurple 40%, transparent)",
            "var(--color-base-content, #000)",
        ],
    )
    def test_a_colour_literal_is_found(self, value):
        sheet = Stylesheet(f".ts-wrapper {{ border: {value}; }}")

        assert [declaration.value for declaration in sheet.colours()] == [value]

    def test_a_colour_literal_in_a_keyframe_is_found(self):
        sheet = Stylesheet("@keyframes x { to { color: #fff; } }")

        assert [declaration.value for declaration in sheet.colours()] == ["#fff"]

    @pytest.mark.parametrize(
        "value",
        [
            "var(--color-base-content)",
            "var(--color-red-500)",
            "color-mix(in oklab, var(--color-neutral) 30%, transparent)",
            "2px solid currentColor",
            "currentcolor transparent currentColor transparent",
            "transparent",
            '"red"',
            "none",
        ],
    )
    def test_a_colour_taken_from_the_theme_is_not_found(self, value):
        sheet = Stylesheet(f".ts-wrapper {{ border: {value}; }}")

        assert sheet.colours() == []

    def test_a_declaration_that_is_not_a_colour_is_not_found(self):
        sheet = Stylesheet(
            ".ts-wrapper { border-radius: 9999px; opacity: 0.6; z-index: 50; }"
        )

        assert sheet.colours() == []


class TestTheLegibilityOfTheStylesheet:
    sheet = Stylesheet()

    def pairings(self):
        sheet = self.sheet
        text = sheet.ink(DROPDOWN, "color")
        surface = sheet.ink(DROPDOWN, "background")
        tag_text = sheet.ink(TAG, "color")
        tag_surface = sheet.ink(TAG, "background")
        active_tag_text = sheet.ink(TAG_ACTIVE, "color")
        active_tag_surface = sheet.ink(TAG_ACTIVE, "background")
        return {
            "an option": Pairing.of("text", text, surface),
            "the active option": Pairing.of(
                "text",
                sheet.ink(ACTIVE, "color", inherited=text),
                sheet.ink(ACTIVE, "background-color").over(surface),
            ),
            "a chosen option": Pairing.of(
                "text",
                sheet.ink(CHOSEN, "color"),
                sheet.ink(CHOSEN, "background-color"),
            ),
            "the line with no results": Pairing.of(
                "text", sheet.ink(NO_RESULTS, "color"), surface
            ),
            "the line with no more results": Pairing.of(
                "text", sheet.ink(NO_MORE_RESULTS, "color"), surface
            ),
            "the line loading more results": Pairing.of(
                "text", sheet.ink(LOADING_MORE_RESULTS, "color"), surface
            ),
            "the clear button": Pairing.of(
                "mark",
                sheet.ink(CLEAR, "color", inherited=CONTENT).faded(
                    sheet.number(CLEAR_SHOWN, "opacity")
                ),
                BASE_100,
            ),
            "the loading ring": Pairing.of(
                "mark",
                sheet.ink(RING, "border", inherited=CONTENT).faded(
                    sheet.number(RING, "opacity")
                ),
                sheet.ink(LOADING, "background-color"),
            ),
            "a group heading": Pairing.of(
                "text", sheet.ink(GROUP_HEADING, "color"), surface
            ),
            "a tag": Pairing.of("text", tag_text, tag_surface),
            "the remove button of a tag": Pairing.of(
                "mark",
                sheet.ink(TAG_REMOVE, "color", inherited=tag_text).faded(
                    sheet.number(TAG_REMOVE, "opacity")
                ),
                tag_surface,
            ),
            "the tag the keyboard is on": Pairing.of(
                "text", active_tag_text, active_tag_surface
            ),
            "the remove button of the tag the keyboard is on": Pairing.of(
                "mark",
                sheet.ink(TAG_REMOVE, "color", inherited=active_tag_text).faded(
                    sheet.number(TAG_REMOVE, "opacity")
                ),
                active_tag_surface,
            ),
            "a disabled tag": Pairing.of(
                "text",
                sheet.ink(DISABLED_TAG, "color"),
                sheet.ink(DISABLED_TAG, "background"),
            ),
            "the disabled wrapper": Pairing.of(
                "text",
                sheet.ink(DISABLED_WRAPPER, "color"),
                sheet.ink(DISABLED_WRAPPER, "background-color"),
            ),
            "a disabled option": Pairing.of(
                "text", text.faded(sheet.number(DISABLED_OPTION, "opacity")), surface
            ),
        }

    @pytest.mark.parametrize("theme", THEMES, ids=lambda theme: theme.name)
    @pytest.mark.parametrize("name", HELD)
    def test_what_a_person_has_to_make_out_meets_the_standard(self, name, theme):
        pairing = self.pairings()[name]

        assert pairing.meets(theme), f"{pairing.name}: {pairing.ratio(theme):.2f}"

    @pytest.mark.parametrize("theme", THEMES, ids=lambda theme: theme.name)
    @pytest.mark.parametrize("name", MEASURED)
    def test_a_disabled_pairing_is_measured_and_not_held(self, name, theme):
        assert 1 <= self.pairings()[name].ratio(theme) <= 21

    def test_the_placeholder_is_the_pairing_daisyui_draws_on_its_own_input(self):
        sheet = self.sheet
        drawn = BeautifulSoup(
            '<input type="text" class="input" placeholder="x">', "html.parser"
        )
        daisyui = next(
            measurement.pairing
            for measurement in Reader("an input").read(drawn)
            if measurement.pairing.part == "placeholder"
        )

        ink = sheet.ink(PLACEHOLDER, "color").faded(
            sheet.number(PLACEHOLDER, "opacity")
        )

        assert (ink, BASE_100) == (daisyui.ink, daisyui.surface)

    def test_a_rule_the_pairings_are_read_from_that_is_gone_is_found(self):
        sheet = Stylesheet(".ts-wrapper { margin: 0; }")

        with pytest.raises(KeyError):
            sheet.ink(DROPDOWN, "color")
