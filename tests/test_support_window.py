"""The support window is read from its declaration and held to the package metadata."""

import copy
import tomllib

import pytest

from support_window import (
    DECLARATION,
    ROOT,
    InvalidWindow,
    MissingClassList,
    Window,
    class_list,
    class_names,
    installed_versions,
    relative_links,
    write_class_list,
)

MAPPING = {
    "python": ["3.12", "3.13"],
    "django": {"versions": ["5.2", "6.0"]},
    "django-crispy-forms": {
        "versions": ["2.6", "2.7"],
        "pairs": {"2.6": ["5.2"], "2.7": ["5.2", "6.0"]},
    },
    "daisyui": {"minimum": "5.0", "newest": "5.4"},
}

DECLARATION_TEXT = """
python = ["3.12", "3.13"]

[django]
versions = ["5.2", "6.0"]

[django-crispy-forms]
versions = ["2.6", "2.7"]

[django-crispy-forms.pairs]
"2.6" = ["5.2"]
"2.7" = ["5.2", "6.0"]

[daisyui]
minimum = "5.0"
newest = "5.4"
"""


@pytest.fixture
def declared():
    with DECLARATION.open("rb") as handle:
        return tomllib.load(handle)


@pytest.fixture
def pyproject():
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


@pytest.fixture
def readme():
    return (ROOT / "README.md").read_text()


@pytest.fixture
def lock():
    with (ROOT / "uv.lock").open("rb") as handle:
        return tomllib.load(handle)


def found(disagreements):
    return {(d.source, d.package, d.version) for d in disagreements}


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


class TestMetadata:
    def test_the_repositorys_metadata_agrees_with_its_declaration(
        self, declared, pyproject
    ):
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
        pyproject = copy.deepcopy(pyproject)
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
        pyproject = copy.deepcopy(pyproject)
        pyproject["project"]["dependencies"] = [
            "django>=5.2",
            "django-crispy-forms>=2.7,<3",
        ]
        window = Window.from_mapping(declared)

        assert ("metadata", "django-crispy-forms", "3") in found(
            window.metadata_disagreements(pyproject)
        )

    def test_a_pinned_requirement_is_a_disagreement(self, declared, pyproject):
        pyproject = copy.deepcopy(pyproject)
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


def section(*links):
    body = "\n".join(f"[a link]({link})" for link in links)
    return (
        "[before](docs/before.md)\n\n<!-- support-window -->\n"
        f"| | Supported |\n<!-- /support-window -->\n{body}\n"
        "<!-- dropped-versions -->\n<!-- /dropped-versions -->\n"
        "\n[after](docs/after.md)\n"
    )


class TestReadmeLinks:
    def test_the_section_of_the_repositorys_readme_holds_no_relative_link(self):
        readme = (ROOT / "README.md").read_text()

        assert relative_links(readme) == []

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


class TestReadme:
    def test_the_repositorys_readme_agrees_with_its_declaration(self, declared, readme):
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


def locked(lock, package, version):
    lock = copy.deepcopy(lock)
    for entry in lock["package"]:
        if entry["name"] == package:
            entry["version"] = version
    return lock


class TestLockfile:
    def test_the_repositorys_lockfile_agrees_with_its_declaration(self, declared, lock):
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
    def test_the_versions_this_run_is_on_are_inside_the_window(self, declared):
        window = Window.from_mapping(declared)

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
