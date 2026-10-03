"""Read the support window and hold the package metadata to it."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DECLARATION = ROOT / "support-window.toml"

VERSION = re.compile(r"\d+\.\d+")
CLAUSE = re.compile(r"\s*(==|!=|~=|>=|<=|>|<)\s*([\w.*]+)\s*")
REQUIREMENT = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)")
DJANGO_CLASSIFIER = re.compile(r"Framework :: Django :: (\d+\.\d+)")
PYTHON_CLASSIFIER = re.compile(r"Programming Language :: Python :: (\d+\.\d+)")
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
