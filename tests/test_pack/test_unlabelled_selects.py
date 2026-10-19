"""A select drawn with no label above it shows its label inside its frame."""

import pytest
from crispy_forms.bootstrap import InlineField, PrependedText
from crispy_forms.layout import Field

from mvp_forms.layout import Join
from tests.forms import UnlabelledSelectsForm

SELECTS = ["plain", "single", "counted", "foreign"]


def frame_of(soup, name):
    """Return the element that holds the select and the label shown inside it."""
    return soup.find(id=f"id_{name}").parent


def shown_label(soup, name):
    """Return the label span drawn before the select, or None."""
    return frame_of(soup, name).find("span", class_="label", recursive=False)


class TestASelectWithLabelsOff:
    @pytest.mark.parametrize("name", SELECTS)
    def test_it_sits_in_a_select_frame_that_shows_its_label(self, draw, name):
        form = UnlabelledSelectsForm()

        soup = draw("{% crispy form %}", form=form)

        assert "select" in frame_of(soup, name)["class"]
        assert shown_label(soup, name).get_text(strip=True) == form[name].label

    @pytest.mark.parametrize("name", ["plain", "single", "counted"])
    def test_it_is_named_by_its_label(self, draw, name):
        form = UnlabelledSelectsForm()

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id=f"id_{name}")["aria-label"] == form[name].label

    def test_the_label_shown_is_escaped(self, draw):
        soup = draw("{% crispy form %}", form=UnlabelledSelectsForm())

        assert shown_label(soup, "counted").find("b") is None
        assert shown_label(soup, "counted").get_text() == "Kind <b>&</b> sort"

    def test_a_stock_select_sits_in_a_label(self, draw):
        soup = draw("{% crispy form %}", form=UnlabelledSelectsForm())

        assert frame_of(soup, "plain").name == "label"

    @pytest.mark.parametrize("name", ["single", "counted", "foreign"])
    def test_a_tom_select_control_sits_in_a_div(self, draw, name):
        soup = draw("{% crispy form %}", form=UnlabelledSelectsForm())

        assert frame_of(soup, name).name == "div"

    def test_an_inline_field_shows_its_label_too(self, draw):
        form = UnlabelledSelectsForm(layout=[InlineField("plain")])
        form.helper.form_show_labels = True

        soup = draw("{% crispy form %}", form=form)

        assert shown_label(soup, "plain").get_text(strip=True) == form["plain"].label

    def test_a_field_with_no_label_shows_none(self, draw):
        soup = draw("{% crispy form %}", form=UnlabelledSelectsForm())

        assert "select" in soup.find(id="id_unnamed")["class"]
        assert soup.find(id="id_unnamed").find_parent(class_="select") is None


class TestASelectThatShowsNoLabelOfItsOwn:
    def test_text_attached_by_a_layout_is_shown_in_its_place(self, draw):
        form = UnlabelledSelectsForm(layout=[PrependedText("plain", "Fruit")])

        soup = draw("{% crispy form %}", form=form)

        spans = frame_of(soup, "plain").find_all("span", class_="label")
        assert [span.get_text(strip=True) for span in spans] == ["Fruit"]

    def test_a_member_of_a_join_shows_none(self, draw):
        form = UnlabelledSelectsForm(
            layout=[Join(Field("plain"), Field("unnamed"), label="Pair")]
        )

        soup = draw("{% crispy form %}", form=form)

        assert soup.find(id="id_plain").find_parent(class_="select") is None
        assert "join-item" in soup.find(id="id_plain")["class"]

    def test_with_labels_on_nothing_changes(self, draw):
        form = UnlabelledSelectsForm()
        form.helper.form_show_labels = True

        soup = draw("{% crispy form %}", form=form)

        for name in SELECTS:
            assert soup.find(id=f"id_{name}").find_parent(class_="select") is None
            assert soup.find("label", attrs={"for": f"id_{name}"}) is not None
