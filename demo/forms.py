"""The forms the demo project draws."""

from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    Alert,
    AppendedText,
    FieldWithButtons,
    FormActions,
    InlineCheckboxes,
    InlineField,
    InlineRadios,
    Modal,
    PrependedAppendedText,
    PrependedText,
    StrictButton,
    Tab,
    TabHolder,
    UneditableField,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    Button,
    ButtonHolder,
    Column,
    Div,
    Field,
    Fieldset,
    Hidden,
    Layout,
    MultiField,
    MultiWidgetField,
    Reset,
    Row,
    Submit,
)
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from mvp_forms.choices import Choice, FormChoices, Modifiers
from mvp_forms.layout import Join
from mvp_forms.widgets import (
    EnumBlock,
    PatternMaskInput,
    RangeBlock,
)

LONG_OPTION = _(
    "C, with a label long enough that a narrow page shows it wrapping onto "
    "several lines beside its input"
)


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
        "text": _(
            "A line of free text. This help text is a long one, so that a narrow "
            "page shows it wrapping onto several lines under its input."
        ),
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
        choices=[("a", "A"), ("b", "B"), ("c", LONG_OPTION)],
        widget=forms.RadioSelect,
    )
    checkbox = forms.BooleanField(label=_("Checkbox"))
    checkbox_group = forms.MultipleChoiceField(
        label=_("Checkbox group"),
        choices=[("a", "A"), ("b", "B"), ("c", LONG_OPTION)],
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


class PlaceholdersForm(forms.Form):
    """A text input and a textarea, each showing a placeholder."""

    text = forms.CharField(
        label=_("Text"),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Some text")}),
    )
    textarea = forms.CharField(
        label=_("Textarea"),
        required=False,
        widget=forms.Textarea(attrs={"placeholder": _("Some lines of text")}),
    )


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


class TabsForm(forms.Form):
    """A form whose fields sit behind three tabs.

    The first tab holds an optional field and the second and third hold required
    ones, so a bound form with nothing in it opens the second tab. Its layout is
    built for each instance, and every id and button name in it carries the form's
    prefix, so two of these forms on one page repeat no id. The form must be given
    a prefix.
    """

    name = forms.CharField(label=_("Name"), required=False)
    street = forms.CharField(label=_("Street"))
    city = forms.CharField(label=_("City"))
    note = forms.CharField(label=_("Note"))

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in every id and button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            TabHolder(
                Tab(_("Profile"), "name", css_id=f"{prefix}-profile"),
                Tab(_("Address"), "street", "city", css_id=f"{prefix}-address"),
                Tab(_("Notes"), "note", css_id=f"{prefix}-notes"),
                css_id=f"{prefix}-tabs",
            ),
        )
        if posts:
            self.helper.add_input(Submit(f"{prefix}-submit", _("Submit")))


class AccordionForm(forms.Form):
    """A form whose fields sit in three accordion groups.

    The first group holds an optional field, the second an optional one and the
    third a required one, so a bound form with nothing in it opens the third. Its
    layout is built for each instance, and every id and button name in it carries
    the form's prefix, so two of these forms on one page repeat no id. The form
    must be given a prefix.
    """

    name = forms.CharField(label=_("Name"), required=False)
    street = forms.CharField(label=_("Street"), required=False)
    note = forms.CharField(label=_("Note"))

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(_("Profile"), "name", css_id=f"{prefix}-profile"),
                AccordionGroup(_("Address"), "street", css_id=f"{prefix}-address"),
                AccordionGroup(_("Notes"), "note", css_id=f"{prefix}-notes"),
                css_id=f"{prefix}-groups",
            ),
        )
        self.helper.add_input(Submit(f"{prefix}-submit", _("Submit")))


class ChosenGroupsForm(forms.Form):
    """A form whose developer decided which of two groups is open.

    The first group is given ``active=False``, so it starts closed although it is
    first, and the second is given ``active=True``. The form is drawn without a
    form element. Every id carries the form's prefix, which it must be given.
    """

    name = forms.CharField(label=_("Name"), required=False)
    street = forms.CharField(label=_("Street"), required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(
                    _("Closed"), "name", active=False, css_id=f"{prefix}-closed"
                ),
                AccordionGroup(
                    _("Open"), "street", active=True, css_id=f"{prefix}-open"
                ),
                css_id=f"{prefix}-groups",
            ),
        )


class ModalForm(forms.Form):
    """A form whose address fields sit in a modal.

    The name is outside the modal and the street and the city, both required, are
    inside it, so a bound form with nothing in it comes back with the modal open.
    The pack draws nothing that opens the modal: the page does, by ``dialog_id``.
    Its layout is built for each instance, and every id and button name in it
    carries the form's prefix, so two of these forms on one page repeat no id. The
    form must be given a prefix.
    """

    name = forms.CharField(label=_("Name"), required=False)
    street = forms.CharField(label=_("Street"))
    city = forms.CharField(label=_("City"))

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            "name",
            Modal(
                "street",
                "city",
                css_id=self.dialog_id,
                title=_("Address"),
                title_id=f"{self.prefix}-title",
            ),
        )
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the control that opens it."""
        return f"{self.prefix}-dialog"


class AlertForm(forms.Form):
    """A form with three alerts between its fields.

    One alert can be dismissed, one is permanent and one carries a daisyUI colour
    modifier. The field is required, so a bound form with nothing in it comes back
    with the alerts drawn again. Its layout is built for each instance, and every
    id and button name in it carries the form's prefix, so two of these forms on
    one page repeat no id. The form must be given a prefix.
    """

    name = forms.CharField(label=_("Name"))

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Alert(
                _("A notice the reader can dismiss."),
                css_id=f"{prefix}-dismissible",
            ),
            Alert(
                _("A notice that stays."),
                dismiss=False,
                css_id=f"{prefix}-permanent",
            ),
            Alert(
                _("A notice with a daisyUI colour."),
                css_class="alert-success",
                css_id=f"{prefix}-coloured",
            ),
            "name",
        )
        self.helper.add_input(Submit(f"{prefix}-submit", _("Submit")))


class AttachedTextForm(forms.Form):
    """A form whose fields have text attached to their inputs.

    Three text inputs take the three layout objects, a prepended text, an
    appended text and both, and a select takes a prepended text. Every field is
    required, so a bound form with nothing in it comes back with an error in each
    decorated frame. Its layout is built for each instance, and every id and
    button name in it carries the form's prefix, so two of these forms on one
    page repeat no id. The form must be given a prefix.
    """

    amount = forms.CharField(label=_("Amount"), help_text=_("In whole units"))
    weight = forms.CharField(label=_("Weight"))
    budget = forms.CharField(label=_("Budget"))
    fruit = forms.ChoiceField(
        label=_("Fruit"),
        choices=[("", "---------"), ("apple", _("Apple")), ("pear", _("Pear"))],
    )

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in every id and button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            PrependedText("amount", "$"),
            AppendedText("weight", "kg"),
            PrependedAppendedText("budget", "$", ".00"),
            PrependedText("fruit", "#"),
        )
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class ChosenForm(forms.Form):
    """A form that states choices for the form and draws no form element.

    None of the forms on the choices page posts anywhere. Every one must be given
    a prefix of its own, so no id repeats on the page.

    Args:
        choices: What the form states for its inputs and buttons, or None.
    """

    def __init__(self, *args, choices=None, **kwargs):
        """Set the helper, with the form's choices when there are any."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        if choices is not None:
            self.helper.daisyui = choices


class PairForm(ChosenForm):
    """One input and one button, small enough to show one choice at a time."""

    name = forms.CharField(label=_("Name"), required=False)

    def __init__(self, *args, **kwargs):
        """Add the button, named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Save")))


class InputKindsForm(ChosenForm):
    """One field of every kind of input that has a size, a colour or a variant.

    Args:
        choices: What the form states for its inputs, or None. A toggle, a rating
            and a range are drawn as such beside it.
    """

    text = forms.CharField(label=_("Text"), required=False)
    textarea = forms.CharField(
        label=_("Textarea"), required=False, widget=forms.Textarea(attrs={"rows": 2})
    )
    select = forms.ChoiceField(
        label=_("Select"), required=False, choices=[("a", "A"), ("b", "B")]
    )
    file = forms.FileField(label=_("File"), required=False, widget=forms.FileInput)
    checkbox = forms.BooleanField(label=_("Checkbox"), required=False)
    toggle = forms.BooleanField(label=_("Toggle"), required=False)
    radio = forms.ChoiceField(
        label=_("Radio group"),
        required=False,
        choices=[("a", "A"), ("b", "B")],
        widget=forms.RadioSelect,
    )
    checkbox_group = forms.MultipleChoiceField(
        label=_("Checkbox group"),
        required=False,
        choices=[("a", "A"), ("b", "B")],
        widget=forms.CheckboxSelectMultiple,
    )
    rating = forms.ChoiceField(
        label=_("Rating"), required=False, choices=[("1", "1"), ("2", "2"), ("3", "3")]
    )
    slider = forms.IntegerField(
        label=_("Range"), required=False, min_value=0, max_value=10
    )

    def __init__(self, *args, choices=None, **kwargs):
        """Draw the toggle, the rating and the range, beside whatever is stated."""
        choices = choices or FormChoices()
        choices.fields.setdefault("toggle", Choice(drawing="toggle"))
        choices.fields.setdefault("rating", Choice(drawing="rating"))
        choices.fields.setdefault("slider", Choice(drawing="range"))
        super().__init__(*args, choices=choices, **kwargs)


class ButtonBarForm(ChosenForm):
    """A bar holding one button in each variant daisyUI has for a button."""

    def __init__(self, *args, **kwargs):
        """Build the layout, with a button for every variant in the table."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            FormActions(
                *[
                    Choice(
                        Button(f"{self.prefix}-{variant}", variant.capitalize()),
                        variant=variant,
                    )
                    for variant in Modifiers.variants[Modifiers.button]
                ]
            )
        )


class PlainButtonsForm(ChosenForm):
    """A bar holding a button in no variant and a disabled one."""

    def __init__(self, *args, **kwargs):
        """Build the layout, with the buttons named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            FormActions(
                Button(f"{self.prefix}-solid", _("Solid")),
                Button(f"{self.prefix}-disabled", _("Disabled"), disabled=True),
            )
        )


class ContainerButtonsForm(ChosenForm):
    """A form with an alert and a modal, whose own buttons take the form's size.

    The pack draws the alert's dismiss button and the modal's close button. The
    pack draws nothing that opens the modal: the page does, by ``dialog_id``.
    The form must be given a prefix.
    """

    name = forms.CharField(label=_("Name"), required=False)
    street = forms.CharField(label=_("Street"), required=False)

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id and button name."""
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper.layout = Layout(
            Alert(_("A notice the reader can dismiss."), css_id=f"{prefix}-notice"),
            "name",
            Modal(
                "street",
                css_id=self.dialog_id,
                title=_("Address"),
                title_id=f"{prefix}-title",
            ),
            FormActions(Submit(f"{prefix}-save", _("Save"))),
        )

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the control that opens it."""
        return f"{self.prefix}-dialog"


class OverrideForm(ChosenForm):
    """A form that states choices and then overrides them in each way there is.

    ``search`` takes a ``Choice`` in the layout, ``city`` one by name, ``notes``
    undoes the colour, and the delete button takes a ``Choice`` of its own. The
    form must be given a prefix.
    """

    name = forms.CharField(label=_("Name"), required=False)
    search = forms.CharField(label=_("Search"), required=False)
    city = forms.CharField(label=_("City"), required=False)
    notes = forms.CharField(
        label=_("Notes"), required=False, widget=forms.Textarea(attrs={"rows": 2})
    )

    def __init__(self, *args, **kwargs):
        """State the form's choices and build the layout."""
        kwargs["choices"] = FormChoices(
            size="sm",
            color="primary",
            variant="ghost",
            button_color="neutral",
            button_variant="outline",
            fields={
                "city": Choice(size="lg", color="accent"),
                "notes": Choice(color=None),
            },
        )
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper.layout = Layout(
            "name",
            Choice("search", size="xl"),
            "city",
            "notes",
            FormActions(
                Submit(f"{prefix}-save", _("Save")),
                Choice(
                    Button(f"{prefix}-delete", _("Delete")),
                    color="error",
                    variant="soft",
                ),
            ),
        )


class DrawingsForm(forms.Form):
    """Three boolean fields, each drawn a different way, which can be posted.

    ``remember`` states nothing and is a checkbox, ``notify`` is a toggle by name
    in ``FormChoices`` and ``publish`` is a switch in the layout. Every id and the
    button's name carry the form's prefix. The form must be given a prefix.
    """

    remember = forms.BooleanField(label=_("Remember me"), required=False)
    notify = forms.BooleanField(label=_("Email me about replies"), required=False)
    publish = forms.BooleanField(label=_("Publish this record"), required=False)

    def __init__(self, *args, **kwargs):
        """Build the helper, with the drawings stated and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.daisyui = FormChoices(fields={"notify": Choice(drawing="toggle")})
        self.helper.layout = Layout(
            "remember",
            "notify",
            Choice("publish", drawing="switch"),
        )
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class DrawingStateForm(ChosenForm):
    """One boolean field, drawn in one drawing and in one state.

    Give the form a prefix of the drawing's name and the state's, so no id
    repeats on the page. The field is ``flag``.

    Args:
        drawing: ``"checkbox"``, ``"toggle"`` or ``"switch"``.
        state: ``"off"``, ``"on"``, ``"help"``, ``"error"`` or ``"disabled"``.
            The form for ``"error"`` is bound with nothing posted, so the
            required field fails.
    """

    flag = forms.BooleanField(label=_("Email me about replies"), required=False)

    def __init__(self, *args, drawing, state, **kwargs):
        """Put the field in its state, and state its drawing for the form."""
        if state == "error":
            args = args or ({},)
        super().__init__(
            *args,
            choices=FormChoices(fields={"flag": Choice(drawing=drawing)}),
            **kwargs,
        )
        flag = self.fields["flag"]
        flag.required = state == "error"
        flag.disabled = state == "disabled"
        if state == "on":
            self.initial["flag"] = True
        if state == "help":
            flag.help_text = _("Sent once a day at most.")


class DrawingTrioForm(ChosenForm):
    """A checkbox, a toggle and a switch, at one size or in one colour.

    The fields are ``checkbox``, ``toggle`` and ``switch``. Give the form a
    prefix, so no id repeats on the page.

    Args:
        size: The size stated for the form, or None.
        color: The colour stated for the form, or None.
    """

    checkbox = forms.BooleanField(label=_("Checkbox"), required=False)
    toggle = forms.BooleanField(label=_("Toggle"), required=False)
    switch = forms.BooleanField(label=_("Switch"), required=False)

    def __init__(self, *args, size=None, color=None, **kwargs):
        """State the size and colour for the form, and the drawing of two fields."""
        super().__init__(
            *args,
            choices=FormChoices(
                size=size,
                color=color,
                fields={
                    "toggle": Choice(drawing="toggle"),
                    "switch": Choice(drawing="switch"),
                },
            ),
            **kwargs,
        )


class DrawingOverrideForm(ChosenForm):
    """A form that states a size and a colour, and one field that overrides both.

    ``inherits`` is a switch that takes the form's size and colour. ``overrides``
    is a toggle that states its own in the layout. Give the form a prefix.
    """

    inherits = forms.BooleanField(label=_("Takes the form's"), required=False)
    overrides = forms.BooleanField(label=_("States its own"), required=False)

    def __init__(self, *args, **kwargs):
        """State the form's choices, and the two fields' drawings."""
        super().__init__(
            *args,
            choices=FormChoices(
                size="sm",
                color="primary",
                fields={"inherits": Choice(drawing="switch")},
            ),
            **kwargs,
        )
        self.helper.layout = Layout(
            "inherits",
            Choice("overrides", drawing="toggle", size="xl", color="accent"),
        )


class FloatingLabelsForm(forms.Form):
    """A form whose fields are drawn with a floating label, which can be posted.

    The form states the floating label for every field and undoes it for
    ``nickname``. The checkbox is passed over. ``name`` is required and has help
    text, so a bound form with nothing in it comes back with an error in the
    frame. Every id and the button's name carry the form's prefix, so two of these
    forms on one page repeat no id. The form must be given a prefix.
    """

    name = forms.CharField(label=_("Name"), help_text=_("As on your card"))
    notes = forms.CharField(label=_("Notes"), widget=forms.Textarea, required=False)
    country = forms.ChoiceField(
        label=_("Country"), choices=[("de", _("Germany")), ("uk", _("United Kingdom"))]
    )
    nickname = forms.CharField(label=_("Nickname"), required=False)
    subscribe = forms.BooleanField(label=_("Subscribe"), required=False)

    def __init__(self, *args, posts=True, **kwargs):
        """State the floating label, and add a submit button when the form posts.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.daisyui = FormChoices(
            label="floating", fields={"nickname": Choice(label=None)}
        )
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class FloatingStatesForm(ChosenForm):
    """A disabled field and a read-only field, with a floating label stated.

    The disabled field is drawn with its ordinary label and the read-only field
    floats. Give the form a prefix, so no id repeats on the page.
    """

    locked = forms.CharField(label=_("Account"), initial="AC-1001", disabled=True)
    readonly = forms.CharField(
        label=_("Reference"),
        initial="REF-2026",
        widget=forms.TextInput(attrs={"readonly": True}),
    )

    def __init__(self, *args, **kwargs):
        """State the floating label for the form."""
        super().__init__(*args, choices=FormChoices(label="floating"), **kwargs)


class FloatingByNameForm(ChosenForm):
    """A form drawn with no layout that floats one field, named in its choices.

    Give the form a prefix, so no id repeats on the page.
    """

    title = forms.CharField(label=_("Title"), required=False)
    company = forms.CharField(label=_("Company"), required=False)

    def __init__(self, *args, **kwargs):
        """State the floating label for ``title`` by name."""
        super().__init__(
            *args,
            choices=FormChoices(fields={"title": Choice(label="floating")}),
            **kwargs,
        )


class FloatingChosenForm(ChosenForm):
    """An input, a textarea and a select, small enough to show one choice at a time.

    Give the form a prefix, so no id repeats on the page. Its choices, with the
    floating label, are the caller's.
    """

    name = forms.CharField(label=_("Name"), required=False)
    notes = forms.CharField(label=_("Notes"), widget=forms.Textarea, required=False)
    country = forms.ChoiceField(
        label=_("Country"), choices=[("de", _("Germany")), ("uk", _("United Kingdom"))]
    )


COUNTRY_CODES = [("+49", "+49"), ("+44", "+44"), ("+1", "+1")]
UNITS = [("kg", "kg"), ("lb", "lb")]


class JoinedGroupsForm(forms.Form):
    """A country code and a number joined under one label, which can be posted.

    ``number`` is required and has help text, so a bound form that holds a code and
    no number comes back with the error of that member alone. Every id and the
    button's name carry the form's prefix, so two of these forms on one page repeat
    no id. The form must be given a prefix.
    """

    country_code = forms.ChoiceField(label=_("Country code"), choices=COUNTRY_CODES)
    number = forms.CharField(label=_("Number"), help_text=_("Digits only"))

    def __init__(self, *args, posts=True, **kwargs):
        """Join the two fields, and add a submit button when the form posts.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            Join(
                "country_code",
                Field("number", autocomplete="tel"),
                label=_("Phone"),
            )
        )
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class JoinedChosenForm(ChosenForm):
    """A country code and a number joined under one label, to show a choice on.

    ``number`` is required, so a bound form that holds a code and no number
    fails in that member alone. Give the form a prefix, so no id repeats on the
    page.

    Args:
        *args: Passed to ``forms.Form``.
        around: What a ``Choice`` around the group states, or None for a group
            with no ``Choice`` around it.
        **kwargs: Passed to ``ChosenForm``.
    """

    country_code = forms.ChoiceField(label=_("Country code"), choices=COUNTRY_CODES)
    number = forms.CharField(label=_("Number"))

    def __init__(self, *args, around=None, **kwargs):
        """Join the two fields, inside a ``Choice`` when ``around`` is given."""
        super().__init__(*args, **kwargs)
        group = Join("country_code", "number", label=_("Phone"))
        self.helper.layout = Layout(Choice(group, **around) if around else group)


class JoinedHelpForm(ChosenForm):
    """An amount with help text joined to its unit.

    Give the form a prefix, so no id repeats on the page.
    """

    amount = forms.IntegerField(
        label=_("Amount"), min_value=0, help_text=_("Whole numbers only")
    )
    unit = forms.ChoiceField(label=_("Unit"), choices=UNITS)

    def __init__(self, *args, **kwargs):
        """Join the two fields under one label."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Join("amount", "unit", label=_("Weight")))


class JoinedStatesForm(ChosenForm):
    """A group with a disabled member, a read-only member and a hidden member.

    The hidden member is drawn beside the join, not in it. Give the form a prefix,
    so no id repeats on the page.
    """

    country_code = forms.ChoiceField(label=_("Country code"), choices=COUNTRY_CODES)
    locked = forms.CharField(label=_("Account"), initial="AC-1001", disabled=True)
    reference = forms.CharField(
        label=_("Reference"),
        initial="REF-2026",
        widget=forms.TextInput(attrs={"readonly": True}),
    )
    token = forms.CharField(widget=forms.HiddenInput, initial="demo", required=False)

    def __init__(self, *args, **kwargs):
        """Join the four fields under one label."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Join("country_code", "locked", "reference", "token", label=_("Account"))
        )


class JoinedUnlabelledForm(ChosenForm):
    """An amount joined to its unit, with no label for the group.

    Each input is still named by its own field's label. Give the form a prefix, so
    no id repeats on the page.
    """

    amount = forms.IntegerField(label=_("Amount"), min_value=0, required=False)
    unit = forms.ChoiceField(label=_("Unit"), choices=UNITS)

    def __init__(self, *args, **kwargs):
        """Join the two fields under no label."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Join("amount", "unit"))


class JoinedSingleForm(ChosenForm):
    """A group that holds one field.

    Give the form a prefix, so no id repeats on the page.
    """

    quantity = forms.IntegerField(label=_("Quantity"), min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        """Join the one field under a label."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Join("quantity", label=_("Order size")))


class InlineChoicesForm(forms.Form):
    """A form whose radio group and checkbox group are drawn along a line.

    Both fields are required, so a bound form with nothing in it comes back with
    an error in each group's frame. Its layout is built for each instance, and
    every id and button name in it carries the form's prefix, so two of these
    forms on one page repeat no id. The form must be given a prefix.
    """

    size = forms.ChoiceField(
        label=_("Size"),
        help_text=_("Pick one"),
        choices=[("s", _("Small")), ("m", _("Medium")), ("l", _("Large"))],
        widget=forms.RadioSelect,
    )
    extras = forms.MultipleChoiceField(
        label=_("Extras"),
        help_text=_("Pick any"),
        choices=[
            ("ketchup", _("Ketchup")),
            ("mustard", _("Mustard")),
            ("onions", _("Fried onions")),
            ("pickles", _("Pickles")),
        ],
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in every id and button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(InlineRadios("size"), InlineCheckboxes("extras"))
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class FieldWithButtonsForm(forms.Form):
    """A form whose fields have buttons joined to their inputs.

    One field has a button and the other has three. Both are required, so a bound
    form with nothing in it comes back with an error in each frame. Its layout is
    built for each instance, and every id and button name in it carries the form's
    prefix, so two of these forms on one page repeat no id. The form must be given
    a prefix.
    """

    search = forms.CharField(label=_("Search"), help_text=_("Words to look for"))
    code = forms.CharField(label=_("Code"))

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in every id and button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        prefix = self.prefix
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            FieldWithButtons(
                "search",
                StrictButton(_("Go"), css_id=f"{prefix}-go"),
                css_id=f"{prefix}-search-group",
            ),
            FieldWithButtons(
                "code",
                StrictButton(_("Apply"), css_id=f"{prefix}-apply"),
                StrictButton(_("Clear"), css_id=f"{prefix}-clear"),
                StrictButton(_("Help"), css_id=f"{prefix}-help"),
                css_id=f"{prefix}-code-group",
            ),
        )
        if posts:
            self.helper.add_input(Submit(f"{prefix}-submit", _("Submit")))


class UneditableFieldForm(forms.Form):
    """A form with an uneditable field beside an editable one.

    The account is declared disabled, so a submitted form keeps its initial value
    and the browser leaving it out is no error. The nickname is optional, so a
    bound form with nothing in it has no error to show. Its layout is built for
    each instance, and the form's prefix is in the button name, so two forms on
    one page repeat no id. The form must be given a prefix.
    """

    account = forms.CharField(
        label=_("Account"),
        initial="AC-1001",
        disabled=True,
        help_text=_("Issued once and never changed"),
    )
    nickname = forms.CharField(
        label=_("Nickname"), required=False, help_text=_("Shown to others")
    )

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in the button name.

        Args:
            *args: Passed to ``forms.Form``.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(UneditableField("account"), "nickname")
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class InlineFieldForm(forms.Form):
    """A short form of fields drawn with no visible label.

    The email and the city are required, so a bound form with nothing in it
    comes back with an error in each frame. The checkbox keeps its label. Its
    layout is built for each instance, and every id and button name in it
    carries the form's prefix, so two of these forms on one page repeat no id.
    The form must be given a prefix.
    """

    email = forms.EmailField(label=_("Email"))
    city = forms.CharField(label=_("City"))
    remember = forms.BooleanField(label=_("Remember me"), required=False)

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in the button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            InlineField("email"), InlineField("city"), InlineField("remember")
        )
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class MultiWidgetFieldForm(forms.Form):
    """A form with a split date and time whose parts each have an attribute.

    The start is required, so a bound form with nothing in it comes back with an
    error in the frame. The end is optional and drawn with no layout object, as
    any split date and time is. Its layout is built for each instance, and the
    form's prefix is in the button name, so two of these forms on one page repeat
    no id. The form must be given a prefix.
    """

    starts = forms.SplitDateTimeField(
        label=_("Starts"), help_text=_("Local date and time")
    )
    ends = forms.SplitDateTimeField(label=_("Ends"), required=False)

    def __init__(self, *args, posts=True, **kwargs):
        """Build the layout, with the prefix in the button name.

        Args:
            *args: Passed to ``forms.Form``.
            posts: Whether the form is drawn with its form element and a submit
                button. The form that already fails is not, so it has neither.
            **kwargs: Passed to ``forms.Form``.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = posts
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            MultiWidgetField(
                "starts",
                attrs=({"placeholder": "2026-10-03"}, {"placeholder": "12:30"}),
            ),
            "ends",
        )
        if posts:
            self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


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


STARS = [(count, format_lazy(_("{count} stars"), count=count)) for count in range(1, 6)]
STATE_STARS = [(str(count), label) for count, label in STARS]


class RatingAndRangeForm(forms.Form):
    """Two ratings and a range, which can be posted.

    ``score`` is a rating by its name in ``FormChoices`` and ``comfort`` is a rating
    in the layout, with an empty choice that clears it. ``volume`` is a range in the
    layout, with limits and a step, and a slider always submits a number, so it is
    never left empty. Every id and the button's name carry the form's prefix. The
    form must be given a prefix.
    """

    score = forms.ChoiceField(label=_("How would you rate this?"), choices=STARS)
    comfort = forms.TypedChoiceField(
        label=_("How comfortable was it?"),
        choices=[("", _("No answer")), *STARS],
        coerce=int,
        empty_value=None,
        required=False,
    )
    volume = forms.IntegerField(
        label=_("Volume"),
        min_value=0,
        max_value=100,
        step_size=5,
        initial=50,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Build the helper, with the drawings stated and a submit button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.daisyui = FormChoices(fields={"score": Choice(drawing="rating")})
        self.helper.layout = Layout(
            "score",
            Choice("comfort", drawing="rating"),
            Choice("volume", drawing="range"),
        )
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class RatingStateForm(ChosenForm):
    """One rating, in one state.

    Give the form a prefix of the state's name, so no id repeats on the page. The
    field is ``score``.

    Args:
        state: ``"help"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with nothing posted, so the required field fails.
    """

    score = forms.ChoiceField(label=_("How would you rate this?"), choices=STATE_STARS)

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state, and state its drawing for the form."""
        if state == "error":
            args = args or ({},)
        super().__init__(
            *args,
            choices=FormChoices(fields={"score": Choice(drawing="rating")}),
            **kwargs,
        )
        score = self.fields["score"]
        score.disabled = state == "disabled"
        if state == "disabled":
            self.initial["score"] = "3"
        if state == "help":
            score.help_text = _("Pick the star that fits best.")


class RangeStateForm(ChosenForm):
    """One range, in one state.

    Give the form a prefix of the state's name, so no id repeats on the page. The
    field is ``volume``.

    Args:
        state: ``"help"``, ``"error"`` or ``"disabled"``. The form for ``"error"``
            is bound with a value above the field's highest.
    """

    volume = forms.IntegerField(
        label=_("Volume"), min_value=0, max_value=100, step_size=5
    )

    def __init__(self, *args, state, **kwargs):
        """Put the field in its state, and state its drawing for the form."""
        if state == "error":
            args = args or ({"volume": "500"},)
        super().__init__(
            *args,
            choices=FormChoices(fields={"volume": Choice(drawing="range")}),
            **kwargs,
        )
        volume = self.fields["volume"]
        volume.disabled = state == "disabled"
        if state == "disabled":
            self.initial["volume"] = 40
        if state == "help":
            volume.help_text = _("Move the slider to set the volume.")


class RatingAndRangeTrioForm(ChosenForm):
    """A rating and a range, at one size or in one colour.

    The fields are ``score`` and ``volume``. Give the form a prefix, so no id repeats
    on the page.

    Args:
        size: The size stated for the form, or None.
        color: The colour stated for the form, or None.
    """

    score = forms.ChoiceField(label=_("Rating"), choices=STATE_STARS)
    volume = forms.IntegerField(
        label=_("Range"), min_value=0, max_value=100, step_size=5, required=False
    )

    def __init__(self, *args, size=None, color=None, **kwargs):
        """State the size and colour for the form, and the drawing of both fields."""
        super().__init__(
            *args,
            choices=FormChoices(
                size=size,
                color=color,
                fields={
                    "score": Choice(drawing="rating"),
                    "volume": Choice(drawing="range"),
                },
            ),
            **kwargs,
        )


class RatingAndRangeOverrideForm(ChosenForm):
    """A form that states a size and a colour, and fields that override both.

    ``inherits_score`` and ``inherits_volume`` take the form's size and colour.
    ``overrides_score`` and ``overrides_volume`` state their own in the layout. Give
    the form a prefix.
    """

    inherits_score = forms.ChoiceField(label=_("Takes the form's"), choices=STATE_STARS)
    inherits_volume = forms.IntegerField(
        label=_("Takes the form's"), min_value=0, max_value=100, required=False
    )
    overrides_score = forms.ChoiceField(label=_("States its own"), choices=STATE_STARS)
    overrides_volume = forms.IntegerField(
        label=_("States its own"), min_value=0, max_value=100, required=False
    )

    def __init__(self, *args, **kwargs):
        """State the form's choices, and the four fields' drawings."""
        super().__init__(
            *args,
            choices=FormChoices(
                size="sm",
                color="primary",
                fields={
                    "inherits_score": Choice(drawing="rating"),
                    "inherits_volume": Choice(drawing="range"),
                },
            ),
            **kwargs,
        )
        self.helper.layout = Layout(
            "inherits_score",
            "inherits_volume",
            Choice("overrides_score", drawing="rating", size="xl", color="accent"),
            Choice("overrides_volume", drawing="range", size="xl", color="accent"),
        )


DAISYUI_VERSION = "5.7.47"
THEME_NAMES = (
    "light",
    "dark",
    "cupcake",
    "bumblebee",
    "emerald",
    "corporate",
    "synthwave",
    "retro",
    "cyberpunk",
    "valentine",
    "halloween",
    "garden",
    "forest",
    "aqua",
    "lofi",
    "pastel",
    "fantasy",
    "wireframe",
    "black",
    "luxury",
    "dracula",
    "cmyk",
    "autumn",
    "business",
    "acid",
    "lemonade",
    "night",
    "coffee",
    "winter",
    "dim",
    "nord",
    "sunset",
    "caramellatte",
    "abyss",
    "silk",
)


class ReadOnlyKindsForm(ChosenForm):
    """One input of each kind that can be read-only, each carrying ``readonly``.

    The pack draws a read-only input as an ordinary one. Give the form a prefix.
    """

    text = forms.CharField(label=_("Text"))
    textarea = forms.CharField(
        label=_("Textarea"), widget=forms.Textarea(attrs={"rows": 2})
    )
    select = forms.ChoiceField(label=_("Select"), choices=[("a", "A"), ("b", "B")])
    checkbox = forms.BooleanField(label=_("Checkbox"))
    file = forms.FileField(label=_("File"), widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        """Mark every widget read-only and give the text fields a value."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs["readonly"] = True
        self.initial.update({"text": "Some text", "textarea": "Some lines"})


class AlertColoursForm(ChosenForm):
    """An alert in each colour daisyUI has for a button, each with its dismiss button.

    Give the form a prefix, so no id repeats on the page.
    """

    def __init__(self, *args, **kwargs):
        """Build the layout, with an alert for every colour in the table."""
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            *[
                Alert(
                    _("A notice in %(colour)s.") % {"colour": colour},
                    css_class=f"alert-{colour}",
                    css_id=f"{self.prefix}-{colour}",
                )
                for colour in Modifiers.names("color", Modifiers.button)
            ]
        )


class LockedKindsForm(InputKindsForm):
    """One disabled field of every kind of input that has a size, colour or variant.

    Args:
        choices: What the form states for its inputs, or None. A toggle is added.
    """

    def __init__(self, *args, **kwargs):
        """Disable every field."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.disabled = True


class UneditableChoicesForm(forms.Form):
    """A form whose every field is drawn uneditable, one of each choice kind.

    The fields are required and hold a value, so a bound form with nothing in it
    shows an error on each uneditable field. Give the form a prefix.
    """

    select = forms.ChoiceField(
        label=_("Select"), choices=[("a", "A"), ("b", "B")], initial="b"
    )
    checkbox = forms.BooleanField(label=_("Checkbox"), initial=True)
    radio = forms.ChoiceField(
        label=_("Radio group"),
        choices=[("a", "A"), ("b", "B")],
        widget=forms.RadioSelect,
        initial="b",
    )
    checkbox_group = forms.MultipleChoiceField(
        label=_("Checkbox group"),
        choices=[("a", "A"), ("b", "B")],
        widget=forms.CheckboxSelectMultiple,
        initial=["a"],
    )
    textarea = forms.CharField(
        label=_("Textarea"), widget=forms.Textarea(attrs={"rows": 2}), initial="Hello"
    )

    def __init__(self, *args, **kwargs):
        """Build the layout, with every field uneditable."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(*[UneditableField(name) for name in self.fields])


# Placeholder characters that say what goes in each position: d, m and y for the
# parts of a date.
DATE_BLOCKS = {
    "d": RangeBlock(1, 31, max_length=2, placeholder_char="d"),
    "m": RangeBlock(1, 12, max_length=2, placeholder_char="m"),
    "Y": RangeBlock(1900, 2100, placeholder_char="y"),
}
PHONE = "+{49} 000 0000000"


class MaskForm(forms.Form):
    """A form of masked fields that can be posted. It must be given a prefix."""

    def __init__(self, *args, **kwargs):
        """Build the helper, with a submit button named by the prefix."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {"novalidate": True}
        self.helper.add_input(Submit(f"{self.prefix}-submit", _("Submit")))


class PatternMaskForm(MaskForm):
    """The pattern widget and each of its options."""

    phone = forms.CharField(
        label=_("Phone number"),
        help_text=_(
            "Pattern: +{49} 000 0000000. Each 0 is a digit. The braces keep 49 "
            "in the value."
        ),
        required=False,
        widget=PatternMaskInput(PHONE),
    )
    postcode = forms.CharField(
        label=_("Postcode"),
        help_text=_(
            "Pattern: 00000. The placeholder is always shown, with # as its character."
        ),
        required=False,
        widget=PatternMaskInput("00000", lazy=False, placeholder_char="#"),
    )
    reference = forms.CharField(
        label=_("Reference"),
        help_text=_(
            "Pattern: aa-0000. Each a is a letter, shown as a, and each 0 is a "
            "digit, shown as #. Typing overwrites."
        ),
        required=False,
        widget=PatternMaskInput(
            "aa-0000",
            lazy=False,
            overwrite=True,
            placeholder_char={"0": "#", "a": "a"},
        ),
    )
    shelf = forms.CharField(
        label=_("Shelf"),
        help_text=_(
            "Pattern: S-00. S is a definition of this field's own, the regular "
            "expression [1-6]."
        ),
        required=False,
        widget=PatternMaskInput("S-00", definitions={"S": "[1-6]"}),
    )
    date = forms.CharField(
        label=_("Date"),
        help_text=_(
            "Pattern: d{.}`m{.}`Y. Blocks d, m and Y are number ranges: 1 to 31, "
            "1 to 12 and 1900 to 2100."
        ),
        required=False,
        widget=PatternMaskInput(
            "d{.}`m{.}`Y", blocks=DATE_BLOCKS, lazy=False, overwrite=True
        ),
    )
    resolution = forms.CharField(
        label=_("Resolution"),
        help_text=_("Pattern: Q. Block Q takes one of a list: HD, TV or VR."),
        required=False,
        widget=PatternMaskInput("Q", blocks={"Q": EnumBlock(["HD", "TV", "VR"])}),
    )
    licence = forms.CharField(
        label=_("Licence key"),
        help_text=_(
            "Pattern: XXXX-XXXX-XXXX. X is defined as [A-Za-z0-9]. Each hyphen "
            "is filled in ahead of the cursor."
        ),
        required=False,
        widget=PatternMaskInput(
            "XXXX-XXXX-XXXX", definitions={"X": "[A-Za-z0-9]"}, eager=True
        ),
    )
    pin = forms.CharField(
        label=_("PIN"),
        help_text=_(
            'Pattern: 0000 with display_char="•". Each digit typed is shown as '
            "a dot, and the form receives the digits."
        ),
        required=False,
        widget=PatternMaskInput("0000", display_char="•"),
    )


class MaskStatesForm(forms.Form):
    """A masked field in each state: filled, disabled, read-only and invalid."""

    filled = forms.CharField(
        label=_("With a value"),
        help_text=_("Pattern: +{49} 000 0000000"),
        required=False,
        widget=PatternMaskInput(PHONE),
    )
    read_only = forms.CharField(
        label=_("Read-only"),
        help_text=_("Pattern: +{49} 000 0000000"),
        required=False,
        widget=PatternMaskInput(PHONE, attrs={"readonly": True}),
    )
    invalid = forms.CharField(
        label=_("With an error"),
        help_text=_("Pattern: +{49} 000 0000000"),
        widget=PatternMaskInput(PHONE),
    )

    def __init__(self, *args, **kwargs):
        """Build a helper that draws no form element and no button."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class MaskSizesForm(forms.Form):
    """A masked field at each size, and one with a colour and a variant.

    Every field has the pattern 000-000 with its placeholder always shown.
    """

    extra_small = forms.CharField(label=_("Extra small"), required=False)
    small = forms.CharField(label=_("Small"), required=False)
    large = forms.CharField(label=_("Large"), required=False)
    coloured = forms.CharField(label=_("Primary, ghost"), required=False)

    def __init__(self, *args, **kwargs):
        """Give every field the mask and state a choice for each."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget = PatternMaskInput("000-000", lazy=False, placeholder_char="#")
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Choice("extra_small", size="xs"),
            Choice("small", size="sm"),
            Choice("large", size="lg"),
            Choice("coloured", color="primary", variant="ghost"),
        )


class MaskedLineForm(forms.Form):
    """One line of a price list: an article number, masked."""

    article = forms.CharField(
        label=_("Article"),
        widget=PatternMaskInput(
            "aa-0000", lazy=False, placeholder_char={"0": "#", "a": "a"}
        ),
    )


MaskedLineFormSet = formset_factory(MaskedLineForm, extra=2)


class MaskedModalForm(forms.Form):
    """A form whose masked fields sit in a modal. It must be given a prefix."""

    name = forms.CharField(label=_("Name"), required=False)
    phone = forms.CharField(
        label=_("Phone number"),
        help_text=_("Pattern: +{49} 000 0000000"),
        required=False,
        widget=PatternMaskInput(PHONE, lazy=False, placeholder_char="#"),
    )
    iban = forms.CharField(
        label=_("IBAN"),
        help_text=_("Pattern: {DE}00 0000 0000 0000 0000 00"),
        required=False,
        widget=PatternMaskInput(
            "{DE}00 0000 0000 0000 0000 00", lazy=False, placeholder_char="#"
        ),
    )

    def __init__(self, *args, **kwargs):
        """Build the layout, with the prefix in every id."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "name",
            Modal(
                "phone",
                "iban",
                css_id=self.dialog_id,
                title=_("Contact details"),
                title_id=f"{self.prefix}-title",
            ),
        )

    @property
    def dialog_id(self):
        """The id of the modal's dialog, for the control that opens it."""
        return f"{self.prefix}-dialog"
