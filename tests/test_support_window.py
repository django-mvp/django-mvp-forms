"""The support window is read from its declaration and held to the package metadata."""

import copy
import tomllib
from types import SimpleNamespace

import pytest

from support_window import (
    DECLARATION,
    ROOT,
    SOURCES,
    Dropped,
    InvalidWindow,
    MissingClassList,
    Window,
    class_list,
    class_names,
    django_series_from,
    final_releases,
    installed_versions,
    main,
    relative_links,
    write_class_list,
)

MAPPING = {
    "python": ["3.12", "3.13"],
    "django": {"first": "5.2", "versions": ["5.2", "6.0"]},
    "django-crispy-forms": {
        "first": "2.6",
        "versions": ["2.6", "2.7"],
        "pairs": {"2.6": ["5.2"], "2.7": ["5.2", "6.0"]},
    },
    "daisyui": {"first": "5.0", "minimum": "5.0", "newest": "5.4"},
}

CURRENT = {
    "python": ["3.12", "3.13"],
    "django": {"first": "5.2", "versions": ["5.2", "6.0", "6.1"]},
    "django-crispy-forms": {
        "first": "2.7",
        "versions": ["2.7"],
        "pairs": {"2.7": ["5.2", "6.0", "6.1"]},
    },
    "daisyui": {"first": "5.0", "minimum": "5.0", "newest": "5.7"},
}

CHANGELOG = "## [Unreleased]\n\n## [v0.1.0] - 2026-10-03\n"

DECLARATION_TEXT = """
python = ["3.12", "3.13"]

[django]
first = "5.2"
versions = ["5.2", "6.0"]

[django-crispy-forms]
first = "2.6"
versions = ["2.6", "2.7"]

[django-crispy-forms.pairs]
"2.6" = ["5.2"]
"2.7" = ["5.2", "6.0"]

[daisyui]
first = "5.0"
minimum = "5.0"
newest = "5.4"
"""


README = """# A package

<!-- support-window -->
| | Supported |
|---|---|
| Django | 5.2, 6.0, 6.1 |
| django-crispy-forms | 2.7 |
| daisyUI | 5.0 to 5.7 |
| Python | 3.12, 3.13 |

Each django-crispy-forms release works with the Django series on its row:

| django-crispy-forms | Django |
|---|---|
| 2.7 | 5.2, 6.0, 6.1 |
<!-- /support-window -->

<!-- dropped-versions -->
<!-- /dropped-versions -->
"""


@pytest.fixture
def declared():
    return copy.deepcopy(CURRENT)


@pytest.fixture
def pyproject():
    return {
        "project": {
            "dependencies": ["django>=5.2", "django-crispy-forms>=2.7"],
            "classifiers": [
                "Framework :: Django",
                "Framework :: Django :: 5.2",
                "Framework :: Django :: 6.0",
                "Framework :: Django :: 6.1",
                "Programming Language :: Python :: 3.12",
                "Programming Language :: Python :: 3.13",
            ],
        }
    }


@pytest.fixture
def readme():
    return README


@pytest.fixture
def lock():
    return {
        "package": [
            {"name": "django", "version": "6.1.1"},
            {"name": "django-crispy-forms", "version": "2.7"},
            {"name": "mvp-forms", "version": "0.1.0"},
        ]
    }


@pytest.fixture
def repository_declaration():
    with DECLARATION.open("rb") as handle:
        return tomllib.load(handle)


@pytest.fixture
def repository_pyproject():
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


@pytest.fixture
def repository_readme():
    return (ROOT / "README.md").read_text()


@pytest.fixture
def repository_changelog():
    return (ROOT / "CHANGELOG.md").read_text()


@pytest.fixture
def repository_lock():
    with (ROOT / "uv.lock").open("rb") as handle:
        return tomllib.load(handle)


def found(disagreements):
    return {(d.source, d.package, d.version) for d in disagreements}


def drop(package, version, release="0.1.0"):
    return {"package": package, "version": version, "last-release": release}


def mapping_starting_at_django_6_0(*dropped):
    mapping = copy.deepcopy(MAPPING)
    mapping["django"]["versions"] = ["6.0"]
    mapping["django-crispy-forms"]["pairs"] = {"2.6": [], "2.7": ["6.0"]}
    mapping["dropped"] = list(dropped)
    return mapping


class TestWindow:
    def test_a_window_built_from_a_mapping_has_the_versions_the_mapping_gave(self):
        window = Window.from_mapping(MAPPING)

        assert window.python == ("3.12", "3.13")
        assert window.django == ("5.2", "6.0")
        assert window.crispy_forms == ("2.6", "2.7")
        assert window.pairs == {"2.6": ("5.2",), "2.7": ("5.2", "6.0")}
        assert window.daisyui_minimum == "5.0"
        assert window.daisyui_newest == "5.4"

    def test_versions_are_ordered_by_number_not_by_text(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["django"]["versions"] = ["5.10", "5.2"]
        mapping["django-crispy-forms"]["pairs"] = {"2.6": ["5.2"], "2.7": ["5.10"]}

        assert Window.from_mapping(mapping).django == ("5.2", "5.10")

    def test_a_file_written_to_disk_reads_as_the_same_window(self, tmp_path):
        path = tmp_path / "window.toml"
        path.write_text(DECLARATION_TEXT)

        assert Window.read(path) == Window.from_mapping(MAPPING)

    def test_the_repositorys_declaration_reads_without_error(self):
        Window.read(DECLARATION)

    def test_the_daisyui_versions_checked_are_the_minimum_then_the_newest(self):
        assert Window.from_mapping(MAPPING).daisyui == ("5.0", "5.4")

    def test_the_daisyui_version_is_checked_once_when_the_ends_are_the_same(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["daisyui"]["newest"] = "5.0"

        assert Window.from_mapping(mapping).daisyui == ("5.0",)

    @pytest.mark.parametrize(
        ("package", "version"),
        [
            ("django", "5.2.17"),
            ("django-crispy-forms", "2.7.1"),
            ("daisyui", "5.7.47"),
        ],
    )
    def test_a_version_written_with_a_patch_number_is_refused(self, package, version):
        mapping = copy.deepcopy(MAPPING)
        if package == "daisyui":
            mapping["daisyui"]["newest"] = version
        else:
            mapping[package]["versions"].append(version)

        with pytest.raises(InvalidWindow) as raised:
            Window.from_mapping(mapping)

        assert raised.value.package == package
        assert raised.value.version == version

    def test_a_pair_naming_a_release_the_window_does_not_name_is_refused(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["django-crispy-forms"]["pairs"]["2.8"] = ["5.2"]

        with pytest.raises(InvalidWindow) as raised:
            Window.from_mapping(mapping)

        assert raised.value.package == "django-crispy-forms"
        assert raised.value.version == "2.8"

    def test_a_pair_naming_a_django_series_the_window_does_not_name_is_refused(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["django-crispy-forms"]["pairs"]["2.7"].append("6.1")

        with pytest.raises(InvalidWindow) as raised:
            Window.from_mapping(mapping)

        assert raised.value.package == "django"
        assert raised.value.version == "6.1"

    def test_the_oldest_version_ever_supported_is_read_for_each_package(self):
        window = Window.from_mapping(MAPPING)

        assert window.django_first == "5.2"
        assert window.crispy_forms_first == "2.6"
        assert window.daisyui_first == "5.0"

    def test_a_window_with_no_dropped_table_has_no_dropped_version(self):
        assert Window.from_mapping(MAPPING).dropped == ()

    def test_a_dropped_table_is_read_as_the_version_and_its_last_release(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["dropped"] = [drop("django", "5.0", "0.3.1")]

        assert Window.from_mapping(mapping).dropped == (
            Dropped("django", "5.0", "0.3.1"),
        )

    @pytest.mark.parametrize(
        ("entry", "package", "version"),
        [
            (drop("flask", "3.0"), "flask", "3.0"),
            (drop("django", "5.0.1"), "django", "5.0.1"),
            ({"package": "django", "version": "5.0"}, "django", "5.0"),
            (drop("django", "5.0", "latest"), "django", "5.0"),
            (drop("django", "5.0", "0.1"), "django", "5.0"),
        ],
    )
    def test_a_malformed_dropped_table_is_refused(self, entry, package, version):
        mapping = copy.deepcopy(MAPPING)
        mapping["dropped"] = [entry]

        with pytest.raises(InvalidWindow) as raised:
            Window.from_mapping(mapping)

        assert raised.value.package == package
        assert raised.value.version == version


class TestMetadata:
    def test_the_repositorys_metadata_agrees_with_its_declaration(
        self, repository_declaration, repository_pyproject
    ):
        window = Window.from_mapping(repository_declaration)

        assert window.metadata_disagreements(repository_pyproject) == []

    def test_metadata_written_for_a_window_agrees_with_it(self, declared, pyproject):
        window = Window.from_mapping(declared)

        assert window.metadata_disagreements(pyproject) == []

    def test_a_django_series_added_to_the_window_is_named(self, declared, pyproject):
        declared["django"]["versions"].append("6.2")
        window = Window.from_mapping(declared)

        assert ("metadata", "django", "6.2") in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_django_series_removed_from_the_window_is_named(
        self, declared, pyproject
    ):
        removed = declared["django"]["versions"].pop()
        for series in declared["django-crispy-forms"]["pairs"].values():
            series.remove(removed)
        window = Window.from_mapping(declared)

        assert ("metadata", "django", removed) in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_raised_crispy_forms_minimum_names_the_version_the_metadata_requires(
        self, declared, pyproject
    ):
        crispy = declared["django-crispy-forms"]
        required = crispy["versions"][0]
        crispy["versions"] = ["2.99"]
        crispy["pairs"] = {"2.99": declared["django"]["versions"]}
        window = Window.from_mapping(declared)

        assert ("metadata", "django-crispy-forms", required) in found(
            window.metadata_disagreements(pyproject)
        )

    def test_an_upper_limit_on_django_is_a_disagreement(self, declared, pyproject):
        pyproject["project"]["dependencies"] = [
            "django>=5.2,<7",
            "django-crispy-forms>=2.7",
        ]
        window = Window.from_mapping(declared)

        assert ("metadata", "django", "7") in found(
            window.metadata_disagreements(pyproject)
        )

    def test_an_upper_limit_on_crispy_forms_is_a_disagreement(
        self, declared, pyproject
    ):
        pyproject["project"]["dependencies"] = [
            "django>=5.2",
            "django-crispy-forms>=2.7,<3",
        ]
        window = Window.from_mapping(declared)

        assert ("metadata", "django-crispy-forms", "3") in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_pinned_requirement_is_a_disagreement(self, declared, pyproject):
        pyproject["project"]["dependencies"] = [
            "django==5.2",
            "django-crispy-forms>=2.7",
        ]
        window = Window.from_mapping(declared)

        assert ("metadata", "django", "5.2") in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_python_version_added_to_the_window_is_named(self, declared, pyproject):
        declared["python"].append("3.14")
        window = Window.from_mapping(declared)

        assert ("metadata", "python", "3.14") in found(
            window.metadata_disagreements(pyproject)
        )

    @pytest.mark.parametrize(
        ("package", "version"),
        [("django", "5.2"), ("django-crispy-forms", "2.7")],
    )
    def test_a_dropped_version_the_requirement_still_admits_is_named(
        self, declared, pyproject, package, version
    ):
        declared["dropped"] = [drop(package, version)]
        window = Window.from_mapping(declared)

        assert ("metadata", package, version) in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_dropped_version_below_the_requirements_minimum_is_not_named(
        self, declared, pyproject
    ):
        declared["dropped"] = [drop("django", "5.0")]
        window = Window.from_mapping(declared)

        assert found(window.metadata_disagreements(pyproject)) == set()


def section(*links):
    body = "\n".join(f"[a link]({link})" for link in links)
    return (
        "[before](docs/before.md)\n\n<!-- support-window -->\n"
        f"| | Supported |\n<!-- /support-window -->\n{body}\n"
        "<!-- dropped-versions -->\n<!-- /dropped-versions -->\n"
        "\n[after](docs/after.md)\n"
    )


class TestReadmeLinks:
    def test_the_section_of_the_repositorys_readme_holds_no_relative_link(
        self, repository_readme
    ):
        assert relative_links(repository_readme) == []

    def test_a_relative_link_in_the_section_is_returned(self):
        assert relative_links(section("docs/support.md")) == ["docs/support.md"]

    def test_an_anchor_in_the_section_is_returned(self):
        assert relative_links(section("#installation")) == ["#installation"]

    def test_an_absolute_link_in_the_section_is_not_returned(self):
        links = section("https://github.com/django-mvp/django-mvp-forms/issues/1")

        assert relative_links(links) == []

    def test_a_relative_link_outside_the_section_is_not_returned(self):
        assert relative_links(section()) == []

    def test_a_readme_with_no_section_has_no_relative_link(self):
        assert relative_links("[a link](docs/support.md)") == []


def with_dropped_rows(readme, *rows):
    table = "| Package | Version | Last release |\n|---|---|---|\n" + "".join(
        f"| {package} | {version} | {release} |\n" for package, version, release in rows
    )
    marker = "<!-- dropped-versions -->\n"
    return readme.replace(marker, marker + table)


class TestReadme:
    def test_the_repositorys_readme_agrees_with_its_declaration(
        self, repository_declaration, repository_readme
    ):
        window = Window.from_mapping(repository_declaration)

        assert window.readme_disagreements(repository_readme) == []

    def test_a_readme_written_for_a_window_agrees_with_it(self, declared, readme):
        window = Window.from_mapping(declared)

        assert window.readme_disagreements(readme) == []

    def test_a_django_series_added_to_the_window_is_named(self, declared, readme):
        declared["django"]["versions"].append("6.2")
        window = Window.from_mapping(declared)

        assert ("README", "django", "6.2") in found(window.readme_disagreements(readme))

    def test_a_django_series_removed_from_the_window_is_named(self, declared, readme):
        removed = declared["django"]["versions"].pop()
        for series in declared["django-crispy-forms"]["pairs"].values():
            series.remove(removed)
        window = Window.from_mapping(declared)

        assert ("README", "django", removed) in found(
            window.readme_disagreements(readme)
        )

    def test_a_crispy_forms_release_added_to_the_window_is_named(
        self, declared, readme
    ):
        crispy = declared["django-crispy-forms"]
        crispy["versions"].append("2.8")
        crispy["pairs"]["2.8"] = declared["django"]["versions"]
        window = Window.from_mapping(declared)

        assert ("README", "django-crispy-forms", "2.8") in found(
            window.readme_disagreements(readme)
        )

    def test_a_raised_daisyui_minimum_names_both_versions_that_differ(
        self, declared, readme
    ):
        declared["daisyui"]["minimum"] = "5.1"
        window = Window.from_mapping(declared)

        assert {
            d.version
            for d in window.readme_disagreements(readme)
            if d.package == "daisyui"
        } == {"5.0", "5.1"}

    def test_a_lowered_daisyui_newest_names_both_versions_that_differ(
        self, declared, readme
    ):
        declared["daisyui"]["newest"] = "5.6"
        window = Window.from_mapping(declared)

        assert {
            d.version
            for d in window.readme_disagreements(readme)
            if d.package == "daisyui"
        } == {"5.6", "5.7"}

    def test_a_python_version_added_to_the_window_is_named(self, declared, readme):
        declared["python"].append("3.14")
        window = Window.from_mapping(declared)

        assert ("README", "python", "3.14") in found(
            window.readme_disagreements(readme)
        )

    def test_a_django_series_removed_from_a_pair_is_named(self, declared, readme):
        declared["django-crispy-forms"]["pairs"]["2.7"].remove("6.1")
        window = Window.from_mapping(declared)

        assert ("README", "django", "6.1") in found(window.readme_disagreements(readme))

    def test_a_pair_removed_from_the_window_is_named(self, declared, readme):
        declared["django-crispy-forms"]["pairs"] = {}
        window = Window.from_mapping(declared)

        assert ("README", "django-crispy-forms", "2.7") in found(
            window.readme_disagreements(readme)
        )

    def test_a_readme_with_no_marked_block_is_a_disagreement(self, declared):
        window = Window.from_mapping(declared)

        assert ("README", "django", "5.2") in found(
            window.readme_disagreements("# a README with no statement")
        )

    def test_a_dropped_version_missing_from_the_table_is_named(self, declared, readme):
        declared["dropped"] = [drop("django", "5.0")]
        window = Window.from_mapping(declared)

        assert ("README", "django", "5.0") in found(window.readme_disagreements(readme))

    def test_a_dropped_version_in_the_table_that_the_declaration_keeps_is_named(
        self, declared, readme
    ):
        window = Window.from_mapping(declared)
        listed = with_dropped_rows(readme, ("django", "5.0", "0.1.0"))

        assert ("README", "django", "5.0") in found(window.readme_disagreements(listed))

    def test_a_dropped_version_with_another_last_release_is_named(
        self, declared, readme
    ):
        declared["dropped"] = [drop("django", "5.0", "0.1.0")]
        window = Window.from_mapping(declared)
        listed = with_dropped_rows(readme, ("django", "5.0", "0.2.0"))

        assert ("README", "django", "5.0") in found(window.readme_disagreements(listed))

    def test_a_dropped_version_listed_with_its_last_release_is_no_disagreement(
        self, declared, readme
    ):
        declared["dropped"] = [drop("django", "5.0", "0.1.0")]
        window = Window.from_mapping(declared)
        listed = with_dropped_rows(readme, ("django", "5.0", "0.1.0"))

        assert window.readme_disagreements(listed) == []

    def test_a_readme_with_no_dropped_versions_block_is_a_disagreement(
        self, declared, readme
    ):
        window = Window.from_mapping(declared)
        unmarked = readme.replace("<!-- dropped-versions -->", "").replace(
            "<!-- /dropped-versions -->", ""
        )

        assert ("README", "dropped-versions", "") in found(
            window.readme_disagreements(unmarked)
        )


def locked(lock, package, version):
    lock = copy.deepcopy(lock)
    for entry in lock["package"]:
        if entry["name"] == package:
            entry["version"] = version
    return lock


class TestLockfile:
    def test_the_repositorys_lockfile_agrees_with_its_declaration(
        self, repository_declaration, repository_lock
    ):
        window = Window.from_mapping(repository_declaration)

        assert window.lockfile_disagreements(repository_lock) == []

    def test_a_lock_written_for_a_window_agrees_with_it(self, declared, lock):
        window = Window.from_mapping(declared)

        assert window.lockfile_disagreements(lock) == []

    def test_a_locked_django_outside_the_window_is_named(self, declared, lock):
        window = Window.from_mapping(declared)

        assert ("lockfile", "django", "7.0.1") in found(
            window.lockfile_disagreements(locked(lock, "django", "7.0.1"))
        )

    def test_a_locked_crispy_forms_outside_the_window_is_named(self, declared, lock):
        window = Window.from_mapping(declared)

        assert ("lockfile", "django-crispy-forms", "3.0") in found(
            window.lockfile_disagreements(locked(lock, "django-crispy-forms", "3.0"))
        )


class TestInstalled:
    def test_the_versions_this_run_is_on_are_inside_the_window(
        self, repository_declaration
    ):
        window = Window.from_mapping(repository_declaration)

        assert window.installed_disagreements(installed_versions(), {}) == []

    def test_an_installed_django_outside_the_window_is_named(self, declared):
        window = Window.from_mapping(declared)
        installed = {"django": "7.0", "django-crispy-forms": "2.7"}

        assert ("installed", "django", "7.0") in found(
            window.installed_disagreements(installed, {})
        )

    def test_an_installed_django_that_is_not_the_one_asked_for_is_named(self, declared):
        window = Window.from_mapping(declared)
        installed = {"django": "6.1.1", "django-crispy-forms": "2.7"}

        assert ("installed", "django", "6.1.1") in found(
            window.installed_disagreements(installed, {"django": "5.2"})
        )

    def test_a_patch_release_of_the_django_asked_for_is_no_disagreement(self, declared):
        window = Window.from_mapping(declared)
        installed = {"django": "5.2.17", "django-crispy-forms": "2.7"}

        assert window.installed_disagreements(installed, {"django": "5.2"}) == []

    def test_an_installed_crispy_forms_that_is_not_the_one_asked_for_is_named(
        self, declared
    ):
        window = Window.from_mapping(declared)
        installed = {"django": "5.2.17", "django-crispy-forms": "2.8"}

        assert ("installed", "django-crispy-forms", "2.8") in found(
            window.installed_disagreements(installed, {"django-crispy-forms": "2.7"})
        )

    def test_the_crispy_forms_release_asked_for_is_no_disagreement(self, declared):
        window = Window.from_mapping(declared)
        installed = {"django": "5.2.17", "django-crispy-forms": "2.7"}

        assert (
            window.installed_disagreements(installed, {"django-crispy-forms": "2.7"})
            == []
        )


class TestClassNames:
    def test_an_escaped_colon_is_undone(self):
        assert class_names(r".md\:flex-row { display: flex }") == {"md:flex-row"}

    def test_an_escaped_leading_digit_is_undone(self):
        assert class_names(r".\32 xl\:btn { display: flex }") == {"2xl:btn"}

    def test_a_number_with_a_decimal_point_in_a_selector_is_not_a_class(self):
        sheet = "@media (min-width: 0.5em) { .wide { top: .5px } }"

        assert class_names(sheet) == {"wide"}

    def test_a_dot_in_a_declaration_is_not_a_class(self):
        sheet = ".logo { background: url(http://www.w3.org/logo.svg) }"

        assert class_names(sheet) == {"logo"}

    def test_every_class_of_a_compound_selector_is_found(self):
        sheet = ".btn.btn-primary:hover > .icon, :where(.menu) li { color: red }"

        assert class_names(sheet) == {"btn", "btn-primary", "icon", "menu"}


class TestClassLists:
    def test_every_named_daisyui_version_has_a_list_that_is_not_empty(
        self, daisyui_classes
    ):
        assert daisyui_classes

    def test_a_version_with_no_list_is_refused_with_the_version(self, tmp_path):
        with pytest.raises(MissingClassList) as raised:
            class_list("5.3", tmp_path)

        assert raised.value.version == "5.3"

    def test_a_list_written_for_a_version_is_the_newest_patch_releases(self, tmp_path):
        sheets = {
            "https://cdn.jsdelivr.net/npm/daisyui@5.3.10/daisyui.css": ".newest {}",
            "https://cdn.jsdelivr.net/npm/daisyui@5.3.9/daisyui.css": ".older {}",
        }
        registry = {
            "versions": {
                "5.2.99": {},
                "5.3.0": {},
                "5.3.9": {},
                "5.3.10": {},
                "5.3.11-beta.1": {},
                "5.4.0": {},
            }
        }

        write_class_list(
            "5.3",
            fetch=sheets.__getitem__,
            registry=lambda url: registry,
            directory=tmp_path,
        )

        assert class_list("5.3", tmp_path) == {"newest"}

    def test_a_minor_version_the_registry_does_not_know_is_refused(self, tmp_path):
        registry = {"versions": {"5.2.0": {}}}

        with pytest.raises(MissingClassList) as raised:
            write_class_list(
                "5.3",
                fetch=lambda url: "",
                registry=lambda url: registry,
                directory=tmp_path,
            )

        assert raised.value.version == "5.3"

    @pytest.mark.parametrize("version", ["5.3.1", "5", "../5.3", "5.x"])
    def test_a_version_that_is_not_two_numbers_is_refused_before_anything_is_fetched(
        self, tmp_path, version
    ):
        fetched = []

        def fetch(url):
            fetched.append(url)
            return ""

        with pytest.raises(InvalidWindow) as raised:
            write_class_list(version, fetch=fetch, registry=fetch, directory=tmp_path)

        assert raised.value.version == version
        assert fetched == []
        assert list(tmp_path.iterdir()) == []


class TestDropped:
    def test_the_repositorys_dropped_versions_agree_with_its_changelog(
        self, repository_declaration, repository_changelog
    ):
        window = Window.from_mapping(repository_declaration)

        assert window.dropped_disagreements(repository_changelog) == []

    def test_django_series_are_walked_from_one_release_to_the_next(self):
        assert django_series_from("5.2", "7.0") == ("5.2", "6.0", "6.1", "6.2", "7.0")

    def test_a_django_series_in_neither_the_window_nor_the_dropped_list_is_named(self):
        window = Window.from_mapping(mapping_starting_at_django_6_0())

        assert ("dropped", "django", "5.2") in found(
            window.dropped_disagreements(CHANGELOG)
        )

    def test_a_django_series_dropped_at_a_recorded_release_is_no_disagreement(self):
        window = Window.from_mapping(
            mapping_starting_at_django_6_0(drop("django", "5.2"))
        )

        assert window.dropped_disagreements(CHANGELOG) == []

    def test_a_release_heading_without_a_v_records_the_release(self):
        window = Window.from_mapping(
            mapping_starting_at_django_6_0(drop("django", "5.2"))
        )

        assert window.dropped_disagreements("## [0.1.0] - 2026-10-03\n") == []

    def test_a_django_series_both_named_and_dropped_is_named(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["dropped"] = [drop("django", "5.2")]
        window = Window.from_mapping(mapping)

        assert ("dropped", "django", "5.2") in found(
            window.dropped_disagreements(CHANGELOG)
        )

    def test_a_last_release_the_changelog_does_not_record_is_named(self):
        window = Window.from_mapping(
            mapping_starting_at_django_6_0(drop("django", "5.2", "9.9.9"))
        )

        assert ("changelog", "django", "5.2") in found(
            window.dropped_disagreements(CHANGELOG)
        )

    def test_the_unreleased_section_does_not_record_a_release(self):
        window = Window.from_mapping(
            mapping_starting_at_django_6_0(drop("django", "5.2", "0.2.0"))
        )

        assert ("changelog", "django", "5.2") in found(
            window.dropped_disagreements("## [Unreleased]\n\n## [v0.1.0]\n")
        )

    def test_every_daisyui_version_below_a_raised_minimum_is_named(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["daisyui"]["minimum"] = "5.2"
        window = Window.from_mapping(mapping)

        assert found(window.dropped_disagreements(CHANGELOG)) == {
            ("dropped", "daisyui", "5.0"),
            ("dropped", "daisyui", "5.1"),
        }

    def test_every_crispy_forms_release_below_the_window_is_named(self):
        mapping = copy.deepcopy(MAPPING)
        crispy = mapping["django-crispy-forms"]
        crispy["first"] = "2.7"
        crispy["versions"] = ["2.9"]
        crispy["pairs"] = {"2.9": ["5.2", "6.0"]}
        window = Window.from_mapping(mapping)

        assert found(window.dropped_disagreements(CHANGELOG)) == {
            ("dropped", "django-crispy-forms", "2.7"),
            ("dropped", "django-crispy-forms", "2.8"),
        }


class RecordedRun:
    def __init__(self, status=0):
        self.status = status
        self.calls = []

    def __call__(self, command, **options):
        self.calls.append((command, options))
        return SimpleNamespace(returncode=self.status)


class TestRunSuite:
    def test_a_named_pair_runs_one_command_that_pins_both_versions(self):
        run = RecordedRun()

        Window.from_mapping(MAPPING).run_suite("5.2", "2.7", ["-x"], run=run)

        assert [command for command, options in run.calls] == [
            [
                "uv",
                "run",
                "--isolated",
                "--with",
                "django==5.2.*",
                "--with",
                "django-crispy-forms==2.7.*",
                "pytest",
                "-x",
            ]
        ]

    def test_the_command_carries_both_versions_in_its_environment(self):
        run = RecordedRun()

        Window.from_mapping(MAPPING).run_suite("6.0", "2.7", [], run=run)

        environment = run.calls[0][1]["env"]
        assert environment["SUPPORT_WINDOW_DJANGO"] == "6.0"
        assert environment["SUPPORT_WINDOW_CRISPY_FORMS"] == "2.7"

    def test_the_status_of_the_command_is_returned(self):
        status = Window.from_mapping(MAPPING).run_suite(
            "5.2", "2.7", [], run=RecordedRun(status=3)
        )

        assert status == 3

    def test_a_django_series_the_window_does_not_name_runs_nothing(self):
        run = RecordedRun()

        status = Window.from_mapping(MAPPING).run_suite("4.2", "2.7", [], run=run)

        assert run.calls == []
        assert status != 0

    def test_a_crispy_forms_release_the_window_does_not_name_runs_nothing(self):
        run = RecordedRun()

        status = Window.from_mapping(MAPPING).run_suite("5.2", "2.5", [], run=run)

        assert run.calls == []
        assert status != 0

    def test_a_pair_the_window_does_not_hold_runs_nothing(self):
        run = RecordedRun()

        status = Window.from_mapping(MAPPING).run_suite("6.0", "2.6", [], run=run)

        assert run.calls == []
        assert status != 0


class TestMain:
    def test_the_test_command_runs_the_suite_on_the_pair_it_names(self, tmp_path):
        declaration = tmp_path / "window.toml"
        declaration.write_text(DECLARATION_TEXT)
        run = RecordedRun()

        status = main(["test", "5.2", "2.7"], run=run, declaration=declaration)

        command = run.calls[0][0]
        assert "django==5.2.*" in command
        assert "django-crispy-forms==2.7.*" in command
        assert status == 0

    def test_arguments_after_the_pair_are_given_to_pytest(self, tmp_path):
        declaration = tmp_path / "window.toml"
        declaration.write_text(DECLARATION_TEXT)
        run = RecordedRun()

        main(
            ["test", "5.2", "2.7", "-x", "tests/test_smoke.py"],
            run=run,
            declaration=declaration,
        )

        assert run.calls[0][0][-3:] == ["pytest", "-x", "tests/test_smoke.py"]

    def test_the_classes_command_refuses_a_version_that_is_not_two_numbers(self):
        with pytest.raises(InvalidWindow) as raised:
            main(["classes", "5.0.1"])

        assert raised.value.version == "5.0.1"


@pytest.fixture
def listings():
    return {
        "django": {
            "5.2": "2025-04-02",
            "5.2.1": "2025-05-07",
            "6.0": "2025-12-03",
            "6.1": "2026-04-01",
            "6.1.1": "2026-05-05",
        },
        "django-crispy-forms": {
            "2.6": "2025-08-01",
            "2.7": "2026-02-02",
            "2.7.1": "2026-03-03",
        },
        "daisyui": {
            "5.0.0": "2025-03-01",
            "5.7.0": "2026-06-01",
            "5.7.1": "2026-06-20",
        },
    }


def outstanding_in(listings):
    return Window.from_mapping(CURRENT).outstanding(
        listings["django"], listings["django-crispy-forms"], listings["daisyui"]
    )


def index_payload(listing):
    return {
        "releases": {
            version: [{"upload_time_iso_8601": f"{day}T10:00:00.000000Z"}]
            for version, day in listing.items()
        }
    }


def served(listings, **failing):
    payloads = {
        SOURCES["django"]: index_payload(listings["django"]),
        SOURCES["django-crispy-forms"]: index_payload(listings["django-crispy-forms"]),
        SOURCES["daisyui"]: {
            "time": {
                "created": "2025-01-01T00:00:00.000Z",
                "modified": "2026-07-01T00:00:00.000Z",
                **{
                    version: f"{day}T10:00:00.000Z"
                    for version, day in listings["daisyui"].items()
                },
            }
        },
    }
    for package, broken in failing.items():
        payloads[SOURCES[package.replace("_", "-")]] = broken

    def fetch(url):
        payload = payloads[url]
        if isinstance(payload, Exception):
            raise payload
        return payload

    return fetch


class TestFinalReleases:
    def test_a_version_has_the_date_of_its_earliest_file(self):
        payload = {
            "releases": {
                "6.1": [
                    {"upload_time_iso_8601": "2026-04-01T10:00:00.000000Z"},
                    {"upload_time_iso_8601": "2026-03-30T09:00:00.000000Z"},
                ]
            }
        }

        assert final_releases(payload, "django") == {"6.1": "2026-03-30"}

    def test_pre_releases_of_the_package_index_are_left_out(self):
        payload = {
            "releases": {
                version: [{"upload_time_iso_8601": "2026-04-01T10:00:00.000000Z"}]
                for version in ("6.2a1", "6.2b1", "6.2rc1", "6.1")
            }
        }

        assert set(final_releases(payload, "django")) == {"6.1"}

    def test_a_version_with_no_files_is_left_out(self):
        payload = {
            "releases": {
                "6.2": [],
                "6.1": [{"upload_time_iso_8601": "2026-04-01T10:00:00Z"}],
            }
        }

        assert set(final_releases(payload, "django")) == {"6.1"}

    def test_the_npm_registry_leaves_out_pre_releases_and_its_own_entries(self):
        payload = {
            "time": {
                "created": "2025-01-01T00:00:00.000Z",
                "modified": "2026-07-01T00:00:00.000Z",
                "5.6.0-beta.0": "2026-05-01T00:00:00.000Z",
                "5.6.0": "2026-05-20T08:00:00.000Z",
            }
        }

        assert final_releases(payload, "daisyui") == {"5.6.0": "2026-05-20"}

    @pytest.mark.parametrize(
        ("payload", "package"),
        [
            ({}, "django"),
            ({"releases": []}, "django"),
            ({"releases": {"6.1": "2026-04-01"}}, "django"),
            ({"releases": {"6.1": [{}]}}, "django"),
            ({"releases": {"6.1": [{"upload_time_iso_8601": 7}]}}, "django"),
            ([], "django-crispy-forms"),
            ({}, "daisyui"),
            ({"time": ["5.7.0"]}, "daisyui"),
            ({"time": {"5.7.0": 7}}, "daisyui"),
        ],
    )
    def test_a_payload_that_is_not_the_shape_expected_raises(self, payload, package):
        with pytest.raises(ValueError):
            final_releases(payload, package)


class TestOutstanding:
    def test_a_window_naming_the_newest_of_each_has_nothing_outstanding(self, listings):
        assert outstanding_in(listings) == []

    def test_a_django_series_the_window_does_not_name_is_outstanding(self, listings):
        listings["django"]["6.2"] = "2026-10-01"
        listings["django"]["6.2.1"] = "2026-11-05"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("django", "6.2")
        assert missing.released == "2026-10-01"
        assert not missing.new_major

    def test_a_django_series_is_reported_once_with_its_first_release(self, listings):
        listings["django"]["6.2.1"] = "2026-11-05"
        listings["django"]["6.2"] = "2026-10-01"
        listings["django"]["6.2.2"] = "2026-12-05"

        assert [m.version for m in outstanding_in(listings)] == ["6.2"]

    def test_a_new_django_major_version_is_outstanding_without_new_major(
        self, listings
    ):
        listings["django"]["7.0"] = "2026-12-01"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("django", "7.0")
        assert not missing.new_major

    def test_every_newer_django_series_is_outstanding(self, listings):
        listings["django"]["6.2"] = "2026-10-01"
        listings["django"]["7.0"] = "2026-12-01"

        assert [m.version for m in outstanding_in(listings)] == ["6.2", "7.0"]

    def test_a_crispy_forms_feature_release_the_window_does_not_name_is_outstanding(
        self, listings
    ):
        listings["django-crispy-forms"]["2.8"] = "2026-09-01"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("django-crispy-forms", "2.8")
        assert missing.released == "2026-09-01"
        assert not missing.new_major

    def test_a_daisyui_minor_release_the_window_does_not_name_is_outstanding(
        self, listings
    ):
        listings["daisyui"]["5.8.0"] = "2026-09-10"
        listings["daisyui"]["5.8.1"] = "2026-09-20"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("daisyui", "5.8")
        assert missing.released == "2026-09-10"
        assert not missing.new_major

    def test_a_new_crispy_forms_major_version_is_returned_with_new_major(
        self, listings
    ):
        listings["django-crispy-forms"]["3.0"] = "2026-09-01"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("django-crispy-forms", "3.0")
        assert missing.new_major

    def test_a_new_daisyui_major_version_is_returned_with_new_major(self, listings):
        listings["daisyui"]["6.0.0"] = "2026-09-01"

        (missing,) = outstanding_in(listings)

        assert (missing.package, missing.version) == ("daisyui", "6.0")
        assert missing.new_major

    def test_a_later_major_version_is_reported_once_at_its_first_series(self, listings):
        listings["daisyui"]["6.0.0"] = "2026-09-01"
        listings["daisyui"]["6.1.0"] = "2026-10-01"

        assert [m.version for m in outstanding_in(listings)] == ["6.0"]

    def test_a_newer_patch_release_of_a_named_version_is_not_outstanding(
        self, listings
    ):
        listings["django"]["6.1.2"] = "2026-06-01"
        listings["daisyui"]["5.7.48"] = "2026-08-01"

        assert outstanding_in(listings) == []

    def test_a_listing_with_no_releases_has_nothing_outstanding(self, listings):
        listings["django"] = {}

        assert outstanding_in(listings) == []


class TestReportReleases:
    def test_nothing_outstanding_returns_0(self, listings):
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings), out=lines.append
        )

        assert status == 0

    def test_a_missing_release_returns_1_and_a_line_holds_its_package_and_version(
        self, listings
    ):
        listings["daisyui"]["5.8.0"] = "2026-09-10"
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings), out=lines.append
        )

        assert status == 1
        assert any("daisyui" in line and "5.8" in line for line in lines)

    def test_a_new_major_version_alone_returns_0_and_a_line_holds_it(self, listings):
        listings["django-crispy-forms"]["3.0"] = "2026-09-01"
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings), out=lines.append
        )

        assert status == 0
        assert any("django-crispy-forms" in line and "3.0" in line for line in lines)

    def test_a_new_major_version_does_not_hide_a_missing_release(self, listings):
        listings["daisyui"]["6.0.0"] = "2026-09-01"
        listings["django"]["6.2"] = "2026-10-01"

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings), out=lambda line: None
        )

        assert status == 1

    def test_a_fetch_that_raises_oserror_returns_2_and_a_line_names_the_package(
        self, listings
    ):
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings, django=OSError("no route")), out=lines.append
        )

        assert status == 2
        assert len(lines) == 1
        assert "django" in lines[0]

    def test_a_payload_that_is_not_the_shape_expected_returns_2(self, listings):
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings, daisyui={"unexpected": True}), out=lines.append
        )

        assert status == 2
        assert len(lines) == 1
        assert "daisyui" in lines[0]

    def test_an_answer_that_is_not_json_returns_2(self, listings):
        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings, django=ValueError("not json")),
            out=lambda line: None,
        )

        assert status == 2

    def test_a_failing_source_beside_a_missing_release_returns_2_and_prints_both(
        self, listings
    ):
        listings["django"]["6.2"] = "2026-10-01"
        lines = []

        status = Window.from_mapping(CURRENT).report_releases(
            fetch=served(listings, daisyui=OSError("no route")), out=lines.append
        )

        assert status == 2
        assert any("django" in line and "6.2" in line for line in lines)
        assert any("daisyui" in line for line in lines)

    def test_every_source_is_asked_for_once(self, listings):
        asked = []
        inner = served(listings)

        def fetch(url):
            asked.append(url)
            return inner(url)

        Window.from_mapping(CURRENT).report_releases(fetch=fetch, out=lambda line: None)

        assert sorted(asked) == sorted(SOURCES.values())


class TestMainReleases:
    def test_the_releases_command_returns_the_status_of_the_report(
        self, tmp_path, listings
    ):
        declaration = tmp_path / "window.toml"
        declaration.write_text(DECLARATION_TEXT)

        status = main(["releases"], declaration=declaration, fetch=served(listings))

        assert status == 1

    def test_the_releases_command_returns_2_when_a_source_fails(
        self, tmp_path, listings
    ):
        declaration = tmp_path / "window.toml"
        declaration.write_text(DECLARATION_TEXT)

        status = main(
            ["releases"],
            declaration=declaration,
            fetch=served(listings, django=OSError("no route")),
        )

        assert status == 2
