"""The layout object that places a notice between the fields of a form."""

from crispy_forms.bootstrap import Alert

DEVELOPER_ATTRS = {"data-role": "notice", "lang": "en"}
FORM_CONTROLS = {"first", "second", "csrfmiddlewaretoken"}


def alerts(soup):
    return soup.find_all(attrs={"role": "alert"})


class TestAlert:
    def test_it_draws_one_alert_between_the_two_fields_around_it(self, draw_layout):
        soup = draw_layout("first", Alert("Mind this", css_id="note"), "second")

        alert = soup.find(id="note")
        assert alert["role"] == "alert"
        assert "alert" in alert["class"]
        assert alert.find_previous("input", id="id_first") is not None
        assert alert.find_next("input", id="id_second") is not None
        assert alert.find_previous("input", id="id_second") is None
        assert alert.find_next("input", id="id_first") is None

    def test_it_is_drawn_again_when_the_form_is_bound(self, draw_layout):
        soup = draw_layout("first", Alert("Mind this", css_id="note"), bound=True)

        assert [alert["id"] for alert in alerts(soup) if alert.has_attr("id")] == [
            "note"
        ]

    def test_content_written_with_markup_is_drawn_as_markup(self, draw_layout):
        soup = draw_layout(
            Alert("<strong id='bold'>Warning!</strong> Look <a href='/x'>here</a>")
        )

        alert = alerts(soup)[0]
        assert alert.find("strong", id="bold") is not None
        assert alert.find("a", href="/x") is not None

    def test_it_is_not_given_a_class_for_block(self, draw_layout):
        soup = draw_layout(Alert("Mind this", block=True, css_id="note"))

        assert "alert-block" not in soup.find(id="note")["class"]
        assert "alert" in soup.find(id="note")["class"]


class TestAlertDismissControl:
    def test_it_holds_one_button_that_is_not_a_submit_and_has_a_name(self, draw_layout):
        soup = draw_layout(Alert("Mind this", css_id="note"))

        alert = soup.find(id="note")
        buttons = alert.find_all("button")
        assert [button["type"] for button in buttons] == ["button"]
        assert buttons[0]["aria-label"]
        assert alert.find(attrs={"type": "submit"}) is None

    def test_without_dismiss_it_holds_no_button(self, draw_layout):
        soup = draw_layout(Alert("Mind this", dismiss=False, css_id="note"))

        assert soup.find(id="note").find("button") is None

    def test_two_alerts_each_hold_their_own_dismiss_control(self, draw_layout):
        soup = draw_layout(Alert("One", css_id="one"), Alert("Two", css_id="two"))

        assert [alert["id"] for alert in alerts(soup)] == ["one", "two"]
        for alert in alerts(soup):
            assert len(alert.find_all("button")) == 1

    def test_the_alert_adds_nothing_the_form_would_submit(self, draw_layout):
        soup = draw_layout("first", Alert("Mind this"), "second")

        controls = soup.find_all(["input", "select", "textarea", "button"])
        named = {control["name"] for control in controls if control.has_attr("name")}
        assert named == FORM_CONTROLS
        assert soup.find(attrs={"type": "submit"}) is None


class TestAlertOptions:
    def test_an_extra_class_is_kept_beside_the_alert_class(self, draw_layout):
        soup = draw_layout(Alert("Mind this", css_id="note", css_class="alert-warning"))

        assert {"alert", "alert-warning"} <= set(soup.find(id="note")["class"])

    def test_a_class_written_for_another_pack_is_not_drawn(self, draw_layout):
        soup = draw_layout(Alert("Mind this", css_id="note", css_class="error mine"))

        assert "error" not in soup.find(id="note")["class"]
        assert "mine" in soup.find(id="note")["class"]

    def test_the_id_and_attributes_reach_the_alert(self, draw_layout):
        soup = draw_layout(Alert("Mind this", css_id="note", **DEVELOPER_ATTRS))

        alert = soup.find(id="note")
        assert alert["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert alert["lang"] == DEVELOPER_ATTRS["lang"]

    def test_an_alert_given_no_id_is_drawn_without_one(self, draw_layout):
        soup = draw_layout(Alert("Mind this"))

        assert not alerts(soup)[0].has_attr("id")
