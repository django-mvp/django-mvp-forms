"""The form drawn as a whole: its own errors, its element and the helper's switches."""

import re

import pytest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from tests.forms import (
    FormWideErrorsForm,
    FormWideMarkupForm,
    MediaForm,
    TextInputsForm,
)

FRAME_ID = "div_"
ALL_SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form|as_crispy_errors }}",
]


def frames_holding(tag):
    return [p for p in tag.parents if p.get("id", "").startswith(FRAME_ID)]


def failing_form(form_class=FormWideErrorsForm):
    form = form_class({})
    form.helper = FormHelper()
    return form


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
