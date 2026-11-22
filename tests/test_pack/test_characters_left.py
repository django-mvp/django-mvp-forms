"""A characters-left field, drawn through each renderer."""

import pytest
from crispy_forms.helper import FormHelper
from django import forms

from mvp_forms.widgets import CharactersLeftInput, CharactersLeftTextarea

SOURCES = [
    "{{ form|crispy }}",
    "{% crispy form %}",
    "{{ form.title|as_crispy_field }}",
    "{{ form.as_div }}",
]
FORM_WIDE = SOURCES[:2]
SCRIPT = "mvp_forms/characters-left.js"
MARKED = ["data-characters-left-from", "data-characters-left-words"]


def form_of(widget, **options):
    class CountedForm(forms.Form):
        title = forms.CharField(
            max_length=40, help_text="Shown in lists.", widget=widget, **options
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper(self)
            self.helper.form_tag = False

    return CountedForm()


def control_of(soup):
    return soup.find(id="id_title")


class TestCharactersLeft:
    @pytest.mark.parametrize("widget", [CharactersLeftInput, CharactersLeftTextarea])
    @pytest.mark.parametrize("source", SOURCES)
    def test_the_same_attributes_are_drawn_whichever_way_the_form_is_rendered(
        self, draw, widget, source
    ):
        form = form_of(widget(show_from=5))
        written = {
            name: control_of(draw(each, form=form))[name]
            for each in SOURCES
            for name in MARKED
        }

        control = control_of(draw(source, form=form))

        assert {name: control[name] for name in MARKED} == written
        assert control["data-characters-left-from"] == "5"
        assert control["maxlength"] == "40"
        assert control["data-characters-left-over"]

    @pytest.mark.parametrize("widget", [CharactersLeftInput, CharactersLeftTextarea])
    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_input_keeps_the_description_the_pack_writes(
        self, draw, widget, source
    ):
        soup = draw(source, form=form_of(widget()))

        control = control_of(soup)

        assert soup.find(id=control["aria-describedby"].split()[0]) is not None

    @pytest.mark.parametrize("source", FORM_WIDE)
    def test_the_description_stays_tied_to_a_field_with_an_error(self, draw, source):
        form = form_of(CharactersLeftInput())
        form.data = {"title": "x" * 41}
        form.is_bound = True

        control = control_of(draw(source, form=form))

        described = control["aria-describedby"].split()
        assert "id_title_error" in described

    @pytest.mark.parametrize(
        ("counted", "plain"),
        [
            (CharactersLeftInput, forms.TextInput),
            (CharactersLeftTextarea, forms.Textarea),
        ],
    )
    @pytest.mark.parametrize("source", SOURCES)
    def test_a_field_without_the_widget_is_drawn_as_it_was(
        self, draw, counted, plain, source
    ):
        before = control_of(draw(source, form=form_of(plain)))
        after = control_of(draw(source, form=form_of(counted())))

        for name in list(after.attrs):
            if name.startswith("data-characters-left"):
                del after[name]
        assert after == before

    @pytest.mark.parametrize("widget", [forms.TextInput, forms.Textarea])
    def test_a_form_without_the_widgets_names_no_script(self, draw, widget):
        form = form_of(widget)

        assert SCRIPT not in str(form.media)
        assert SCRIPT not in str(draw("{% crispy form %}", form=form))

    @pytest.mark.parametrize("widget", [CharactersLeftInput, CharactersLeftTextarea])
    def test_a_form_with_the_widget_names_the_script_once(self, widget):
        assert str(form_of(widget()).media).count(SCRIPT) == 1
