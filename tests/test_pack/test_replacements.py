"""A host project replaces one pack template and every other stays the pack's."""

import copy
import re

import pytest
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Row, Submit
from crispy_forms.templatetags import crispy_forms_filters, crispy_forms_tags
from crispy_forms.utils import default_field_template
from django.conf import settings
from django.template import Context, Template
from django.test import override_settings

from tests.conftest import (
    FORM_RENDERER_THAT_READS_TEMPLATES,
    PACK_TEMPLATES,
    clear_crispy_template_caches,
)
from tests.forms import (
    CheckboxForm,
    DateSelectsForm,
    FieldAndFormWideErrorsForm,
    LineFormSet,
    RadioGroupsForm,
    TextInputsForm,
    TextInputsWithLayoutForm,
)
from tests.test_pack.test_independence import STATES

MARKER = "@@replaced@@"
TEMPLATE_PATHS = sorted(
    path.relative_to(PACK_TEMPLATES).as_posix()
    for path in (PACK_TEMPLATES / "daisyui").rglob("*.html")
)
NEVER_DRAWN = {"daisyui/layout/tab-link.html"}
CRISPY_TEMPLATES_KEPT_IN_MEMORY = (
    default_field_template,
    crispy_forms_filters.uni_form_template,
    crispy_forms_filters.uni_formset_template,
    crispy_forms_tags.whole_uni_form_template,
    crispy_forms_tags.whole_uni_formset_template,
)
FILTER = "{{ form|crispy }}"
TAG = "{% crispy form %}"
OWN_CONTAINER = "tests/own_container.html"
FRAME = '<div data-replaced="frame">{{ drawn.render }}</div>'
REQUIRED_MARKER = (
    '{% if field.field.required %}<i data-replaced="marker"></i>{% endif %}'
)
DIV = '<div data-replaced="div" id="{{ div.css_id }}">{{ fields }}</div>'
GROUP = (
    '<div data-replaced="group">'
    '{% include "daisyui/widgets/group_options.html" %}</div>'
)
SELECT_DATE = '<div data-replaced="select-date"></div>'
RANDOM_IDS = re.compile(r"(tabs|accordion)-[0-9a-f]+")
WHITESPACE = re.compile(r"\s+")


def draw_state(source, build):
    template = Template("{% load crispy_forms_tags %}" + source)
    html = template.render(Context({"csrf_token": "token", "form": build()}))
    return RANDOM_IDS.sub(r"\1-id", html)


def without_marker(html):
    # The form renderer strips what a widget template draws, so the whitespace
    # beside a marker at its start is not the pack's.
    return WHITESPACE.sub(" ", html.replace(MARKER, ""))


def draw_every_state():
    return [draw_state(*param.values[:2]) for param in STATES]


@pytest.fixture(scope="class")
def untouched():
    return [without_marker(html) for html in draw_every_state()]


class TestEveryTemplate:
    def test_the_package_has_templates_to_replace(self):
        assert TEMPLATE_PATHS

    @pytest.mark.parametrize("path", TEMPLATE_PATHS)
    def test_a_copy_with_a_marker_draws_what_the_pack_draws_plus_the_marker(
        self, replace, pack_source, untouched, path
    ):
        with replace({path: MARKER + pack_source(path)}):
            replaced = draw_every_state()

        assert [without_marker(html) for html in replaced] == untouched
        if path not in NEVER_DRAWN:
            assert any(MARKER in html for html in replaced)


class TestTheReplaceFixture:
    def test_leaving_the_block_restores_the_settings(self, replace):
        templates = settings.TEMPLATES[0]["DIRS"]
        renderer = settings.FORM_RENDERER
        apps = list(settings.INSTALLED_APPS)

        with replace({"daisyui/required_marker.html": MARKER}):
            assert len(settings.TEMPLATES[0]["DIRS"]) == len(templates) + 1
            assert settings.FORM_RENDERER == FORM_RENDERER_THAT_READS_TEMPLATES
            assert "django.forms" in settings.INSTALLED_APPS

        assert settings.TEMPLATES[0]["DIRS"] == templates
        assert renderer == settings.FORM_RENDERER
        assert apps == settings.INSTALLED_APPS

    def test_leaving_the_block_clears_the_five_templates_crispy_keeps(
        self, replace, draw, draw_layout
    ):
        with replace({"daisyui/whole_uni_formset.html": MARKER}):
            draw_layout("first")
            draw("{% crispy form %}", form=LineFormSet())
            draw("{{ form|crispy }}", form=LineFormSet())
            draw("{{ form|crispy }}", form=TextInputsForm())
            draw("{% crispy form %}", form=TextInputsForm())
            assert all(
                template.cache_info().currsize
                for template in CRISPY_TEMPLATES_KEPT_IN_MEMORY
            )

        assert not any(
            template.cache_info().currsize
            for template in CRISPY_TEMPLATES_KEPT_IN_MEMORY
        )

    def test_a_replacement_of_a_template_crispy_keeps_is_gone_afterwards(
        self, replace, draw
    ):
        with replace({"daisyui/whole_uni_formset.html": MARKER}):
            inside = draw("{% crispy form %}", form=LineFormSet())

        outside = draw("{% crispy form %}", form=LineFormSet())

        assert MARKER in inside.get_text()
        assert MARKER not in outside.get_text()


def found(soup, name):
    return soup.find_all(attrs={"data-replaced": name})


def helped(form, **attributes):
    form.helper = FormHelper()
    for name, value in attributes.items():
        setattr(form.helper, name, value)
    return form


def required_fields(form_class):
    return sum(field.required for field in form_class.base_fields.values())


def as_table(formset):
    return helped(formset, template="daisyui/table_inline_formset.html")


def with_save_button(form):
    helped(form).helper.add_input(Submit("save", "Save"))
    return form


def left_alone(soup):
    return (
        [str(tag) for tag in soup.find_all(["input", "select", "textarea"])],
        [str(tag) for tag in soup.find_all(attrs={"role": "alert"})],
        [str(tag) for tag in soup.find_all(attrs={"type": "submit"})],
    )


def layout_with_div_between_rows():
    return (
        Div("first", css_id="one"),
        Row("second", css_id="two"),
        Div("third", css_id="three"),
    )


class TestReplacingOneTemplate:
    def test_a_replaced_frame_frames_every_field_and_nothing_else_changes(
        self, replace, draw
    ):
        before = draw(TAG, form=with_save_button(FieldAndFormWideErrorsForm({})))

        with replace({"daisyui/frame.html": FRAME}):
            after = draw(TAG, form=with_save_button(FieldAndFormWideErrorsForm({})))

        assert len(found(after, "frame")) == len(FieldAndFormWideErrorsForm().fields)
        assert before.find_all(class_="fieldset")
        assert not after.find_all(class_="fieldset")
        assert left_alone(after) == left_alone(before)
        assert left_alone(after)[1] and left_alone(after)[2]

    def test_a_replaced_layout_object_is_drawn_among_the_pack_s_own(
        self, replace, draw_layout
    ):
        before = draw_layout(*layout_with_div_between_rows())

        with replace({"daisyui/layout/div.html": DIV}):
            after = draw_layout(*layout_with_div_between_rows())

        assert {tag["id"] for tag in found(after, "div")} == {"one", "three"}
        assert not found(before, "div")
        assert str(after.find(id="two")) == str(before.find(id="two"))
        assert after.find(id="one").find(id="id_first") is not None

    def test_a_replaced_widget_is_drawn_inside_the_pack_s_frame(self, replace, draw):
        before = draw(FILTER, form=RadioGroupsForm())

        with replace({"daisyui/widgets/group.html": GROUP}):
            after = draw(FILTER, form=RadioGroupsForm())

        frame = after.find(id="div_id_choice")
        assert not found(before, "group")
        assert frame.find(attrs={"data-replaced": "group"}) is not None
        assert "fieldset" in frame["class"]
        assert str(frame.legend) == str(before.find(id="div_id_choice").legend)
        assert str(after.find(id="id_choice_helptext")) == str(
            before.find(id="id_choice_helptext")
        )

    @pytest.mark.parametrize(
        ("source", "build", "required"),
        [
            pytest.param(
                FILTER, TextInputsForm, required_fields(TextInputsForm), id="label"
            ),
            pytest.param(
                FILTER, RadioGroupsForm, required_fields(RadioGroupsForm), id="legend"
            ),
            pytest.param(
                FILTER, CheckboxForm, required_fields(CheckboxForm), id="checkbox"
            ),
            pytest.param(
                TAG,
                lambda: as_table(LineFormSet()),
                required_fields(LineFormSet.form),
                id="table header",
            ),
        ],
    )
    def test_the_template_several_pack_templates_include_is_drawn_by_each(
        self, replace, draw, source, build, required
    ):
        with replace({"daisyui/required_marker.html": REQUIRED_MARKER}):
            soup = draw(source, form=build())

        assert required
        assert len(found(soup, "marker")) == required

    @pytest.mark.parametrize(
        ("source", "build"),
        [
            pytest.param(FILTER, TextInputsForm, id="filter"),
            pytest.param(TAG, TextInputsWithLayoutForm, id="tag"),
            pytest.param(TAG, LineFormSet, id="stacked formset"),
            pytest.param(TAG, lambda: as_table(LineFormSet()), id="table formset"),
        ],
    )
    def test_the_same_replacement_is_used_through_the_filter_the_tag_and_formsets(
        self, replace, draw, source, build
    ):
        before = draw(source, form=build())

        with replace({"daisyui/frame.html": FRAME}):
            after = draw(source, form=build())

        assert before.find_all(class_="fieldset")
        assert found(after, "frame")
        assert not after.find_all(class_="fieldset")

    @pytest.mark.parametrize(
        ("path", "replacement", "source", "build"),
        [
            pytest.param(
                "daisyui/frame.html", FRAME, FILTER, TextInputsForm, id="frame"
            ),
            pytest.param(
                "daisyui/widgets/group.html",
                GROUP,
                FILTER,
                RadioGroupsForm,
                id="widget",
            ),
            pytest.param(
                "daisyui/whole_uni_formset.html",
                '<div data-replaced="whole"></div>',
                TAG,
                LineFormSet,
                id="one crispy keeps in memory",
            ),
        ],
    )
    def test_a_replacement_taken_away_leaves_the_form_drawn_as_before(
        self, replace, draw, path, replacement, source, build
    ):
        before = draw(source, form=build())

        with replace({path: replacement}):
            inside = draw(source, form=build())
        after = draw(source, form=build())

        assert inside.find(attrs={"data-replaced": True}) is not None
        assert str(after) == str(before)

    def test_a_layout_object_s_own_template_wins_over_a_replacement(
        self, replace, draw_layout
    ):
        layout = (
            Div("first", css_id="mine", template=OWN_CONTAINER),
            Div("second", css_id="plain"),
        )

        with replace({"daisyui/layout/div.html": DIV}):
            soup = draw_layout(*layout)

        assert soup.find(id="own-container") is not None
        assert [tag["id"] for tag in found(soup, "div")] == ["plain"]

    def test_a_helper_s_field_template_wins_over_a_replacement(self, replace, draw):
        own = helped(TextInputsForm(), field_template=OWN_CONTAINER)

        with replace({"daisyui/field.html": '<div data-replaced="field"></div>'}):
            drawn = draw(TAG, form=own)
            elsewhere = draw(FILTER, form=TextInputsForm())

        assert len(drawn.find_all(id="own-container")) == len(own.fields)
        assert not found(drawn, "field")
        assert found(elsewhere, "field")

    def test_a_helper_s_template_wins_over_a_replacement(self, replace, draw):
        own = helped(TextInputsForm(), template=OWN_CONTAINER)

        with replace(
            {"daisyui/whole_uni_form.html": '<div data-replaced="whole"></div>'}
        ):
            drawn = draw(TAG, form=own)
            elsewhere = draw(TAG, form=helped(TextInputsForm()))

        assert drawn.find(id="own-container") is not None
        assert not found(drawn, "whole")
        assert found(elsewhere, "whole")


class TestWhereAReplacementIsFound:
    def test_an_app_listed_after_the_pack_is_not_used(self, draw, settings):
        apps = [*settings.INSTALLED_APPS, "tests.host_app"]

        with override_settings(INSTALLED_APPS=apps):
            soup = draw(FILTER, form=DateSelectsForm())

        assert soup.find_all("select")
        assert not found(soup, "host-select-date")

    def test_an_app_listed_before_the_pack_is_used_by_the_default_renderer(
        self, draw, settings
    ):
        apps = list(settings.INSTALLED_APPS)
        apps.insert(apps.index("mvp_forms"), "tests.host_app")

        with override_settings(INSTALLED_APPS=apps):
            soup = draw(FILTER, form=DateSelectsForm())

        assert found(soup, "host-select-date")

    def test_a_page_template_in_an_app_listed_after_the_pack_is_not_used(
        self, draw, settings
    ):
        apps = [*settings.INSTALLED_APPS, "tests.host_app"]

        with override_settings(INSTALLED_APPS=apps):
            clear_crispy_template_caches()
            soup = draw(FILTER, form=TextInputsForm())
        clear_crispy_template_caches()

        assert soup.find_all("input")
        assert not found(soup, "host-marker")

    def test_a_page_template_in_an_app_listed_before_the_pack_is_used(
        self, draw, settings
    ):
        apps = list(settings.INSTALLED_APPS)
        apps.insert(apps.index("mvp_forms"), "tests.host_app")

        with override_settings(INSTALLED_APPS=apps):
            clear_crispy_template_caches()
            soup = draw(FILTER, form=TextInputsForm())
        clear_crispy_template_caches()

        assert found(soup, "host-marker")

    def test_a_widget_replacement_in_dirs_is_not_used_by_the_default_renderer(
        self, draw, settings, tmp_path
    ):
        (tmp_path / "daisyui" / "widgets").mkdir(parents=True)
        (tmp_path / "daisyui" / "widgets" / "select_date.html").write_text(SELECT_DATE)
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [tmp_path, *templates[0]["DIRS"]]

        with override_settings(TEMPLATES=templates):
            soup = draw(FILTER, form=DateSelectsForm())

        assert soup.find_all("select")
        assert not found(soup, "select-date")

    def test_two_replacements_one_including_the_other_are_both_used(
        self, replace, draw
    ):
        frame = (
            '<div data-replaced="frame">{{ field.label }}'
            '{% include "daisyui/required_marker.html" %}{{ drawn.render }}</div>'
        )

        with replace(
            {
                "daisyui/frame.html": frame,
                "daisyui/required_marker.html": REQUIRED_MARKER,
            }
        ):
            soup = draw(FILTER, form=TextInputsForm())

        assert len(found(soup, "frame")) == len(TextInputsForm().fields)
        assert len(found(soup, "marker")) == len(TextInputsForm().fields)

    def test_a_tab_link_replacement_is_drawn_where_the_tab_template_draws_links(
        self, replace, draw_layout
    ):
        tabs = (TabHolder(Tab("One", "first"), Tab("Two", "second")),)
        holder = '<div data-replaced="tabs">{{ links }}</div>'
        link = '<i data-replaced="link"></i>'

        with replace(
            {"daisyui/layout/tab.html": holder, "daisyui/layout/tab-link.html": link}
        ):
            soup = draw_layout(*tabs)

        assert len(found(soup, "link")) == 2
        assert soup.find(attrs={"data-replaced": "tabs"}).find(
            attrs={"data-replaced": "link"}
        )

    def test_a_tab_link_replacement_alone_is_rendered_and_not_drawn(
        self, replace, draw_layout
    ):
        tabs = (TabHolder(Tab("One", "first"), Tab("Two", "second")),)

        with replace({"daisyui/layout/tab-link.html": '<i data-replaced="link"></i>'}):
            soup = draw_layout(*tabs)

        assert not found(soup, "link")

    def test_a_template_of_the_host_project_s_own_changes_nothing_else(
        self, replace, draw_layout
    ):
        own = (
            '<section data-replaced="own" id="{{ div.css_id }}">{{ fields }}</section>'
        )
        rest = ("second", "third", "fourth")
        before = draw_layout(Div("first", css_id="mine"), *rest)

        with replace({"daisyui/layout/own.html": own}):
            after = draw_layout(
                Div("first", css_id="mine", template="daisyui/layout/own.html"), *rest
            )

        assert [tag["id"] for tag in found(after, "own")] == ["mine"]
        for name in rest:
            assert str(after.find(id=f"div_id_{name}")) == str(
                before.find(id=f"div_id_{name}")
            )

    def test_a_widget_that_names_its_own_template_is_not_drawn_by_a_replacement(
        self, replace, draw
    ):
        with replace({"daisyui/widgets/select_date.html": SELECT_DATE}):
            soup = draw(FILTER, form=DateSelectsForm())

        assert found(soup, "select-date")
        assert soup.find(id="div_id_own").find(attrs={"data-replaced": True}) is None

    def test_a_frame_that_leaves_out_the_errors_draws_none_and_raises_nothing(
        self, replace, draw
    ):
        with replace({"daisyui/frame.html": FRAME}):
            soup = draw(FILTER, form=TextInputsForm({}))

        assert found(soup, "frame")
        assert not soup.find_all(id=re.compile("_error$"))
