"""The pack's tags and filters, which draw inputs and buttons as daisyUI."""

import copy
from html import unescape
from typing import Any

from django import forms, template
from django.forms.boundfield import BoundField
from django.template import Context
from django.utils.html import strip_tags
from django.utils.safestring import SafeData, SafeString
from django.utils.translation import gettext_lazy

register = template.Library()

DATE_PARTS = {
    "_year": gettext_lazy("Year"),
    "_month": gettext_lazy("Month"),
    "_day": gettext_lazy("Day"),
}
# Class names django-crispy-forms writes for other template packs. daisyUI does
# not define them, so a button or a group is drawn without them.
UPSTREAM_ONLY_CLASSES = frozenset({"btn-inverse", "ctrlHolder", "blockLabel", "error"})


class FieldInput:
    """Draw one bound field's widget for one render.

    The pack's class is passed to ``BoundField.as_widget``, which merges it over
    the widget's own attributes for that render only, so the widget is never
    changed. A widget the pack has a template for is drawn from a copy of it with
    that template, for the same reason.

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
        forms.CheckboxInput: "checkbox",
        forms.CheckboxSelectMultiple: "checkbox",
        forms.RadioSelect: "radio",
        forms.Select: "select",
        forms.SelectDateWidget: "select",
        forms.FileInput: "file-input",
    }
    # Makes an input fill its field, unless the developer's own class holds a
    # width. See docs/adr/0007-inputs-fill-their-container.md.
    width = "w-full"
    # A checkbox and a radio are fixed-size and never widened.
    fixed_size: set[str] = {"checkbox", "radio"}
    templates: dict[type[forms.Widget], str] = {
        forms.CheckboxSelectMultiple: "daisyui/widgets/group.html",
        forms.RadioSelect: "daisyui/widgets/group.html",
        forms.SelectDateWidget: "daisyui/widgets/select_date.html",
        forms.ClearableFileInput: "daisyui/widgets/clearable_file_input.html",
    }
    # Written out, not built from the component's name, so a host project's
    # Tailwind build finds them when it scans this module.
    error_modifiers: dict[str, str] = {
        "input": "input-error",
        "textarea": "textarea-error",
        "select": "select-error",
        "checkbox": "checkbox-error",
        "radio": "radio-error",
        "file-input": "file-input-error",
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
    def template_name(self) -> str | None:
        """The pack's template for the field's widget, or None when it has none.

        A widget that names a template of its own, or an option template of its
        own, is drawn by that template, so the pack's applies only while the
        widget has its class's templates.
        """
        widget = self.field.field.widget
        for widget_class, name in self.templates.items():
            if isinstance(widget, widget_class) and all(
                getattr(widget, attr, None) == getattr(widget_class, attr, None)
                for attr in ("template_name", "option_template_name")
            ):
                return name
        return None

    @property
    def widget(self) -> forms.Widget:
        """The widget to draw: the field's own, or a copy with the pack's template."""
        widget: forms.Widget = self.field.field.widget
        if self.template_name:
            widget = copy.copy(widget)
            widget.template_name = self.template_name
        return widget

    @property
    def is_group(self) -> bool:
        """Whether the field is several inputs that share one label."""
        return self.field.use_fieldset

    @property
    def is_single_checkbox(self) -> bool:
        """Whether the field is one checkbox, which sits inside its own label."""
        return self.component == "checkbox" and not self.is_group

    @property
    def css_class(self) -> str:
        """The widget's own classes, the component, a width, then its error modifier."""
        classes = self.field.field.widget.attrs.get("class", "").split()
        if self.component:
            classes.append(self.component)
            if self.component not in self.fixed_size and not any(
                name.startswith("w-") for name in classes
            ):
                classes.append(self.width)
            if self.show_errors and self.field.errors:
                classes.append(self.error_modifiers[self.component])
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
            attrs["aria-label"] = self.label_text
        if self.hides_error_element and self.description:
            attrs["aria-describedby"] = self.description
        return attrs

    @property
    def label_text(self) -> str:
        """The label as plain text, for an attribute that is escaped once.

        A label marked safe is markup, so its tags are dropped and its entities
        read as characters. Any other label is shown as written.
        """
        label = self.field.label
        if isinstance(label, SafeData):
            return unescape(strip_tags(str(label))).strip()
        return str(label)

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

    @property
    def group_description(self) -> str:
        """The ids a group's fieldset is described by, or an empty string.

        Names the help text, then the error element, for whichever is drawn.
        """
        ids = [self.description] if self.description else []
        if self.show_errors and self.field.errors and self.field.auto_id:
            ids.append(f"{self.field.auto_id}_error")
        return " ".join(ids)

    def render(self) -> SafeString:
        """Return the widget drawn with the pack's attributes.

        With errors off, a field with errors and no help text has nothing for
        its description to name, which ``as_widget`` cannot express, so the
        widget is rendered from the attributes Django would have built.

        Returns:
            The widget's markup.
        """
        if self.hides_error_element and not self.description:
            widget = self.widget
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
        return self.field.as_widget(widget=self.widget, attrs=self.attrs)


@register.simple_tag(takes_context=True)
def daisyui_field(context: Context, field: BoundField) -> FieldInput:
    """Return the pack's drawing of a bound field's widget.

    Used as ``{% daisyui_field field as drawn %}``: the frame asks the result
    which shape to draw, then draws it with ``drawn.render``.

    Args:
        context: The template context, read for the helper's label and error
            switches. Each is off only when it equals False, as the
            templates read it, and on when absent.
        field: The bound field whose widget is drawn.

    Returns:
        The field's input.
    """
    return FieldInput(
        field,
        show_labels=context.get("form_show_labels") != False,  # noqa: E712
        show_errors=context.get("form_show_errors") != False,  # noqa: E712
    )


@register.filter
def daisyui_date_part(name: str) -> str:
    """Name the part of a date that a select draws, from the end of its name.

    Args:
        name: The select's name, such as ``born_year``.

    Returns:
        The translated name of the part, or an empty string for a name that
        ends in none of year, month or day.
    """
    for suffix, part in DATE_PARTS.items():
        if name.endswith(suffix):
            return str(part)
    return ""


@register.filter
def daisyui_classes(value: str | None) -> str:
    """Return a class string without the names written for other template packs.

    Repeated names are dropped and the order of the rest is kept.

    Args:
        value: The class string django-crispy-forms wrote, or None.

    Returns:
        The class string, empty when nothing is left.
    """
    names = (
        name for name in (value or "").split() if name not in UPSTREAM_ONLY_CLASSES
    )
    return " ".join(dict.fromkeys(names))


@register.filter
def daisyui_shown(inputs: list | None) -> list:
    """Return the inputs a form helper holds that a person can see.

    Args:
        inputs: The objects added to the helper with ``add_input``, or None.

    Returns:
        Every one of them that is not a hidden input, in the order given.
    """
    return [
        item for item in inputs or [] if getattr(item, "input_type", "") != "hidden"
    ]


@register.simple_tag(takes_context=True)
def daisyui_layout_object(context: Context, layout_object: Any) -> SafeString:
    """Draw a layout object held by a form helper as a layout would draw it.

    django-crispy-forms never renders what ``add_input`` was given, so an
    object that draws itself, such as a ``StrictButton``, is rendered here.

    Args:
        context: The template context, read for the form and the pack's name,
            both of which the crispy tag supplies.
        layout_object: The object added to the helper.

    Returns:
        The object's markup.
    """
    with context.push():
        return SafeString(
            layout_object.render(
                context.get("form"), context, template_pack=context["template_pack"]
            )
        )
