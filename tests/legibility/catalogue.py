"""Every form state the pack draws, drawn without pytest and read."""

import functools
from collections.abc import Iterator
from dataclasses import dataclass

from bs4 import BeautifulSoup
from crispy_forms.bootstrap import Alert, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Reset, Submit
from django import forms
from django.template import Context, Template

from mvp_forms.choices import Choice, FormChoices, Modifiers
from tests.forms import (
    STAR_CHOICES,
    ButtonedForm,
    DisabledInputsForm,
    EveryInputForm,
    RangesForm,
    RatingsForm,
    ReadOnlyInputsForm,
    StructureForm,
)
from tests.legibility.pairings import Measurement
from tests.legibility.reader import Reader
from tests.test_pack.test_independence import STATES

TAG = "{% crispy form %}"
FILTER = "{{ form|crispy }}"


class DisabledFileForm(forms.Form):
    """A file field drawn with the plain file input, disabled."""

    plain = forms.FileField(widget=forms.FileInput, required=False, disabled=True)


class DisabledBooleansForm(forms.Form):
    """A boolean field drawn as a toggle and one drawn as a switch, both disabled."""

    notify = forms.BooleanField(required=False, disabled=True)
    publish = forms.BooleanField(required=False, disabled=True, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.daisyui = FormChoices(
            fields={
                "notify": Choice(drawing="toggle"),
                "publish": Choice(drawing="switch"),
            }
        )


class DisabledRatingAndRangeForm(forms.Form):
    """A rating and a range, both disabled."""

    score = forms.ChoiceField(choices=STAR_CHOICES, required=False, disabled=True)
    volume = forms.IntegerField(
        required=False, min_value=0, max_value=100, initial=20, disabled=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.daisyui = FormChoices(
            fields={
                "score": Choice(drawing="rating"),
                "volume": Choice(drawing="range"),
            }
        )


@dataclass(frozen=True)
class DrawnState:
    """One form state, drawn.

    Args:
        name: The state's name.
        soup: The markup the pack drew.
        supplied: The classes the form itself supplied.
    """

    name: str
    soup: BeautifulSoup
    supplied: frozenset[str]


class Catalogue:
    """Every form state the pack draws, and the pairings read from them."""

    @classmethod
    def draw(cls, source: str, form: forms.BaseForm) -> BeautifulSoup:
        """Draw a form through a template, as a host project would.

        Args:
            source: The template text, using `form`.
            form: The form to draw.

        Returns:
            The parsed markup.
        """
        template = Template("{% load crispy_forms_tags %}" + source)
        html = template.render(Context({"csrf_token": "token", "form": form}))
        return BeautifulSoup(html, "html.parser")

    @classmethod
    @functools.cache
    def states(cls) -> tuple[DrawnState, ...]:
        """Draw every state: the listed ones, the disabled ones and the sweeps.

        Returns:
            The drawn states, each under a unique name.
        """
        listed = [
            DrawnState(
                param.id,
                cls.draw(param.values[0], param.values[1]()),
                frozenset(param.values[2]),
            )
            for param in STATES
        ]
        extra = [
            DrawnState(name, cls.draw(source, form), frozenset())
            for name, source, form in cls.disabled()
        ]
        swept = [
            DrawnState(name, cls.draw(TAG, form), frozenset())
            for name, form in (
                *cls.inputs(),
                *cls.sweeps(),
                *cls.buttons(),
                *cls.alerts(),
            )
        ]
        return tuple(listed + extra + swept)

    @classmethod
    def disabled(cls) -> Iterator[tuple[str, str, forms.BaseForm]]:
        """Describe the forms of disabled and read-only fields.

        Returns:
            The name, the template text and the form of each.
        """
        yield "disabled inputs", FILTER, DisabledInputsForm()
        yield "read-only inputs", FILTER, ReadOnlyInputsForm()
        yield "disabled file input", FILTER, DisabledFileForm()
        yield "disabled toggle and switch", TAG, DisabledBooleansForm()
        yield "disabled rating and range", TAG, DisabledRatingAndRangeForm()
        yield (
            "disabled buttons",
            TAG,
            ButtonedForm(
                buttons=(
                    Submit("save", "Save", disabled=True),
                    Button("help", "Help", disabled=True),
                    StrictButton("More", disabled=True),
                )
            ),
        )

    @classmethod
    def inputs(cls) -> Iterator[tuple[str, forms.BaseForm]]:
        """Describe the inputs drawn once per colour, variant and size.

        Returns:
            The name and the form of each.
        """
        kinds = (
            ("color", Modifiers.colors["input"]),
            ("variant", Modifiers.variants["input"]),
            ("size", Modifiers.sizes["input"]),
        )
        for kind, names in kinds:
            for name in names:
                form = EveryInputForm()
                form.helper.daisyui = FormChoices(
                    **{kind: name}, fields={"agree": Choice(drawing="toggle")}
                )
                yield f"inputs, {kind} {name}", form

    @classmethod
    def sweeps(cls) -> Iterator[tuple[str, forms.BaseForm]]:
        """Describe a rating and a range, each drawn once per colour and size.

        Returns:
            The name and the form of each.
        """
        drawn = (
            ("rating", RatingsForm, ("score", "again")),
            ("range", RangesForm, ("volume", "ratio")),
        )
        tables = (("color", Modifiers.colors), ("size", Modifiers.sizes))
        for drawing, form_class, names in drawn:
            for kind, table in tables:
                for name in table[drawing]:
                    fields = {field: Choice(drawing=drawing) for field in names}
                    choices = FormChoices(**{kind: name}, fields=fields)
                    yield f"{drawing}s, {kind} {name}", form_class(choices=choices)

    @classmethod
    def buttons(cls) -> Iterator[tuple[str, forms.BaseForm]]:
        """Describe the buttons drawn once per size, colour, variant and pair.

        Returns:
            The name and the form of each.
        """
        colours = tuple(Modifiers.colors["btn"])
        variants = tuple(Modifiers.variants["btn"])
        choices = [(f"size {size}", {"size": size}) for size in Modifiers.sizes["btn"]]
        choices += [(f"colour {c}", {"button_color": c}) for c in colours]
        choices += [(f"variant {v}", {"button_variant": v}) for v in variants]
        choices += [
            (f"colour {c} with variant {v}", {"button_color": c, "button_variant": v})
            for c in colours
            for v in variants
        ]
        for name, stated in choices:
            form = ButtonedForm(
                buttons=(
                    Submit("save", "Save"),
                    Reset("clear", "Clear"),
                    Button("help", "Help"),
                    StrictButton("More"),
                )
            )
            form.helper.daisyui = FormChoices(**stated)
            yield f"buttons, {name}", form

    @classmethod
    def alerts(cls) -> Iterator[tuple[str, forms.BaseForm]]:
        """Describe an alert in each colour, with its dismiss button.

        Returns:
            The name and the form of each.
        """
        for colour in Modifiers.colors["btn"]:
            layout = (Alert("Heads up", css_class=f"alert-{colour}"),)
            yield f"alert, {colour}", StructureForm(layout=layout)

    @classmethod
    @functools.cache
    def measurements(cls) -> list[Measurement]:
        """Read every state. The pack's output is the same under every theme.

        Returns:
            Every measurement, state by state.

        Raises:
            Uncovered: A state carries a class the reader has no row for.
        """
        return [
            measurement
            for state in cls.states()
            for measurement in Reader(state.name, state.supplied).read(state.soup)
        ]
