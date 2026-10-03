import pytest
from bs4 import BeautifulSoup

from tests.legibility.pairings import Ink
from tests.legibility.reader import Reader, Uncovered

CONTENT = Ink("base-content")
BASE_100 = Ink("base-100")
BASE_200 = Ink("base-200")
ERROR = Ink("error")
SOFT_ERROR = ERROR.mixed(BASE_100, 0.08)


def read(html, supplied=frozenset(), form_state="fragment"):
    return Reader(form_state, frozenset(supplied)).read(
        BeautifulSoup(html, "html.parser")
    )


def pairs(html, **kwargs):
    return {
        (m.pairing.part, m.pairing.ink, m.pairing.surface) for m in read(html, **kwargs)
    }


def only(html, part, **kwargs):
    found = [m for m in read(html, **kwargs) if m.pairing.part == part]
    assert len(found) == 1, found
    return found[0]


def of(html, part, ink, surface, **kwargs):
    found = [
        m
        for m in read(html, **kwargs)
        if (m.pairing.part, m.pairing.ink, m.pairing.surface) == (part, ink, surface)
    ]
    assert found, pairs(html, **kwargs)
    return found[0]


class TestReader:
    def test_text_with_no_class_is_base_content_on_base_100(self):
        assert pairs("<p>Hello</p>") == {("text", CONTENT, BASE_100)}

    def test_text_outside_any_element_is_read(self):
        assert pairs("Hello") == {("text", CONTENT, BASE_100)}

    def test_whitespace_and_comments_are_not_text(self):
        assert read("<div> \n <!-- note --> </div>") == []

    def test_a_label_is_sixty_percent_of_the_text_ink(self):
        found = of('<p class="label">Help</p>', "text", CONTENT.faded(0.6), BASE_100)

        assert found.held
        assert found.own

    def test_a_label_beside_text_base_content_is_base_content(self):
        html = '<p class="label text-base-content">Help</p>'

        assert pairs(html) == {("text", CONTENT, BASE_100)}

    def test_a_fieldset_legend_is_base_content(self):
        found = of(
            '<legend class="fieldset-legend">Name</legend>', "text", CONTENT, BASE_100
        )

        assert not found.own

    def test_text_error_has_no_row_because_the_pack_no_longer_writes_it(self):
        with pytest.raises(Uncovered) as raised:
            read('<div class="text-error"><p>No</p></div>')

        assert raised.value.class_name == "text-error"

    def test_a_table_header_is_sixty_percent(self):
        html = '<table class="table"><thead><tr><th>Name</th></tr></thead></table>'

        found = of(html, "text", CONTENT.faded(0.6), BASE_100)
        assert found.own

    def test_a_table_header_with_text_base_content_is_not(self):
        html = (
            '<table class="table"><thead class="text-base-content">'
            "<tr><th>Name</th></tr></thead></table>"
        )

        assert pairs(html) == {("text", CONTENT, BASE_100)}

    def test_table_cells_inherit(self):
        html = '<table class="table"><tbody><tr><td>One</td></tr></tbody></table>'

        assert pairs(html) == {("text", CONTENT, BASE_100)}

    def test_text_in_a_base_200_group_is_on_base_200(self):
        html = '<details class="collapse bg-base-200"><div><p>One</p></div></details>'

        assert ("text", CONTENT, BASE_200) in pairs(html)

    def test_text_in_a_modal_box_is_on_base_100_even_inside_base_200(self):
        html = (
            '<div class="bg-base-200"><div class="modal-box"><h3>Title</h3></div></div>'
        )

        assert pairs(html) == {("text", CONTENT, BASE_100)}

    def test_a_script_and_a_style_are_not_text(self):
        assert read("<script>var a = 1;</script><style>p {}</style>") == []

    def test_a_hidden_input_yields_nothing(self):
        assert read('<input type="hidden" name="a" value="b">') == []

    def test_a_class_supplied_by_the_developer_is_passed_over(self):
        assert pairs('<p class="mine">Hi</p>', supplied={"mine"}) == {
            ("text", CONTENT, BASE_100)
        }

    def test_a_class_with_no_row_raises_uncovered_naming_it_and_the_state(self):
        with pytest.raises(Uncovered) as raised:
            read('<p class="mystery">Hi</p>', form_state="unbound")

        assert raised.value.class_name == "mystery"
        assert raised.value.form_state == "unbound"

    def test_a_class_supplied_for_one_reader_is_unknown_to_another(self):
        with pytest.raises(Uncovered):
            read('<p class="mine">Hi</p>')


class TestReaderAlerts:
    PACK = (
        '<div role="alert" class="alert alert-error alert-soft">'
        "<div><p>No</p></div></div>"
    )

    def test_the_packs_error_alert_is_error_on_its_tinted_fill(self):
        found = of(self.PACK, "text", ERROR, SOFT_ERROR)

        assert found.held
        assert found.own

    def test_the_packs_error_alert_with_text_base_content_is_base_content(self):
        html = self.PACK.replace("alert-soft", "alert-soft text-base-content")

        assert pairs(html) == {("text", CONTENT, SOFT_ERROR)}

    def test_an_alert_with_no_colour_is_base_content_on_base_200(self):
        html = '<div role="alert" class="alert"><span>Stay</span></div>'

        assert pairs(html) == {("text", CONTENT, BASE_200)}

    def test_an_alert_with_a_developers_colour_yields_nothing(self):
        html = '<div role="alert" class="alert alert-warning"><span>Mind</span></div>'

        assert read(html) == []

    def test_the_dismiss_button_in_a_coloured_alert_is_read_on_the_alerts_fill(self):
        html = (
            '<div role="alert" class="alert alert-info"><span>Mind</span>'
            '<button type="button" class="btn btn-sm btn-ghost">x</button></div>'
        )

        found = of(html, "button text", CONTENT, Ink("info"))

        assert found.own
        assert len(read(html)) == 1

    def test_a_soft_alert_in_another_colour_has_no_row(self):
        html = '<div class="alert alert-info alert-soft"><span>x</span></div>'

        with pytest.raises(Uncovered) as raised:
            read(html)

        assert raised.value.class_name == "alert-soft"

    def test_an_alert_variant_with_no_row_raises(self):
        html = '<div class="alert alert-outline"><span>x</span></div>'

        with pytest.raises(Uncovered) as raised:
            read(html)

        assert raised.value.class_name == "alert-outline"


class TestReaderInputs:
    def test_an_input_yields_its_border_and_its_value(self):
        html = '<input type="text" class="input w-full" id="id_a">'

        assert pairs(html) == {
            ("border", CONTENT.faded(0.2), BASE_100),
            ("text", CONTENT, BASE_100),
        }

    def test_an_input_with_a_placeholder_yields_it(self):
        html = '<input type="text" class="input" placeholder="Name">'

        found = of(html, "placeholder", CONTENT.faded(0.5), BASE_100)

        assert found.held
        assert not found.own

    def test_a_colour_modifier_sets_the_border(self):
        html = '<input type="text" class="input input-primary">'

        assert ("border", Ink("primary"), BASE_100) in pairs(html)

    def test_the_error_modifier_sets_the_border(self):
        html = '<textarea class="textarea textarea-error"></textarea>'

        assert ("border", ERROR, BASE_100) in pairs(html)

    def test_a_ghost_input_has_no_border(self):
        html = '<input type="text" class="input input-ghost" placeholder="x">'

        assert {part for part, _, _ in pairs(html)} == {"text", "placeholder"}

    def test_a_ghost_input_keeps_the_surface_it_stands_on(self):
        html = '<div class="bg-base-200"><input class="input input-ghost"></div>'

        assert pairs(html) == {("text", CONTENT, BASE_200)}

    def test_a_textarea_yields_its_border_and_its_value(self):
        html = '<textarea class="textarea">Hello</textarea>'

        assert {part for part, _, _ in pairs(html)} == {"border", "text"}

    def test_a_select_yields_its_border_its_value_and_its_arrow(self):
        html = '<select class="select"><option>One</option></select>'

        assert pairs(html) == {
            ("border", CONTENT.faded(0.2), BASE_100),
            ("text", CONTENT, BASE_100),
            ("mark", CONTENT, BASE_100),
        }

    def test_a_file_input_yields_its_border_and_its_buttons_text(self):
        html = '<input type="file" class="file-input">'

        assert pairs(html) == {
            ("border", CONTENT.faded(0.2), BASE_100),
            ("button text", CONTENT, BASE_200),
        }

    def test_a_coloured_file_input_has_its_buttons_text_on_the_colour(self):
        html = '<input type="file" class="file-input file-input-primary">'

        assert ("button text", Ink("primary-content"), Ink("primary")) in pairs(html)

    def test_attached_text_sits_on_its_wrappers_fill(self):
        html = (
            '<div class="bg-base-200"><label class="input">'
            '<span class="label">$</span><input type="text"></label></div>'
        )

        found = of(html, "text", CONTENT.faded(0.6), BASE_100)

        assert found.own
        assert ("border", CONTENT.faded(0.2), BASE_200) in pairs(html)

    def test_an_input_inside_a_wrapper_yields_its_value_and_placeholder(self):
        html = '<label class="input"><input type="text" placeholder="x"></label>'

        assert {part for part, _, _ in pairs(html)} == {"border", "text", "placeholder"}

    def test_a_select_that_takes_many_choices_draws_no_arrow(self):
        html = '<select class="select" multiple><option>One</option></select>'

        assert {part for part, _, _ in pairs(html)} == {"border", "text"}

    def test_a_wrapped_select_yields_one_arrow_for_the_wrapper(self):
        html = '<label class="select"><select><option>a</option></select></label>'

        assert [m.pairing.part for m in read(html)].count("mark") == 1

    def test_an_input_with_no_daisyui_class_yields_value_and_placeholder_only(self):
        html = '<input type="search" placeholder="Find">'

        assert pairs(html) == {
            ("text", CONTENT, BASE_100),
            ("placeholder", CONTENT.faded(0.5), BASE_100),
        }

    def test_a_read_only_input_is_read_as_an_ordinary_one(self):
        ordinary = '<input type="text" class="input" value="Ada">'
        locked = '<input type="text" class="input" value="Ada" readonly>'

        assert pairs(locked) == pairs(ordinary)
        assert all(m.held for m in read(locked))


class TestReaderChoiceInputs:
    def test_a_checkbox_is_read_off_and_on(self):
        html = '<input type="checkbox" class="checkbox">'

        assert pairs(html) == {
            ("border", CONTENT.faded(0.2), BASE_100),
            ("mark", CONTENT, BASE_100),
        }

    def test_a_checkbox_is_read_both_ways_whatever_the_markup_says(self):
        assert pairs('<input type="checkbox" class="checkbox" checked>') == pairs(
            '<input type="checkbox" class="checkbox">'
        )

    def test_a_coloured_checkbox_has_its_border_fill_and_mark_in_the_colour(self):
        html = '<input type="checkbox" class="checkbox checkbox-primary">'

        assert pairs(html) == {
            ("border", Ink("primary"), BASE_100),
            ("mark", Ink("primary-content"), Ink("primary")),
        }

    def test_a_radio_draws_its_border_in_a_fifth_of_the_text_ink(self):
        html = '<label class="label text-base-content"><input class="radio"></label>'

        assert ("border", CONTENT.faded(0.2), BASE_100) in pairs(html)

    def test_a_radio_chosen_has_its_ring_and_dot_in_the_text_ink(self):
        html = '<label class="label text-base-content"><input class="radio"></label>'

        found = pairs(html)

        assert ("border", CONTENT, BASE_100) in found
        assert ("mark", CONTENT, BASE_100) in found

    def test_a_radio_in_a_label_takes_the_labels_sixty_percent(self):
        html = '<label class="label"><input type="radio" class="radio">A</label>'

        found = of(html, "mark", CONTENT.faded(0.6), BASE_100)

        assert found.own

    def test_a_radios_faded_border_is_not_the_packs_to_repair(self):
        html = '<label class="label"><input type="radio" class="radio">A</label>'

        assert not of(html, "border", CONTENT.faded(0.12), BASE_100).own

    def test_a_coloured_radio_is_drawn_in_the_colour(self):
        html = '<input type="radio" class="radio radio-error">'

        assert pairs(html) == {
            ("border", ERROR, BASE_100),
            ("mark", ERROR, BASE_100),
        }

    def test_a_toggle_off_has_a_border_at_half_the_content(self):
        found = pairs('<input type="checkbox" class="toggle" role="switch">')

        assert ("border", CONTENT.faded(0.5), BASE_100) in found

    def test_a_toggle_on_has_its_border_and_knob_in_the_content(self):
        found = pairs('<input type="checkbox" class="toggle">')

        assert ("border", CONTENT, BASE_100) in found
        assert ("mark", CONTENT, BASE_100) in found

    def test_a_coloured_toggle_on_is_drawn_in_the_colour_and_off_is_unchanged(self):
        found = pairs('<input type="checkbox" class="toggle toggle-success">')

        assert ("border", CONTENT.faded(0.5), BASE_100) in found
        assert ("border", Ink("success"), BASE_100) in found
        assert ("mark", Ink("success"), BASE_100) in found


STAR = '<input type="radio" class="mask mask-star-2{extra}"{attrs}>'


def rating(extra="", attrs="", wrapper="rating"):
    star = STAR.format(extra=extra, attrs=attrs)
    return (
        f'<div class="{wrapper}"><input type="radio" class="rating-hidden">{star}</div>'
    )


class TestReaderRatings:
    def test_a_star_is_read_lit_and_unlit(self):
        assert pairs(rating()) == {
            ("mark", CONTENT, BASE_100),
            ("border", CONTENT.faded(0.2), BASE_100),
        }

    def test_a_star_is_read_both_ways_whatever_the_markup_says(self):
        assert pairs(rating(attrs=" checked")) == pairs(rating())

    def test_a_coloured_star_is_drawn_in_the_colour(self):
        assert pairs(rating(" bg-success")) == {
            ("mark", Ink("success"), BASE_100),
            ("border", Ink("success").faded(0.2), BASE_100),
        }

    def test_the_error_colour_wins_over_the_chosen_one(self):
        assert pairs(rating(" bg-primary bg-error")) == {
            ("mark", ERROR, BASE_100),
            ("border", ERROR.faded(0.2), BASE_100),
        }

    def test_a_star_is_daisyuis_drawing_and_not_the_packs_to_repair(self):
        found = read(rating(" bg-accent"))

        assert found
        assert all(m.held and not m.own for m in found)

    def test_a_star_stands_on_the_surface_around_the_rating(self):
        html = f'<div class="bg-base-200">{rating()}</div>'

        assert pairs(html) == {
            ("mark", CONTENT, BASE_200),
            ("border", CONTENT.faded(0.2), BASE_200),
        }

    def test_the_clearing_choice_is_nothing_to_make_out(self):
        html = '<div class="rating"><input type="radio" class="rating-hidden"></div>'

        assert read(html) == []

    @pytest.mark.parametrize("size", ["xs", "sm", "md", "lg", "xl"])
    def test_a_size_paints_nothing(self, size):
        assert pairs(rating(wrapper=f"rating rating-{size}")) == pairs(rating())

    def test_a_disabled_rating_is_drawn_as_an_enabled_one_and_not_held(self):
        found = read(rating(attrs=" disabled"))

        assert {(m.pairing.part, m.pairing.ink) for m in found} == {
            ("mark", CONTENT),
            ("border", CONTENT.faded(0.2)),
        }
        assert not any(m.held for m in found)

    def test_a_measurement_names_the_rating_it_came_from(self):
        found = read(rating())[0]

        assert found.element.kind == "rating"

    def test_a_colour_the_reader_has_no_row_for_raises_uncovered(self):
        with pytest.raises(Uncovered):
            read(rating(" bg-pink"))


class TestReaderRanges:
    def test_a_range_is_its_ink_on_the_surface_and_a_tenth_of_it_for_the_track(self):
        assert pairs('<input type="range" class="range">') == {
            ("mark", CONTENT, BASE_100),
            ("border", CONTENT.faded(0.1), BASE_100),
        }

    def test_a_coloured_range_is_drawn_in_the_colour(self):
        assert pairs('<input type="range" class="range range-info">') == {
            ("mark", Ink("info"), BASE_100),
            ("border", Ink("info").faded(0.1), BASE_100),
        }

    def test_the_error_colour_wins_over_the_chosen_one(self):
        html = '<input type="range" class="range range-primary range-error">'

        assert ("mark", ERROR, BASE_100) in pairs(html)

    def test_a_range_with_no_colour_takes_the_text_ink_it_inherits(self):
        html = '<label class="label"><input type="range" class="range"></label>'

        found = of(html, "mark", CONTENT.faded(0.6), BASE_100)

        assert found.held
        assert found.own

    def test_the_empty_track_is_not_the_packs_to_repair(self):
        html = '<label class="label"><input type="range" class="range"></label>'

        assert not of(html, "border", CONTENT.faded(0.06), BASE_100).own

    def test_a_coloured_range_is_not_the_packs_to_repair(self):
        found = read('<input type="range" class="range range-accent">')

        assert not any(m.own for m in found)

    @pytest.mark.parametrize("size", ["xs", "sm", "md", "lg", "xl"])
    def test_a_size_paints_nothing(self, size):
        html = f'<input type="range" class="range range-{size}">'

        assert pairs(html) == pairs('<input type="range" class="range">')

    def test_a_disabled_range_is_dimmed_to_thirty_percent_and_not_held(self):
        found = read('<input type="range" class="range" disabled>')

        assert {(m.pairing.part, m.pairing.ink) for m in found} == {
            ("mark", CONTENT.faded(0.3)),
            ("border", CONTENT.faded(0.1).faded(0.3)),
        }
        assert not any(m.held for m in found)

    def test_a_measurement_names_the_range_it_came_from(self):
        found = read('<input type="range" class="range" id="id_volume">')[0]

        assert found.element.kind == "range"


class TestReaderButtons:
    def test_a_button_with_no_colour_is_base_content_on_base_200(self):
        found = of('<button class="btn">Go</button>', "button text", CONTENT, BASE_200)

        assert found.held
        assert not found.own

    def test_a_coloured_button_is_the_colours_content_on_the_colour(self):
        html = '<input type="submit" class="btn btn-primary" value="Go">'

        assert pairs(html) == {("button text", Ink("primary-content"), Ink("primary"))}

    def test_a_link_drawn_as_a_button_is_read(self):
        assert len(read('<a class="btn" href="/">Go</a>')) == 1

    @pytest.mark.parametrize("variant", ["outline", "dash", "ghost"])
    def test_a_button_with_no_fill_has_the_colour_as_text_on_the_surface(self, variant):
        html = f'<button class="btn btn-primary btn-{variant}">Go</button>'

        assert pairs(html) == {("button text", Ink("primary"), BASE_100)}

    @pytest.mark.parametrize("variant", ["outline", "dash", "ghost"])
    def test_a_button_with_no_fill_and_no_colour_has_base_content(self, variant):
        html = f'<button class="btn btn-{variant}">Go</button>'

        assert pairs(html) == {("button text", CONTENT, BASE_100)}

    def test_a_soft_button_has_the_colour_on_an_eighth_of_it_in_base_100(self):
        html = '<button class="btn btn-error btn-soft">Go</button>'

        assert pairs(html) == {("button text", ERROR, ERROR.mixed(BASE_100, 0.08))}

    def test_a_soft_neutral_button_has_a_fill_that_is_eighty_eight_percent_opaque(self):
        html = '<button class="btn btn-neutral btn-soft">Go</button>'

        neutral = Ink("neutral")
        fill = neutral.mixed(Ink("neutral-content"), 1 / 11).faded(0.88).over(BASE_100)

        assert pairs(html) == {("button text", neutral, fill)}

    def test_a_soft_button_with_no_colour_mixes_base_content_into_base_100(self):
        html = '<button class="btn btn-soft">Go</button>'

        assert pairs(html) == {("button text", CONTENT, CONTENT.mixed(BASE_100, 0.08))}

    def test_a_link_button_with_no_colour_is_primary(self):
        html = '<button class="btn btn-link">Go</button>'

        assert pairs(html) == {("button text", Ink("primary"), BASE_100)}

    def test_a_link_button_with_a_colour_is_that_colour(self):
        html = '<button class="btn btn-link btn-accent">Go</button>'

        assert pairs(html) == {("button text", Ink("accent"), BASE_100)}

    def test_a_button_in_a_group_stands_on_the_groups_surface(self):
        html = '<div class="bg-base-200"><button class="btn btn-ghost">x</button></div>'

        assert pairs(html) == {("button text", CONTENT, BASE_200)}


class TestReaderTabsAndGroups:
    TABS = (
        '<div class="tabs tabs-border"><input type="radio" class="tab"'
        ' aria-label="One" checked><input type="radio" class="tab" aria-label="Two">'
        "</div>"
    )

    def test_a_tab_is_read_chosen_and_not_chosen_with_its_bar(self):
        found = pairs(self.TABS)

        assert found == {
            ("text", CONTENT, BASE_100),
            ("text", CONTENT.faded(0.5), BASE_100),
            ("mark", CONTENT, BASE_100),
        }

    def test_a_tab_is_always_the_packs_own(self):
        assert all(m.own for m in read(self.TABS))

    def test_a_tab_with_text_base_content_is_base_content_chosen_or_not(self):
        html = self.TABS.replace('class="tab"', 'class="tab text-base-content"')

        assert {ink for part, ink, _ in pairs(html) if part == "text"} == {CONTENT}

    def test_an_accordion_group_yields_its_arrow_on_its_surface(self):
        html = (
            '<details class="collapse collapse-arrow bg-base-200">'
            '<summary class="collapse-title">One</summary></details>'
        )

        assert pairs(html) == {
            ("text", CONTENT, BASE_200),
            ("mark", CONTENT, BASE_200),
        }


class TestReaderDisabled:
    def test_a_disabled_input_is_dimmed_and_not_held(self):
        html = '<input type="text" class="input" disabled placeholder="x">'

        found = read(html)

        assert {m.pairing.part for m in found} == {"border", "text", "placeholder"}
        assert not any(m.held for m in found)

    def test_a_disabled_inputs_text_is_forty_percent_on_base_200(self):
        html = '<input type="text" class="input" disabled>'

        assert ("text", CONTENT.faded(0.4), BASE_200) in pairs(html)

    def test_a_disabled_ghost_input_is_filled_and_bordered_in_base_200(self):
        html = '<input type="text" class="input input-ghost" disabled>'

        found = read(html)

        assert {(m.pairing.part, m.pairing.ink, m.pairing.surface) for m in found} == {
            ("border", BASE_200, BASE_100),
            ("text", CONTENT.faded(0.4), BASE_200),
        }
        assert not any(m.held for m in found)

    def test_a_disabled_checkbox_is_dimmed_and_not_held(self):
        found = read('<input type="checkbox" class="checkbox" disabled>')

        assert found
        assert not any(m.held for m in found)

    def test_a_disabled_toggle_is_dimmed_and_not_held(self):
        found = read('<input type="checkbox" class="toggle" disabled>')

        assert found
        assert not any(m.held for m in found)

    def test_a_disabled_radio_is_dimmed_and_not_held(self):
        found = read('<input type="radio" class="radio" disabled>')

        assert found
        assert not any(m.held for m in found)

    def test_a_disabled_file_input_is_dimmed_and_not_held(self):
        found = read('<input type="file" class="file-input" disabled>')

        assert found
        assert not any(m.held for m in found)

    def test_a_disabled_button_is_dimmed_and_not_held(self):
        found = read('<button class="btn btn-primary" disabled>Go</button>')

        assert [m.pairing.part for m in found] == ["button text"]
        assert not found[0].held

    def test_a_disabled_wrapped_input_makes_the_wrapper_dimmed_too(self):
        html = (
            '<label class="input"><span class="label">$</span><input disabled></label>'
        )

        found = read(html)
        border = [m for m in found if m.pairing.part == "border"]

        assert border
        assert not border[0].held

    def test_the_label_of_a_disabled_input_is_still_held(self):
        html = (
            '<label class="fieldset-legend">Name</label>'
            '<input type="text" class="input" disabled>'
            '<p class="label">Help</p>'
        )

        held = {m.pairing.ink for m in read(html) if m.held}

        assert held == {CONTENT, CONTENT.faded(0.6)}


class TestReaderOwn:
    @pytest.mark.parametrize(
        "html",
        [
            '<p class="label">x</p>',
            '<table class="table"><thead><tr><th>x</th></tr></thead></table>',
            '<input type="radio" class="tab" aria-label="x">',
            '<div class="alert alert-error alert-soft"><p>x</p></div>',
        ],
    )
    def test_text_the_pack_colours_is_its_own(self, html):
        assert any(m.own for m in read(html))

    @pytest.mark.parametrize(
        "html",
        [
            '<input class="input" placeholder="x">',
            '<input type="checkbox" class="checkbox checkbox-error">',
            '<button class="btn btn-ghost">x</button>',
            "<p>x</p>",
        ],
    )
    def test_a_controls_drawing_and_plain_text_are_not(self, html):
        assert not any(m.own for m in read(html))

    def test_a_measurement_names_the_element_it_came_from(self):
        found = read('<input type="text" class="input input-error" id="id_a">')[0]

        assert found.element.tag == "input"
        assert found.element.id == "id_a"
        assert found.element.kind == "input"
        assert found.form_state == "fragment"
