"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

import re

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from django.urls import reverse

from mvp_forms.choices import Modifiers
from tests.forms import ruled_data

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


CHOICE_STATES = ["empty", "value", "required", "help", "error", "disabled"]
CHOICE_KINDS = [
    ("select", "select", None),
    ("grouped_select", "select", None),
    ("multiple_select", "select", None),
    ("null_boolean", "select", None),
    ("date_year", "select", None),
    ("date_month", "select", None),
    ("date_day", "select", None),
    ("radio", "input", "radio"),
    ("checkbox", "input", "checkbox"),
    ("checkbox_group", "input", "checkbox"),
    ("file", "input", "file"),
    ("clearable_file", "input", "file"),
    ("hidden", "input", "hidden"),
]
GROUP_KINDS = ["date_year", "radio", "checkbox_group"]
HELD_FILE_FIELDS = ["value", "disabled"]
CHOICE_SUBMITTED = {"submit-select": "not a choice"}


def named(page, state, name):
    return page.find_all(attrs={"name": f"{state}-{name}"})


class ChoiceInputsPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = CHOICE_SUBMITTED if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize("state", CHOICE_STATES)
    @pytest.mark.parametrize(("name", "tag", "kind"), CHOICE_KINDS)
    def test_every_kind_is_present_in_every_state(
        self, open_page, state, name, tag, kind
    ):
        page = open_page(self.url_name)
        found = [
            element
            for element in named(page, state, name)
            if element.name == tag and element.get("type") == kind
        ]
        assert found

    @pytest.mark.parametrize(("name", "tag", "kind"), CHOICE_KINDS)
    def test_the_submittable_form_holds_every_kind(self, open_page, name, tag, kind):
        page = open_page(self.url_name)
        found = [
            element
            for element in named(page, "submit", name)
            if element.name == tag and element.get("type") == kind
        ]
        assert found

    def test_the_multiple_select_allows_several_choices(self, open_page):
        page = open_page(self.url_name)
        assert named(page, "empty", "multiple_select")[0].has_attr("multiple")
        assert not named(page, "empty", "select")[0].has_attr("multiple")

    def test_the_required_state_marks_its_inputs_required(self, open_page):
        page = open_page(self.url_name)
        assert named(page, "required", "select")[0].has_attr("required")
        assert not named(page, "empty", "select")[0].has_attr("required")

    def test_the_value_state_holds_a_value(self, open_page):
        page = open_page(self.url_name)
        select = named(page, "value", "select")[0]
        assert select.find("option", selected=True) is not None
        assert named(page, "value", "checkbox")[0].has_attr("checked")
        assert not named(page, "empty", "checkbox")[0].has_attr("checked")
        assert named(page, "value", "hidden")[0].get("value")
        assert not named(page, "empty", "hidden")[0].get("value")

    @pytest.mark.parametrize("state", HELD_FILE_FIELDS)
    def test_a_state_holding_a_file_links_it(self, open_page, state):
        page = open_page(self.url_name)
        file_input = named(page, state, "clearable_file")[0]
        assert file_input.find_parent("div").find("a", href=True) is not None

    def test_a_state_without_a_file_links_none(self, open_page):
        page = open_page(self.url_name)
        file_input = named(page, "empty", "clearable_file")[0]
        assert file_input.find_parent("div").find("a", href=True) is None

    def test_the_help_state_describes_its_inputs(self, open_page):
        page = open_page(self.url_name)
        assert named(page, "help", "select")[0].get("aria-describedby")
        assert named(page, "empty", "select")[0].get("aria-describedby") is None

    def test_the_error_state_shows_a_field_error(self, open_page):
        page = open_page(self.url_name)
        select = named(page, "error", "select")[0]
        assert page.find(id=f"{select['id']}_error") is not None
        assert select["aria-invalid"] == "true"
        assert named(page, "empty", "select")[0].get("aria-invalid") is None

    @pytest.mark.parametrize(
        "name", [name for name, tag, kind in CHOICE_KINDS if kind not in {"hidden"}]
    )
    def test_every_visible_kind_is_invalid_in_the_error_state(self, open_page, name):
        page = open_page(self.url_name)
        inputs = named(page, "error", name)
        assert inputs
        assert all(element["aria-invalid"] == "true" for element in inputs)

    def test_the_error_state_shows_the_alert_a_hidden_field_leads_to(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"role": "alert"}) is not None

    def test_the_disabled_state_disables_every_input(self, open_page):
        page = open_page(self.url_name)
        inputs = page.find_all(["input", "select", "textarea"])
        disabled = [e for e in inputs if e.get("name", "").startswith("disabled-")]
        assert disabled
        assert all(element.has_attr("disabled") for element in disabled)
        assert not named(page, "empty", "select")[0].has_attr("disabled")

    def test_a_text_input_appears_disabled_and_another_read_only(self, open_page):
        page = open_page(self.url_name)
        disabled = page.find(attrs={"name": "textdisabled-text"})
        read_only = page.find(attrs={"name": "textreadonly-text"})
        assert disabled.has_attr("disabled")
        assert not disabled.has_attr("readonly")
        assert read_only.has_attr("readonly")
        assert not read_only.has_attr("disabled")

    @pytest.mark.parametrize("name", ["text", "textarea"])
    def test_the_text_states_hold_text_inputs(self, open_page, name):
        page = open_page(self.url_name)
        tag = "textarea" if name == "textarea" else "input"
        assert page.find(tag, attrs={"name": f"textdisabled-{name}"}) is not None
        assert page.find(tag, attrs={"name": f"textreadonly-{name}"}) is not None

    def test_a_post_comes_back_with_a_field_error(self, open_page):
        page = open_page(self.url_name, CHOICE_SUBMITTED)
        select = named(page, "submit", "select")[0]
        assert page.find(id=f"{select['id']}_error") is not None
        assert select["aria-invalid"] == "true"

    def test_a_post_validates_an_upload(self, open_page):
        upload = SimpleUploadedFile("note.txt", b"held for the response only")
        page = open_page(self.url_name, {**CHOICE_SUBMITTED, "submit-file": upload})
        file_input = named(page, "submit", "file")[0]
        assert page.find(id=f"{file_input['id']}_error") is None
        assert file_input.get("aria-invalid") is None

    def test_a_post_without_an_upload_refuses_the_required_file(self, open_page):
        page = open_page(self.url_name, CHOICE_SUBMITTED)
        file_input = named(page, "submit", "file")[0]
        assert page.find(id=f"{file_input['id']}_error") is not None

    def test_the_submittable_form_is_multipart_with_a_token_and_a_button(
        self, open_page
    ):
        page = open_page(self.url_name)
        form = named(page, "submit", "select")[0].find_parent("form")
        assert form["method"] == "post"
        assert form["enctype"] == "multipart/form-data"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("button", type="submit") is not None

    def test_only_the_submittable_form_is_a_form_element(self, open_page):
        page = open_page(self.url_name)
        for state in CHOICE_STATES:
            assert named(page, state, "select")[0].find_parent("form") is None

    def test_every_visible_input_has_a_label_or_an_aria_label(self, page):
        fields = page.find_all(["input", "select", "textarea"])
        visible = [f for f in fields if f.get("type") not in {"hidden", "submit"}]
        assert visible
        for field in visible:
            labelled = page.find("label", attrs={"for": field["id"]}) is not None
            assert labelled or field.get("aria-label")

    @pytest.mark.parametrize("name", GROUP_KINDS)
    def test_every_group_is_a_fieldset_with_a_legend(self, page, name):
        for state in [*CHOICE_STATES, "submit"]:
            fieldset = named(page, state, name)[0].find_parent("fieldset")
            assert fieldset is not None
            assert fieldset.find("legend") is not None

    def test_every_described_id_exists(self, page):
        described = page.find_all(attrs={"aria-describedby": True})
        assert described
        for element in described:
            for described_id in element["aria-describedby"].split():
                assert page.find(id=described_id) is not None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestChoiceInputsPage(ChoiceInputsPageContract):
    url_name = "choice-inputs"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("choice-inputs")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("choice-inputs-standalone")) is not None


class TestStandaloneChoiceInputsPage(ChoiceInputsPageContract):
    url_name = "choice-inputs-standalone"

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
        assert page.find("a", href=reverse("choice-inputs")) is not None


LAYOUT_SUBMIT_PREFIX = "layout"
LAYOUT_FAILING_PREFIX = "failing"
LAYOUT_ROW_FIELDS = ["first_name", "last_name"]
LAYOUT_INPUT_BUTTONS = ["submit", "reset", "button"]
HELPER_PREFIX = "helper"
SMALL_PREFIX = "small"


ELEMENTS_OF_THE_THIRTEEN_OBJECTS = {
    "Fieldset": {"id": f"{LAYOUT_SUBMIT_PREFIX}-details"},
    "Div": {"id": f"{LAYOUT_SUBMIT_PREFIX}-more"},
    "Row": {"id": f"{LAYOUT_SUBMIT_PREFIX}-row"},
    "Column": {"id": f"{LAYOUT_SUBMIT_PREFIX}-first"},
    "MultiField": {"id": f"{LAYOUT_SUBMIT_PREFIX}-contact"},
    "HTML": {"id": f"{LAYOUT_SUBMIT_PREFIX}-aside"},
    "Submit": {"name": f"{LAYOUT_SUBMIT_PREFIX}-submit"},
    "Reset": {"name": f"{LAYOUT_SUBMIT_PREFIX}-reset"},
    "Button": {"name": f"{LAYOUT_SUBMIT_PREFIX}-button"},
    "StrictButton": {"id": f"{LAYOUT_SUBMIT_PREFIX}-strict"},
    "Hidden": {"name": f"{LAYOUT_SUBMIT_PREFIX}-step"},
    "ButtonHolder": {"id": f"{SMALL_PREFIX}-actions"},
    "FormActions": {"id": f"{LAYOUT_SUBMIT_PREFIX}-actions"},
}


def layout_field_id(prefix, name):
    return f"id_{prefix}-{name}"


class LayoutObjectsPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = {} if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize(
        "attrs",
        ELEMENTS_OF_THE_THIRTEEN_OBJECTS.values(),
        ids=ELEMENTS_OF_THE_THIRTEEN_OBJECTS,
    )
    def test_every_layout_object_is_drawn_once(self, page, attrs):
        assert len(page.find_all(attrs=attrs)) == 1

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


TABS_SUBMIT_PREFIX = "tabs"
TABS_FAILING_PREFIX = "failing-tabs"


def tab_radios(page, prefix):
    return page.find(id=f"{prefix}-tabs").find_all("input", class_="tab")


def checked_tabs(page, prefix):
    radios = tab_radios(page, prefix)
    return [index for index, radio in enumerate(radios) if radio.has_attr("checked")]


class ContainersPageContract:
    url_name = ""

    def test_a_get_checks_the_first_tab_of_the_posting_form(self, open_page):
        page = open_page(self.url_name)
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [0]

    def test_a_post_of_the_empty_form_checks_the_second_tab(self, open_page):
        page = open_page(self.url_name, {})
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [1]

    def test_the_error_comes_back_inside_the_second_tabs_content(self, open_page):
        page = open_page(self.url_name, {})
        content = tab_radios(page, TABS_SUBMIT_PREFIX)[1].find_next_sibling()
        error_id = layout_field_id(TABS_SUBMIT_PREFIX, "street") + "_error"
        assert content.find(id=error_id) is not None

    def test_the_form_that_already_fails_has_its_third_tab_checked(self, open_page):
        page = open_page(self.url_name)
        assert checked_tabs(page, TABS_FAILING_PREFIX) == [2]

    def test_the_posting_form_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = page.find(id=f"{TABS_SUBMIT_PREFIX}-tabs")
        failing = page.find(id=f"{TABS_FAILING_PREFIX}-tabs")
        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, {}], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestTabsPage(ContainersPageContract):
    url_name = "tabs"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("tabs")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("containers-standalone")) is not None


class TestContainersStandalonePage(ContainersPageContract):
    url_name = "containers-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, open_page):
        page = open_page(self.url_name)
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_tabs_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("tabs")) is not None


ACCORDION_PREFIX = "accordion"
CHOSEN_PREFIX = "chosen-accordion"
ACCORDION_POST = {f"{ACCORDION_PREFIX}-submit": "Submit"}


def accordion_groups(page, prefix):
    return page.find(id=f"{prefix}-groups").find_all("details")


def open_groups(page, prefix):
    groups = accordion_groups(page, prefix)
    return [index for index, group in enumerate(groups) if group.has_attr("open")]


class AccordionPageContract:
    url_name = ""

    def test_a_get_opens_the_first_group_of_the_posting_form(self, open_page):
        page = open_page(self.url_name)
        assert open_groups(page, ACCORDION_PREFIX) == [0]

    def test_a_post_of_the_empty_form_opens_the_third_group(self, open_page):
        page = open_page(self.url_name, ACCORDION_POST)
        assert open_groups(page, ACCORDION_PREFIX) == [2]

    def test_the_error_comes_back_inside_the_third_group(self, open_page):
        page = open_page(self.url_name, ACCORDION_POST)
        group = accordion_groups(page, ACCORDION_PREFIX)[2]
        error_id = layout_field_id(ACCORDION_PREFIX, "note") + "_error"
        assert group.find(id=error_id) is not None

    def test_the_second_form_has_the_developers_open_group_open(self, open_page):
        page = open_page(self.url_name)
        assert page.find("details", id=f"{CHOSEN_PREFIX}-open").has_attr("open")

    def test_the_second_form_has_the_developers_closed_group_closed(self, open_page):
        page = open_page(self.url_name)
        assert not page.find("details", id=f"{CHOSEN_PREFIX}-closed").has_attr("open")

    def test_the_second_form_has_no_form_element(self, open_page):
        page = open_page(self.url_name)
        assert page.find(id=f"{CHOSEN_PREFIX}-groups").find_parent("form") is None

    @pytest.mark.parametrize("data", [None, ACCORDION_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestAccordionPage(AccordionPageContract):
    url_name = "accordion"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("accordion")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("containers-standalone")) is not None


class TestContainersStandaloneAccordion(AccordionPageContract):
    url_name = "containers-standalone"

    def test_a_post_of_the_accordion_form_binds_only_that_form(self, open_page):
        page = open_page(self.url_name, ACCORDION_POST)
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [0]

    def test_a_post_of_the_tabs_form_binds_only_that_form(self, open_page):
        page = open_page(self.url_name, {f"{TABS_SUBMIT_PREFIX}-submit": "Submit"})
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [1]
        assert open_groups(page, ACCORDION_PREFIX) == [0]

    def test_it_links_back_to_the_accordion_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("accordion")) is not None


MODAL_PREFIX = "modal"
MODAL_ID = f"{MODAL_PREFIX}-dialog"
MODAL_POST = {f"{MODAL_PREFIX}-submit": "Submit"}


def modal_dialog(page):
    return page.find("dialog", id=MODAL_ID)


class ModalPageContract:
    url_name = ""

    def test_a_get_draws_the_dialog_closed(self, open_page):
        page = open_page(self.url_name)
        assert not modal_dialog(page).has_attr("open")

    def test_a_post_of_the_empty_form_comes_back_with_the_dialog_open(self, open_page):
        page = open_page(self.url_name, MODAL_POST)
        assert modal_dialog(page).has_attr("open")

    def test_the_error_comes_back_inside_the_dialog(self, open_page):
        page = open_page(self.url_name, MODAL_POST)
        error_id = layout_field_id(MODAL_PREFIX, "street") + "_error"
        assert modal_dialog(page).find(id=error_id) is not None

    def test_a_control_outside_the_dialog_names_its_id(self, open_page):
        page = open_page(self.url_name)
        openers = [
            button
            for button in page.find_all("button", attrs={"type": "button"})
            if MODAL_ID in button.get("onclick", "")
        ]
        assert openers
        for button in openers:
            assert button.find_parent("dialog") is None

    def test_the_dialog_is_inside_the_posting_form(self, open_page):
        page = open_page(self.url_name)
        assert modal_dialog(page).find_parent("form")["method"] == "post"

    @pytest.mark.parametrize("data", [None, MODAL_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestModalPage(ModalPageContract):
    url_name = "modal"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("modal")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("containers-standalone")) is not None


class TestContainersStandaloneModal(ModalPageContract):
    url_name = "containers-standalone"

    def test_a_post_of_the_modal_form_binds_only_that_form(self, open_page):
        page = open_page(self.url_name, MODAL_POST)
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [0]
        assert open_groups(page, ACCORDION_PREFIX) == [0]

    def test_a_post_of_the_tabs_form_leaves_the_dialog_closed(self, open_page):
        page = open_page(self.url_name, {f"{TABS_SUBMIT_PREFIX}-submit": "Submit"})
        assert not modal_dialog(page).has_attr("open")

    def test_it_links_back_to_the_modal_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("modal")) is not None


ALERT_PREFIX = "alert"
ALERT_POST = {f"{ALERT_PREFIX}-submit": "Submit"}
ALERT_DISMISSIBLE = f"{ALERT_PREFIX}-dismissible"
ALERT_PERMANENT = f"{ALERT_PREFIX}-permanent"


class AlertPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = ALERT_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    def test_it_holds_an_alert_with_a_dismiss_control(self, page):
        alert = page.find(id=ALERT_DISMISSIBLE)
        assert alert["role"] == "alert"
        assert [button["type"] for button in alert.find_all("button")] == ["button"]

    def test_it_holds_an_alert_without_one(self, page):
        alert = page.find(id=ALERT_PERMANENT)
        assert alert["role"] == "alert"
        assert alert.find("button") is None

    def test_the_alerts_are_inside_the_posting_form(self, page):
        alert = page.find(id=ALERT_DISMISSIBLE)
        assert alert.find_parent("form")["method"] == "post"

    @pytest.mark.parametrize("data", [None, ALERT_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestAlertPage(AlertPageContract):
    url_name = "alert"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("alert")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("containers-standalone")) is not None


class TestContainersStandaloneAlert(AlertPageContract):
    url_name = "containers-standalone"

    def test_it_holds_an_element_for_each_of_the_four_layout_objects(self, open_page):
        page = open_page(self.url_name)
        assert page.find(class_="tabs") is not None
        assert page.find("details") is not None
        assert page.find("dialog") is not None
        assert page.find(attrs={"role": "alert"}) is not None

    def test_a_post_of_the_alert_form_binds_only_that_form(self, open_page):
        page = open_page(self.url_name, ALERT_POST)
        assert checked_tabs(page, TABS_SUBMIT_PREFIX) == [0]
        assert open_groups(page, ACCORDION_PREFIX) == [0]
        assert not modal_dialog(page).has_attr("open")

    def test_a_post_of_the_tabs_form_leaves_the_alerts_drawn(self, open_page):
        page = open_page(self.url_name, {f"{TABS_SUBMIT_PREFIX}-submit": "Submit"})
        assert page.find(id=ALERT_DISMISSIBLE) is not None

    def test_it_links_back_to_the_alert_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("alert")) is not None


FORMSET_SUBMIT_PREFIX = "order"
FORMSET_FAILING_PREFIX = "failing"
FORMSET_PAGES = ["formset-stacked", "formset-table"]
FORMSET_FAILING_LINES = [
    {"item": "pen", "quantity": "0", "unit_price": "2"},
    {"item": "ink", "quantity": "1000", "unit_price": "1000"},
    {"item": "ink", "quantity": "1", "unit_price": "1"},
]


def formset_region(page, prefix):
    return page.find(id=f"{prefix}-formset")


def formset_unit(region, prefix, index):
    """The smallest element holding one form's inputs and no other form's."""
    own = region.find(attrs={"name": f"{prefix}-{index}-item"})
    others = [
        region.find(attrs={"name": f"{prefix}-{other}-item"})
        for other in range(len(FORMSET_FAILING_LINES))
        if other != index
    ]
    unit = None
    for parent in own.parents:
        if any(parent in other.parents for other in others):
            break
        unit = parent
    return unit


def formset_units(region, prefix):
    return [formset_unit(region, prefix, i) for i in range(len(FORMSET_FAILING_LINES))]


class FormsetPageContract:
    url_name = ""
    drawn_as_table = False

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = None
        if request.param == "post":
            data = ruled_data(*FORMSET_FAILING_LINES, prefix=FORMSET_SUBMIT_PREFIX)
        return open_page(self.url_name, data)

    def assert_all_three_errors(self, page, prefix):
        region = formset_region(page, prefix)
        units = formset_units(region, prefix)
        assert region.find(id=f"id_{prefix}-0-quantity_error") is not None
        assert units[1].find(attrs={"role": "alert"}) is not None
        outside = [
            alert
            for alert in region.find_all(attrs={"role": "alert"})
            if not any(unit in alert.parents for unit in units)
        ]
        assert len(outside) == 1

    @pytest.mark.parametrize("index", range(3))
    def test_the_formset_to_submit_has_a_delete_input_in_every_form(
        self, open_page, index
    ):
        page = open_page(self.url_name)
        name = f"{FORMSET_SUBMIT_PREFIX}-{index}-DELETE"
        assert page.find("input", attrs={"name": name, "type": "checkbox"})

    @pytest.mark.parametrize("index", range(3))
    def test_the_formset_to_submit_has_an_order_input_in_every_form(
        self, open_page, index
    ):
        page = open_page(self.url_name)
        name = f"{FORMSET_SUBMIT_PREFIX}-{index}-ORDER"
        assert page.find("input", attrs={"name": name, "type": "number"})

    def test_the_formset_that_already_fails_shows_all_three_kinds_of_error(
        self, open_page
    ):
        self.assert_all_three_errors(open_page(self.url_name), FORMSET_FAILING_PREFIX)

    def test_the_formset_to_submit_starts_without_errors(self, open_page):
        region = formset_region(open_page(self.url_name), FORMSET_SUBMIT_PREFIX)
        assert region.find(attrs={"role": "alert"}) is None
        assert region.find(id=re.compile(r"_error$")) is None

    def test_a_post_of_invalid_data_comes_back_with_all_three_kinds_of_error(
        self, open_page
    ):
        data = ruled_data(*FORMSET_FAILING_LINES, prefix=FORMSET_SUBMIT_PREFIX)
        page = open_page(self.url_name, data)
        self.assert_all_three_errors(page, FORMSET_SUBMIT_PREFIX)

    def test_a_post_keeps_what_was_submitted(self, open_page):
        data = ruled_data(*FORMSET_FAILING_LINES, prefix=FORMSET_SUBMIT_PREFIX)
        page = open_page(self.url_name, data)
        quantity = page.find(attrs={"name": f"{FORMSET_SUBMIT_PREFIX}-1-quantity"})
        assert quantity["value"] == "1000"

    def test_the_formset_to_submit_posts_with_a_token_and_a_submit_button(
        self, open_page
    ):
        page = open_page(self.url_name)
        total = page.find(id=f"id_{FORMSET_SUBMIT_PREFIX}-TOTAL_FORMS")
        form = total.find_parent("form")
        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find(attrs={"type": "submit"}) is not None
        assert form.find(attrs={"name": f"{FORMSET_SUBMIT_PREFIX}-2-item"})

    def test_the_formset_that_fails_is_not_a_form_element(self, open_page):
        page = open_page(self.url_name)
        total = page.find(id=f"id_{FORMSET_FAILING_PREFIX}-TOTAL_FORMS")
        assert total.find_parent("form") is None

    def test_both_formsets_are_drawn_in_the_layout_of_the_page(self, page):
        tables = [
            formset_region(page, prefix).find("table")
            for prefix in (FORMSET_SUBMIT_PREFIX, FORMSET_FAILING_PREFIX)
        ]
        assert all(table is not None for table in tables) is self.drawn_as_table
        assert any(table is not None for table in tables) is self.drawn_as_table

    def test_every_visible_input_has_a_label_or_an_aria_label(self, page):
        fields = page.find_all(["input", "select", "textarea"])
        visible = [f for f in fields if f.get("type") not in {"hidden", "submit"}]
        assert visible
        for field in visible:
            labelled = page.find("label", attrs={"for": field.get("id")}) is not None
            group = field.find_parent("fieldset")
            named = group is not None and (
                group.find("legend") is not None or group.get("aria-label")
            )
            assert labelled or field.get("aria-label") or named

    def test_every_described_id_exists(self, page):
        described = page.find_all(attrs={"aria-describedby": True})
        assert described
        for element in described:
            for described_id in element["aria-describedby"].split():
                assert page.find(id=described_id) is not None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestFormsetPagesInTheSidebar:
    @pytest.mark.parametrize("name", FORMSET_PAGES)
    def test_the_sidebar_links_it(self, overview_page: str, name) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse(name)}"' in sidebar


class TestStackedFormsetPage(FormsetPageContract):
    url_name = "formset-stacked"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("formset-stacked-standalone")) is not None


class TestStandaloneStackedFormsetPage(FormsetPageContract):
    url_name = "formset-stacked-standalone"

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
        assert page.find("a", href=reverse("formset-stacked")) is not None


class TestTableFormsetPage(FormsetPageContract):
    url_name = "formset-table"
    drawn_as_table = True

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("formset-table-standalone")) is not None


class TestStandaloneTableFormsetPage(FormsetPageContract):
    url_name = "formset-table-standalone"
    drawn_as_table = True

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
        assert page.find("a", href=reverse("formset-table")) is not None


CHOICES_OVERRIDE_PREFIX = "override"
INPUT_ELEMENTS = ["input", "select", "textarea"]
BUTTON_ELEMENTS = ["input", "button"]
INPUT_COMPONENTS = [name for name in Modifiers.sizes if name != Modifiers.button]
COMPONENTS_OF = {
    "size": INPUT_COMPONENTS,
    "color": INPUT_COMPONENTS,
    "variant": [name for name in Modifiers.variants if name != Modifiers.button],
}


def carriers(page, elements, classes):
    return [
        element
        for element in page.find_all(elements, class_=True)
        if classes & set(element["class"])
    ]


def modifier_classes(kind, name, components):
    return {Modifiers.tables[kind][component][name] for component in components}


class ChoicesPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    @pytest.mark.parametrize("kind", ["size", "color", "variant"])
    def test_every_name_in_the_tables_is_on_an_input(self, page, kind):
        for name in Modifiers.names(kind, None):
            classes = modifier_classes(kind, name, COMPONENTS_OF[kind])
            assert carriers(page, INPUT_ELEMENTS, classes), name

    @pytest.mark.parametrize("kind", ["size", "color", "variant"])
    def test_every_name_in_the_tables_is_on_a_button(self, page, kind):
        for name in Modifiers.names(kind, Modifiers.button):
            classes = modifier_classes(kind, name, [Modifiers.button])
            assert carriers(page, BUTTON_ELEMENTS, classes), name

    @pytest.mark.parametrize("component", INPUT_COMPONENTS)
    def test_every_kind_of_input_is_drawn_at_a_stated_size(self, page, component):
        classes = set(Modifiers.sizes[component].values())
        assert carriers(page, INPUT_ELEMENTS, classes)

    def test_the_overriding_field_differs_from_the_form(self, page):
        field = page.find(id=f"id_{CHOICES_OVERRIDE_PREFIX}-search")
        large = Modifiers.sizes["input"]["xl"]
        small = Modifiers.sizes["input"]["sm"]
        assert large in field["class"]
        assert small not in field["class"]

    def test_the_overriding_button_differs_from_the_form(self, page):
        button = page.find(attrs={"name": f"{CHOICES_OVERRIDE_PREFIX}-delete"})
        assert Modifiers.colors["btn"]["error"] in button["class"]
        assert Modifiers.colors["btn"]["neutral"] not in button["class"]

    def test_the_field_that_undoes_the_colour_is_drawn_without_it(self, page):
        field = page.find(id=f"id_{CHOICES_OVERRIDE_PREFIX}-notes")
        assert Modifiers.colors["textarea"]["primary"] not in field["class"]
        assert Modifiers.sizes["textarea"]["sm"] in field["class"]

    def test_no_form_element_surrounds_a_form(self, page):
        field = page.find(id=f"id_{CHOICES_OVERRIDE_PREFIX}-search")
        assert field.find_parent("form") is None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestChoicesPage(ChoicesPageContract):
    url_name = "choices"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("choices")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("choices-standalone")) is not None


class TestStandaloneChoicesPage(ChoicesPageContract):
    url_name = "choices-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, page):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("choices")) is not None


DRAWINGS_PREFIX = "drawings"
DRAWINGS_FIELDS = ["remember", "notify", "publish"]


def drawings_input(page, name):
    return page.find(id=f"id_{DRAWINGS_PREFIX}-{name}")


def drawings_submitted(page, on):
    form = drawings_input(page, "remember").find_parent("form")
    data = {}
    for tag in form.find_all("input"):
        name = tag.get("name")
        if not name or tag["type"] == "submit":
            continue
        if tag["type"] == "checkbox":
            if name in on:
                data[name] = tag.get("value", "on")
        else:
            data[name] = tag.get("value", "")
    return data


class DrawingsPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    @pytest.mark.parametrize("name", DRAWINGS_FIELDS)
    def test_every_field_is_a_checkbox_input_with_its_name(self, page, name):
        tag = drawings_input(page, name)
        assert (tag.name, tag["type"]) == ("input", "checkbox")
        assert tag["name"] == f"{DRAWINGS_PREFIX}-{name}"

    def test_the_first_field_is_a_checkbox(self, page):
        tag = drawings_input(page, "remember")
        assert "checkbox" in tag["class"]
        assert "toggle" not in tag["class"]
        assert not tag.has_attr("role")

    def test_the_second_field_is_a_toggle(self, page):
        tag = drawings_input(page, "notify")
        assert "toggle" in tag["class"]
        assert "checkbox" not in tag["class"]
        assert not tag.has_attr("role")

    def test_the_third_field_is_a_switch(self, page):
        tag = drawings_input(page, "publish")
        assert "toggle" in tag["class"]
        assert tag["role"] == "switch"

    def test_the_form_posts_with_a_token_and_a_button(self, page):
        form = drawings_input(page, "remember").find_parent("form")
        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("input", attrs={"type": "submit"}) is not None

    def test_nothing_is_shown_as_cleaned_before_a_post(self, page):
        assert page.find(id=f"{DRAWINGS_PREFIX}-cleaned") is None

    @pytest.mark.parametrize(
        ("on", "expected"),
        [
            ({"notify"}, {"remember": "False", "notify": "True", "publish": "False"}),
            (
                {"remember", "publish"},
                {"remember": "True", "notify": "False", "publish": "True"},
            ),
        ],
    )
    def test_a_post_shows_what_the_form_cleaned_to(self, open_page, on, expected):
        sent = {f"{DRAWINGS_PREFIX}-{name}" for name in on}
        data = drawings_submitted(open_page(self.url_name), sent)

        page = open_page(self.url_name, data)

        for name, value in expected.items():
            shown = page.find(id=f"{DRAWINGS_PREFIX}-cleaned-{name}")
            assert shown.get_text(strip=True) == value

    def test_a_post_draws_each_field_checked_as_it_was_posted(self, open_page):
        sent = {f"{DRAWINGS_PREFIX}-notify", f"{DRAWINGS_PREFIX}-publish"}
        data = drawings_submitted(open_page(self.url_name), sent)

        page = open_page(self.url_name, data)

        assert not drawings_input(page, "remember").has_attr("checked")
        assert drawings_input(page, "notify").has_attr("checked")
        assert drawings_input(page, "publish").has_attr("checked")

    def test_every_input_has_a_label_that_names_it(self, page):
        for name in DRAWINGS_FIELDS:
            field = drawings_input(page, name)
            assert page.find("label", attrs={"for": field["id"]}) is not None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestDrawingsPage(DrawingsPageContract):
    url_name = "drawings"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("drawings")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("drawings-standalone")) is not None


class TestStandaloneDrawingsPage(DrawingsPageContract):
    url_name = "drawings-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, page):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("drawings")) is not None


DRAWING_NAMES = ["checkbox", "toggle", "switch"]
DRAWING_STATES = ["off", "on", "help", "error", "disabled"]
DRAWING_ERROR_MODIFIERS = {
    "checkbox": "checkbox-error",
    "toggle": "toggle-error",
    "switch": "toggle-error",
}


def drawing_state(page, drawing, state):
    return page.find(id=f"id_{drawing}-{state}-flag")


class DrawingStatesPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    @pytest.mark.parametrize("state", DRAWING_STATES)
    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_every_drawing_is_drawn_in_every_state(self, page, drawing, state):
        tag = drawing_state(page, drawing, state)
        assert (tag.name, tag["type"]) == ("input", "checkbox")

    @pytest.mark.parametrize("state", DRAWING_STATES)
    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_each_input_is_drawn_as_its_drawing(self, page, drawing, state):
        tag = drawing_state(page, drawing, state)
        component = "checkbox" if drawing == "checkbox" else "toggle"
        assert component in tag["class"]
        assert tag.get("role") == ("switch" if drawing == "switch" else None)

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_only_the_on_state_is_checked(self, page, drawing):
        for state in DRAWING_STATES:
            tag = drawing_state(page, drawing, state)
            assert tag.has_attr("checked") == (state == "on")

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_the_help_state_is_described_by_its_help_text(self, page, drawing):
        tag = drawing_state(page, drawing, "help")
        for name in tag["aria-describedby"].split():
            assert page.find(id=name) is not None
        assert drawing_state(page, drawing, "off").get("aria-describedby") is None

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_the_error_state_is_required_invalid_and_described_by_its_error(
        self, page, drawing
    ):
        tag = drawing_state(page, drawing, "error")
        label = page.find("label", attrs={"for": tag["id"]})
        assert label.find(attrs={"aria-hidden": "true"}) is not None
        assert tag["aria-invalid"] == "true"
        assert DRAWING_ERROR_MODIFIERS[drawing] in tag["class"]
        assert f"{tag['id']}_error" in tag["aria-describedby"].split()

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_only_the_error_state_is_invalid(self, page, drawing):
        for state in DRAWING_STATES:
            tag = drawing_state(page, drawing, state)
            assert tag.has_attr("aria-invalid") == (state == "error")

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_only_the_disabled_state_is_disabled(self, page, drawing):
        for state in DRAWING_STATES:
            tag = drawing_state(page, drawing, state)
            assert tag.has_attr("disabled") == (state == "disabled")

    @pytest.mark.parametrize("state", DRAWING_STATES)
    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_every_input_has_a_label_that_names_it(self, page, drawing, state):
        tag = drawing_state(page, drawing, state)
        assert page.find("label", attrs={"for": tag["id"]}) is not None

    def test_no_form_element_surrounds_a_state(self, page):
        assert drawing_state(page, "toggle", "off").find_parent("form") is None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestDrawingStatesInThePage(DrawingStatesPageContract):
    url_name = "drawings"


class TestDrawingStatesInTheStandalonePage(DrawingStatesPageContract):
    url_name = "drawings-standalone"


DRAWING_OVERRIDE_PREFIX = "override"
DRAWING_COMPONENTS = {"checkbox": "checkbox", "toggle": "toggle", "switch": "toggle"}


def drawing_sample(page, kind, name, drawing):
    return page.find(id=f"id_{kind}-{name}-{drawing}")


class DrawingSizesPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_every_drawing_is_drawn_at_every_size_the_table_has(self, page, drawing):
        component = DRAWING_COMPONENTS[drawing]
        for name, expected in Modifiers.sizes[component].items():
            tag = drawing_sample(page, "size", name, drawing)
            assert (tag.name, tag["type"]) == ("input", "checkbox")
            assert expected in tag["class"]

    @pytest.mark.parametrize("drawing", DRAWING_NAMES)
    def test_every_drawing_is_drawn_in_every_colour_the_table_has(self, page, drawing):
        component = DRAWING_COMPONENTS[drawing]
        for name, expected in Modifiers.colors[component].items():
            tag = drawing_sample(page, "color", name, drawing)
            assert (tag.name, tag["type"]) == ("input", "checkbox")
            assert expected in tag["class"]

    def test_the_sizes_and_colours_shown_are_those_of_the_toggle_table(self, page):
        for kind, table in (("size", Modifiers.sizes), ("color", Modifiers.colors)):
            shown = {
                tag["id"].split("-")[1]
                for tag in page.find_all(id=re.compile(f"^id_{kind}-.*-toggle$"))
            }
            assert shown == set(table["toggle"])

    @pytest.mark.parametrize("drawing", ["toggle", "switch"])
    def test_no_checkbox_modifier_is_written_on_a_toggle_or_a_switch(
        self, page, drawing
    ):
        for kind in ("size", "color"):
            for tag in page.find_all(id=re.compile(f"^id_{kind}-.*-{drawing}$")):
                assert not [c for c in tag["class"] if c.startswith("checkbox")]

    def test_a_switch_is_a_switch_at_every_size_and_in_every_colour(self, page):
        for tag in page.find_all(id=re.compile("^id_(size|color)-.*-switch$")):
            assert tag["role"] == "switch"

    def test_the_field_that_states_nothing_takes_the_forms_size_and_colour(self, page):
        tag = page.find(id=f"id_{DRAWING_OVERRIDE_PREFIX}-inherits")
        assert tag["role"] == "switch"
        assert Modifiers.sizes["toggle"]["sm"] in tag["class"]
        assert Modifiers.colors["toggle"]["primary"] in tag["class"]

    def test_the_field_that_overrides_takes_its_own_size_and_colour(self, page):
        tag = page.find(id=f"id_{DRAWING_OVERRIDE_PREFIX}-overrides")
        assert Modifiers.sizes["toggle"]["xl"] in tag["class"]
        assert Modifiers.colors["toggle"]["accent"] in tag["class"]
        assert Modifiers.sizes["toggle"]["sm"] not in tag["class"]
        assert Modifiers.colors["toggle"]["primary"] not in tag["class"]

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestDrawingSizesInThePage(DrawingSizesPageContract):
    url_name = "drawings"


class TestDrawingSizesInTheStandalonePage(DrawingSizesPageContract):
    url_name = "drawings-standalone"
