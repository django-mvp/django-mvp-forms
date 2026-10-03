"""A single-choice field drawn as a rating, through crispy-forms."""

import pytest
from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    InlineRadios,
    PrependedText,
    Tab,
    TabHolder,
)
from crispy_forms.layout import Column, Fieldset, Row
from django.contrib.auth.models import Group
from django.http import QueryDict

from mvp_forms.choices import Choice, FormChoices, InvalidChoice
from tests.forms import (
    STAR_CHOICES,
    DevelopersRatingForm,
    EdgeChoicesForm,
    KeptRatingsForm,
    ModelRatingForm,
    OwnTemplateRatingsForm,
    RadioRatingsForm,
    RatedLineFormSet,
    RatingsForm,
    RefusedRatingsForm,
    formset_helper,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
TAG = "{% crispy form %}"
TABLE = "daisyui/table_inline_formset.html"
SIZES = ("xs", "sm", "md", "lg", "xl")
COLORS = (
    "neutral",
    "primary",
    "secondary",
    "accent",
    "info",
    "success",
    "warning",
    "error",
)
VALUES = [choice[0] for choice in STAR_CHOICES]
LABELS = [choice[1] for choice in STAR_CHOICES]


def stating(*names):
    return FormChoices(fields={name: Choice(drawing="rating") for name in names})


def inputs_of(soup, name):
    return soup.find(id=f"id_{name}").find_all("input")


def stars_of(soup, name):
    return [tag for tag in inputs_of(soup, name) if "rating-hidden" not in tag["class"]]


def picked_from(soup, name, position):
    """Return the value of the drawn input, or option, at a position."""
    wrapper = soup.find(id=f"id_{name}")
    if wrapper.name == "select":
        return wrapper.find_all("option")[position]["value"]
    return wrapper.find_all("input")[position]["value"]


def submitted(soup, **picks):
    data = QueryDict(mutable=True)
    for name, position in picks.items():
        data[name] = picked_from(soup, name, position)
    return data


def refused(draw, source, form):
    with pytest.raises(InvalidChoice) as caught:
        draw(source, form=form)
    return caught.value


def wrapper_classes(soup, name):
    return set(soup.find(id=f"id_{name}")["class"])


def star_classes(soup, name):
    return [set(tag["class"]) for tag in stars_of(soup, name)]


def clearing_classes(soup, name):
    return [
        set(tag["class"])
        for tag in inputs_of(soup, name)
        if "rating-hidden" in tag["class"]
    ]


def signature(tags):
    return [
        (tag["type"], tag["value"], tag.has_attr("checked"), tag.get("aria-label"))
        for tag in tags
    ]


class TestRating:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_with_no_drawing_stated_is_the_select_or_radio_group_it_was(
        self, draw, source
    ):
        soup = draw(source, form=RatingsForm())

        assert soup.find("select", id="id_score") is not None
        assert soup.find(class_="rating") is None
        assert [tag["type"] for tag in inputs_of(soup, "kind")] == ["radio"] * 5

    @pytest.mark.parametrize("form_class", [RatingsForm, RadioRatingsForm])
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_rating_is_one_radio_input_for_each_choice_in_order(
        self, draw, source, form_class
    ):
        soup = draw(source, form=form_class(choices=stating("score")))

        wrapper = soup.find(id="id_score")
        stars = wrapper.find_all("input")

        assert "rating" in wrapper["class"]
        assert [tag["type"] for tag in stars] == ["radio"] * 5
        assert [tag["value"] for tag in stars] == VALUES
        assert {tag["name"] for tag in stars} == {"score"}
        assert wrapper.find("label") is None
        assert soup.find("select", id="id_score") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_choice_whose_value_is_zero_is_drawn_as_a_star(self, draw, source):
        soup = draw(source, form=EdgeChoicesForm(choices=stating("zero_first")))

        stars = stars_of(soup, "zero_first")

        assert [tag["value"] for tag in stars] == ["0", "1", "2"]
        assert all("mask" in tag["class"] for tag in stars)

    @pytest.mark.parametrize("form_class", [RatingsForm, RadioRatingsForm])
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_star_picked_cleans_as_it_does_in_the_ordinary_drawing(
        self, draw, source, form_class
    ):
        plain = draw(source, form=form_class())
        rated = draw(source, form=form_class(choices=stating("score")))

        before = form_class(submitted(plain, score=2))
        after = form_class(submitted(rated, score=2))

        assert before.is_valid()
        assert after.is_valid()
        assert after.cleaned_data == before.cleaned_data

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_bound_value_is_drawn_as_the_star_picked(self, draw, source):
        form = RatingsForm({"score": "4"}, choices=stating("score"))

        soup = draw(source, form=form)

        assert [tag.has_attr("checked") for tag in inputs_of(soup, "score")] == [
            False,
            False,
            False,
            True,
            False,
        ]

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_initial_value_is_drawn_as_the_star_picked(self, draw, source):
        form = RatingsForm(initial={"score": "2"}, choices=stating("score"))

        soup = draw(source, form=form)

        assert [
            tag["value"] for tag in inputs_of(soup, "score") if tag.has_attr("checked")
        ] == ["2"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_rating_with_no_value_has_no_star_picked(self, draw, source):
        form = RatingsForm(choices=stating("score", "again"))

        soup = draw(source, form=form)

        assert not any(tag.has_attr("checked") for tag in stars_of(soup, "score"))
        assert not any(tag.has_attr("checked") for tag in stars_of(soup, "again"))

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_empty_choice_is_the_one_input_that_clears_and_is_not_a_star(
        self, draw, source
    ):
        soup = draw(source, form=RatingsForm(choices=stating("again")))

        everything = inputs_of(soup, "again")
        clearing = [tag for tag in everything if tag["value"] == ""]

        assert len(clearing) == 1
        assert "rating-hidden" in clearing[0]["class"]
        assert "mask" not in clearing[0]["class"]
        assert len(stars_of(soup, "again")) == 3

    @pytest.mark.parametrize("source", SOURCES)
    def test_clearing_the_rating_cleans_to_the_fields_empty_value(self, draw, source):
        plain = draw(source, form=RatingsForm())
        rated = draw(source, form=RatingsForm(choices=stating("again")))

        before = RatingsForm(submitted(plain, score=0, again=0))
        after = RatingsForm(submitted(rated, score=0, again=0))

        assert before.is_valid()
        assert after.is_valid()
        assert after.cleaned_data["again"] is None
        assert after.cleaned_data == before.cleaned_data

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_empty_choice_listed_last_is_drawn_before_every_star(self, draw, source):
        soup = draw(source, form=EdgeChoicesForm(choices=stating("empty_last")))

        everything = inputs_of(soup, "empty_last")

        assert [tag["value"] for tag in everything] == ["", *VALUES]
        assert "rating-hidden" in everything[0]["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_choices_in_named_groups_are_stars_in_order_with_no_group_name(
        self, draw, source
    ):
        soup = draw(source, form=EdgeChoicesForm(choices=stating("named")))

        wrapper = soup.find(id="id_named")

        assert [tag["value"] for tag in wrapper.find_all("input")] == ["1", "2", "3"]
        assert wrapper.find("fieldset") is None
        assert wrapper.find("legend") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_with_no_choices_is_drawn_with_its_frame_and_no_input(
        self, draw, source
    ):
        soup = draw(source, form=EdgeChoicesForm(choices=stating("none")))

        assert soup.find(id="div_id_none") is not None
        assert soup.find(id="id_none").find("input") is None

    @pytest.mark.django_db
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_model_choice_field_has_its_empty_label_as_the_clearing_input(
        self, draw, source
    ):
        first = Group.objects.create(name="First")
        second = Group.objects.create(name="Second")
        form = ModelRatingForm(choices=stating("group"))

        soup = draw(source, form=form)

        assert [tag["value"] for tag in inputs_of(soup, "group")] == [
            "",
            str(first.pk),
            str(second.pk),
        ]
        assert "rating-hidden" in inputs_of(soup, "group")[0]["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_select_and_a_radio_group_with_the_same_choices_draw_the_same_inputs(
        self, draw, source
    ):
        select = draw(
            source, form=RatingsForm({"again": "2"}, choices=stating("again"))
        )
        group = draw(
            source, form=RadioRatingsForm({"again": "2"}, choices=stating("again"))
        )

        assert signature(inputs_of(select, "again")) == signature(
            inputs_of(group, "again")
        )

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_form_drawn_twice_gives_the_same_markup(self, draw, source):
        form = DevelopersRatingForm({"score": "2"}, choices=stating("score", "kind"))

        first = draw(source, form=form)
        second = draw(source, form=form)

        assert str(first) == str(second)

    @pytest.mark.parametrize("source", SOURCES)
    def test_no_script_is_drawn(self, draw, source):
        soup = draw(source, form=RatingsForm(choices=stating("score", "again")))

        assert soup.find("script") is None


class TestRatingKeepsWhatARadioGroupHas:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_stars_are_one_group_named_by_the_label_and_each_by_its_choice(
        self, draw, source
    ):
        form = RatingsForm(choices=stating("score"))

        soup = draw(source, form=form)

        group = soup.find("fieldset", id="div_id_score")
        assert form["score"].label in group.find("legend").get_text()
        assert [tag["aria-label"] for tag in inputs_of(soup, "score")] == LABELS

    @pytest.mark.parametrize("form_class", [KeptRatingsForm])
    @pytest.mark.parametrize("source", SOURCES)
    def test_help_text_and_errors_are_drawn_and_tie_to_the_group(
        self, draw, source, form_class
    ):
        form = form_class({}, choices=stating("score", "kind"))

        soup = draw(source, form=form)

        for name in ("score", "kind"):
            group = soup.find("fieldset", id=f"div_id_{name}")
            described = group["aria-describedby"].split()
            assert f"id_{name}_helptext" in described
            assert f"id_{name}_error" in described
            assert all(soup.find(id=ident) is not None for ident in described)

    @pytest.mark.parametrize("source", SOURCES)
    def test_each_star_of_a_required_rating_left_empty_is_invalid(self, draw, source):
        form = KeptRatingsForm({}, choices=stating("score", "kind"))

        soup = draw(source, form=form)

        for name in ("score", "kind"):
            assert all(
                tag.get("aria-invalid") == "true" for tag in inputs_of(soup, name)
            )

    @pytest.mark.parametrize("source", SOURCES)
    def test_no_star_of_a_rating_that_is_not_in_error_is_invalid(self, draw, source):
        soup = draw(source, form=KeptRatingsForm(choices=stating("score")))

        assert not any(tag.has_attr("aria-invalid") for tag in inputs_of(soup, "score"))

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_legend_holds_the_required_marker_a_radio_group_holds(
        self, draw, source
    ):
        soup = draw(source, form=KeptRatingsForm(choices=stating("score")))

        rated = soup.find("fieldset", id="div_id_score").find("legend")
        group = soup.find("fieldset", id="div_id_kind").find("legend")

        assert rated.find(attrs={"aria-hidden": "true"}) is not None
        assert group.find(attrs={"aria-hidden": "true"}) is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_every_star_of_a_disabled_field_is_disabled(self, draw, source):
        soup = draw(source, form=KeptRatingsForm(choices=stating("locked")))

        stars = inputs_of(soup, "locked")

        assert len(stars) == 5
        assert all(tag.has_attr("disabled") for tag in stars)

    def test_with_labels_off_the_group_has_an_aria_label_and_each_star_keeps_its_own(
        self, draw
    ):
        form = RatingsForm(choices=stating("score"), show_labels=False)

        soup = draw(TAG, form=form)

        group = soup.find("fieldset", id="div_id_score")
        assert group["aria-label"] == form["score"].label
        assert group.find("legend") is None
        assert [tag["aria-label"] for tag in inputs_of(soup, "score")] == LABELS

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_class_and_attribute_are_on_every_input(self, draw, source):
        form = DevelopersRatingForm(choices=stating("score", "kind"))

        soup = draw(source, form=form)

        for name in ("score", "kind"):
            everything = inputs_of(soup, name)
            assert len(everything) == 4
            assert all("mine" in tag["class"] for tag in everything)
            assert all(tag["data-own"] == "yes" for tag in everything)


class TestRatingAmongOtherFields:
    @pytest.mark.parametrize("source", SOURCES)
    def test_only_the_field_stated_changes(self, draw, source):
        soup = draw(source, form=RatingsForm(choices=stating("score")))

        assert len(soup.find_all(class_="rating")) == 1
        assert soup.find("select", id="id_other") is not None
        assert [tag["type"] for tag in inputs_of(soup, "kind")] == ["radio"] * 5
        assert all("mask" not in tag["class"] for tag in inputs_of(soup, "kind"))

    @pytest.mark.parametrize("template", [None, TABLE], ids=["stacked", "table"])
    def test_every_form_of_a_formset_draws_the_field_as_a_rating(self, draw, template):
        settings = {} if template is None else {"template": template}
        helper = formset_helper(**settings)
        helper.daisyui = stating("score")

        soup = draw(
            "{% crispy formset helper %}", formset=RatedLineFormSet(), helper=helper
        )

        ids = [tag["id"] for tag in soup.find_all(id=True)]
        names = []
        for row in range(3):
            wrapper = soup.find(id=f"id_form-{row}-score")
            assert "rating" in wrapper["class"]
            row_names = {tag["name"] for tag in wrapper.find_all("input")}
            assert len(row_names) == 1
            names.extend(row_names)
        assert len(ids) == len(set(ids))
        assert len(names) == len(set(names)) == 3

    @pytest.mark.parametrize(
        "wrap",
        [
            lambda: Row(Column("score")),
            lambda: Fieldset("Rate it", "score"),
            lambda: TabHolder(Tab("Rate", "score")),
            lambda: Accordion(AccordionGroup("Rate", "score")),
        ],
        ids=["row", "fieldset", "tab", "accordion group"],
    )
    def test_inside_another_layout_object_it_is_drawn_as_it_is_outside_one(
        self, draw, wrap
    ):
        alone = draw(TAG, form=RatingsForm(layout=[Choice("score", drawing="rating")]))
        inside = draw(
            TAG,
            form=RatingsForm(layout=[wrap()], choices=stating("score")),
        )

        assert signature(inputs_of(inside, "score")) == signature(
            inputs_of(alone, "score")
        )
        assert "rating" in inside.find(id="id_score")["class"]

    def test_text_attached_to_a_rating_is_not_drawn_and_the_rating_is(self, draw):
        form = RatingsForm(
            layout=[Choice(PrependedText("score", "$"), drawing="rating")]
        )

        soup = draw(TAG, form=form)

        assert [tag["value"] for tag in inputs_of(soup, "score")] == VALUES
        assert "$" not in soup.get_text()

    def test_a_layout_object_that_draws_radios_along_a_line_draws_the_rating(
        self, draw
    ):
        form = RatingsForm(layout=[InlineRadios("kind")], choices=stating("kind"))

        soup = draw(TAG, form=form)

        assert "rating" in soup.find(id="id_kind")["class"]
        assert [tag["value"] for tag in inputs_of(soup, "kind")] == VALUES


class TestRatingMistakes:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_name_that_is_not_a_drawing_names_the_field_and_the_rating(
        self, draw, source
    ):
        error = refused(
            draw,
            source,
            RatingsForm(
                choices=FormChoices(fields={"score": Choice(drawing="slider")})
            ),
        )

        assert (error.kind, error.value, error.target) == ("drawing", "slider", "score")
        assert error.allowed == ("rating",)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("name", "allowed"),
        [
            ("title", ()),
            ("many", ()),
            ("boxes", ()),
            ("maybe", ()),
            ("flag", ("checkbox", "toggle", "switch")),
        ],
    )
    def test_a_rating_stated_for_another_kind_of_field_is_refused(
        self, draw, source, name, allowed
    ):
        error = refused(draw, source, RefusedRatingsForm(choices=stating(name)))

        assert (error.kind, error.value, error.target) == ("drawing", "rating", name)
        assert error.allowed == allowed

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", ["checkbox", "toggle", "switch"])
    @pytest.mark.parametrize("name", ["score", "kind"])
    def test_a_drawing_of_a_boolean_field_is_refused_with_the_rating_allowed(
        self, draw, source, name, drawing
    ):
        choices = FormChoices(fields={name: Choice(drawing=drawing)})

        error = refused(draw, source, RatingsForm(choices=choices))

        assert (error.kind, error.value, error.target) == ("drawing", drawing, name)
        assert error.allowed == ("rating",)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["own_select", "own_group"])
    def test_a_rating_stated_for_a_widget_with_a_template_of_its_own_is_refused(
        self, draw, source, name
    ):
        error = refused(draw, source, OwnTemplateRatingsForm(choices=stating(name)))

        assert (error.kind, error.value, error.target) == ("drawing", "rating", name)
        assert error.allowed == ()

    def test_a_rating_stated_in_a_layout_for_a_text_field_is_refused(self, draw):
        form = RatingsForm(layout=[Choice("title", drawing="rating")])

        error = refused(draw, TAG, form)

        assert (error.kind, error.target) == ("drawing", "title")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_hidden_field_raises_nothing_and_is_a_hidden_input(self, draw, source):
        soup = draw(source, form=RefusedRatingsForm(choices=stating("secret")))

        tag = soup.find("input", attrs={"name": "secret"})

        assert tag["type"] == "hidden"


class TestRatingSizeAndColour:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["score", "kind"])
    def test_the_forms_size_is_on_the_element_that_is_the_rating(
        self, draw, source, name
    ):
        choices = FormChoices(size="sm", fields={name: Choice(drawing="rating")})

        soup = draw(source, form=RatingsForm(choices=choices))

        assert "rating-sm" in wrapper_classes(soup, name)
        assert all("rating-sm" not in classes for classes in star_classes(soup, name))

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("name", ["score", "kind", "again"])
    def test_the_forms_colour_is_on_every_star_and_never_on_the_clearing_input(
        self, draw, source, name
    ):
        choices = FormChoices(color="primary", fields={name: Choice(drawing="rating")})

        soup = draw(source, form=RatingsForm(choices=choices))

        assert all("bg-primary" in classes for classes in star_classes(soup, name))
        assert "bg-primary" not in wrapper_classes(soup, name)
        assert all(
            "bg-primary" not in classes for classes in clearing_classes(soup, name)
        )
        assert bool(clearing_classes(soup, name)) == (name == "again")

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_fields_own_size_and_colour_win_when_stated_by_name(self, draw, source):
        choices = FormChoices(
            size="sm",
            color="primary",
            fields={"score": Choice(drawing="rating", size="lg", color="accent")},
        )

        soup = draw(source, form=RatingsForm(choices=choices))

        assert {"rating-lg"} <= wrapper_classes(soup, "score")
        assert "rating-sm" not in wrapper_classes(soup, "score")
        for classes in star_classes(soup, "score"):
            assert "bg-accent" in classes
            assert "bg-primary" not in classes

    def test_the_fields_own_size_and_colour_win_when_stated_in_a_layout(self, draw):
        form = RatingsForm(
            layout=[
                Choice("score", drawing="rating", size="xl", color="error"),
                Choice("again", drawing="rating"),
            ],
            choices=FormChoices(size="sm", color="primary"),
        )

        soup = draw(TAG, form=form)

        assert "rating-xl" in wrapper_classes(soup, "score")
        assert all("bg-error" in classes for classes in star_classes(soup, "score"))
        assert "rating-sm" in wrapper_classes(soup, "again")
        assert all("bg-primary" in classes for classes in star_classes(soup, "again"))

    def test_a_drawing_a_size_and_a_colour_stated_together_all_take_effect(self, draw):
        form = RatingsForm(
            layout=[Choice("score", drawing="rating", size="xs", color="success")]
        )

        soup = draw(TAG, form=form)

        assert {"rating", "rating-xs"} <= wrapper_classes(soup, "score")
        for classes in star_classes(soup, "score"):
            assert {"mask", "mask-star-2", "bg-success"} <= classes

    @pytest.mark.parametrize("source", SOURCES)
    def test_with_nothing_stated_no_size_or_colour_is_written(self, draw, source):
        soup = draw(source, form=RatingsForm(choices=stating("score", "again")))

        for name in ("score", "again"):
            assert "rating" in wrapper_classes(soup, name)
            assert not {
                value
                for value in wrapper_classes(soup, name)
                if value.startswith("rating-")
            }
            for classes in star_classes(soup, name):
                assert not {value for value in classes if value.startswith("bg-")}

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_variant_the_form_states_is_passed_over(self, draw, source):
        choices = FormChoices(
            variant="ghost", fields={"score": Choice(drawing="rating")}
        )

        soup = draw(source, form=RatingsForm(choices=choices))

        assert "rating" in wrapper_classes(soup, "score")

    def test_a_variant_stated_on_the_field_raises_naming_it(self, draw):
        form = RatingsForm(layout=[Choice("score", drawing="rating", variant="ghost")])

        error = refused(draw, TAG, form)

        assert (error.kind, error.value, error.allowed) == ("variant", "ghost", ())
        assert error.target == "score"

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_in_error_drops_the_colour_keeps_the_size_and_carries_bg_error(
        self, draw, source
    ):
        choices = FormChoices(
            size="sm",
            color="primary",
            fields={
                "again": Choice(drawing="rating"),
                "score": Choice(drawing="rating"),
            },
        )
        form = RatingsForm({"again": "9", "score": "3"}, choices=choices)

        soup = draw(source, form=form)

        assert "rating-sm" in wrapper_classes(soup, "again")
        for classes in star_classes(soup, "again"):
            assert "bg-error" in classes
            assert "bg-primary" not in classes
        assert all(
            "bg-error" not in classes for classes in clearing_classes(soup, "again")
        )
        assert all("bg-primary" in classes for classes in star_classes(soup, "score"))

    @pytest.mark.parametrize("size", SIZES)
    def test_every_size_is_written_as_its_rating_class(self, draw, size):
        choices = FormChoices(size=size, fields={"score": Choice(drawing="rating")})

        soup = draw(TAG, form=RatingsForm(choices=choices))

        assert f"rating-{size}" in wrapper_classes(soup, "score")

    @pytest.mark.parametrize("color", COLORS)
    def test_every_colour_is_written_as_its_background_class(self, draw, color):
        choices = FormChoices(color=color, fields={"score": Choice(drawing="rating")})

        soup = draw(TAG, form=RatingsForm(choices=choices))

        assert all(f"bg-{color}" in classes for classes in star_classes(soup, "score"))
