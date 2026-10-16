"""A choice drawn as stars and a number drawn as a slider."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from mvp_forms.choices import Choice, FormChoices

STARS = [(count, f"{count} stars") for count in range(1, 6)]


class ReviewForm(forms.Form):
    """Two ratings and a range."""

    score = forms.ChoiceField(choices=STARS)
    comfort = forms.ChoiceField(choices=[("", "No answer"), *STARS], required=False)
    volume = forms.IntegerField(min_value=0, max_value=100, step_size=5, initial=50)

    def __init__(self, *args, **kwargs):
        """State a rating by name, a rating in the layout and a range."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.daisyui = FormChoices(
            color="primary", fields={"score": Choice(drawing="rating")}
        )
        self.helper.layout = Layout(
            "score",
            Choice("comfort", drawing="rating"),
            Choice("volume", drawing="range", color="accent"),
        )
        self.helper.add_input(Submit("submit", "Send"))
