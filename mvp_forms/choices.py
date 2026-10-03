"""The size, colour, variant, drawing and label a form states, and what they mean."""

from enum import Enum
from typing import Any, ClassVar

from crispy_forms.layout import LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django.template import Context
from django.utils.safestring import SafeString


class Inherit(Enum):
    """The type of ``INHERIT``, so that a signature can say "a name, None or this"."""

    INHERIT = "inherit"


INHERIT = Inherit.INHERIT


class InvalidChoice(ValueError):
    """A size, colour, variant, drawing or label that cannot be drawn.

    Args:
        kind: What was stated: ``"size"``, ``"color"``, ``"variant"``,
            ``"drawing"`` or ``"label"``.
        value: The value that was stated.
        allowed: The names allowed, in daisyUI's order. Empty when the input
            drawn has no modifier of this kind at all, when a drawing was
            stated for a field that takes none, or when a label was stated for
            something that cannot take one. For a drawing, the names the field
            takes: the three of a boolean field, ``"rating"`` for a field that
            holds one choice, or ``"range"`` for a number field.
        target: The field's name, or the button's name or content, when the
            statement was made for one of them. None when the form made it.
    """

    def __init__(
        self, kind: str, value: Any, allowed: tuple[str, ...], target: str | None = None
    ) -> None:
        self.kind = kind
        self.value = value
        self.allowed = allowed
        self.target = target
        where = f" for {target!r}" if target is not None else ""
        options = f"allowed: {', '.join(allowed)}" if allowed else "this input has none"
        super().__init__(f"{value!r} is not a {kind}{where}; {options}")


class UnknownField(KeyError):
    """A name in ``FormChoices(fields=...)`` that is not a field of the form.

    Args:
        names: The names the form has no field for.
    """

    def __init__(self, names: list[str]) -> None:
        self.names = names
        super().__init__(f"the form has no field named {', '.join(names)}")


class Modifiers:
    """The daisyUI class each choice means, for each kind of input and for buttons.

    Each table maps a component to daisyUI's name for a choice and then to the
    class that name means for that component. A component missing from a table
    has no modifier of that kind.
    """

    # Written out, not built from the component's name, so a host project's
    # Tailwind build finds them when it scans this module.
    sizes: ClassVar[dict[str, dict[str, str]]] = {
        "input": {
            "xs": "input-xs",
            "sm": "input-sm",
            "md": "input-md",
            "lg": "input-lg",
            "xl": "input-xl",
        },
        "textarea": {
            "xs": "textarea-xs",
            "sm": "textarea-sm",
            "md": "textarea-md",
            "lg": "textarea-lg",
            "xl": "textarea-xl",
        },
        "select": {
            "xs": "select-xs",
            "sm": "select-sm",
            "md": "select-md",
            "lg": "select-lg",
            "xl": "select-xl",
        },
        "file-input": {
            "xs": "file-input-xs",
            "sm": "file-input-sm",
            "md": "file-input-md",
            "lg": "file-input-lg",
            "xl": "file-input-xl",
        },
        "checkbox": {
            "xs": "checkbox-xs",
            "sm": "checkbox-sm",
            "md": "checkbox-md",
            "lg": "checkbox-lg",
            "xl": "checkbox-xl",
        },
        "toggle": {
            "xs": "toggle-xs",
            "sm": "toggle-sm",
            "md": "toggle-md",
            "lg": "toggle-lg",
            "xl": "toggle-xl",
        },
        "radio": {
            "xs": "radio-xs",
            "sm": "radio-sm",
            "md": "radio-md",
            "lg": "radio-lg",
            "xl": "radio-xl",
        },
        "rating": {
            "xs": "rating-xs",
            "sm": "rating-sm",
            "md": "rating-md",
            "lg": "rating-lg",
            "xl": "rating-xl",
        },
        "range": {
            "xs": "range-xs",
            "sm": "range-sm",
            "md": "range-md",
            "lg": "range-lg",
            "xl": "range-xl",
        },
        "btn": {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl",
        },
    }
    colors: ClassVar[dict[str, dict[str, str]]] = {
        "input": {
            "neutral": "input-neutral",
            "primary": "input-primary",
            "secondary": "input-secondary",
            "accent": "input-accent",
            "info": "input-info",
            "success": "input-success",
            "warning": "input-warning",
            "error": "input-error",
        },
        "textarea": {
            "neutral": "textarea-neutral",
            "primary": "textarea-primary",
            "secondary": "textarea-secondary",
            "accent": "textarea-accent",
            "info": "textarea-info",
            "success": "textarea-success",
            "warning": "textarea-warning",
            "error": "textarea-error",
        },
        "select": {
            "neutral": "select-neutral",
            "primary": "select-primary",
            "secondary": "select-secondary",
            "accent": "select-accent",
            "info": "select-info",
            "success": "select-success",
            "warning": "select-warning",
            "error": "select-error",
        },
        "file-input": {
            "neutral": "file-input-neutral",
            "primary": "file-input-primary",
            "secondary": "file-input-secondary",
            "accent": "file-input-accent",
            "info": "file-input-info",
            "success": "file-input-success",
            "warning": "file-input-warning",
            "error": "file-input-error",
        },
        "checkbox": {
            "neutral": "checkbox-neutral",
            "primary": "checkbox-primary",
            "secondary": "checkbox-secondary",
            "accent": "checkbox-accent",
            "info": "checkbox-info",
            "success": "checkbox-success",
            "warning": "checkbox-warning",
            "error": "checkbox-error",
        },
        "toggle": {
            "neutral": "toggle-neutral",
            "primary": "toggle-primary",
            "secondary": "toggle-secondary",
            "accent": "toggle-accent",
            "info": "toggle-info",
            "success": "toggle-success",
            "warning": "toggle-warning",
            "error": "toggle-error",
        },
        "radio": {
            "neutral": "radio-neutral",
            "primary": "radio-primary",
            "secondary": "radio-secondary",
            "accent": "radio-accent",
            "info": "radio-info",
            "success": "radio-success",
            "warning": "radio-warning",
            "error": "radio-error",
        },
        "rating": {
            "neutral": "bg-neutral",
            "primary": "bg-primary",
            "secondary": "bg-secondary",
            "accent": "bg-accent",
            "info": "bg-info",
            "success": "bg-success",
            "warning": "bg-warning",
            "error": "bg-error",
        },
        "range": {
            "neutral": "range-neutral",
            "primary": "range-primary",
            "secondary": "range-secondary",
            "accent": "range-accent",
            "info": "range-info",
            "success": "range-success",
            "warning": "range-warning",
            "error": "range-error",
        },
        "btn": {
            "neutral": "btn-neutral",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "accent": "btn-accent",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "error": "btn-error",
        },
    }
    variants: ClassVar[dict[str, dict[str, str]]] = {
        "input": {
            "ghost": "input-ghost",
        },
        "textarea": {
            "ghost": "textarea-ghost",
        },
        "select": {
            "ghost": "select-ghost",
        },
        "file-input": {
            "ghost": "file-input-ghost",
        },
        "btn": {
            "outline": "btn-outline",
            "dash": "btn-dash",
            "soft": "btn-soft",
            "ghost": "btn-ghost",
            "link": "btn-link",
        },
    }

    # A toggle and a switch are both daisyUI's toggle.
    drawings: ClassVar[dict[str, str]] = {
        "checkbox": "checkbox",
        "toggle": "toggle",
        "switch": "toggle",
        "rating": "rating",
        "range": "range",
    }

    # The label a field is drawn with, other than the ordinary one.
    labels: ClassVar[dict[str, str]] = {"floating": "floating-label"}

    tables: ClassVar[dict[str, dict[str, dict[str, str]]]] = {
        "size": sizes,
        "color": colors,
        "variant": variants,
    }
    button = "btn"

    @classmethod
    def names(cls, kind: str, component: str | None) -> tuple[str, ...]:
        """Return the names a statement is checked against.

        Args:
            kind: ``"size"``, ``"color"`` or ``"variant"``.
            component: The component drawn, or None for a widget with none.
                Buttons are one family and every other component, or none, is
                the other.

        Returns:
            Every name any component of the family has for the kind, in table
            order.
        """
        table = cls.tables[kind]
        if component == cls.button:
            members = [cls.button]
        else:
            members = [name for name in table if name != cls.button]
        return tuple(
            dict.fromkeys(name for member in members for name in table[member])
        )

    @classmethod
    def resolve(
        cls,
        kind: str,
        component: str | None,
        *,
        own: str | Inherit | None = INHERIT,
        form: str | None = None,
        target: str | None = None,
        in_error: bool = False,
    ) -> str | None:
        """Return the class one choice means for one component, or None.

        The field's or button's own statement wins when it is not ``INHERIT``,
        and otherwise the form's is used. None, stated by either, is the
        ordinary drawing and means no class.

        Args:
            kind: ``"size"``, ``"color"`` or ``"variant"``.
            component: The component drawn, or None for a widget with none.
            own: What the field or button states, or ``INHERIT``.
            form: What the form states for this kind, or None.
            target: The field's name, or the button's name or content, named by
                the error when the statement was its own.
            in_error: Whether the field is drawn as in error. Its colour is
                left out, so that the error modifier is the only colour written.

        Returns:
            The class, or None when nothing is stated, when the statement is
            None, when the form's statement means nothing for the component, or
            for the colour of a field in error.

        Raises:
            InvalidChoice: The name is not one daisyUI has for this family of
                components, or a field's or button's own statement is a name
                this component has no modifier for.
        """
        stated_here = own is not INHERIT
        value = own if stated_here else form
        if value is None:
            return None
        blamed = target if stated_here else None
        allowed = cls.names(kind, component)
        if value not in allowed:
            raise InvalidChoice(kind, value, allowed, blamed)
        modifiers = cls.tables[kind].get(component or "", {})
        if value not in modifiers:
            if stated_here:
                raise InvalidChoice(kind, value, tuple(modifiers), blamed)
            return None
        if kind == "color" and in_error:
            return None
        return modifiers[value]


class Choice(LayoutObject):
    """A size, a colour, a variant, a drawing and a label stated for one field.

    Each argument left out is inherited from the statement it is merged over,
    and None is the pack's ordinary drawing, which undoes it.

    In a layout it draws what it holds, at any depth, with itself placed in the
    context under ``context_name``, merged over any ``Choice`` around it. Holding
    nothing, it is the value in ``FormChoices(fields=...)``.

    Args:
        *fields: What the choice holds. Nothing when it is a value in
            ``FormChoices(fields=...)``.
        size: The size, or ``INHERIT``.
        color: The colour, or ``INHERIT``.
        variant: The variant, or ``INHERIT``.
        drawing: How a field is drawn, or ``INHERIT``. A boolean field takes
            ``"checkbox"``, ``"toggle"`` or ``"switch"``. A field that holds one
            choice, a select or a radio group, takes ``"rating"``. A number
            field takes ``"range"``. Any other field takes none.
        label: ``"floating"`` to draw the label of an input, a textarea or a
            select as daisyUI's floating label, or ``INHERIT``. None is the
            ordinary label. A button takes none.
    """

    context_name = "daisyui_choice"

    def __init__(
        self,
        *fields: Any,
        size: str | Inherit | None = INHERIT,
        color: str | Inherit | None = INHERIT,
        variant: str | Inherit | None = INHERIT,
        drawing: str | Inherit | None = INHERIT,
        label: str | Inherit | None = INHERIT,
    ) -> None:
        self.fields = list(fields)
        self.size = size
        self.color = color
        self.variant = variant
        self.drawing = drawing
        self.label = label

    def over(self, outer: "Choice") -> "Choice":
        """Return this choice merged over an outer one, each kind separately.

        Args:
            outer: The choice stated further out, which supplies whatever this
                one inherits.

        Returns:
            A choice holding nothing. Neither of the two is changed.
        """
        return Choice(
            size=outer.size if self.size is INHERIT else self.size,
            color=outer.color if self.color is INHERIT else self.color,
            variant=outer.variant if self.variant is INHERIT else self.variant,
            drawing=outer.drawing if self.drawing is INHERIT else self.drawing,
            label=outer.label if self.label is INHERIT else self.label,
        )

    def render(
        self,
        form: Any,
        context: Context,
        template_pack: str = TEMPLATE_PACK,
        **kwargs: Any,
    ) -> SafeString:
        """Draw what the choice holds, with the choice placed in the context.

        django-crispy-forms leaves layers of its own on top of the context while
        it draws, so the layer pushed here is removed by identity and never by
        popping the top.

        Args:
            form: The form being drawn.
            context: The template context.
            template_pack: The template pack drawing the layout.
            **kwargs: Passed on to what the choice holds.

        Returns:
            The markup of what the choice holds, in order.
        """
        outer = context.get(self.context_name)
        placed = self.over(outer) if isinstance(outer, Choice) else self
        layer = context.push({self.context_name: placed})
        try:
            drawn: SafeString = self.get_rendered_fields(
                form, context, template_pack, **kwargs
            )
            return drawn
        finally:
            for index in range(len(context.dicts) - 1, -1, -1):
                if context.dicts[index] is layer:
                    del context.dicts[index]
                    break


class FormChoices:
    """The choices a form states once, set as ``helper.daisyui``.

    Size reaches inputs and buttons. Colour and variant are held for inputs and
    for buttons separately. It is set on the helper instance, because
    django-crispy-forms passes a helper's instance attributes into the context
    and not its class attributes.

    Args:
        size: The size of every input and button.
        color: The colour of every input.
        variant: The variant of every input.
        button_color: The colour of every button.
        button_variant: The variant of every button.
        label: ``"floating"`` to draw the label of every input, textarea and
            select as daisyUI's floating label. Every other field is passed over.
        fields: A ``Choice`` for a field, by the field's name.
    """

    attribute = "daisyui"

    def __init__(
        self,
        *,
        size: str | None = None,
        color: str | None = None,
        variant: str | None = None,
        button_color: str | None = None,
        button_variant: str | None = None,
        label: str | None = None,
        fields: dict[str, Choice] | None = None,
    ) -> None:
        self.size = size
        self.color = color
        self.variant = variant
        self.button_color = button_color
        self.button_variant = button_variant
        self.label = label
        self.fields = dict(fields or {})

    def check(self) -> None:
        """Raise when the statement holds a name daisyUI does not have.

        The names for the form are checked wherever the statement is found, so a
        mistake in the buttons' choices is reported when the form is drawn
        without a button, as ``{{ form|crispy }}`` draws it. A field's or a
        button's own choice is checked when it is resolved.

        Raises:
            InvalidChoice: A size, a colour or a variant is not one daisyUI has
                for the inputs, a button's colour or variant is not one it has
                for buttons, or the label is not one the pack has.
        """
        stated = (
            ("size", self.size, None),
            ("color", self.color, None),
            ("variant", self.variant, None),
            ("color", self.button_color, Modifiers.button),
            ("variant", self.button_variant, Modifiers.button),
        )
        for kind, value, component in stated:
            allowed = Modifiers.names(kind, component)
            if value is not None and value not in allowed:
                raise InvalidChoice(kind, value, allowed)
        if self.label is not None and self.label not in Modifiers.labels:
            raise InvalidChoice("label", self.label, tuple(Modifiers.labels))

    @classmethod
    def lookup(cls, context: Context, form: Any = None) -> "FormChoices | None":
        """Find the statement for one draw, and check it.

        The context's value is used when it is a ``FormChoices``. A value there
        that is not one is the host page's own and is treated as absent. Failing
        that, the ``daisyui`` attribute of the form's helper is used.

        Args:
            context: The template context.
            form: The form being drawn, when one is at hand.

        Returns:
            The statement, or None when there is none.

        Raises:
            TypeError: The form's helper has a ``daisyui`` attribute that is not
                a ``FormChoices``.
            InvalidChoice: The statement holds a name daisyUI does not have.
            UnknownField: ``fields`` names a field the form at hand does not
                have.
        """
        found = context.get(cls.attribute)
        if not isinstance(found, cls):
            helper = getattr(form, "helper", None)
            if helper is None or not hasattr(helper, cls.attribute):
                return None
            found = getattr(helper, cls.attribute)
            if not isinstance(found, cls):
                raise TypeError(
                    f"helper.{cls.attribute} must be a FormChoices, not {found!r}"
                )
        found.check()
        known = getattr(form, "fields", found.fields)
        unknown = [name for name in found.fields if name not in known]
        if unknown:
            raise UnknownField(unknown)
        return found
