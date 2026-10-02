"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

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
