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
        assert form.find("button", type="submit") is not None

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


LAYOUT_SUBMIT_PREFIX = "layout"
LAYOUT_FAILING_PREFIX = "failing"
LAYOUT_ROW_FIELDS = ["first_name", "last_name"]
LAYOUT_INPUT_BUTTONS = ["submit", "reset", "button"]
HELPER_PREFIX = "helper"
SMALL_PREFIX = "small"


def layout_field_id(prefix, name):
    return f"id_{prefix}-{name}"


class LayoutObjectsPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = {} if request.param == "post" else None
        return open_page(self.url_name, data)

    def test_it_holds_a_fieldset_with_a_legend(self, page):
        fieldset = page.find("fieldset", id=f"{LAYOUT_SUBMIT_PREFIX}-details")
        assert fieldset.find("legend") is not None

    @pytest.mark.parametrize("name", LAYOUT_ROW_FIELDS)
    def test_the_row_holds_its_fields_by_id(self, page, name):
        row = page.find(id=f"{LAYOUT_SUBMIT_PREFIX}-row")
        assert row.find("input", id=layout_field_id(LAYOUT_SUBMIT_PREFIX, name))

    def test_the_bound_form_shows_its_errors_without_a_post(self, open_page):
        page = open_page(self.url_name)
        fieldset = page.find("fieldset", id=f"{LAYOUT_FAILING_PREFIX}-details")
        error_id = layout_field_id(LAYOUT_FAILING_PREFIX, "first_name") + "_error"
        assert fieldset.find(id=error_id) is not None

    def test_the_submittable_form_starts_without_errors(self, open_page):
        page = open_page(self.url_name)
        error_id = layout_field_id(LAYOUT_SUBMIT_PREFIX, "first_name") + "_error"
        assert page.find(id=error_id) is None

    def test_a_post_of_the_empty_form_comes_back_with_a_field_error(self, open_page):
        page = open_page(self.url_name, {})
        error_id = layout_field_id(LAYOUT_SUBMIT_PREFIX, "first_name") + "_error"
        assert page.find(id=error_id) is not None

    @pytest.mark.parametrize("name", LAYOUT_INPUT_BUTTONS)
    def test_the_actions_hold_each_input_button_by_name(self, page, name):
        actions = page.find(id=f"{LAYOUT_SUBMIT_PREFIX}-actions")
        assert actions.find("input", attrs={"name": f"{LAYOUT_SUBMIT_PREFIX}-{name}"})

    def test_the_actions_hold_the_strict_button_by_id(self, page):
        actions = page.find(id=f"{LAYOUT_SUBMIT_PREFIX}-actions")
        assert actions.find("button", id=f"{LAYOUT_SUBMIT_PREFIX}-strict")

    def test_the_submittable_form_is_drawn_with_its_own_form_element(self, page):
        button = page.find("input", attrs={"name": f"{LAYOUT_SUBMIT_PREFIX}-submit"})
        form = button.find_parent("form")
        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find(id=layout_field_id(LAYOUT_SUBMIT_PREFIX, "first_name"))

    def test_the_raw_html_sits_inside_the_fieldset_with_its_context_filled_in(
        self, page
    ):
        fieldset = page.find("fieldset", id=f"{LAYOUT_SUBMIT_PREFIX}-details")
        aside = fieldset.find(id=f"{LAYOUT_SUBMIT_PREFIX}-aside")
        assert aside is not None
        assert "{{" not in aside.get_text()

    def test_the_hidden_input_is_inside_the_form_with_no_class_or_id(self, page):
        hidden = page.find("input", attrs={"name": f"{LAYOUT_SUBMIT_PREFIX}-step"})
        assert hidden["type"] == "hidden"
        assert hidden.find_parent("form") is not None
        assert not hidden.has_attr("class")
        assert not hidden.has_attr("id")

    @pytest.mark.parametrize("name", ["email", "phone"])
    def test_the_multi_field_holds_each_of_its_fields_by_id(self, page, name):
        group = page.find("fieldset", id=f"{LAYOUT_SUBMIT_PREFIX}-contact")
        assert group.find("legend") is not None
        assert group.find("input", id=layout_field_id(LAYOUT_SUBMIT_PREFIX, name))

    def test_an_error_inside_the_multi_field_is_in_its_field_frame(self, open_page):
        page = open_page(self.url_name)
        group = page.find("fieldset", id=f"{LAYOUT_FAILING_PREFIX}-contact")
        error_id = layout_field_id(LAYOUT_FAILING_PREFIX, "email") + "_error"
        frame = group.find(id="div_" + layout_field_id(LAYOUT_FAILING_PREFIX, "email"))
        assert frame.find(id=error_id) is not None

    def test_the_form_that_fails_is_drawn_without_a_form_element(self, page):
        field = page.find(id=layout_field_id(LAYOUT_FAILING_PREFIX, "first_name"))
        assert field.find_parent("form") is None

    def test_the_form_that_fails_still_draws_its_buttons(self, page):
        actions = page.find(id=f"{LAYOUT_FAILING_PREFIX}-actions")
        assert actions.find("input", attrs={"type": "submit"}) is not None

    @pytest.mark.parametrize("name", ["submit", "reset"])
    def test_the_helper_buttons_are_inside_the_form_after_its_fields(self, page, name):
        field = page.find(id=layout_field_id(HELPER_PREFIX, "first_name"))
        button = page.find("input", attrs={"name": f"{HELPER_PREFIX}-{name}"})
        form = field.find_parent("form")
        assert button.find_parent("form") is form
        assert field in button.find_all_previous("input")

    def test_the_small_layout_row_holds_its_fields_with_no_column(self, page):
        row = page.find(id=f"{SMALL_PREFIX}-row")
        for name in LAYOUT_ROW_FIELDS:
            assert row.find("input", id=layout_field_id(SMALL_PREFIX, name))
        assert row.find("div", id=f"{SMALL_PREFIX}-column") is None

    def test_the_small_layout_ends_in_a_button_holder_with_a_button(self, page):
        holder = page.find(id=f"{SMALL_PREFIX}-actions")
        assert holder.find("input", attrs={"name": f"{SMALL_PREFIX}-submit"})

    def test_every_described_id_exists(self, page):
        described = page.find_all(attrs={"aria-describedby": True})
        assert described
        for element in described:
            for described_id in element["aria-describedby"].split():
                assert page.find(id=described_id) is not None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestLayoutObjectsPage(LayoutObjectsPageContract):
    url_name = "layout-objects"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("layout-objects")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("layout-objects-standalone")) is not None


class TestStandaloneLayoutObjectsPage(LayoutObjectsPageContract):
    url_name = "layout-objects-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, open_page):
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
        assert page.find("a", href=reverse("layout-objects")) is not None
