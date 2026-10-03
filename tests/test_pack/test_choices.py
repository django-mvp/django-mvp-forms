"""Size, colour and variant stated for a whole form, drawn through crispy-forms."""

import re

import pytest
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Button,
    Column,
    Div,
    Fieldset,
    Hidden,
    Layout,
    Reset,
    Row,
    Submit,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template

from mvp_forms.choices import Choice, FormChoices
from tests.forms import (
    ButtonedForm,
    DeveloperAttrsForm,
    EveryInputForm,
    FilesForm,
    StructureForm,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
STATEMENT = {"size": "lg", "color": "primary", "variant": "ghost"}
# Each field of EveryInputForm that is drawn as inputs: its name, the daisyUI
# component, and how many inputs it is made of.
INPUTS = [
    ("text", "input", 1),
    ("message", "textarea", 1),
    ("choice", "select", 1),
    ("born", "select", 3),
    ("agree", "checkbox", 1),
    ("radios", "radio", 2),
    ("boxes", "checkbox", 2),
    ("upload", "file-input", 1),
    ("held", "file-input", 1),
    ("locked", "input", 1),
    ("readonly", "input", 1),
]
WITH_VARIANT = [
    row for row in INPUTS if row[1] in {"input", "textarea", "select", "file-input"}
]
WITHOUT_VARIANT = [row for row in INPUTS if row[1] in {"checkbox", "radio"}]
IN_ERROR = [
    row
    for row in INPUTS
    if row[0] in {"text", "message", "choice", "born", "radios", "boxes"}
]


def stated(form, **statement):
    form.helper.daisyui = FormChoices(**statement)
    return form


def inputs_of(soup, name):
    pattern = re.compile(rf"^{name}(_year|_month|_day)?$")
    return soup.find_all(["input", "select", "textarea"], attrs={"name": pattern})


def classes(tag):
    return set(tag.get("class", []))


def without_classes(soup):
    for tag in soup.find_all(class_=True):
        del tag["class"]
    return str(soup)


def fields_in_a_nest():
    return [
        Fieldset(
            "Everything",
            Div(
                Row(Column("text"), Column("message")),
                Div("choice", "born", css_id="inner"),
            ),
            "agree",
            Row(Column("radios"), Column("boxes")),
        ),
        "upload",
        "held",
        "locked",
        "readonly",
        "token",
    ]


class TestFormWideChoices:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), INPUTS)
    def test_every_visible_input_carries_the_size(
        self, draw, source, name, component, count
    ):
        soup = draw(source, form=stated(EveryInputForm(), size="lg"))

        found = inputs_of(soup, name)

        assert len(found) == count
        assert all(f"{component}-lg" in classes(tag) for tag in found)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), INPUTS)
    def test_every_visible_input_carries_the_colour(
        self, draw, source, name, component, count
    ):
        soup = draw(source, form=stated(EveryInputForm(), color="primary"))

        found = inputs_of(soup, name)

        assert len(found) == count
        assert all(f"{component}-primary" in classes(tag) for tag in found)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), WITH_VARIANT)
    def test_every_input_with_the_variant_carries_it(
        self, draw, source, name, component, count
    ):
        soup = draw(source, form=stated(EveryInputForm(), variant="ghost"))

        found = inputs_of(soup, name)

        assert len(found) == count
        assert all(f"{component}-ghost" in classes(tag) for tag in found)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), WITHOUT_VARIANT)
    def test_an_input_without_the_variant_is_drawn_without_it(
        self, draw, source, name, component, count
    ):
        with_variant = draw(source, form=stated(EveryInputForm(), variant="ghost"))
        without = draw(source, form=EveryInputForm())

        found = inputs_of(with_variant, name)

        assert len(found) == count
        assert [classes(tag) for tag in found] == [
            classes(tag) for tag in inputs_of(without, name)
        ]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("kind", "before", "after"),
        [
            ("size", "sm", "lg"),
            ("color", "primary", "accent"),
            ("variant", "ghost", None),
        ],
    )
    def test_changing_one_choice_leaves_the_other_two_as_they_were(
        self, draw, source, kind, before, after
    ):
        base = {"size": "sm", "color": "primary", "variant": "ghost"}
        first = draw(source, form=stated(EveryInputForm(), **{**base, kind: before}))
        second = draw(source, form=stated(EveryInputForm(), **{**base, kind: after}))

        for name, component, _ in INPUTS:
            for one, other in zip(
                inputs_of(first, name), inputs_of(second, name), strict=True
            ):
                assert classes(one) - {f"{component}-{before}"} == classes(other) - {
                    f"{component}-{after}"
                }

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_removal_checkbox_of_a_held_file_takes_the_size_and_colour(
        self, draw, source
    ):
        soup = draw(source, form=stated(EveryInputForm(), **STATEMENT))

        removal = soup.find("input", attrs={"name": "held-clear"})

        assert classes(removal) == {"checkbox", "checkbox-lg", "checkbox-primary"}

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_drawn_with_nothing_stated_has_the_removal_checkbox_it_had(
        self, draw, source
    ):
        soup = draw(source, form=EveryInputForm())

        removal = soup.find("input", attrs={"name": "held-clear"})

        assert removal["class"] == ["checkbox"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_hidden_inputs_are_unchanged(self, draw, source):
        plain = draw(source, form=EveryInputForm())
        chosen = draw(source, form=stated(EveryInputForm(), **STATEMENT))

        hidden = chosen.find("input", attrs={"name": "token"})

        assert hidden["type"] == "hidden"
        assert str(hidden) == str(plain.find("input", attrs={"name": "token"}))

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_stating_nothing_is_drawn_as_a_form_with_no_statement_is(
        self, draw, source
    ):
        without = draw(source, form=EveryInputForm({}))
        stating_nothing = draw(source, form=stated(EveryInputForm({})))

        assert str(stating_nothing) == str(without)

    @pytest.mark.parametrize("source", SOURCES)
    def test_only_classes_change_labels_help_errors_and_attributes_stay(
        self, draw, source
    ):
        without = draw(source, form=EveryInputForm({}))
        chosen = draw(source, form=stated(EveryInputForm({}), **STATEMENT))

        assert without_classes(chosen) == without_classes(without)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_disabled_field_takes_the_choices_and_stays_disabled(self, draw, source):
        soup = draw(source, form=stated(EveryInputForm(), **STATEMENT))

        locked = soup.find(id="id_locked")

        assert locked.has_attr("disabled")
        assert {"input-lg", "input-primary", "input-ghost"} <= classes(locked)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_read_only_field_takes_the_choices_and_stays_read_only(
        self, draw, source
    ):
        soup = draw(source, form=stated(EveryInputForm(), **STATEMENT))

        readonly = soup.find(id="id_readonly")

        assert readonly.has_attr("readonly")
        assert {"input-lg", "input-primary", "input-ghost"} <= classes(readonly)

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_developers_own_classes_are_kept(self, draw, source):
        form = DeveloperAttrsForm()
        form.helper = FormHelper(form)
        form.helper.daisyui = FormChoices(size="sm")

        name = draw(source, form=form).find(id="id_name")

        assert {"wide", "input", "input-sm"} <= classes(name)

    def test_every_field_takes_the_choices_wherever_the_layout_places_it(self, draw):
        form = stated(EveryInputForm(layout=fields_in_a_nest()), size="lg")

        soup = draw("{% crispy form %}", form=form)

        for name, component, count in INPUTS:
            found = inputs_of(soup, name)
            assert len(found) == count
            assert all(f"{component}-lg" in classes(tag) for tag in found)


class TestFormWideChoicesOnAFieldInError:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), IN_ERROR)
    def test_it_keeps_its_error_modifier_and_drops_the_colour(
        self, draw, source, name, component, count
    ):
        soup = draw(source, form=stated(EveryInputForm({}), **STATEMENT))

        found = inputs_of(soup, name)

        assert len(found) == count
        for tag in found:
            assert f"{component}-error" in classes(tag)
            assert f"{component}-primary" not in classes(tag)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(("name", "component", "count"), IN_ERROR)
    def test_it_keeps_the_size(self, draw, source, name, component, count):
        soup = draw(source, form=stated(EveryInputForm({}), **STATEMENT))

        assert all(f"{component}-lg" in classes(t) for t in inputs_of(soup, name))

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("name", "component"),
        [("text", "input"), ("message", "textarea"), ("choice", "select")],
    )
    def test_it_keeps_the_variant(self, draw, source, name, component):
        soup = draw(source, form=stated(EveryInputForm({}), **STATEMENT))

        assert f"{component}-ghost" in classes(soup.find(id=f"id_{name}"))

    def test_with_errors_off_the_field_is_not_in_error_and_takes_the_colour(self, draw):
        form = stated(EveryInputForm({}), **STATEMENT)
        form.helper.form_show_errors = False

        text = draw("{% crispy form %}", form=form).find(id="id_text")

        assert "input-primary" in classes(text)
        assert "input-error" not in classes(text)


class TestRemovalCheckboxOfAFileInError:
    def contradicting(self):
        data = {"optional-clear": "on"}
        files = {"optional": SimpleUploadedFile("new.pdf", b"content")}
        return FilesForm(data, files)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_stating_nothing_draws_it_with_the_class_it_has_today(
        self, draw, source
    ):
        soup = draw(source, form=self.contradicting())

        removal = soup.find("input", attrs={"name": "optional-clear"})

        assert "file-input-error" in classes(soup.find(id="id_optional"))
        assert removal["class"] == ["checkbox"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_form_stating_choices_gives_it_the_size_and_never_the_error(
        self, draw, source
    ):
        form = self.contradicting()
        form.helper = FormHelper(form)
        form.helper.daisyui = FormChoices(**STATEMENT)

        soup = draw(source, form=form)
        removal = soup.find("input", attrs={"name": "optional-clear"})

        assert "file-input-error" in classes(soup.find(id="id_optional"))
        assert classes(removal) == {"checkbox", "checkbox-lg"}


def structured(*layout, **statement):
    form = StructureForm(layout=layout)
    form.helper.daisyui = FormChoices(**statement)
    return form


def named(form, name):
    return classes(form.find(id=f"id_{name}"))


class TestFieldChoices:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_named_by_the_form_takes_its_own_size_and_no_other_changes(
        self, draw, source
    ):
        form = StructureForm()
        form.helper.daisyui = FormChoices(
            size="sm", fields={"second": Choice(size="lg")}
        )

        soup = draw(source, form=form)

        assert "input-lg" in named(soup, "second")
        assert "input-sm" not in named(soup, "second")
        for other in ("first", "third", "fourth"):
            assert "input-sm" in named(soup, other)
            assert "input-lg" not in named(soup, other)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_named_by_the_form_on_a_form_stating_nothing_else_takes_it(
        self, draw, source
    ):
        form = StructureForm()
        form.helper.daisyui = FormChoices(fields={"second": Choice(color="accent")})

        soup = draw(source, form=form)

        assert "input-accent" in named(soup, "second")
        assert "input-accent" not in named(soup, "first")

    def test_a_choice_in_a_layout_gives_its_field_its_own_size(self, draw):
        form = structured(
            Choice("second", size="lg"), "first", "third", "fourth", size="sm"
        )

        soup = draw("{% crispy form %}", form=form)

        assert "input-lg" in named(soup, "second")
        assert "input-sm" not in named(soup, "second")
        for other in ("first", "third", "fourth"):
            assert "input-sm" in named(soup, other)
            assert "input-lg" not in named(soup, other)

    def test_a_field_stating_only_a_colour_keeps_the_forms_size(self, draw):
        form = structured(
            Choice("first", color="accent"), "second", size="sm", color="primary"
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"input-accent", "input-sm"} <= named(soup, "first")
        assert "input-primary" not in named(soup, "first")
        assert {"input-primary", "input-sm"} <= named(soup, "second")

    def test_none_undoes_the_forms_colour_and_keeps_its_size(self, draw):
        form = structured(
            Choice("first", color=None), "second", size="sm", color="primary"
        )

        soup = draw("{% crispy form %}", form=form)

        assert "input-sm" in named(soup, "first")
        assert not {"input-primary", "input-accent"} & named(soup, "first")
        assert "input-primary" in named(soup, "second")

    def test_a_choice_in_a_layout_on_a_form_stating_nothing_takes_effect(self, draw):
        form = structured(Choice("first", size="lg"), "second")

        soup = draw("{% crispy form %}", form=form)

        assert "input-lg" in named(soup, "first")
        assert "input-lg" not in named(soup, "second")

    def test_a_choice_in_a_layout_wins_over_the_one_named_by_the_form(self, draw):
        form = structured(
            Choice("first", size="xl"),
            "second",
            fields={"first": Choice(size="xs", color="accent")},
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"input-xl", "input-accent"} <= named(soup, "first")
        assert "input-xs" not in named(soup, "first")

    def test_wrapping_a_field_with_a_choice_gives_it_the_choice(self, draw):
        form = structured("first", "second", "third", size="sm")
        form.helper["second"].wrap(Choice, size="lg")

        soup = draw("{% crispy form %}", form=form)

        assert "input-lg" in named(soup, "second")
        assert "input-sm" in named(soup, "first")
        assert "input-sm" in named(soup, "third")

    def test_a_choice_inside_a_choice_wins_for_each_kind_it_states(self, draw):
        form = structured(
            Choice(
                "first",
                Choice("second", size="xl"),
                "third",
                size="lg",
                color="accent",
            ),
            "fourth",
            size="sm",
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"input-lg", "input-accent"} <= named(soup, "first")
        assert {"input-xl", "input-accent"} <= named(soup, "second")
        assert "input-lg" not in named(soup, "second")
        assert {"input-lg", "input-accent"} <= named(soup, "third")
        assert "input-sm" in named(soup, "fourth")
        assert "input-accent" not in named(soup, "fourth")

    def test_a_choice_holding_a_row_gives_every_field_in_it_the_choice(self, draw):
        form = structured(
            Choice(Row(Column("first"), Column("second")), size="lg"),
            "third",
            size="sm",
        )

        soup = draw("{% crispy form %}", form=form)

        assert "input-lg" in named(soup, "first")
        assert "input-lg" in named(soup, "second")
        assert "input-sm" in named(soup, "third")

    def test_a_field_after_a_choice_in_the_same_layout_is_not_affected(self, draw):
        form = structured(Choice("first", size="lg", color="accent"), "second")

        soup = draw("{% crispy form %}", form=form)

        assert named(soup, "second") == classes(
            draw("{% crispy form %}", form=structured("first", "second")).find(
                id="id_second"
            )
        )

    def test_the_developers_own_classes_are_kept(self, draw):
        form = DeveloperAttrsForm()
        form.helper = FormHelper(form)
        form.helper.layout = Layout(Choice("name", size="lg"))

        name = draw("{% crispy form %}", form=form).find(id="id_name")

        assert {"wide", "input", "input-lg"} <= classes(name)

    def test_a_choice_stating_nothing_draws_what_no_choice_draws(self, draw):
        plain = draw("{% crispy form %}", form=structured("first", "second"))
        chosen = draw("{% crispy form %}", form=structured(Choice("first"), "second"))

        assert str(chosen) == str(plain)

    def test_the_context_holds_no_choice_after_the_layout_is_drawn(self, draw):
        form = structured(Choice("first", size="lg"), "second")
        context = Context({"csrf_token": "token", "form": form})

        Template("{% load crispy_forms_tags %}{% crispy form %}").render(context)

        assert Choice.context_name not in context


BUTTONS = [
    pytest.param(
        lambda **options: Submit("act", "Go", css_id="act", **options), id="submit"
    ),
    pytest.param(
        lambda **options: Reset("act", "Go", css_id="act", **options), id="reset"
    ),
    pytest.param(
        lambda **options: Button("act", "Go", css_id="act", **options), id="button"
    ),
    pytest.param(
        lambda **options: StrictButton("Go", css_id="act", **options),
        id="strict button",
    ),
]


def button_of(soup, name="act"):
    return classes(soup.find(id=name))


class TestButtonChoices:
    @pytest.mark.parametrize("make", BUTTONS)
    def test_every_button_carries_the_forms_size(self, draw, make):
        form = structured("first", make(), size="lg")

        soup = draw("{% crispy form %}", form=form)

        assert "btn-lg" in button_of(soup)

    @pytest.mark.parametrize("make", BUTTONS)
    def test_every_button_carries_the_button_colour_and_variant_and_no_input_does(
        self, draw, make
    ):
        form = structured(
            "first", make(), button_color="accent", button_variant="outline"
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"btn-accent", "btn-outline"} <= button_of(soup)
        assert not {"input-accent", "input-outline", "input-ghost"} & named(
            soup, "first"
        )

    @pytest.mark.parametrize("make", BUTTONS)
    def test_the_colour_and_variant_for_inputs_reach_no_button(self, draw, make):
        form = structured("first", make(), color="accent", variant="ghost")

        soup = draw("{% crispy form %}", form=form)

        assert {"input-accent", "input-ghost"} <= named(soup, "first")
        assert not {"btn-accent", "btn-ghost"} & button_of(soup)

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_button_in_a_choice_takes_its_own_and_the_others_the_forms(
        self, draw, make
    ):
        other = StrictButton("Other", css_id="other")
        form = structured(
            Choice(make(), color="error"),
            other,
            button_color="accent",
            button_variant="outline",
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"btn-error", "btn-outline"} <= button_of(soup)
        assert "btn-accent" not in button_of(soup)
        assert {"btn-accent", "btn-outline"} <= button_of(soup, "other")
        assert "btn-error" not in button_of(soup, "other")

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_choice_stating_none_undoes_the_forms_button_colour(self, draw, make):
        form = structured(Choice(make(), color=None), button_color="accent")

        soup = draw("{% crispy form %}", form=form)

        assert "btn-accent" not in button_of(soup)

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_choice_around_a_row_reaches_the_buttons_in_it(self, draw, make):
        form = structured(Choice(Row(Column(make())), size="xl"), size="sm")

        soup = draw("{% crispy form %}", form=form)

        assert "btn-xl" in button_of(soup)

    def test_a_submit_given_a_colour_is_drawn_without_the_default_colour(self, draw):
        form = structured(Submit("act", "Go", css_id="act"), button_color="error")

        soup = draw("{% crispy form %}", form=form)

        assert "btn-error" in button_of(soup)
        assert "btn-primary" not in button_of(soup)

    def test_a_submit_given_the_default_colour_is_drawn_with_it_once(self, draw):
        form = structured(Submit("act", "Go", css_id="act"), button_color="primary")

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id="act")["class"].count("btn-primary") == 1

    def test_a_submit_given_btn_primary_as_its_own_class_keeps_it(self, draw):
        form = structured(
            Submit("act", "Go", css_id="act", css_class="btn-primary"),
            button_color="error",
        )

        soup = draw("{% crispy form %}", form=form)

        assert {"btn-error", "btn-primary"} <= button_of(soup)

    @pytest.mark.parametrize(
        "statement", [{}, {"size": "lg"}, {"button_variant": "soft"}]
    )
    def test_a_submit_given_no_colour_keeps_the_default_colour(self, draw, statement):
        form = structured(Submit("act", "Go", css_id="act"), **statement)

        soup = draw("{% crispy form %}", form=form)

        assert "btn-primary" in button_of(soup)

    @pytest.mark.parametrize("make", BUTTONS)
    def test_the_developers_class_id_and_attributes_are_kept(self, draw, make):
        form = structured(
            make(css_class="mine other", data_class="x", title="Act"),
            size="lg",
            button_color="accent",
        )

        soup = draw("{% crispy form %}", form=form)

        button = soup.find(id="act")
        assert {"mine", "other", "btn", "btn-lg", "btn-accent"} <= classes(button)
        assert button["data-class"] == "x"
        assert button["title"] == "Act"

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_button_in_a_form_stating_nothing_is_drawn_as_it_was(self, draw, make):
        plain = structured("first", make(css_class="mine", title="Act"))
        stating_nothing = structured(
            "first", make(css_class="mine", title="Act"), size=None
        )

        assert str(draw("{% crispy form %}", form=stating_nothing)) == str(
            draw("{% crispy form %}", form=plain)
        )

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_button_in_a_form_with_no_statement_at_all_is_drawn_as_it_was(
        self, draw, make
    ):
        without = StructureForm(layout=("first", make()))
        stating_nothing = structured("first", make())

        assert str(draw("{% crispy form %}", form=stating_nothing)) == str(
            draw("{% crispy form %}", form=without)
        )

    def test_a_hidden_input_is_unchanged(self, draw):
        stated = structured(
            Hidden("secret", "x"),
            size="lg",
            button_color="accent",
            button_variant="outline",
        )
        plain = structured(Hidden("secret", "x"))

        assert str(draw("{% crispy form %}", form=stated)) == str(
            draw("{% crispy form %}", form=plain)
        )

    @pytest.mark.parametrize("make", BUTTONS[:3])
    def test_a_button_added_to_the_helper_takes_the_forms_choices(self, draw, make):
        form = ButtonedForm(buttons=(make(),))
        form.helper.daisyui = FormChoices(size="lg", button_color="accent")

        soup = draw("{% crispy form %}", form=form)

        assert {"btn-lg", "btn-accent"} <= button_of(soup)

    def test_a_strict_button_added_to_the_helper_takes_the_forms_choices(self, draw):
        form = ButtonedForm(buttons=(StrictButton("Go", css_id="act"),))
        form.helper.daisyui = FormChoices(size="lg", button_variant="soft")

        soup = draw("{% crispy form %}", form=form)

        assert {"btn-lg", "btn-soft"} <= button_of(soup)

    def test_a_hidden_input_added_to_the_helper_is_unchanged(self, draw):
        form = ButtonedForm(buttons=(Hidden("secret", "x"),))
        form.helper.daisyui = FormChoices(size="lg", button_color="accent")

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("input", attrs={"name": "secret"}).get("class") is None

    @pytest.mark.parametrize("make", BUTTONS)
    def test_a_page_that_names_its_form_otherwise_still_gets_the_choices(
        self, draw, make
    ):
        form = structured("first", make(), size="lg", button_color="accent")

        soup = draw("{% crispy settings_form %}", settings_form=form)

        assert {"btn-lg", "btn-accent"} <= button_of(soup)
        assert "input-lg" in named(soup, "first")

    def test_a_page_variable_named_daisyui_that_is_not_a_statement_is_ignored(
        self, draw
    ):
        form = structured(Submit("act", "Go", css_id="act"), size="lg")

        soup = draw("{% crispy form %}", form=form, **{"daisyui": "the page's own"})

        assert "btn-lg" in button_of(soup)
