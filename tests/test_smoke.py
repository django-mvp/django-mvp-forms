"""The package installs and exposes what a consuming project needs from it."""

from django.apps import apps


class TestPackagedApp:
    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_forms")
