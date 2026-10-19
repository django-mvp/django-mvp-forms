"""Image fields drawn with the stored image beside the input."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.fields.files import FieldFile

from demo.settings import BASE_DIR
from mvp_forms.widgets import ImageInput

# The demo keeps no records, so the stored images are files shipped with it,
# handed to each form as its initial values.
SAMPLES = FileSystemStorage(
    location=BASE_DIR / "demo" / "static" / "demo" / "sample-images",
    base_url="/static/demo/sample-images/",
)
SAMPLE_FIELD = models.ImageField(storage=SAMPLES)


def stored(name):
    """Return a stored file, as a model instance would hand it to a form."""
    return FieldFile(None, SAMPLE_FIELD, name)


class SampleForm(forms.Form):
    """A form with a submit button and no browser validation."""

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Save"))


class ProfileForm(SampleForm):
    """A record that already has its pictures."""

    photo = forms.ImageField(
        label="Profile photo",
        widget=ImageInput,
        required=False,
        help_text="A square photo works best.",
    )
    cover = forms.ImageField(label="Cover image", widget=ImageInput, required=False)
    report = forms.FileField(
        label="Field report",
        required=False,
        help_text="A FileField keeps the plain clearable file input.",
    )

    initial_values = {
        "photo": stored("ada-portrait.jpg"),
        "cover": stored("field-season-cover.jpg"),
        "report": stored("field-report-2025.pdf"),
    }


class NewRecordForm(SampleForm):
    """A record that has no pictures yet."""

    photo = forms.ImageField(label="Profile photo", widget=ImageInput, required=False)
    badge = forms.ImageField(
        label="Station badge",
        widget=ImageInput,
        help_text="Required. PNG or JPEG.",
    )


class StatesForm(SampleForm):
    """The shapes and states a stored image can come in."""

    icon = forms.ImageField(
        label="Station icon",
        widget=ImageInput,
        help_text="Required, so it can be replaced but not removed.",
    )
    scan = forms.ImageField(
        label="Label scan",
        widget=ImageInput,
        required=False,
        help_text="A tall image with a long file name.",
    )
    lost = forms.ImageField(
        label="Site photo",
        widget=ImageInput,
        required=False,
        help_text="The stored file is no longer on disk.",
    )
    locked = forms.ImageField(
        label="Approved portrait",
        widget=ImageInput,
        required=False,
        disabled=True,
        help_text="Disabled.",
    )

    initial_values = {
        "icon": stored("station-icon.png"),
        "scan": stored("core-label-borehole-GH-2291-section-04-of-11-reverse-side.png"),
        "lost": stored("site-photo-deleted.jpg"),
        "locked": stored("ada-portrait.jpg"),
    }


class SentBackForm(SampleForm):
    """A form sent with a file that is not an image, and a required one empty."""

    photo = forms.ImageField(label="Profile photo", widget=ImageInput, required=False)
    badge = forms.ImageField(label="Station badge", widget=ImageInput)

    initial_values = {"photo": stored("ada-portrait.jpg")}

    @classmethod
    def sent(cls):
        """Return the data and files the form is drawn as having been sent."""
        notes = SimpleUploadedFile("notes.txt", b"Not an image.", "text/plain")
        return {}, {"photo": notes}
