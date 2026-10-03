"""File fields drawn through django-crispy-forms."""

import pytest
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.forms import FilesForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]


def rejected():
    return FilesForm(
        {}, {"plain": SimpleUploadedFile("empty.txt", b""), "needed": None}
    )


class TestFileInput:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["plain", "empty", "optional", "several"])
    def test_each_is_a_file_input_with_the_component_class(self, draw, source, name):
        drawn = draw(source, form=FilesForm()).find(id=f"id_{name}")

        assert drawn.name == "input"
        assert drawn["type"] == "file"
        assert "file-input" in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["plain", "empty", "optional", "needed"])
    def test_the_frames_label_names_the_file_input(self, draw, source, name):
        soup = draw(source, form=FilesForm())

        label = soup.find("label", attrs={"for": f"id_{name}"})

        assert label is not None
        assert soup.find(id=f"id_{name}")["type"] == "file"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_holding_nothing_has_no_link_and_no_removal_checkbox(
        self, draw, source
    ):
        frame = draw(source, form=FilesForm()).find(id="div_id_empty")

        assert frame.find("a") is None
        assert frame.find("input", attrs={"type": "checkbox"}) is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_plain_file_input_is_described_by_its_help_text(self, draw, source):
        soup = draw(source, form=FilesForm())

        assert soup.find(id="id_plain")["aria-describedby"] == "id_plain_helptext"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_widget_allowing_several_files_has_multiple(self, draw, source):
        soup = draw(source, form=FilesForm())

        assert soup.find(id="id_several").has_attr("multiple")
        assert not soup.find(id="id_plain").has_attr("multiple")


class TestHeldFile:
    @pytest.mark.parametrize("source", SOURCES)
    def test_an_optional_field_links_to_the_file(self, draw, source):
        frame = draw(source, form=FilesForm()).find(id="div_id_optional")

        assert frame.find("a")["href"] == "/media/report.pdf"
        assert "link" in frame.find("a")["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_optional_field_offers_a_removal_checkbox_with_its_own_label(
        self, draw, source
    ):
        soup = draw(source, form=FilesForm())

        checkbox = soup.find(id="optional-clear_id")
        label = soup.find("label", attrs={"for": "optional-clear_id"})

        assert checkbox["type"] == "checkbox"
        assert checkbox["name"] == "optional-clear"
        assert "checkbox" in checkbox["class"]
        assert label is not None
        assert label is not soup.find("label", attrs={"for": "id_optional"})

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_optional_field_still_offers_the_file_input(self, draw, source):
        drawn = draw(source, form=FilesForm()).find(id="id_optional")

        assert drawn["type"] == "file"
        assert "file-input" in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_required_field_links_to_the_file_without_a_removal_checkbox(
        self, draw, source
    ):
        frame = draw(source, form=FilesForm()).find(id="div_id_needed")

        assert frame.find("a")["href"] == "/media/contract.pdf"
        assert frame.find("input", attrs={"type": "checkbox"}) is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_required_field_holding_a_file_is_not_required_in_the_browser(
        self, draw, source
    ):
        drawn = draw(source, form=FilesForm()).find(id="id_needed")

        assert drawn["type"] == "file"
        assert not drawn.has_attr("required")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_required_field_holding_nothing_is_required_in_the_browser(
        self, draw, source
    ):
        class Form(forms.Form):
            needed = forms.FileField()

        drawn = draw(source, form=Form()).find(id="id_needed")

        assert drawn.has_attr("required")

    @pytest.mark.parametrize("source", SOURCES)
    def test_markup_in_a_file_name_is_escaped(self, draw, source):
        frame = draw(source, form=FilesForm()).find(id="div_id_marked")

        assert frame.find("a").string == "<b>x</b>&.pdf"
        assert frame.find("b") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_widget_disables_the_removal_checkbox(self, draw, source):
        soup = draw(source, form=FilesForm())

        assert soup.find(id="locked-clear_id").has_attr("disabled")
        assert not soup.find(id="optional-clear_id").has_attr("disabled")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_ticked_removal_checkbox_stays_ticked_when_drawn_again(
        self, draw, source
    ):
        form = FilesForm({"optional-clear": "on"})

        soup = draw(source, form=form)

        assert soup.find(id="optional-clear_id").has_attr("checked")


class TestRejectedFile:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_file_input_is_marked_and_described_by_its_error(self, draw, source):
        form = rejected()
        soup = draw(source, form=form)

        drawn = soup.find(id="id_plain")

        assert form.errors["plain"]
        assert "file-input-error" in drawn["class"]
        assert drawn["aria-invalid"] == "true"
        described = drawn["aria-describedby"].split()
        assert "id_plain_error" in described
        assert all(soup.find(id=name) is not None for name in described)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_valid_file_input_carries_no_error_modifier(self, draw, source):
        drawn = draw(source, form=rejected()).find(id="id_empty")

        assert "file-input-error" not in drawn["class"]
        assert not drawn.has_attr("aria-invalid")


class TestOwnTemplate:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_subclass_naming_its_own_template_is_drawn_by_it(self, draw, source):
        frame = draw(source, form=FilesForm()).find(id="div_id_own")

        drawn = frame.find("input", attrs={"type": "file"})

        assert "file-input" in drawn["class"]
        assert frame.find("a") is None
