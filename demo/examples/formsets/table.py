"""The lines of an order, drawn as the rows of a table."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory

from mvp_forms.choices import FormChoices, TablePanel

ITEMS = [("", "---------"), ("pen", "Pen"), ("ink", "Ink"), ("paper", "Paper")]


class OrderLineForm(forms.Form):
    """One line of an order."""

    item = forms.ChoiceField(choices=ITEMS)
    quantity = forms.IntegerField(min_value=1, help_text="How many to order.")
    unit_price = forms.DecimalField(min_value=0, decimal_places=2)


OrderLineFormSet = formset_factory(OrderLineForm, extra=2, can_delete=True)


class OrderHelper(FormHelper):
    """Draws the formset as a table, with one submit button."""

    template = "daisyui/table_inline_formset.html"

    def __init__(self, *args, **kwargs):
        """Add the button."""
        super().__init__(*args, **kwargs)
        self.attrs = {"novalidate": True}
        self.add_input(Submit("submit", "Place the order"))


LINES = [
    {"item": "pen", "quantity": 12, "unit_price": "1.20"},
    {"item": "ink", "quantity": 3, "unit_price": "4.50"},
]


def sent_back():
    """Return the order as if sent with no quantity on its second line."""
    data = {
        "form-TOTAL_FORMS": "3",
        "form-INITIAL_FORMS": "2",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    for index, line in enumerate(LINES):
        for name, value in line.items():
            data[f"form-{index}-{name}"] = str(value)
    data["form-1-quantity"] = ""
    return data


class TitledHelper(OrderHelper):
    """The table in a panel under a legend, which does not collapse."""

    def __init__(self, *args, **kwargs):
        """State the legend."""
        super().__init__(*args, **kwargs)
        self.daisyui = FormChoices(table=TablePanel(legend="Order lines"))


class CollapsibleHelper(OrderHelper):
    """The table closed, with how many lines it holds in its legend."""

    def __init__(self, *args, **kwargs):
        """State the legend."""
        super().__init__(*args, **kwargs)
        self.daisyui = FormChoices(
            table=TablePanel(
                legend="Order lines ({{ formset.initial_form_count }})",
                collapsible=True,
            )
        )
