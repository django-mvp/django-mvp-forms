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
        widget=ImageInput(show_file_name=True),
        required=False,
        help_text="A tall image, with show_file_name=True and a long file name.",
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


class ShapesForm(SampleForm):
    """Thumbnails shaped like the places the images are shown."""

    banner = forms.ImageField(
        label="Banner",
        widget=ImageInput(aspect_ratio=3),
        required=False,
        help_text="aspect_ratio=3",
    )
    video_still = forms.ImageField(
        label="Video still",
        widget=ImageInput(aspect_ratio=16 / 9),
        required=False,
        help_text="aspect_ratio=16 / 9",
    )
    portrait = forms.ImageField(
        label="Portrait",
        widget=ImageInput(aspect_ratio=3 / 4),
        required=False,
        help_text="aspect_ratio=3 / 4",
    )

    initial_values = {
        "banner": stored("field-season-cover.jpg"),
        "video_still": stored("field-season-cover.jpg"),
        "portrait": stored("ada-portrait.jpg"),
    }


class PickerForm(SampleForm):
    """Images changed by clicking them, with no file input in sight."""

    photo = forms.ImageField(
        label="Profile photo",
        widget=ImageInput(show_input=False, aspect_ratio=1),
        required=False,
    )
    logo = forms.ImageField(
        label="Logo",
        widget=ImageInput(show_input=False),
        required=False,
        help_text="Nothing stored yet.",
    )
    cover = forms.ImageField(
        label="Cover image",
        widget=ImageInput(show_input=False, aspect_ratio=3),
        required=False,
    )

    initial_values = {
        "photo": stored("ada-portrait.jpg"),
        "cover": stored("field-season-cover.jpg"),
    }


class HorizontalForm(SampleForm):
    """The thumbnail beside the input, where there is room for both."""

    photo = forms.ImageField(
        label="Profile photo",
        widget=ImageInput(horizontal=True),
        required=False,
        help_text='The rest sits in the middle, align="middle".',
    )
    top = forms.ImageField(
        label="Cover image",
        widget=ImageInput(horizontal=True, align="top", show_file_name=True),
        required=False,
        help_text='align="top"',
    )
    bottom = forms.ImageField(
        label="Station badge",
        widget=ImageInput(horizontal=True, align="bottom", height=8),
        required=False,
        help_text='align="bottom", height=8',
    )
    avatar = forms.ImageField(
        label="Avatar",
        widget=ImageInput(horizontal=True, show_input=False, aspect_ratio=1),
        required=False,
        help_text="horizontal=True with show_input=False.",
    )

    initial_values = {
        "photo": stored("ada-portrait.jpg"),
        "top": stored("field-season-cover.jpg"),
        "avatar": stored("ada-portrait.jpg"),
    }


class SizesForm(SampleForm):
    """The same image at three heights."""

    small = forms.ImageField(
        label="Small",
        widget=ImageInput(height=4, aspect_ratio=1, horizontal=True),
        required=False,
        help_text="height=4",
    )
    default = forms.ImageField(
        label="Default",
        widget=ImageInput(aspect_ratio=1, horizontal=True),
        required=False,
        help_text="height=6, the default",
    )
    large = forms.ImageField(
        label="Large",
        widget=ImageInput(height=12, aspect_ratio=1, horizontal=True),
        required=False,
        help_text="height=12",
    )

    initial_values = {
        "small": stored("ada-portrait.jpg"),
        "default": stored("ada-portrait.jpg"),
        "large": stored("ada-portrait.jpg"),
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


class PickerSentBackForm(SentBackForm):
    """The same form sent back, with the thumbnails as the pickers."""

    photo = forms.ImageField(
        label="Profile photo",
        widget=ImageInput(show_input=False, aspect_ratio=1),
        required=False,
    )
    badge = forms.ImageField(
        label="Station badge", widget=ImageInput(show_input=False, aspect_ratio=1)
    )
