"""The demo project's user, which stores each person's preferences as django-mvp asks."""

from django.contrib.auth.models import AbstractUser
from mvp.models import PreferencesMixin


class User(PreferencesMixin, AbstractUser):
    """A person who signs in to the demo."""
