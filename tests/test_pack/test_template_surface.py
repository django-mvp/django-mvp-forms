"""The check that keeps the README's template list and the pack's templates true."""

import pytest

from tests.template_surface import TemplateSurface, UnreadTag

TABLE_HEAD = "| Template | Draws | Handed | Found by |\n|---|---|---|---|\n"


def readme(*rows):
    lines = [
        f"| `{path}` | It draws something. | {handed} | `{route}` |"
        for path, handed, route in rows
    ]
    return "### Replacing one template\n\n" + TABLE_HEAD + "\n".join(lines) + "\n"


class TestNamesRead:
    def test_a_variable_is_read_by_its_first_name(self, names_read):
        assert names_read("{{ a }}{{ b.c.d }}") == {"a", "b"}

    def test_a_tag_argument_is_read(self, names_read):
        source = "{% load daisyui %}{% daisyui_field field inline=flag %}"

        assert names_read(source) == {"field", "flag"}

    def test_a_filter_argument_is_read(self, names_read):
        assert names_read("{{ a|default:b }}") == {"a", "b"}

    def test_a_literal_and_true_false_and_none_are_not_names(self, names_read):
        source = '{{ "a" }}{{ 1 }}{{ True }}{{ False }}{{ None }}{{ x|default:"y" }}'

        assert names_read(source) == {"x"}

    def test_a_condition_reads_every_name_it_compares(self, names_read):
        source = (
            '{% if a and not b %}{% elif c.d == "s" or e in f %}'
            "{% else %}{{ g }}{% endif %}"
        )

        assert names_read(source) == {"a", "b", "c", "e", "f", "g"}

    def test_a_loop_binds_its_names_and_forloop_inside_its_body(self, names_read):
        source = (
            "{% for i, j in items.pairs %}{{ i }}{{ j }}{{ forloop.first }}{% endfor %}"
        )

        assert names_read(source) == {"items"}

    def test_a_loop_binds_nothing_in_its_empty_clause(self, names_read):
        source = "{% for i in items %}{% empty %}{{ i }}{{ forloop.first }}{% endfor %}"

        assert names_read(source) == {"items", "i", "forloop"}

    def test_a_with_binds_its_names_inside_its_body_only(self, names_read):
        source = "{% with x=a.b %}{{ x }}{% endwith %}{{ x }}"

        assert names_read(source) == {"a", "x"}

    def test_a_name_set_with_as_is_bound_for_what_follows_the_tag(self, names_read):
        source = (
            "{% load daisyui %}{{ later }}{% daisyui_field field as later %}"
            "{{ later }}{{ other }}"
        )

        assert names_read(source) == {"later", "field", "other"}

    def test_a_name_set_with_as_is_bound_inside_the_nodes_that_follow(self, names_read):
        source = (
            "{% load daisyui %}{% daisyui_field field as drawn %}"
            "{% if drawn.is_group %}{{ drawn.join }}{% endif %}"
        )

        assert names_read(source) == {"field"}

    def test_an_include_reads_its_with_values_and_binds_nothing(self, names_read):
        source = '{% include "a.html" with x=y %}{{ x }}'

        assert names_read(source) == {"y", "x"}

    def test_an_include_reads_the_name_of_the_template_it_is_given(self, names_read):
        assert names_read("{% include chosen %}") == {"chosen"}

    def test_csrf_token_reads_csrf_token(self, names_read):
        assert names_read("{% csrf_token %}") == {"csrf_token"}

    def test_drawn_and_table_come_back_one_level_down(self, names_read):
        source = (
            "{{ drawn.join.css_class }}{{ drawn.is_group }}{{ table.rows }}"
            "{{ field.auto_id }}"
        )

        assert names_read(source) == {
            "drawn.join",
            "drawn.is_group",
            "table.rows",
            "field",
        }

    def test_a_tag_that_holds_nodes_has_them_read(self, names_read):
        assert names_read("{% spaceless %}{{ a }}{% endspaceless %}") == {"a"}

    @pytest.mark.parametrize(
        "source",
        [
            "{% firstof a b %}",
            "{% url 'overview' a %}",
            "{% regroup a by b as c %}{{ c }}",
            "{% filter default:a %}{{ b }}{% endfilter %}",
        ],
    )
    def test_a_tag_it_cannot_read_is_refused(self, names_read, source):
        with pytest.raises(UnreadTag):
            names_read(source)


class TestDistributed:
    def test_every_template_under_the_directory_is_a_path_in_posix_form(
        self, template_surface
    ):
        surface = template_surface("", {"daisyui/b.html": "", "daisyui/x/a.html": ""})

        assert surface.distributed() == ["daisyui/b.html", "daisyui/x/a.html"]


class TestRendererRoute:
    def test_it_holds_what_the_form_renderer_loads_and_what_those_include(
        self, template_surface
    ):
        surface = template_surface(
            "",
            {
                "daisyui/widgets/group.html": '{% include "daisyui/shared.html" %}',
                "daisyui/shared.html": '{% include "daisyui/deeper.html" %}',
                "daisyui/deeper.html": "",
                "daisyui/widgets/unused.html": "",
                "daisyui/field.html": '{% include "daisyui/frame.html" %}',
            },
        )

        assert surface.renderer_route() == {
            "daisyui/widgets/group.html",
            "daisyui/shared.html",
            "daisyui/deeper.html",
            "daisyui/widgets/inline_group.html",
            "daisyui/widgets/select_date.html",
            "daisyui/widgets/clearable_file_input.html",
            "daisyui/widgets/rating.html",
            "mvp_forms/widgets/partial_date.html",
        }

    def test_an_include_by_a_name_is_not_followed(self, template_surface):
        surface = template_surface(
            "",
            {
                "daisyui/widgets/group.html": "{% include chosen %}",
                "chosen": "",
            },
        )

        assert "chosen" not in surface.renderer_route()


class TestListed:
    def test_a_row_is_its_path_what_it_draws_what_it_is_handed_and_its_route(
        self, template_surface
    ):
        text = (
            "intro\n\n### Replacing one template\n\n"
            + TABLE_HEAD
            + "| `daisyui/a.html` | Draws a. | `field`, `drawn.join` | `TEMPLATES` |\n"
            "| `daisyui/b.html` | Draws b. |  | `FORM_RENDERER` |\n"
            "\n### After\n\n| `daisyui/c.html` | no | `x` | `TEMPLATES` |\n"
        )
        surface = template_surface(text, {})

        assert surface.listed() == [
            {
                "path": "daisyui/a.html",
                "draws": "Draws a.",
                "handed": {"field", "drawn.join"},
                "route": "TEMPLATES",
            },
            {
                "path": "daisyui/b.html",
                "draws": "Draws b.",
                "handed": set(),
                "route": "FORM_RENDERER",
            },
        ]


class TestDisagreements:
    TEMPLATES = {"daisyui/a.html": "{{ field }}{{ drawn.join.css_class }}"}
    ROW = ("daisyui/a.html", "`field`, `drawn.join`", "TEMPLATES")

    def test_a_list_and_a_package_that_agree_have_none(self, template_surface):
        surface = template_surface(readme(self.ROW), self.TEMPLATES)

        assert surface.disagreements() == []

    def test_a_template_added_without_a_row_is_reported(self, template_surface):
        templates = {**self.TEMPLATES, "daisyui/new.html": ""}
        surface = template_surface(readme(self.ROW), templates)

        assert surface.disagreements() == [("not listed", "daisyui/new.html")]

    def test_a_row_for_a_template_removed_is_reported(self, template_surface):
        surface = template_surface(readme(self.ROW), {})

        assert surface.disagreements() == [("not distributed", "daisyui/a.html")]

    def test_a_template_renamed_is_reported_at_both_paths(self, template_surface):
        surface = template_surface(
            readme(self.ROW), {"daisyui/renamed.html": self.TEMPLATES["daisyui/a.html"]}
        )

        assert sorted(surface.disagreements()) == [
            ("not distributed", "daisyui/a.html"),
            ("not listed", "daisyui/renamed.html"),
        ]

    def test_a_name_read_that_the_row_leaves_out_is_reported_with_the_name(
        self, template_surface
    ):
        row = ("daisyui/a.html", "`field`", "TEMPLATES")
        surface = template_surface(readme(row), self.TEMPLATES)

        assert surface.disagreements() == [
            ("name not listed", "daisyui/a.html", "drawn.join")
        ]

    def test_a_name_listed_that_the_template_does_not_read_is_not_reported(
        self, template_surface
    ):
        row = ("daisyui/a.html", "`field`, `drawn.join`, `form`", "TEMPLATES")
        surface = template_surface(readme(row), self.TEMPLATES)

        assert surface.disagreements() == []

    def test_a_widget_template_listed_as_found_through_templates_is_reported(
        self, template_surface
    ):
        row = ("daisyui/widgets/group.html", "", "TEMPLATES")
        surface = template_surface(readme(row), {row[0]: ""})

        assert surface.disagreements() == [("wrong route", row[0])]

    def test_a_template_listed_as_found_by_the_renderer_is_reported(
        self, template_surface
    ):
        row = ("daisyui/a.html", "`field`, `drawn.join`", "FORM_RENDERER")
        surface = template_surface(readme(row), self.TEMPLATES)

        assert surface.disagreements() == [("wrong route", "daisyui/a.html")]

    def surface_with_withdrawn(self, template_surface, rows, withdrawn):
        built = template_surface(readme(*rows), self.TEMPLATES)
        return TemplateSurface(built.readme, built.templates_directory, withdrawn)

    def test_a_withdrawn_path_the_table_does_not_list_is_reported(
        self, template_surface
    ):
        gone = "daisyui/gone.html"
        surface = self.surface_with_withdrawn(template_surface, [self.ROW], [gone])

        assert surface.disagreements() == [("withdrawn not listed", gone)]

    def test_a_listed_path_that_is_withdrawn_is_not_reported_as_not_distributed(
        self, template_surface
    ):
        gone = ("daisyui/gone.html", "", "TEMPLATES")
        surface = self.surface_with_withdrawn(
            template_surface, [self.ROW, gone], [gone[0]]
        )

        assert surface.disagreements() == []

    def test_a_withdrawn_path_the_package_still_distributes_is_reported(
        self, template_surface
    ):
        surface = self.surface_with_withdrawn(
            template_surface, [self.ROW], [self.ROW[0]]
        )

        assert surface.disagreements() == [("withdrawn still distributed", self.ROW[0])]

    def test_a_path_with_two_rows_is_reported(self, template_surface):
        surface = template_surface(readme(self.ROW, self.ROW), self.TEMPLATES)

        assert surface.disagreements() == [("listed twice", self.ROW[0])]

    def test_a_listed_path_that_is_not_withdrawn_is_reported_as_not_distributed(
        self, template_surface
    ):
        gone = ("daisyui/gone.html", "", "TEMPLATES")
        surface = self.surface_with_withdrawn(template_surface, [self.ROW, gone], [])

        assert surface.disagreements() == [("not distributed", gone[0])]
