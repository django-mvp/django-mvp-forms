"""The lines of an order, each drawn as a form under the last."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory

ITEMS = [("", "---------"), ("pen", "Pen"), ("ink", "Ink"), ("paper", "Paper")]


class OrderLineForm(forms.Form):
    """One line of an order."""

    item = forms.ChoiceField(choices=ITEMS)
    quantity = forms.IntegerField(min_value=1, help_text="How many to order.")
    unit_price = forms.DecimalField(min_value=0, decimal_places=2)


OrderLineFormSet = formset_factory(OrderLineForm, extra=2, can_delete=True)


class OrderHelper(FormHelper):
    """Draws the formset stacked, which is the default, with one submit button."""

    def __init__(self, *args, **kwargs):
        """Add the button."""
        super().__init__(*args, **kwargs)
        self.attrs = {"novalidate": True}
        self.add_input(Submit("submit", "Place the order"))
