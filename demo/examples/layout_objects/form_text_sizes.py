"""The three sizes of form text, plain and muted, beside a field's help text and a legend."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from mvp_forms.layout import Fieldset, FormText

LONG = (
    "A longer passage wraps onto as many lines as it needs and never makes the "
    "form wider than a narrow page. It can hold markup, such as a "
    '<a class="link" href="#">link</a> or <strong>a word in bold</strong>.'
)


class FormTextSizesForm(forms.Form):
    """Nothing to send: the page is for comparing the sizes."""

    reference = forms.CharField(
        required=False, help_text="This is a field's help text, for comparison."
    )

    def __init__(self, *args, **kwargs):
        """Draw each size, short and long, inside a fieldset with a legend."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                "A legend, for comparison",
                "reference",
                FormText('Small: <code>size="small"</code>', size="small"),
                FormText(LONG, size="small"),
                FormText(
                    'Small, muted: <code>size="small", variant="muted"</code>',
                    size="small",
                    variant="muted",
                ),
                FormText(LONG, size="small", variant="muted"),
                FormText("No size"),
                FormText(LONG),
                FormText('Muted: <code>variant="muted"</code>', variant="muted"),
                FormText(LONG, variant="muted"),
                FormText('Large: <code>size="large"</code>', size="large"),
                FormText(LONG, size="large"),
                FormText(
                    'Large, muted: <code>size="large", variant="muted"</code>',
                    size="large",
                    variant="muted",
                ),
                FormText(LONG, size="large", variant="muted"),
            ),
        )
