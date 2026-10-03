"""A number field drawn as a range, through crispy-forms."""

import pytest
from crispy_forms.bootstrap import PrependedText
from django.http import QueryDict

from mvp_forms.choices import Choice, FormChoices, InvalidChoice
from tests.forms import (
    DevelopersRangeForm,
    KeptRangesForm,
    OwnNumberRangeForm,
    RangedLineFormSet,
    RangesForm,
    RefusedRangesForm,
    formset_helper,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
TAG = "{% crispy form %}"
TABLE = "daisyui/table_inline_formset.html"


def stating(*names):
    return FormChoices(fields={name: Choice(drawing="range") for name in names})


def input_of(soup, name):
    return soup.find("input", id=f"id_{name}")


def submitted(soup, **slid):
    """Return the data a person sends after setting each slider to a value."""
    data = QueryDict(mutable=True)
    for name, value in slid.items():
        data[input_of(soup, name)["name"]] = str(value)
    return data


def codes_of(form):
    return {
        name: [error.code for error in errors]
        for name, errors in form.errors.as_data().items()
    }


def refused(draw, source, form):
    with pytest.raises(InvalidChoice) as caught:
        draw(source, form=form)
    return caught.value


class TestRange:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_with_no_drawing_stated_is_the_number_input_it_was(
        self, draw, source
    ):
        soup = draw(source, form=RangesForm())

        tag = input_of(soup, "volume")

        assert tag["type"] == "number"
        assert "range" not in tag["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_range_is_one_input_of_type_range_with_the_fields_name(
        self, draw, source
    ):
        soup = draw(source, form=RangesForm(choices=stating("volume")))

        tags = soup.find_all("input", id="id_volume")

        assert len(tags) == 1
        assert tags[0]["type"] == "range"
        assert tags[0]["name"] == "volume"
        assert "range" in tags[0]["class"]

    def test_a_range_stated_in_a_layout_is_drawn_for_that_field_only(self, draw):
        form = RangesForm(layout=[Choice("volume", drawing="range"), "ratio"])

        soup = draw(TAG, form=form)

        assert input_of(soup, "volume")["type"] == "range"
        assert input_of(soup, "ratio")["type"] == "number"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_float_a_decimal_and_a_subclass_of_number_input_are_drawn_too(
        self, draw, source
    ):
        soup = draw(source, form=RangesForm(choices=stating("ratio", "price")))
        own = draw(source, form=OwnNumberRangeForm(choices=stating("volume")))

        assert input_of(soup, "ratio")["type"] == "range"
        assert input_of(soup, "price")["type"] == "range"
        assert input_of(own, "volume")["type"] == "range"

    @pytest.mark.parametrize("source", SOURCES)
    def test_min_max_and_step_are_the_ones_the_field_declares(self, draw, source):
        soup = draw(source, form=RangesForm(choices=stating("volume", "ratio")))

        volume = input_of(soup, "volume")
        ratio = input_of(soup, "ratio")

        assert (volume["min"], volume["max"], volume["step"]) == ("0", "100", "5")
        assert (ratio["min"], ratio["max"]) == ("0", "1")
        assert ratio["step"] == "any"

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_integer_field_that_declares_no_limit_has_none_written(
        self, draw, source
    ):
        soup = draw(source, form=RangesForm(choices=stating("bare")))

        tag = input_of(soup, "bare")

        assert not any(tag.has_attr(name) for name in ("min", "max", "step"))

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("value", [35, 500])
    def test_a_slid_value_cleans_as_it_does_in_the_ordinary_drawing(
        self, draw, source, value
    ):
        plain = draw(source, form=RangesForm())
        ranged = draw(source, form=RangesForm(choices=stating("volume")))

        before = RangesForm(submitted(plain, volume=value))
        after = RangesForm(submitted(ranged, volume=value))

        assert after.is_valid() is before.is_valid()
        assert after.cleaned_data == before.cleaned_data
        assert codes_of(after) == codes_of(before)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_bound_value_is_the_inputs_value(self, draw, source):
        form = RangesForm({"volume": "35"}, choices=stating("volume"))

        soup = draw(source, form=form)

        assert input_of(soup, "volume")["value"] == "35"

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_initial_value_is_the_inputs_value(self, draw, source):
        form = RangesForm(initial={"volume": 60}, choices=stating("volume"))

        soup = draw(source, form=form)

        assert input_of(soup, "volume")["value"] == "60"

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_labels_for_is_the_inputs_id(self, draw, source):
        soup = draw(source, form=RangesForm(choices=stating("volume")))

        tag = input_of(soup, "volume")

        assert soup.find("label", attrs={"for": tag["id"]}) is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_no_script_is_drawn(self, draw, source):
        soup = draw(source, form=RangesForm(choices=stating("volume", "ratio")))

        assert soup.find("script") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_form_drawn_twice_gives_the_same_markup(self, draw, source):
        form = DevelopersRangeForm({"volume": "3"}, choices=stating("volume"))

        first = draw(source, form=form)
        second = draw(source, form=form)

        assert str(first) == str(second)

    def test_the_forms_own_widget_is_still_a_number_input_after_a_draw(self, draw):
        form = RangesForm(choices=stating("volume"))
        own = form.fields["volume"].widget

        draw(TAG, form=form)
        draw("{{ form|crispy }}", form=form)

        assert form.fields["volume"].widget is own
        assert own.input_type == "number"


class TestRangeKeepsWhatANumberInputHas:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_input_is_described_by_the_help_text(self, draw, source):
        form = KeptRangesForm(choices=stating("volume"))

        soup = draw(source, form=form)

        tag = input_of(soup, "volume")
        assert tag["aria-describedby"].split() == ["id_volume_helptext"]
        assert len(soup.find_all(id="id_volume_helptext")) == 1

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_in_error_is_invalid_described_by_its_error_and_carries_range_error(
        self, draw, source
    ):
        form = KeptRangesForm({"volume": "500"}, choices=stating("volume"))

        soup = draw(source, form=form)

        tag = input_of(soup, "volume")
        assert tag["aria-invalid"] == "true"
        assert "range-error" in tag["class"]
        assert set(tag["aria-describedby"].split()) == {
            "id_volume_helptext",
            "id_volume_error",
        }
        assert soup.find(id="id_volume_error") is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_that_is_not_in_error_carries_no_error_modifier(self, draw, source):
        form = KeptRangesForm({"volume": "50"}, choices=stating("volume"))

        tag = input_of(draw(source, form=form), "volume")

        assert "range-error" not in tag["class"]
        assert not tag.has_attr("aria-invalid")

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_required_marker_is_in_the_label_of_a_required_field_only(
        self, draw, source
    ):
        form = KeptRangesForm(choices=stating("volume", "ratio"))

        soup = draw(source, form=form)

        required = soup.find("label", attrs={"for": "id_volume"})
        optional = soup.find("label", attrs={"for": "id_ratio"})
        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_field_is_disabled(self, draw, source):
        form = KeptRangesForm(choices=stating("locked", "ratio"))

        soup = draw(source, form=form)

        assert input_of(soup, "locked").has_attr("disabled")
        assert not input_of(soup, "ratio").has_attr("disabled")

    def test_with_labels_off_the_input_is_named_by_aria_label(self, draw):
        form = RangesForm(choices=stating("volume"), show_labels=False)

        soup = draw(TAG, form=form)

        frame = soup.find(id="div_id_volume")
        assert frame.find("label") is None
        assert input_of(soup, "volume")["aria-label"] == form["volume"].label

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_attributes_and_classes_are_kept(self, draw, source):
        form = DevelopersRangeForm(choices=stating("volume"))

        tag = input_of(draw(source, form=form), "volume")

        assert "mine" in tag["class"]
        assert "range" in tag["class"]
        assert tag["data-own"] == "yes"
        assert tag["max"] == "100"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_width_the_developer_set_leaves_the_packs_width_out(self, draw, source):
        form = DevelopersRangeForm(choices=stating("volume", "wide"))

        soup = draw(source, form=form)

        assert "w-full" in input_of(soup, "volume")["class"]
        assert "w-full" not in input_of(soup, "wide")["class"]
        assert "w-24" in input_of(soup, "wide")["class"]


class TestRangeAmongOtherFields:
    @pytest.mark.parametrize("source", SOURCES)
    def test_only_the_field_stated_changes(self, draw, source):
        soup = draw(source, form=RangesForm(choices=stating("volume")))

        assert [tag["id"] for tag in soup.find_all("input", type="range")] == [
            "id_volume"
        ]
        assert input_of(soup, "ratio")["type"] == "number"
        assert input_of(soup, "title")["type"] == "text"

    @pytest.mark.parametrize("template", [None, TABLE], ids=["stacked", "table"])
    def test_every_form_of_a_formset_draws_the_range_with_an_id_of_its_own(
        self, draw, template
    ):
        settings = {} if template is None else {"template": template}
        helper = formset_helper(**settings)
        helper.daisyui = stating("level")

        soup = draw(
            "{% crispy formset helper %}",
            formset=RangedLineFormSet(),
            helper=helper,
        )

        ids = [tag["id"] for tag in soup.find_all(id=True)]
        for row in range(3):
            assert input_of(soup, f"form-{row}-level")["type"] == "range"
        assert len(ids) == len(set(ids))

    def test_text_attached_to_a_range_is_not_drawn_and_the_range_is(self, draw):
        form = RangesForm(
            layout=[Choice(PrependedText("volume", "$"), drawing="range")]
        )

        soup = draw(TAG, form=form)

        assert input_of(soup, "volume")["type"] == "range"
        assert "$" not in soup.get_text()


class TestRangeMistakes:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("name", "allowed"),
        [
            ("title", ()),
            ("many", ()),
            ("pick", ("rating",)),
            ("flag", ("checkbox", "toggle", "switch")),
            ("local_count", ()),
            ("local_price", ()),
        ],
    )
    def test_a_range_stated_for_another_kind_of_field_is_refused(
        self, draw, source, name, allowed
    ):
        error = refused(draw, source, RefusedRangesForm(choices=stating(name)))

        assert (error.kind, error.value, error.target) == ("drawing", "range", name)
        assert error.allowed == allowed

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", ["checkbox", "toggle", "switch", "rating"])
    def test_another_drawing_stated_for_a_number_field_is_refused_with_range_allowed(
        self, draw, source, drawing
    ):
        choices = FormChoices(fields={"volume": Choice(drawing=drawing)})

        error = refused(draw, source, RangesForm(choices=choices))

        assert (error.kind, error.value, error.target) == ("drawing", drawing, "volume")
        assert error.allowed == ("range",)

    def test_a_range_stated_in_a_layout_for_a_text_field_is_refused(self, draw):
        form = RangesForm(layout=[Choice("title", drawing="range")])

        error = refused(draw, TAG, form)

        assert (error.kind, error.target) == ("drawing", "title")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_hidden_field_raises_nothing_and_is_a_hidden_input(self, draw, source):
        soup = draw(source, form=RefusedRangesForm(choices=stating("secret")))

        tag = soup.find("input", attrs={"name": "secret"})

        assert tag["type"] == "hidden"
