"""Hidden inputs: drawn bare, and their errors drawn with the form-wide errors."""

import pytest
from crispy_forms.helper import FormHelper

from tests.forms import (
    DisabledHiddenForm,
    HiddenAndFormWideErrorsForm,
    HiddenErrorForm,
    HiddenInputsForm,
    HiddenOnlyForm,
    SplitHiddenForm,
)

FRAME_ID = "div_"
ALL_SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form|as_crispy_errors }}",
]
DRAWN_SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]


def helped(form):
    form.helper = FormHelper()
    return form


def refused(form_class=HiddenErrorForm):
    return form_class({"token": "bad", "ids": ["1"], "name": "x"})


class TestHiddenInputs:
    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_hidden_field_is_an_input_holding_its_value(self, draw, source):
        soup = draw(source, form=helped(HiddenInputsForm()))

        token = soup.find(id="id_token")
        assert token["type"] == "hidden"
        assert token["value"] == "abc"

    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_hidden_field_has_no_frame_label_help_or_error_element(
        self, draw, source
    ):
        soup = draw(source, form=helped(refused()))

        assert soup.find(id=FRAME_ID + "id_token") is None
        assert soup.find(id=FRAME_ID + "id_ids") is None
        assert soup.find("label", attrs={"for": "id_token"}) is None
        assert soup.find(id="id_token_helptext") is None
        assert soup.find(id="id_token_error") is None
        assert soup.find(id="id_ids_error") is None

    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_multiple_hidden_input_draws_one_input_per_value(self, draw, source):
        soup = draw(source, form=helped(HiddenInputsForm()))

        inputs = soup.find_all("input", attrs={"name": "ids"})
        assert [i["type"] for i in inputs] == ["hidden", "hidden"]
        assert [i["value"] for i in inputs] == ["1", "2"]

    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_form_of_only_hidden_fields_draws_no_frame(self, draw, source):
        soup = draw(source, form=helped(HiddenOnlyForm()))

        assert soup.find(id="id_token")["type"] == "hidden"
        assert [t for t in soup.find_all(id=True) if t["id"].startswith(FRAME_ID)] == []
        assert soup.find("label") is None

    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_disabled_hidden_field_is_drawn_as_django_draws_it(self, draw, source):
        soup = draw(source, form=helped(DisabledHiddenForm()))

        token = soup.find(id="id_token")
        assert token["type"] == "hidden"
        assert token.has_attr("disabled")

    @pytest.mark.parametrize("source", DRAWN_SOURCES)
    def test_a_split_hidden_date_time_is_two_hidden_inputs_and_no_frame(
        self, draw, source
    ):
        soup = draw(source, form=helped(SplitHiddenForm()))

        inputs = soup.find_all("input", attrs={"name": ["moment_0", "moment_1"]})
        assert [i["type"] for i in inputs] == ["hidden", "hidden"]
        assert soup.find(id=FRAME_ID + "id_moment_0") is None
        assert soup.find("label") is None


class TestHiddenFieldErrors:
    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_the_alert_holds_one_message_naming_the_field_and_its_error(
        self, draw, source
    ):
        form = refused()

        soup = draw(source, form=form)

        alerts = soup.find_all(attrs={"role": "alert"})
        assert len(alerts) == 1
        messages = alerts[0]("p")
        assert len(messages) == 1
        assert "token" in messages[0].get_text()
        assert "<b>Refused</b> bad" in messages[0].get_text()

    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_the_alert_is_drawn_when_no_other_form_wide_error_exists(
        self, draw, source
    ):
        form = refused()
        assert list(form.non_field_errors()) == []

        soup = draw(source, form=form)

        assert soup.find(attrs={"role": "alert"}) is not None

    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_a_form_wide_error_and_a_hidden_error_share_the_one_alert(
        self, draw, source
    ):
        soup = draw(source, form=refused(HiddenAndFormWideErrorsForm))

        alerts = soup.find_all(attrs={"role": "alert"})
        assert len(alerts) == 1
        assert len(alerts[0]("p")) == 2

    @pytest.mark.parametrize("source", ALL_SOURCES)
    def test_markup_in_a_hidden_fields_error_is_escaped(self, draw, source):
        soup = draw(source, form=refused())

        assert soup.find(attrs={"role": "alert"}).find("b") is None

    @pytest.mark.parametrize("source", ["{{ form|crispy }}", "{% crispy form %}"])
    def test_a_valid_hidden_field_draws_no_alert(self, draw, source):
        soup = draw(
            source,
            form=helped(HiddenInputsForm({"token": "a", "ids": ["1"], "name": "x"})),
        )

        assert soup.find(attrs={"role": "alert"}) is None

    def test_with_errors_off_no_alert_is_drawn(self, draw):
        form = helped(refused())
        form.helper.form_show_errors = False

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(attrs={"role": "alert"}) is None
