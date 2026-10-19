# Image input

An `ImageField` is drawn as a plain clearable file input unless you give it a
widget: a link to the stored file, a checkbox to clear it and a file input.
`ImageInput` shows the image itself. The stored image is drawn as a thumbnail,
and a file you choose takes its place before the form is sent.

```python
from mvp_forms.widgets import ImageInput


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["photo", "banner"]
        widgets = {
            "photo": ImageInput(show_input=False, aspect_ratio=1),
            "banner": ImageInput(aspect_ratio=3),
        }
```

The thumbnail's alternative text is the field's label. The widget's script comes
with the form's media, and needs nothing else on the page.

| Option | Default | What it does |
| --- | --- | --- |
| `aspect_ratio` | none | The thumbnail's width over its height, such as `3` or `16 / 9`. The image fills that shape. Without it the thumbnail is square and the image is shown whole. |
| `show_input` | `True` | `False` leaves out the file input. The thumbnail opens the file picker. |
| `show_file_name` | `False` | `True` names the stored file above the input, as a link to it. |
| `horizontal` | `False` | `True` sets the thumbnail beside the input where there is room, and above it where there is not. |

## A record with pictures

Choose a new file for either image and the thumbnail changes straight away,
with a line saying it is saved when the form is sent. **Undo** puts the stored
image back. Tick **Remove image** and the thumbnail fades. Choosing a file and
removing the image cannot both be asked for, so doing one undoes the other.

The field report is a `FileField`, which keeps the plain clearable file input.

```{live-example} /examples/image-input/
:title: Two stored images and a stored file

../../examples/custom_widgets/image_input.py
```

## The image as the picker

With `show_input=False` there is no file input to see. Click the thumbnail, or
tab to it and press Enter, to choose a file. An empty one says **Add image**,
and a stored one shows **Change image** over it while the pointer or the focus
is on it.

```{live-example} /examples/image-input-picker/
:title: Click the image to change it

../../examples/custom_widgets/image_input.py
```

## Shaped like where it is shown

`aspect_ratio` gives the thumbnail the shape the image has in your site, so a
banner is seen cropped the way visitors will see it. The thumbnail keeps its
height and takes the width the shape needs.

```{live-example} /examples/image-input-shapes/
:title: A banner, a video still and a portrait

../../examples/custom_widgets/image_input.py
```

## Beside the input

`horizontal=True` puts the thumbnail beside the input. On a narrow screen the
input moves under it.

```{live-example} /examples/image-input-horizontal/
:title: Thumbnail and input side by side

../../examples/custom_widgets/image_input.py
```

## A new record

With nothing stored, the thumbnail says so. A required field has no remove
checkbox, as with any clearable file input.

```{live-example} /examples/image-input-new/
:title: Nothing stored yet

../../examples/custom_widgets/image_input.py
```

## Shapes and states

A small image is shown at its own size and never stretched. A tall or wide one
is shown whole, fitted inside the thumbnail. A stored file that is no longer on
disk is shown as missing, not as a broken picture, and a long file name wraps.

```{live-example} /examples/image-input-states/
:title: Small, tall, missing and disabled

../../examples/custom_widgets/image_input.py
```

## Sent back with errors

This form arrives as if it had just been sent with a text file for the photo and
no badge. The stored photo is still shown, so it is clear what is kept if the
form is sent again.

```{live-example} /examples/image-input-sent-back/
:title: A file that is not an image, and a required image missing

../../examples/custom_widgets/image_input.py
../../examples/views.py
```
