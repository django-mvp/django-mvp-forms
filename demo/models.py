"""The demo project's user, which keeps each person's preferences for django-mvp."""

from django.contrib.auth.models import AbstractUser
from mvp.models import PreferencesMixin


class User(PreferencesMixin, AbstractUser):
    """A person who signs in to the demo."""
