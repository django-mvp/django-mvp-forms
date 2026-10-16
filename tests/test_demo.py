"""The demo project's pages and live examples, asserted as rendered."""

# Everything in the demo fails quietly: a page missing from the contents is
# dropped from the sidebar, and a live example whose address does not resolve
# draws an empty frame. So the tests read the built pages and the answers.

import subprocess
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import Client

from demo.examples.urls import urlpatterns as example_urlpatterns
from demo.mounted import docs

SOURCE_DIR = Path(docs.source_dir)
PAGES = sorted(
    path.relative_to(SOURCE_DIR)
    for path in SOURCE_DIR.rglob("*.md")
    if "_build" not in path.parts
)
EXAMPLES = sorted(f"/examples/{pattern.pattern}" for pattern in example_urlpatterns)
SIGN_IN_URL = resolve_url(settings.LOGIN_URL)


def address_of(page):
    """Return the address a Markdown page under the source directory is served at."""
    parts = page.with_suffix("").parts
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "".join(f"{part}/" for part in parts)


@pytest.fixture(scope="session")
def build(tmp_path_factory):
    """Build the pages once, serve them from the build, and return its warnings."""
    build_dir = tmp_path_factory.mktemp("docs")
    finished = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "sphinx", "-q", "-b", "json", SOURCE_DIR, build_dir],
        capture_output=True,
        text=True,
        check=False,
    )
    served = docs.build_dir
    docs.build_dir = build_dir
    yield finished
    docs.build_dir = served


@pytest.fixture(scope="session")
def rendered(build, django_db_setup, django_db_blocker):
    """Return each page's status and parsed HTML, read once for the session."""
    client = Client()
    with django_db_blocker.unblock():
        answers = {page: client.get(address_of(page)) for page in PAGES}
    return {
        page: (answer.status_code, BeautifulSoup(answer.content, "html.parser"))
        for page, answer in answers.items()
    }


def frames(rendered):
    """Return the address of every live example the pages show."""
    return {
        frame["src"]
        for _, soup in rendered.values()
        for frame in soup.select("iframe.mvp-sphinx-example-frame")
    }


class TestSignIn:
    def test_the_sign_in_page_renders(self, client, db) -> None:
        assert client.get(SIGN_IN_URL).status_code == 200

    def test_a_seeded_account_can_sign_in(self, client, django_user_model) -> None:
        django_user_model.objects.create_user(
            username="regular.user@example.com", password="password"
        )
        response = client.post(
            SIGN_IN_URL,
            {"username": "regular.user@example.com", "password": "password"},
        )
        assert response.status_code == 302
        assert "_auth_user_id" in client.session


class TestPages:
    def test_they_build_with_no_warning(self, build) -> None:
        assert build.returncode == 0
        assert build.stderr == ""

    @pytest.mark.parametrize("page", PAGES, ids=str)
    def test_each_is_served(self, rendered, page) -> None:
        assert rendered[page][0] == 200

    @pytest.mark.parametrize("page", PAGES, ids=str)
    def test_the_sidebar_links_each(self, rendered, page) -> None:
        _, overview = rendered[Path("index.md")]
        sidebar = overview.find("nav", attrs={"aria-label": "MVP Forms"})

        assert sidebar.find("a", href=address_of(page))


class TestLiveExamples:
    def test_every_example_is_shown_on_a_page(self, rendered) -> None:
        assert frames(rendered) == set(EXAMPLES)

    @pytest.mark.parametrize("address", EXAMPLES)
    def test_each_draws_a_form(self, client, db, address) -> None:
        response = client.get(address)

        assert response.status_code == 200
        assert BeautifulSoup(response.content, "html.parser").find("form")

    @pytest.mark.parametrize("address", EXAMPLES)
    def test_each_answers_a_post_of_nothing(self, client, db, address) -> None:
        assert client.post(address, {}).status_code in {200, 302}
