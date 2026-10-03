"""The pack's input tag, which draws a widget as a daisyUI component."""

from html import unescape

from django import forms, template
from django.forms.boundfield import BoundField
from django.template import Context
from django.utils.html import strip_tags
from django.utils.safestring import SafeString

register = template.Library()


class FieldInput:
    """Draw one bound field's widget for one render.

    The pack's class is passed to ``BoundField.as_widget``, which merges it over
    the widget's own attributes for that render only, so the widget is never
    changed.

    Args:
        field: The bound field whose widget is drawn.
        show_labels: Whether the form draws labels. Without them the input is
            named by an ``aria-label``.
        show_errors: Whether the form draws errors. Without them the input has
            no error modifier and no description naming the error element.
    """

    components: dict[type[forms.Widget], str] = {
        forms.TextInput: "input",
        forms.EmailInput: "input",
        forms.URLInput: "input",
        forms.NumberInput: "input",
        forms.PasswordInput: "input",
        forms.Textarea: "textarea",
    }

    def __init__(
        self, field: BoundField, show_labels: bool = True, show_errors: bool = True
    ) -> None:
        self.field = field
        self.show_labels = show_labels
        self.show_errors = show_errors

    @property
    def component(self) -> str | None:
        """The daisyUI class for the field's widget, or None when it has none."""
        for widget_class, component in self.components.items():
            if isinstance(self.field.field.widget, widget_class):
                return component
        return None

    @property
    def css_class(self) -> str:
        """The widget's own classes, the component, then its error modifier."""
        classes = self.field.field.widget.attrs.get("class", "").split()
        if self.component:
            classes.append(self.component)
            if self.show_errors and self.field.errors:
                classes.append(f"{self.component}-error")
        return " ".join(dict.fromkeys(classes))

    @property
    def attrs(self) -> dict[str, str | bool]:
        """The attributes the pack adds to the widget for this render."""
        attrs: dict[str, str | bool] = {}
        if self.component:
            attrs["class"] = self.css_class
        if self.requires_aria_required:
            attrs["aria-required"] = "true"
        if self.requires_aria_label:
            # A plain str, so the attribute is escaped once however the label
            # was marked.
            attrs["aria-label"] = unescape(strip_tags(str(self.field.label))).strip()
        if self.hides_error_element and self.description:
            attrs["aria-describedby"] = self.description
        return attrs

    @property
    def requires_aria_required(self) -> bool:
        """Whether the requirement must reach assistive technology by ARIA.

        Django writes ``required`` itself unless the form turns it off, and a
        grouped widget copies its attributes onto every option.
        """
        return (
            self.field.field.required
            and not self.field.form.use_required_attribute
            and not self.field.use_fieldset
        )

    @property
    def requires_aria_label(self) -> bool:
        """Whether the input needs a name of its own because no label is drawn."""
        widget = self.field.field.widget
        return (
            not self.show_labels
            and bool(self.field.label)
            and "aria-label" not in widget.attrs
            and not self.field.use_fieldset
        )

    @property
    def hides_error_element(self) -> bool:
        """Whether Django would describe the input by an error element not drawn."""
        widget = self.field.field.widget
        return (
            not self.show_errors
            and bool(self.field.errors)
            and "aria-describedby" not in widget.attrs
            and not self.field.use_fieldset
        )

    @property
    def description(self) -> str:
        """The id of the help text, or an empty string when none is drawn."""
        if self.field.help_text and self.field.auto_id:
            return f"{self.field.auto_id}_helptext"
        return ""

    def render(self) -> SafeString:
        """Return the widget drawn with the pack's attributes.

        With errors off, a field with errors and no help text has nothing for
        its description to name, which ``as_widget`` cannot express, so the
        widget is rendered from the attributes Django would have built.

        Returns:
            The widget's markup.
        """
        if self.hides_error_element and not self.description:
            widget = self.field.field.widget
            attrs = self.field.build_widget_attrs(self.attrs, widget)
            attrs.pop("aria-describedby", None)
            if self.field.auto_id and "id" not in widget.attrs:
                attrs.setdefault("id", self.field.auto_id)
            return SafeString(
                widget.render(
                    name=self.field.html_name,
                    value=self.field.value(),
                    attrs=attrs,
                    renderer=self.field.form.renderer,
                )
            )
        return self.field.as_widget(attrs=self.attrs)


@register.simple_tag(takes_context=True)
def daisyui_input(context: Context, field: BoundField) -> SafeString:
    """Draw a bound field's widget as a daisyUI component.

    Args:
        context: The template context, read for the helper's label and error
            switches, which are both on when absent.
        field: The bound field whose widget is drawn.

    Returns:
        The widget's markup.
    """
    return FieldInput(
        field,
        show_labels=context.get("form_show_labels") is not False,
        show_errors=context.get("form_show_errors") is not False,
    ).render()
