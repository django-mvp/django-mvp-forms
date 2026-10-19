"""The script that shows the image an image input holds, run in Chrome."""

import io
import re

import pytest
from django.urls import reverse
from PIL import Image
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def png():
    """Return a file Playwright can hand to a file input: a small PNG."""
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (40, 120, 200)).save(buffer, "PNG")
    return {"name": "new.png", "mimeType": "image/png", "buffer": buffer.getvalue()}


def text_file():
    """Return a file that is not an image."""
    return {"name": "notes.txt", "mimeType": "text/plain", "buffer": b"Not an image."}


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def images_page(page, page_errors, live_server):
    """Open the page of image inputs of the test project."""

    def open_page(name="images"):
        page.goto(f"{live_server.url}{reverse(name)}")
        page.wait_for_load_state("load")
        return page

    return open_page


def group(page, name):
    """Return the image input of one field."""
    return page.locator(f"#div_id_{name} [data-image-input]")


def hook(page, name, which):
    """Return one part of a field's image input, by the hook the script uses."""
    return group(page, name).locator(f"[data-image-input-{which}]")


class TestChoosingAFile:
    def test_a_chosen_image_is_shown_in_place_of_the_stored_one(self, images_page):
        page = images_page()

        page.locator("#id_photo").set_input_files(png())

        expect(hook(page, "photo", "preview")).to_have_attribute(
            "src", re.compile(r"^blob:")
        )
        expect(hook(page, "photo", "status")).to_be_visible()
        expect(hook(page, "photo", "revert")).to_be_visible()

    def test_reverting_shows_the_stored_image_and_empties_the_input(self, images_page):
        page = images_page()
        stored = hook(page, "photo", "preview").get_attribute("src")
        page.locator("#id_photo").set_input_files(png())

        hook(page, "photo", "revert").click()

        expect(hook(page, "photo", "preview")).to_have_attribute("src", stored)
        assert page.locator("#id_photo").evaluate("node => node.files.length") == 0
        expect(hook(page, "photo", "status")).to_be_hidden()
        expect(hook(page, "photo", "revert")).to_be_hidden()

    def test_a_chosen_image_in_an_empty_field_can_be_reverted(self, images_page):
        page = images_page()

        page.locator("#id_empty").set_input_files(png())
        expect(hook(page, "empty", "preview")).to_be_visible()
        hook(page, "empty", "revert").click()

        expect(hook(page, "empty", "preview")).to_be_hidden()
        expect(hook(page, "empty", "empty")).to_be_visible()

    def test_a_file_that_is_not_an_image_is_not_previewed(self, images_page):
        page = images_page()

        page.locator("#id_photo").set_input_files(text_file())

        expect(hook(page, "photo", "preview")).to_be_hidden()
        expect(hook(page, "photo", "empty")).to_be_visible()
        expect(hook(page, "photo", "status")).to_be_visible()


class TestRemovingTheStoredImage:
    def test_ticking_remove_drops_a_chosen_file(self, images_page):
        page = images_page()
        page.locator("#id_photo").set_input_files(png())

        page.locator("#photo-clear_id").check()

        assert page.locator("#id_photo").evaluate("node => node.files.length") == 0
        expect(hook(page, "photo", "status")).to_be_visible()
        expect(hook(page, "photo", "revert")).to_be_hidden()

    def test_choosing_a_file_unticks_remove(self, images_page):
        page = images_page()
        page.locator("#photo-clear_id").check()

        page.locator("#id_photo").set_input_files(png())

        expect(page.locator("#photo-clear_id")).not_to_be_checked()

    def test_unticking_remove_takes_the_message_away(self, images_page):
        page = images_page()
        page.locator("#photo-clear_id").check()

        page.locator("#photo-clear_id").uncheck()

        expect(hook(page, "photo", "status")).to_be_hidden()


class TestAStoredFileThatIsGone:
    def test_it_is_shown_as_missing_and_not_as_a_broken_image(self, images_page):
        page = images_page()

        expect(hook(page, "lost", "preview")).to_be_hidden()
        expect(hook(page, "lost", "empty")).to_be_visible()


class TestTheThumbnailAsThePicker:
    def test_the_file_input_leaves_the_tab_order(self, images_page):
        page = images_page()

        expect(hook(page, "picked", "open")).to_be_visible()
        assert page.locator("#id_picked").get_attribute("tabindex") == "-1"

    def test_the_thumbnail_opens_the_file_picker(self, images_page):
        page = images_page()

        with page.expect_file_chooser() as chooser:
            hook(page, "picked", "open").click()
        chooser.value.set_files(png())

        expect(hook(page, "picked", "preview")).to_have_attribute(
            "src", re.compile(r"^blob:")
        )

    def test_the_thumbnail_is_reached_and_opened_from_the_keyboard(self, images_page):
        page = images_page()
        opener = hook(page, "picked", "open")
        expect(opener).to_be_visible()

        with page.expect_file_chooser():
            opener.press("Enter")

    def test_a_picker_added_later_is_prepared(self, images_page):
        page = images_page()

        page.evaluate(
            """document.getElementById("later").append(
              document.getElementById("picker").content.cloneNode(true))"""
        )

        added = page.locator("#later [data-image-input]")
        expect(added.locator("[data-image-input-open]")).to_be_visible()
        expect(added.locator('input[type="file"]')).to_have_attribute("tabindex", "-1")

    def test_without_the_script_the_file_input_stays_usable(self, images_page):
        page = images_page("images-bare")

        expect(page.locator("#id_picked")).to_be_visible()
        expect(hook(page, "picked", "open")).to_be_hidden()


class TestThePage:
    def test_the_script_raises_no_error(self, images_page, page_errors):
        page = images_page()
        page.locator("#id_photo").set_input_files(png())
        hook(page, "photo", "revert").click()

        assert page_errors == []
