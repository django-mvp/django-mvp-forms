"""A characters-left field, drawn through each renderer."""

import gettext
import json
from pathlib import Path

import django
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


def words_of(control):
    return json.loads(control["data-characters-left-words"])


class TestTheLineFromTheStart:
    @pytest.mark.parametrize("widget", [CharactersLeftInput, CharactersLeftTextarea])
    def test_without_a_number_the_control_states_none_to_appear_from(
        self, draw, widget
    ):
        control = control_of(draw("{% crispy form %}", form=form_of(widget())))

        assert not control.has_attr("data-characters-left-from")
        assert control.has_attr("data-characters-left-words")

    def test_a_number_stated_on_the_widget_is_written_on_the_control(self, draw):
        form = form_of(CharactersLeftInput(show_from=5))

        control = control_of(draw("{% crispy form %}", form=form))

        assert control["data-characters-left-from"] == "5"

    @pytest.mark.parametrize(
        ("limit", "written"), [(40, 41), (199, 200), (200, 200), (5000, 200)]
    )
    def test_a_sentence_is_written_for_each_count_up_to_the_limit_or_199(
        self, draw, limit, written
    ):
        class Long(forms.Form):
            title = forms.CharField(max_length=limit, widget=CharactersLeftInput)

        control = control_of(draw("{{ form }}", form=Long()))

        assert len(words_of(control)) == written

    def test_each_sentence_carries_its_own_count(self, draw):
        control = control_of(draw("{{ form }}", form=form_of(CharactersLeftInput())))

        for count, words in enumerate(words_of(control)):
            assert str(count) in words

    @pytest.mark.parametrize("show_from", [0, -1, 2.5, "3", True])
    def test_a_number_that_is_not_a_whole_number_above_zero_is_refused(self, show_from):
        with pytest.raises(ValueError, match="show_from"):
            CharactersLeftInput(show_from=show_from)


def plural_formulas():
    """The plural function of every catalogue Django ships."""
    found = {}
    for path in sorted(
        Path(django.__file__).parent.glob("conf/locale/*/LC_MESSAGES/django.mo")
    ):
        with path.open("rb") as catalogue:
            found[path.parts[-3]] = gettext.GNUTranslations(catalogue).plural
    return found


class TestPluralFormsOfEveryLocale:
    """The script writes a large count with the sentence of 100 + count % 100."""

    def test_django_ships_catalogues_to_prove_it_against(self):
        assert len(plural_formulas()) > 50

    @pytest.mark.parametrize("locale", sorted(plural_formulas()))
    def test_a_count_of_200_or_more_takes_the_form_of_100_plus_its_last_two_digits(
        self, locale
    ):
        plural = plural_formulas()[locale]

        different = [n for n in range(200, 5000) if plural(n) != plural(100 + n % 100)]

        assert different == []
