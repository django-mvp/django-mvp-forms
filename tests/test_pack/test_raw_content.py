"""The layout objects that place raw markup and hidden values in a layout."""

import pytest
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import HTML, ButtonHolder, Column, Fieldset, Hidden

from tests.forms import ButtonedForm, StructureForm

NOTE = '<p id="note">A <strong>note</strong></p>'
CONTAINERS = [
    pytest.param(
        lambda *items: Fieldset("Legend", *items, css_id="box"), id="fieldset"
    ),
    pytest.param(lambda *items: Column(*items, css_id="box"), id="column"),
    pytest.param(lambda *items: ButtonHolder(*items, css_id="box"), id="button holder"),
    pytest.param(lambda *items: FormActions(*items, css_id="box"), id="form actions"),
]


class TestHTML:
    def test_it_is_drawn_between_the_two_fields_it_was_placed_between(
        self, draw_layout
    ):
        soup = draw_layout("first", HTML(NOTE), "second")

        note = soup.find(id="note")
        assert soup.find(id="id_first") in note.find_all_previous("input")
        assert soup.find(id="id_second") in note.find_all_next("input")
        assert soup.find(id="id_first") not in note.find_all_next("input")

    def test_the_markup_the_developer_wrote_is_kept(self, draw_layout):
        soup = draw_layout(HTML(NOTE))

        assert soup.find(id="note").find("strong").get_text() == "note"

    def test_a_context_value_in_it_is_filled_in(self, draw_layout):
        soup = draw_layout(HTML('<p id="note">Hello {{ who }}</p>'), who="Ada")

        assert soup.find(id="note").get_text() == "Hello Ada"

    def test_markup_in_a_context_value_is_escaped(self, draw_layout):
        soup = draw_layout(
            HTML('<p id="note"><em>Hello</em> {{ who }}</p>'), who="<script>x</script>"
        )

        note = soup.find(id="note")
        assert note.find("script") is None
        assert note.find("em") is not None
        assert "<script>x</script>" in note.get_text()

    @pytest.mark.parametrize("container", CONTAINERS)
    def test_it_is_inside_the_container_it_was_placed_in(self, draw_layout, container):
        soup = draw_layout(container(HTML(NOTE)))

        assert soup.find(id="box").find(id="note") is not None

    def test_it_is_drawn_when_it_is_the_only_object(self, draw_layout):
        soup = draw_layout(HTML(NOTE))

        assert soup.find(id="note") is not None


class TestHidden:
    @pytest.fixture
    def draw_in_form(self, draw):
        def draw_hidden(*layout):
            form = StructureForm(None, layout=layout)
            form.helper.form_tag = True
            return draw("{% crispy form %}", form=form)

        return draw_hidden

    def test_it_is_a_hidden_input_with_its_name_and_value(self, draw_layout):
        soup = draw_layout(Hidden("step", "two"))

        control = soup.find("input", attrs={"name": "step"})
        assert control["type"] == "hidden"
        assert control["value"] == "two"

    def test_it_is_inside_the_form_element(self, draw_in_form):
        soup = draw_in_form("first", Hidden("step", "two"))

        control = soup.find("input", attrs={"name": "step"})
        assert control.find_parent("form") is soup.find("form")

    def test_it_is_inside_the_form_element_when_added_to_the_helper(self, draw):
        form = ButtonedForm(buttons=[Hidden("step", "two")])

        soup = draw("{% crispy form %}", form=form)

        control = soup.find("input", attrs={"name": "step"})
        assert control.find_parent("form") is soup.find("form")

    def test_it_carries_no_class_attribute(self, draw_layout):
        soup = draw_layout(Hidden("step", "two"))

        assert not soup.find("input", attrs={"name": "step"}).has_attr("class")

    def test_it_carries_no_generated_id(self, draw_layout):
        soup = draw_layout(Hidden("step", "two"))

        assert not soup.find("input", attrs={"name": "step"}).has_attr("id")

    def test_an_attribute_passed_as_a_keyword_arrives(self, draw_layout):
        soup = draw_layout(Hidden("step", "two", **{"data-role": "wizard"}))

        control = soup.find("input", attrs={"name": "step"})
        assert control["data-role"] == "wizard"

    def test_an_id_passed_as_a_keyword_arrives(self, draw_layout):
        soup = draw_layout(Hidden("step", "two", id="the-step"))

        assert soup.find("input", id="the-step")["name"] == "step"

    def test_a_value_reading_the_context_is_filled_in(self, draw_layout):
        soup = draw_layout(Hidden("step", "{{ step }}"), step="three")

        assert soup.find("input", attrs={"name": "step"})["value"] == "three"

    def test_markup_in_a_value_is_escaped(self, draw_layout):
        soup = draw_layout(Hidden("step", "{{ step }}"), step='"><script>x</script>')

        assert soup.find("script") is None
        assert soup.find("input", attrs={"name": "step"})["value"] == (
            '"><script>x</script>'
        )
