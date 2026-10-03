"""The README's list of templates is true of the templates the pack distributes."""

from pathlib import Path

from mvp_forms.deprecation import WITHDRAWN
from tests.conftest import PACK_TEMPLATES
from tests.template_surface import TemplateSurface

README = Path(__file__).parents[2] / "README.md"


class TestTheListMatchesThePackage:
    surface = TemplateSurface(README.read_text(), PACK_TEMPLATES, WITHDRAWN)

    def test_the_list_and_the_package_do_not_differ(self):
        assert self.surface.disagreements() == []

    def test_every_row_says_what_its_template_draws(self):
        rows = self.surface.listed()

        assert rows
        assert [row["path"] for row in rows if not row["draws"].strip()] == []
