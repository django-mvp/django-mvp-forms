"""Read the support window, hold the repository to it, and report on it."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from http.client import HTTPException
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DECLARATION = ROOT / "support-window.toml"
CLASS_DIRECTORY = ROOT / "tests" / "data"
TIMEOUT = 30
ASKED = {
    "django": "SUPPORT_WINDOW_DJANGO",
    "django-crispy-forms": "SUPPORT_WINDOW_CRISPY_FORMS",
}
SUITE_ARGUMENTS = ("-n", "auto", "--dist", "loadscope")
PACKAGES = ("django", "django-crispy-forms", "daisyui")
SOURCES = {
    "django": "https://pypi.org/pypi/Django/json",
    "django-crispy-forms": "https://pypi.org/pypi/django-crispy-forms/json",
    "daisyui": "https://registry.npmjs.org/daisyui",
}

VERSION = re.compile(r"[0-9]+\.[0-9]+")
CELL_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+)+")
NAME_SEPARATOR = re.compile(r"[-_.]+")
CLAUSE = re.compile(r"\s*(==|!=|~=|>=|<=|>|<)\s*([\w.*]+)\s*")
REQUIREMENT = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)")
DJANGO_CLASSIFIER = re.compile(r"Framework :: Django :: ([0-9]+\.[0-9]+)")
PYTHON_CLASSIFIER = re.compile(r"Programming Language :: Python :: ([0-9]+\.[0-9]+)")
SUPPORT_BLOCK = re.compile(
    r"<!-- support-window -->(.*?)<!-- /support-window -->", re.S
)
SEPARATOR = re.compile(r":?-+:?")
PATCH = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
COMMENT = re.compile(r"/\*.*?\*/", re.S)
LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|url\([^)\"']*\)")
PRELUDE_START = re.compile(r"[};]")
NAMED_AT_RULE = re.compile(r"\s*@(?:layer|container)\b")
CLASS_SELECTOR = re.compile(r"\.(?![0-9])((?:\\[0-9a-fA-F]{1,6}\s?|\\.|[\w-])+)")
HEX_ESCAPE = re.compile(r"\\([0-9a-fA-F]{1,6})\s?")
ESCAPE = re.compile(r"\\(.)")
DROPPED_BLOCK = re.compile(
    r"<!-- dropped-versions -->(.*?)<!-- /dropped-versions -->", re.S
)
RELEASE_HEADING = re.compile(r"^## \[v?([^\]]+)\]", re.M)
STATEMENT = re.compile(r"<!-- support-window -->.*<!-- /dropped-versions -->", re.S)
LINK_TARGET = re.compile(
    r"\]\(\s*(?:<([^>]*)>|([^)\s]+))"
    r"|(?:href|src)=[\"']([^\"']+)"
    r"|^\[[^\]]+\]:\s*(?:<([^>]*)>|(\S+))",
    re.M,
)
ABSOLUTE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
FINAL = re.compile(r"[0-9]{1,9}(?:\.[0-9]{1,9})*")
DAY = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def fetch_json(url: str) -> Any:
    """Fetch an address and read the answer as JSON.

    Args:
        url: A fixed https address.

    Returns:
        The parsed JSON.
    """
    with urlopen(url, timeout=TIMEOUT) as response:  # noqa: S310 fixed https address
        return json.load(response)


def fetch_text(url: str) -> str:
    """Fetch an address and read the answer as text.

    Args:
        url: An https address built from a version already matched as numbers.

    Returns:
        The text of the answer.
    """
    with urlopen(url, timeout=TIMEOUT) as response:  # noqa: S310 built from numbers
        return response.read().decode("utf-8")


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
class Dropped:
    """A version that has left the window.

    Args:
        package: The package the version belongs to: ``django``,
            ``django-crispy-forms`` or ``daisyui``.
        version: The version that left, such as ``5.2``.
        last_release: The last release of this package that supported it, such
            as ``0.1.0``.
    """

    package: str
    version: str
    last_release: str


@dataclass(frozen=True)
class Outstanding:
    """A release that the window does not name.

    Args:
        package: The package the release belongs to: ``django``,
            ``django-crispy-forms`` or ``daisyui``.
        version: The release series, such as ``6.2`` for Django or ``5.8`` for
            daisyUI.
        released: The day of the first final release of the series, such as
            ``2026-10-01``.
        new_major: True for the first series of a later major version of
            django-crispy-forms or daisyUI, which is reported apart.
    """

    package: str
    version: str
    released: str
    new_major: bool = False


@dataclass(frozen=True)
class Window:
    """The versions the package states it works with.

    Args:
        python: The Python versions the suite runs on, oldest first.
        django: The named Django release series, oldest first.
        django_first: The oldest Django series any release of this package
            supported.
        crispy_forms: The named django-crispy-forms releases, oldest first.
        crispy_forms_first: The oldest django-crispy-forms release any release
            of this package supported.
        pairs: For each named django-crispy-forms release, the named Django
            series it supports.
        daisyui_first: The oldest daisyUI minor release any release of this
            package supported.
        daisyui_minimum: The oldest daisyUI minor release named.
        daisyui_newest: The newest daisyUI minor release named.
        dropped: The versions that have left the window.
    """

    python: tuple[str, ...]
    django: tuple[str, ...]
    django_first: str
    crispy_forms: tuple[str, ...]
    crispy_forms_first: str
    pairs: dict[str, tuple[str, ...]]
    daisyui_first: str
    daisyui_minimum: str
    daisyui_newest: str
    dropped: tuple[Dropped, ...] = ()

    @classmethod
    def read(cls, path: Path) -> Window:
        """Read a window from a TOML file.

        Args:
            path: The file to read.

        Returns:
            The window the file declares.

        Raises:
            InvalidWindow: The file is refused as ``from_mapping`` refuses a
                mapping.
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
            InvalidWindow: A list of versions is empty, a version is not two
                numbers, the daisyUI minimum is above the newest, a ``first`` is
                above the oldest version named, a pair names a release or a
                Django series the window does not, or a dropped entry is
                malformed.
        """
        python = cls.named_versions("python", data["python"])
        django = cls.named_versions("django", data["django"]["versions"])
        (django_first,) = cls.parse_versions("django", [data["django"]["first"]])
        crispy = data["django-crispy-forms"]
        (crispy_forms_first,) = cls.parse_versions(
            "django-crispy-forms", [crispy["first"]]
        )
        crispy_forms = cls.named_versions("django-crispy-forms", crispy["versions"])
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
        (daisyui_first,) = cls.parse_versions("daisyui", [daisyui["first"]])
        (minimum,) = cls.parse_versions("daisyui", [daisyui["minimum"]])
        (newest,) = cls.parse_versions("daisyui", [daisyui["newest"]])
        if cls.numbers(minimum) > cls.numbers(newest):
            raise InvalidWindow("daisyui", minimum, "the minimum is above the newest")
        oldest = {
            "django": (django_first, django[0]),
            "django-crispy-forms": (crispy_forms_first, crispy_forms[0]),
            "daisyui": (daisyui_first, minimum),
        }
        for package, (first, named) in oldest.items():
            if cls.numbers(first) > cls.numbers(named):
                raise InvalidWindow(package, first, "first is above the oldest named")
        dropped = tuple(cls.parse_dropped(entry) for entry in data.get("dropped", []))
        return cls(
            python,
            django,
            django_first,
            crispy_forms,
            crispy_forms_first,
            pairs,
            daisyui_first,
            minimum,
            newest,
            dropped,
        )

    @classmethod
    def parse_dropped(cls, entry: dict[str, Any]) -> Dropped:
        """Check one dropped entry and read it.

        Args:
            entry: One ``[[dropped]]`` table as ``tomllib`` parses it.

        Returns:
            The version that left and the last release that supported it.

        Raises:
            InvalidWindow: The package is not one of the three, the version is not
                two numbers, or the last release is not three numbers.
        """
        package = str(entry.get("package", ""))
        version = str(entry.get("version", ""))
        if package not in PACKAGES:
            raise InvalidWindow(package, version, "not a package that can be dropped")
        (version,) = cls.parse_versions(package, [version])
        release = str(entry.get("last-release", ""))
        if not PATCH.fullmatch(release):
            raise InvalidWindow(package, version, "no last release such as 0.1.0")
        return Dropped(package, version, release)

    @staticmethod
    def named_versions(package: str, versions: list[str]) -> tuple[str, ...]:
        """Check that a window names at least one version of a package.

        Args:
            package: The package the versions belong to.
            versions: The versions as written.

        Returns:
            The versions, oldest first.

        Raises:
            InvalidWindow: The list is empty, or a version is not two numbers.
        """
        if not versions:
            raise InvalidWindow(package, "", "no version named")
        return Window.parse_versions(package, versions)

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
        return tuple(sorted(versions, key=Window.numbers))

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
            named version and nothing else, one with an empty version for each of
            Django and django-crispy-forms that no requirement names, and for
            each Django or Python
            classifier the window does not name or does not have, and for each
            dropped Django or django-crispy-forms version the requirements still
            admit.
        """
        project = pyproject["project"]
        found = []
        required = {
            "django": self.django[0],
            "django-crispy-forms": self.crispy_forms[0],
        }
        named = set()
        for requirement in project["dependencies"]:
            name, specifiers = REQUIREMENT.fullmatch(requirement).groups()
            package = NAME_SEPARATOR.sub("-", name).lower()
            if package in required:
                named.add(package)
                found += self.requirement_disagreements(
                    package, specifiers, required[package]
                )
                found += self.admitted_disagreements(package, specifiers)
        found += [
            Disagreement("metadata", package, "", f"no requirement names {package}")
            for package in required
            if package not in named
        ]
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

    def admitted_disagreements(
        self, package: str, specifiers: str
    ) -> list[Disagreement]:
        """Compare the dropped versions of a package with what its requirement admits.

        Args:
            package: The package the requirement is for.
            specifiers: The version specifiers, such as ``>=5.2``.

        Returns:
            One disagreement for each dropped version of the package that is not
            below the version the requirement asks for. None when the requirement
            has no ``>=`` clause, which ``requirement_disagreements`` names.
        """
        clauses = (CLAUSE.fullmatch(clause) for clause in specifiers.split(","))
        minimums = [m.group(2) for m in clauses if m and m.group(1) == ">="]
        floor = VERSION.match(minimums[0]) if minimums else None
        if floor is None:
            return []
        return [
            Disagreement(
                "metadata",
                package,
                entry.version,
                f"the requirement admits {entry.version}, which has left the window",
            )
            for entry in self.dropped
            if entry.package == package
            and self.numbers(entry.version) >= self.numbers(floor.group())
        ]

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
                for version in CELL_VERSION.findall(cell)
            }
            found += self.set_disagreements(
                "README", package, set(versions), stated, "the statement"
            )
        stated_pairs = {
            name: set(CELL_VERSION.findall(cell))
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
        return found + self.dropped_table_disagreements(readme)

    def dropped_table_disagreements(self, readme: str) -> list[Disagreement]:
        """Compare the table of dropped versions in the README with the window.

        The table is read between the ``dropped-versions`` comments. A row is
        ``| package | version | last release |`` and is found by the package
        named in its first cell. An empty table means no version has left.

        Args:
            readme: The text of the README.

        Returns:
            One disagreement for each dropped version the table lacks, for each
            version the table gives and the window does not drop, and for each
            dropped version listed with another last release. A README with no
            ``dropped-versions`` block is one disagreement, naming the block.
        """
        block = DROPPED_BLOCK.search(readme)
        found = []
        if block is None:
            found.append(
                Disagreement(
                    "README",
                    "dropped-versions",
                    "",
                    "the README has no dropped-versions block",
                )
            )
        rows = [
            cells
            for cells in self.table_cells(block.group(1) if block else "")
            if len(cells) >= 3 and cells[0].lower() in PACKAGES
        ]
        for package in PACKAGES:
            found += self.set_disagreements(
                "README",
                package,
                {d.version for d in self.dropped if d.package == package},
                {cells[1] for cells in rows if cells[0].lower() == package},
                "the table of dropped versions",
            )
        listed = {(cells[0].lower(), cells[1]): cells[2] for cells in rows}
        for entry in self.dropped:
            release = listed.get((entry.package, entry.version), entry.last_release)
            if release != entry.last_release:
                found.append(
                    Disagreement(
                        "README",
                        entry.package,
                        entry.version,
                        f"the table gives last release {release}, "
                        f"and the window gives {entry.last_release}",
                    )
                )
        return found

    def dropped_disagreements(self, changelog: str) -> list[Disagreement]:
        """Compare the dropped versions with the window and with the changelog.

        Every version from the oldest ever supported to the newest named is in
        the window or in the dropped list. For daisyUI the window starts at the
        minimum, so the versions below it are the ones that must be dropped.

        Args:
            changelog: The text of ``CHANGELOG.md``.

        Returns:
            One ``dropped`` disagreement for each version that is both named and
            dropped, and for each version in between that is neither. One
            ``changelog`` disagreement for each dropped version whose last
            release has no heading in the changelog, with or without a ``v``.
        """
        walks = {
            "django": (
                self.django_series_from(self.django_first, self.django[-1]),
                self.django,
            ),
            "django-crispy-forms": (
                self.minors_from(self.crispy_forms_first, self.crispy_forms[-1]),
                self.crispy_forms,
            ),
            "daisyui": (
                self.minors_from(self.daisyui_first, self.daisyui_newest),
                self.minors_from(self.daisyui_minimum, self.daisyui_newest),
            ),
        }
        found = []
        for package, (walk, named) in walks.items():
            dropped = {d.version for d in self.dropped if d.package == package}
            for version in sorted(dropped & set(named), key=self.numbers):
                found.append(
                    Disagreement(
                        "dropped", package, version, "both in the window and dropped"
                    )
                )
            for version in walk:
                if version not in named and version not in dropped:
                    found.append(
                        Disagreement(
                            "dropped",
                            package,
                            version,
                            "neither in the window nor dropped",
                        )
                    )
        recorded = set(RELEASE_HEADING.findall(changelog))
        for entry in self.dropped:
            if entry.last_release not in recorded:
                found.append(
                    Disagreement(
                        "changelog",
                        entry.package,
                        entry.version,
                        f"the changelog has no release {entry.last_release}",
                    )
                )
        return found

    def lockfile_disagreements(self, lock: dict[str, Any]) -> list[Disagreement]:
        """Compare the versions the lockfile holds with the window.

        Args:
            lock: The parsed ``uv.lock``.

        Returns:
            One disagreement for each locked Django or django-crispy-forms
            whose release series the window does not name, giving the version
            as locked, and one with an empty version for each of the two that
            the lock has no entry for.
        """
        named = {"django": self.django, "django-crispy-forms": self.crispy_forms}
        locked = {entry["name"] for entry in lock["package"]}
        missing = [
            Disagreement(
                "lockfile", package, "", f"the lock has no entry for {package}"
            )
            for package in named
            if package not in locked
        ]
        return missing + [
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

    def run_suite(
        self,
        django: str,
        crispy_forms: str,
        extra: Sequence[str] = SUITE_ARGUMENTS,
        run: Callable[..., Any] = subprocess.run,
    ) -> int:
        """Run the whole suite on one named Django and django-crispy-forms pair.

        The two versions are laid over the project's environment for that one
        command, so the development environment is left as it was. Both are
        also put in the environment of the run, where ``tests/conftest.py``
        reads them to stop a run that is on other versions.

        Args:
            django: The Django release series, such as ``5.2``.
            crispy_forms: The django-crispy-forms release, such as ``2.7``.
            extra: The arguments given to pytest.
            run: Runs a command and returns an object with a ``returncode``.

        Returns:
            The status of the run, or ``2`` when the window does not offer the
            pair, in which case nothing is run.
        """
        offered = (
            django in self.django
            and crispy_forms in self.crispy_forms
            and django in self.pairs.get(crispy_forms, ())
        )
        if not offered:
            print(
                f"The window does not offer Django {django} with "
                f"django-crispy-forms {crispy_forms}.",
                file=sys.stderr,
            )
            return 2
        command = [
            "uv",
            "run",
            "--isolated",
            "--with",
            f"django=={django}.*",
            "--with",
            f"django-crispy-forms=={crispy_forms}.*",
            "pytest",
            *extra,
        ]
        environment = {
            **os.environ,
            ASKED["django"]: django,
            ASKED["django-crispy-forms"]: crispy_forms,
        }
        return run(command, env=environment, cwd=ROOT, check=False).returncode

    def outstanding(
        self,
        django: Mapping[str, str],
        crispy_forms: Mapping[str, str],
        daisyui: Mapping[str, str],
    ) -> list[Outstanding]:
        """List the releases the window does not name.

        Args:
            django: The final releases of Django, as ``final_releases`` gives
                them.
            crispy_forms: The final releases of django-crispy-forms.
            daisyui: The final releases of daisyUI.

        Returns:
            Every Django series newer than the newest named, every feature
            release of django-crispy-forms and every minor release of daisyUI
            newer than the newest named on the same major version, and the first
            series of each later major version of the last two with
            ``new_major`` set. A newer patch release of a named version is not
            one of them.
        """
        return [
            *self.later_series("django", django, self.django[-1], False),
            *self.later_series(
                "django-crispy-forms", crispy_forms, self.crispy_forms[-1], True
            ),
            *self.later_series("daisyui", daisyui, self.daisyui_newest, True),
        ]

    def report_releases(
        self,
        fetch: Callable[[str], Any] = fetch_json,
        out: Callable[[str], object] = print,
    ) -> int:
        """Print the releases the window does not name and say how it ended.

        Args:
            fetch: Reads the JSON at an address, one of ``SOURCES``.
            out: Takes each line to print.

        Returns:
            ``2`` when a source could not be reached, when its answer could not
            be read, or when it lists no final release of the newest version the
            window names. ``1`` when a release the window does not name is
            outstanding, and ``0`` otherwise. A new major version is printed and
            does not change the status. A line says the window is current only
            when the status is ``0``.
        """
        listings: dict[str, dict[str, str]] = {}
        failed = False
        newest = {
            "django": self.django[-1],
            "django-crispy-forms": self.crispy_forms[-1],
            "daisyui": self.daisyui_newest,
        }
        for package, address in SOURCES.items():
            try:
                listings[package] = self.listing_with(
                    newest[package], final_releases(fetch(address), package), package
                )
            except (OSError, ValueError, HTTPException) as error:
                failed = True
                out(f"{package}: could not find out ({type(error).__name__})")
                listings[package] = {}
        found = self.outstanding(
            listings["django"], listings["django-crispy-forms"], listings["daisyui"]
        )
        for release in found:
            kind = "new major version" if release.new_major else "release"
            out(f"{release.package} {release.version}: {kind} of {release.released}")
        if failed:
            return 2
        if any(not release.new_major for release in found):
            return 1
        out("The window names the newest release of each package.")
        return 0

    @staticmethod
    def listing_with(
        newest: str, releases: dict[str, str], package: str
    ) -> dict[str, str]:
        """Check that a listing holds the newest version the window names.

        A listing without it cannot say that nothing newer exists.

        Args:
            newest: The newest series the window names, such as ``6.1``.
            releases: Each final release with the day it was published.
            package: The package the releases belong to.

        Returns:
            The listing, unchanged.

        Raises:
            ValueError: No release of the newest named series is listed.
        """
        if newest not in map(Window.series, releases):
            raise ValueError(f"{package}: {newest} is not listed")
        return releases

    @staticmethod
    def later_series(
        package: str,
        releases: Mapping[str, str],
        newest: str,
        major_is_new: bool,
    ) -> list[Outstanding]:
        """List the release series of a package that are newer than one.

        Args:
            package: The package the releases belong to.
            releases: Each final release with the day it was published.
            newest: The newest series the window names, such as ``2.7``.
            major_is_new: True when a later major version is reported apart,
                once, at its first series. False when every later series is
                reported.

        Returns:
            One outstanding release for each series newer than ``newest``,
            oldest first, dated by the first final release of the series.
        """
        first: dict[str, str] = {}
        for version, released in releases.items():
            series = Window.series(version)
            if VERSION.fullmatch(series) and Window.numbers(series) > Window.numbers(
                newest
            ):
                first[series] = min(released, first.get(series, released))
        found = []
        majors: set[int] = set()
        for series in sorted(first, key=Window.numbers):
            major = Window.numbers(series)[0]
            new_major = major_is_new and major > Window.numbers(newest)[0]
            if new_major and major in majors:
                continue
            majors.add(major)
            found.append(Outstanding(package, series, first[series], new_major))
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
    def table_cells(text: str) -> list[list[str]]:
        """Read the cells of the Markdown tables in a text.

        Args:
            text: Markdown that holds tables.

        Returns:
            The cells of every row that is not a header separator.
        """
        rows = []
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not SEPARATOR.fullmatch(cells[0]):
                rows.append(cells)
        return rows

    @staticmethod
    def table_rows(text: str) -> list[tuple[str, str]]:
        """Read the first two cells of the rows of the Markdown tables in a text.

        Args:
            text: Markdown that holds tables.

        Returns:
            The first two cells of every row that has two and is not a header
            separator.
        """
        return [
            (cells[0], cells[1])
            for cells in Window.table_cells(text)
            if len(cells) >= 2
        ]

    @staticmethod
    def numbers(version: str) -> tuple[int, ...]:
        """Read a version as numbers, so that ``5.10`` is after ``5.9``.

        Args:
            version: A version such as ``5.2``.

        Returns:
            The numbers of the version, such as ``(5, 2)``.
        """
        return tuple(map(int, version.split(".")))

    @staticmethod
    def django_series_from(first: str, newest: str) -> tuple[str, ...]:
        """List the Django release series from one to another.

        Django numbers its series ``A.0``, ``A.1``, ``A.2`` and then ``(A+1).0``.

        Args:
            first: The oldest series, such as ``5.2``.
            newest: The newest series, such as ``7.0``.

        Returns:
            Every series from ``first`` to ``newest``, such as ``5.2``, ``6.0``,
            ``6.1``, ``6.2`` and ``7.0``.
        """
        major, minor = Window.numbers(first)
        series = []
        while (major, minor) <= Window.numbers(newest):
            series.append(f"{major}.{minor}")
            major, minor = (major, minor + 1) if minor < 2 else (major + 1, 0)
        return tuple(series)

    @staticmethod
    def minors_from(first: str, newest: str) -> tuple[str, ...]:
        """List the releases of a package whose second number counts up.

        Args:
            first: The oldest release, such as ``2.7``.
            newest: The newest release, such as ``2.9``.

        Returns:
            Every release from ``first`` to ``newest``, such as ``2.7``, ``2.8``
            and ``2.9``. Empty when the two are on different major versions,
            because the releases of the older major version are not known.
        """
        major, low = first.split(".")
        newest_major, high = newest.split(".")
        if major != newest_major:
            return ()
        return tuple(f"{major}.{minor}" for minor in range(int(low), int(high) + 1))

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
    package index, where the README is shown away from the repository. Inline
    links, reference definitions, ``href`` and ``src`` are read.

    Args:
        readme: The text of the README.

    Returns:
        The targets of the links that have no scheme, in the order they appear.
        Empty when the README has no statement.
    """
    statement = STATEMENT.search(readme)
    if statement is None:
        return []
    targets = (
        match.group(match.lastindex)
        for match in LINK_TARGET.finditer(statement.group())
    )
    return [target for target in targets if not ABSOLUTE.match(target)]


class MissingClassList(LookupError):
    """There is no class list for a daisyUI version.

    Args:
        version: The daisyUI version that has no list.

    Attributes:
        version: The daisyUI version that has no list.
    """

    def __init__(self, version: str) -> None:
        super().__init__(f"daisyUI {version} has no class list")
        self.version = version


def final_releases(payload: Any, source: str) -> dict[str, str]:
    """Read the final releases of a package from the answer of its source.

    A final release is a version of digits and dots, each number of at most nine
    digits, so ``6.2a1`` and ``5.8.0-beta.0`` are left out, and so are the
    ``created`` and ``modified`` entries that the npm registry keeps beside its
    versions.

    Args:
        payload: The JSON of the package index for Django and
            django-crispy-forms, or of the npm registry for daisyUI.
        source: The package the payload is for, a key of ``SOURCES``.

    Returns:
        Each final release with the day it was first published. For the package
        index that is the day of the earliest file of the release, and a release
        with no files is left out.

    Raises:
        ValueError: The payload is not the shape the source gives, or it lists no
            final release, or a release has no readable date.
    """
    try:
        if source == "daisyui":
            stamps = {version: [stamp] for version, stamp in payload["time"].items()}
        else:
            stamps = {
                version: [file["upload_time_iso_8601"] for file in files]
                for version, files in payload["releases"].items()
            }
        days = {
            version: min(stamp[:10] for stamp in times)
            for version, times in stamps.items()
            if FINAL.fullmatch(version) and times
        }
        readable = all(DAY.fullmatch(day) for day in days.values())
    except (AttributeError, KeyError, TypeError) as error:
        raise ValueError(f"{source}: the answer is not the shape expected") from error
    if not readable:
        raise ValueError(f"{source}: a release has no readable date")
    if not days:
        raise ValueError(f"{source}: the answer lists no final release")
    return days


def class_names(stylesheet: str) -> set[str]:
    """List the class selectors of a stylesheet with CSS escapes undone.

    Only the selector in front of each ``{`` is read, so a dot in a number, a
    string or an address in a declaration is never taken for a class, and the
    name after ``@layer`` or ``@container`` is not one either.

    Args:
        stylesheet: The text of the stylesheet.

    Returns:
        The class names, such as ``md:flex-row`` for ``.md\\:flex-row`` and
        ``2xl:btn`` for ``.\\32 xl\\:btn``.
    """
    text = LITERAL.sub("", COMMENT.sub("", stylesheet))
    names = set()
    for chunk in text.split("{")[:-1]:
        prelude = PRELUDE_START.split(chunk)[-1]
        if NAMED_AT_RULE.match(prelude):
            continue
        for escaped in CLASS_SELECTOR.findall(prelude):
            unescaped = HEX_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), escaped)
            names.add(ESCAPE.sub(r"\1", unescaped))
    return names


def class_list(version: str, directory: Path = CLASS_DIRECTORY) -> set[str]:
    """Read the class list kept for a daisyUI version.

    Args:
        version: The daisyUI version, such as ``5.0``.
        directory: The directory that holds the lists.

    Returns:
        The class names in ``daisyui-classes-<version>.txt``.

    Raises:
        MissingClassList: The directory has no list for the version.
    """
    path = directory / f"daisyui-classes-{version}.txt"
    if not path.is_file():
        raise MissingClassList(version)
    lines = path.read_text(encoding="utf-8").splitlines()
    return {line for line in lines if line and not line.startswith("#")}


def write_class_list(
    version: str,
    fetch: Callable[[str], str] = fetch_text,
    registry: Callable[[str], Any] = fetch_json,
    directory: Path = CLASS_DIRECTORY,
) -> Path:
    """Write the class list of the newest patch release of a daisyUI version.

    Args:
        version: The daisyUI version, such as ``5.0``.
        fetch: Reads a stylesheet from its address.
        registry: Reads the npm registry's JSON from its address.
        directory: The directory to write the list to.

    Returns:
        The path of the list written.

    Raises:
        MissingClassList: The registry holds no release of the version.
        UnicodeEncodeError: The stylesheet holds a name that cannot be written.
            The list already there is left as it was.
    """
    Window.parse_versions("daisyui", [version])
    versions = registry("https://registry.npmjs.org/daisyui")["versions"]
    patches = [
        patch
        for patch in versions
        if PATCH.fullmatch(patch) and Window.series(patch) == version
    ]
    if not patches:
        raise MissingClassList(version)
    newest = max(patches, key=Window.numbers)
    address = f"https://cdn.jsdelivr.net/npm/daisyui@{newest}/daisyui.css"
    names = sorted(class_names(fetch(address)))
    header = (
        f"# Every class selector in daisyUI {newest}'s CDN stylesheet, one per line.\n"
        f"# Source: {address}\n"
        f"# Written by: uv run python support_window.py classes {version}\n"
    )
    path = directory / f"daisyui-classes-{version}.txt"
    path.write_bytes((header + "\n".join(names) + "\n").encode("utf-8"))
    return path


def main(
    argv: Sequence[str] | None = None,
    run: Callable[..., Any] = subprocess.run,
    declaration: Path = DECLARATION,
    fetch: Callable[[str], Any] = fetch_json,
) -> int:
    """Run a command of this module.

    Args:
        argv: The command line without the program name. Defaults to the
            arguments the program was started with.
        run: Runs a command, for the ``test`` command.
        declaration: The file that declares the window.
        fetch: Reads the JSON at an address, for the ``releases`` command.

    Returns:
        The exit status.
    """
    parser = argparse.ArgumentParser(
        prog="support_window.py", description="Work with the support window."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    suite = commands.add_parser(
        "test", help="run the whole suite on one named Django and django-crispy-forms"
    )
    suite.add_argument("django", help="a Django release series, such as 5.2")
    suite.add_argument(
        "crispy_forms", help="a django-crispy-forms release, such as 2.7"
    )
    suite.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="arguments for pytest, which replace the default of running in parallel",
    )
    commands.add_parser(
        "releases",
        help="say whether a release exists that the window does not name",
    )
    classes = commands.add_parser(
        "classes", help="write the class list of a daisyUI version"
    )
    classes.add_argument("version", help="a daisyUI version, such as 5.0")
    arguments = parser.parse_args(argv)
    if arguments.command == "classes":
        print(write_class_list(arguments.version))
        return 0
    if arguments.command == "releases":
        return Window.read(declaration).report_releases(fetch=fetch)
    return Window.read(declaration).run_suite(
        arguments.django,
        arguments.crispy_forms,
        arguments.extra or SUITE_ARGUMENTS,
        run=run,
    )


if __name__ == "__main__":
    sys.exit(main())
