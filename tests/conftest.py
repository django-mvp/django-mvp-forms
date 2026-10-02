"""Fixtures shared across the test suite."""

import pytest
from django.urls import reverse


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()
