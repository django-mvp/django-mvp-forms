"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

import json
import re

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from django.template.loader import get_template
from django.urls import reverse

from demo.autocompletes import ROCKS, UNGROUPED_ROCKS
from demo.forms import DAISYUI_VERSION, THEME_NAMES, PatternMaskForm
from demo.tomselect_forms import SampleFormSet, country_field
from demo.tomselect_views import TomSelectMixin
from mvp_forms.choices import Modifiers
from tests.forms import ruled_data
from tests.legibility.catalogue import Catalogue
from tests.legibility.reader import Reader
from tests.legibility.themes import THEMES_CSS, Themes

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


ATTACHED_PREFIX = "attached"
ATTACHED_FAILING_PREFIX = "failing-attached"
ATTACHED_POST = {f"{ATTACHED_PREFIX}-submit": "Submit"}
ATTACHED_TEXT_FIELDS = ["amount", "weight", "budget"]


def attached_frame(page, prefix, name):
    return page.find(id=f"div_{layout_field_id(prefix, name)}")


class AttachedTextPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = ATTACHED_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize("prefix", [ATTACHED_PREFIX, ATTACHED_FAILING_PREFIX])
    @pytest.mark.parametrize("name", ATTACHED_TEXT_FIELDS)
    def test_each_layout_object_draws_its_input_in_a_wrapper(self, page, prefix, name):
        frame = attached_frame(page, prefix, name)

        wrapper = frame.find("label", class_="input")

        assert wrapper.find(id=layout_field_id(prefix, name)) is not None
        assert wrapper.find("span", class_="label") is not None

    @pytest.mark.parametrize("prefix", [ATTACHED_PREFIX, ATTACHED_FAILING_PREFIX])
    def test_a_select_is_drawn_in_a_wrapper(self, page, prefix):
        frame = attached_frame(page, prefix, "fruit")

        wrapper = frame.find("label", class_="select")

        assert wrapper.find("select", id=layout_field_id(prefix, "fruit"))

    def test_the_form_that_already_fails_shows_the_error_in_a_decorated_frame(
        self, page
    ):
        frame = attached_frame(page, ATTACHED_FAILING_PREFIX, "amount")

        assert frame.find(
            id=layout_field_id(ATTACHED_FAILING_PREFIX, "amount") + "_error"
        )
        assert "input-error" in frame.find("label", class_="input")["class"]

    def test_a_field_that_holds_a_valid_value_shows_no_error(self, page):
        frame = attached_frame(page, ATTACHED_FAILING_PREFIX, "weight")

        assert (
            frame.find(id=layout_field_id(ATTACHED_FAILING_PREFIX, "weight") + "_error")
            is None
        )

    def test_a_post_of_the_empty_form_comes_back_with_an_error_in_a_decorated_frame(
        self, open_page
    ):
        page = open_page(self.url_name, ATTACHED_POST)

        for name in [*ATTACHED_TEXT_FIELDS, "fruit"]:
            frame = attached_frame(page, ATTACHED_PREFIX, name)
            error_id = layout_field_id(ATTACHED_PREFIX, name) + "_error"
            assert frame.find(id=error_id) is not None

    def test_the_form_to_post_is_unbound_on_a_get(self, open_page):
        page = open_page(self.url_name)

        for name in ATTACHED_TEXT_FIELDS:
            frame = attached_frame(page, ATTACHED_PREFIX, name)
            assert frame.find(class_="input-error") is None

    def test_the_form_to_post_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = attached_frame(page, ATTACHED_PREFIX, "amount")
        failing = attached_frame(page, ATTACHED_FAILING_PREFIX, "amount")

        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, ATTACHED_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestAttachedTextPage(AttachedTextPageContract):
    url_name = "attached-text"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("attached-text")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandalonePage(AttachedTextPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, open_page):
        page = open_page(self.url_name)
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_no_script_but_tailwinds_browser_build(self, open_page):
        page = open_page(self.url_name)
        scripts = page.find_all("script", src=True)
        assert [script["src"] for script in scripts] == [
            "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_attached_text_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("attached-text")) is not None


INLINE_PREFIX = "inline"
INLINE_FAILING_PREFIX = "failing-inline"
INLINE_POST = {f"{INLINE_PREFIX}-submit": "Submit"}
INLINE_FIELDS = {"size": "radio", "extras": "checkbox"}


def inline_frame(page, prefix, name):
    return page.find(id=f"div_{layout_field_id(prefix, name)}")


class InlineChoicesPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = INLINE_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize("prefix", [INLINE_PREFIX, INLINE_FAILING_PREFIX])
    @pytest.mark.parametrize("name", INLINE_FIELDS)
    def test_each_group_is_a_fieldset_of_inputs_each_in_a_label_of_its_own(
        self, page, prefix, name
    ):
        frame = inline_frame(page, prefix, name)

        options = frame.find_all("input")

        assert frame.name == "fieldset"
        assert len(options) > 1
        assert {option["type"] for option in options} == {INLINE_FIELDS[name]}
        for option in options:
            assert frame.find("label", attrs={"for": option["id"]}) is not None

    @pytest.mark.parametrize("name", INLINE_FIELDS)
    def test_the_form_that_already_fails_shows_an_error_in_each_group(self, page, name):
        frame = inline_frame(page, INLINE_FAILING_PREFIX, name)

        error_id = layout_field_id(INLINE_FAILING_PREFIX, name) + "_error"

        assert frame.find(id=error_id) is not None

    @pytest.mark.parametrize("name", INLINE_FIELDS)
    def test_a_post_of_the_empty_form_comes_back_with_an_error_in_each_frame(
        self, open_page, name
    ):
        page = open_page(self.url_name, INLINE_POST)

        frame = inline_frame(page, INLINE_PREFIX, name)

        assert frame.find(id=layout_field_id(INLINE_PREFIX, name) + "_error")

    @pytest.mark.parametrize("name", INLINE_FIELDS)
    def test_the_form_to_post_shows_no_error_on_a_get(self, open_page, name):
        page = open_page(self.url_name)

        frame = inline_frame(page, INLINE_PREFIX, name)

        assert frame.find(id=layout_field_id(INLINE_PREFIX, name) + "_error") is None

    def test_the_form_to_post_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = inline_frame(page, INLINE_PREFIX, "size")
        failing = inline_frame(page, INLINE_FAILING_PREFIX, "size")

        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, INLINE_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestInlineChoicesPage(InlineChoicesPageContract):
    url_name = "inline-choices"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("inline-choices")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandaloneInlineChoices(InlineChoicesPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_links_back_to_the_inline_choices_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("inline-choices")) is not None

    def test_a_post_of_the_inline_form_leaves_the_attached_text_form_unbound(
        self, open_page
    ):
        page = open_page(self.url_name, INLINE_POST)

        frame = attached_frame(page, ATTACHED_PREFIX, "amount")

        assert (
            frame.find(id=layout_field_id(ATTACHED_PREFIX, "amount") + "_error") is None
        )

    def test_a_post_of_the_attached_text_form_leaves_the_inline_form_unbound(
        self, open_page
    ):
        page = open_page(self.url_name, ATTACHED_POST)

        frame = inline_frame(page, INLINE_PREFIX, "size")

        assert frame.find(id=layout_field_id(INLINE_PREFIX, "size") + "_error") is None


BUTTONS_PREFIX = "buttons"
BUTTONS_FAILING_PREFIX = "failing-buttons"
BUTTONS_POST = {f"{BUTTONS_PREFIX}-submit": "Submit"}
BUTTON_COUNTS = {"search": 1, "code": 3}


def buttons_frame(page, prefix, name):
    return page.find(id=f"div_{layout_field_id(prefix, name)}")


class FieldWithButtonsPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = BUTTONS_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize("prefix", [BUTTONS_PREFIX, BUTTONS_FAILING_PREFIX])
    @pytest.mark.parametrize(("name", "count"), BUTTON_COUNTS.items())
    def test_each_field_is_one_join_of_its_input_first_and_then_its_buttons(
        self, page, prefix, name, count
    ):
        frame = buttons_frame(page, prefix, name)

        joins = frame.find_all(class_="join")
        parts = joins[0].find_all(True, recursive=False)

        assert len(joins) == 1
        assert parts[0]["id"] == layout_field_id(prefix, name)
        assert "join-item" in parts[0]["class"]
        assert [part.name for part in parts[1:]] == ["button"] * count

    @pytest.mark.parametrize("name", BUTTON_COUNTS)
    def test_the_form_that_already_fails_shows_an_error_in_each_frame(self, page, name):
        frame = buttons_frame(page, BUTTONS_FAILING_PREFIX, name)

        error_id = layout_field_id(BUTTONS_FAILING_PREFIX, name) + "_error"

        assert frame.find(id=error_id) is not None

    @pytest.mark.parametrize("name", BUTTON_COUNTS)
    def test_a_post_of_the_empty_form_comes_back_with_an_error_in_each_frame(
        self, open_page, name
    ):
        page = open_page(self.url_name, BUTTONS_POST)

        frame = buttons_frame(page, BUTTONS_PREFIX, name)

        assert frame.find(id=layout_field_id(BUTTONS_PREFIX, name) + "_error")

    @pytest.mark.parametrize("name", BUTTON_COUNTS)
    def test_the_form_to_post_shows_no_error_on_a_get(self, open_page, name):
        page = open_page(self.url_name)

        frame = buttons_frame(page, BUTTONS_PREFIX, name)

        assert frame.find(id=layout_field_id(BUTTONS_PREFIX, name) + "_error") is None

    def test_the_form_to_post_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = buttons_frame(page, BUTTONS_PREFIX, "search")
        failing = buttons_frame(page, BUTTONS_FAILING_PREFIX, "search")

        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, BUTTONS_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestFieldWithButtonsPage(FieldWithButtonsPageContract):
    url_name = "field-with-buttons"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("field-with-buttons")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandaloneFieldWithButtons(FieldWithButtonsPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_links_back_to_the_field_with_buttons_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("field-with-buttons")) is not None

    @pytest.mark.parametrize(
        "data", [ATTACHED_POST, INLINE_POST], ids=["attached", "inline"]
    )
    def test_a_post_of_another_form_leaves_the_buttons_form_unbound(
        self, open_page, data
    ):
        page = open_page(self.url_name, data)

        frame = buttons_frame(page, BUTTONS_PREFIX, "search")

        assert (
            frame.find(id=layout_field_id(BUTTONS_PREFIX, "search") + "_error") is None
        )

    def test_a_post_of_the_buttons_form_leaves_the_others_unbound(self, open_page):
        page = open_page(self.url_name, BUTTONS_POST)

        attached = attached_frame(page, ATTACHED_PREFIX, "amount")
        inline = inline_frame(page, INLINE_PREFIX, "size")

        assert (
            attached.find(id=layout_field_id(ATTACHED_PREFIX, "amount") + "_error")
            is None
        )
        assert inline.find(id=layout_field_id(INLINE_PREFIX, "size") + "_error") is None


UNEDITABLE_PREFIX = "uneditable"
UNEDITABLE_POST = {f"{UNEDITABLE_PREFIX}-submit": "Submit"}


def uneditable_input(page, name):
    return page.find(id=layout_field_id(UNEDITABLE_PREFIX, name))


class UneditableFieldPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = UNEDITABLE_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    def test_the_uneditable_field_shows_its_value_and_is_disabled(self, page):
        field = uneditable_input(page, "account")

        assert field["value"]
        assert field.has_attr("disabled")
        assert "input" in field["class"]

    def test_the_editable_field_beside_it_is_not_disabled(self, page):
        field = uneditable_input(page, "nickname")

        assert field is not None
        assert not field.has_attr("disabled")
        assert field.find_parent("form") is uneditable_input(
            page, "account"
        ).find_parent("form")

    def test_the_form_has_a_form_element_that_posts(self, page):
        field = uneditable_input(page, "account")

        assert field.find_parent("form")["method"] == "post"

    def test_a_post_comes_back_with_no_error_and_the_value_kept(self, open_page):
        page = open_page(self.url_name, UNEDITABLE_POST)
        frame = page.find(id=f"div_{layout_field_id(UNEDITABLE_PREFIX, 'account')}")

        assert (
            frame.find(id=layout_field_id(UNEDITABLE_PREFIX, "account") + "_error")
            is None
        )
        assert uneditable_input(page, "account")["value"]

    @pytest.mark.parametrize("data", [None, UNEDITABLE_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestUneditableFieldPage(UneditableFieldPageContract):
    url_name = "uneditable-field"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("uneditable-field")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandaloneUneditableField(UneditableFieldPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_links_back_to_the_uneditable_field_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("uneditable-field")) is not None

    def test_a_post_of_the_uneditable_form_leaves_the_others_unbound(self, open_page):
        page = open_page(self.url_name, UNEDITABLE_POST)

        attached = attached_frame(page, ATTACHED_PREFIX, "amount")
        inline = inline_frame(page, INLINE_PREFIX, "size")
        buttons = buttons_frame(page, BUTTONS_PREFIX, "search")

        assert (
            attached.find(id=layout_field_id(ATTACHED_PREFIX, "amount") + "_error")
            is None
        )
        assert inline.find(id=layout_field_id(INLINE_PREFIX, "size") + "_error") is None
        assert (
            buttons.find(id=layout_field_id(BUTTONS_PREFIX, "search") + "_error")
            is None
        )

    @pytest.mark.parametrize(
        "data",
        [ATTACHED_POST, INLINE_POST, BUTTONS_POST],
        ids=["attached", "inline", "buttons"],
    )
    def test_a_post_of_another_form_leaves_the_uneditable_form_unbound(
        self, open_page, data
    ):
        page = open_page(self.url_name, data)

        assert uneditable_input(page, "account").has_attr("disabled")
        assert uneditable_input(page, "account")["value"]


INLINE_FIELD_PREFIX = "inline-field"
INLINE_FIELD_FAILING_PREFIX = "failing-inline-field"
INLINE_FIELD_POST = {f"{INLINE_FIELD_PREFIX}-submit": "Submit"}
INLINE_FIELD_NAMES = ["email", "city"]


def inline_field_frame(page, prefix, name):
    return page.find(id=f"div_{layout_field_id(prefix, name)}")


class InlineFieldPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = INLINE_FIELD_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize(
        "prefix", [INLINE_FIELD_PREFIX, INLINE_FIELD_FAILING_PREFIX]
    )
    @pytest.mark.parametrize("name", INLINE_FIELD_NAMES)
    def test_each_inline_field_has_no_label_and_is_named_by_aria_label(
        self, page, prefix, name
    ):
        frame = inline_field_frame(page, prefix, name)
        field = frame.find(id=layout_field_id(prefix, name))

        assert frame.find("label") is None
        assert field["aria-label"]
        assert field["placeholder"] == field["aria-label"]

    @pytest.mark.parametrize("name", INLINE_FIELD_NAMES)
    def test_the_form_that_already_fails_shows_an_error_in_each_frame(self, page, name):
        frame = inline_field_frame(page, INLINE_FIELD_FAILING_PREFIX, name)

        error_id = layout_field_id(INLINE_FIELD_FAILING_PREFIX, name) + "_error"

        assert frame.find(id=error_id) is not None

    @pytest.mark.parametrize("name", INLINE_FIELD_NAMES)
    def test_a_post_of_the_empty_form_comes_back_with_an_error_in_each_frame(
        self, open_page, name
    ):
        page = open_page(self.url_name, INLINE_FIELD_POST)

        frame = inline_field_frame(page, INLINE_FIELD_PREFIX, name)

        assert frame.find(id=layout_field_id(INLINE_FIELD_PREFIX, name) + "_error")

    @pytest.mark.parametrize("name", INLINE_FIELD_NAMES)
    def test_the_form_to_post_shows_no_error_on_a_get(self, open_page, name):
        page = open_page(self.url_name)

        frame = inline_field_frame(page, INLINE_FIELD_PREFIX, name)

        assert (
            frame.find(id=layout_field_id(INLINE_FIELD_PREFIX, name) + "_error") is None
        )

    def test_the_form_to_post_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = inline_field_frame(page, INLINE_FIELD_PREFIX, "email")
        failing = inline_field_frame(page, INLINE_FIELD_FAILING_PREFIX, "email")

        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, INLINE_FIELD_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestInlineFieldPage(InlineFieldPageContract):
    url_name = "inline-field"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("inline-field")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandaloneInlineField(InlineFieldPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_links_back_to_the_inline_field_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("inline-field")) is not None

    @pytest.mark.parametrize(
        "data",
        [ATTACHED_POST, INLINE_POST, BUTTONS_POST, UNEDITABLE_POST],
        ids=["attached", "inline", "buttons", "uneditable"],
    )
    def test_a_post_of_another_form_leaves_the_inline_field_form_unbound(
        self, open_page, data
    ):
        page = open_page(self.url_name, data)

        frame = inline_field_frame(page, INLINE_FIELD_PREFIX, "email")

        assert (
            frame.find(id=layout_field_id(INLINE_FIELD_PREFIX, "email") + "_error")
            is None
        )

    def test_a_post_of_the_inline_field_form_leaves_the_others_unbound(self, open_page):
        page = open_page(self.url_name, INLINE_FIELD_POST)

        attached = attached_frame(page, ATTACHED_PREFIX, "amount")
        inline = inline_frame(page, INLINE_PREFIX, "size")
        buttons = buttons_frame(page, BUTTONS_PREFIX, "search")

        assert (
            attached.find(id=layout_field_id(ATTACHED_PREFIX, "amount") + "_error")
            is None
        )
        assert inline.find(id=layout_field_id(INLINE_PREFIX, "size") + "_error") is None
        assert (
            buttons.find(id=layout_field_id(BUTTONS_PREFIX, "search") + "_error")
            is None
        )


MULTI_WIDGET_PREFIX = "multi-widget"
MULTI_WIDGET_FAILING_PREFIX = "failing-multi-widget"
MULTI_WIDGET_POST = {f"{MULTI_WIDGET_PREFIX}-submit": "Submit"}


def multi_widget_frame(page, prefix):
    return page.find(id=f"div_{layout_field_id(prefix, 'starts')}")


def multi_widget_part(page, prefix, index):
    return page.find(attrs={"name": f"{prefix}-starts_{index}"})


class MultiWidgetFieldPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = MULTI_WIDGET_POST if request.param == "post" else None
        return open_page(self.url_name, data)

    @pytest.mark.parametrize(
        "prefix", [MULTI_WIDGET_PREFIX, MULTI_WIDGET_FAILING_PREFIX]
    )
    def test_each_part_has_an_attribute_of_its_own(self, page, prefix):
        date = multi_widget_part(page, prefix, 0)
        time = multi_widget_part(page, prefix, 1)

        assert date["placeholder"]
        assert time["placeholder"]
        assert date["placeholder"] != time["placeholder"]

    @pytest.mark.parametrize(
        "prefix", [MULTI_WIDGET_PREFIX, MULTI_WIDGET_FAILING_PREFIX]
    )
    def test_each_part_is_an_input_and_the_frame_is_one_fieldset(self, page, prefix):
        frame = multi_widget_frame(page, prefix)

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend")) == 1
        assert "input" in multi_widget_part(page, prefix, 0)["class"]
        assert "input" in multi_widget_part(page, prefix, 1)["class"]

    def test_the_form_that_already_fails_shows_an_error_in_its_frame(self, page):
        frame = multi_widget_frame(page, MULTI_WIDGET_FAILING_PREFIX)

        error_id = layout_field_id(MULTI_WIDGET_FAILING_PREFIX, "starts") + "_error"

        assert frame.find(id=error_id) is not None
        assert (
            "input-error"
            in multi_widget_part(page, MULTI_WIDGET_FAILING_PREFIX, 0)["class"]
        )

    def test_a_post_of_the_empty_form_comes_back_with_an_error_in_the_frame(
        self, open_page
    ):
        page = open_page(self.url_name, MULTI_WIDGET_POST)

        frame = multi_widget_frame(page, MULTI_WIDGET_PREFIX)

        error_id = layout_field_id(MULTI_WIDGET_PREFIX, "starts") + "_error"
        assert frame.find(id=error_id) is not None

    def test_the_form_to_post_shows_no_error_on_a_get(self, open_page):
        page = open_page(self.url_name)

        frame = multi_widget_frame(page, MULTI_WIDGET_PREFIX)

        error_id = layout_field_id(MULTI_WIDGET_PREFIX, "starts") + "_error"
        assert frame.find(id=error_id) is None

    def test_the_form_to_post_has_a_form_element_and_the_failing_one_has_none(
        self, open_page
    ):
        page = open_page(self.url_name)
        posting = multi_widget_frame(page, MULTI_WIDGET_PREFIX)
        failing = multi_widget_frame(page, MULTI_WIDGET_FAILING_PREFIX)

        assert posting.find_parent("form")["method"] == "post"
        assert failing.find_parent("form") is None

    @pytest.mark.parametrize("data", [None, MULTI_WIDGET_POST], ids=["get", "post"])
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestMultiWidgetFieldPage(MultiWidgetFieldPageContract):
    url_name = "multi-widget-field"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("multi-widget-field")}"' in sidebar

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("decorated-fields-standalone")) is not None


class TestDecoratedFieldsStandaloneMultiWidgetField(MultiWidgetFieldPageContract):
    url_name = "decorated-fields-standalone"

    def test_it_links_back_to_the_multi_widget_field_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("multi-widget-field")) is not None

    @pytest.mark.parametrize(
        "data",
        [ATTACHED_POST, INLINE_POST, BUTTONS_POST, UNEDITABLE_POST, INLINE_FIELD_POST],
        ids=["attached", "inline", "buttons", "uneditable", "inline field"],
    )
    def test_a_post_of_another_form_leaves_the_multi_widget_form_unbound(
        self, open_page, data
    ):
        page = open_page(self.url_name, data)

        frame = multi_widget_frame(page, MULTI_WIDGET_PREFIX)

        error_id = layout_field_id(MULTI_WIDGET_PREFIX, "starts") + "_error"
        assert frame.find(id=error_id) is None

    def test_a_post_of_the_multi_widget_form_leaves_the_others_unbound(self, open_page):
        page = open_page(self.url_name, MULTI_WIDGET_POST)

        attached = attached_frame(page, ATTACHED_PREFIX, "amount")
        inline = inline_frame(page, INLINE_PREFIX, "size")
        inline_field = inline_field_frame(page, INLINE_FIELD_PREFIX, "email")

        assert (
            attached.find(id=layout_field_id(ATTACHED_PREFIX, "amount") + "_error")
            is None
        )
        assert inline.find(id=layout_field_id(INLINE_PREFIX, "size") + "_error") is None
        assert (
            inline_field.find(
                id=layout_field_id(INLINE_FIELD_PREFIX, "email") + "_error"
            )
            is None
        )


CHOICES_OVERRIDE_PREFIX = "override"
# A rating's size is on the element that holds its stars.
INPUT_ELEMENTS = ["input", "select", "textarea", "div"]
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


CHOICES_CONTAINERS_PREFIX = "containers"
CHOICES_CONTAINER_SIZES = ["sm", "lg"]


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

    @pytest.mark.parametrize("size", CHOICES_CONTAINER_SIZES)
    def test_a_modal_s_and_an_alert_s_own_buttons_take_the_form_s_size(
        self, page, size
    ):
        prefix = f"{CHOICES_CONTAINERS_PREFIX}-{size}"
        expected = Modifiers.sizes["btn"][size]
        close = page.find("dialog", id=f"{prefix}-dialog").find("button")
        dismiss = page.find(id=f"{prefix}-notice").find("button")
        save = page.find(attrs={"name": f"{prefix}-save"})

        assert expected in close["class"]
        assert expected in dismiss["class"]
        assert expected in save["class"]

    @pytest.mark.parametrize("size", CHOICES_CONTAINER_SIZES)
    def test_a_button_on_the_page_opens_each_sized_modal(self, page, size):
        dialog_id = f"{CHOICES_CONTAINERS_PREFIX}-{size}-dialog"

        assert [
            button
            for button in page.find_all("button", onclick=True)
            if f"'{dialog_id}'" in button["onclick"]
            and button.find_parent("dialog") is None
        ]

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


RATING_PREFIX = "rating"
RATING_FIELDS = ["score", "comfort"]
RATING_STATES = ["help", "error", "disabled"]


def rating_wrapper(page, name, state=None):
    prefix = RATING_PREFIX if state is None else f"{RATING_PREFIX}-{state}"
    return page.find(id=f"id_{prefix}-{name}")


def rating_picked(page, **positions):
    data = {}
    for name, position in positions.items():
        stars = rating_wrapper(page, name).find_all("input")
        data[f"{RATING_PREFIX}-{name}"] = stars[position]["value"]
    return data


class RatingAndRangePageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class RatingFormPageContract(RatingAndRangePageContract):
    @pytest.mark.parametrize("name", RATING_FIELDS)
    def test_every_field_is_a_rating_of_radio_inputs_with_its_name(self, page, name):
        wrapper = rating_wrapper(page, name)

        stars = wrapper.find_all("input")

        assert "rating" in wrapper["class"]
        assert {tag["type"] for tag in stars} == {"radio"}
        assert {tag["name"] for tag in stars} == {f"{RATING_PREFIX}-{name}"}

    def test_the_optional_rating_can_be_cleared_and_the_required_one_cannot(self, page):
        required = rating_wrapper(page, "score").find_all("input")
        optional = rating_wrapper(page, "comfort").find_all("input")

        assert all(tag["value"] != "" for tag in required)
        assert [tag["value"] for tag in optional].count("") == 1

    def test_the_form_posts_with_a_token_and_a_button(self, page):
        form = rating_wrapper(page, "score").find_parent("form")

        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("input", attrs={"type": "submit"}) is not None

    def test_nothing_is_shown_as_cleaned_before_a_post(self, page):
        assert page.find(id=f"{RATING_PREFIX}-cleaned") is None

    def test_a_post_with_a_star_picked_shows_the_value_the_form_cleaned_to(
        self, open_page
    ):
        data = rating_picked(open_page(self.url_name), score=2, comfort=3)

        page = open_page(self.url_name, data)

        shown = page.find(id=f"{RATING_PREFIX}-cleaned-score")
        assert shown.get_text(strip=True) == data[f"{RATING_PREFIX}-score"]
        assert page.find(id=f"{RATING_PREFIX}-cleaned-comfort") is not None

    def test_a_post_draws_the_star_picked_as_picked(self, open_page):
        data = rating_picked(open_page(self.url_name), score=2)

        page = open_page(self.url_name, data)

        checked = [
            tag["value"]
            for tag in rating_wrapper(page, "score").find_all("input")
            if tag.has_attr("checked")
        ]
        assert checked == [data[f"{RATING_PREFIX}-score"]]

    def test_clearing_the_optional_rating_cleans_to_none(self, open_page):
        data = rating_picked(open_page(self.url_name), score=0, comfort=0)

        page = open_page(self.url_name, data)

        shown = page.find(id=f"{RATING_PREFIX}-cleaned-comfort")
        assert shown.get_text(strip=True) == "None"

    def test_a_post_with_no_star_picked_for_the_required_rating_shows_an_error(
        self, open_page
    ):
        page = open_page(self.url_name, {})

        stars = rating_wrapper(page, "score").find_all("input")

        assert all(tag.get("aria-invalid") == "true" for tag in stars)
        assert page.find(id=f"{RATING_PREFIX}-cleaned") is None


class RatingStatesPageContract(RatingAndRangePageContract):
    @pytest.mark.parametrize("state", RATING_STATES)
    def test_every_state_is_drawn_as_a_rating(self, page, state):
        wrapper = rating_wrapper(page, "score", state)

        assert "rating" in wrapper["class"]
        assert len(wrapper.find_all("input")) > 1

    def test_the_rating_with_help_text_is_described_by_it(self, page):
        group = page.find("fieldset", id=f"div_id_{RATING_PREFIX}-help-score")

        described = group["aria-describedby"].split()

        assert f"id_{RATING_PREFIX}-help-score_helptext" in described
        assert page.find(id=described[0]) is not None

    def test_the_rating_in_error_is_invalid_and_draws_its_error(self, page):
        stars = rating_wrapper(page, "score", "error").find_all("input")

        assert all(tag.get("aria-invalid") == "true" for tag in stars)
        assert page.find(id=f"id_{RATING_PREFIX}-error-score_error") is not None

    def test_every_star_of_the_disabled_rating_is_disabled(self, page):
        stars = rating_wrapper(page, "score", "disabled").find_all("input")

        assert all(tag.has_attr("disabled") for tag in stars)

    def test_the_disabled_rating_shows_its_value(self, page):
        stars = rating_wrapper(page, "score", "disabled").find_all("input")

        assert sum(tag.has_attr("checked") for tag in stars) == 1


RANGE_PREFIX = "range"


def range_input(page, state=None):
    prefix = RATING_PREFIX if state is None else f"{RANGE_PREFIX}-{state}"
    return page.find("input", id=f"id_{prefix}-volume")


class RangeFormPageContract(RatingAndRangePageContract):
    def test_the_field_is_a_range_with_its_name_and_the_limits_of_the_field(self, page):
        tag = range_input(page)

        assert tag["type"] == "range"
        assert tag["name"] == f"{RATING_PREFIX}-volume"
        assert (tag["min"], tag["max"], tag["step"]) == ("0", "100", "5")

    def test_a_post_with_the_slider_set_shows_the_number_the_form_cleaned_to(
        self, open_page
    ):
        first = open_page(self.url_name)
        data = {**rating_picked(first, score=2), range_input(first)["name"]: "35"}

        page = open_page(self.url_name, data)

        shown = page.find(id=f"{RATING_PREFIX}-cleaned-volume")
        assert shown.get_text(strip=True) == "35"
        assert range_input(page)["value"] == "35"

    def test_a_post_beyond_the_limits_shows_an_error_and_nothing_cleaned(
        self, open_page
    ):
        first = open_page(self.url_name)
        data = {**rating_picked(first, score=2), range_input(first)["name"]: "500"}

        page = open_page(self.url_name, data)

        tag = range_input(page)
        assert tag["aria-invalid"] == "true"
        assert "range-error" in tag["class"]
        assert page.find(id=f"{RATING_PREFIX}-cleaned") is None


class RangeStatesPageContract(RatingAndRangePageContract):
    @pytest.mark.parametrize("state", RATING_STATES)
    def test_every_state_is_drawn_as_a_range_with_limits_and_a_step(self, page, state):
        tag = range_input(page, state)

        assert tag["type"] == "range"
        assert {"min", "max", "step"} <= set(tag.attrs)

    def test_the_range_with_help_text_is_described_by_it(self, page):
        tag = range_input(page, "help")

        described = tag["aria-describedby"].split()

        assert f"id_{RANGE_PREFIX}-help-volume_helptext" in described
        assert page.find(id=described[0]) is not None

    def test_the_range_in_error_is_invalid_and_draws_its_error(self, page):
        tag = range_input(page, "error")

        assert tag["aria-invalid"] == "true"
        assert "range-error" in tag["class"]
        assert page.find(id=f"id_{RANGE_PREFIX}-error-volume_error") is not None

    def test_the_disabled_range_is_disabled_and_shows_its_value(self, page):
        tag = range_input(page, "disabled")

        assert tag.has_attr("disabled")
        assert tag["value"] == "40"


RATING_OVERRIDE_PREFIX = "override"


def rating_sample(page, kind, name):
    return page.find(id=f"id_{kind}-{name}-score")


def range_sample(page, kind, name):
    return page.find("input", id=f"id_{kind}-{name}-volume")


def stars_of_sample(wrapper):
    return [
        tag for tag in wrapper.find_all("input") if "rating-hidden" not in tag["class"]
    ]


class RatingAndRangeSizesPageContract(RatingAndRangePageContract):
    def test_a_rating_and_a_range_are_drawn_at_every_size_the_tables_have(self, page):
        for name, expected in Modifiers.sizes["rating"].items():
            assert expected in rating_sample(page, "size", name)["class"]
        for name, expected in Modifiers.sizes["range"].items():
            tag = range_sample(page, "size", name)
            assert tag["type"] == "range"
            assert expected in tag["class"]

    def test_a_rating_and_a_range_are_drawn_in_every_colour_the_tables_have(self, page):
        for name, expected in Modifiers.colors["rating"].items():
            stars = stars_of_sample(rating_sample(page, "color", name))
            assert stars
            assert all(expected in tag["class"] for tag in stars)
        for name, expected in Modifiers.colors["range"].items():
            assert expected in range_sample(page, "color", name)["class"]

    def test_the_sizes_and_colours_shown_are_those_of_the_tables(self, page):
        for kind, table in (("size", Modifiers.sizes), ("color", Modifiers.colors)):
            for component, field in (("rating", "score"), ("range", "volume")):
                shown = {
                    tag["id"].split("-")[1]
                    for tag in page.find_all(id=re.compile(f"^id_{kind}-.*-{field}$"))
                }
                assert shown == set(table[component])

    def test_the_fields_that_state_nothing_take_the_forms_size_and_colour(self, page):
        wrapper = page.find(id=f"id_{RATING_OVERRIDE_PREFIX}-inherits_score")
        tag = page.find("input", id=f"id_{RATING_OVERRIDE_PREFIX}-inherits_volume")

        assert Modifiers.sizes["rating"]["sm"] in wrapper["class"]
        assert all(
            Modifiers.colors["rating"]["primary"] in star["class"]
            for star in stars_of_sample(wrapper)
        )
        assert Modifiers.sizes["range"]["sm"] in tag["class"]
        assert Modifiers.colors["range"]["primary"] in tag["class"]

    def test_the_fields_that_override_take_their_own_size_and_colour(self, page):
        wrapper = page.find(id=f"id_{RATING_OVERRIDE_PREFIX}-overrides_score")
        tag = page.find("input", id=f"id_{RATING_OVERRIDE_PREFIX}-overrides_volume")

        assert Modifiers.sizes["rating"]["xl"] in wrapper["class"]
        assert Modifiers.sizes["rating"]["sm"] not in wrapper["class"]
        for star in stars_of_sample(wrapper):
            assert Modifiers.colors["rating"]["accent"] in star["class"]
            assert Modifiers.colors["rating"]["primary"] not in star["class"]
        assert Modifiers.sizes["range"]["xl"] in tag["class"]
        assert Modifiers.colors["range"]["accent"] in tag["class"]
        assert Modifiers.sizes["range"]["sm"] not in tag["class"]
        assert Modifiers.colors["range"]["primary"] not in tag["class"]


class TestRatingAndRangePage(
    RatingFormPageContract,
    RatingStatesPageContract,
    RangeFormPageContract,
    RangeStatesPageContract,
    RatingAndRangeSizesPageContract,
):
    url_name = "rating-and-range"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("rating-and-range")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("rating-and-range-standalone")) is not None


class TestStandaloneRatingAndRangePage(
    RatingFormPageContract,
    RatingStatesPageContract,
    RangeFormPageContract,
    RangeStatesPageContract,
    RatingAndRangeSizesPageContract,
):
    url_name = "rating-and-range-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, page):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("rating-and-range")) is not None


THEMES_FORMS_ID = "theme-forms"
THEMES_STYLESHEET = (
    f"https://cdn.jsdelivr.net/npm/daisyui@{Themes.version(THEMES_CSS.read_text())}"
    "/themes.css"
)
DAISYUI_CDN = "https://cdn.jsdelivr.net/npm/daisyui@5"


class TestThemeList:
    def test_the_demo_lists_the_themes_the_suite_pins(self):
        assert list(THEME_NAMES) == [theme.name for theme in Themes.shipped()]

    def test_the_demo_names_the_version_the_suite_pins(self):
        assert Themes.version(THEMES_CSS.read_text()) == DAISYUI_VERSION


class ThemesPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    def test_the_chooser_has_one_radio_for_each_shipped_theme_and_no_other(self, page):
        radios = page.find_all("input", class_="theme-controller")
        assert sorted(radio["value"] for radio in radios) == sorted(
            theme.name for theme in Themes.shipped()
        )

    def test_the_chooser_is_one_radio_group(self, page):
        radios = page.find_all("input", class_="theme-controller")
        assert {radio["type"] for radio in radios} == {"radio"}
        assert len({radio["name"] for radio in radios}) == 1

    def test_it_links_daisyuis_themes_at_the_pinned_version(self, page):
        links = [link["href"] for link in page.find_all("link", rel="stylesheet")]
        assert THEMES_STYLESHEET in links

    def test_the_forms_hold_every_pairing_the_catalogue_holds(self, page):
        forms_element = page.find(id=THEMES_FORMS_ID)
        assert forms_element is not None

        read = {
            (m.element.kind, m.pairing.name)
            for m in Reader("themes").read(forms_element)
        }
        wanted = {(m.element.kind, m.pairing.name) for m in Catalogue.measurements()}

        assert wanted <= read, sorted(wanted - read)

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]
        assert len(ids) == len(set(ids))


class TestThemesPage(ThemesPageContract):
    url_name = "themes"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("themes")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("themes-standalone")) is not None


class TestStandaloneThemesPage(ThemesPageContract):
    url_name = "themes-standalone"

    def test_it_loads_daisyuis_cdn_install_and_themes_and_no_other_stylesheet(
        self, page
    ):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [DAISYUI_CDN, THEMES_STYLESHEET]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_draws_no_cotton_component(self):
        source = get_template("demo/themes_standalone.html").template.source
        assert "<c-" not in source
        assert "cotton" not in source

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("themes")) is not None


FLOATING_PREFIX = "floating"
FLOATING_FAILING_PREFIX = "failing-floating"
FLOATING_STATES_PREFIX = "floating-states"
FLOATING_BY_NAME_PREFIX = "floating-by-name"
FLOATING_POST = {
    f"{FLOATING_PREFIX}-name": "Ada Lovelace",
    f"{FLOATING_PREFIX}-notes": "Notes on the engine",
    f"{FLOATING_PREFIX}-country": "uk",
    f"{FLOATING_PREFIX}-nickname": "Ada",
    f"{FLOATING_PREFIX}-subscribe": "on",
    f"{FLOATING_PREFIX}-submit": "Submit",
}
FLOATING_EMPTY_POST = {f"{FLOATING_PREFIX}-submit": "Submit"}


def floating_field(page, prefix, name):
    return page.find(id=layout_field_id(prefix, name))


def floating_label_around(page, prefix, name):
    field = floating_field(page, prefix, name)
    return field.find_parent("label", class_="floating-label")


FLOATING_CHOSEN_COMPONENTS = {"name": "input", "notes": "textarea", "country": "select"}
CHOSEN_KINDS = ("size", "color", "variant")


def carried_modifiers(field, kind, component):
    return set(field["class"]) & set(Modifiers.tables[kind][component].values())


class FloatingLabelsPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    @pytest.mark.parametrize("name", ["name", "notes", "country"])
    @pytest.mark.parametrize("prefix", [FLOATING_PREFIX, FLOATING_FAILING_PREFIX])
    def test_the_floating_fields_are_drawn_inside_a_label_that_names_them(
        self, page, prefix, name
    ):
        label = floating_label_around(page, prefix, name)

        assert label["for"] == layout_field_id(prefix, name)

    @pytest.mark.parametrize("name", ["nickname", "subscribe"])
    def test_the_field_that_opts_out_and_the_checkbox_are_not_floating(
        self, page, name
    ):
        field = floating_field(page, FLOATING_PREFIX, name)
        label = page.find("label", attrs={"for": field["id"]})

        assert floating_label_around(page, FLOATING_PREFIX, name) is None
        assert label is not None
        assert "floating-label" not in label.get("class", [])

    def test_every_floating_input_and_textarea_has_a_placeholder_and_a_select_none(
        self, page
    ):
        for name in ("name", "notes"):
            assert floating_field(page, FLOATING_PREFIX, name)["placeholder"]
        assert not floating_field(page, FLOATING_PREFIX, "country").has_attr(
            "placeholder"
        )

    def test_the_form_that_already_fails_keeps_its_marker_help_and_error(self, page):
        field = floating_field(page, FLOATING_FAILING_PREFIX, "name")
        label = floating_label_around(page, FLOATING_FAILING_PREFIX, "name")
        field_id = field["id"]

        assert label.find(attrs={"aria-hidden": "true"}) is not None
        assert page.find(id=f"{field_id}_helptext") is not None
        assert page.find(id=f"{field_id}_error") is not None
        assert field["aria-invalid"] == "true"
        assert {f"{field_id}_helptext", f"{field_id}_error"} <= set(
            field["aria-describedby"].split()
        )

    def test_the_disabled_field_has_its_ordinary_label_and_the_read_only_one_floats(
        self, page
    ):
        locked = floating_field(page, FLOATING_STATES_PREFIX, "locked")
        readonly = floating_field(page, FLOATING_STATES_PREFIX, "readonly")

        assert locked.has_attr("disabled")
        assert floating_label_around(page, FLOATING_STATES_PREFIX, "locked") is None
        assert page.find("label", attrs={"for": locked["id"]}) is not None
        assert readonly.has_attr("readonly")
        assert floating_label_around(page, FLOATING_STATES_PREFIX, "readonly")

    def test_the_form_with_no_layout_floats_only_the_field_named(self, page):
        assert floating_label_around(page, FLOATING_BY_NAME_PREFIX, "title")
        assert floating_label_around(page, FLOATING_BY_NAME_PREFIX, "company") is None

    @pytest.mark.parametrize("kind", CHOSEN_KINDS)
    def test_every_name_in_the_tables_reaches_a_floating_field_of_each_kind(
        self, page, kind
    ):
        for value in Modifiers.names(kind, None):
            prefix = f"floating-{kind}-{value}"
            for name, component in FLOATING_CHOSEN_COMPONENTS.items():
                field = floating_field(page, prefix, name)
                expected = Modifiers.tables[kind][component].get(value)

                assert floating_label_around(page, prefix, name) is not None
                assert carried_modifiers(field, kind, component) == (
                    {expected} - {None}
                )

    def test_the_forms_that_state_a_choice_are_not_form_elements(self, page):
        for kind in CHOSEN_KINDS:
            for value in Modifiers.names(kind, None):
                field = floating_field(page, f"floating-{kind}-{value}", "name")
                assert field.find_parent("form") is None

    def test_the_form_to_submit_posts_with_a_token_and_a_button(self, page):
        form = floating_field(page, FLOATING_PREFIX, "name").find_parent("form")

        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("input", attrs={"type": "submit"}) is not None

    def test_only_the_form_to_submit_is_a_form_element(self, page):
        for prefix in (
            FLOATING_FAILING_PREFIX,
            FLOATING_STATES_PREFIX,
            FLOATING_BY_NAME_PREFIX,
        ):
            field = page.find(id=re.compile(f"^id_{prefix}-"))
            assert field.find_parent("form") is None

    def test_nothing_is_shown_as_cleaned_before_a_post(self, page):
        assert page.find(id=f"{FLOATING_PREFIX}-cleaned") is None

    def test_a_post_shows_what_the_form_cleaned_to(self, open_page):
        page = open_page(self.url_name, FLOATING_POST)

        for name, expected in (
            ("name", "Ada Lovelace"),
            ("country", "uk"),
            ("nickname", "Ada"),
            ("subscribe", "True"),
        ):
            shown = page.find(id=f"{FLOATING_PREFIX}-cleaned-{name}")
            assert shown.get_text(strip=True) == expected

    def test_a_post_keeps_the_fields_floating(self, open_page):
        page = open_page(self.url_name, FLOATING_POST)

        assert floating_label_around(page, FLOATING_PREFIX, "name")
        assert floating_label_around(page, FLOATING_PREFIX, "nickname") is None

    def test_a_post_of_the_empty_form_comes_back_with_its_error(self, open_page):
        page = open_page(self.url_name, FLOATING_EMPTY_POST)

        field = floating_field(page, FLOATING_PREFIX, "name")

        assert page.find(id=f"{field['id']}_error") is not None
        assert field["aria-invalid"] == "true"
        assert page.find(id=f"{FLOATING_PREFIX}-cleaned") is None

    @pytest.mark.parametrize(
        "data",
        [None, FLOATING_POST, FLOATING_EMPTY_POST],
        ids=["get", "valid", "empty"],
    )
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]

        assert len(ids) == len(set(ids))


class TestFloatingLabelsPage(FloatingLabelsPageContract):
    url_name = "floating-labels"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("floating-labels")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("floating-labels-standalone")) is not None


class TestStandaloneFloatingLabelsPage(FloatingLabelsPageContract):
    url_name = "floating-labels-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, page):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("floating-labels")) is not None


JOINED_PREFIX = "joined"
JOINED_FAILING_PREFIX = "failing-joined"
JOINED_HELP_PREFIX = "joined-help"
JOINED_STATES_PREFIX = "joined-states"
JOINED_UNLABELLED_PREFIX = "joined-unlabelled"
JOINED_SINGLE_PREFIX = "joined-single"
JOINED_POST = {
    f"{JOINED_PREFIX}-country_code": "+44",
    f"{JOINED_PREFIX}-number": "5551234",
    f"{JOINED_PREFIX}-submit": "Submit",
}
JOINED_ONE_MEMBER_FAILS = {
    f"{JOINED_PREFIX}-country_code": "+44",
    f"{JOINED_PREFIX}-submit": "Submit",
}


def joined_field(page, prefix, name):
    return page.find(id=layout_field_id(prefix, name))


def join_around(page, prefix, name):
    return joined_field(page, prefix, name).find_parent("div", class_="join")


def members_of(group):
    return [tag["name"] for tag in group.find_all(True, recursive=False)]


JOINED_CHOSEN_COMPONENTS = {"country_code": "select", "number": "input"}
JOINED_ERROR_PREFIX = "joined-error"
JOINED_CHOICE_PREFIX = "joined-choice"


class JoinedGroupsPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    def test_the_form_to_submit_joins_the_code_and_the_number_under_one_legend(
        self, page
    ):
        group = join_around(page, JOINED_PREFIX, "number")

        assert members_of(group) == [
            f"{JOINED_PREFIX}-country_code",
            f"{JOINED_PREFIX}-number",
        ]
        assert len(group.find_parent("fieldset").find_all("legend")) == 1

    def test_the_form_that_already_fails_flags_only_the_member_that_failed(self, page):
        number = joined_field(page, JOINED_FAILING_PREFIX, "number")
        code = joined_field(page, JOINED_FAILING_PREFIX, "country_code")

        assert number["aria-invalid"] == "true"
        assert not code.has_attr("aria-invalid")
        assert page.find(id=f"{number['id']}_error") is not None
        assert page.find(id=f"{code['id']}_error") is None

    def test_a_member_with_help_text_is_described_by_it(self, page):
        amount = joined_field(page, JOINED_HELP_PREFIX, "amount")
        unit = joined_field(page, JOINED_HELP_PREFIX, "unit")

        assert page.find(id=f"{amount['id']}_helptext") is not None
        assert f"{amount['id']}_helptext" in amount["aria-describedby"].split()
        assert not unit.has_attr("aria-describedby")

    def test_the_states_group_has_a_disabled_a_read_only_and_a_hidden_member(
        self, page
    ):
        group = join_around(page, JOINED_STATES_PREFIX, "locked")
        locked = joined_field(page, JOINED_STATES_PREFIX, "locked")
        reference = joined_field(page, JOINED_STATES_PREFIX, "reference")
        token = joined_field(page, JOINED_STATES_PREFIX, "token")

        assert locked.has_attr("disabled")
        assert reference.has_attr("readonly")
        assert token["type"] == "hidden"
        assert token.find_parent(class_="join") is None
        assert token["name"] not in members_of(group)
        assert locked["name"] in members_of(group)
        assert reference["name"] in members_of(group)

    def test_the_group_with_no_label_has_no_legend_and_names_its_inputs(self, page):
        group = join_around(page, JOINED_UNLABELLED_PREFIX, "amount")

        assert group.find_parent("fieldset").find("legend") is None
        for tag in group.find_all(True, recursive=False):
            assert tag["aria-label"]

    def test_the_group_of_one_is_a_join_of_one_input(self, page):
        group = join_around(page, JOINED_SINGLE_PREFIX, "quantity")

        assert members_of(group) == [f"{JOINED_SINGLE_PREFIX}-quantity"]

    @pytest.mark.parametrize("kind", CHOSEN_KINDS)
    def test_every_name_in_the_tables_reaches_every_member_of_a_group(self, page, kind):
        for value in Modifiers.names(kind, None):
            prefix = f"joined-{kind}-{value}"
            for name, component in JOINED_CHOSEN_COMPONENTS.items():
                field = joined_field(page, prefix, name)
                expected = Modifiers.tables[kind][component].get(value)

                assert join_around(page, prefix, name) is not None
                assert carried_modifiers(field, kind, component) == (
                    {expected} - {None}
                )

    def test_in_the_coloured_group_only_the_failing_member_carries_the_error_modifier(
        self, page
    ):
        number = joined_field(page, JOINED_ERROR_PREFIX, "number")
        code = joined_field(page, JOINED_ERROR_PREFIX, "country_code")
        colour = Modifiers.colors

        assert number["aria-invalid"] == "true"
        assert carried_modifiers(number, "color", "input") == {colour["input"]["error"]}
        assert carried_modifiers(code, "color", "select") == {
            colour["select"]["primary"]
        }

    def test_the_choice_around_a_group_wins_over_the_form_for_each_member(self, page):
        for name, component in JOINED_CHOSEN_COMPONENTS.items():
            field = joined_field(page, JOINED_CHOICE_PREFIX, name)

            assert carried_modifiers(field, "size", component) == {
                Modifiers.sizes[component]["lg"]
            }
            assert carried_modifiers(field, "color", component) == {
                Modifiers.colors[component]["accent"]
            }

    def test_the_forms_that_state_a_choice_are_not_form_elements(self, page):
        prefixes = [
            f"joined-{kind}-{value}"
            for kind in CHOSEN_KINDS
            for value in Modifiers.names(kind, None)
        ]
        for prefix in [*prefixes, JOINED_ERROR_PREFIX, JOINED_CHOICE_PREFIX]:
            assert joined_field(page, prefix, "number").find_parent("form") is None

    def test_the_form_to_submit_posts_with_a_token_and_a_button(self, page):
        form = joined_field(page, JOINED_PREFIX, "number").find_parent("form")

        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find("input", attrs={"type": "submit"}) is not None

    def test_only_the_form_to_submit_is_a_form_element(self, page):
        for prefix in (
            JOINED_FAILING_PREFIX,
            JOINED_HELP_PREFIX,
            JOINED_STATES_PREFIX,
            JOINED_UNLABELLED_PREFIX,
            JOINED_SINGLE_PREFIX,
        ):
            field = page.find(id=re.compile(f"^id_{prefix}-"))
            assert field.find_parent("form") is None

    def test_nothing_is_shown_as_cleaned_before_a_post(self, page):
        assert page.find(id=f"{JOINED_PREFIX}-cleaned") is None

    def test_a_valid_post_shows_what_the_form_cleaned_to(self, open_page):
        page = open_page(self.url_name, JOINED_POST)

        for name, expected in (("country_code", "+44"), ("number", "5551234")):
            shown = page.find(id=f"{JOINED_PREFIX}-cleaned-{name}")
            assert shown.get_text(strip=True) == expected

    def test_a_post_that_fails_in_one_member_comes_back_with_that_members_error(
        self, open_page
    ):
        page = open_page(self.url_name, JOINED_ONE_MEMBER_FAILS)

        number = joined_field(page, JOINED_PREFIX, "number")
        code = joined_field(page, JOINED_PREFIX, "country_code")
        assert number["aria-invalid"] == "true"
        assert not code.has_attr("aria-invalid")
        assert page.find(id=f"{number['id']}_error") is not None
        assert code.find("option", selected=True)["value"] == "+44"
        assert page.find(id=f"{JOINED_PREFIX}-cleaned") is None

    @pytest.mark.parametrize(
        "data",
        [None, JOINED_POST, JOINED_ONE_MEMBER_FAILS],
        ids=["get", "valid", "one member fails"],
    )
    def test_no_id_repeats(self, open_page, data):
        page = open_page(self.url_name, data)
        ids = [element["id"] for element in page.find_all(id=True)]

        assert len(ids) == len(set(ids))


class TestJoinedGroupsPage(JoinedGroupsPageContract):
    url_name = "joined-groups"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("joined-groups")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("joined-groups-standalone")) is not None


class TestStandaloneJoinedGroupsPage(JoinedGroupsPageContract):
    url_name = "joined-groups-standalone"

    def test_it_carries_no_stylesheet_but_daisyuis_cdn_build(self, page):
        sheets = page.find_all("link", rel="stylesheet")
        assert [sheet["href"] for sheet in sheets] == [
            "https://cdn.jsdelivr.net/npm/daisyui@5"
        ]

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("joined-groups")) is not None


TOMSELECT_PREFIX = "tomselect"
TOMSELECT_STYLESHEET = "mvp_forms/tomselect.css"
TOMSELECT_SUBMIT = {f"{TOMSELECT_PREFIX}-submit": "Submit"}
TOMSELECT_WITH_COUNTRY = {**TOMSELECT_SUBMIT, f"{TOMSELECT_PREFIX}-country": "Germany"}
TOMSELECT_CONTROLS_OF_A_LINE = ("country", "rock", "keywords")
TOMSELECT_NEW_KEYWORD = "a-keyword-no-option-holds"
TOMSELECT_WITH_NEW_KEYWORD = {
    **TOMSELECT_WITH_COUNTRY,
    f"{TOMSELECT_PREFIX}-keywords": [TOMSELECT_NEW_KEYWORD],
}
# The prefix of each form the page draws in a state, a size, a colour and a variant.
TOMSELECT_SECTIONS = [
    *(f"state-{state}" for state, _ in TomSelectMixin.states),
    *(f"size-{name}" for name in Modifiers.names("size", "select")),
    *(f"color-{name}" for name in Modifiers.names("color", "select")),
    *(f"variant-{name}" for name in Modifiers.names("variant", "select")),
]


def links_the_tomselect_stylesheet(page):
    return any(
        TOMSELECT_STYLESHEET in link["href"]
        for link in page.find_all("link", rel="stylesheet")
    )


class TomSelectPageContract:
    url_name = ""

    @pytest.fixture(params=["get", "post"])
    def page(self, request, open_page):
        data = TOMSELECT_WITH_COUNTRY if request.param == "post" else None
        return open_page(self.url_name, data)

    def test_it_links_the_stylesheet_for_the_controls(self, open_page):
        assert links_the_tomselect_stylesheet(open_page(self.url_name))

    def test_the_form_draws_a_select_for_each_of_its_controls(self, open_page):
        page = open_page(self.url_name)

        for name in ("plan", "country", "spoken", "languages", "keywords", "rock"):
            assert page.find("select", id=f"id_{TOMSELECT_PREFIX}-{name}") is not None

    def test_each_state_size_colour_and_variant_is_drawn(self, open_page):
        page = open_page(self.url_name)

        missing = [
            prefix
            for prefix in TOMSELECT_SECTIONS
            if page.find("select", id=f"id_{prefix}-country") is None
        ]

        assert missing == []

    def test_a_get_shows_nothing_cleaned(self, open_page):
        assert open_page(self.url_name).find(id=f"{TOMSELECT_PREFIX}-cleaned") is None

    def test_a_post_with_a_country_shows_what_the_form_cleaned_to(self, open_page):
        page = open_page(self.url_name, TOMSELECT_WITH_COUNTRY)

        shown = page.find(id=f"{TOMSELECT_PREFIX}-cleaned-country")
        assert shown.get_text(strip=True) == "Germany"

    def test_a_post_with_a_keyword_that_is_not_an_option_shows_it_cleaned(
        self, open_page
    ):
        page = open_page(self.url_name, TOMSELECT_WITH_NEW_KEYWORD)

        shown = page.find(id=f"{TOMSELECT_PREFIX}-cleaned-keywords")
        assert TOMSELECT_NEW_KEYWORD in shown.get_text()

    def test_the_modal_holds_its_three_controls_and_no_other_modal_control_is_outside(
        self, open_page
    ):
        page = open_page(self.url_name)

        dialog = page.find("dialog", id="modal-dialog")
        inside = {select["id"] for select in dialog.find_all("select")}
        everywhere = {
            select["id"]
            for select in page.find_all("select", id=re.compile("^id_modal-"))
        }
        expected = {f"id_modal-{name}" for name in TOMSELECT_CONTROLS_OF_A_LINE}
        assert inside == everywhere == expected

    def test_the_table_draws_a_control_in_every_row(self, open_page):
        page = open_page(self.url_name)

        rows = [
            row
            for row in page.find("table").find_all("tr")
            if row.find("select") is not None
        ]
        assert [
            {select["id"] for select in row.find_all("select")} for row in rows
        ] == [
            {f"id_samples-{line}-{name}" for name in TOMSELECT_CONTROLS_OF_A_LINE}
            for line in range(SampleFormSet.extra)
        ]

    def test_a_post_without_a_country_comes_back_in_error(self, open_page):
        page = open_page(self.url_name, TOMSELECT_SUBMIT)

        country = page.find(id=f"id_{TOMSELECT_PREFIX}-country")
        assert country["aria-invalid"] == "true"
        assert page.find(id=f"{country['id']}_error") is not None
        assert page.find(id=f"{TOMSELECT_PREFIX}-cleaned") is None

    def test_no_id_repeats(self, page):
        ids = [element["id"] for element in page.find_all(id=True)]

        assert len(ids) == len(set(ids))


class TestTomSelectPage(TomSelectPageContract):
    url_name = "tomselect"

    def test_the_shell_wraps_it(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_lists_it_under_a_group_apart_from_the_standard_pages(
        self, open_page
    ):
        nav = open_page("overview").find(attrs={"aria-label": "Main navigation"})
        entries = [
            link["href"] if (link := item.find("a")) else None
            for item in nav.find_all("li", recursive=False)
        ]
        mine = entries.index(reverse("tomselect"))
        standard = [
            position
            for position, href in enumerate(entries)
            if href and href != reverse("tomselect")
        ]

        assert max(standard) < mine
        assert not any(entries[max(standard) + 1 : mine])
        assert mine - max(standard) > 1

    def test_it_links_the_standalone_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("tomselect-standalone")) is not None


class TestStandaloneTomSelectPage(TomSelectPageContract):
    url_name = "tomselect-standalone"

    def test_it_carries_none_of_the_shells_navigation(self, open_page):
        page = open_page(self.url_name)
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_links_back_to_the_shell_page(self, open_page):
        page = open_page(self.url_name)
        assert page.find("a", href=reverse("tomselect")) is not None


class TestTheFormHtmxFetches:
    def fetched(self, client, parse, count):
        response = client.get(reverse("tomselect-fetched"), {"count": count})
        assert response.status_code == 200
        return parse(response.content.decode())

    @pytest.mark.parametrize("count", ["1", "2", "7"])
    def test_its_controls_carry_a_prefix_that_follows_the_count_asked_for(
        self, client, db, parse, count
    ):
        page = self.fetched(client, parse, count)

        ids = {select["id"] for select in page.find_all("select")}
        assert ids == {f"id_fetched-{count}-{name}" for name in ("country", "keywords")}

    def test_its_ids_collide_with_none_on_the_page_and_none_of_another_fetch(
        self, client, db, open_page, parse
    ):
        page = open_page("tomselect")
        first = self.fetched(client, parse, "2")
        second = self.fetched(client, parse, "3")

        on_the_page, one, other = (
            {element["id"] for element in soup.find_all(id=True)}
            for soup in (page, first, second)
        )
        assert not on_the_page & one
        assert not one & other


class TestThePageHtmxNavigationLoads:
    def test_it_responds_and_draws_the_form_with_its_controls(self, open_page):
        page = open_page("tomselect-boosted")

        for name in ("country", "keywords", "rock"):
            assert page.find("select", id=f"id_{TOMSELECT_PREFIX}-{name}") is not None


class TestTheDemosHtmxSetting:
    def test_use_htmx_is_set_in_the_default_configuration(self, settings):
        assert settings.TOMSELECT["DEFAULT_CONFIG"]["use_htmx"] is True

    def test_a_control_of_the_demo_reads_it(self):
        assert country_field().widget.use_htmx is True


class TestTheRocksEndpoint:
    @pytest.fixture
    def results(self, client, db):
        response = client.get(reverse("ac-rocks"))
        assert response.status_code == 200
        return response.json()["results"]

    def test_a_grouped_rock_names_its_group(self, results):
        groups = {rock: group for group, rocks in ROCKS.items() for rock in rocks}
        grouped = {
            result["value"]: result["optgroup"]
            for result in results
            if "optgroup" in result
        }

        assert grouped == groups

    def test_the_rocks_that_have_no_group_carry_no_optgroup_key(self, results):
        ungrouped = {result["value"] for result in results if "optgroup" not in result}

        assert ungrouped == set(UNGROUPED_ROCKS)


class TestEveryShellPage:
    def test_every_page_the_sidebar_lists_links_the_stylesheet(
        self, client, db, overview_page, parse
    ):
        nav = parse(overview_page).find(attrs={"aria-label": "Main navigation"})
        hrefs = [link["href"] for link in nav.find_all("a", href=True)]

        unlinked = [
            href
            for href in hrefs
            if not links_the_tomselect_stylesheet(parse(client.get(href).content))
        ]

        assert reverse("tomselect") in hrefs
        assert unlinked == []


PATTERN_PREFIX = "pattern"
PATTERN_POST = {
    "phone": "+49 151 2345678",
    "postcode": "12345",
    "reference": "ab-1234",
    "shelf": "3-12",
    "date": "24.12.2025",
    "resolution": "HD",
    "licence": "AB12-CD34-EF56",
    "pin": "1234",
}
REFERENCE_OPTIONS = {
    "kind": "pattern",
    "mask": "aa-0000",
    "definitions": {"0": {"placeholderChar": "#"}, "a": {"placeholderChar": "a"}},
    "lazy": False,
}


class InputMasksPageContract:
    url_name = ""

    @pytest.fixture
    def page(self, open_page):
        return open_page(self.url_name)

    def test_the_pattern_section_holds_a_masked_input_for_each_field(self, page):
        section = page.find(id=PATTERN_PREFIX)

        masked = section.find_all("input", attrs={"data-imask": True})

        assert {tag["name"] for tag in masked} == {
            f"{PATTERN_PREFIX}-{name}" for name in PatternMaskForm.base_fields
        }

    def test_a_post_of_the_pattern_form_returns_what_each_field_received(
        self, open_page
    ):
        data = {f"{PATTERN_PREFIX}-{name}": v for name, v in PATTERN_POST.items()}
        data[f"{PATTERN_PREFIX}-submit"] = ""

        page = open_page(self.url_name, data)

        rows = page.find(id=PATTERN_PREFIX).find("table").find("tbody").find_all("tr")
        received = [row.find_all("code")[1].get_text() for row in rows]
        assert received == list(PATTERN_POST.values())

    def test_the_reference_states_a_placeholder_character_for_each_definition(
        self, page
    ):
        options = json.loads(
            page.find(id=f"id_{PATTERN_PREFIX}-reference")["data-imask"]
        )

        assert options == {**REFERENCE_OPTIONS, "overwrite": True}

    def test_the_article_of_the_formset_states_the_same_pattern(self, page):
        options = json.loads(page.find(id="id_lines-0-article")["data-imask"])

        assert options == REFERENCE_OPTIONS

    def test_it_loads_an_exact_version_of_imask_with_an_integrity_value(self, page):
        scripts = page.find_all("script", src=re.compile(r"^https://.*imask"))

        assert len(scripts) == 1
        assert "imask@7.6.1/" in scripts[0]["src"]
        assert scripts[0]["integrity"].startswith("sha384-")
        assert scripts[0]["crossorigin"] == "anonymous"


class TestInputMasksPage(InputMasksPageContract):
    url_name = "input-masks"

    def test_the_shell_wraps_it(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is not None

    def test_the_sidebar_links_it(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("input-masks")}"' in sidebar

    def test_it_links_the_standalone_page(self, page):
        assert page.find("a", href=reverse("input-masks-standalone")) is not None


class TestStandaloneInputMasksPage(InputMasksPageContract):
    url_name = "input-masks-standalone"

    def test_it_carries_none_of_the_shells_navigation(self, page):
        assert page.find(attrs={"aria-label": "Main navigation"}) is None

    def test_it_draws_no_cotton_component(self):
        source = get_template("demo/input_masks_standalone.html").template.source
        assert "<c-" not in source
        assert "cotton" not in source

    def test_it_links_back_to_the_shell_page(self, page):
        assert page.find("a", href=reverse("input-masks")) is not None
