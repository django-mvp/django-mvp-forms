"""The pack's template for django-tomselect lists an option under its group."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template import Context, Template
from django.test import override_settings
from django_tomselect.middleware import TomSelectMiddleware

from tests.forms import TomSelectForm

GROUP_FIELD = "optgroupField"
GROUP_REGISTRAR = "optionGroupRegister"
TEMPLATE = "django_tomselect/tomselect.html"
PROJECT_MARKER = "projectTemplateWasHere"
PROJECT_TEMPLATE = (
    f'{{% extends "{TEMPLATE}" %}}'
    f"{{% block tomselect_render %}}{PROJECT_MARKER}: 1,{{{{ block.super }}}}"
    "{% endblock tomselect_render %}"
)
FIELDS = ["group", "groups", "country", "countries"]

pytestmark = pytest.mark.django_db


@pytest.fixture
def draw(rf, parse):
    # django-tomselect draws a model-backed widget in full only while its middleware
    # holds a request. Each widget writes one script that names the element it starts.
    def drawing():
        request = rf.get("/")
        request.user = AnonymousUser()
        template = Template("{% load crispy_forms_tags %}{% crispy form %}")
        drawn = []

        def respond(request):
            drawn.append(
                template.render(
                    Context({"csrf_token": "token", "form": TomSelectForm()})
                )
            )
            return HttpResponse()

        TomSelectMiddleware(respond)(request)
        soup = parse(drawn[0])
        texts = [script.get_text() for script in soup.find_all("script")]
        return soup, {
            name: [text for text in texts if f"'id_{name}'" in text] for name in FIELDS
        }

    return drawing


class TestTheGroupingTemplate:
    def test_the_script_of_each_widget_names_the_group_field_and_the_registrar(
        self, draw
    ):
        soup, scripts = draw()

        assert {name: len(found) for name, found in scripts.items()} == dict.fromkeys(
            FIELDS, 1
        )
        for (script,) in scripts.values():
            assert GROUP_FIELD in script
            assert GROUP_REGISTRAR in script

    def test_with_the_pack_after_django_tomselect_neither_is_named_and_the_widget_draws(
        self, draw, settings
    ):
        apps = [app for app in settings.INSTALLED_APPS if app != "mvp_forms"]
        apps.insert(apps.index("django_tomselect") + 1, "mvp_forms")

        with override_settings(INSTALLED_APPS=apps):
            soup, scripts = draw()

        assert {name: len(found) for name, found in scripts.items()} == dict.fromkeys(
            FIELDS, 1
        )
        for (script,) in scripts.values():
            assert GROUP_FIELD not in script
            assert GROUP_REGISTRAR not in script
        assert all(soup.find(id=f"id_{name}") is not None for name in FIELDS)

    def test_a_project_template_at_the_same_path_that_extends_it_still_groups(
        self, draw, replace
    ):
        with replace({TEMPLATE: PROJECT_TEMPLATE}):
            soup, scripts = draw()

        assert {name: len(found) for name, found in scripts.items()} == dict.fromkeys(
            FIELDS, 1
        )
        for (script,) in scripts.values():
            assert PROJECT_MARKER in script
            assert GROUP_FIELD in script
            assert GROUP_REGISTRAR in script
