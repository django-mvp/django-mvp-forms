"""One field drawn disabled with its value, by UneditableField."""

import pytest
from crispy_forms.bootstrap import UneditableField
from crispy_forms.layout import Field

from tests.forms import UneditableFieldsForm


def build_form(*layout, data=None):
    return UneditableFieldsForm(data, layout=layout)


def draw_form(draw, *layout, data=None):
    return draw("{% crispy form %}", form=build_form(*layout, data=data))


def frame_of(soup, name="account"):
    return soup.find(id=f"div_id_{name}")


class TestUneditableFieldDrawn:
    def test_the_input_shows_the_value_is_disabled_and_keeps_its_component(self, draw):
        soup = draw_form(draw, UneditableField("account"))

        field = soup.find(id="id_account")

        assert field["value"] == "AC-1001"
        assert field.has_attr("disabled")
        assert "input" in field["class"]

    def test_the_label_and_help_text_are_drawn_and_tied_to_the_input(self, draw):
        soup = draw_form(draw, UneditableField("account"))

        frame = frame_of(soup)
        field = frame.find(id="id_account")

        assert len(frame.find_all("label", attrs={"for": "id_account"})) == 1
        assert len(frame.find_all(id="id_account_helptext")) == 1
        assert "id_account_helptext" in field["aria-describedby"].split()

    def test_a_field_with_no_value_is_empty_and_disabled_without_error(self, draw):
        soup = draw_form(draw, UneditableField("empty"))

        field = soup.find(id="id_empty")

        assert not field.get("value")
        assert field.has_attr("disabled")
        assert frame_of(soup, "empty").find(id="id_empty_error") is None

    def test_a_value_holding_markup_is_escaped(self, draw):
        soup = draw_form(draw, UneditableField("markup"))

        field = soup.find(id="id_markup")

        assert field["value"] == '<b onclick="x()">&amp;</b>'
        assert frame_of(soup, "markup").find("b") is None

    def test_a_select_is_disabled_and_shows_its_value(self, draw):
        soup = draw_form(draw, UneditableField("country"))

        field = soup.find(id="id_country")

        assert field.has_attr("disabled")
        assert [
            option["value"] for option in field.find_all("option", selected=True)
        ] == ["b"]

    def test_a_single_checkbox_is_disabled_and_stays_checked(self, draw):
        soup = draw_form(draw, UneditableField("agree"))

        field = soup.find(id="id_agree")

        assert field.has_attr("disabled")
        assert field.has_attr("checked")

    @pytest.mark.parametrize(
        ("name", "kind", "checked"),
        [("pick", "radio", "b"), ("boxes", "checkbox", "a")],
    )
    def test_every_option_of_a_group_is_disabled(self, draw, name, kind, checked):
        soup = draw_form(draw, UneditableField(name))

        options = frame_of(soup, name).find_all("input", attrs={"type": kind})

        assert len(options) == 2
        assert all(option.has_attr("disabled") for option in options)
        assert [
            option["value"] for option in options if option.has_attr("checked")
        ] == [checked]

    def test_a_textarea_is_disabled_and_shows_its_value(self, draw):
        soup = draw_form(draw, UneditableField("notes"))

        field = soup.find(id="id_notes")

        assert field.has_attr("disabled")
        assert field.get_text().strip() == "Hello"

    def test_a_field_not_wrapped_is_not_disabled(self, draw):
        soup = draw_form(draw, "account")

        assert not soup.find(id="id_account").has_attr("disabled")


class TestUneditableFieldClasses:
    def test_the_class_crispy_writes_for_other_packs_is_not_drawn(self, draw):
        soup = draw_form(draw, UneditableField("account"))

        written = {name for tag in soup.find_all(class_=True) for name in tag["class"]}

        assert "uneditable-input" not in written

    def test_a_class_of_the_developers_is_drawn_beside_the_component(self, draw):
        soup = draw_form(draw, UneditableField("account", css_class="mine"))

        field = soup.find(id="id_account")

        assert "mine" in field["class"]
        assert "input" in field["class"]

    def test_a_class_named_active_on_an_input_is_still_drawn(self, draw):
        soup = draw_form(draw, Field("account", css_class="active"))

        assert "active" in soup.find(id="id_account")["class"]

    def test_a_wrapper_class_reaches_the_frames_outer_element(self, draw):
        soup = draw_form(draw, UneditableField("account", wrapper_class="mine"))

        assert "mine" in frame_of(soup)["class"]

    def test_a_template_of_the_developers_draws_the_field(self, draw):
        soup = draw_form(
            draw, UneditableField("account", template="tests/own_container.html")
        )

        assert soup.find("section", id="own-container") is not None
        assert frame_of(soup) is None


class TestUneditableFieldLeavesTheFormAlone:
    def test_the_form_field_and_its_widget_are_not_disabled_by_the_pack(self, draw):
        form = build_form(UneditableField("account"))

        draw("{% crispy form %}", form=form)

        assert form.fields["account"].disabled is False
        assert "disabled" not in form.fields["account"].widget.attrs


class TestUneditableFieldSubmitted:
    def test_a_field_declared_disabled_keeps_its_initial_value(self, draw, posted):
        soup = draw_form(draw, UneditableField("locked"))
        form = build_form(UneditableField("locked"), data=posted(soup))

        assert "locked" not in form.errors
        assert form.cleaned_data["locked"] == "Ada"

    def test_a_required_field_not_declared_disabled_fails_when_left_out(
        self, draw, posted
    ):
        soup = draw_form(draw, UneditableField("kept"))
        form = build_form(UneditableField("kept"), data=posted(soup))

        form.is_valid()

        assert [error.code for error in form.errors.as_data()["kept"]] == ["required"]
