"""A host project's replacement at a path the pack has moved away from is honoured."""

import warnings

import pytest
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from mvp_forms.deprecation import WITHDRAWN, host_template

OLD = "daisyui/old.html"
NEW = "daisyui/new.html"


def nothing_there(path):
    raise TemplateDoesNotExist(path)


def something_there(path):
    return object()


class TestWithdrawn:
    def test_no_path_is_withdrawn_as_shipped(self):
        assert WITHDRAWN == {}


class TestHostTemplate:
    def test_a_template_at_the_old_path_is_returned_and_warned_about(self, monkeypatch):
        monkeypatch.setitem(WITHDRAWN, OLD, NEW)

        with pytest.warns(DeprecationWarning) as recorded:
            path = host_template(OLD, something_there)

        assert path == OLD
        assert OLD in str(recorded[0].message)
        assert NEW in str(recorded[0].message)

    def test_nothing_at_the_old_path_returns_the_replacing_path_without_a_warning(
        self, monkeypatch
    ):
        monkeypatch.setitem(WITHDRAWN, OLD, NEW)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            path = host_template(OLD, nothing_there)

        assert path == NEW

    def test_a_row_with_no_replacement_returns_nothing_when_the_host_has_none(
        self, monkeypatch
    ):
        monkeypatch.setitem(WITHDRAWN, OLD, None)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            path = host_template(OLD, nothing_there)

        assert path == ""

    def test_a_row_with_no_replacement_warns_when_the_host_has_a_template(
        self, monkeypatch
    ):
        monkeypatch.setitem(WITHDRAWN, OLD, None)

        with pytest.warns(DeprecationWarning) as recorded:
            path = host_template(OLD, something_there)

        assert path == OLD
        assert OLD in str(recorded[0].message)

    def test_a_path_that_is_not_withdrawn_raises_a_key_error(self):
        with pytest.raises(KeyError) as raised:
            host_template(OLD, something_there)

        assert raised.value.args == (OLD,)

    def test_a_path_that_is_not_withdrawn_is_not_looked_up_in_the_templates(self):
        asked = []

        def recording(path):
            asked.append(path)
            return object()

        with pytest.raises(KeyError):
            host_template(OLD, recording)

        assert asked == []

    def test_a_template_the_host_project_has_is_found_through_the_engine(
        self, monkeypatch, replace
    ):
        monkeypatch.setitem(WITHDRAWN, OLD, NEW)

        with replace({OLD: "<i></i>"}), pytest.warns(DeprecationWarning):
            path = host_template(OLD, get_template)

        assert path == OLD

    def test_a_template_the_host_project_lacks_is_not_found_through_the_engine(
        self, monkeypatch
    ):
        monkeypatch.setitem(WITHDRAWN, OLD, NEW)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            path = host_template(OLD, get_template)

        assert path == NEW
