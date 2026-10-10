"""A partial date field, drawn as the pack draws a text input and through each renderer."""

import json

import pytest
from django.forms import formset_factory

from mvp_forms.choices import FormChoices
from mvp_forms.widgets import PartialDateInput, PartialDateMaskInput, PartialDateSelect
from tests.forms import (
    PartialDateForm,
    PartialDateLineFormSet,
    PartialDateMaskForm,
    PartialDateMaskLineFormSet,
    PartialDatePartsForm,
    PartialDatePartsLineFormSet,
    PartialDateSelectLineFormSet,
    PartialDateSelectPartsForm,
    partial_date_form,
)

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.born|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]


class TestPartialDateField:
    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_daisyui_text_input(self, draw, source):
        soup = draw(source, form=PartialDateForm())

        drawn = soup.find(id="id_born")

        assert drawn.name == "input"
        assert drawn["type"] == "text"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_pack_gives_the_text_input_its_class(self, draw, source):
        soup = draw(source, form=PartialDateForm())

        assert "input" in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "input-lg"),
            ("color", "primary", "input-primary"),
            ("variant", "ghost", "input-ghost"),
        ],
    )
    def test_it_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = PartialDateForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_is_drawn_as_a_text_input(self, draw, source):
        soup = draw(source, form=PartialDateLineFormSet().empty_form)

        assert (
            soup.find("input", attrs={"name": "form-__prefix__-born"})["type"] == "text"
        )

    def test_the_form_names_no_script(self):
        assert "<script" not in str(PartialDateForm().media)


class TestPartialDateMaskInput:
    @pytest.mark.parametrize("source", SOURCES)
    def test_it_is_drawn_as_a_text_input_carrying_its_options(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        drawn = soup.find(id="id_born")

        assert drawn.name == "input"
        assert drawn["type"] == "text"
        assert json.loads(drawn["data-imask"]) == {
            "kind": "partial-date",
            "resolution": "day",
        }

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_attrs_and_the_numeric_keypad_are_drawn(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        drawn = soup.find(id="id_born")

        assert drawn["placeholder"] == "Born"
        assert drawn["inputmode"] == "numeric"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_pack_gives_the_text_input_its_class(self, draw, source):
        soup = draw(source, form=PartialDateMaskForm())

        assert "input" in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "input-lg"),
            ("color", "primary", "input-primary"),
            ("variant", "ghost", "input-ghost"),
        ],
    )
    def test_it_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = PartialDateMaskForm()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        assert added in soup.find(id="id_born")["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_carries_the_same_options(self, draw, source):
        formset = PartialDateMaskLineFormSet()

        row = draw(source, form=formset.forms[0])
        template = draw(source, form=formset.empty_form)

        assert (
            template.find("input", attrs={"data-imask": True})["data-imask"]
            == row.find("input", attrs={"data-imask": True})["data-imask"]
        )

    def test_the_forms_media_names_the_script(self):
        assert "mvp_forms/imask.js" in str(PartialDateMaskForm().media)


SENT = {"born_year": "2021", "born_month": "02", "born_day": "30"}


class ThreePartDateDrawn:
    """How the pack draws a three-part date, run once for each widget."""

    form = None
    line_formset = None
    year_tag = None

    def part(self, soup, name):
        return soup.find(attrs={"data-partial-date-part": name})

    def shown(self, soup, name):
        part = self.part(soup, name)
        if part.name == "input":
            return part.get("value") or None
        option = part.find("option", selected=True)
        return (option["value"] or None) if option else None

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_is_one_fieldset_whose_legend_is_the_label(self, draw, source):
        soup = draw(source, form=self.form())

        frame = soup.find(id="div_id_born")

        assert frame.name == "fieldset"
        assert len(frame.find_all("legend")) == 1

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_it_has_one_help_text_and_one_set_of_errors(self, draw, source):
        soup = draw(source, form=self.form({"born_year": "", "born_month": "3"}))

        frame = soup.find(id="div_id_born")

        assert len(frame.find_all(id="id_born_helptext")) == 1
        assert len(frame.find_all(id="id_born_error")) == 1

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_parts_are_inside_one_element_that_marks_the_group(self, draw, source):
        soup = draw(source, form=self.form())

        groups = soup.find_all(attrs={"data-partial-date": True})

        assert len(groups) == 1
        parts = groups[0].find_all(attrs={"data-partial-date-part": True})
        assert [part["data-partial-date-part"] for part in parts] == [
            "year",
            "month",
            "day",
        ]
        names = [part["aria-label"] for part in parts]
        assert all(names)
        assert len(set(names)) == len(names)

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_only_the_year_is_required(self, draw, source):
        soup = draw(source, form=self.form())

        assert self.part(soup, "year").has_attr("required")
        assert not self.part(soup, "month").has_attr("required")
        assert not self.part(soup, "day").has_attr("required")

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("kind", "value", "added"),
        [
            ("size", "lg", "lg"),
            ("color", "primary", "primary"),
            ("variant", "ghost", "ghost"),
        ],
    )
    def test_each_part_takes_the_size_colour_and_variant_stated_for_the_form(
        self, draw, source, kind, value, added
    ):
        form = self.form()
        form.helper.daisyui = FormChoices(**{kind: value})

        soup = draw(source, form=form)

        for name in ("year", "month", "day"):
            part = self.part(soup, name)
            assert f"{part.name}-{added}" in part["class"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            (SENT, ("2021", "02", "30")),
            ({**SENT, "born_month": ""}, ("2021", None, "30")),
        ],
        ids=["30th of February", "day with no month"],
    )
    def test_a_refused_submission_is_drawn_as_it_was_sent(
        self, draw, source, sent, expected
    ):
        form = self.form(sent)

        soup = draw(source, form=form)

        assert not form.is_valid()
        assert (
            tuple(self.shown(soup, name) for name in ("year", "month", "day"))
            == expected
        )

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_draws_the_three_parts(self, draw, source):
        soup = draw(source, form=self.line_formset().empty_form)

        names = [
            tag["name"] for tag in soup.find_all(attrs={"data-partial-date-part": True})
        ]

        assert names == [
            "form-__prefix__-born_year",
            "form-__prefix__-born_month",
            "form-__prefix__-born_day",
        ]

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_parts_drawn_by_any_renderer_submit_what_they_were_given(
        self, draw, posted, source
    ):
        soup = draw(source, form=self.form(initial={"born": "2021-03-14"}))

        sent = posted(soup)
        form = self.form(sent)

        assert [
            tag.name for tag in soup.find_all(attrs={"data-partial-date-part": True})
        ] == [
            self.year_tag,
            "select",
            "select",
        ]
        assert form.is_valid()
        assert form.cleaned_data["born"] == "2021-03-14"

    def test_the_forms_media_names_the_script(self):
        assert "mvp_forms/partial-date.js" in str(self.form().media)


class TestPartialDateInput(ThreePartDateDrawn):
    form = PartialDatePartsForm
    line_formset = PartialDatePartsLineFormSet
    year_tag = "input"


class TestPartialDateSelect(ThreePartDateDrawn):
    form = PartialDateSelectPartsForm
    line_formset = PartialDateSelectLineFormSet
    year_tag = "select"


class TestResolution:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_masked_input_is_drawn_with_the_resolution_of_the_field(
        self, draw, source
    ):
        form = partial_date_form(
            max_resolution="month", widget=PartialDateMaskInput()
        )()

        soup = draw(source, form=form)

        assert (
            json.loads(soup.find(id="id_born")["data-imask"])["resolution"] == "month"
        )

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("widget", [PartialDateInput, PartialDateSelect])
    def test_the_three_part_widgets_are_drawn_without_the_day_at_a_resolution_of_month(
        self, draw, source, widget
    ):
        form = partial_date_form(max_resolution="month", widget=widget())()

        soup = draw(source, form=form)

        parts = soup.find_all(attrs={"data-partial-date-part": True})
        assert [part["data-partial-date-part"] for part in parts] == ["year", "month"]

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize("widget", [PartialDateInput, PartialDateSelect])
    def test_the_empty_form_of_a_formset_is_drawn_to_the_resolution_too(
        self, draw, source, widget
    ):
        formset = formset_factory(
            partial_date_form(max_resolution="year", widget=widget()), extra=1
        )

        soup = draw(source, form=formset().empty_form)

        parts = soup.find_all(attrs={"data-partial-date-part": True})
        assert [part["name"] for part in parts] == ["form-__prefix__-born_year"]


class TestLimits:
    LIMITS = {"min_value": "1998-03-15", "max_value": "2004-09"}

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_masked_input_is_drawn_with_the_limits_of_the_field(self, draw, source):
        form = partial_date_form(widget=PartialDateMaskInput(), **self.LIMITS)()

        soup = draw(source, form=form)

        assert json.loads(soup.find(id="id_born")["data-imask"]) == {
            "kind": "partial-date",
            "resolution": "day",
            "min": "1998-03-15",
            "max": "2004-09",
        }

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("widget", [PartialDateInput, PartialDateSelect])
    def test_the_group_of_parts_is_drawn_with_the_limits_of_the_field(
        self, draw, source, widget
    ):
        form = partial_date_form(widget=widget(), **self.LIMITS)()

        soup = draw(source, form=form)

        group = soup.find(attrs={"data-partial-date": True})
        assert group["data-partial-date-min"] == "1998-03-15"
        assert group["data-partial-date-max"] == "2004-09"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_empty_form_of_a_formset_is_drawn_with_the_limits_too(
        self, draw, source
    ):
        masked = formset_factory(
            partial_date_form(widget=PartialDateMaskInput(), **self.LIMITS), extra=1
        )
        parts = formset_factory(
            partial_date_form(widget=PartialDateInput(), **self.LIMITS), extra=1
        )

        masked_soup = draw(source, form=masked().empty_form)
        parts_soup = draw(source, form=parts().empty_form)

        written = masked_soup.find(attrs={"data-imask": True})["data-imask"]
        group = parts_soup.find(attrs={"data-partial-date": True})
        assert json.loads(written)["min"] == "1998-03-15"
        assert group["data-partial-date-max"] == "2004-09"

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_a_masked_input_refused_for_a_date_outside_the_limits_shows_what_was_sent(
        self, draw, source
    ):
        form = partial_date_form(widget=PartialDateMaskInput(), **self.LIMITS)(
            {"born": "1997-03-14"}
        )

        soup = draw(source, form=form)

        assert form.has_error("born", code="min_value")
        assert soup.find(id="id_born")["value"] == "1997-03-14"
        assert len(soup.find(id="div_id_born").find_all(id="id_born_error")) == 1

    @pytest.mark.parametrize("source", FORM_WIDE)
    @pytest.mark.parametrize("widget", [PartialDateInput, PartialDateSelect])
    def test_a_group_of_parts_refused_for_a_date_outside_the_limits_shows_what_was_sent(
        self, draw, source, widget
    ):
        form = partial_date_form(widget=widget(), **self.LIMITS)(
            {"born_year": "2005", "born_month": "02", "born_day": "11"}
        )

        soup = draw(source, form=form)

        shown = []
        for name in ("year", "month", "day"):
            part = soup.find(attrs={"data-partial-date-part": name})
            if part.name == "input":
                shown.append(part["value"])
            else:
                shown.append(part.find("option", selected=True)["value"])
        assert form.has_error("born", code="max_value")
        assert shown == ["2005", "02", "11"]
