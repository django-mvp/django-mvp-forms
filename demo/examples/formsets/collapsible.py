"""The forms of a stacked formset drawn as collapsible panels, with three kinds of legend."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory

from mvp_forms.choices import FormChoices, StackedForms

ROLES = [("", "---------"), ("lead", "Lead"), ("member", "Member"), ("guest", "Guest")]


class MemberForm(forms.Form):
    """One member of a team."""

    name = forms.CharField()
    email = forms.EmailField(help_text="Invitations are sent here.")
    role = forms.ChoiceField(choices=ROLES)


MemberFormSet = formset_factory(MemberForm, extra=1, can_delete=True)

MEMBERS = [
    {"name": "Ada Lovelace", "email": "ada@example.com", "role": "lead"},
    {"name": "Charles Babbage", "email": "charles@example.com", "role": "member"},
]


def sent_back():
    """Return the team as if sent with a mistyped email in the second member."""
    data = {
        "form-TOTAL_FORMS": "3",
        "form-INITIAL_FORMS": "2",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    for index, member in enumerate(MEMBERS):
        for name, value in member.items():
            data[f"form-{index}-{name}"] = value
    data["form-1-email"] = "charles.example.com"
    return data


class NamedHelper(FormHelper):
    """Each member closed, under its own name, and an empty form under "New member"."""

    def __init__(self, *args, **kwargs):
        """State the legend and add the button."""
        super().__init__(*args, **kwargs)
        self.attrs = {"novalidate": True}
        self.daisyui = FormChoices(
            forms=StackedForms(
                legend='{{ form.name.value|default:"New member" }}',
                collapsible=True,
            )
        )
        self.add_input(Submit("submit", "Save the team"))


class NumberedHelper(FormHelper):
    """Each member open, numbered by its place in the formset."""

    def __init__(self, *args, **kwargs):
        """State the legend and add the button."""
        super().__init__(*args, **kwargs)
        self.attrs = {"novalidate": True}
        self.daisyui = FormChoices(
            forms=StackedForms(
                legend="Member {{ number }}", collapsible=True, open=True
            )
        )
        self.add_input(Submit("submit", "Save the team"))


class TitledHelper(FormHelper):
    """Each member a panel that does not collapse, under a legend the developer gives."""

    def __init__(self, *args, **kwargs):
        """State the legend and add the button."""
        super().__init__(*args, **kwargs)
        self.attrs = {"novalidate": True}
        self.daisyui = FormChoices(forms=StackedForms(legend="Team member"))
        self.add_input(Submit("submit", "Save the team"))
