"""The README's list of templates is true of the templates the pack distributes."""

from pathlib import Path

from mvp_forms.deprecation import WITHDRAWN
from tests.conftest import PACK_TEMPLATES
from tests.template_surface import TemplateSurface

README = Path(__file__).parents[2] / "README.md"

PACK_TABLE = (
    "### Replacing one template\n\n"
    "| Template | Draws | Handed | Found by |\n|---|---|---|---|\n"
    "| `daisyui/a.html` | Draws a. | `field` | `TEMPLATES` |\n\n"
)
SUPPORTED_TABLE = (
    "#### A supported package's templates\n\n"
    "| Template | Draws | Found by |\n|---|---|---|\n"
    "| `django_tomselect/tomselect.html` | Draws it. | Application directories. |\n\n"
)
PACK_TEMPLATE = "{{ field }}"
SUPPORTED_TEMPLATE = '{% extends "django_tomselect/tomselect.html" %}'


class TestTheListMatchesThePackage:
    surface = TemplateSurface(README.read_text(), PACK_TEMPLATES, WITHDRAWN)

    def test_the_list_and_the_package_do_not_differ(self):
        assert self.surface.disagreements() == []

    def test_every_row_says_what_its_template_draws(self):
        rows = [*self.surface.listed(), *self.surface.listed_supported()]

        assert rows
        assert [row["path"] for row in rows if not row["draws"].strip()] == []

    def test_a_supported_package_has_a_row_of_its_own(self):
        rows = self.surface.listed_supported()

        assert [row["path"] for row in rows] == ["django_tomselect/tomselect.html"]


class TestASupportedPackagesTemplates:
    FILES = {
        "daisyui/a.html": PACK_TEMPLATE,
        "django_tomselect/tomselect.html": SUPPORTED_TEMPLATE,
    }

    def test_a_template_in_the_second_table_is_not_read_for_names(
        self, template_surface
    ):
        surface = template_surface(PACK_TABLE + SUPPORTED_TABLE, self.FILES)

        assert surface.disagreements() == []

    def test_a_supported_template_with_no_row_is_reported(self, template_surface):
        surface = template_surface(PACK_TABLE, self.FILES)

        assert surface.disagreements() == [
            ("not listed", "django_tomselect/tomselect.html")
        ]

    def test_a_template_outside_both_directories_is_reported(self, template_surface):
        files = {**self.FILES, "other/x.html": ""}
        surface = template_surface(PACK_TABLE + SUPPORTED_TABLE, files)

        assert sorted(surface.disagreements()) == [
            ("not listed", "other/x.html"),
            ("outside the directories", "other/x.html"),
        ]

    def test_a_pack_template_in_the_second_table_is_reported(self, template_surface):
        row = "| `daisyui/a.html` | Draws a. | Application directories. |\n"
        surface = template_surface(PACK_TABLE + SUPPORTED_TABLE + row, self.FILES)

        assert surface.disagreements() == [
            ("listed twice", "daisyui/a.html"),
            ("wrong table", "daisyui/a.html"),
        ]

    def test_a_supported_template_in_the_pack_table_is_reported(self, template_surface):
        row = "| `django_tomselect/tomselect.html` | Draws it. | | `TEMPLATES` |\n"
        surface = template_surface(PACK_TABLE.rstrip("\n") + "\n" + row, self.FILES)

        assert surface.disagreements() == [
            ("wrong table", "django_tomselect/tomselect.html")
        ]

    def test_a_row_for_a_supported_template_removed_is_reported(self, template_surface):
        files = {"daisyui/a.html": PACK_TEMPLATE}
        surface = template_surface(PACK_TABLE + SUPPORTED_TABLE, files)

        assert surface.disagreements() == [
            ("not distributed", "django_tomselect/tomselect.html")
        ]
