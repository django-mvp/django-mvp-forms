"""A boolean field drawn as a single checkbox, through django-crispy-forms."""

import copy

import pytest
from crispy_forms.helper import FormHelper

from tests.forms import CheckboxForm

SOURCES = ["{{ form|crispy }}", "{% crispy form %}"]


def helped(form, **settings):
    form.helper = FormHelper()
    for name, value in settings.items():
        setattr(form.helper, name, value)
    return form


class TestCheckbox:
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_field_is_a_checkbox_with_the_component_class_and_no_width(
        self, draw, source
    ):
        drawn = draw(source, form=CheckboxForm()).find(id="id_agree")

        assert drawn.name == "input"
        assert drawn["type"] == "checkbox"
        assert "checkbox" in drawn["class"]
        assert "w-full" not in drawn["class"]

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_label_holds_the_checkbox_and_is_tied_to_it(self, draw, source):
        soup = draw(source, form=CheckboxForm())

        label = soup.find("label", attrs={"for": "id_agree"})

        assert "label" in label["class"]
        assert label.find("input")["id"] == "id_agree"

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_frame_has_exactly_one_label_for_the_field(self, draw, source):
        soup = draw(source, form=CheckboxForm())

        assert len(soup.find(id="div_id_agree").find_all("label")) == 1

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_true_value_is_checked_and_a_false_one_is_not(self, draw, source):
        form = CheckboxForm(initial={"agree": True, "news": False})

        soup = draw(source, form=form)

        assert soup.find(id="id_agree").has_attr("checked")
        assert not soup.find(id="id_news").has_attr("checked")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_submitted_tick_stays_ticked_when_the_form_is_drawn_again(
        self, draw, source
    ):
        form = CheckboxForm({"agree": "on", "news": "on"})

        soup = draw(source, form=form)

        assert soup.find(id="id_news").has_attr("checked")
        assert not form.errors.get("news")

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_required_box_submitted_unticked_shows_its_error_on_the_checkbox(
        self, draw, source
    ):
        soup = draw(source, form=CheckboxForm({}))

        drawn = soup.find(id="id_agree")

        assert soup.find(id="id_agree_error") is not None
        assert "checkbox-error" in drawn["class"]
        assert drawn["aria-invalid"] == "true"
        assert "id_agree_error" in drawn["aria-describedby"].split()

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_valid_box_carries_no_error_modifier(self, draw, source):
        drawn = draw(source, form=CheckboxForm({"agree": "on"})).find(id="id_agree")

        assert "checkbox-error" not in drawn["class"]
        assert not drawn.has_attr("aria-invalid")

    @pytest.mark.parametrize("source", SOURCES)
    def test_help_text_is_described_and_drawn_once(self, draw, source):
        soup = draw(source, form=CheckboxForm())

        described = soup.find(id="id_agree")["aria-describedby"].split()

        assert described == ["id_agree_helptext"]
        assert len(soup.find_all(id="id_agree_helptext")) == 1

    @pytest.mark.parametrize("source", SOURCES)
    def test_the_marker_is_drawn_only_for_a_required_field(self, draw, source):
        soup = draw(source, form=CheckboxForm())

        required = soup.find(id="div_id_agree").find("label")
        optional = soup.find(id="div_id_news").find("label")

        assert required.find(attrs={"aria-hidden": "true"}) is not None
        assert optional.find(attrs={"aria-hidden": "true"}) is None

    def test_the_helpers_label_class_reaches_the_label(self, draw):
        form = helped(CheckboxForm(), label_class="supplied")

        soup = draw("{% crispy form %}", form=form)

        assert "supplied" in soup.find("label", attrs={"for": "id_agree"})["class"]

    def test_the_helpers_field_class_holds_the_label(self, draw):
        form = helped(CheckboxForm(), field_class="holder")

        soup = draw("{% crispy form %}", form=form)

        holder = soup.find(class_="holder")
        assert holder.find("label", attrs={"for": "id_agree"}) is not None

    def test_with_labels_off_the_checkbox_is_named_by_aria_label(self, draw):
        form = helped(CheckboxForm(), form_show_labels=False)

        soup = draw("{% crispy form %}", form=form)

        frame = soup.find(id="div_id_agree")
        assert frame.find("label") is None
        assert frame.find("input")["aria-label"] == form["agree"].label

    def test_the_developers_class_is_kept_beside_the_component(self, draw):
        drawn = draw("{{ form|crispy }}", form=CheckboxForm()).find(id="id_styled")

        assert {"mine", "checkbox"} <= set(drawn["class"])

    @pytest.mark.parametrize("source", SOURCES)
    def test_a_draw_leaves_the_widgets_attrs_unchanged(self, draw, source):
        form = CheckboxForm({})
        before = {n: copy.deepcopy(f.widget.attrs) for n, f in form.fields.items()}

        draw(source, form=form)

        assert {n: f.widget.attrs for n, f in form.fields.items()} == before
