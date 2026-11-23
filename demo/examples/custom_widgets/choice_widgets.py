"""A choice drawn as a scale, pills, chips or cards, and the settings each takes."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe

from mvp_forms.choices import Choice, FormChoices
from mvp_forms.widgets import (
    CardSelect,
    CardSelectMultiple,
    ChipSelect,
    ChipSelectMultiple,
    PillSelect,
    PillSelectMultiple,
    ScaleSelect,
)

SCORES = [(score, str(score)) for score in range(11)]
COLOURS = [
    ("red", "Red"),
    ("orange", "Orange"),
    ("green", "Green"),
    ("blue", "Blue"),
    ("violet", "Violet"),
]
INTERESTS = [
    ("cycling", "Cycling"),
    ("cooking", "Cooking"),
    ("gardening", "Gardening"),
    ("photography", "Photography"),
    ("chess", "Chess"),
    ("hiking", "Hiking"),
    ("pottery", "Pottery"),
    ("woodworking", "Woodworking, joinery and other work with hand tools"),
    ("birdwatching", "Birdwatching"),
    ("astronomy", "Astronomy"),
    ("baking", "Baking"),
    ("sailing", "Sailing"),
]
USUAL_INTERESTS = ["cycling", "cooking", "gardening"]
PLANS = [("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")]
DELIVERY = [
    ("post", "Post"),
    ("courier", "Courier"),
    ("collect", "Collect in store"),
    ("locker", "Parcel locker"),
]
ADDONS = [
    ("gift", "Gift wrap"),
    ("insurance", "Insurance"),
    ("signature", "Signature on delivery"),
    ("express", "Express handling"),
]

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round" class="size-6" aria-hidden="true">{}</svg>'
)
PLAN_ICONS = {
    "basic": mark_safe(SVG.format('<path d="M4 12h16"/>')),  # noqa: S308
    "standard": mark_safe(SVG.format('<path d="M4 9h16M4 15h16"/>')),  # noqa: S308
    "premium": mark_safe(  # noqa: S308
        SVG.format(
            '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1'
            'L3.2 9.5l6.1-.9z"/>'
        )
    ),
}
PLAN_DESCRIPTIONS = {
    "basic": "One user and the essentials.",
    "standard": "Five users and shared folders.",
    "premium": "Unlimited users, with priority support.",
}
PLAN_META = {"basic": "Free", "standard": "9 a month", "premium": "29 a month"}
DELIVERY_DESCRIPTIONS = {
    "post": "Three to five days.",
    "courier": "Next day, to your door.",
    "collect": "Ready in an hour.",
    "locker": "Open any time of day.",
}


class DemoForm(forms.Form):
    """A form with the helper every example in this module needs."""

    def __init__(self, *args, **kwargs):
        """Add the helper and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit("submit", "Send"))


class ScaleForm(DemoForm):
    """A scale with words at its ends, one with none and one that can be cleared."""

    recommend = forms.ChoiceField(
        label="How likely are you to recommend us?",
        choices=SCORES,
        widget=ScaleSelect(low="Not at all likely", high="Extremely likely"),
        initial="7",
    )
    rating = forms.ChoiceField(
        label="Rate the service",
        choices=[(score, str(score)) for score in range(1, 6)],
        widget=ScaleSelect,
    )
    effort = forms.ChoiceField(
        label="How easy was it?",
        choices=[("", "No answer"), *[(score, str(score)) for score in range(1, 8)]],
        widget=ScaleSelect(low="Very hard", high="Very easy"),
        required=False,
        help_text="The choice with no value is drawn after the scale, to clear it.",
    )


class PillsForm(DemoForm):
    """Pills for one choice and for several, and one that can be cleared."""

    colour = forms.ChoiceField(
        label="Favourite colour", choices=COLOURS, widget=PillSelect, initial="green"
    )
    shades = forms.MultipleChoiceField(
        label="Colours you like",
        choices=COLOURS,
        widget=PillSelectMultiple,
        initial=["red", "blue"],
    )
    accent = forms.ChoiceField(
        label="Accent colour",
        choices=[("", "No accent"), *COLOURS],
        widget=PillSelect,
        required=False,
        help_text="Choose No accent to clear the field.",
    )


class ChipsForm(DemoForm):
    """Chips that show a long label in full, with a fold and a clearing choice."""

    interest = forms.ChoiceField(
        label="Main interest",
        choices=[("", "None of these"), *INTERESTS],
        widget=ChipSelect(show=USUAL_INTERESTS),
        required=False,
        help_text="A choice that is chosen stays on show.",
    )
    interests = forms.MultipleChoiceField(
        label="Interests",
        choices=INTERESTS,
        widget=ChipSelectMultiple(show=USUAL_INTERESTS),
        initial=["pottery", "cooking"],
    )
    hobbies = forms.MultipleChoiceField(
        label="Hobbies",
        choices=INTERESTS,
        widget=ChipSelectMultiple(show=USUAL_INTERESTS, fold_label="Other hobbies"),
        required=False,
        help_text="The button after the chips has the words you give.",
    )


class PersonalFoldForm(DemoForm):
    """A fold set in the form's own ``__init__`` for the person using the form."""

    interests = forms.MultipleChoiceField(
        label="Interests", choices=INTERESTS, widget=ChipSelectMultiple, required=False
    )

    def __init__(self, *args, usual=("hiking", "birdwatching"), **kwargs):
        """Keep the choices this person uses most on show, on this form alone."""
        super().__init__(*args, **kwargs)
        self.fields["interests"].widget.show = set(usual)


class CardsForm(DemoForm):
    """Cards in one, two and three columns, with icons, descriptions and a line."""

    plan = forms.ChoiceField(
        label="Plan",
        choices=PLANS,
        widget=CardSelect(
            columns=3,
            descriptions=PLAN_DESCRIPTIONS,
            icons=PLAN_ICONS,
            meta=PLAN_META,
        ),
        initial="standard",
        help_text="Three across on a wide screen, and one on a narrow one.",
    )
    delivery = forms.ChoiceField(
        label="Delivery",
        choices=DELIVERY,
        widget=CardSelect(columns=2, descriptions=DELIVERY_DESCRIPTIONS),
        help_text="Two across.",
    )
    extras = forms.MultipleChoiceField(
        label="Extras",
        choices=ADDONS,
        widget=CardSelectMultiple(columns=1),
        required=False,
        help_text="One across, with several chosen.",
    )


class CardMarkForm(DemoForm):
    """Cards with the mark at the start: mark, icon, then text."""

    plan = forms.ChoiceField(
        label="Plan",
        choices=PLANS,
        widget=CardSelect(
            columns=2,
            mark="start",
            descriptions=PLAN_DESCRIPTIONS,
            icons=PLAN_ICONS,
            meta=PLAN_META,
        ),
        initial="standard",
        help_text="The radio is drawn before the icon.",
    )
    extras = forms.MultipleChoiceField(
        label="Extras",
        choices=ADDONS,
        widget=CardSelectMultiple(columns=1, mark="start"),
        required=False,
        help_text="The checkbox is drawn before the text.",
    )


class FoldedCardsForm(DemoForm):
    """Cards with a fold and a choice that clears the field."""

    delivery = forms.ChoiceField(
        label="Delivery",
        choices=[("", "Decide later"), *DELIVERY],
        widget=CardSelect(
            show=["post"], descriptions=DELIVERY_DESCRIPTIONS, fold_label="More ways"
        ),
        required=False,
    )
    extras = forms.MultipleChoiceField(
        label="Extras",
        choices=ADDONS,
        widget=CardSelectMultiple(show=["gift"]),
        required=False,
    )


class StatesForm(DemoForm):
    """A field in error and a disabled field, drawn beside a field that is fine."""

    recommend = forms.ChoiceField(
        label="How likely are you to recommend us?",
        choices=SCORES,
        widget=ScaleSelect(low="Not at all likely", high="Extremely likely"),
        help_text="Required. Send the form with nothing chosen to see the error.",
    )
    interests = forms.MultipleChoiceField(
        label="Interests",
        choices=INTERESTS,
        widget=ChipSelectMultiple(show=USUAL_INTERESTS),
        help_text="Required.",
    )
    delivery = forms.ChoiceField(
        label="Delivery",
        choices=DELIVERY,
        widget=CardSelect(descriptions=DELIVERY_DESCRIPTIONS),
        initial="courier",
        disabled=True,
        help_text="A disabled field.",
    )
    colour = forms.ChoiceField(
        label="Favourite colour",
        choices=COLOURS,
        widget=PillSelect,
        initial="blue",
        disabled=True,
        help_text="A disabled field.",
    )


class SmallForm(DemoForm):
    """The form states a small size and the accent colour, and one field its own."""

    recommend = forms.ChoiceField(
        label="How likely are you to recommend us?",
        choices=SCORES,
        widget=ScaleSelect(low="Not at all likely", high="Extremely likely"),
        initial="4",
    )
    colour = forms.ChoiceField(
        label="Favourite colour", choices=COLOURS, widget=PillSelect, initial="red"
    )
    interests = forms.MultipleChoiceField(
        label="Interests",
        choices=INTERESTS,
        widget=ChipSelectMultiple(show=USUAL_INTERESTS),
        initial=["chess"],
    )
    plan = forms.ChoiceField(
        label="Plan",
        choices=PLANS,
        widget=CardSelect(columns=3, descriptions=PLAN_DESCRIPTIONS),
        initial="basic",
    )

    def __init__(self, *args, **kwargs):
        """State the form's size and colour, and the plan's own colour."""
        super().__init__(*args, **kwargs)
        self.helper.daisyui = FormChoices(
            size="sm", color="accent", fields={"plan": Choice(color="secondary")}
        )


class ParcelForm(forms.Form):
    """One parcel of an order, with a fold in each row of a formset."""

    delivery = forms.ChoiceField(
        label="Delivery", choices=DELIVERY, widget=CardSelect(columns=2)
    )
    extras = forms.MultipleChoiceField(
        label="Extras",
        choices=ADDONS,
        widget=ChipSelectMultiple(show=["gift"]),
        required=False,
    )


ParcelFormSet = formset_factory(ParcelForm, extra=1)


class ParcelHelper(FormHelper):
    """Draws the formset's rows with no ``form`` element, which the page writes."""

    def __init__(self, *args, **kwargs):
        """Leave the ``form`` element and the buttons to the page."""
        super().__init__(*args, **kwargs)
        self.form_tag = False
