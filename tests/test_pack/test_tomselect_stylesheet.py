"""The stylesheet for django-tomselect stays inside its controls and takes its colours
from the theme."""

import pytest

from tests.tomselect_stylesheet import Stylesheet, UnreadRule

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
