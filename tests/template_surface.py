"""Reads the pack's templates and the README's template list, and compares them."""

import re
from collections.abc import Collection
from pathlib import Path
from typing import Any

from django.template import Variable, engines
from django.template.base import TextNode
from django.template.defaulttags import (
    AutoEscapeControlNode,
    CommentNode,
    CsrfTokenNode,
    ForNode,
    IfNode,
    LoadNode,
    SpacelessNode,
    TemplateLiteral,
    WithNode,
)
from django.template.library import SimpleNode
from django.template.loader_tags import IncludeNode

from mvp_forms.templatetags.daisyui import FieldInput
from mvp_forms.widgets import PartialDateInput

LIST_HEADING = "### Replacing one template"
SUPPORTED_HEADING = "#### A supported package's templates"
PACK_DIRECTORY = ("daisyui/", "mvp_forms/")
SUPPORTED_DIRECTORIES = ("django_tomselect/",)
LITERAL_NAMES = {"True", "False", "None"}
PACKS_OWN_OBJECTS = {"drawn", "table"}
BACKTICKED = re.compile(r"`([^`]*)`")
TABLE_COLUMNS = 4
SUPPORTED_COLUMNS = 3
RENDERER_ROUTE = "FORM_RENDERER"
ENGINE_ROUTE = "TEMPLATES"
# Tags that read no name themselves. What they hold is read.
READS_NOTHING = (
    TextNode,
    CommentNode,
    LoadNode,
    SpacelessNode,
    AutoEscapeControlNode,
)


class UnreadTag(Exception):
    """A template uses a tag whose arguments ``TemplateSurface`` cannot read.

    Teach ``TemplateSurface.read_nodes`` the tag before a template uses it, so
    that a name it reads cannot go unlisted.
    """


class TemplateSurface:
    """The templates a package distributes, read against the README's list of them.

    It asserts nothing: ``disagreements`` returns every way the list and the
    package differ, and a test decides what to do with them.

    Args:
        readme: The text of the README holding the list.
        templates_directory: The directory the package's templates are in. A
            template's path is its path under this directory, as Django names it.
        withdrawn: The paths the package has moved away from. The package no
            longer distributes them, and the list still has a row for each.
    """

    def __init__(
        self,
        readme: str,
        templates_directory: Path,
        withdrawn: Collection[str] = (),
    ) -> None:
        self.readme = readme
        self.templates_directory = templates_directory
        self.withdrawn = set(withdrawn)

    def distributed(self) -> list[str]:
        """Return the path of every template under the directory.

        Returns:
            The paths, with forward slashes, in order.
        """
        return sorted(
            path.relative_to(self.templates_directory).as_posix()
            for path in self.templates_directory.rglob("*.html")
        )

    def names_read(self, source: str) -> set[str]:
        """Return the names a template reads from outside itself.

        The source is compiled with Django's engine and its nodes are walked with
        scope. A loop's variables and ``forloop`` inside its body, a ``with``'s
        names inside its body and a name set by a tag with ``as`` for the nodes
        after it are the template's own. A name is its first lookup, except
        ``drawn`` and ``table``, which come back with the part read, as
        ``drawn.join``.

        Args:
            source: The text of a template.

        Returns:
            The names the template is handed.

        Raises:
            UnreadTag: The template uses a tag this class has not been taught to
                read.
        """
        names: set[str] = set()
        nodelist = engines["django"].from_string(source).template.nodelist
        self.read_nodes(nodelist, frozenset(), names)
        return names

    def renderer_route(self) -> set[str]:
        """Return the paths the form renderer loads, not Django's template engine.

        These are the templates ``FieldInput`` names for a widget or for a
        rating, the template a widget of the package names for itself, and
        every template those include, by a literal name, however
        deep.

        Returns:
            The paths on the form renderer's route.
        """
        route: set[str] = set()
        pending = [
            *FieldInput.templates.values(),
            *FieldInput.inline_templates.values(),
            FieldInput.rating_template,
            PartialDateInput.template_name,
        ]
        while pending:
            path = pending.pop()
            if path in route:
                continue
            route.add(path)
            file = self.templates_directory / path
            if file.is_file():
                pending.extend(self.included_by(file.read_text()))
        return route

    def listed(self) -> list[dict[str, Any]]:
        """Return the rows of the README's table.

        Returns:
            One dict per row, in order, with ``path``, ``draws``, ``handed`` (a
            set of names) and ``route``, taken from the table in the README's
            section on replacing one template.
        """
        rows = []
        for cells in self.table_rows(TABLE_COLUMNS):
            rows.append(
                {
                    "path": cells[0].strip("`"),
                    "draws": cells[1],
                    "handed": set(BACKTICKED.findall(cells[2])),
                    "route": cells[3].strip("`"),
                }
            )
        return rows

    def listed_supported(self) -> list[dict[str, Any]]:
        """Return the rows of the README's table of a supported package's templates.

        Returns:
            One dict per row, in order, with ``path``, ``draws`` and ``found``,
            taken from the table under the heading that follows the pack's own.
        """
        section = self.readme.split(LIST_HEADING, 1)[1]
        if SUPPORTED_HEADING not in section:
            return []
        section = section.split(SUPPORTED_HEADING, 1)[1]
        section = re.split(r"^#{1,4} ", section, maxsplit=1, flags=re.M)[0]
        return [
            {"path": cells[0].strip("`"), "draws": cells[1], "found": cells[2]}
            for cells in self.table_rows(SUPPORTED_COLUMNS, section)
        ]

    def table_rows(self, columns: int, section: str | None = None) -> list[list[str]]:
        """Return the cells of each table row that begins with a template path.

        Args:
            columns: The number of cells a row has.
            section: The text to read. By default, the README's section on
                replacing one template, up to the next heading of the third
                level or above.

        Returns:
            The cells of each row, in order.
        """
        if section is None:
            section = self.readme.split(LIST_HEADING, 1)[1]
            section = re.split(r"^#{1,3} ", section, maxsplit=1, flags=re.M)[0]
        rows = []
        for line in section.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not line.startswith("|") or len(cells) != columns:
                continue
            if BACKTICKED.fullmatch(cells[0]):
                rows.append(cells)
        return rows

    def disagreements(self) -> list[tuple[str, ...]]:
        """Return every way the list and the package differ.

        A name the list gives a template that the template does not read is not a
        disagreement, and a withdrawn path is listed without being distributed. A
        template of a supported package is listed in a table of its own and is not
        read for the names it is handed, since it extends the supported package's
        template and reads nothing itself.

        Returns:
            Tuples naming the kind and the path, and the name for a name left out
            of a row: ``("not listed", path)``, ``("not distributed", path)``,
            ``("listed twice", path)``, ``("withdrawn not listed", path)``,
            ``("withdrawn still distributed", path)``,
            ``("name not listed", path, name)``, ``("wrong route", path)``,
            ``("wrong table", path)`` and ``("outside the directories", path)``.
        """
        pack_rows = {row["path"]: row for row in self.listed()}
        supported = [row["path"] for row in self.listed_supported()]
        listed = [row["path"] for row in self.listed()] + supported
        rows = {*pack_rows, *supported}
        distributed = self.distributed()
        route = self.renderer_route()
        found: list[tuple[str, ...]] = []
        found.extend(
            ("listed twice", path) for path in sorted(rows) if listed.count(path) > 1
        )
        found.extend(
            ("withdrawn still distributed", path)
            for path in distributed
            if path in self.withdrawn
        )
        found.extend(("not listed", path) for path in distributed if path not in rows)
        found.extend(
            ("not distributed", path)
            for path in sorted(rows)
            if path not in distributed and path not in self.withdrawn
        )
        found.extend(
            ("withdrawn not listed", path)
            for path in sorted(self.withdrawn)
            if path not in rows
        )
        for path in distributed:
            if path.startswith(PACK_DIRECTORY):
                if path in supported:
                    found.append(("wrong table", path))
            elif path.startswith(SUPPORTED_DIRECTORIES):
                if path in pack_rows:
                    found.append(("wrong table", path))
            else:
                found.append(("outside the directories", path))
            if path not in pack_rows or not path.startswith(PACK_DIRECTORY):
                continue
            handed = pack_rows[path]["handed"]
            source = (self.templates_directory / path).read_text()
            found.extend(
                ("name not listed", path, name)
                for name in sorted(self.names_read(source) - handed)
            )
            expected = RENDERER_ROUTE if path in route else ENGINE_ROUTE
            if pack_rows[path]["route"] != expected:
                found.append(("wrong route", path))
        return found

    def included_by(self, source: str) -> list[str]:
        """Return the paths a template includes by a literal name.

        Args:
            source: The text of a template.

        Returns:
            The paths written as a string in an ``{% include %}``.
        """
        paths: list[str] = []
        nodelist = engines["django"].from_string(source).template.nodelist
        pending = [nodelist]
        while pending:
            for node in pending.pop():
                if isinstance(node, IncludeNode) and not isinstance(
                    node.template.var, Variable
                ):
                    paths.append(str(node.template.var))
                for attribute in node.child_nodelists:
                    pending.append(getattr(node, attribute, None) or [])
        return paths

    def read_nodes(self, nodelist: Any, bound: frozenset[str], names: set[str]) -> None:
        """Add to ``names`` what the nodes read that ``bound`` does not hold.

        Args:
            nodelist: The nodes of a template or of one tag's body.
            bound: The names the template has set by this point.
            names: The set the names read are added to.

        Raises:
            UnreadTag: A node is of a tag this method does not know.
        """
        for node in nodelist:
            if isinstance(node, ForNode):
                self.read_expression(node.sequence, bound, names)
                inside = bound | {*node.loopvars, "forloop"}
                self.read_nodes(node.nodelist_loop, inside, names)
                self.read_nodes(node.nodelist_empty, bound, names)
            elif isinstance(node, WithNode):
                for value in node.extra_context.values():
                    self.read_expression(value, bound, names)
                inside = bound | set(node.extra_context)
                self.read_nodes(node.nodelist, inside, names)
            elif isinstance(node, IfNode):
                for condition, body in node.conditions_nodelists:
                    if condition is not None:
                        self.read_condition(condition, bound, names)
                    self.read_nodes(body, bound, names)
            elif isinstance(node, IncludeNode):
                self.read_expression(node.template, bound, names)
                for value in node.extra_context.values():
                    self.read_expression(value, bound, names)
            elif isinstance(node, SimpleNode):
                for value in [*node.args, *node.kwargs.values()]:
                    self.read_expression(value, bound, names)
                if node.target_var:
                    bound = bound | {node.target_var}
            elif isinstance(node, CsrfTokenNode):
                if "csrf_token" not in bound:
                    names.add("csrf_token")
            elif hasattr(node, "filter_expression"):
                self.read_expression(node.filter_expression, bound, names)
                # {% translate "..." as name %} sets a name for what follows.
                if getattr(node, "asvar", None):
                    bound = bound | {node.asvar}
            elif isinstance(node, READS_NOTHING):
                for attribute in node.child_nodelists:
                    self.read_nodes(getattr(node, attribute, None) or [], bound, names)
            else:
                raise UnreadTag(type(node).__name__)

    def read_condition(
        self, condition: Any, bound: frozenset[str], names: set[str]
    ) -> None:
        """Add to ``names`` what an ``{% if %}`` condition reads.

        Args:
            condition: A condition, which is an operator over conditions or a
                literal holding an expression.
            bound: The names the template has set by this point.
            names: The set the names read are added to.
        """
        if isinstance(condition, TemplateLiteral):
            self.read_expression(condition.value, bound, names)
            return
        for operand in (condition.first, condition.second):
            if operand is not None:
                self.read_condition(operand, bound, names)

    def read_expression(
        self, expression: Any, bound: frozenset[str], names: set[str]
    ) -> None:
        """Add to ``names`` what a variable, with its filters, reads.

        Args:
            expression: A ``FilterExpression``.
            bound: The names the template has set by this point.
            names: The set the names read are added to.
        """
        variables = [expression.var]
        for applied in expression.filters:
            # Each is the filter and its arguments, an argument a pair saying
            # whether it is looked up and what it is.
            variables.extend(value for looked_up, value in applied[1] if looked_up)
        for variable in variables:
            if not isinstance(variable, Variable) or variable.lookups is None:
                continue
            first, *rest = variable.lookups
            if first in LITERAL_NAMES or first in bound:
                continue
            names.add(
                f"{first}.{rest[0]}" if first in PACKS_OWN_OBJECTS and rest else first
            )
