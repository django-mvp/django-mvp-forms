"""A boolean field drawn as a checkbox, a toggle or a switch, through crispy-forms."""

import pytest
from crispy_forms.layout import Submit
from django.http import QueryDict

from mvp_forms.choices import Choice, FormChoices, InvalidChoice
from tests.forms import (
    DrawnBooleanLineFormSet,
    DrawnBooleansForm,
    KeptBooleansForm,
    RequiredDrawnBooleanForm,
    formset_helper,
)

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]
TAG = "{% crispy form %}"
NAMES = ("remember", "notify", "publish")
DRAWINGS = ["checkbox", "toggle", "switch"]
TABLE = "daisyui/table_inline_formset.html"
TOGGLES = ["toggle", "switch"]
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
ERROR_MODIFIERS = {
    "checkbox": "checkbox-error",
    "toggle": "toggle-error",
    "switch": "toggle-error",
}


def stating(**drawings):
    return FormChoices(
        fields={name: Choice(drawing=drawing) for name, drawing in drawings.items()}
    )


def submitted(soup, on):
    data = QueryDict(mutable=True)
    for tag in soup.find_all("input"):
        name = tag.get("name")
        if not name:
            continue
        if tag["type"] == "checkbox":
            if name in on:
                data[name] = tag.get("value", "on")
        else:
            data[name] = tag.get("value", "")
    return data


def refused(draw, source, form):
    with pytest.raises(InvalidChoice) as caught:
        draw(source, form=form)
    return caught.value


def classes_of(soup, name):
    return set(soup.find(id=f"id_{name}")["class"])


class TestDrawings:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_with_no_drawing_stated_is_drawn_as_a_checkbox(self, draw, source):
        soup = draw(source, form=DrawnBooleansForm())

        for name in NAMES:
            tag = soup.find(id=f"id_{name}")
            assert "checkbox" in tag["class"]
            assert "toggle" not in tag["class"]
            assert not tag.has_attr("role")

    @pytest.mark.parametrize("source", SOURCES)
    def test_checkbox_stated_draws_the_markup_that_stating_nothing_draws(
        self, draw, source
    ):
        plain = draw(source, form=DrawnBooleansForm())

        stated = draw(
            source,
            form=DrawnBooleansForm(
                choices=stating(remember="checkbox", notify="checkbox")
            ),
        )

        assert str(stated) == str(plain)

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_toggle_has_the_toggle_class_and_no_role(self, draw, source):
        form = DrawnBooleansForm(choices=stating(notify="toggle"))

        tag = draw(source, form=form).find(id="id_notify")

        assert "toggle" in tag["class"]
        assert "checkbox" not in tag["class"]
        assert "w-full" not in tag["class"]
        assert not tag.has_attr("role")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_switch_has_the_toggle_class_and_the_switch_role(self, draw, source):
        form = DrawnBooleansForm(choices=stating(publish="switch"))

        tag = draw(source, form=form).find(id="id_publish")

        assert "toggle" in tag["class"]
        assert "checkbox" not in tag["class"]
        assert tag["role"] == "switch"

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize(
        ("on", "off"), [("notify", "publish"), ("publish", "notify")]
    )
    def test_a_form_posted_with_one_on_and_one_off_cleans_as_checkboxes_do(
        self, draw, source, on, off
    ):
        choices = stating(notify="toggle", publish="switch")
        soup = draw(source, form=DrawnBooleansForm(choices=choices))

        form = DrawnBooleansForm(submitted(soup, {on}), choices=choices)

        assert form.is_valid()
        assert form.cleaned_data[on] is True
        assert form.cleaned_data[off] is False
        assert form.cleaned_data["remember"] is False

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_bound_true_is_drawn_checked_and_a_bound_false_is_not(
        self, draw, source, drawing
    ):
        choices = stating(remember=drawing, notify=drawing)

        soup = draw(
            source,
            form=DrawnBooleansForm({"remember": "on"}, choices=choices),
        )

        assert soup.find(id="id_remember").has_attr("checked")
        assert not soup.find(id="id_notify").has_attr("checked")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_an_initial_true_is_drawn_checked(self, draw, source, drawing):
        form = DrawnBooleansForm(
            initial={"notify": True}, choices=stating(notify=drawing)
        )

        assert draw(source, form=form).find(id="id_notify").has_attr("checked")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_the_input_is_a_checkbox_input_with_the_fields_name_and_no_script(
        self, draw, source, drawing
    ):
        form = DrawnBooleansForm(choices=stating(notify=drawing))

        soup = draw(source, form=form)

        tag = soup.find(id="id_notify")
        assert (tag.name, tag["type"], tag["name"]) == ("input", "checkbox", "notify")
        assert soup.find("script") is None

    @pytest.mark.parametrize("source", SOURCES)
    def test_only_the_field_stated_changes(self, draw, source):
        plain = draw(source, form=DrawnBooleansForm())

        soup = draw(source, form=DrawnBooleansForm(choices=stating(notify="switch")))

        assert classes_of(soup, "notify") != classes_of(plain, "notify")
        for name in ("remember", "publish", "title"):
            assert str(soup.find(id=f"div_id_{name}")) == str(
                plain.find(id=f"div_id_{name}")
            )

    def test_a_drawing_in_a_layout_changes_only_the_fields_it_holds(self, draw):
        form = DrawnBooleansForm(
            layout=["remember", Choice("notify", drawing="toggle"), "publish"]
        )

        soup = draw(TAG, form=form)

        assert "toggle" in classes_of(soup, "notify")
        assert "checkbox" in classes_of(soup, "remember")
        assert "checkbox" in classes_of(soup, "publish")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", ["toggle", "switch"])
    def test_a_field_in_error_drawn_as_a_toggle_keeps_the_error_modifier(
        self, draw, source, drawing
    ):
        form = RequiredDrawnBooleanForm({}, choices=stating(agree=drawing))

        tag = draw(source, form=form).find(id="id_agree")

        assert "toggle" in tag["class"]
        assert "toggle-error" in tag["class"]
        assert tag["aria-invalid"] == "true"


def stating_all(drawing):
    return stating(agree=drawing, news=drawing, locked=drawing)


class TestDrawingKeepsWhatACheckboxHas:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_the_label_is_tied_to_the_input_and_holds_it(self, draw, source, drawing):
        form = KeptBooleansForm(choices=stating_all(drawing))

        soup = draw(source, form=form)

        tag = soup.find(id="id_agree")
        label = soup.find("label", attrs={"for": tag["id"]})
        assert label.find("input") is tag
        assert len(soup.find(id="div_id_agree").find_all("label")) == 1

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_the_input_is_described_by_the_help_text(self, draw, source, drawing):
        form = KeptBooleansForm(choices=stating_all(drawing))

        soup = draw(source, form=form)

        tag = soup.find(id="id_agree")
        assert tag["aria-describedby"].split() == ["id_agree_helptext"]
        assert len(soup.find_all(id="id_agree_helptext")) == 1
        assert not soup.find(id="id_news").has_attr("aria-describedby")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_required_field_left_off_is_invalid_and_described_by_its_error(
        self, draw, source, drawing
    ):
        form = KeptBooleansForm({}, choices=stating_all(drawing))

        soup = draw(source, form=form)

        tag = soup.find(id="id_agree")
        assert tag["aria-invalid"] == "true"
        assert ERROR_MODIFIERS[drawing] in tag["class"]
        assert "id_agree_error" in tag["aria-describedby"].split()
        assert soup.find(id="id_agree_error") is not None

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_field_that_is_not_in_error_carries_no_error_modifier(
        self, draw, source, drawing
    ):
        form = KeptBooleansForm({"agree": "on"}, choices=stating_all(drawing))

        tag = draw(source, form=form).find(id="id_agree")

        assert ERROR_MODIFIERS[drawing] not in tag["class"]
        assert not tag.has_attr("aria-invalid")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_the_required_marker_is_in_the_label_of_a_required_field_only(
        self, draw, source, drawing
    ):
        form = KeptBooleansForm(choices=stating_all(drawing))

        soup = draw(source, form=form)

        required = soup.find("label", attrs={"for": "id_agree"})
        optional = soup.find("label", attrs={"for": "id_news"})
        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_disabled_field_is_disabled(self, draw, source, drawing):
        form = KeptBooleansForm(choices=stating_all(drawing))

        soup = draw(source, form=form)

        assert soup.find(id="id_locked").has_attr("disabled")
        assert not soup.find(id="id_news").has_attr("disabled")

    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_with_labels_off_the_input_is_named_by_aria_label(self, draw, drawing):
        form = KeptBooleansForm(choices=stating_all(drawing), show_labels=False)

        soup = draw(TAG, form=form)

        frame = soup.find(id="div_id_agree")
        assert frame.find("label") is None
        assert frame.find("input")["aria-label"] == form["agree"].label


class TestDrawingSizeAndColour:
    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_the_forms_size_is_taken(self, draw, source, drawing):
        choices = FormChoices(size="sm", fields={"notify": Choice(drawing=drawing)})

        soup = draw(source, form=DrawnBooleansForm(choices=choices))

        assert "toggle-sm" in classes_of(soup, "notify")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_the_forms_colour_is_taken(self, draw, source, drawing):
        choices = FormChoices(
            color="primary", fields={"notify": Choice(drawing=drawing)}
        )

        soup = draw(source, form=DrawnBooleansForm(choices=choices))

        assert "toggle-primary" in classes_of(soup, "notify")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_the_fields_own_size_and_colour_win_when_stated_by_name(
        self, draw, source, drawing
    ):
        choices = FormChoices(
            size="sm",
            color="primary",
            fields={"notify": Choice(drawing=drawing, size="lg", color="accent")},
        )

        classes = classes_of(
            draw(source, form=DrawnBooleansForm(choices=choices)), "notify"
        )

        assert {"toggle-lg", "toggle-accent"} <= classes
        assert not {"toggle-sm", "toggle-primary"} & classes

    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_the_fields_own_size_and_colour_win_when_stated_in_the_layout(
        self, draw, drawing
    ):
        form = DrawnBooleansForm(
            layout=[
                "remember",
                Choice("notify", drawing=drawing, size="xl", color="error"),
            ],
            choices=FormChoices(size="sm", color="primary"),
        )

        soup = draw(TAG, form=form)

        assert {"toggle-xl", "toggle-error"} <= classes_of(soup, "notify")
        assert {"checkbox-sm", "checkbox-primary"} <= classes_of(soup, "remember")

    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_a_drawing_a_size_and_a_colour_stated_together_all_take_effect(
        self, draw, drawing
    ):
        form = DrawnBooleansForm(
            layout=[Choice("notify", drawing=drawing, size="xs", color="success")]
        )

        tag = draw(TAG, form=form).find(id="id_notify")

        assert {"toggle", "toggle-xs", "toggle-success"} <= set(tag["class"])
        assert tag.get("role") == ("switch" if drawing == "switch" else None)

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_with_nothing_stated_no_size_or_colour_is_written(
        self, draw, source, drawing
    ):
        choices = stating(notify=drawing)

        classes = classes_of(
            draw(source, form=DrawnBooleansForm(choices=choices)), "notify"
        )

        assert "toggle" in classes
        assert not {name for name in classes if name.startswith("toggle-")}

    @pytest.mark.parametrize("size", SIZES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_every_size_is_written_as_its_toggle_class(self, draw, drawing, size):
        choices = FormChoices(size=size, fields={"notify": Choice(drawing=drawing)})

        soup = draw(TAG, form=DrawnBooleansForm(choices=choices))

        assert f"toggle-{size}" in classes_of(soup, "notify")

    @pytest.mark.parametrize("color", COLORS)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_every_colour_is_written_as_its_toggle_class(self, draw, drawing, color):
        choices = FormChoices(color=color, fields={"notify": Choice(drawing=drawing)})

        soup = draw(TAG, form=DrawnBooleansForm(choices=choices))

        assert f"toggle-{color}" in classes_of(soup, "notify")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_a_field_in_error_keeps_the_error_modifier_and_drops_the_colour(
        self, draw, source, drawing
    ):
        choices = FormChoices(
            size="sm",
            color="primary",
            fields={
                "agree": Choice(drawing=drawing),
                "notify": Choice(drawing=drawing),
            },
        )

        soup = draw(source, form=RequiredDrawnBooleanForm({}, choices=choices))

        assert {"toggle-error", "toggle-sm"} <= classes_of(soup, "agree")
        assert "toggle-primary" not in classes_of(soup, "agree")
        assert "toggle-primary" in classes_of(soup, "notify")

    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_no_checkbox_modifier_is_written_on_a_toggle(self, draw, drawing):
        choices = FormChoices(
            size="lg",
            color="info",
            fields={
                "agree": Choice(drawing=drawing),
                "notify": Choice(drawing=drawing),
            },
        )

        soup = draw(TAG, form=RequiredDrawnBooleanForm({}, choices=choices))

        for name in ("agree", "notify"):
            assert not {c for c in classes_of(soup, name) if c.startswith("checkbox")}

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_a_variant_the_form_states_is_passed_over(self, draw, source, drawing):
        choices = FormChoices(
            variant="ghost", fields={"notify": Choice(drawing=drawing)}
        )

        classes = classes_of(
            draw(source, form=DrawnBooleansForm(choices=choices)), "notify"
        )

        assert not {name for name in classes if name.startswith("toggle-")}

    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_a_variant_stated_on_the_field_raises(self, draw, drawing):
        form = DrawnBooleansForm(
            layout=[Choice("notify", drawing=drawing, variant="ghost")]
        )

        error = refused(draw, TAG, form)

        assert (error.kind, error.value, error.allowed) == ("variant", "ghost", ())
        assert error.target == "notify"

    @pytest.mark.parametrize("drawing", TOGGLES)
    def test_a_size_the_field_states_that_is_not_one_raises_naming_the_field(
        self, draw, drawing
    ):
        form = DrawnBooleansForm(
            layout=[Choice("notify", drawing=drawing, size="huge")]
        )

        error = refused(draw, TAG, form)

        assert (error.kind, error.value, error.target) == ("size", "huge", "notify")
        assert error.allowed == SIZES


class TestDrawingsInAFormset:
    @pytest.mark.parametrize("template", [None, TABLE], ids=["stacked", "table"])
    @pytest.mark.parametrize(
        ("drawing", "role"), [("toggle", None), ("switch", "switch")]
    )
    def test_every_row_draws_the_field_as_stated_by_name_on_the_helper(
        self, draw, template, drawing, role
    ):
        settings = {} if template is None else {"template": template}
        helper = formset_helper(**settings)
        helper.daisyui = stating(done=drawing)

        soup = draw(
            "{% crispy formset helper %}",
            formset=DrawnBooleanLineFormSet(),
            helper=helper,
        )

        for row in range(3):
            tag = soup.find(id=f"id_form-{row}-done")
            assert "toggle" in tag["class"]
            assert tag.get("role") == role

    def test_every_row_draws_the_field_as_stated_in_the_helpers_layout(self, draw):
        helper = formset_helper("name", Choice("done", drawing="switch"))

        soup = draw(
            "{% crispy formset helper %}",
            formset=DrawnBooleanLineFormSet(),
            helper=helper,
        )

        for row in range(3):
            tag = soup.find(id=f"id_form-{row}-done")
            assert "toggle" in tag["class"]
            assert tag["role"] == "switch"


class TestDrawingMistakes:
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_name_that_is_not_a_drawing_is_refused_naming_the_field(
        self, draw, source
    ):
        error = refused(
            draw, source, DrawnBooleansForm(choices=stating(notify="slider"))
        )

        assert (error.kind, error.value, error.target) == (
            "drawing",
            "slider",
            "notify",
        )
        assert error.allowed == ("checkbox", "toggle", "switch")

    def test_a_name_that_is_not_a_drawing_is_refused_in_a_layout(self, draw):
        form = DrawnBooleansForm(
            layout=["remember", Choice("notify", drawing="slider")]
        )

        error = refused(draw, TAG, form)

        assert (error.kind, error.target) == ("drawing", "notify")

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_drawing_stated_for_a_field_that_is_not_a_boolean_field_is_refused(
        self, draw, source, drawing
    ):
        error = refused(draw, source, DrawnBooleansForm(choices=stating(title=drawing)))

        assert (error.kind, error.value, error.target) == ("drawing", drawing, "title")
        assert error.allowed == ()

    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_drawing_stated_for_a_text_field_in_a_layout_is_refused(
        self, draw, drawing
    ):
        form = DrawnBooleansForm(layout=[Choice("title", drawing=drawing)])

        error = refused(draw, TAG, form)

        assert (error.kind, error.target, error.allowed) == ("drawing", "title", ())

    @pytest.mark.parametrize("source", SOURCES)
    def test_checkbox_stated_for_a_boolean_field_is_accepted(self, draw, source):
        form = DrawnBooleansForm(choices=stating(notify="checkbox"))

        assert "checkbox" in draw(source, form=form).find(id="id_notify")["class"]

    @pytest.mark.parametrize("source", SOURCES)
    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_hidden_boolean_field_with_a_drawing_stated_is_a_hidden_input(
        self, draw, source, drawing
    ):
        form = DrawnBooleansForm(choices=stating(token=drawing))

        tag = draw(source, form=form).find(id="id_token")

        assert tag["type"] == "hidden"

    @pytest.mark.parametrize("drawing", DRAWINGS)
    def test_a_hidden_boolean_field_in_a_layout_with_a_drawing_stated_is_hidden(
        self, draw, drawing
    ):
        form = DrawnBooleansForm(layout=[Choice("token", drawing=drawing)])

        assert draw(TAG, form=form).find(id="id_token")["type"] == "hidden"

    def test_a_drawing_stated_around_a_button_is_refused(self, draw):
        form = DrawnBooleansForm(
            layout=[Choice("notify", Submit("save", "Save"), drawing="toggle")]
        )

        error = refused(draw, TAG, form)

        assert (error.kind, error.allowed) == ("drawing", ())
