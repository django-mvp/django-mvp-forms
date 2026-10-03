"""The form drawn as a whole: its own errors, its element and the helper's switches."""

import re

import pytest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from tests.forms import (
    DeveloperLabelledForm,
    FieldAndFormWideErrorsForm,
    FormWideErrorsForm,
    FormWideMarkupForm,
    HelpedForm,
    MediaForm,
    TextInputsForm,
    UploadForm,
)

FRAME_ID = "div_"
ALL_SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form|as_crispy_errors }}",
]


def frames_holding(tag):
    return [p for p in tag.parents if p.get("id", "").startswith(FRAME_ID)]


def helped(form):
    form.helper = FormHelper()
    return form


def failing_form(form_class=FormWideErrorsForm):
    return helped(form_class({}))


class TestFormWideErrors:
    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_each_error_is_drawn_once_inside_one_alert(self, draw, source):
        form = FormWideErrorsForm({})

        soup = draw(source, form=form)

        alerts = soup.find_all(attrs={"role": "alert"})
        assert len(alerts) == 1
        drawn = [p.get_text(strip=True) for p in alerts[0]("p")]
        assert drawn == list(form.non_field_errors())

    @pytest.mark.parametrize("source", ["{{ form|crispy }}", "{% crispy form %}"])
    def test_the_alert_is_outside_every_field_frame(self, draw, source):
        soup = draw(source, form=FormWideErrorsForm({}))

        alert = soup.find(attrs={"role": "alert"})

        assert frames_holding(alert) == []
        assert soup.find(id=FRAME_ID + "id_name") is not None

    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_a_form_without_form_wide_errors_draws_no_alert(self, draw, source):
        soup = draw(source, form=TextInputsForm())

        assert soup.find(attrs={"role": "alert"}) is None

    def test_a_laid_out_form_draws_its_alert_once_outside_the_frame(self, draw):
        form = failing_form()
        form.helper.layout = Layout("name")

        soup = draw("{% crispy form %}", form=form)

        alerts = soup.find_all(attrs={"role": "alert"})
        assert len(alerts) == 1
        assert frames_holding(alerts[0]) == []
        assert soup.find(id=FRAME_ID + "id_name") is not None

    def test_a_field_error_is_not_a_form_wide_error(self, draw):
        soup = draw("{{ form|as_crispy_errors }}", form=TextInputsForm({}))

        assert soup.find(attrs={"role": "alert"}) is None

    def test_markup_in_a_form_wide_error_is_escaped(self, draw):
        soup = draw("{{ form|crispy }}", form=FormWideMarkupForm({}))

        assert soup.find(attrs={"role": "alert"}).find("script") is None

    def test_a_helpers_error_title_is_drawn_inside_the_alert_escaped(self, draw):
        form = failing_form()
        form.helper.form_error_title = "<i>Title</i>"

        soup = draw("{% crispy form %}", form=form)

        alert = soup.find(attrs={"role": "alert"})
        assert alert.find("i") is None
        assert "<i>Title</i>" in alert.get_text()


class TestMedia:
    @pytest.mark.parametrize("layout", [None, Layout("name")])
    def test_the_forms_media_is_drawn_once_through_the_tag(self, draw, layout):
        form = MediaForm()
        form.helper = FormHelper()
        form.helper.layout = layout

        soup = draw("{% crispy form %}", form=form)

        assert len(soup.find_all("script", src=re.compile(r"tests/media\.js"))) == 1

    def test_a_helper_can_leave_the_media_out(self, draw):
        form = MediaForm()
        form.helper = FormHelper()
        form.helper.include_media = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("script") is None


class TestFormElement:
    def test_a_form_with_no_helper_settings_is_wrapped_with_a_token(self, draw):
        soup = draw("{% crispy form %}", form=TextInputsForm())

        form = soup.find("form")

        assert form["method"] == "post"
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) is not None
        assert form.find(id="id_text") is not None

    def test_the_helpers_method_action_id_class_and_attributes_are_on_the_element(
        self, draw
    ):
        form = helped(TextInputsForm())
        form.helper.form_method = "get"
        form.helper.form_action = "/search/"
        form.helper.form_id = "the-form"
        form.helper.form_class = "mine"
        form.helper.attrs = {"data-extra": "yes"}

        drawn = draw("{% crispy form %}", form=form).find("form")

        assert drawn["method"] == "get"
        assert drawn["action"] == "/search/"
        assert drawn["id"] == "the-form"
        assert drawn["class"] == ["mine"]
        assert drawn["data-extra"] == "yes"

    def test_a_get_form_has_no_token(self, draw):
        form = helped(TextInputsForm())
        form.helper.form_method = "get"

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("input", attrs={"name": "csrfmiddlewaretoken"}) is None

    def test_disabling_the_token_leaves_the_form_element(self, draw):
        form = helped(TextInputsForm())
        form.helper.disable_csrf = True

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("form") is not None
        assert soup.find("input", attrs={"name": "csrfmiddlewaretoken"}) is None

    def test_a_form_with_a_file_field_is_multipart(self, draw):
        soup = draw("{% crispy form %}", form=UploadForm())

        assert soup.find("form")["enctype"] == "multipart/form-data"

    def test_a_form_without_a_file_field_is_not_multipart(self, draw):
        soup = draw("{% crispy form %}", form=TextInputsForm())

        assert not soup.find("form").has_attr("enctype")

    def test_turning_the_form_tag_off_leaves_the_fields_alone(self, draw):
        form = helped(TextInputsForm())
        form.helper.form_tag = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("form") is None
        assert soup.find(id="id_text") is not None


class TestHelperSwitches:
    def test_labels_off_leaves_no_label_and_names_each_input(self, draw):
        form = helped(TextInputsForm())
        form.helper.form_show_labels = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find("label") is None
        inputs = soup.find_all(["input", "textarea"], id=True)
        assert len(inputs) == len(TextInputsForm.base_fields)
        assert all(tag["aria-label"] for tag in inputs)

    def test_labels_off_never_replaces_a_label_the_developer_wrote(self, draw):
        form = helped(DeveloperLabelledForm())
        form.helper.form_show_labels = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id="id_name")["aria-label"] == "Mine"

    def test_errors_off_draws_no_field_error_and_no_form_wide_error(self, draw):
        form = helped(FieldAndFormWideErrorsForm({}))
        form.helper.form_show_errors = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(attrs={"role": "alert"}) is None
        assert soup.find(id=re.compile(r"_error$")) is None
        inputs = soup.find_all("input", id=True)
        assert len(inputs) == len(HelpedForm.base_fields)
        assert all("input-error" not in tag["class"] for tag in inputs)

    @pytest.mark.parametrize(
        ("name", "described"),
        [("helped", ["id_helped_helptext"]), ("bare", [])],
    )
    def test_errors_off_leaves_no_description_naming_a_missing_element(
        self, draw, name, described
    ):
        form = helped(HelpedForm({}))
        form.helper.form_show_errors = False

        soup = draw("{% crispy form %}", form=form)

        drawn = soup.find(id=f"id_{name}").get("aria-describedby", "").split()
        assert drawn == described
        assert all(soup.find(id=referenced) is not None for referenced in drawn)

    def test_label_class_and_field_class_reach_every_label_and_holder(self, draw):
        form = helped(TextInputsForm())
        form.helper.label_class = "mine-label"
        form.helper.field_class = "mine-holder"

        soup = draw("{% crispy form %}", form=form)

        labels = soup.find_all("label")
        assert len(labels) == len(TextInputsForm.base_fields)
        assert all("mine-label" in label["class"] for label in labels)
        for name in TextInputsForm.base_fields:
            assert "mine-holder" in soup.find(id=f"id_{name}").parent["class"]

    def test_without_the_classes_no_holder_is_drawn(self, draw):
        soup = draw("{% crispy form %}", form=helped(TextInputsForm()))

        frame = soup.find(id="div_id_text")

        assert frame.find(id="id_text").parent is frame

    def test_the_inline_settings_change_nothing(self, draw):
        plain = helped(HelpedForm({}))
        inline = helped(HelpedForm({}))
        inline.helper.help_text_inline = True
        inline.helper.error_text_inline = False

        assert str(draw("{% crispy form %}", form=inline)) == str(
            draw("{% crispy form %}", form=plain)
        )
