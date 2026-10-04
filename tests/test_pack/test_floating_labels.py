"""A field drawn with daisyUI's floating label, through crispy-forms."""

import pytest
from crispy_forms.bootstrap import (
    FieldWithButtons,
    InlineField,
    PrependedText,
    StrictButton,
)

from mvp_forms.choices import Choice, FormChoices, InvalidChoice, Modifiers
from tests.forms import FloatingForm, LineFormSet, formset_helper

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
TAG = "{% crispy form %}"
FORMSET = "{% crispy formset helper %}"
TABLE = "daisyui/table_inline_formset.html"
FLOATING = FormChoices(label="floating")
FLOATERS = ("name", "notes", "country")
COMPONENTS = {"name": "input", "notes": "textarea", "country": "select"}
STATED = [
    pytest.param("size", "lg", id="size"),
    pytest.param("color", "primary", id="colour"),
    pytest.param("variant", "ghost", id="variant"),
]


def named(*names, label="floating"):
    return FormChoices(fields={name: Choice(label=label) for name in names})


def floating_label_of(soup, name):
    return soup.find(id=f"id_{name}").find_parent("label", class_="floating-label")


def labels_for(soup, name):
    return soup.find_all("label", attrs={"for": f"id_{name}"})


def classes_of(soup, name):
    return set(soup.find(id=f"id_{name}")["class"])


def modifiers_of(soup, name, kind):
    component = COMPONENTS.get(name, "input")
    return classes_of(soup, name) & set(Modifiers.tables[kind][component].values())


def refused(draw, source, form):
    with pytest.raises(InvalidChoice) as caught:
        draw(source, form=form)
    return caught.value


class TestFloatingLabels:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_that_states_nothing_has_no_floating_label(self, draw, source):
        soup = draw(source, form=FloatingForm())

        assert soup.find(class_="floating-label") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_stated_by_name_is_drawn_inside_one_floating_label(
        self, draw, source
    ):
        soup = draw(source, form=FloatingForm(choices=named("name")))

        label = floating_label_of(soup, "name")
        assert label is not None
        assert label["for"] == "id_name"
        assert len(soup.find_all(class_="floating-label")) == 1
        assert labels_for(soup, "name") == [label]

    def test_a_field_stated_in_a_layout_is_drawn_inside_one_floating_label(self, draw):
        form = FloatingForm(layout=[Choice("name", label="floating"), "notes"])

        soup = draw(TAG, form=form)

        label = floating_label_of(soup, "name")
        assert label["for"] == "id_name"
        assert labels_for(soup, "name") == [label]
        assert floating_label_of(soup, "notes") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_forms_statement_floats_an_input_a_textarea_and_a_select(
        self, draw, source
    ):
        soup = draw(source, form=FloatingForm(choices=FLOATING))

        for name in FLOATERS:
            assert floating_label_of(soup, name)["for"] == f"id_{name}"
            assert len(labels_for(soup, name)) == 1

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_forms_statement_leaves_the_checkbox_as_it_is_without_it(
        self, draw, source
    ):
        plain = draw(source, form=FloatingForm())
        stated = draw(source, form=FloatingForm(choices=FLOATING))

        assert floating_label_of(stated, "agree") is None
        assert stated.find(id="div_id_agree") == plain.find(id="div_id_agree")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_that_undoes_the_statement_has_its_ordinary_label(
        self, draw, source
    ):
        choices = FormChoices(label="floating", fields={"notes": Choice(label=None)})

        soup = draw(source, form=FloatingForm(choices=choices))

        (ordinary,) = labels_for(soup, "notes")
        assert "floating-label" not in ordinary.get("class", [])
        assert floating_label_of(soup, "notes") is None
        assert floating_label_of(soup, "name") is not None
        assert floating_label_of(soup, "country") is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_empty_field_with_no_placeholder_carries_its_label_as_one(
        self, draw, source
    ):
        form = FloatingForm(choices=FLOATING)

        soup = draw(source, form=form)

        assert soup.find(id="id_name")["placeholder"] == form["name"].label
        assert soup.find(id="id_notes")["placeholder"] == form["notes"].label

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_placeholder_the_developer_set_is_kept(self, draw, source):
        form = FloatingForm(choices=FLOATING)

        soup = draw(source, form=form)

        widget = form.fields["nickname"].widget
        assert soup.find(id="id_nickname")["placeholder"] == widget.attrs["placeholder"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_select_is_given_no_placeholder(self, draw, source):
        soup = draw(source, form=FloatingForm(choices=FLOATING))

        assert not soup.find(id="id_country").has_attr("placeholder")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_required_field_in_error_keeps_its_marker_help_text_and_error(
        self, draw, source
    ):
        soup = draw(source, form=FloatingForm({}, choices=FLOATING))

        field = soup.find(id="id_name")
        label = floating_label_of(soup, "name")
        assert label.find(attrs={"aria-hidden": "true"}) is not None
        assert len(soup.find_all(id="id_name_helptext")) == 1
        assert len(soup.find_all(id="id_name_error")) == 1
        assert field["aria-invalid"] == "true"
        assert set(field["aria-describedby"].split()) == {
            "id_name_helptext",
            "id_name_error",
        }

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_help_text_and_the_error_are_not_inside_the_floating_label(
        self, draw, source
    ):
        soup = draw(source, form=FloatingForm({}, choices=FLOATING))

        label = floating_label_of(soup, "name")

        assert label.find(id="id_name_helptext") is None
        assert label.find(id="id_name_error") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_field_is_disabled_and_has_its_ordinary_label(
        self, draw, source
    ):
        soup = draw(source, form=FloatingForm(choices=named("locked")))

        (ordinary,) = labels_for(soup, "locked")
        assert soup.find(id="id_locked").has_attr("disabled")
        assert "floating-label" not in ordinary.get("class", [])
        assert floating_label_of(soup, "locked") is None

    def test_with_the_labels_off_no_label_is_drawn_and_the_input_is_named(self, draw):
        form = FloatingForm(choices=FLOATING, show_labels=False)

        soup = draw(TAG, form=form)

        assert soup.find("label") is None
        for name in FLOATERS:
            assert soup.find(id=f"id_{name}")["aria-label"] == form[name].label

    def test_every_form_of_a_stacked_formset_draws_the_field_floating(self, draw):
        helper = formset_helper()
        helper.daisyui = FLOATING

        soup = draw(FORMSET, formset=LineFormSet(), helper=helper)

        for row in range(3):
            label = soup.find(id=f"id_form-{row}-name").find_parent(
                "label", class_="floating-label"
            )
            assert label["for"] == f"id_form-{row}-name"

    def test_a_field_stated_by_name_floats_in_every_form_of_a_stacked_formset(
        self, draw
    ):
        helper = formset_helper()
        helper.daisyui = FormChoices(fields={"name": Choice(label="floating")})

        soup = draw(FORMSET, formset=LineFormSet(), helper=helper)

        assert len(soup.find_all(class_="floating-label")) == 3


class TestFloatingLabelChoices:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("kind", "value"), STATED)
    def test_the_forms_choice_reaches_an_input_a_textarea_and_a_select(
        self, draw, source, kind, value
    ):
        soup = draw(
            source,
            form=FloatingForm(choices=FormChoices(label="floating", **{kind: value})),
        )

        for name, component in COMPONENTS.items():
            assert floating_label_of(soup, name) is not None
            assert modifiers_of(soup, name, kind) == {
                Modifiers.tables[kind][component][value]
            }

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("kind", ["size", "color", "variant"])
    def test_every_name_the_tables_have_reaches_a_floating_field(
        self, draw, source, kind
    ):
        for value in Modifiers.names(kind, None):
            soup = draw(
                source,
                form=FloatingForm(
                    choices=FormChoices(label="floating", **{kind: value})
                ),
            )

            for name, component in COMPONENTS.items():
                expected = Modifiers.tables[kind][component].get(value)
                assert modifiers_of(soup, name, kind) == ({expected} - {None})

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_floating_field_carries_what_it_carries_with_its_ordinary_label(
        self, draw, source
    ):
        stated = {"size": "sm", "color": "primary", "variant": "ghost"}

        ordinary = draw(source, form=FloatingForm(choices=FormChoices(**stated)))
        floating = draw(
            source, form=FloatingForm(choices=FormChoices(label="floating", **stated))
        )

        for name in FLOATERS:
            assert classes_of(floating, name) == classes_of(ordinary, name)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_fields_own_choice_wins_over_the_forms_for_that_field_alone(
        self, draw, source
    ):
        choices = FormChoices(
            label="floating",
            size="sm",
            color="primary",
            fields={"name": Choice(size="xl", color="accent")},
        )

        soup = draw(source, form=FloatingForm(choices=choices))

        assert modifiers_of(soup, "name", "size") == {Modifiers.sizes["input"]["xl"]}
        assert modifiers_of(soup, "name", "color") == {
            Modifiers.colors["input"]["accent"]
        }
        assert modifiers_of(soup, "notes", "size") == {
            Modifiers.sizes["textarea"]["sm"]
        }
        assert modifiers_of(soup, "notes", "color") == {
            Modifiers.colors["textarea"]["primary"]
        }

    def test_a_choice_in_the_layout_wins_over_the_fields_entry_and_the_forms(
        self, draw
    ):
        choices = FormChoices(
            label="floating", size="sm", fields={"name": Choice(size="xl")}
        )
        form = FloatingForm(
            choices=choices, layout=[Choice("name", size="xs"), "notes"]
        )

        soup = draw(TAG, form=form)

        assert modifiers_of(soup, "name", "size") == {Modifiers.sizes["input"]["xs"]}
        assert modifiers_of(soup, "notes", "size") == {
            Modifiers.sizes["textarea"]["sm"]
        }

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_that_undoes_a_choice_carries_none_of_that_kind(self, draw, source):
        choices = FormChoices(
            label="floating", size="sm", fields={"notes": Choice(size=None)}
        )

        soup = draw(source, form=FloatingForm(choices=choices))

        assert modifiers_of(soup, "notes", "size") == set()
        assert modifiers_of(soup, "name", "size") == {Modifiers.sizes["input"]["sm"]}

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_floating_field_in_error_carries_the_error_modifier_and_no_colour(
        self, draw, source
    ):
        choices = FormChoices(label="floating", color="primary")

        soup = draw(source, form=FloatingForm({}, choices=choices))

        assert modifiers_of(soup, "name", "color") == {
            Modifiers.colors["input"]["error"]
        }
        assert modifiers_of(soup, "nickname", "color") == {
            Modifiers.colors["input"]["primary"]
        }


class TestFloatingLabelKeepsTheData:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("bound", [False, True], ids=["valid", "invalid"])
    def test_a_form_posted_from_its_drawn_inputs_cleans_to_the_same_data(
        self, draw, posted, source, bound
    ):
        results = []
        for choices in (None, FLOATING):
            data = posted(draw(source, form=FloatingForm(choices=choices)))
            data["name"] = "" if bound else "Ada"
            form = FloatingForm(data, choices=choices)
            results.append(
                (sorted(data), form.is_valid(), form.errors, form.cleaned_data)
            )

        assert results[0] == results[1]
        assert results[0][1] is not bound


class TestFloatingLabelMistakes:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_that_cannot_float_raises_naming_the_field(self, draw, source):
        error = refused(draw, source, FloatingForm(choices=named("agree")))

        assert (error.kind, error.value, error.target) == (
            "label",
            "floating",
            "agree",
        )
        assert error.allowed == ()

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_unknown_name_for_a_field_raises_with_the_names_allowed(
        self, draw, source
    ):
        error = refused(
            draw, source, FloatingForm(choices=named("name", label="sliding"))
        )

        assert (error.kind, error.value, error.target) == ("label", "sliding", "name")
        assert error.allowed == ("floating",)

    @pytest.mark.parametrize("source", SOURCES)
    def test_an_unknown_name_for_the_form_raises_naming_no_field(self, draw, source):
        error = refused(
            draw, source, FloatingForm(choices=FormChoices(label="sliding"))
        )

        assert (error.kind, error.value, error.target) == ("label", "sliding", None)
        assert error.allowed == ("floating",)

    def test_a_field_that_cannot_float_in_a_layout_raises_naming_the_field(self, draw):
        form = FloatingForm(layout=[Choice("agree", label="floating")])

        error = refused(draw, TAG, form)

        assert (error.kind, error.target, error.allowed) == ("label", "agree", ())

    @pytest.mark.parametrize(
        "layout",
        [
            pytest.param(lambda: PrependedText("name", "$"), id="attached text"),
            pytest.param(
                lambda: FieldWithButtons("name", StrictButton("Go")), id="buttons"
            ),
            pytest.param(lambda: InlineField("name"), id="inline"),
        ],
    )
    def test_a_field_with_a_decoration_raises_naming_the_field_when_stated_by_name(
        self, draw, layout
    ):
        form = FloatingForm(layout=[layout()], choices=named("name"))

        error = refused(draw, TAG, form)

        assert (error.kind, error.target, error.allowed) == ("label", "name", ())

    @pytest.mark.parametrize(
        "layout",
        [
            pytest.param(lambda: PrependedText("name", "$"), id="attached text"),
            pytest.param(
                lambda: FieldWithButtons("name", StrictButton("Go")), id="buttons"
            ),
            pytest.param(lambda: InlineField("name"), id="inline"),
        ],
    )
    def test_the_forms_statement_passes_over_a_field_with_a_decoration(
        self, draw, layout
    ):
        form = FloatingForm(layout=[layout()], choices=FLOATING)

        soup = draw(TAG, form=form)

        assert floating_label_of(soup, "name") is None

    def test_a_label_stated_around_a_button_raises_naming_the_button(self, draw):
        form = FloatingForm(
            layout=["name", Choice(StrictButton("Go"), label="floating")]
        )

        error = refused(draw, TAG, form)

        assert (error.kind, error.allowed) == ("label", ())
        assert error.target is not None

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_hidden_field_takes_nothing_and_raises_nothing(self, draw, source):
        soup = draw(source, form=FloatingForm(choices=named("token")))

        assert soup.find(id="id_token")["type"] == "hidden"

    def test_a_formset_drawn_as_a_table_draws_no_floating_label_and_raises_nothing(
        self, draw
    ):
        helper = formset_helper(template=TABLE)
        helper.daisyui = FLOATING

        soup = draw(FORMSET, formset=LineFormSet(), helper=helper)

        assert soup.find(class_="floating-label") is None
        assert soup.find(id="id_form-0-name") is not None


class TestFloatingLabelEscaping:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_label_holding_markup_is_escaped_inside_the_floating_label(
        self, draw, source
    ):
        form = FloatingForm(choices=named("markup"))

        soup = draw(source, form=form)

        label = floating_label_of(soup, "markup")
        assert label.find("b") is None
        assert label.find("span").get_text().strip() == form["markup"].label

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_label_holding_markup_is_escaped_in_the_placeholder(self, draw, source):
        form = FloatingForm(choices=named("markup"))

        soup = draw(source, form=form)

        assert soup.find(id="id_markup")["placeholder"] == form["markup"].label
