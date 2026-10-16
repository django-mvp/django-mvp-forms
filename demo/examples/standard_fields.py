"""A plain Django form with one of every standard field."""

from django import forms

COLOURS = [("red", "Red"), ("green", "Green"), ("blue", "Blue")]
FOOD = [
    ("", "---------"),
    ("Fruit", [("apple", "Apple"), ("pear", "Pear")]),
    ("Vegetables", [("leek", "Leek"), ("kale", "Kale")]),
]


class StandardFieldsForm(forms.Form):
    """Nothing here but Django: no helper, no layout, no widget of ours."""

    text = forms.CharField(help_text="A line of free text.")
    email = forms.EmailField()
    url = forms.URLField(label="URL", required=False)
    integer = forms.IntegerField(required=False)
    decimal = forms.DecimalField(decimal_places=2, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}), required=False
    )
    search = forms.CharField(widget=forms.SearchInput, required=False)
    telephone = forms.CharField(widget=forms.TelInput, required=False)
    colour = forms.CharField(widget=forms.ColorInput, required=False)
    textarea = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))

    select = forms.ChoiceField(choices=[("", "---------"), *COLOURS])
    grouped_select = forms.ChoiceField(choices=FOOD, required=False)
    multiple_select = forms.MultipleChoiceField(choices=COLOURS, required=False)
    null_boolean = forms.NullBooleanField(required=False)
    date_as_selects = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2025, 2031)), required=False
    )
    radio = forms.ChoiceField(choices=COLOURS, widget=forms.RadioSelect)
    checkbox_group = forms.MultipleChoiceField(
        choices=COLOURS, widget=forms.CheckboxSelectMultiple, required=False
    )
    checkbox = forms.BooleanField(label="I agree to the terms")

    file = forms.FileField(widget=forms.FileInput, required=False)
    clearable_file = forms.FileField(required=False)
