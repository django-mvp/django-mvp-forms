"""The size, colour and variant a form states, and the daisyUI classes they mean."""

from enum import Enum
from typing import Any, ClassVar

from django.template import Context


class Inherit(Enum):
    """The type of ``INHERIT``, so that a signature can say "a name, None or this"."""

    INHERIT = "inherit"


INHERIT = Inherit.INHERIT
Stated = str | Inherit | None


class InvalidChoice(ValueError):
    """A size, colour or variant that cannot be drawn.

    Args:
        kind: What was stated: ``"size"``, ``"color"`` or ``"variant"``.
        value: The value that was stated.
        allowed: The names allowed, in daisyUI's order. Empty when the input
            drawn has no modifier of this kind at all.
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
        "radio": {
            "xs": "radio-xs",
            "sm": "radio-sm",
            "md": "radio-md",
            "lg": "radio-lg",
            "xl": "radio-xl",
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
        own: Stated = INHERIT,
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


class Choice:
    """A size, a colour and a variant stated for one field or one button.

    Each argument left out is inherited from the statement it is merged over,
    and None is the pack's ordinary drawing, which undoes it.

    Args:
        *fields: What the choice holds. Nothing when it is a value in
            ``FormChoices(fields=...)``.
        size: The size, or ``INHERIT``.
        color: The colour, or ``INHERIT``.
        variant: The variant, or ``INHERIT``.
    """

    def __init__(
        self,
        *fields: Any,
        size: Stated = INHERIT,
        color: Stated = INHERIT,
        variant: Stated = INHERIT,
    ) -> None:
        self.fields = list(fields)
        self.size = size
        self.color = color
        self.variant = variant

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
        )


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
        fields: dict[str, Choice] | None = None,
    ) -> None:
        self.size = size
        self.color = color
        self.variant = variant
        self.button_color = button_color
        self.button_variant = button_variant
        self.fields = dict(fields or {})

    @classmethod
    def lookup(cls, context: Context, form: Any = None) -> "FormChoices | None":
        """Find the statement for one draw.

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
        """
        found = context.get(cls.attribute)
        if isinstance(found, cls):
            return found
        helper = getattr(form, "helper", None)
        if helper is None or not hasattr(helper, cls.attribute):
            return None
        found = getattr(helper, cls.attribute)
        if not isinstance(found, cls):
            raise TypeError(
                f"helper.{cls.attribute} must be a FormChoices, not {found!r}"
            )
        return found
