"""The support window is read from its declaration and held to the package metadata."""

import copy
import tomllib

import pytest

from support_window import DECLARATION, ROOT, InvalidWindow, Window, relative_links

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
