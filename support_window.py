"""Read the support window and hold the package metadata to it."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DECLARATION = ROOT / "support-window.toml"

VERSION = re.compile(r"\d+\.\d+")
CLAUSE = re.compile(r"\s*(==|!=|~=|>=|<=|>|<)\s*([\w.*]+)\s*")
REQUIREMENT = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)")
DJANGO_CLASSIFIER = re.compile(r"Framework :: Django :: (\d+\.\d+)")
PYTHON_CLASSIFIER = re.compile(r"Programming Language :: Python :: (\d+\.\d+)")
VERSIONS = re.compile(r"\d+\.\d+")
SUPPORT_BLOCK = re.compile(
    r"<!-- support-window -->(.*?)<!-- /support-window -->", re.S
)
SEPARATOR = re.compile(r":?-+:?")
STATEMENT = re.compile(r"<!-- support-window -->.*<!-- /dropped-versions -->", re.S)
LINK_TARGET = re.compile(r"\]\(\s*<?([^)\s>]+)|href=[\"']([^\"']+)")
ABSOLUTE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


class InvalidWindow(ValueError):
    """The declaration cannot be read as a support window.

    Args:
        package: The package whose version is at fault.
        version: The version as written.
        problem: What is wrong with it.

    Attributes:
        package: The package whose version is at fault.
        version: The version as written.
    """

    def __init__(self, package: str, version: str, problem: str) -> None:
        super().__init__(f"{package} {version}: {problem}")
        self.package = package
        self.version = version


@dataclass(frozen=True)
class Disagreement:
    """One place where a source differs from the declared window.

    Args:
        source: The thing compared with the window, such as ``"metadata"``.
        package: The package whose version differs.
        version: The version that differs.
        problem: A sentence for the person reading the failure.
    """

    source: str
    package: str
    version: str
    problem: str


@dataclass(frozen=True)
class Window:
    """The versions the package states it works with.

    Args:
        python: The Python versions the suite runs on, oldest first.
        django: The named Django release series, oldest first.
        crispy_forms: The named django-crispy-forms releases, oldest first.
        pairs: For each named django-crispy-forms release, the named Django
            series it supports.
        daisyui_minimum: The oldest daisyUI minor release named.
        daisyui_newest: The newest daisyUI minor release named.
    """

    python: tuple[str, ...]
    django: tuple[str, ...]
    crispy_forms: tuple[str, ...]
    pairs: dict[str, tuple[str, ...]]
    daisyui_minimum: str
    daisyui_newest: str

    @classmethod
    def read(cls, path: Path) -> Window:
        """Read a window from a TOML file.

        Args:
            path: The file to read.

        Returns:
            The window the file declares.

        Raises:
            InvalidWindow: The file declares a version that is not two numbers, or
                a pair that names a version the window does not.
        """
        with path.open("rb") as handle:
            return cls.from_mapping(tomllib.load(handle))

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Window:
        """Build a window from a parsed declaration.

        Args:
            data: The declaration as ``tomllib`` parses it.

        Returns:
            The window the mapping declares.

        Raises:
            InvalidWindow: A version is not two numbers, or a pair names a release
                or a Django series the window does not.
        """
        python = cls.parse_versions("python", data["python"])
        django = cls.parse_versions("django", data["django"]["versions"])
        crispy = data["django-crispy-forms"]
        crispy_forms = cls.parse_versions("django-crispy-forms", crispy["versions"])
        pairs = {}
        for release, series in crispy["pairs"].items():
            if release not in crispy_forms:
                raise InvalidWindow(
                    "django-crispy-forms", release, "a pair names a release not named"
                )
            pairs[release] = cls.parse_versions("django", series)
            for version in pairs[release]:
                if version not in django:
                    raise InvalidWindow(
                        "django", version, "a pair names a series not named"
                    )
        daisyui = data["daisyui"]
        minimum, newest = cls.parse_versions(
            "daisyui", [daisyui["minimum"], daisyui["newest"]]
        )
        return cls(python, django, crispy_forms, pairs, minimum, newest)

    @staticmethod
    def parse_versions(package: str, versions: list[str]) -> tuple[str, ...]:
        """Check that every version is two numbers and order them.

        Args:
            package: The package the versions belong to.
            versions: The versions as written.

        Returns:
            The versions, oldest first.

        Raises:
            InvalidWindow: A version is not two numbers, such as ``5.2.17``.
        """
        for version in versions:
            if not VERSION.fullmatch(version):
                raise InvalidWindow(package, version, "not a release series")
        return tuple(sorted(versions, key=lambda v: tuple(map(int, v.split(".")))))

    @property
    def daisyui(self) -> tuple[str, ...]:
        """The daisyUI versions the suite checks.

        Returns:
            The minimum then the newest, or the one when they are the same.
        """
        return tuple(dict.fromkeys((self.daisyui_minimum, self.daisyui_newest)))

    def metadata_disagreements(self, pyproject: dict[str, Any]) -> list[Disagreement]:
        """Compare the package metadata with the window.

        Args:
            pyproject: The parsed ``pyproject.toml``.

        Returns:
            One disagreement for each requirement that is not ``>=`` the oldest
            named version and nothing else, and for each Django or Python
            classifier the window does not name or does not have.
        """
        project = pyproject["project"]
        found = []
        required = {
            "django": self.django[0],
            "django-crispy-forms": self.crispy_forms[0],
        }
        for requirement in project["dependencies"]:
            name, specifiers = REQUIREMENT.fullmatch(requirement).groups()
            if name.lower() in required:
                found += self.requirement_disagreements(
                    name.lower(), specifiers, required[name.lower()]
                )
        found += self.classifier_disagreements(
            "django", DJANGO_CLASSIFIER, self.django, project["classifiers"]
        )
        found += self.classifier_disagreements(
            "python", PYTHON_CLASSIFIER, self.python, project["classifiers"]
        )
        return found

    @staticmethod
    def requirement_disagreements(
        package: str, specifiers: str, minimum: str
    ) -> list[Disagreement]:
        """Compare one requirement with the oldest named version.

        Args:
            package: The package the requirement is for.
            specifiers: The version specifiers, such as ``>=5.2,<7``.
            minimum: The oldest named version, which the requirement must be
                ``>=`` and nothing else.

        Returns:
            One disagreement for each specifier other than ``>=`` the minimum.
        """
        found = []
        clauses = [clause for clause in specifiers.split(",") if clause.strip()]
        for clause in clauses:
            match = CLAUSE.fullmatch(clause)
            operator, version = match.groups() if match else ("", clause.strip())
            if (operator, version) != (">=", minimum):
                found.append(
                    Disagreement(
                        "metadata",
                        package,
                        version,
                        f"the requirement says {clause.strip()}, "
                        f"and the window asks for >={minimum} alone",
                    )
                )
        if not any(clause.strip().startswith(">=") for clause in clauses):
            found.append(
                Disagreement(
                    "metadata", package, minimum, f"the requirement has no >={minimum}"
                )
            )
        return found

    @staticmethod
    def classifier_disagreements(
        package: str,
        pattern: re.Pattern[str],
        named: tuple[str, ...],
        classifiers: list[str],
    ) -> list[Disagreement]:
        """Compare the classifiers of one kind with the named versions.

        Args:
            package: The package the classifiers advertise.
            pattern: Matches a classifier of this kind and captures its version.
            named: The versions the window names.
            classifiers: The classifiers from the package metadata.

        Returns:
            One disagreement for each version advertised and not named, and for
            each version named and not advertised.
        """
        advertised = {m.group(1) for c in classifiers if (m := pattern.fullmatch(c))}
        found = []
        for version in sorted(advertised - set(named)):
            found.append(
                Disagreement(
                    "metadata", package, version, "advertised and not in the window"
                )
            )
        for version in sorted(set(named) - advertised):
            found.append(
                Disagreement(
                    "metadata", package, version, "in the window and not advertised"
                )
            )
        return found

    def readme_disagreements(self, readme: str) -> list[Disagreement]:
        """Compare the statement in the README with the window.

        The statement is read between the ``support-window`` comments. A row of
        the first table is found by the package named in its first cell, and a
        row of the pairs table by the django-crispy-forms release in its first
        cell.

        Args:
            readme: The text of the README.

        Returns:
            One disagreement for each version the window names and the
            statement lacks, and for each version the statement gives and the
            window does not name. A README with no statement lacks them all.
        """
        block = SUPPORT_BLOCK.search(readme)
        rows = self.table_rows(block.group(1) if block else "")
        found = []
        named = {
            "django": self.django,
            "django-crispy-forms": self.crispy_forms,
            "daisyui": self.daisyui,
            "python": self.python,
        }
        for package, versions in named.items():
            stated = {
                version
                for name, cell in rows
                if name.lower() == package
                for version in VERSIONS.findall(cell)
            }
            found += self.set_disagreements(
                "README", package, set(versions), stated, "the statement"
            )
        stated_pairs = {
            name: set(VERSIONS.findall(cell))
            for name, cell in rows
            if VERSION.fullmatch(name)
        }
        declared_pairs = {
            release: set(series) for release, series in self.pairs.items()
        }
        found += self.set_disagreements(
            "README",
            "django-crispy-forms",
            set(declared_pairs),
            set(stated_pairs),
            "the pairs table",
        )
        for release in sorted(declared_pairs.keys() & stated_pairs.keys()):
            found += self.set_disagreements(
                "README",
                "django",
                declared_pairs[release],
                stated_pairs[release],
                f"the pairs table, on the row for django-crispy-forms {release}",
            )
        return found

    def lockfile_disagreements(self, lock: dict[str, Any]) -> list[Disagreement]:
        """Compare the versions the lockfile holds with the window.

        Args:
            lock: The parsed ``uv.lock``.

        Returns:
            One disagreement for each locked Django or django-crispy-forms
            whose release series the window does not name, giving the version
            as locked.
        """
        named = {"django": self.django, "django-crispy-forms": self.crispy_forms}
        return [
            Disagreement(
                "lockfile",
                entry["name"],
                entry["version"],
                "locked at a release the window does not name",
            )
            for entry in lock["package"]
            if entry["name"] in named
            and self.series(entry["version"]) not in named[entry["name"]]
        ]

    def installed_disagreements(
        self, installed: Mapping[str, str], asked: Mapping[str, str]
    ) -> list[Disagreement]:
        """Compare the installed versions with the window and with what was asked.

        Args:
            installed: The installed version of each of ``django`` and
                ``django-crispy-forms``, as ``installed_versions`` gives them.
            asked: The release series a run was asked to use, for the packages
                it was asked about. A package that is absent was not asked about.

        Returns:
            One disagreement for each package installed at a version that is not
            the series asked for, or, when none was asked for, at a series the
            window does not name. The version is given as installed.
        """
        named = {"django": self.django, "django-crispy-forms": self.crispy_forms}
        found = []
        for package, version in installed.items():
            if package in asked:
                if self.series(version) != asked[package]:
                    found.append(
                        Disagreement(
                            "installed",
                            package,
                            version,
                            f"the run was asked for {asked[package]}",
                        )
                    )
            elif self.series(version) not in named[package]:
                found.append(
                    Disagreement(
                        "installed",
                        package,
                        version,
                        "installed at a release the window does not name",
                    )
                )
        return found

    @staticmethod
    def series(version: str) -> str:
        """Reduce a version to its release series.

        Args:
            version: A version such as ``5.2.17``.

        Returns:
            The first two numbers, such as ``5.2``.
        """
        return ".".join(version.split(".")[:2])

    @staticmethod
    def table_rows(text: str) -> list[tuple[str, str]]:
        """Read the rows of the Markdown tables in a text.

        Args:
            text: Markdown that holds tables.

        Returns:
            The first two cells of every row that is not a header separator.
        """
        rows = []
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and not SEPARATOR.fullmatch(cells[0]):
                rows.append((cells[0], cells[1]))
        return rows

    @staticmethod
    def set_disagreements(
        source: str, package: str, declared: set[str], stated: set[str], place: str
    ) -> list[Disagreement]:
        """Compare the versions a source gives with the versions declared.

        Args:
            source: The thing compared with the window, such as ``"README"``.
            package: The package the versions belong to.
            declared: The versions the window names.
            stated: The versions the source gives.
            place: Where in the source the versions were read, for the sentence.

        Returns:
            One disagreement for each version in one set and not the other.
        """
        found = [
            Disagreement(source, package, version, f"in the window and not in {place}")
            for version in sorted(declared - stated)
        ]
        found += [
            Disagreement(source, package, version, f"in {place} and not in the window")
            for version in sorted(stated - declared)
        ]
        return found


def installed_versions() -> dict[str, str]:
    """Read the installed versions of Django and django-crispy-forms.

    Returns:
        The version of each package as ``importlib.metadata`` reports it, keyed
        by the package name.
    """
    return {
        package: metadata.version(package)
        for package in ("django", "django-crispy-forms")
    }


def relative_links(readme: str) -> list[str]:
    """List the links in the README's statement that are not absolute.

    The statement runs from the ``support-window`` comment to the end of the
    ``dropped-versions`` comment. A link that is not absolute breaks on the
    package index, where the README is shown away from the repository.

    Args:
        readme: The text of the README.

    Returns:
        The targets of the links that have no scheme, in the order they appear.
        Empty when the README has no statement.
    """
    statement = STATEMENT.search(readme)
    if statement is None:
        return []
    targets = (a or b for a, b in LINK_TARGET.findall(statement.group()))
    return [target for target in targets if not ABSOLUTE.match(target)]
