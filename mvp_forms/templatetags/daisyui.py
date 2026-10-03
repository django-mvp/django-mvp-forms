"""The pack's tags and filters, which draw inputs and buttons as daisyUI."""

import copy
import re
import secrets
from collections.abc import Callable
from html import unescape
from typing import Any

from django import forms, template
from django.forms.boundfield import BoundField
from django.forms.formsets import BaseFormSet
from django.template import Context
from django.utils.html import strip_tags
from django.utils.safestring import SafeData, SafeString
from django.utils.translation import gettext_lazy

from mvp_forms.choices import INHERIT, Choice, FormChoices, InvalidChoice, Modifiers

register = template.Library()

DATE_PARTS = {
    "_year": gettext_lazy("Year"),
    "_month": gettext_lazy("Month"),
    "_day": gettext_lazy("Day"),
}
# Class names django-crispy-forms writes for other template packs. daisyUI does
# not define them, so a button or a group is drawn without them.
UPSTREAM_ONLY_CLASSES = frozenset(
    {
        "btn-inverse",
        "ctrlHolder",
        "blockLabel",
        "error",
        "tab-pane",
        "active",
        "alert-block",
    }
)
# Written by layout/tab-pane.html in place of a group name; daisyui_tab_group
# swaps it for the name one tab holder's radios share.
TAB_GROUP_PLACEHOLDER = 'name="daisyui-tab-group"'


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
        choices: The form's statement of size, colour and variant, if any.
        placed: The ``Choice`` of a layout around the field, if any. It wins
            over the form's statement for this field, and the field's entry in
            ``choices.fields`` stands between the two.

    Raises:
        InvalidChoice: A size, colour or variant stated for the form or the
            field is not one daisyUI has, or the field states one its input has
            no modifier for. A drawing the field states is not one of the three,
            or the field is not a boolean field.
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
    # A checkbox, a radio and a toggle are fixed-size and never widened.
    fixed_size: set[str] = {"checkbox", "radio", "toggle"}
    templates: dict[type[forms.Widget], str] = {
        forms.CheckboxSelectMultiple: "daisyui/widgets/group.html",
        forms.RadioSelect: "daisyui/widgets/group.html",
        forms.SelectDateWidget: "daisyui/widgets/select_date.html",
        forms.ClearableFileInput: "daisyui/widgets/clearable_file_input.html",
    }
    # The removal checkbox of a held file takes the size and the colour. A
    # checkbox has no variant.
    removal_kinds = ("size", "color")
    # Written out, not built from the component's name, so a host project's
    # Tailwind build finds them when it scans this module.
    error_modifiers: dict[str, str] = {
        "input": "input-error",
        "textarea": "textarea-error",
        "select": "select-error",
        "checkbox": "checkbox-error",
        "toggle": "toggle-error",
        "radio": "radio-error",
        "file-input": "file-input-error",
    }

    def __init__(
        self,
        field: BoundField,
        show_labels: bool = True,
        show_errors: bool = True,
        choices: FormChoices | None = None,
        placed: Choice | None = None,
    ) -> None:
        self.field = field
        self.show_labels = show_labels
        self.show_errors = show_errors
        choices = choices or FormChoices()
        own = self.own_choice(choices, placed)
        self.drawing = self.resolve_drawing(own)
        self.modifiers = self.resolve_modifiers(choices, own, self.component)
        self.removal_modifiers = (
            self.resolve_modifiers(choices, own, "checkbox", self.removal_kinds)
            if self.component == "file-input"
            else []
        )

    def own_choice(self, choices: FormChoices, placed: Choice | None) -> Choice:
        """Return what is stated for this field alone.

        Args:
            choices: The form's statement.
            placed: The ``Choice`` of a layout around the field, or None.

        Returns:
            The layout's choice merged over the one named for the field on the
            form, whichever of the two there is, or an empty choice.
        """
        named = choices.fields.get(self.field.name)
        if placed is None:
            return Choice() if named is None else named
        return placed if named is None else placed.over(named)

    def resolve_drawing(self, own: Choice) -> str | None:
        """Return the name of the drawing stated for the field, or None.

        Resolved before the modifiers, because the component they are for
        depends on it, and when the input is built, so a mistake is raised from
        the tag and not from inside a template's ``{% if %}``.

        Args:
            own: What is stated for this field alone.

        Returns:
            The drawing's name, or None when none is stated.

        Raises:
            InvalidChoice: See the class.
        """
        drawing = own.drawing
        if drawing is None or drawing is INHERIT:
            return None
        if not isinstance(self.field.field.widget, forms.CheckboxInput):
            raise InvalidChoice("drawing", drawing, (), self.field.name)
        allowed = tuple(Modifiers.drawings)
        if drawing not in allowed:
            raise InvalidChoice("drawing", drawing, allowed, self.field.name)
        return str(drawing)

    def resolve_modifiers(
        self,
        choices: FormChoices,
        own: Choice,
        component: str | None,
        kinds: tuple[str, ...] = ("size", "color", "variant"),
    ) -> list[str]:
        """Return the daisyUI class of each choice that applies to a component.

        Resolved when the input is built, so a mistake is raised from the tag
        and not from inside a template's ``{% if %}``, which would swallow it.

        Args:
            choices: The form's statement.
            own: What is stated for this field alone.
            component: The component the classes are for: the field's own, or
                the checkbox that removes a held file.
            kinds: Which of size, colour and variant to resolve.

        Returns:
            The classes for the kinds asked for, in that order, for each one
            that resolves to a class.

        Raises:
            InvalidChoice: See the class.
        """
        stated = {
            "size": choices.size,
            "color": choices.color,
            "variant": choices.variant,
        }
        resolved = (
            Modifiers.resolve(
                kind,
                component,
                own=getattr(own, kind),
                form=stated[kind],
                target=self.field.name,
                in_error=self.is_in_error,
            )
            for kind in kinds
        )
        return [modifier for modifier in resolved if modifier]

    @property
    def is_in_error(self) -> bool:
        """Whether the field is drawn as in error."""
        return self.show_errors and bool(self.field.errors)

    @property
    def component(self) -> str | None:
        """The daisyUI class for the field's widget, or None when it has none.

        A drawing stated for the field decides it, for a boolean field.
        """
        if self.drawing:
            return Modifiers.drawings[self.drawing]
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
            if self.removal_modifiers:
                widget.get_context = self.removal_context(  # type: ignore[method-assign]
                    widget.get_context
                )
        return widget

    def removal_context(self, get_context: Callable[..., dict]) -> Callable[..., dict]:
        """Wrap a widget's context so that it names the removal checkbox's classes.

        Only the widget's own context reaches its template, so the classes the
        pack resolved for the checkbox that removes a held file are added there,
        on the copy of the widget that is drawn.

        Args:
            get_context: The copy's own ``get_context``.

        Returns:
            A function that returns the same context with ``removal_class`` set.
        """

        def with_removal_class(*args: Any, **kwargs: Any) -> dict:
            context = get_context(*args, **kwargs)
            context["widget"]["removal_class"] = " ".join(self.removal_modifiers)
            return context

        return with_removal_class

    @property
    def is_group(self) -> bool:
        """Whether the field is several inputs that share one label."""
        return self.field.use_fieldset

    @property
    def is_single_checkbox(self) -> bool:
        """Whether the field is one checkbox, which sits inside its own label.

        A toggle and a switch are one too.
        """
        return self.component in {"checkbox", "toggle"} and not self.is_group

    @property
    def css_class(self) -> str:
        """The widget's own classes, the component, the choices, a width, the error."""
        classes = self.field.field.widget.attrs.get("class", "").split()
        if self.component:
            classes.append(self.component)
            classes.extend(self.modifiers)
            if self.component not in self.fixed_size and not any(
                name.startswith("w-") for name in classes
            ):
                classes.append(self.width)
            if self.is_in_error:
                classes.append(self.error_modifiers[self.component])
        return " ".join(dict.fromkeys(classes))

    @property
    def attrs(self) -> dict[str, str | bool]:
        """The attributes the pack adds to the widget for this render."""
        attrs: dict[str, str | bool] = {}
        if self.component:
            attrs["class"] = self.css_class
        if self.drawing == "switch":
            attrs["role"] = "switch"
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


class DrawnButton:
    """Draw one button for one render, with the choices that apply to it.

    A ``Submit``, ``Reset`` or ``Button`` is an ``<input>`` whose classes are
    ``css_class``. A ``StrictButton`` is a ``<button>`` whose attributes are
    ``flat_attrs``. A hidden input is not a button and takes nothing.

    Args:
        button: The layout object, or the object given to ``add_input``.
        choices: The form's statement of size, colour and variant, if any.
        placed: The ``Choice`` of a layout around the button, if any. It wins
            over the form's statement for this button.

    Raises:
        InvalidChoice: A size, colour or variant stated for the form or the
            button is not one daisyUI has, or the layout around the button
            states a drawing, which a button has none of.
    """

    # The colour django-crispy-forms gives a Submit when none is chosen.
    default_color = "btn-primary"
    class_attribute = re.compile(r'( class=")([^"]*)(")')

    def __init__(
        self,
        button: Any,
        choices: FormChoices | None = None,
        placed: Choice | None = None,
    ) -> None:
        self.button = button
        self.modifiers = self.resolve_modifiers(choices or FormChoices(), placed)

    def resolve_modifiers(
        self, choices: FormChoices, placed: Choice | None
    ) -> list[str]:
        """Return the daisyUI class of each choice that applies to the button.

        Resolved when the button is built, so a mistake is raised from the tag
        and not from inside a template's ``{% if %}``, which would swallow it.

        Args:
            choices: The form's statement.
            placed: The ``Choice`` of a layout around the button, or None.

        Returns:
            The classes for size, colour and variant, in that order, for each
            one that resolves to a class. None of them for a hidden input.

        Raises:
            InvalidChoice: See the class.
        """
        if getattr(self.button, "input_type", "") == "hidden":
            return []
        own = Choice() if placed is None else placed
        if own.drawing is not None and own.drawing is not INHERIT:
            raise InvalidChoice("drawing", own.drawing, (), self.target)
        stated = {
            "size": choices.size,
            "color": choices.button_color,
            "variant": choices.button_variant,
        }
        resolved = (
            Modifiers.resolve(
                kind,
                Modifiers.button,
                own=getattr(own, kind),
                form=form,
                target=self.target,
            )
            for kind, form in stated.items()
        )
        return [modifier for modifier in resolved if modifier]

    @property
    def target(self) -> str:
        """What an error names: the button's name, or a ``StrictButton``'s content."""
        name = getattr(self.button, "name", None)
        return str(name if name is not None else self.button.content)

    @property
    def has_color(self) -> bool:
        """Whether a colour class resolved for the button."""
        return any(
            modifier in Modifiers.colors[Modifiers.button].values()
            for modifier in self.modifiers
        )

    @property
    def css_class(self) -> str:
        """The classes of an ``<input>`` button: its own, then the choices.

        The colour a ``Submit`` is given by default is left out when a colour
        resolved, so that one colour is written. The same class given by the
        developer as ``css_class`` is kept.
        """
        names = self.button.field_classes.split()
        if (
            self.has_color
            and self.default_color in names
            and self.default_color in type(self.button).field_classes.split()
        ):
            names.remove(self.default_color)
        kept = daisyui_classes(" ".join(names)).split()
        return " ".join(dict.fromkeys([*kept, *self.modifiers]))

    @property
    def flat_attrs(self) -> str:
        """The attributes of a ``StrictButton``, with the choices in its classes.

        The string is returned as django-crispy-forms wrote it when there are
        no choices. Otherwise they are added inside the ``class`` attribute,
        found by its leading space so that an attribute whose name ends in
        ``class`` is left alone.
        """
        attrs: str = self.button.flat_attrs
        if not self.modifiers:
            return attrs

        def add(found: re.Match[str]) -> str:
            names = [*found.group(2).split(), *self.modifiers]
            return f"{found.group(1)}{' '.join(dict.fromkeys(names))}{found.group(3)}"

        return SafeString(self.class_attribute.sub(add, attrs, count=1))


@register.simple_tag(takes_context=True)
def daisyui_button(context: Context, button: Any) -> DrawnButton:
    """Return the pack's drawing of a button.

    Used as ``{% daisyui_button input as drawn %}``. A button in a layout is
    drawn with no form in the context, so the form's statement reaches it only
    through the context name ``daisyui``, which django-crispy-forms copies from
    the helper.

    Args:
        context: The template context, read for the form's statement of
            choices and for the choice of a layout around the button.
        button: The layout object, or the object given to ``add_input``.

    Returns:
        The button's drawing.

    Raises:
        InvalidChoice: A choice that applies to the button is not one daisyUI
            has.
    """
    placed = context.get(Choice.context_name)
    return DrawnButton(
        button,
        choices=FormChoices.lookup(context),
        placed=placed if isinstance(placed, Choice) else None,
    )


@register.simple_tag(takes_context=True)
def daisyui_field(context: Context, field: BoundField) -> FieldInput:
    """Return the pack's drawing of a bound field's widget.

    Used as ``{% daisyui_field field as drawn %}``: the frame asks the result
    which shape to draw, then draws it with ``drawn.render``.

    Args:
        context: The template context, read for the helper's label and error
            switches. Each is off only when it equals False, as the
            templates read it, and on when absent. It is also read for the
            form's statement of choices and for the choice of a layout around
            the field.
        field: The bound field whose widget is drawn.

    Returns:
        The field's input.

    Raises:
        InvalidChoice: A choice that applies to the field is not one daisyUI has,
            or a drawing is stated for a field that is not a boolean field.
        TypeError: The form's helper holds a ``daisyui`` attribute that is not a
            ``FormChoices``.
    """
    placed = context.get(Choice.context_name)
    return FieldInput(
        field,
        show_labels=context.get("form_show_labels") != False,  # noqa: E712
        show_errors=context.get("form_show_errors") != False,  # noqa: E712
        choices=FormChoices.lookup(context, field.form),
        placed=placed if isinstance(placed, Choice) else None,
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


@register.filter(is_safe=True)
def daisyui_tab_group(panes: str) -> str:
    """Give the radios of one tab holder a group name no other holder has.

    When no radio is checked, which is so when the first tab was given
    ``active``, the first radio is checked, so one tab is always open. An inner
    holder has been through this filter before the outer one, so each holder
    gets a name and a check of its own.

    Args:
        panes: The drawn tabs of one holder, each a radio followed by its content.

    Returns:
        The panes with the placeholder name replaced by one name for the holder.
    """
    if f"{TAB_GROUP_PLACEHOLDER} checked" not in panes:
        panes = panes.replace(
            TAB_GROUP_PLACEHOLDER, f"{TAB_GROUP_PLACEHOLDER} checked", 1
        )
    return panes.replace(TAB_GROUP_PLACEHOLDER, f'name="tabs-{secrets.token_hex(4)}"')


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


class FormsetTable:
    """Lay a formset's forms out as the rows and columns of one table.

    A template cannot look a field up by name, so the columns and the cell of
    every row are worked out here. Every form is taken to have the first form's
    fields.

    Args:
        formset: The formset whose forms are the rows.
    """

    def __init__(self, formset: BaseFormSet) -> None:
        self.formset = formset

    @property
    def columns(self) -> list[BoundField]:
        """The first form's visible fields, in its own order. Empty with no forms."""
        if not self.formset.forms:
            return []
        return list(self.formset.forms[0].visible_fields())

    @property
    def rows(self) -> list[dict[str, Any]]:
        """One entry per form, in the formset's order: the form and its cells.

        A cell is the form's bound field with the column's name, or None when
        the form has no field of that name. With no columns each row has one
        None cell, so the row's hidden fields have a cell to sit in.
        """
        names = [column.name for column in self.columns]
        return [
            {
                "form": form,
                "cells": [form[name] if name in form.fields else None for name in names]
                or [None],
            }
            for form in self.formset.forms
        ]


@register.simple_tag
def daisyui_formset_table(formset: BaseFormSet) -> FormsetTable:
    """Return a formset's forms laid out as the rows and columns of a table.

    Used as ``{% daisyui_formset_table formset as table %}``.

    Args:
        formset: The formset to lay out.

    Returns:
        The formset's table.
    """
    return FormsetTable(formset)
