"""The pack's input tag, which draws a widget as a daisyUI component."""

from django import forms, template
from django.forms.boundfield import BoundField
from django.utils.safestring import SafeString

register = template.Library()


class FieldInput:
    """Draw one bound field's widget for one render.

    The pack's class is passed to ``BoundField.as_widget``, which merges it over
    the widget's own attributes for that render only, so the widget is never
    changed.

    Args:
        field: The bound field whose widget is drawn.
    """

    components: dict[type[forms.Widget], str] = {
        forms.TextInput: "input",
        forms.EmailInput: "input",
        forms.URLInput: "input",
        forms.NumberInput: "input",
        forms.PasswordInput: "input",
        forms.Textarea: "textarea",
    }

    def __init__(self, field: BoundField) -> None:
        self.field = field

    @property
    def component(self) -> str | None:
        """The daisyUI class for the field's widget, or None when it has none."""
        for widget_class, component in self.components.items():
            if isinstance(self.field.field.widget, widget_class):
                return component
        return None

    @property
    def css_class(self) -> str:
        """The widget's own classes followed by the component, each once."""
        classes = self.field.field.widget.attrs.get("class", "").split()
        if self.component:
            classes.append(self.component)
        return " ".join(dict.fromkeys(classes))

    @property
    def attrs(self) -> dict[str, str | bool]:
        """The attributes the pack adds to the widget for this render."""
        if self.component:
            return {"class": self.css_class}
        return {}

    def render(self) -> SafeString:
        """Return the widget drawn with the pack's attributes.

        Returns:
            The widget's markup.
        """
        return self.field.as_widget(attrs=self.attrs)


@register.simple_tag
def daisyui_input(field: BoundField) -> SafeString:
    """Draw a bound field's widget as a daisyUI component.

    Args:
        field: The bound field whose widget is drawn.

    Returns:
        The widget's markup.
    """
    return FieldInput(field).render()
