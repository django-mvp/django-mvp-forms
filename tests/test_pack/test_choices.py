"""Size, colour and variant stated for a whole form, drawn through crispy-forms."""

import re

import pytest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Row
from django.core.files.uploadedfile import SimpleUploadedFile

from mvp_forms.choices import FormChoices
from tests.forms import DeveloperAttrsForm, EveryInputForm, FilesForm

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
