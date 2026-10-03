"""The forms the demo project draws."""

from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    Button,
    ButtonHolder,
    Column,
    Div,
    Fieldset,
    Hidden,
    Layout,
    MultiField,
    Reset,
    Row,
    Submit,
)
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory
from django.utils.translation import gettext_lazy as _


class TextInputsForm(forms.Form):
    """One field of each text input kind the pack draws.

    Every field is optional and carries no help text until the constructor says
    otherwise, so the same form can stand for each state a field can be in. Its
    ``clean`` always fails, so a bound form shows both a field's errors and one
    that belongs to the form as a whole.
    """

    text = forms.CharField(label=_("Text"))
    email = forms.EmailField(label=_("Email"))
    url = forms.URLField(label=_("URL"))
    number = forms.IntegerField(label=_("Number"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    date = forms.DateField(label=_("Date"))
    time = forms.TimeField(label=_("Time"))
    date_time = forms.DateTimeField(label=_("Date and time"))
    textarea = forms.CharField(label=_("Textarea"), widget=forms.Textarea)

    help_texts = {
        "text": _("A line of free text."),
        "email": _("An address such as name@example.com."),
        "url": _("An address that starts with http:// or https://."),
        "number": _("A whole number."),
        "password": _("Kept out of the page when the form is drawn again."),
        "date": _("A date such as 2026-10-03."),
        "time": _("A time such as 14:30."),
        "date_time": _("A date and a time such as 2026-10-03 14:30."),
        "textarea": _("Several lines of free text."),
    }

    def __init__(self, *args, required=False, with_help=False, **kwargs):
        """Switch every field's required flag and help text at once.

        Args:
            *args: Passed to ``forms.Form``.
            required: Whether every field is required.
            with_help: Whether every field carries its help text.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.required = required
            field.help_text = self.help_texts[name] if with_help else ""

    def clean(self):
        """Fail every time, so the form always has an error of its own.

        Raises:
            ValidationError: Always.
        """
        raise ValidationError(
            _("The form as a whole was refused, whatever its fields hold."),
            code="demo_refusal",
        )


class ChoiceInputsForm(forms.Form):
    """One field of each choice, boolean, file and hidden input the pack draws.

    Every field is optional, enabled and without help text until the constructor
    says otherwise, so the same form can stand for each state a field can be in.
    """

    select = forms.ChoiceField(
        label=_("Select"), choices=[("", "---------"), ("a", "A"), ("b", "B")]
    )
    grouped_select = forms.ChoiceField(
        label=_("Select with groups"),
        choices=[
            ("", "---------"),
            ("Fruit", [("apple", "Apple"), ("pear", "Pear")]),
            ("Vegetables", [("leek", "Leek"), ("kale", "Kale")]),
        ],
    )
    multiple_select = forms.MultipleChoiceField(
        label=_("Multiple select"), choices=[("a", "A"), ("b", "B"), ("c", "C")]
    )
    null_boolean = forms.NullBooleanField(
        label=_("Null boolean"), widget=forms.NullBooleanSelect
    )
    date = forms.DateField(
        label=_("Date as three selects"),
        widget=forms.SelectDateWidget(years=range(2025, 2031)),
    )
    radio = forms.ChoiceField(
        label=_("Radio group"),
        choices=[("a", "A"), ("b", "B"), ("c", "C")],
        widget=forms.RadioSelect,
    )
    checkbox = forms.BooleanField(label=_("Checkbox"))
    checkbox_group = forms.MultipleChoiceField(
        label=_("Checkbox group"),
        choices=[("a", "A"), ("b", "B"), ("c", "C")],
        widget=forms.CheckboxSelectMultiple,
    )
    file = forms.FileField(label=_("File"), widget=forms.FileInput)
    clearable_file = forms.FileField(label=_("Clearable file"))
    hidden = forms.IntegerField(label=_("Hidden"), widget=forms.HiddenInput)

    help_texts = {
        "select": _("One of two choices."),
        "grouped_select": _("A choice from named groups."),
        "multiple_select": _("Any number of choices."),
        "null_boolean": _("Yes, no or unknown."),
        "date": _("A year, a month and a day."),
        "radio": _("Exactly one of three."),
        "checkbox": _("Tick it, or leave it."),
        "checkbox_group": _("Any number of three."),
        "file": _("A file to upload."),
        "clearable_file": _("A file to upload, or to remove."),
        "hidden": _("Nobody sees this."),
    }

    def __init__(
        self, *args, required=False, with_help=False, disabled=False, **kwargs
    ):
        """Switch every field's required, help text and disabled flags at once.

        Args:
            *args: Passed to ``forms.Form``.
            required: Whether every field is required.
            with_help: Whether every field carries its help text.
            disabled: Whether every field is disabled.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.required = required
            field.disabled = disabled
            field.help_text = self.help_texts[name] if with_help else ""

    def clean_null_boolean(self):
        """Refuse "unknown" when the field is required.

        Django's own field accepts all three answers, so without this the error
        state would show the select with no error.

        Returns:
            The answer given.

        Raises:
            ValidationError: When the field is required and the answer is unknown.
        """
        value = self.cleaned_data["null_boolean"]
        if value is None and self.fields["null_boolean"].required:
            raise ValidationError(_("Choose yes or no."), code="required")
        return value


class TextStatesForm(forms.Form):
    """A text input and a textarea, drawn once disabled and once read-only."""

    text = forms.CharField(label=_("Text"))
    textarea = forms.CharField(label=_("Textarea"), widget=forms.Textarea)

    def __init__(self, *args, disabled=False, read_only=False, **kwargs):
        """Switch the state both fields are in.

        Args:
            *args: Passed to ``forms.Form``.
            disabled: Whether both fields are disabled.
            read_only: Whether both widgets carry the browser's ``readonly``.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.disabled = disabled
            if read_only:
                field.widget.attrs["readonly"] = True


class LayoutObjectsForm(forms.Form):
    """A form whose layout uses every layout object the pack draws so far.

    Its layout is built for each instance, and every id and button name in it
    carries the form's prefix, so two of these forms on one page repeat no id.
    The form must be given a prefix.
    """

    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    email = forms.EmailField(label=_("Email"))
    phone = forms.CharField(label=_("Phone"))
    note = forms.CharField(label=_("Note"))

    def __init__(self, *args, form_tag=True, **kwargs):
        """Build the layout, with the prefix in every id and button name.

        Args:
            *args: Passed to ``forms.Form``.
            form_tag: Whether the helper draws the form element. The form that
                already fails has none, so its buttons are drawn on their own.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_tag = form_tag
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Fieldset(
                _("Details for {{ owner }}"),
                Row(
                    Column("first_name", css_id=f"{prefix}-first"),
                    Column("last_name", css_id=f"{prefix}-last"),
                    css_id=f"{prefix}-row",
                ),
                HTML(
                    '<p id="{}-aside">{}</p>'.format(
                        prefix, _("Prepared for {{ owner }}.")
                    )
                ),
                MultiField(
                    _("How to reach you"),
                    "email",
                    "phone",
                    css_id=f"{prefix}-contact",
                ),
                Div("note", css_id=f"{prefix}-more"),
                css_id=f"{prefix}-details",
            ),
            Hidden(f"{prefix}-step", "details"),
            FormActions(
                Submit(f"{prefix}-submit", _("Submit")),
                Reset(f"{prefix}-reset", _("Reset")),
                Button(f"{prefix}-button", _("Button")),
                StrictButton(_("Strict button"), css_id=f"{prefix}-strict"),
                css_id=f"{prefix}-actions",
            ),
        )


class HelperButtonsForm(forms.Form):
    """A form with no layout whose buttons were added to its helper.

    It is a GET form, so submitting it only reloads the page.
    """

    first_name = forms.CharField(label=_("First name"), required=False)
    last_name = forms.CharField(label=_("Last name"), required=False)

    def __init__(self, *args, **kwargs):
        """Add a submit and a reset button to the helper, named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "get"
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))
        self.helper.add_input(Reset(f"{self.prefix}-reset", _("Reset")))


class RowButtonsForm(forms.Form):
    """A small layout with two fields straight in a row and a button holder.

    It is a GET form, so submitting it only reloads the page.
    """

    first_name = forms.CharField(label=_("First name"), required=False)
    last_name = forms.CharField(label=_("Last name"), required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_method = "get"
        self.helper.layout = Layout(
            Row("first_name", "last_name", css_id=f"{prefix}-row"),
            ButtonHolder(
                Submit(f"{prefix}-submit", _("Submit")), css_id=f"{prefix}-actions"
            ),
        )


ORDER_LINE_LIMIT = 10000
ORDER_ITEMS = [
    ("", "---------"),
    ("pen", _("Pen")),
    ("ink", _("Ink")),
    ("paper", _("Paper")),
]


class OrderLineForm(forms.Form):
    """One line of an order: an item, a quantity, a unit price and a reference.

    The quantity must be at least one, which is an error on the field. A line
    whose total passes ``ORDER_LINE_LIMIT`` is an error on the form as a whole.
    """

    item = forms.ChoiceField(label=_("Item"), choices=ORDER_ITEMS)
    quantity = forms.IntegerField(
        label=_("Quantity"), min_value=1, help_text=_("How many to order.")
    )
    unit_price = forms.DecimalField(
        label=_("Unit price"), min_value=0, decimal_places=2
    )
    reference = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        """Refuse a line whose total passes the limit.

        Returns:
            The cleaned data.

        Raises:
            ValidationError: When quantity times unit price passes the limit.
        """
        cleaned = super().clean()
        quantity = cleaned.get("quantity")
        unit_price = cleaned.get("unit_price")
        if quantity and unit_price and quantity * unit_price > ORDER_LINE_LIMIT:
            raise ValidationError(
                _("A line may not total more than %(limit)s."),
                code="over_limit",
                params={"limit": ORDER_LINE_LIMIT},
            )
        return cleaned


class BaseOrderLineFormSet(BaseFormSet):
    """The lines of an order, none of which may repeat an item."""

    def clean(self):
        """Refuse the same item on two lines.

        Raises:
            ValidationError: When two lines that are kept name the same item.
        """
        super().clean()
        items = [
            form.cleaned_data["item"]
            for form in self.forms
            if getattr(form, "cleaned_data", None)
            and form.cleaned_data.get("item")
            and not form.cleaned_data.get("DELETE")
        ]
        if len(items) != len(set(items)):
            raise ValidationError(
                _("Each item may be ordered on one line only."),
                code="duplicate_item",
            )


OrderLineFormSet = formset_factory(
    OrderLineForm, BaseOrderLineFormSet, extra=3, can_delete=True, can_order=True
)


class StackedOrderHelper(FormHelper):
    """Draws the order lines stacked, with one submit button.

    The submit button's name carries the formset's prefix, so two of these on
    one page repeat no id.
    """

    def __init__(self, prefix, *args, form_tag=True, **kwargs):
        """Name the submit button by the prefix.

        Args:
            prefix: The prefix of the formset this helper draws.
            *args: Passed to ``FormHelper``.
            form_tag: Whether the helper draws the form element. The formset that
                already fails has none.
            **kwargs: Passed to ``FormHelper``.
        """
        super().__init__(*args, **kwargs)
        self.form_tag = form_tag
        self.attrs = {"novalidate": True}
        self.add_input(Submit(f"{prefix}-submit", _("Submit")))


class TableOrderHelper(StackedOrderHelper):
    """Draws the order lines as a table, with one submit button."""

    template = "daisyui/table_inline_formset.html"
