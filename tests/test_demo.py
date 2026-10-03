"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

import pytest
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse

# The address a page guarded by LoginRequiredMixin sends an anonymous visitor to.
SIGN_IN_URL = resolve_url(settings.LOGIN_URL)


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


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        # A template that fails to extend the shell still returns 200.
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_links_the_pages_that_exist(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("overview")}"' in sidebar


STATES = ["empty", "value", "required", "help", "error"]
INPUT_KINDS = [
    ("text", "input"),
    ("email", "input"),
    ("url", "input"),
    ("number", "input"),
    ("password", "input"),
    ("date", "input"),
    ("time", "input"),
    ("date_time", "input"),
    ("textarea", "textarea"),
]
SUBMITTED = {"submit-email": "not an email"}


def field_id(state, name):
    return f"id_{state}-{name}"


class TextInputsPageContract:
    """What both text inputs pages promise, whichever way they are styled."""

    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = SUBMITTED if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize("state", STATES)
    @pytest.mark.parametrize(("name", "tag"), INPUT_KINDS)
    def test_every_kind_is_present_in_every_state(self, open_page, state, name, tag):
        page = open_page(self.url_name)
        assert page.find(tag, id=field_id(state, name)) is not None

    @pytest.mark.parametrize(("name", "tag"), INPUT_KINDS)
    def test_the_submittable_form_holds_every_kind(self, open_page, name, tag):
        page = open_page(self.url_name)
        assert page.find(tag, id=field_id("submit", name)) is not None

    def test_the_required_state_marks_its_inputs_required(self, open_page):
        page = open_page(self.url_name)
        assert page.find(id=field_id("required", "email")).has_attr("required")
        assert not page.find(id=field_id("empty", "email")).has_attr("required")

    def test_the_value_state_holds_a_value(self, open_page):
        page = open_page(self.url_name)
        assert page.find(id=field_id("value", "email")).get("value")
        assert not page.find(id=field_id("empty", "email")).get("value")

    def test_the_help_state_describes_its_inputs(self, open_page):
        page = open_page(self.url_name)
        assert page.find(id=field_id("help", "email")).get("aria-describedby")
        assert page.find(id=field_id("empty", "email")).get("aria-describedby") is None

    def test_the_error_state_shows_a_field_error(self, open_page):
        page = open_page(self.url_name)
        assert page.find(id=f"{field_id('error', 'email')}_error") is not None
        assert page.find(id=field_id("error", "email"))["aria-invalid"] == "true"
        assert page.find(id=field_id("empty", "email")).get("aria-invalid") is None

    def test_a_post_comes_back_with_a_field_error_and_a_form_wide_alert(
        self, open_page
    ):
        page = open_page(self.url_name, SUBMITTED)
        submitted = page.find(id=field_id("submit", "email")).find_parent("form")
        assert submitted.find(id=f"{field_id('submit', 'email')}_error") is not None
        assert submitted.find(attrs={"role": "alert"}) is not None

    def test_a_post_keeps_what_was_submitted(self, open_page):
        page = open_page(self.url_name, SUBMITTED)
        email = page.find(id=field_id("submit", "email"))
        assert email["value"] == SUBMITTED["submit-email"]

    def test_the_submittable_form_posts_with_a_token_and_a_button(self, open_page):
        page = open_page(self.url_name)
        form = page.find(id=field_id("submit", "email")).find_parent("form")
        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("button", class_="btn") is not None

    def test_only_the_submittable_form_is_a_form_element(self, open_page):
        page = open_page(self.url_name)
        for state in STATES:
            assert page.find(id=field_id(state, "email")).find_parent("form") is None

    def test_every_input_has_a_label_that_names_it(self, page):
        fields = page.find_all(["input", "textarea"])
        visible = [f for f in fields if f.get("type") not in {"hidden", "submit"}]
        assert visible
        for field in visible:
            assert page.find("label", attrs={"for": field["id"]}) is not None

    def test_every_described_id_exists(self, page):
        described = page.find_all(attrs={"aria-describedby": True})
        assert described
        for element in described:
            for described_id in element["aria-describedby"].split():
                assert page.find(id=described_id) is not None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestTextInputsPage(TextInputsPageContract):
    url_name = "text-inputs"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("text-inputs")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("text-inputs-standalone")) is not None


class TestStandaloneTextInputsPage(TextInputsPageContract):
    url_name = "text-inputs-standalone"

    def test_it_carries_daisyuis_cdn_stylesheet(self, open_page):
        page = open_page(self.url_name)
        link = page.find("link", href="https://cdn.jsdelivr.net/npm/daisyui@5")
        assert link["rel"] == ["stylesheet"]

    def test_it_carries_tailwinds_browser_build(self, open_page):
        page = open_page(self.url_name)
        source = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"
        assert page.find("script", src=source) is not None

    def test_it_carries_no_stylesheet_of_the_shell(self, open_page):
        page = open_page(self.url_name)
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("text-inputs")) is not None
