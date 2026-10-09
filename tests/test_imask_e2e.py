"""The script that applies IMask, run in Chrome against pages of the test project."""

from pathlib import Path

import pytest
from django.urls import reverse

from tests.urls import IMASK_URL

pytestmark = pytest.mark.e2e

IMASK = Path(__file__).parent / "data" / "imask-7.6.1.min.js"
# Counts each mask the script reports applying, by the id of its input.
COUNT_MASKS = """
window.masked = [];
document.addEventListener("mvp-forms:imask", (event) =>
  window.masked.push(event.target.id));
"""
INSERT_INPUT = """
(options) => {
  const input = document.createElement("input");
  input.id = "id_later";
  input.name = "later";
  input.dataset.imask = JSON.stringify(options);
  document.getElementById("masked").append(input);
}
"""
INSERT_LINE = """
document.getElementById("masked").append(
  document.getElementById("line").content.cloneNode(true));
"""
MOVE_PHONE = """
const holder = document.createElement("div");
document.getElementById("masked").append(holder);
holder.append(document.getElementById("id_phone"));
"""
# Records each event the script sends, and whether it carries an IMask instance.
LISTEN = """
window.heard = [];
document.addEventListener("mvp-forms:imask", (event) =>
  window.heard.push({
    id: event.target.id,
    instance: event.detail.mask instanceof window.IMask.InputMask,
  }));
"""
# A listener that sets an option the widgets do not carry, on one input only.
UPPERCASE = """
document.addEventListener("mvp-forms:imask", (event) => {
  if (event.target.id === "id_reference") {
    event.detail.mask.updateOptions({ prepareChar: (char) => char.toUpperCase() });
  }
});
"""
# One node holding an input IMask refuses and, after it, an input it accepts.
INSERT_REFUSED_THEN_ACCEPTED = """
const holder = document.createElement("div");
for (const [id, options] of [
  ["id_refused", { kind: "regex", mask: "^a*$", flags: "ii" }],
  ["id_accepted", { kind: "pattern", mask: "000" }],
]) {
  const input = document.createElement("input");
  input.id = id;
  input.dataset.imask = JSON.stringify(options);
  holder.append(input);
}
document.getElementById("masked").append(holder);
"""
DISABLE_BY_FIELDSET = """
const fieldset = document.createElement("fieldset");
fieldset.disabled = true;
document.getElementById("id_pin").before(fieldset);
fieldset.append(document.getElementById("id_pin"));
"""
SELECT = "(node, [from, to]) => node.setSelectionRange(from, to)"
MOVE_BORN = """
const holder = document.createElement("div");
document.getElementById("masked").append(holder);
holder.append(document.getElementById("id_born"));
"""
MASKS_OF = "(id) => window.masked.filter((each) => each === id).length"
ENTRIES = "Object.fromEntries(new FormData(document.getElementById('masked')))"


@pytest.fixture
def page_errors(page):
    """The errors the page raises, as they arrive."""
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    return errors


@pytest.fixture
def masked_page(page, page_errors, live_server):
    """Open a page of the test project, with IMask answered from tests/data."""
    page.route(
        IMASK_URL,
        lambda route: route.fulfill(path=IMASK, content_type="text/javascript"),
    )
    page.add_init_script(COUNT_MASKS)

    def open_page(name="masked", **initial):
        query = "&".join(f"{key}={value}" for key, value in initial.items())
        page.goto(f"{live_server.url}{reverse(name)}?{query}")
        page.wait_for_load_state("load")
        return page

    return open_page


def type_into(page, name, text):
    field = page.locator(f"#id_{name}")
    field.click()
    field.press_sequentially(text)
    return field.input_value()


class TestMaskedInputs:
    def test_a_definition_the_developer_stated_decides_what_is_accepted(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "shelf", "9") == ""
        assert type_into(page, "shelf", "3") == "3"

    def test_a_range_block_refuses_a_number_no_value_in_its_bounds_starts_with(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "day", "4") == ""
        assert type_into(page, "day", "3") == "3"

    def test_an_enum_block_completes_a_value_from_its_list(self, masked_page):
        page = masked_page()

        assert type_into(page, "resolution", "T") == "TV"

    def test_a_repeated_block_stops_after_its_last_repeat(self, masked_page):
        page = masked_page()

        assert type_into(page, "serial", "12345") == "123"

    def test_a_pattern_shown_always_is_shown_with_its_placeholder_character(
        self, masked_page
    ):
        page = masked_page()

        assert page.locator("#id_postcode").input_value() == "#####"

    def test_a_placeholder_character_for_each_definition_is_shown_for_it(
        self, masked_page
    ):
        page = masked_page()

        assert page.locator("#id_reference").input_value() == "aa-####"

    def test_a_built_in_definition_with_a_placeholder_character_keeps_its_rule(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "reference", "1") == "aa-####"

    def test_a_value_the_form_was_drawn_with_is_shown_under_the_mask(self, masked_page):
        page = masked_page(postcode="12")

        assert page.locator("#id_postcode").input_value() == "12###"


class TestRegexMaskedInputs:
    def test_a_character_that_stops_the_value_matching_is_not_accepted(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "customer", "12a3") == "123"

    def test_a_flag_reaches_imask(self, masked_page):
        page = masked_page()

        assert type_into(page, "colour", "#AbC") == "#AbC"


class TestNumberMaskedInputs:
    def test_a_typed_number_gains_its_separators(self, masked_page):
        page = masked_page()

        assert type_into(page, "amount", "1234567,5") == "1 234 567,5"

    def test_an_initial_value_is_shown_with_its_separators(self, masked_page):
        page = masked_page(amount="1234567.5")

        assert page.locator("#id_amount").input_value() == "1 234 567,5"

    def test_a_post_returns_the_plain_number(self, masked_page):
        page = masked_page("masked-cleaned")
        type_into(page, "amount", "1234567,5")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"amount": "1234567.5"' in page.inner_text("body")

    def test_a_page_without_imask_posts_the_plain_number_too(self, masked_page):
        page = masked_page("masked-bare-cleaned", amount="1234567.5")

        assert page.locator("#id_amount").input_value() == "1234567,5"
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"amount": "1234567.5"' in page.inner_text("body")


class TestDynamicMaskedInputs:
    def test_the_mask_in_place_changes_as_more_is_typed(self, masked_page):
        page = masked_page()
        field = page.locator("#id_telephone")

        seven = type_into(page, "telephone", "1234567")
        field.press("End")
        field.press_sequentially("8")

        assert seven == "123-4567"
        assert field.input_value() == "(123) 456-78"

    def test_a_regular_expression_and_a_number_in_the_list_each_apply_their_rule(
        self, masked_page
    ):
        colour = type_into(masked_page(), "code", "#AbCg")
        number = type_into(masked_page(), "code", "12a3")

        assert (colour, number) == ("#AbC", "123")

    def test_a_list_holding_a_display_character_submits_what_was_typed(
        self, masked_page
    ):
        page = masked_page()

        shown = type_into(page, "secret", "1234")
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert shown == "••••"
        assert '"secret": ["1234"]' in page.inner_text("body")


class TestOneMaskForEachInput:
    def test_every_input_is_masked_once_when_the_script_is_on_the_page_once(
        self, masked_page
    ):
        page = masked_page()

        inputs = page.locator("input[data-imask]").evaluate_all(
            "(nodes) => nodes.map((node) => node.id)"
        )

        assert sorted(page.evaluate("window.masked")) == sorted(inputs)

    def test_every_input_is_masked_once_when_the_script_is_on_the_page_three_times(
        self, masked_page
    ):
        page = masked_page("masked-copies")

        inputs = page.locator("input[data-imask]").evaluate_all(
            "(nodes) => nodes.map((node) => node.id)"
        )

        assert sorted(page.evaluate("window.masked")) == sorted(inputs)


class TestInputsAddedAfterThePageLoads:
    def test_an_input_inserted_by_a_script_is_masked_once(self, masked_page):
        page = masked_page()

        page.evaluate(INSERT_INPUT, {"kind": "pattern", "mask": "000"})

        assert type_into(page, "later", "12a3") == "123"
        assert page.evaluate(MASKS_OF, "id_later") == 1

    def test_a_node_holding_an_input_is_masked_once(self, masked_page):
        page = masked_page()

        page.evaluate(INSERT_LINE)

        assert type_into(page, "form-__prefix__-article", "ab1234") == "ab-1234"
        assert page.evaluate(MASKS_OF, "id_form-__prefix__-article") == 1

    def test_an_input_moved_within_the_page_keeps_one_mask(self, masked_page):
        page = masked_page()

        page.evaluate(MOVE_PHONE)

        assert page.evaluate(MASKS_OF, "id_phone") == 1
        assert type_into(page, "phone", "12a3") == "+49 123"

    def test_an_input_in_a_modal_works_once_the_dialog_is_open(self, masked_page):
        page = masked_page()

        page.evaluate("document.getElementById('contact-dialog').showModal()")

        assert type_into(page, "mobile", "12a3") == "+49 123"
        assert page.evaluate(MASKS_OF, "id_mobile") == 1


class TestAnInputIMaskRefuses:
    def test_it_does_not_stop_the_inputs_after_it(self, masked_page, page_errors):
        page = masked_page()

        page.evaluate(INSERT_REFUSED_THEN_ACCEPTED)
        page.wait_for_function("window.masked.includes('id_accepted')")
        field = page.locator("#id_accepted")
        field.click()
        field.press_sequentially("1a2")

        assert field.input_value() == "12"
        assert page_errors == []


class TestDisabledAndReadOnlyInputs:
    def test_a_disabled_input_shows_its_value_under_the_mask_and_stays_disabled(
        self, masked_page
    ):
        page = masked_page(locked="123456")

        field = page.locator("#id_locked")

        assert field.input_value() == "123-456"
        assert field.is_disabled()

    def test_a_read_only_input_shows_its_value_under_the_mask_and_stays_read_only(
        self, masked_page
    ):
        page = masked_page(frozen="654321")

        field = page.locator("#id_frozen")

        assert field.input_value() == "654-321"
        assert field.get_attribute("readonly") is not None
        assert not field.is_editable()


class TestTheEvent:
    def test_a_listener_on_the_document_hears_each_input_with_its_mask(
        self, page, masked_page
    ):
        page.add_init_script(LISTEN)
        masked_page()

        inputs = page.locator("input[data-imask]").evaluate_all(
            "(nodes) => nodes.map((node) => node.id)"
        )
        heard = page.evaluate("window.heard")

        assert sorted(each["id"] for each in heard) == sorted(inputs)
        assert all(each["instance"] for each in heard)

    def test_an_input_added_later_sends_it_too(self, page, masked_page):
        page.add_init_script(LISTEN)
        masked_page()

        page.evaluate(INSERT_INPUT, {"kind": "pattern", "mask": "000"})

        later = [
            each for each in page.evaluate("window.heard") if "later" in each["id"]
        ]
        assert later == [{"id": "id_later", "instance": True}]

    def test_options_updated_from_the_listener_apply_to_what_is_typed_next(
        self, page, masked_page
    ):
        page.add_init_script(UPPERCASE)
        masked_page()

        assert type_into(page, "reference", "ab1234") == "AB-1234"


class TestAPageWithoutIMask:
    def test_it_raises_no_error_and_leaves_a_text_input(self, masked_page, page_errors):
        page = masked_page("masked-bare")

        assert page_errors == []
        assert page.locator("#id_postcode").input_value() == ""
        assert page.locator("#id_postcode").get_attribute("type") == "text"

    def test_it_submits_what_was_typed(self, masked_page):
        page = masked_page("masked-bare")
        type_into(page, "phone", "abc")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert '"phone": ["abc"]' in page.inner_text("body")


class TestWhatTheFormReceives:
    def test_a_display_character_shows_but_the_field_submits_what_was_typed(
        self, masked_page
    ):
        page = masked_page()

        shown = type_into(page, "pin", "1234")
        with page.expect_navigation():
            page.click("button[type=submit]")

        assert shown == "••••"
        assert '"pin": ["1234"]' in page.inner_text("body")

    def test_an_input_removed_from_its_form_adds_no_entry(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate("document.getElementById('id_pin').remove()")

        assert "pin" not in page.evaluate(ENTRIES)

    def test_a_disabled_input_adds_no_entry(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate("document.getElementById('id_pin').disabled = true")

        assert "pin" not in page.evaluate(ENTRIES)

    def test_an_input_disabled_by_its_fieldset_adds_no_entry(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate(DISABLE_BY_FIELDSET)

        assert "pin" not in page.evaluate(ENTRIES)

    def test_a_form_that_was_reset_submits_what_its_inputs_show(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")
        type_into(page, "shelf", "3")

        page.evaluate("document.getElementById('masked').reset()")

        entries = page.evaluate(ENTRIES)
        assert entries["pin"] == page.locator("#id_pin").input_value()
        assert entries["shelf"] == page.locator("#id_shelf").input_value()

    def test_a_value_a_script_assigned_is_what_is_submitted(self, masked_page):
        page = masked_page()
        type_into(page, "pin", "1234")

        page.evaluate("document.getElementById('id_pin').value = '99'")

        assert page.evaluate(ENTRIES)["pin"] == "99"

    def test_a_placeholder_nothing_was_typed_into_submits_nothing(self, masked_page):
        page = masked_page()

        assert page.locator("#id_postcode").input_value() == "#####"
        assert page.evaluate(ENTRIES)["postcode"] == ""

    def test_a_placeholder_partly_filled_submits_what_is_shown(self, masked_page):
        page = masked_page()

        shown = type_into(page, "postcode", "12")

        assert page.evaluate(ENTRIES)["postcode"] == shown == "12###"

    def test_an_input_with_no_name_adds_no_entry(self, masked_page):
        page = masked_page()

        assert "" not in page.evaluate(ENTRIES)


class TestAStrictContentSecurityPolicy:
    def test_a_page_that_forbids_inline_script_is_still_masked(self, masked_page):
        page = masked_page("masked-strict")

        assert type_into(page, "shelf", "9") == ""
        assert type_into(page, "shelf", "3") == "3"


def select_in(page, name, start, end):
    """Focus the input and select the characters from start up to end."""
    field = page.locator(f"#id_{name}")
    field.focus()
    field.evaluate(SELECT, [start, end])
    return field


class TestPartialDateMaskedInput:
    def test_typed_digits_have_their_hyphens_placed(self, masked_page):
        page = masked_page()

        assert type_into(page, "born", "20210314") == "2021-03-14"

    @pytest.mark.parametrize(
        ("typed", "shown"),
        [
            ("202113", "2021-1"),
            ("202100", "2021-0"),
            ("20210332", "2021-03-3"),
            ("20210400", "2021-04-0"),
        ],
    )
    def test_a_digit_that_makes_no_month_or_day_is_refused(
        self, masked_page, typed, shown
    ):
        page = masked_page()

        assert type_into(page, "born", typed) == shown

    @pytest.mark.parametrize(
        ("typed", "shown"),
        [
            ("20210230", "2021-02-0"),
            ("20210229", "2021-02-2"),
            ("20200229", "2020-02-29"),
            ("21000229", "2100-02-2"),
            ("20000229", "2000-02-29"),
            ("20210431", "2021-04-3"),
            ("20210331", "2021-03-31"),
        ],
    )
    def test_a_day_the_typed_month_does_not_have_is_refused(
        self, masked_page, typed, shown
    ):
        page = masked_page()

        assert type_into(page, "born", typed) == shown

    def test_a_single_digit_that_can_only_be_the_whole_month_or_day_is_padded(
        self, masked_page
    ):
        page = masked_page()

        assert type_into(page, "born", "202145") == "2021-04-05"

    def test_a_digit_that_could_start_two_digits_waits_for_the_next(self, masked_page):
        page = masked_page()

        assert type_into(page, "born", "20211") == "2021-1"

    @pytest.mark.parametrize(
        ("pasted", "shown"),
        [("2021-3-4", "2021-03-04"), ("2021-1-4", "2021-01-04"), ("2021-3", "2021-03")],
    )
    def test_a_pasted_date_with_one_digit_parts_is_padded(
        self, masked_page, pasted, shown
    ):
        page = masked_page()
        page.locator("#id_born").focus()

        page.keyboard.insert_text(pasted)

        assert page.locator("#id_born").input_value() == shown

    def test_a_change_in_the_middle_of_a_value_keeps_the_rest(self, masked_page):
        page = masked_page(born="2021-12-14")
        field = select_in(page, "born", 5, 7)

        page.keyboard.type("4")

        assert field.input_value() == "2021-04-14"

    def test_a_change_that_leaves_the_day_without_a_date_is_refused(self, masked_page):
        page = masked_page(born="2020-02-29")
        field = select_in(page, "born", 3, 4)

        page.keyboard.type("1")

        assert field.input_value() == "2020-02-29"

    @pytest.mark.parametrize(
        ("typed", "cleaned"), [("2021", "2021"), ("202103", "2021-03")]
    )
    def test_stopping_after_the_year_or_the_month_submits_a_valid_form(
        self, masked_page, typed, cleaned
    ):
        page = masked_page("masked-cleaned")
        type_into(page, "born", typed)

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert f'"born": "{cleaned}"' in page.inner_text("body")

    @pytest.mark.parametrize(
        ("name", "shown"), [("born_month", "2021-03"), ("born_year", "2021")]
    )
    def test_nothing_finer_than_the_resolution_the_field_states_is_taken(
        self, masked_page, name, shown
    ):
        page = masked_page()

        assert type_into(page, name, "20210314") == shown

    def test_a_year_and_month_the_form_was_drawn_with_are_shown(self, masked_page):
        page = masked_page(born="2021-03")

        assert page.locator("#id_born").input_value() == "2021-03"

    def test_a_value_the_mask_would_change_is_shown_whole(self, masked_page):
        page = masked_page(born="2021-02-30")

        assert page.locator("#id_born").input_value() == "2021-02-30"

    def test_a_value_shown_whole_is_left_alone_when_the_page_is_scanned_again(
        self, masked_page
    ):
        page = masked_page(born="2021-02-30")
        page.evaluate("document.getElementById('id_born').value = '2021-03'")

        page.evaluate(MOVE_BORN)

        assert page.locator("#id_born").input_value() == "2021-03"
        assert page.evaluate(MASKS_OF, "id_born") == 0

    def test_a_value_shown_whole_is_masked_once_it_is_changed_to_one_the_mask_takes(
        self, masked_page
    ):
        page = masked_page(born="2021-02-30")
        field = page.locator("#id_born")
        field.focus()
        field.press("End")
        for _ in range(6):
            field.press("Backspace")

        page.keyboard.type("45")

        assert field.input_value() == "2021-04-05"
        assert page.evaluate(MASKS_OF, "id_born") == 1

    def test_an_input_added_later_is_masked_once(self, masked_page):
        page = masked_page()

        page.evaluate(INSERT_INPUT, {"kind": "partial-date", "resolution": "day"})

        assert type_into(page, "later", "202145") == "2021-04-05"
        assert page.evaluate(MASKS_OF, "id_later") == 1

    def test_a_page_without_imask_raises_no_error_and_submits(
        self, masked_page, page_errors
    ):
        page = masked_page("masked-bare")
        type_into(page, "born", "2021-03")

        with page.expect_navigation():
            page.click("button[type=submit]")

        assert page_errors == []
        assert '"born": ["2021-03"]' in page.inner_text("body")
