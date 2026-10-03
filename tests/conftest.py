"""Fixtures shared across the test suite."""

import pytest
from bs4 import BeautifulSoup
from django.template import Context, Template
from django.urls import reverse


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def parse():
    def parse_fragment(html):
        return BeautifulSoup(html, "html.parser")

    return parse_fragment


@pytest.fixture
def draw(parse):
    def draw_template(source, **context):
        template = Template("{% load crispy_forms_tags %}" + source)
        return parse(template.render(Context(context)))

    return draw_template
