"""The forms the suite draws."""

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import (
    BaseFormSet,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
    widgets,
)


class TextInputsForm(forms.Form):
    text = forms.CharField()
    email = forms.EmailField()
    url = forms.URLField()
    number = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput)
    date = forms.DateField()
    time = forms.TimeField()
    date_time = forms.DateTimeField()
    message = forms.CharField(widget=forms.Textarea)


class DeveloperAttrsForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "wide", "placeholder": "Your name"})
    )
    born = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))


class SecretForm(forms.Form):
    hidden = forms.CharField(widget=forms.PasswordInput)
    shown = forms.CharField(widget=forms.PasswordInput(render_value=True))


class TextInputsWithLayoutForm(TextInputsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)


class UncoveredInput(widgets.Input):
    input_type = "text"


class UncoveredWidgetsForm(forms.Form):
    first = forms.CharField(help_text="First help")
    choice = forms.ChoiceField(
        choices=[("a", "A")], widget=UncoveredInput, help_text="Choice help"
    )
    agree = forms.BooleanField(widget=UncoveredInput, help_text="Agree help")
    upload = forms.FileField(widget=UncoveredInput, help_text="Upload help")
    last = forms.CharField(help_text="Last help")


class NoFieldsForm(forms.Form):
    pass


class FormWideErrorsForm(forms.Form):
    name = forms.CharField(required=False)

    def clean(self):
        raise ValidationError(
            [
                ValidationError("The first failure", code="first"),
                ValidationError("The second failure", code="second"),
            ]
        )


class FormWideMarkupForm(forms.Form):
    name = forms.CharField(required=False)

    def clean(self):
        raise ValidationError("<script>alert(1)</script>", code="markup")


class HelpedForm(forms.Form):
    helped = forms.CharField(help_text="Some help")
    bare = forms.CharField()
    optional = forms.CharField(required=False)


class UploadForm(forms.Form):
    upload = forms.FileField(required=False)


class MediaWidget(forms.TextInput):
    class Media:
        js = ["tests/media.js"]


class MediaForm(forms.Form):
    name = forms.CharField(widget=MediaWidget)


class DeveloperLabelledForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"aria-label": "Mine"}))


class FieldAndFormWideErrorsForm(HelpedForm):
    def clean(self):
        raise ValidationError("It failed as a whole", code="whole")


FRUIT = [("a", "Apple"), ("b", "Banana")]
GROUPED = [("Fruit", FRUIT), ("Vegetable", [("c", "Carrot")]), ("d", "Dill")]


class SelectsForm(forms.Form):
    choice = forms.ChoiceField(choices=FRUIT, help_text="Pick one")
    many = forms.MultipleChoiceField(choices=FRUIT)
    maybe = forms.NullBooleanField()
    grouped = forms.ChoiceField(choices=GROUPED)


class SelectEdgesForm(forms.Form):
    empty = forms.ChoiceField(choices=[], required=False)
    marked = forms.ChoiceField(
        choices=[("<b>", "<b>Bold</b>"), ("x", "Tom & Jerry")], required=False
    )
    marked_groups = forms.ChoiceField(
        choices=[("<i>Group</i>", [("y", "Yes")])], required=False
    )
    styled = forms.ChoiceField(
        choices=FRUIT,
        widget=forms.Select(attrs={"class": "mine", "data-role": "picker"}),
    )


class OwnTemplateDateWidget(forms.SelectDateWidget):
    template_name = "django/forms/widgets/multiwidget.html"


class DateSelectsForm(forms.Form):
    born = forms.DateField(
        widget=forms.SelectDateWidget(years=[2020, 2021]), help_text="Date of birth"
    )
    plain = forms.DateField(
        widget=forms.SelectDateWidget(years=[2020, 2021]), required=False
    )
    own = forms.DateField(
        widget=OwnTemplateDateWidget(years=[2020, 2021]), required=False
    )


class LabelledDateForm(forms.Form):
    born = forms.DateField(
        widget=forms.SelectDateWidget(years=[2020, 2021], attrs={"aria-label": "Mine"})
    )


class CheckboxForm(forms.Form):
    agree = forms.BooleanField(help_text="Read the terms first")
    news = forms.BooleanField(required=False)
    styled = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "mine"})
    )


class SecondOptionDisabled:
    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if value == "b":
            option["attrs"]["disabled"] = True
        return option


class DisablingRadio(SecondOptionDisabled, forms.RadioSelect):
    pass


class DisablingCheckboxes(SecondOptionDisabled, forms.CheckboxSelectMultiple):
    pass


class OwnTemplateRadio(forms.RadioSelect):
    template_name = "django/forms/widgets/multiple_input.html"


class OwnOptionTemplateRadio(forms.RadioSelect):
    option_template_name = "django/forms/widgets/checkbox_option.html"


class OwnTemplateCheckboxes(forms.CheckboxSelectMultiple):
    template_name = "django/forms/widgets/multiple_input.html"


class OwnOptionTemplateCheckboxes(forms.CheckboxSelectMultiple):
    option_template_name = "django/forms/widgets/radio_option.html"


MARKED = [("<b>", "<b>Bold</b>"), ("x", "Tom & Jerry")]
MARKED_GROUPS = [("<i>Group</i>", [("y", "Yes")])]


class RadioGroupsForm(forms.Form):
    choice = forms.ChoiceField(
        choices=FRUIT, widget=forms.RadioSelect, help_text="Pick one"
    )
    grouped = forms.ChoiceField(
        choices=GROUPED, widget=forms.RadioSelect, required=False
    )
    empty = forms.ChoiceField(choices=[], widget=forms.RadioSelect, required=False)
    marked = forms.ChoiceField(choices=MARKED, widget=forms.RadioSelect, required=False)
    marked_groups = forms.ChoiceField(
        choices=MARKED_GROUPS, widget=forms.RadioSelect, required=False
    )
    locked = forms.ChoiceField(choices=FRUIT, widget=DisablingRadio, required=False)
    own = forms.ChoiceField(choices=FRUIT, widget=OwnTemplateRadio, required=False)
    own_option = forms.ChoiceField(
        choices=FRUIT, widget=OwnOptionTemplateRadio, required=False
    )


class CheckboxGroupsForm(forms.Form):
    choice = forms.MultipleChoiceField(
        choices=FRUIT, widget=forms.CheckboxSelectMultiple, help_text="Pick any"
    )
    grouped = forms.MultipleChoiceField(
        choices=GROUPED, widget=forms.CheckboxSelectMultiple, required=False
    )
    empty = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple, required=False
    )
    marked = forms.MultipleChoiceField(
        choices=MARKED, widget=forms.CheckboxSelectMultiple, required=False
    )
    marked_groups = forms.MultipleChoiceField(
        choices=MARKED_GROUPS, widget=forms.CheckboxSelectMultiple, required=False
    )
    locked = forms.MultipleChoiceField(
        choices=FRUIT, widget=DisablingCheckboxes, required=False
    )
    own = forms.MultipleChoiceField(
        choices=FRUIT, widget=OwnTemplateCheckboxes, required=False
    )
    own_option = forms.MultipleChoiceField(
        choices=FRUIT, widget=OwnOptionTemplateCheckboxes, required=False
    )


class HeldFile:
    def __init__(self, name):
        self.name = name
        self.url = f"/media/{name}"

    def __str__(self):
        return self.name

    def __bool__(self):
        return True


class SeveralFilesInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class OwnTemplateFileInput(forms.ClearableFileInput):
    template_name = "django/forms/widgets/file.html"


class FilesForm(forms.Form):
    plain = forms.FileField(widget=forms.FileInput, required=False, help_text="Plain")
    empty = forms.FileField(required=False, help_text="Nothing held")
    optional = forms.FileField(
        required=False, initial=HeldFile("report.pdf"), help_text="Optional"
    )
    needed = forms.FileField(initial=HeldFile("contract.pdf"))
    marked = forms.FileField(required=False, initial=HeldFile("<b>x</b>&.pdf"))
    several = forms.FileField(widget=SeveralFilesInput, required=False)
    own = forms.FileField(widget=OwnTemplateFileInput, required=False)
    locked = forms.FileField(
        required=False,
        initial=HeldFile("locked.pdf"),
        widget=forms.ClearableFileInput(attrs={"disabled": True}),
    )


def refuse_hidden(value):
    raise ValidationError(
        "<b>Refused</b> %(value)s", code="refused", params={"value": value}
    )


class HiddenInputsForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput, initial="abc")
    ids = forms.MultipleChoiceField(
        choices=[("1", "One"), ("2", "Two")],
        widget=forms.MultipleHiddenInput,
        initial=["1", "2"],
    )
    name = forms.CharField(help_text="Visible help")


class HiddenOnlyForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput, initial="abc")


class HiddenErrorForm(HiddenInputsForm):
    token = forms.CharField(widget=forms.HiddenInput, validators=[refuse_hidden])


class HiddenAndFormWideErrorsForm(HiddenErrorForm):
    def clean(self):
        raise ValidationError("It failed as a whole", code="whole")


class DisabledHiddenForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput, initial="abc", disabled=True)


class SplitHiddenForm(forms.Form):
    moment = forms.SplitDateTimeField(
        widget=forms.SplitHiddenDateTimeWidget,
        initial=datetime.datetime(2026, 10, 3, 12, 30),
    )


class DisabledInputsForm(forms.Form):
    text = forms.CharField(initial="Ada", disabled=True)
    number = forms.IntegerField(initial=42, disabled=True)
    date = forms.DateField(initial=datetime.date(2026, 10, 3), disabled=True)
    message = forms.CharField(
        widget=forms.Textarea, initial="Hello there", disabled=True
    )
    choice = forms.ChoiceField(choices=FRUIT, initial="b", disabled=True)
    agree = forms.BooleanField(initial=True, disabled=True)
    upload = forms.FileField(
        required=False, initial=HeldFile("kept.pdf"), disabled=True
    )
    radios = forms.ChoiceField(
        choices=FRUIT, widget=forms.RadioSelect, initial="b", disabled=True
    )
    boxes = forms.MultipleChoiceField(
        choices=FRUIT,
        widget=forms.CheckboxSelectMultiple,
        initial=["a", "b"],
        disabled=True,
    )
    secret = forms.CharField(
        widget=forms.PasswordInput, initial="hunter2", disabled=True
    )


class ReadOnlyInputsForm(forms.Form):
    text = forms.CharField(
        initial="Ada", widget=forms.TextInput(attrs={"readonly": True})
    )
    message = forms.CharField(
        initial="Hello there", widget=forms.Textarea(attrs={"readonly": True})
    )
    choice = forms.ChoiceField(
        choices=FRUIT, initial="b", widget=forms.Select(attrs={"readonly": True})
    )
    agree = forms.BooleanField(
        initial=True, widget=forms.CheckboxInput(attrs={"readonly": True})
    )
    upload = forms.FileField(
        required=False, widget=forms.FileInput(attrs={"readonly": True})
    )


class DisabledAndReadOnlyForm(forms.Form):
    text = forms.CharField(
        initial="Ada", widget=forms.TextInput(attrs={"readonly": True}), disabled=True
    )


class StructureForm(forms.Form):
    first = forms.CharField()
    second = forms.CharField()
    third = forms.CharField()
    fourth = forms.CharField()

    def __init__(self, *args, layout=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(*layout)


class StructureWideErrorForm(StructureForm):
    def clean(self):
        raise ValidationError("It failed as a whole", code="whole")


class StructureHiddenForm(StructureForm):
    token = forms.CharField(widget=forms.HiddenInput)


class ButtonedForm(forms.Form):
    first = forms.CharField()
    second = forms.CharField()

    def __init__(self, *args, buttons=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        for button in buttons:
            self.helper.add_input(button)


class DocumentedExamplesForm(forms.Form):
    form_field = forms.CharField()
    form_field_1 = forms.CharField()
    form_field_2 = forms.CharField()
    form_field_3 = forms.CharField()

    def __init__(self, *args, layout=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(*layout)


class EveryInputForm(forms.Form):
    text = forms.CharField(help_text="Some help")
    message = forms.CharField(widget=forms.Textarea)
    choice = forms.ChoiceField(choices=FRUIT)
    born = forms.DateField(widget=forms.SelectDateWidget(years=[2020, 2021]))
    agree = forms.BooleanField(required=False)
    radios = forms.ChoiceField(choices=FRUIT, widget=forms.RadioSelect)
    boxes = forms.MultipleChoiceField(
        choices=FRUIT, widget=forms.CheckboxSelectMultiple
    )
    upload = forms.FileField(widget=forms.FileInput, required=False)
    held = forms.FileField(required=False, initial=HeldFile("report.pdf"))
    locked = forms.CharField(initial="Ada", disabled=True)
    readonly = forms.CharField(
        initial="Ada", widget=forms.TextInput(attrs={"readonly": True})
    )
    token = forms.CharField(widget=forms.HiddenInput, initial="abc")

    def __init__(self, *args, layout=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        if layout is not None:
            self.helper.layout = Layout(*layout)


class LineForm(forms.Form):
    name = forms.CharField(help_text="What it is")
    quantity = forms.IntegerField(required=False)
    ref = forms.CharField(required=False, widget=forms.HiddenInput)


class ChoiceLineForm(forms.Form):
    fruit = forms.ChoiceField(
        choices=FRUIT, widget=forms.RadioSelect, help_text="Pick one"
    )
    extras = forms.MultipleChoiceField(
        choices=FRUIT, widget=forms.CheckboxSelectMultiple, required=False
    )


class RuledLineForm(LineForm):
    def clean_ref(self):
        if self.cleaned_data["ref"] == "bad":
            raise ValidationError("The reference is refused", code="refused")
        return self.cleaned_data["ref"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("name") == "whole":
            raise ValidationError("The line failed as a whole", code="whole")
        return cleaned


class RuledBaseFormSet(BaseFormSet):
    refusal = "The lines add up to too much"
    limit = 10

    def clean(self):
        super().clean()
        total = sum(form.cleaned_data.get("quantity") or 0 for form in self.forms)
        if total > self.limit:
            raise ValidationError(self.refusal, code="too_much")


class MarkupRuledBaseFormSet(RuledBaseFormSet):
    refusal = "<script>alert(1)</script>"


class MarkupLineForm(LineForm):
    refusal = "<script>alert(2)</script>"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "<script>alert(3)</script>"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("name") == "whole":
            raise ValidationError(self.refusal, code="whole")
        return cleaned


LineFormSet = formset_factory(LineForm, extra=3)
OrderedLineFormSet = formset_factory(LineForm, extra=3, can_delete=True, can_order=True)
KeptLineFormSet = formset_factory(
    LineForm, extra=1, can_delete=True, can_delete_extra=False, can_order=True
)
RuledLineFormSet = formset_factory(RuledLineForm, RuledBaseFormSet, extra=3)
MarkupRuledLineFormSet = formset_factory(RuledLineForm, MarkupRuledBaseFormSet, extra=3)
MarkupLineFormSet = formset_factory(MarkupLineForm, extra=3)
ChoiceLineFormSet = formset_factory(ChoiceLineForm, extra=2)
NoLinesFormSet = formset_factory(LineForm, extra=0)
MediaFormSet = formset_factory(MediaForm, extra=2)
GroupFormSet = modelformset_factory(Group, fields=["name"], extra=1)
PermissionFormSet = inlineformset_factory(
    ContentType, Permission, fields=["name", "codename"], extra=1
)


def formset_helper(*layout, buttons=(), **settings):
    helper = FormHelper()
    for name, value in settings.items():
        setattr(helper, name, value)
    if layout:
        helper.layout = Layout(*layout)
    for button in buttons:
        helper.add_input(button)
    return helper


def ruled_data(*lines, prefix="form"):
    data = {
        f"{prefix}-TOTAL_FORMS": str(len(lines)),
        f"{prefix}-INITIAL_FORMS": "0",
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }
    for index, line in enumerate(lines):
        for name, value in line.items():
            data[f"{prefix}-{index}-{name}"] = value
    return data


class DrawnBooleansForm(forms.Form):
    remember = forms.BooleanField(required=False)
    notify = forms.BooleanField(required=False)
    publish = forms.BooleanField(required=False)
    title = forms.CharField(required=False)
    token = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, layout=None, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        if layout is not None:
            self.helper.layout = Layout(*layout)
        if choices is not None:
            self.helper.daisyui = choices


class DrawnBooleanLineForm(forms.Form):
    name = forms.CharField(required=False)
    done = forms.BooleanField(required=False)


DrawnBooleanLineFormSet = formset_factory(DrawnBooleanLineForm, extra=3)


class RequiredDrawnBooleanForm(forms.Form):
    agree = forms.BooleanField()
    notify = forms.BooleanField(required=False)

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        if choices is not None:
            self.helper.daisyui = choices
